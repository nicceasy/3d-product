# Beauty rounds on render nodes

How to render a film's sequences on one or more render nodes while the workstation keeps building, grading and
delivering. The rules hold for any node: one packed job per shot, one renderer per GPU, dynamic frame claiming, skip
finished work, a watcher, power caps, the corrupt-frame check. Machine facts for one real site: `site-profile-example.md`.
Cycles settings: `cycles-production.md`; the Octane path (a converted master + animation packs in a kept-alive session):
`octane-production.md`. Per-shot trims come from the ray-cast scene audit (`scene-optimisation.md` §3).

**The farm is for throughput, not iteration (`fast-feedback.md`).** A beauty night starts only after the same shots
were approved at preview cost: FIRST/KEY/LAST stills, then the grey-box animatic. A first beauty round's review
typically scraps a few shots and changes about half of the rest (composition, camera moves, DOF, timing), all of it
visible before the farm. Look questions run as single frames or crops, not sequences.

## Jobs
- **One packed .blend per shot** with a `job.json` (frames, key_frame, last_frame, output). Never write a new round
  over running job folders: use new, versioned folders.
- **A pre-script per renderer instance:** pins one GPU (by PCI bus id), forces OptiX, resets the render settings and
  applies the shot's one complete spec, reads it back and writes its hash into each frame's metadata
  (`cycles-production.md` §9.4), then any material fixes and the texture cap at load. Expose A/B switches as
  environment variables (threshold, min samples, glossy filter, seed, a sample-count AOV); an A/B run logs its own hash.
- **Always `--factory-startup` for Cycles jobs**: a user add-on (e.g. Octane) forced a full scene re-sync every frame.
- **VRAM:** every shot was verified in core at stage 10 (`scene-optimisation.md` §1). The job re-applies the set-texture
  cap at load (the product, its prints and the HDRI keep theirs), hides (never deletes) only the render-verified lists,
  and runs no GPU denoiser: OIDN on a full card hung at a fixed sample.

## Sampling (tune with the sample-count AOV, not by eye)
- Settings and evidence: `cycles-production.md` §2 (adaptive 0.02, min 32, max 1024, no denoiser, clamp indirect 3,
  Filter Glossy 1.0) as the starting point; each shot's cap and threshold come from the stage 10 sweep. Every frame of
  a sequence uses the KEY frame's sampling (a standing rule). 32-bit ZIP EXR always, the light passes on.
- Noise faults and their causes (splotches from materials, refraction flicker from mirror-smooth glass):
  `cycles-production.md` §7.

## Queue
- Pass 1: FIRST/KEY/LAST stills of every shot; pass 2: full sequences in script order, each shot only after its key
  frame passed the level check (`render-supervision.md` §8).
- **Dynamic frame claiming**: each GPU instance renders `-s k+1 -e N -a` with placeholders on (Blender skips frames
  whose file exists), overwrite off, instances started 2 s apart → no card waits on a slow one.
- **Skip finished work without launching Blender** (count non-empty EXRs ≥ N) → restarts cost seconds.
- On a Windows node, run the queue as a SYSTEM scheduled task: Windows OpenSSH lives in Session 0, so GUI apps (and
  Octane) need a one-off `/it` task and headless work a SYSTEM task. When the node's ssh shell is Git Bash,
  `export MSYS_NO_PATHCONV=1` before `schtasks /run …`, or `/run` becomes a path.

## Keeping it alive
- **Unattended runs are owned by a plain-shell supervisor** (`render-supervision.md`,
  `scripts/render_supervisor_template.sh`): node, share, session, power cap, GPU count (reboot on loss), render server,
  hang check, relaunch of incomplete shots with skip-existing, a relaunch cap, desktop alerts. It replaces the earlier
  watcher, which exited on the first problem and could read old logs after a restart (one false HUNG).
- **Power is a budget:** four high-end GPUs plus the CPU trip a shared surge protector within hours at sustained load
  near its rating (once at ~1.4–1.5 kW continuous). Keep the node's wall draw under the circuit's continuous rating:
  cap each GPU (`nvidia-smi -pl <W>`) from one cap file, re-applied at every logon after any vendor tool, never raised
  by a script. Measured: a 40 % cut of board power costs ≈ 2 % speed; ≈ 45 % of board power runs cool (40–52 °C). The
  real fix is a dedicated circuit; keep the workstation and the router off the node's circuit.
- **After any power loss, test every frame written in the last seconds:** each GPU's last frame can be corrupt *at full
  size* (EXR_ERR_CORRUPT_CHUNK), so size checks miss it. Read the newest frames with OpenEXR, move bad ones aside, restart
  the queue (it re-renders the gaps).

## Finishing and delivery (workstation)
- A finishing loop walks the script order and, when a shot's sequence completes, jump-scans it and runs the film's
  chosen finish (`finishing.md` §1 or §7) → ProRes .mov, H.264 .mp4 → the review folder (`NN_<shot>.mp4`).
- A watcher that copies review videos to a synced review folder (videos only, `fast-feedback.md`) must key on **new file names**, not
  mtimes: the loop re-copies finished shots on every restart.
- Notify the user per arrival only if they asked for it; a push to the phone needs Remote Control on.
- Launch long workstation loops detached (`nohup caffeinate -i -s …` on macOS) so they survive the session; re-launch
  after a restart.
- **A finishing chain per shot** finishes each shot as soon as its frames are complete (counted on the node), and the
  picture and sound conforms follow automatically (`render-supervision.md` §3).
