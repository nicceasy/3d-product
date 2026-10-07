# Site profile: one example studio and the setup.json format

The pipeline talks in **roles**; this file holds the facts about one concrete site, as the format example for
`scripts/probe_setup.py` (stage 0.5) and `~/.config/3d-product/site.json` (template: `scripts/site.example.json`). The
example is the two-machine studio the skill was built on: a laptop workstation and one Windows render node with four
GPUs. A new site runs the probe and gets its own profile; nothing in the stages should assume these machines.

| Role | What it does | In the example |
|---|---|---|
| Workstation | builds scenes and jobs, previews, look-dev, compositions, FKL previews, finishing, boards | a macOS laptop (Apple silicon, 64 GB unified memory), Blender 5.2 (Metal) |
| Render node(s) | throughput: FKL finals, sequences, composition finals | `node1`: Windows 11, 256 GB, 4 × 24 GB NVIDIA GPUs (OptiX), Octane 31.10 |
| Shared storage | job folders and frames both sides can reach | an NVMe volume on the node, shared over SMB and mounted on the workstation |
| Finishing host | the look chain, Resolve, encodes | the workstation: DaVinci Resolve Studio 21.1 (scriptable), ffmpeg, a Python venv |

## Workstation
- A project venv (numpy, OpenEXR, build123d); a separate venv for LuxCore if you use it. The system `python3` often
  lacks PIL or trimesh: run pipeline scripts with the venv (`site.json` → `python`).
- Resolve external scripting: set `RESOLVE_SCRIPT_API`, `RESOLVE_SCRIPT_LIB` and `PYTHONPATH` so
  `DaVinciResolveScript` imports. Screenshots of Resolve fail while the display sleeps; the API keeps working.
- Grey box and previews run here (Metal).
- Long loops: `nohup caffeinate -i -s …` on macOS so they survive the session (the render supervisor, finishing
  chains, conform waiters).

## Render node (Windows)
- **Access:** key-based ssh to an alias (`node1`). If the node's default shell is Git Bash, pipe scripts with
  `ssh node1 bash -s <<< "…"` (Windows OpenSSH mangles quoted commands), and `export MSYS_NO_PATHCONV=1` before
  `schtasks /run …` (else `/run` becomes a path).
- **Sessions:** ssh lands in Session 0; OctaneServer and every GUI app run in the console Session 1. Octane jobs
  therefore launch through a one-off interactive task (`schtasks /create /it /sc once` → run → delete); a plain
  `ssh node1 blender -b` Octane job "succeeds" with no meshes or textures (`octane-production.md` §2). Cycles queues can
  run as a SYSTEM scheduled task. Launch Resolve in the logged-in session with a one-off `/it` task, never over ssh.
- **Blender:** if the Octane add-on is installed, run Cycles jobs with `--factory-startup`. Log to a file
  (`*> x.log`); streaming output over ssh can reset the connection.
- **Octane:** the OctaneBlender add-on plus OctaneServer, listening on localhost:50051 and activated. Restarting the
  server is the user's call unless the supervisor's policy allows it.
- **A GPU that drops off the bus** repeatedly: keep it out of Cycles queues until the hardware is fixed.
- **Power:** if the rig trips a breaker or surge strip, cap every card (the example used 225 W each to stay under
  1.4 kW total) from a cap file on the share, re-applied by a logon scheduled task (a vendor tool's startup profile can
  restore full power). Never raise a cap from a script; any script that sets a limit reads the file. The real fix is a
  dedicated circuit (`render-farm.md`).
- **A GPU driver reset** can leave OctaneServer running but hung (clients refused, GPUs at 0 %) with every card
  present: restart the server in the console session (a one-off `/it` task), then resume with skip-existing.
- **Example policies** (set by the user, recorded here so agents follow them): killing render-node processes is
  pre-authorised (confirm the PID's image and session first; save-and-quit Resolve through its API); a lost GPU means
  reboot and resume without asking; overnight watching is a plain-shell supervisor on the workstation, never an agent.

## Shared storage and the link
- One share, the same storage at a path on each side, remounted at login.
- A direct 10GbE cable between the workstation and the node's second Ethernet port, on a private subnet, with SMB
  multichannel: measured 520 MB/s workstation → node and 860 MB/s node → workstation, against ~110 MB/s on the home
  network. scp is CPU-bound at ~130 MB/s (Windows OpenSSH crypto), so bulk data goes through the share.
- A 1080p multi-pass 32-bit EXR is ~24 MB; 24 fps playback off the share needs ~576 MB/s.

## Supervisor hooks for this kind of site (`scripts/render_supervisor_template.sh`)
- Node: `ssh node1` (BatchMode); frames counted on the node (Git Bash `find`/`ls` under the frames root), never
  through the share mount.
- Session check: `explorer.exe` present (Get-Process); server: `OctaneServer.exe`, started by a one-off `/it` task;
  driver PIDs: `blender.exe` whose command line names the driver script.
- Remount: `osascript -e 'mount volume "smb://<user>@<node address>/<share>"'`.
- Power: read the cap file and apply it. Reboot: `shutdown //r //t 5 //f` (Git Bash).
- Alerts: macOS notifications. The run's own hooks file and logs live with the project, not in the skill.

## Review surfaces
- A synced review folder the user can open on a phone (e.g. iCloud Drive), one flat folder per review section.
- FigJam boards per project (`figjam-board.md`).

## Measure and gate
Run the probe with the brief, before any plan carries a budget: every machine-time budget later is tests × seconds,
and the seconds come from here. The card budget is set here too, so every 3D stage can check its weight against it
instead of meeting the card's limit at production.

| Measure | How | Pass |
|---|---|---|
| Roles | `probe_setup.py` → `setup.json` | every role filled or marked missing |
| Seconds per host and rung | `--bench` times one rung-1 clay frame on the workstation (640×360, 128 spp). Time the other rungs the plan uses once by hand: a rung-2 preview (960×540) on each preview host, one final-engine frame on each render node. Add each to the setup notes as {host, rung, engine, res, spp, seconds} | a measured number for every host and rung a budget will use |
| Card budget | the smallest render card's memory (on unified memory, what the engine may use) → `budget.json` in the study; format and per-stage split in `scene-optimisation.md` §0 | written before stage 2 builds anything |
| Project constraints | the user's rules for this project in the setup notes ("renders on the workstation only"); a node busy with another project's queue counts as missing | recorded, and the recommendation re-read with them |

**Sheet:** the five-line setup summary, the seconds table and the card budget.

## setup.json (what `probe_setup.py` writes)
```
{ "probed_at", "probe_s", "site_config",
  "local": { "name": "local", "host", "os", "memory_gb", "gpus": [{name, memory_gb, memory_kind: unified|vram, …}],
             "backend": METAL|OPTIX|CUDA|HIP|null,
             "blender": {path, version, cycles_devices: {OPTIX|CUDA|HIP|METAL|ONEAPI: [[name, type]] | "unsupported"}},
             "bench": {backend, res, spp, seconds} (with --bench),
             "octane": {addon: [paths], server_running, server_exe, listening_50051, licence},
             "resolve": {installed, path, version, scripting_module, running, product, studio},
             "python": {python, numpy_openexr, numpy}, "ffmpeg" },
  "nodes": [ { "name", "ssh", "reachable", "os", "windows", "gpus": [{index, name, memory_gb, util_pct, bus, driver,
               power_limit_w}], "backend", "blender": {path, version, cycles_devices (with --deep)},
               "octane": {addon, server_exe, server_running, server_process, listening_50051,
                          needs_interactive_session}, "ssh_session_id", "resolve": {installed, path, running},
               "link": {host, interface, media}, "probe_s" } ],
  "shares": [ {name, local, remote: {node: path}, mounted, free_tb, mount} ],
  "recommendation": { "finals": {path: octane|cycles, node, why}, "gpu_per_frame",
                      "previews": {node, engine, ladder, bench}, "finishing": {look_chain, resolve_host,
                      resolve_scriptable}, "storage", "notes": [ … ] } }
```
Measured on the example site (4.2 s; 6.5 s with `--deep --bench`): local = Apple silicon laptop, Metal, Blender 5.2,
Resolve Studio scriptable, no Octane; `node1` = 4 × 24 GB NVIDIA GPUs (OptiX + CUDA), Octane add-on and server running
in the console session, `needs_interactive_session: true`, a 10GbE link; share mounted. Recommendation (priority
realism): finals = Octane on `node1`, all GPUs per frame, one kept-alive session; previews = Cycles on the workstation;
finishing = local Resolve Studio + the numpy chain. With `--priority speed`: finals = Cycles on `node1`, one GPU per
frame.
