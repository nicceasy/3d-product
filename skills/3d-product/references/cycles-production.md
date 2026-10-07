# Cycles production: the complete second path

Cycles is a full production path, not a fallback: it renders whole beauty rounds and composition finals, and it is
2–3× faster per frame than Octane's realism config (measured). Octane wins one thing: light carried through glass inside
a scene (a glass or acrylic cover, window glazing, chrome) clean at production samples. The shared stages are the same
for both paths: FKL in the final engine → main's check → the user's go → sequences → finishing (`SKILL.md` stages
11–12). **§1 and §9–10 apply to both paths:** picking the path, and settling the engine once at stage 6 (the noise
target, the denoiser policy, sampling archetypes, the session architecture, complete settings, the output spec, the
look per light state, temporal checks). Engine specifics for Octane: the Octane manual (or an `/octane` reference skill, if installed).

Contents: 1 Pick a path · 2 Settings that worked · 3 GPUs per frame · 4 Output · 5 Light through glass · 6 Launch and
memory · 7 Noise faults and their real causes · 8 Timings · 9 Settle the engine once (stage 6, both paths) · 10 Measure
and gate (stage 6)

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
| Post denoise | **none by default** (§9.1); a colour-only pass on *converged* frames only when the user asks | approved once on frames at 0.02: residual from a few codes to ≈ 0.1, no boil in motion, ≈ 1 s/frame |
| Clamp indirect / Filter Glossy | 3 / 1.0 | production biases (§5 says what they cost) |
| Sampling per sequence | every frame at the KEY frame's settings (a standing rule), swept per shot at stage 10 | |
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
Max 2048 / 4096 at 0.02: 1.5× / 2.0× time for RMSE ≈ 0.013 (almost nothing). A cheaper config leaning on a post
denoiser (0.05 + OIDN) looks good on stills but is not the default (§9.1); if the user asks for one, run the temporal
checks (§9.7) on a moving range first.

## 3. GPUs per frame
- **One GPU per frame, one Blender per GPU** on a multi-GPU node: throughput = (per-GPU frame time) / (GPU count),
  measured once ≈ 7 s/frame on four high-end consumer GPUs at 1080p. Pin each instance to one card (by PCI bus id), force OptiX, and
  claim frames dynamically (each instance `-s k+1 -e N -a` over placeholders, started 2 s apart; `render-farm.md`).
- All GPUs on one frame: faster in steady state for a small scene, but **slower on most heavy single frames** (measured
  0.8–1.8× a single GPU's time): each device uploads the whole scene.
- Multi-GPU on one frame only for one urgent frame of a small scene.

## 4. Output
- 32-bit float EXR, ZIP, scene-linear, always; data passes (Depth, Object Index, Mist, Normal, Crypto).
- A light group for every emitter (lights, emissive parts, late-added props); the groups sum to the beauty within
  0.5 % (`realism-finishing.md` §4). `render.lg_denoise: true` (compositor-denoised groups) only where the beauty is
  denoised: previews, never finals by default (§9.1). The full output spec: §9.5.
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
- Set textures are capped at ingest (stage 4; the product, its prints and labels and the HDRI keep full size) and the
  job re-applies the cap at load. Every shot is verified in core at stage 10 (`scene-optimisation.md` §1); per-shot
  trims only where a shot would otherwise go out of core. Out-of-core rendering is an order of magnitude slower
  (measured ≈ 2 min/frame against 6.7 s in core).
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

## 9. Settle the engine once (stage 6, both paths)
Stage 6 picks the path (§1) and settles everything that would otherwise be rediscovered in production. Octane's own
numbers and how-tos belong in its manual (or an `/octane` reference skill); this is the process for either engine.

### 9.1 The noise target and the denoiser policy
- **Default: no denoiser in finals. Sample to the noise target**: the render's residual is at or below the film grain's
  σ in the darkest third of the frame, at 1:1, measured after the look.
- **Why (measured):**
  - A whole film rendered at a third of the samples plus a post denoise was rejected for artifacts and re-rendered
    without one.
  - An in-render AI denoiser erased ~25 % of fine detail energy (grooves, print) and flickered 1.7× raw.
  - At 256–512 spp the in-render AI denoiser left single-pixel speckle and blotchy mottling on dark lacquer and dark
    plastic.
- **A colour-only post denoise of *converged* frames** is an option only when the user asks for it. It was approved on
  frames already at the production threshold: the residual went from a few codes to ≈ 0.1 with no boil in motion.
  Never use it to rescue under-sampled frames.
- **Keep the raw beauty in the EXR whenever a denoiser is tested** (extra layers plus a header flag), so the finish can
  choose without a re-render.
- Previews, grey box and look-dev may denoise: they are judged on composition and light, not on noise.
- **How to measure the residual:**
  1. Take a high-sample reference rendered with a **different seed**. Cycles is deterministic per seed, so a seed-0
     image and a seed-0 reference share samples and under-report noise.
  2. Take the high-pass std of the difference in the display domain after the look, in 8-bit codes, per 32-px tile.
  3. Compare it with the film grain's own σ on the same tiles. Report p50 / p90 / p99 and the darkest third, with the
     renderer's own seconds.

### 9.2 A sampling archetype per light state
For each named light state, sweep cap × threshold on its worst frame. Prove adaptive engages: the render takes less
time than a flat-cap render, and a sample-count or noise pass shows the share of pixels that stopped. Then record the
state's archetype:
- **Converging:** most pixels stop (lamp-lit close-ups: 88–95 % stopped, measured). The threshold sets the noise; the
  cap only adds time once pixels converge. Measured: threshold 0.05 with cap 4096 had the noise of cap 16384, in 47 s
  against 83 s.
- **Cap-bound:** indirect-lit interiors (daylight through windows). Every variant runs to its cap, and the cap buys
  the smoothness. Measured dark-third residual against a 16k reference: 17.5 % at 2k / 0.1 (40 s), 12.1 % at 8k / 0.05
  (160 s).
- **Scene-bound:** a region that never converges, fixed in the scene (stage 3 or 5), not with samples. Two examples:
  - refraction-lit pixels under a glass cover with real shadows (0.9 % stopped, measured);
  - a hot spot in rough glass (it forced a 16k cap until it was removed).

Write the archetype and its starting spec on the light-state sheet. Stage 10 confirms it per shot on the final frames
(`scene-optimisation.md` §1 step 4). The numbers above are from one Octane node; for Cycles start
from §2.

### 9.3 The session architecture and its fixed costs
Pick the production architecture with the path, and measure its fixed costs now:
- **Keep the scene loaded across frames:** a kept-alive session (Octane) or persistent data (Cycles).
- **One master plus per-shot animation packs** wherever a conversion step exists (`octane-production.md` §3).
- **Cycles node jobs:** `--factory-startup`, one GPU per frame, frames claimed over placeholders (§3, §6).
- **Decompose one frame** into sync, start-up, sampling and stop, switching one factor off per session.

Why (measured): the fixed costs were ~75 % of a stock per-frame Octane job (≈ 120 s → 30 s per frame kept alive), and a
conversion per shot cost ≈ 13× the time and ~10⁵× the disk of a pack.

The architecture also decides how stage 9 authors motion:
- as channels a pack carries per frame (camera, rig, mechanisms, light state, driven values);
- with no per-shot edits to the master;
- with drivers the converter can't carry baked into the pack.

Record the start-up, the stop, a shot switch and a warm frame: they feed the stage 10 estimate.

### 9.4 Set render settings completely, every time
1. Reset every sampler, kernel, transport, clamp, denoiser and output input to the engine's defaults.
2. Apply ONE complete spec file for the shot.
3. Read every value back. Abort on a mismatch.
4. Log the spec's hash with every frame (EXR header or the driver's per-frame log). The supervisor alerts when it
   changes mid-run (`render-supervision.md` §2, the drift check).

Why: a saved scene keeps whatever was last set. A partial override list once left stale kernel values in a master (an
old cap, a sampler mode, an adaptive switch), and frames ran to the cap. A carried-over denoiser setting once corrupted a
noise measurement. Octane's settings live in several places (scene, kernel, imager, camera, render layer).

### 9.5 The output spec, complete and costed
- 32-bit float ZIP EXR, scene-linear; the raw beauty kept whenever a denoiser is tested.
- **Light passes by emitter role** (sun, sky, each practical, fills) that sum to the beauty, plus diffuse and
  specular / refraction splits.
- **Data passes:** Z, normals, Cryptomatte where the engine has it, and **object or material IDs for the product's
  parts**. Finishing samples the product as a reference and needs its masks.
- **Diffuse-light passes** (direct + indirect diffuse) when the finish balances on a reference object: they work as a
  virtual grey card.
- **Cost the spec on one frame and put it in the estimate.** Measured: 15 passes added +7–10 % per frame and ~180 MB per
  1080p frame (the beauty alone ≈ 24 MB).
- **The first frame of every run is opened and its layers listed** before the run continues.

Why: beauty-only finals can't be fixed in comp. A shot that rendered 5.8× too bright had to be re-rendered, and
hand-made product masks were wrong in many shots.

### 9.6 The final-engine look per light state
When finals and previews use different engines:
1. Calibrate on a grey card first.
2. Render every named light state in both engines at 540p from the same camera.
3. Each region (product, set, outdoors, practicals) is within ±10 % of the preview. Otherwise the difference is physical
   and accepted by name with the user (light through a tinted cover is one).

Why: master fixes found only at production FKL (a lamp ×1.3, windows ×1.2, label chroma, a mix inversion) each cost a
new master version after the cameras were final. ±10 % was the acceptance rule that worked.

### 9.7 Temporal checks
Run them on a 10-frame still-camera range and on a moving one:
- **Flicker:** the second temporal difference of 16-px block means, and of the frame mean (level jitter). Measured:
  - Cycles production read 0.00041 on block means, and the approved Octane config 0.00044; both were steady.
  - Frame-mean jitter of 0.5–1.5 % (Octane, static noise off, caps 1–4k) drew notes. 0.009–0.013 % at an 8k cap was
    invisible.
- **Sizzle:** the per-pixel second temporal difference (Cycles production 0.0029, measured).
- **Screen-lock, on moving shots:** the correlation of consecutive frames' high-pass residual at the same pixel. ≈ 0 is
  fresh noise. 0.87 drew the note "static noise"; 0.34 was masked only after a denoise and fresh grain.
- **Pass:**
  - flicker and sizzle no worse than the approved production config;
  - screen-lock < ~0.3 on moving shots (judgement).

## 10. Measure and gate (stage 6)
| Measure | Pass |
|---|---|
| Matched-noise table for the chosen path (time and residual against an independent-seed reference, per candidate config) | the chosen config meets the noise target (§9.1) on the worst frame of each light state, with no denoiser |
| Adaptive engages | the renderer's time below a flat-cap render; stopped share read from a sample-count or noise pass |
| Archetype per light state | converging / cap-bound / scene-bound recorded with a starting spec; scene-bound states sent back to stage 3 or 5 |
| Architecture fixed costs | start-up, stop, shot switch and warm frame measured and written down |
| Settings | the reset + one complete spec + read-back driver works; the hash is logged |
| Output spec | the pass list complete (light passes, product-part IDs, diffuse-light passes where needed); its cost measured on one frame |
| Look per light state | every region within ±10 % of the preview engine, or accepted by name |
| Temporal | flicker and sizzle ≤ production; screen-lock < ~0.3 on moving shots |

**Show:** the speed / quality table with 1:1 crops, the archetype per light state, and the fixed costs.
