# supervisor_hooks.example.sh - example site hooks for render_supervisor_template.sh. Copy it per run (versioned),
# replace every <PLACEHOLDER>, delete the variant you don't use, then run:  render_supervisor_template.sh hooks.sh test
# Two variants: a Linux render node, and a Windows render node (OpenSSH with a Git Bash default shell) whose render
# server must live in the logged-on console session (references/octane-production.md section 2).
# Rules the hooks must keep: count and time frames ON THE NODE; match PIDs by image name AND command line; verify
# every kill; never raise a power cap; return non-zero when the node can't be read.

RUN_NAME="<run name>"
LOG="<local folder>/supervisor_<run>.log"
LOG2="<shared storage>/logs/supervisor_<run>.log"      # optional
EXPECTED_GPUS=4                                         # <the node's GPU count>
NEEDS_SESSION=0                                         # 1 for a server that needs a logged-on session
SSH="ssh -o ConnectTimeout=10 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 -o BatchMode=yes <node>"
FRAMES="<frames root on the node>"                     # one folder per shot: <FRAMES>/<shot>/*.exr
JOBS="<job or pack folder readable here>"              # one JSON per shot with its frame list

frames_want() {      # "<shot> <n>" from the job files; adapt to your job schema
  local f
  for f in "$JOBS"/*.json; do
    python3 -c "import json,sys,os; d=json.load(open(sys.argv[1])); print(os.path.basename(sys.argv[1])[:-5], len(d['frames']))" "$f" || return 1
  done
}
frames_have() {      # counted on the node, never through the share mount
  $SSH "for d in $FRAMES/*/; do echo \"\$(basename \$d) \$(find \$d -name '*.exr' -size +0 | wc -l)\"; done" 2>/dev/null
}
newest_frame_age_s() {
  $SSH "m=\$(ls -t $FRAMES/*/*.exr 2>/dev/null | head -1); [ -n \"\$m\" ] && echo \$(( \$(date +%s) - \$(stat -c %Y \"\$m\") )) || echo 99999" 2>/dev/null | tr -d '\r'
}
node_ok() { $SSH "echo ok" 2>/dev/null | grep -q ok; }
delete_zero_byte() { $SSH "find $FRAMES -name '*.exr' -size 0 -delete" 2>/dev/null; }
gpu_count() { $SSH "nvidia-smi --query-gpu=index --format=csv,noheader" 2>/dev/null | grep -c '^[0-9]'; }
power_over_cap() {   # 0 when any card's limit is above the cap file's value (the cap file is the site's single truth)
  local cap; cap=$($SSH "cat <cap file on the node>" 2>/dev/null | tr -dc '0-9'); [ -n "$cap" ] || return 1
  $SSH "nvidia-smi --query-gpu=power.limit --format=csv,noheader,nounits" 2>/dev/null | tr -d '\r' |
    awk -v c="$cap" '$1 + 0 > c + 1 { bad = 1 } END { exit !bad }'
}
apply_power_cap() { $SSH "<site script that applies the cap file to every card>" >/dev/null 2>&1; }
# share_ok() { [ -d "<shared storage>/logs" ]; }
# share_remount() { <mount command for the share>; sleep 10; }   # macOS: osascript -e 'mount volume "smb://<user>@<host>/<share>"'

# ---------------- variant A: Linux node ----------------
driver_pids() { $SSH "pgrep -f '<driver script name>'" 2>/dev/null; }
kill_verified() {
  $SSH 'for p in $(pgrep -f "<driver script name>"); do ps -o args= -p $p | grep -q "<driver script name>" && kill $p; done; sleep 5;
        pgrep -f "<driver script name>" && echo STILL_ALIVE' 2>/dev/null
}
launch() {           # detached on the node, skip-existing ON, only the shots given
  $SSH "nohup <render command> --shots $(echo "$@" | tr ' ' ,) --skip_existing 1 > $FRAMES/../logs/drive_\$(date +%s).log 2>&1 &"
}
reboot_node() { $SSH "sudo /sbin/reboot" >/dev/null 2>&1; }     # only if the user pre-authorised automatic reboots

# ---------------- variant B: Windows node, Git Bash default shell, GUI-session render server ----------------
# NEEDS_SESSION=1
# session_ok() { [ "$($SSH "powershell -NoProfile -Command \"@(Get-Process explorer -ErrorAction SilentlyContinue).Count\"" 2>/dev/null | tr -dc '0-9')" != 0 ]; }
# server_ok() { [ "$($SSH "powershell -NoProfile -Command \"@(Get-Process <ServerImage> -ErrorAction SilentlyContinue).Count\"" 2>/dev/null | tr -dc '0-9')" != 0 ]; }
# start_server() {    # a one-off interactive task: ssh itself lands in a non-interactive session
#   $SSH bash -s >/dev/null 2>&1 <<'EOS'
# export MSYS_NO_PATHCONV=1
# schtasks /create /tn SUP_SERVER /tr "<command that starts the server>" /sc once /st 00:00 /it /f >/dev/null
# schtasks /run /tn SUP_SERVER >/dev/null; sleep 2; schtasks /delete /tn SUP_SERVER /f >/dev/null
# EOS
#   sleep 20
# }
# driver_pids() {
#   $SSH "powershell -NoProfile -Command \"Get-CimInstance Win32_Process -Filter \\\"Name='<driver image>.exe'\\\" | Where-Object { \\\$_.CommandLine -like '*<driver script name>*' } | Select-Object -ExpandProperty ProcessId\"" 2>/dev/null | tr -d '\r' | grep -E '^[0-9]+$'
# }
# kill_verified() {   # driver(s) and the hung server; Stop-Process, never a removed tool such as wmic
#   $SSH "powershell -NoProfile -Command \"Get-CimInstance Win32_Process | Where-Object { (\\\$_.Name -eq '<driver image>.exe' -and \\\$_.CommandLine -like '*<driver script name>*') -or \\\$_.Name -eq '<ServerImage>.exe' } | ForEach-Object { Stop-Process -Id \\\$_.ProcessId -Force }\"" >/dev/null 2>&1
#   sleep 10
# }
# launch() { <site launcher that runs the driver inside the interactive session, with the shot list and skip-existing ON>; }
# reboot_node() { $SSH "shutdown //r //t 5 //f" >/dev/null 2>&1; }   # Git Bash: // keeps the switches
# frames_have / newest_frame_age_s work unchanged under Git Bash (stat -c %Y).

# notify_hook() { <custom alert, e.g. a push service>; }
# on_done() { echo "$(date +%T) ALL FRAMES RENDERED" >> "<chain log the finishing chain waits on>"; }
