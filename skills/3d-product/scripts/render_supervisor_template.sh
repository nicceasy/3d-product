#!/bin/bash
# render_supervisor_template.sh - an unattended overnight render supervisor in plain bash (no agent, no credits).
#
# Why: an agent polling a render all night costs credits, dies with the session and tends to re-arm duplicate wait
# loops; a watchdog that only watches one process exits after a node reboot ("no process found"), and a queue script
# then moves on and silently drops the rest of the run. This loop owns the whole run until every frame is on disk.
# The method and its reasons: references/render-supervision.md.
#
# Usage:  render_supervisor_template.sh <site_hooks.sh> [test|once|run]
#   test  print what every hook reports and change nothing (run it first, and after any hook edit)
#   once  one pass of the loop (it acts), then exit
#   run   loop every LOOP_S until every frame exists (exit 0) or the relaunch cap is hit (exit 1)
# Launch detached so it survives the session and the workstation stays awake:
#   macOS: nohup caffeinate -i -s ./render_supervisor_template.sh hooks.sh run > sup.out 2>&1 &
#   Linux: nohup ./render_supervisor_template.sh hooks.sh run > sup.out 2>&1 &
#
# The hooks file is per site and per run (copy it, version it, fill it in); this engine stays generic.
# Required hooks (shell functions; each returns non-zero when it cannot read the node, so the loop waits instead of
# acting on a wrong answer):
#   node_ok                 0 if the render node answers (e.g. ssh -o BatchMode=yes -o ConnectTimeout=10 node 'echo ok')
#   frames_want             print "<shot> <frames wanted>" per shot (from the job or pack files)
#   frames_have             print "<shot> <non-empty frames on disk>" per shot, COUNTED ON THE NODE, never through a
#                           network mount (an SMB client can hide new files for many minutes)
#   driver_pids             print the PIDs of running render drivers (match the image name AND the command line)
#   newest_frame_age_s      print the seconds since the newest frame was written, measured on the node
#   launch <shot...>        start the driver detached on the node for these shots, with skip-existing ON
#   kill_verified           kill the driver(s) (and a hung render server) after re-checking each PID's name;
#                           check they are gone (a kill tool that no longer exists fails silently)
# Optional hooks (missing = skipped):
#   share_ok / share_remount          the shared storage is mounted here / remount it
#   session_ok                        an interactive logged-on session exists (render servers that live in one)
#   gpu_count                         print how many GPUs the node sees
#   power_over_cap / apply_power_cap  0 if any GPU's power limit is above the site's cap / apply the cap from the
#                                     site's cap file. The supervisor never raises a cap.
#   reboot_node                       reboot the node (only where the user pre-authorised automatic reboots)
#   server_ok / start_server          the render server is running / start it (in the interactive session)
#   delete_zero_byte                  delete zero-byte frames (placeholders of an interrupted run)
#   notify_hook "<msg>"               a custom alert; default: a desktop notification
#   on_done                           run once when every frame exists (e.g. touch a DONE marker for a chain)
#   drift_check                       print one line per drift found in the frames on the node, as "<key>: <message>":
#                                     a frame slower than ~1.5x its shot's estimate, a settings-spec hash that differs
#                                     from the shot's launch hash, a new frame missing pass layers (read the frames'
#                                     metadata or the driver's per-frame log ON THE NODE). Each key alerts once, so
#                                     keep counts and frame numbers after the colon (e.g. "slow <shot>: 12 frames > 1.5x").
set -u

HOOKS=${1:-}
MODE=${2:-run}
[ -n "$HOOKS" ] && [ -f "$HOOKS" ] || { echo "usage: $0 <site_hooks.sh> [test|once|run]" >&2; exit 2; }

# ---- defaults (override any of them in the hooks file) ----
RUN_NAME="render"
LOG="./supervisor.log"     # local log, always written
LOG2=""                    # optional second log (e.g. on the shared storage)
LOOP_S=60                  # seconds between passes
HANG_S=600                 # no new frame for this long while a driver runs = hung
GRACE_S=900                # after a launch, the hang check waits this long (scene load, kernel compile, cold frame)
LAUNCH_SETTLE_S=180        # after a launch, wait this long before deciding the driver is gone
MAX_LAUNCH=12              # relaunch cap: stop and alert instead of looping forever
EXPECTED_GPUS=0            # 0 = don't check the GPU count
MAX_REBOOT=3               # automatic reboots on GPU loss, then alert and render on what is left
REBOOT_GAP_S=900           # minimum time between two reboots
REBOOT_WAIT_S=120          # wait after a reboot before the next pass
DOWN_ALERT_S=600           # node unreachable this long -> alert (it may need a power cycle)
LOGON_ALERT_S=300          # no interactive session this long -> alert (someone must log on)
NEEDS_SESSION=0            # 1 = the render server needs an interactive logged-on session

# shellcheck source=/dev/null
. "$HOOKS"

have() { declare -F "$1" >/dev/null; }
for h in node_ok frames_want frames_have driver_pids newest_frame_age_s launch kill_verified; do
  have "$h" || { echo "hooks file $HOOKS does not define the required hook: $h" >&2; exit 2; }
done

now() { date +%s; }
dur_txt() { if [ "$1" -ge 60 ]; then echo "$(($1 / 60)) min"; else echo "$1 s"; fi; }
log() {
  local l; l="$(date '+%m-%d %T') $*"
  echo "$l" >> "$LOG"
  if [ -n "$LOG2" ]; then echo "$l" >> "$LOG2" 2>/dev/null || true; fi
}
notify() {
  log "ALERT $*"
  if have notify_hook; then notify_hook "$*"; return 0; fi
  local msg=${*//\"/\'}
  if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"$msg\" with title \"$RUN_NAME\"" >/dev/null 2>&1
  elif command -v notify-send >/dev/null 2>&1; then
    notify-send "$RUN_NAME" "$msg" >/dev/null 2>&1
  fi
  return 0
}

# shots still short of frames, space-separated; non-zero when the node can't be counted
incomplete() {
  local want have_
  want=$(frames_want) || return 1
  have_=$(frames_have) || return 1
  [ -n "$want" ] || return 1
  awk 'NR==FNR { h[$1] = $2; next } NF >= 2 { got = ($1 in h) ? h[$1] : 0; if (got + 0 < $2 + 0) printf "%s ", $1 }' \
    <(printf '%s\n' "$have_") <(printf '%s\n' "$want")
}
total() { awk '{ s += $2 } END { print s + 0 }'; }

if [ "$MODE" = test ]; then
  echo "run: $RUN_NAME   hooks: $HOOKS   log: $LOG"
  node_ok && echo "node: reachable" || echo "node: UNREACHABLE"
  if have share_ok; then share_ok && echo "share: mounted" || echo "share: NOT mounted"; fi
  if have session_ok; then session_ok && echo "session: logged on" || echo "session: NONE"; fi
  if have gpu_count; then echo "gpus: $(gpu_count) (expected $EXPECTED_GPUS)"; fi
  if have power_over_cap; then power_over_cap && echo "power: ABOVE the cap" || echo "power: at or under the cap"; fi
  if have server_ok; then server_ok && echo "server: running" || echo "server: NOT running"; fi
  echo "driver pids: $(driver_pids | tr '\n' ' ')"
  echo "newest frame age: $(newest_frame_age_s) s"
  if have drift_check; then echo "drift: $(drift_check | tr '\n' ';')"; fi
  W=$(frames_want); H=$(frames_have)
  echo "frames: $(printf '%s\n' "$H" | total) of $(printf '%s\n' "$W" | total)"
  echo "incomplete shots: $(incomplete)"
  exit 0
fi

NL=0; NREBOOT=0; LASTREBOOT=0; LAUNCHED=0; DOWN=0; DOWNALERT=0; NOLOGON=0; GPUALERT=0; SEEN_DRIFT="|"
log "supervisor start (pid $$, mode $MODE): $(frames_want | total) frames wanted"
while true; do
  T=$(now)
  # 1 the node
  if ! node_ok; then
    [ "$DOWN" = 0 ] && { DOWN=$T; log "node unreachable"; }
    if [ "$DOWNALERT" = 0 ] && [ $((T - DOWN)) -gt "$DOWN_ALERT_S" ]; then
      notify "$RUN_NAME: render node unreachable for $(dur_txt "$DOWN_ALERT_S") - it may need a power cycle. The supervisor resumes by itself when it is back."
      DOWNALERT=1
    fi
    [ "$MODE" = once ] && exit 0; sleep "$LOOP_S"; continue
  fi
  if [ "$DOWN" != 0 ]; then log "node back after $((T - DOWN)) s"; DOWN=0; DOWNALERT=0; fi
  # 2 the shared storage
  if have share_ok && ! share_ok; then
    log "shared storage not mounted -> remount"
    have share_remount && share_remount
  fi
  # 3 the interactive session
  if [ "$NEEDS_SESSION" = 1 ] && have session_ok && ! session_ok; then
    [ "$NOLOGON" = 0 ] && { NOLOGON=$T; log "no interactive session yet"; }
    if [ "$NOLOGON" -gt 0 ] && [ $((T - NOLOGON)) -gt "$LOGON_ALERT_S" ]; then
      notify "$RUN_NAME: the render node is up but nobody is logged on - log on so the render can resume."
      NOLOGON=-1
    fi
    [ "$MODE" = once ] && exit 0; sleep "$LOOP_S"; continue
  fi
  NOLOGON=0
  # 4 the power cap (apply, never raise)
  if have power_over_cap && power_over_cap; then
    log "a GPU power limit is above the site cap -> apply the cap"
    have apply_power_cap && apply_power_cap
  fi
  # 5 the GPUs
  if [ "$EXPECTED_GPUS" -gt 0 ] && have gpu_count; then
    NG=$(gpu_count | tr -dc '0-9'); NG=${NG:-0}
    if [ "$NG" -lt "$EXPECTED_GPUS" ]; then
      if have reboot_node && [ "$NREBOOT" -lt "$MAX_REBOOT" ]; then
        if [ $((T - LASTREBOOT)) -gt "$REBOOT_GAP_S" ]; then
          NREBOOT=$((NREBOOT + 1)); LASTREBOOT=$T
          log "only $NG of $EXPECTED_GPUS GPUs -> reboot $NREBOOT of $MAX_REBOOT"
          reboot_node
          [ "$MODE" = once ] && exit 0; sleep "$REBOOT_WAIT_S"; continue
        fi                                   # too soon after the last reboot: render on what is left meanwhile
      elif [ "$GPUALERT" = 0 ]; then
        notify "$RUN_NAME: the node sees $NG of $EXPECTED_GPUS GPUs (after $NREBOOT automatic reboots) - rendering on what is left."
        GPUALERT=1
      fi
    fi
  fi
  # 6 the render server
  if have server_ok && ! server_ok; then
    log "render server not running -> start it"
    have start_server && start_server
  fi
  # 7 drift in the frames written so far (slow frames, a changed spec hash, missing pass layers): alert once per key
  if have drift_check; then
    while IFS= read -r D; do
      [ -n "$D" ] || continue
      K=${D%%:*}
      case "$SEEN_DRIFT" in *"|$K|"*) ;; *) SEEN_DRIFT="$SEEN_DRIFT$K|"; notify "$RUN_NAME drift - $D";; esac
    done < <(drift_check 2>/dev/null)
  fi
  # 8 the driver
  P=$(driver_pids | tr '\n' ' ')
  if [ -n "${P// /}" ]; then
    AGE=$(newest_frame_age_s | tr -dc '0-9'); AGE=${AGE:-0}
    if [ $((T - LAUNCHED)) -gt "$GRACE_S" ] && [ "$AGE" -gt "$HANG_S" ]; then
      log "HANG: driver ($P) alive but no new frame for ${AGE} s -> kill (verified) and restart"
      kill_verified
      have start_server && start_server
    fi
    [ "$MODE" = once ] && exit 0; sleep "$LOOP_S"; continue
  fi
  # no driver running: finished, starting up, or needs a relaunch
  if [ $((T - LAUNCHED)) -lt "$LAUNCH_SETTLE_S" ]; then [ "$MODE" = once ] && exit 0; sleep "$LOOP_S"; continue; fi
  if ! INC=$(incomplete); then
    log "cannot count frames on the node; waiting"
    [ "$MODE" = once ] && exit 0; sleep "$LOOP_S"; continue
  fi
  INC=$(echo $INC)
  if [ -z "$INC" ]; then
    log "ALL FRAMES RENDERED - supervisor done"
    notify "$RUN_NAME: all $(frames_want | total) frames rendered."
    have on_done && on_done
    exit 0
  fi
  if [ "$NL" -ge "$MAX_LAUNCH" ]; then
    notify "$RUN_NAME: the supervisor hit $MAX_LAUNCH relaunches - stopping. Incomplete shots: $INC"
    exit 1
  fi
  have delete_zero_byte && delete_zero_byte
  NL=$((NL + 1))
  log "LAUNCH $NL of $MAX_LAUNCH: shots $INC"
  # shellcheck disable=SC2086
  launch $INC
  LAUNCHED=$(now)
  [ "$MODE" = once ] && exit 0
  sleep "$LOOP_S"
done
