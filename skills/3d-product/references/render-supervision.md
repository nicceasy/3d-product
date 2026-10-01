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
7. **The driver:** alive → the hang check (no new frame for ~10 min, after a ~15 min grace from the launch for scene
   load and the cold frame) → kill the verified PIDs (image name and command line checked; the kill verified), restart
   the server, and let the next pass relaunch. Not alive → delete zero-byte frames, **relaunch only the incomplete
   shots with skip-existing**. All frames on disk → notify, run the done hook, exit 0. A relaunch cap (~12) → alert and
   exit 1 rather than loop forever.
- **Count frames and their ages on the node**, never through a network mount: a mount's cache can hide new files or
  report a live run as hung for many minutes.
- **A hung server is not a hung client.** GPUs at 0 % while clients are refused (seen after a GPU driver reset with
  every card still present) means the server is dead: restart the server; relaunching the client changes nothing.

## 3. The chain after the frames
- **A finishing chain per shot, in film order:** it waits until the shot's frames are complete (counted on the node),
  then finishes that shot (denoise → look → encodes), so finished shots exist long before the last frame renders.
- **The conform runs automatically after the chain:** the picture conform writes a DONE line to its log; the sound
  conform waits for that line (`grep` in a loop), then conforms the approved mix (with the end hold of
  `sound-design.md` §11) and notifies.
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
