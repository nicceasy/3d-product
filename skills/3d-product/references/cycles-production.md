# Cycles production: the complete second path

Cycles is a full production path, not a fallback: it renders whole beauty rounds and composition finals, and it is
2–3× faster per frame than Octane's realism config (measured). Octane wins one thing: light carried through glass inside
a scene (a glass or acrylic cover, window glazing, chrome) clean at production samples. The shared stages are the same
for both paths: FKL in the final engine → main's check → the user's go → sequences → finishing (`SKILL.md` stages
11–12).

Contents: 1 Pick a path · 2 Settings that worked · 3 GPUs per frame · 4 Output · 5 Light through glass · 6 Launch and
memory · 7 Noise faults and their real causes · 8 Timings

## 1. Pick a path (by the brief, then by the hardware)
| The brief | Octane available (a node with the add-on + a running server) | No Octane |
|---|---|---|
| Sunlight through glass or acrylic inside a scene (a cover over the product, glazing, chrome carrying the room) | **Octane, the realism config** (`octane-production.md` §5) | Cycles with the production biases, accepting darker glass-enclosed interiors; unbiased Cycles only for single hero stills (fireflies) |
| A glass product in a studio (caustics, spectra on the set) | Cycles with the glass settings (§5) + a LuxCore caustic layer (`glass-light.md` §7) | same |
| Metal, plastic, lacquer, fabric; throughput first | **Cycles production** | **Cycles production** |
| Previews, look-dev, grey box, compositions, FKL previews | Cycles on the workstation | Cycles on the workstation |
| One urgent frame on a multi-GPU node | Cycles, all GPUs on the frame if the scene is small | same |
`probe_setup.py --priority realism|speed` applies the hardware half of this table.

## 2. Settings that worked
| Setting | Value | Why (measured) |
|---|---|---|
| Adaptive threshold | **0.02** | at 0.01, ≈ 97 % of pixels hit max samples; 0.02 cut sampling ≈ 25 % with no visible change |
| Min / max samples | 32 / 1024 | min 16–128: no effect |
| In-render denoiser | **off** (the author: "get it done through the renderer") | in-render OIDN at low spp blotches dark bead-blasted metal in motion |
| Post denoise | OIDN colour-only on the converged EXRs (`finishing.md`) | residual noise → ≤ 0.1 code values; no boil added in motion; ≈ 1 s/frame |
| Clamp indirect / Filter Glossy | 3 / 1.0 | production biases (§5 says what they cost) |
| Sampling per sequence | every frame at the KEY frame's settings (a standing rule) | |
| Persistent data | on for sequences and preview loops | a camera-only change re-renders in ≈ 1–2 s at preview size |
| Motion blur | shutter 0.5 (180°), centred; LINEAR keys; `motion_steps` 2 on fast-spinning parts | +3–11 % time; CONSTANT keys double the image |
| Glossy / transmission bounces | defaults | raising them made no measurable difference in an interior set |

Measured noise vs time (one GPU, 540p, RMSE against an independent-seed 4096-spp reference; time relative to the 0.02
production setting):

| Threshold | Raw time / RMSE | + OIDN time / RMSE |
|---|---|---|
| 0.01 | 1.26× @ 0.0130 | — |
| **0.02 (production)** | 1.00× @ 0.0145 | 1.07× @ 0.0068 |
| 0.05 | 0.44× @ 0.0290 | 0.49× @ 0.0081 |
| 0.1 | 0.17× @ 0.0482 | 0.26× @ 0.0094 |
Max 2048 / 4096 at 0.02: 1.5× / 2.0× time for RMSE ≈ 0.013 (almost nothing). A faster production (0.05 + OIDN) looks
good on stills but is unproven in motion: run the 10-frame flicker check before using it for a sequence.

## 3. GPUs per frame
- **One GPU per frame, one Blender per GPU** on a multi-GPU node: throughput = (per-GPU frame time) / (GPU count),
  measured once ≈ 7 s/frame on four high-end consumer GPUs at 1080p. Pin each instance to one card (by PCI bus id), force OptiX, and
  claim frames dynamically (each instance `-s k+1 -e N -a` over placeholders, started 2 s apart; `render-farm.md`).
- All GPUs on one frame: faster in steady state for a small scene, but **slower on most heavy single frames** (measured
  0.8–1.8× a single GPU's time): each device uploads the whole scene.
- Multi-GPU on one frame only for one urgent frame of a small scene.

## 4. Output
- 32-bit float EXR, ZIP, scene-linear, always; data passes (Depth, Object Index, Mist, Normal, Crypto).
- A light group for every emitter (lights, emissive parts, late-added props); `render.lg_denoise: true` writes
  compositor-denoised groups that sum to the beauty within 0.5 % (`realism-finishing.md` §4).
- Blender writes a multi-part EXR: read every part. The pass is "Object Index", not IndexOB.

## 5. Light through glass: what Cycles' production settings cost (measured against Octane)
Three production biases darken everything seen through or lying under glass:
1. **clamp_indirect counts from the first glass hit**: behind a camera-visible glass surface the glass hit is bounce 0,
   so all light beyond it is clamped.
2. **The caustics filter** (refractive and reflective caustics off, Filter Glossy 1.0): turning caustics on alone
   brought the Octane/Cycles luminance ratio in shadows from ≈ 1.3 to ≈ 1.1.
3. **Glass is opaque to shadow rays** with caustics off: a glass or acrylic cover blocks the direct sun.

With both engines unbiased (Cycles clamp_indirect 0 + caustics on + Filter Glossy 0; Octane GI clamp off; 2048 spp) they
agree: frame ΔE00 falls to ≈ 2.5–3.3, a region under a cover from ΔE00 ≈ 16 to ≈ 4 and from 7.8× to 1.16× in
luminance. **But unbiased Cycles has fireflies everywhere** at 2048 spp, where Octane renders the same transport clean
at 1024. No clean Cycles middle setting exists. So: in Cycles, keep the biases and design around them (shots with the
cover open, flags, a sun through open windows), or send glass-enclosed hero shots to Octane.

**Glass products in a studio** (caustics are the point): bounces 64, clamp 0, Filter Glossy 0, lights ≥ a few mm,
≥ 256 spp before denoise, no OIDN on sparse caustics; LuxCore for caustics, spectra and projections.
**Sun through glass in motion:** a mirror-smooth pane lets the sun arrive only through rare BSDF hits and sparkles frame
to frame: roughness ≥ 0.03 on any glass the sun passes through in a moving shot.

## 6. Launch and memory
- **`--factory-startup` on every render-node Cycles job**: a user add-on (e.g. Octane) forced a full scene re-sync every
  frame (measured ≈ 10× the per-frame sync).
- Cap set textures at load (2048 px; the product, its prints and labels and the HDRI keep full size); trim per shot by
  the scene audit (`scene-optimisation.md`); fit the shot in-core. Out-of-core rendering is an order of magnitude slower
  (measured ≈ 2 min/frame).
- One packed .blend per shot with a `job.json`; never write a new round over running job folders.
- A render-node queue that skips finished work without launching Blender, a watcher (hung, slow, zero-byte, GPU lost),
  power caps and the corrupt-frame check after any power loss: `render-farm.md`.

## 7. Noise faults and their real causes
- **Splotches ≥ 1 cm are often material, not GI:** a two-seed A/B that keeps the pattern in place proves it. Measured
  causes: a cm-scale mottle in a lacquer, a wall bump at 100 % (→ 25 %).
- **Refraction flicker** under sun: mirror-smooth glass (fix: roughness ≥ 0.03).
- **A preview denoiser shows detail the path-traced final doesn't** (a small print under glass): compare final against
  preview before writing a caption.
- Cycles is deterministic (seed 0): an image and a seed-0 reference share samples, so RMSE under-reports noise.
  Measure against an independent seed.

## 8. Timings (measured, 1080p unless noted)
| Where | Config | Per frame |
|---|---|---|
| Laptop workstation (laptop-class GPU, Metal) | FKL previews 960×540, 256 spp + OIDN | 30–40 s |
| Laptop workstation | grey box 960×540, 8 spp + OIDN | ≈ 2 s |
| Laptop workstation | composition previews 640×360, 16 spp + OIDN | 1–2 s per camera change |
| 4-GPU node (high-end consumer GPUs, 200 W) | production, one GPU per frame | ≈ 7 s throughput (≈ 27 s per GPU) |
| 4-GPU node | production, 4 GPUs on one frame | ≈ 10 s steady |
| 4-GPU node | compositions 1024 spp, no denoiser, one Blender per GPU | ≈ 50 s average (spread ×12); ≈ 4 frames/min |
