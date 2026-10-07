# Unattended renders: a plain-shell supervisor, finishing chains, verified status

How a long render (overnight, a whole film) runs to the end without anyone watching, and how the finishing and the
conform follow it automatically. The node-level facts (jobs, queues, power, corrupt frames) are in `render-farm.md`;
the engine paths in `octane-production.md` and `cycles-production.md`.

## 1. The rule: a plain-shell supervisor, not an agent
**Why:** the user ruled that overnight watching must not use Claude or credits. An agent polling a render costs
tokens, dies with its session and tends to re-arm wait loops without ending the old ones (seven duplicates once piled
up). A watchdog that watches one process exits after a node reboot ("no process found"), and a queue script then moves
on and silently drops the rest of the run.
- One supervisor owns the whole run until every frame is on disk. It runs detached on the workstation (`nohup` plus,
  on macOS, `caffeinate -i -s`), logs to a local file and to the shared storage, and alerts by desktop notification.
- The bundled engine `scripts/render_supervisor_template.sh` takes a per-site hooks file
  (`scripts/supervisor_hooks.example.sh`); run `… hooks.sh test` first (it reports and changes nothing).
- It caught a real hang overnight (no new frame for 10 min), restarted the server, relaunched the remaining shots and
  finished the run unattended; the next run needed no intervention.

## 2. Each pass, in order (every ~60 s)
1. **The node answers** (ssh). Unreachable for ~10 min → an alert that it may need a power cycle; keep waiting and
   resume by itself when it is back.
2. **Shared storage is mounted** → remount if not.
3. **An interactive session exists**, where the render server must live in one (a GUI-session server on Windows) →
   after ~5 min, an alert asking someone to log on.
4. **The power cap holds:** if any GPU's limit is above the site's cap file, apply the cap. **Never raise a cap**;
   every script that sets a limit reads the cap file.
5. **All GPUs present:** on a loss, reboot the node where the user pre-authorised it (at most ~3 times, ≥ 15 min
   apart), then alert and render on what is left.
6. **The render server runs** → start it in the right session.
7. **Drift** (the optional `drift_check` hook, read on the node from the frames' metadata or the driver's per-frame
   log): a frame slower than ~1.5× its shot's estimate (judgement; an absolute limit the user gives also works), a
   settings-spec hash that differs from the shot's launch hash, a new frame missing pass layers. Each kind alerts once
   per shot; the run continues, and the morning report explains every alert.
8. **The driver:** alive → the hang check (no new frame for ~10 min, after a ~15 min grace from the launch for scene
   load and the cold frame) → kill the verified PIDs (image name and command line checked; the kill verified), restart
   the server, and let the next pass relaunch. Not alive → delete zero-byte frames, **relaunch only the incomplete
   shots with skip-existing**. All frames on disk → notify, run the done hook, exit 0. A relaunch cap (~12) → alert and
   exit 1 rather than loop forever.
- **Count frames and their ages on the node**, never through a network mount: a mount's cache can hide new files or
  report a live run as hung for many minutes.
- **Count with a script file on the node** (`count.ps1 -Dir …`, `count.sh …`), never an inline one-liner passed through
  ssh: one shell layer ate a PowerShell `$_`, the count read 0 forever, every job "hung" every 10 min, and a shot was
  marked done at 29 %. A new count is proven against a known folder before a supervisor uses it.
- **The hang clock starts when the job starts**, not when the supervisor queues it: a launcher still waiting on the
  one-job lock is not a hang (a supervisor once killed its own queued job).
- **One render job at a time per server, by lock:** count running driver processes by command line, matching every
  driver version in use (a version bump once made a running job invisible to the lock). Stacked jobs corrupt each other.
- **A hung server is not a hung client.** GPUs at 0 % while clients are refused (seen after a GPU driver reset with
  every card still present) means the server is dead: restart the server; relaunching the client changes nothing.

## 3. The chain after the frames
- **A finishing chain per shot, in film order:** it waits until the shot's frames are complete (counted on the node),
  then jump-scans that shot (§8) and finishes it (the film's chosen finish → encodes; a denoise only if the user chose
  one), so finished shots exist long before the last frame renders.
- **The conform runs automatically after the chain:** the picture conform writes a DONE line to its log; the sound
  conform waits for that line (`grep` in a loop), then conforms the approved mix and notifies. The final shot is
  rendered long enough to play through the end hold (`finishing.md` §5).
- Each step is a versioned script that refuses to overwrite its outputs; markers are lines in logs, read by the next
  step.

## 4. Status is measured, never predicted
- Report what was measured: frames on disk per shot (counted on the node), GPU load and power, the newest frame's
  time, the log's last lines. After a restart the answer is "not yet confirmed" until new frames land.
- ETA = measured seconds per frame on this run × frames left, plus the fixed costs (session start, finishing).
- Never report a pending agent's result; relay checkpoints as they land.

## 5. Power, as a budget
- **Budget the node's wall draw under the circuit or power strip's continuous rating** (a shared 15 A strip tripped at
  ~1.4–1.5 kW continuous with four high-end GPUs). Cap each GPU at (budget − CPU and supply losses) / GPUs: measured, a
  cap that cuts board power by ~40 % costs only a few percent of render speed.
- Apply the cap from one file at every logon, after any vendor tool whose startup profile would restore full power.
- The real fix is a dedicated circuit or a PDU; keep the workstation and network gear off the node's circuit.

## 6. Background-task hygiene
- One owner per watch. Before arming a wait loop, list the background tasks and end the duplicates; after a session
  restart, re-arm only what is missing.
- Kill by verified PID, never by a pattern that can match the shell running it (`traps.md`).
- Recovery actions on the render node (kills, server restarts, reboots) follow the site's standing policy
  (`site-profile-example.md`); on the workstation, ask.

## 7. Pausing a queue, and an agent check-in when the user asks
- **Pausing for a test:** stop each supervisor by its own PID (a list of PIDs in one variable fails in zsh), then any
  orphaned launcher still waiting on the lock, then the node job; run the test; restart one supervisor (skip-existing
  resumes). List processes before and after — two supervisors race the moment the node frees up.
- **When the user asks the agent to watch overnight** (the default stays: the supervisor alone, no credits), add a
  check-in loop beside the supervisor: it polls every ~5 min and exits (waking the agent) on a stall longer than the
  supervisor's own restart, the node unreachable for three polls, the supervisor gone, the queue done, or every ~100 min.
  Each wake: read the reason, act, jump-scan any finished shot, re-arm. Never a second supervisor.

## 8. Gates around a production run (stage 11)
The supervisor keeps a run alive; it can't tell whether the frames are right. These checks can.

**The gate re-opens.** Every shot whose master, light rig, kernel spec or sampling changed after its FKL approval goes
back through at least its key-frame level check before its sequence runs.
- Why: an optimised whole-film relaunch once skipped it. One shot came out 5.8× too bright (a sampling aid that let the
  sun through an open glass cover), and it had no light passes to fix it in comp.

**The key-frame level check, before every sequence:**
1. Finish the new key frame and the approved one through the same look, grain off.
2. Report:
   - the mean and median level ratio;
   - the level ratio on the product's mask;
   - the mid-tone (L* 15–85) colour difference;
   - a side-by-side sheet.
3. **Pass:** level within ±5 % and mid-tone colour within ~2 ΔE, unless the change was asked for. These thresholds are
   judgement: the measured passes sat within 3 %, and the fails were +19 % and 5.8×.
4. A fail stops that shot's sequence until its cause is found.

**The launch and the first frame:**
- The launch command carries the shot's complete settings spec (`cycles-production.md` §9.4) and its pass list. Read
  both in the command itself, not from memory.
- Open the first frame of every run before leaving it alone, and check:
  - its layers: beauty, light passes, data, product-part IDs;
  - its spec hash and sample count.

**Light passes with every final** (`cycles-production.md` §9.5): per-light direct and indirect, sun, sky, emitters,
reflection and refraction, and Z, normals and IDs. A light that comes out wrong in one shot is then a gain in the comp,
not a re-render. Measured cost on 4 GPUs: ~+10 % per frame, ~180 MB per 1080p frame for 15 passes.

**The jump scan, on every finished shot:**
1. Compute the consecutive-frame difference at 1/8 resolution (mean absolute difference, relative to the frame mean).
2. Flag any frame whose step is more than ~3× the shot's median step (judgement). On moving shots the normal relative
   step measured 0.10–0.15.
3. Flag any step that is exactly zero: a stale or duplicated buffer. Measured: stale frames were byte-identical to
   another frame.
4. Explain each flag (a lamp switching on is a real step). Otherwise read the frame's metadata (shot, frame, spec hash,
   sample count) against the pack to find the cause: a stacked job, the wrong frame, or a restart that changed a
   setting.

**The resumed-session scan, on every shot that was restarted** (a hang, a crash, a pause):
1. Find each resume point from the frame files' write times: a gap well above the shot's normal frame interval (or
   frames written out of order). The frame after the gap is the first frame of a new render session.
2. Score each such frame for a single-frame pop: the mean of |frame − ½(previous + next)| on a blurred log-luminance
   image, against the same score for its ±5 neighbours. A whole-frame mean or a step scan misses it; this one doesn't.
3. Re-render every popping first frame in a new session with **one throwaway pre-roll frame** before it (render f−1
   and f, keep only f), into a new versioned folder, then merge a full copy of the sequence for the comp or the edit.
- Why: the first frame of a render session is not the same render as the frames after it (measured: re-rendering a
  mid-session frame as a session's first frame changed it by about the noise level; the frames after it matched the
  original to ~0.02 %). On a close-up of a spinning part this read as the part "popping" for one frame at each
  restart, and the user found it in the edit. Shots whose restart frames scored no higher than their neighbours were
  left alone.
- Prevention: a supervisor that resumes a shot renders one pre-roll frame first.

## 9. Measure and gate (stage 11)
| Check | Pass |
|---|---|
| FKL in the final engine | main has checked every frame against the approved previews; the user's "go" per shot or act |
| Key-frame level check (and every re-opened gate) | level ±5 %, mid-tone colour ≤ ~2 ΔE against the approved frame, or the change was asked for |
| First frame of every run | every layer present; the spec hash is the shot's; the sample count plausible |
| During the run | no unexplained drift alert; measured seconds per frame within ~1.5× the stage 10 estimate |
| Frame counts | complete per shot, counted on the node; zero-byte frames and frames corrupted by an interruption re-rendered |
| Jump scan | every step above ~3× the median explained; no zero steps |
| Resumed sessions | every restart's first frame scored for a single-frame pop; poppers re-rendered with a pre-roll frame |
| Light passes | present in every final frame |

**Show:** FKL in the final engine beside the approved previews, the level-check table, then each shot as it lands.
