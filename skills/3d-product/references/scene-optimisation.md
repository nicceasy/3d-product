# Scene optimisation: light from the start, verified before production

A product film's scene is kept light while it is built, not trimmed at the end. Every 3D stage works to a written
budget, measures what it made and fixes an outlier where it was made (§0). Stage 10 then verifies the budgets, confirms
sampling per shot and writes the estimate (§1–2). The methods it verifies with (§3–8) never change a pixel.

Contents: 0 Budget from the start · 1 Production readiness (stage 10) · 2 Measure and gate (stage 10) · 3 The
visibility audit · 4 Textures and GPU memory · 5 Heavy geometry · 6 Session and launch overheads · 7 Unused data and
geometry correctness · 8 Several master lines

## 0. Budget from the start (stages 0.5, 2, 3, 4, 5, 6, 8, 9)
**Rule.** Every 3D stage builds within the study's `budget.json`, runs the weight check at its end and fixes an outlier
at the stage that made it. Stage 10 only verifies. It optimises only when a measurement fails.

**Why: you cannot trim your way out of a heavy scene after dressing; you have to build it light.** Measured:
- **A dressed interior built without a budget needed about twice a 24 GB card.** Capped textures still left it out of
  core, at ≈ 2 min per frame against 6.7 s in core (≈ 18×).
- **After dressing, little was left to trim.** A glossy product, glass and metal mirror the room, so most objects are
  seen in reflections. The objects no ray from any camera reached were 1.1 % of the triangles. Per-shot trims took 3–7 % of
  the triangles and texture pixels, and an in-core trim saved 0.6 % per frame.
- **The cheap fixes close at approval.** Replace, proxy, don't import, a lighter light design: none of them is cheap
  once a look is approved. One never-framed prop held 46 % of a scene's triangles, but by production it shaped a
  lamp's light, so it stayed. A lamp rebuilt for noise after approval changed the night look and re-opened every
  approval it touched.
- **Light and material decisions moved seconds per frame 5–30×. Scene weight moved them ~20–25 %.** The big ones were
  real shadows under a glass cover, a hot spot in rough glass, a bulb inside a shade and rendering without a denoiser.
  Shared shader code bought the ~20–25 %, plus seconds of start-up. So the budget has two halves.

**The two budgets.**
1. **Weight:** GPU memory, triangles, the heaviest object, objects, image bytes, shader programs, script nodes, emitters
   in light sampling. Weight decides in core or out of core, and the start-up, sync and stop seconds.
2. **Convergence:** seconds per final frame per light state at the noise target. Convergence decides the render bill.
   - **The noise target:** the render's residual is at or below the film grain's σ in the darkest third of the frame.
     It is measured in the display domain the film is judged in, at 1:1, with no denoiser.
   - **The residual:** the high-pass std of the render minus a high-sample reference rendered with a different seed.

### 0.1 Write the budget at stage 0.5
1. Take the smallest card that will render finals from `setup.json` (`card_gb`). Several cards add speed, not memory:
   each holds the whole scene.
2. Take the film's machine-time budget (the node hours the user accepts, `machine_hours`) and its planned frames,
   counting handles and the end hold (`film_frames`).
   - Average seconds per frame = hours × 3600 ÷ frames, minus the fixed costs (§1 step 6).
   - Split that average per light state by its share of the frames (`s_per_frame_by_state`). A daylit interior costs
     more than a lamp-lit one (measured: §0.3, stage 5).
3. Write the noise target (§0, above) into the budget.
4. Fill the weight keys from the table below. Save `<study>/budget.json` (example: `scripts/budget.example.json`),
   versioned. Change a key only with a written reason.

| Key | What it limits | Example | Basis |
|---|---|---|---|
| `card_gb` | the smallest render card's memory | 24 | `setup.json` |
| `max_vram_share` | the weight estimate, and the renderer's own memory figure, as a share of the card | 0.5 | judgement: the measured in-core working point was 0.35–0.5 of a 24 GB card, and render settings alone (parallel samples) moved it from 10 to 19 GB |
| `max_triangles` | the scene's triangles, instances counted as render load | 10 M | judgement; measured ≈ 0.19 GB per million triangles; a dressed room with its product was 6.6 M |
| `max_object_triangles`, `max_object_share` | the heaviest non-hero object | 1 M, 0.15 | judgement; measured: one never-framed 3 M-triangle prop was 46 % of a scene and ≈ 8–10 s of sync per session |
| `hero_collections` | exempt from the per-object and per-image lines | the product's collection | the product, its prints and labels and the HDRI keep full size |
| `max_objects` | separate objects | 1,000 | measured: ≈ 55 ms of start + stop per separate object per session in a session-based engine (1,200 objects: 72 s; joined: 6–10 s) |
| `max_image_px` | the longest side of any non-hero image | 2048 | measured: set textures capped at 2048 at load worked; 1024 was once chosen for everything but the product and HDRI |
| `max_image_gb` | the image bytes on the GPU (8-bit 4 B/px, float 16 B/px) | 8 | derived: card × share − the geometry estimate − frame buffers and passes (1–2 GB at 1080p, judgement) |
| `max_shader_programs` | distinct material node-graph structures | 50 | judgement; measured: 124 distinct converted procedural shaders folded to 29 shared ones cut sampling 22–25 % |
| `max_procedural_nodes`, `max_script_nodes` | procedural texture nodes (they become script code in a converting engine); script (OSL) nodes | 100, 40 | measured: ≈ 0.26 s per script node + 0.38 s per distinct code at every session start (136 nodes ≈ 80 s); the limits are judgement (≈ 40 s of compile per session) |
| `max_mesh_emitters`, `max_sampled_mesh_emitters` | meshes with emissive materials; those still in light sampling | 200, 6 | measured: ~225,000 emissive prop triangles in light sampling were a third of a 9× time gain. Only the practicals meant to light are sampled |
| `s_per_frame_by_state` | the renderer's seconds per final frame per light state, at the noise target, passes on | 45 / 50 / 35 | from `machine_hours` |
| `machine_hours`, `film_frames`, `noise_target` | the node hours the user accepts; the planned frames (handles and the end hold included); the noise target in words | 30, 2400 | the user and the shot list; read by the stage 5 record and the stage 10 estimate, ignored by `scene_weight.py` |

`scene_weight.py` reads the Cycles side (Emission Sampling for sampled emitters). On a converted master, read the
emitters' sampling from the other engine's own setting.

### 0.2 Measure at the end of every 3D stage
1. **Weight**, in seconds, read-only, on the stage's saved scene (run it where the textures live; it flags any image
   it can't size):
   ```bash
   blender -b <scene>.blend --factory-startup --python ~/.claude/skills/3d-product/scripts/scene_weight.py -- \
     --budget <study>/budget.json --out <study>/weight/<stage>_v<NN>.json [--top 15] [--image-cap 2048]
   ```
   It prints PASS or FAIL per budget line, the heaviest objects with their shares, live modifiers that multiply
   geometry, shape-keyed and animated objects, shader programs, script nodes, the largest images, mesh emitters (and
   those still in light sampling), volumes and a VRAM estimate.
2. **The renderer's own memory** on one frame at the end of stages 4 and 5 and at stage 10: the Cycles log's peak, or
   `used_memory` in Octane's frame-buffer stats. The estimate is for trend and triage; the renderer's figure decides.
3. **The convergence record** at the end of stage 5, one line per light state. Render the state's worst frame in the
   final engine at preview resolution (960×540) at the production noise target, then write down:
   - the renderer's seconds to the target;
   - the share of pixels adaptive stopped (from a sample-count or noise pass);
   - the per-light noise share: each light pass's noise variance as a share of the sum. A pass's noise is the std of
     the difference between two independent-seed renders, ÷ √2;
   - the hot spots found in reflections and refractions, and how each was removed at the source.
4. **One record per study:** a line per stage and version. Each line holds triangles, the heaviest non-hero share,
   objects, image GB, shader programs, script nodes, sampled emitters, the estimate's share of the card, the
   renderer's figure, and seconds per frame per state. Show it at every 3D stage's gate.

### 0.3 What each stage keeps light
| Stage | Keep light | Budget lines | Measured by | Rules of thumb (measured unless marked) |
|---|---|---|---|---|
| **0.5 Probe** | the budgets, before anything is built | `card_gb`, `max_vram_share`, `machine_hours`, `s_per_frame_by_state` | `setup.json`; frames × seconds ≤ node hours | several cards add speed, not memory. An estimate several times the budget is cheaper to fix here than at stage 11 (judgement) |
| **2 Modelling** | static parts truly static (modifiers applied, no shape keys, deform modifiers or drivers); tessellation by screen need; repeated parts instanced; one named object per part; UVs at build; closed glass meshes clean | the product's share of `max_triangles`; `max_objects`; 0 deformers on static parts; 0 inward faces on closed refractive meshes | `scene_weight.py` (triangles, multiplying modifiers, shape-keyed and animated counts); the ray-parity check (§7) | engines cache static meshes: sync 15.3 → 1.4 s from frame 2, while a deforming mesh re-exports every frame. Halving the tessellation tolerance cost ≈ 3.4× the triangles: memory and sync, not sampling. The product itself was never the weight (≈ 1.1–1.4 M triangles, ~0.25 GB) |
| **3 Materials** | one parameterised shader per material family; procedurals baked, or native where the difference is invisible at 1:1; textures sized by role; greyscale maps single-channel; covers and hero gloss that converge | `max_shader_programs`, `max_procedural_nodes`, `max_script_nodes`, `max_image_px` | `scene_weight.py`; one convergence still per light state for every refractive cover and every very rough or glossy hero surface (time to the noise target, adaptive's stopped share) | shared shader code: −22…−25 % sampling and −30 s of start-up, images identical at 1:1. Under a cover with real shadows 0.9 % of pixels stopped, against 88–95 % in a lamp-lit frame. A hot spot in a rough cover needed a 16k cap; once it was removed, 4k / 0.05 matched 16k (47 s against 83 s) |
| **4 Environment** | import only what the previs cameras see or a reflection carries; set textures capped at ingest; heavy props decided at import; emitters audited; unused data purged; static dressing instanced or joined; the enclosure and the outdoors whole | every weight line; the renderer's memory on one previs frame within `max_vram_share` | `scene_weight.py` at the end of the stage; the renderer's own memory; the emitter audit (share of non-black texels per emissive map, and whether it lights anything seen) | a set loaded at 4K for everything needed ≈ 50 GB of GPU memory; capped at 2048 it still needed 34 GB and ran out of core. ~55 ms per separate object per session. The global safe-off list comes from the previs cameras (rooms behind walls are never imported) |
| **5 Lighting** | lights that converge: analytic primitives for practicals; a shade as its own fitted emitter, excluded from the bulb's light; glowing props out of light sampling; fake shadows only on closed covers, checked per state; no hot spots in rough glass; haze opt-in with its cost; clamps last | `s_per_frame_by_state`, `max_sampled_mesh_emitters` | the convergence record (§0.2 step 3) | analytic lamps + glowing props out of sampling + fake shadows on a closed cover: ≈ 9× less time at equal noise. A bulb inside a fabric shade was 89–91 % of the night noise for 5–9 % of the light. Window-lit day interiors are cap-bound. A room haze volume: ~0 sampling cost in Octane (4–7 % of the night noise), +15 % biased / +32 % unbiased in Cycles |
| **6 Engines** | the session architecture (the scene loaded across frames; one master + per-shot packs where a conversion exists; `--factory-startup` for Cycles node jobs; one GPU per frame); one complete settings spec; the passes costed | the fixed costs measured; the passes inside the estimate | start-up decomposition (sync / start-up / sampling / stop, one factor off per session); the matched-noise table (`cycles-production.md` §9–10) | fixed costs were ~75 % of a per-frame job (120 → 30 s per frame kept alive). A conversion per shot cost ≈ 13× the time and ~10⁵× the disk of a pack. 15 light passes: +7–10 % per frame, ~180 MB per 1080p frame. A user add-on forced a re-sync every frame in Cycles jobs (≈ 10×) |
| **8 FKL (cameras final)** | texture sizes from on-screen need; compose (stage 7) and render FKL in the full master at preview cost, never from a frustum-trimmed copy | `max_image_gb` re-measured | surface samples: pixels per metre ÷ UV density over every frame (§4) | 73 maps resized by need: −2.6 GB per card and −7 s of start-up, sampling unchanged (memory, not speed). Finals re-rendered from a trimmed copy came out 3–7 % and once 2× brighter (trims dropped light occluders) |
| **9 Motion** | animate only what the production path carries per frame (camera, rig, mechanisms, light state, driven values); the master untouched per shot | 0 per-shot edits to the master; 0 drivers the converter can't carry | the pack bake fails loudly on a missed still state or camera (`octane-production.md` §11) | drivers and per-still extras found late cost repeated pack re-bakes |
| **10 Readiness** | verification only (§1) | everything above, re-measured; the estimate within `machine_hours` | `scene_weight.py`, the renderer's memory, the visibility audit, the per-shot sweep, the estimate | trims for speed in core saved 0.6 % per frame (§3) |

### 0.4 When a line fails
1. **Fix it at the stage that made it, before approval:** replace, proxy, don't import, bake, fold the shader, or change
   the light design. Record the decision next to the weight record.
2. **Or accept it with a written reason** (the object is the hero; it shapes a lamp's light). For a heavy prop that
   shapes light, A/B the light it casts before swapping it for a proxy.
3. **Never buy weight back by hiding the enclosure, the outdoors, or anything a camera or a reflection sees** (§3).
4. **Never buy convergence back with exposure or a denoiser.** Fix the light or the material (stages 5 and 3).
5. **A change after approval re-opens the approvals it touches** (§2, and `render-supervision.md` §8).

## 1. Production readiness (stage 10): verify the budgets, confirm sampling per shot, estimate
**Why.** The scene has been kept light since stage 2, and each 3D stage left a weight and convergence record. This
stage proves nothing regressed, fixes each shot's sampling on its final frames, and turns measured seconds into the
machine-time bill before anything is queued.
1. **Weight against the budget.** Run `scene_weight.py --budget` on the production master and compare it with the
   stage 5 record. Every line passes, or carries a written reason.
2. **Memory, measured by the renderer.** Render one key frame per light state and read the renderer's own memory figure.
   Every shot stays in core within `max_vram_share` of the smallest card.
3. **The visibility audit, as verification** (§3). Cast rays over every final camera path. Prove the global safe-off
   list at FIRST, KEY and LAST of every shot. Trim per shot only where a shot would otherwise go out of core.
4. **Sampling per shot, before the estimate.** Start each shot from its light state's archetype (stage 6,
   `cycles-production.md` §9.2).
   - On two frames per shot (the key and one more), sweep cap × threshold against a high-sample reference rendered
     with a different seed.
   - Score by region, the darkest third first, and by the renderer's own seconds.
   - Shots that share a light state and archetype may share a swept spec; confirm it on one frame each.
   - A shot that needs far more than its archetype goes back to the light or the material (stage 5 or 3), never to a
     bigger cap without a look at the cause. Remove hot spots at the source first: one found here sends the shot back
     to stage 5.
5. **A complete settings spec per shot:** reset to defaults, apply the one spec, read it back, log its hash with every
   frame (`cycles-production.md` §9.4).
6. **The estimate:**
   - Total = Σ over shots (frames × measured seconds per frame at the shot's own sampling, passes on) + sessions ×
     (start-up + stop) + shot switches × the measured switch cost + finishing.
   - Measured on a 4-GPU node in a kept-alive session: a shot switch costs 25–50 s, a session start ~100 s, a stop
     ~85 s.
   - Write the total down and compare it with `machine_hours`. If it is over, cut by decision: fewer frames, a cheaper
     light state, or a lower cap where the noise target still holds. Never cut by silently dropping passes.
7. **A rebuilt master** (an optimisation, a fix, a new master line) is A/B'd on key frames before it replaces the old
   one (§2).

## 2. Measure and gate (stage 10)
| Check | Pass |
|---|---|
| Weight record against `budget.json` | every line PASS, or accepted by the user with a written reason |
| The renderer's own memory, one key frame per light state | in core, ≤ `max_vram_share` × the smallest card |
| Visibility lists (global and any per-shot), group render at FIRST / KEY / LAST | mean ΔE00 < 0.5, p99 < 2, ≤ 4 of 16 cells above ΔE00 2 |
| Sampling per shot | the darkest-third residual ≤ the grain σ at 1:1, no denoiser; archetype and seconds recorded |
| Settings | one complete spec per shot, read back; its hash logged with every frame |
| Estimate | written per shot (shot, frames, s/frame, hours) and ≤ `machine_hours`, or a cut decided with the user |
| A rebuilt master | the renderer's own time (not the wall clock: a shot switch can stall tens of seconds); every region within ±3 % of the old master (the acceptance rule that worked); 1:1 crops of every part the change touches |

- Judge a rebuilt master on region levels and crops. Render noise is correlated over pixels, so blur-based difference
  scores over-read. A faster master once rendered wrong (a parameter clamped to its default range); only the region
  check caught it.
- **Gate re-opening:** every shot whose master, light rig, kernel spec or sampling changed after its FKL approval
  re-opens its key-frame level check before its sequence runs (`render-supervision.md` §8).
- **Show:** the budget record stage by stage, and the estimate table.

## 3. The visibility audit (verification): hide only what no ray reaches, prove it by render
The global safe-off list is first made at stage 4 from the previs cameras (rooms behind walls are never imported).
Here it is re-verified on the final camera paths. Per-shot lists are made only for shots that would go out of core.
1. **Cast visibility over the whole camera path, per shot, without rendering.** Sample the path through the same timing
   curve the animation uses:
   - pass 1: every 4th frame plus FIRST / KEY / LAST, a 256 × 144 ray grid with a 2 % margin past each edge;
   - pass 2: every frame at 128 × 72 with a 3 % margin, for motion between pass-1 samples;
   - rays start at clip start, origins jittered over the aperture when DOF is on;
   - they continue through up to 8 transmissive / alpha / volume layers (glass, clear covers, leaves);
   - one reflected ray from every glossy, metal, glass or texture-roughness surface (+2 jittered for glossy and rough),
     and reflected rays continue through glass;
   - result per object, shot and frame: D (direct), T (through glass), Rs / Rg / Rr (reflection off sharp / glossy /
     rough surfaces). Honour ray-visibility flags and the per-frame hide state.
2. **Candidate list per shot** = objects no ray of any kind reaches, minus the rules:
   - **never the enclosure or the outdoors** (walls, floors, ceilings, beams, doors, windows, street, neighbouring
     buildings, trees, foliage), even when unseen: they shade and bounce. Measured: removing an unseen street and floor
     slab changed a shot's local light by up to ΔE00 ≈ 20; an unseen tree shades a window;
   - never product parts (they shade and mirror each other at close range);
   - never emitters active in the shot's light state (an unseen lamp still lights the room);
   - keep parts under 5 cm whose siblings are seen (small ticks and details fall between ray samples).
3. **Verify by group render** at FIRST, KEY and LAST: Cycles 480 × 270, 64 spp, fixed seed, the same texture cap on both
   sides. FULL vs FULL − list passes when mean ΔE00 < 0.5, p99 < 2 and ≤ 4 cells of the 4 × 4-binned image are above
   ΔE00 2. Anything that fails goes back in the scene.
   - Discard one warm-up render per session: Metal's first render differs from every later one by mean ΔE00 ≈ 0.1. The
     true noise floor is ≈ 0.02.
4. **A global safe-off list** (objects no shot's ray reaches: behind walls, other rooms) is hidden in every shot. Expect
   few: a glossy product, glass and metal mirror the room, and in a dressed interior most objects are seen only in
   reflections.
5. Re-run the audit whenever a camera moves, the set is re-dressed or the product model changes: the lists are keyed
   by object name.

**Typical savings (measured, dressed interior):** ≈ 40 % of the objects hidden per shot (median), but only ≈ 3–7 % of
the triangles, materials and texture pixels: most of the weight is in what the camera or the reflections see.

**Don't:** trim by bounding box in the frustum. It keeps anything with a bbox corner in view and drops the outdoors and
everything the product mirrors: measured, almost every shot changed at KEY, the worst by mean ΔE00 ≈ 20 (the view
outside a window gone).

**When not to trim (measured in an Octane kept-alive session, the master in core at ≈ half the card).** Trimmed vs
untrimmed:
- warm frame and cold start: the same within 1 %;
- first frame after a shot switch: the trimmed session ≈ 1.45× slower (a switch toggles hundreds of objects and Octane
  recompiles them);
- peak VRAM: untrimmed ≈ +1 % of the card; images identical within noise.
Trims also carry a risk only a trimmed-vs-untrimmed render catches: a hidden object is absent for the whole shot, while
verification runs only at F/K/L (an object seen only in a reflection between the checked frames).
- **Rule:** trim for memory, not for speed. When the scene fits in core, render untrimmed.
- Trims still earn their keep on the Cycles path when a shot would otherwise go out of core.

**Applying it:** toggle the hides at render time from the saved lists, never save them into the scene; a job builder
applies the shot's list to the untrimmed scene. In the Octane architecture the per-shot hides travel in the animation
pack; the master carries only the global list (`octane-production.md` §3). **Trims are not composition tools:** a
composition never hides visible dressing (it moves the camera), and a trim never hides anything a ray reaches.

## 4. Textures and GPU memory
- **Cap set textures at ingest (stage 4):** 2048 px is the default; the Octane converter caps 8-bit images at 1024. The
  product, its prints and labels, and the HDRI keep full size. Greyscale maps (roughness, metallic, height, masks) stay
  single-channel at 16 bits at most. A height map that only feeds bump needs no 32-bit float.
  - Measured: capping alone rarely fits a dressed set. Capping at 2048 cut the need by ≈ 30 %, and the shot still went
    out of core at ≈ 2 min per frame.
- Packed images reach Octane as float RGBA buffers (16 bytes per pixel) through shared memory. A few gigapixels of
  textures cost ~15 s of Octane start-up and ~8 s of stop per session. Keep textures as files.
- If a denoiser is used at all, run it on the CPU when a card is full: OIDN on a full card hung at a fixed sample.
- **Size textures from the screen need, on the real surfaces, once the cameras are final (end of stage 8).**
  1. Sample points over every visible object, each with its triangle's UV density (UV units per metre).
  2. Over every frame, need = pixels per metre at that point ÷ UV density.
  3. Halve a map only with a 2× margin, and cap the textures of objects no frame ever shows.
  4. Never change format, bit depth or colour space in the same pass. A/B at 1:1.
  - Bounding spheres fail for walls and floors: the camera stands inside them, so everything looks maximally close.
  - On a card with headroom this buys memory and a few seconds of start-up, not sampling speed (measured: −2.6 GB per
    card, −7 s, sampling unchanged).
- Stage 10 only re-measures (§1 steps 1–2).

## 5. Heavy geometry
- **Decide it at import (stage 4)** from `scene_weight.py`'s heaviest-object lines, while replacing it is still cheap.
  The choices:
  - keep it, with a reason (it shapes a lamp's light);
  - proxy it, keeping its job: a low-poly shade with an opacity map, or a measured emission distribution for a lamp
    shade. A/B the light it casts first;
  - swap it for a lighter level of detail;
  - hide it where the audit proves it unseen.
  Never decimate the product.
- A 3 M-triangle prop costs ~10 s of first-frame Blender-side sync in Octane (cached afterwards).
- B-rep glTFs have 2 triangles per flat face; densify only faces that deform (`manufacturing-variation.md`).
- Octane re-exports only meshes that are "Reshapable proxy" or deform-modified. Keep shape keys, deform modifiers and
  animated modifier values off static objects (stage 2). Bake a deformation into the mesh, or carry its value in the
  pack. Mesh type settings (Global / Scatter / Movable / Auto) behave the same.

## 6. Session and launch overheads (chosen at stage 6, verified here)
The architecture is picked, and its fixed costs measured, at stage 6 (`cycles-production.md` §9.3). The facts it rests
on:
- **Cycles on a render node: always `--factory-startup`.** A user add-on (Octane) forced a full scene re-sync every
  frame: ≈ 10× the per-frame sync. (Octane jobs are the exception: they need the add-on.)
- **Keep the scene loaded.** Loop variants inside one Blender session; hundreds of packed images take tens of seconds
  to load.
- Persistent data on for Cycles sequences and preview loops (a camera-only change ≈ 1–2 s at 640 × 360).
- **Octane:** the kept-alive session (`octane-production.md` §3), static geometry cached from frame 2, resource cache
  'All', and OSL → native nodes or bakes where parity is invisible (cutting all OSL links took start-up to first sample
  from ≈ 75 s to ≈ 4 s). One converted master + packs instead of one converted scene per shot.
- Multi-GPU Cycles on one frame is slower on most heavy frames (each device uploads the whole scene): render one frame
  per GPU, frames claimed dynamically (`render-farm.md`).
- **Share procedural shader code (stage 3).** A converter that writes one shader per material socket with its numbers
  inlined makes the GPU run hundreds of distinct functions; threads in a warp that hit different materials serialise.
  Fold structurally identical shaders into shared codes with the numbers as parameters (pin values). Measured: −25 %
  sampling time and −30 s compile per session, images identical at 1:1.
  - Declare wide min / max metadata on every parameter: a plug-in may clamp a pin to its default range (the first fold
    rendered wrong).
  - Read every value back after setting it. Fold a node only if its current code is the code the parameters came from.
- **Decompose a slow start before fixing it.** Switch one factor off per session (unlink the procedural shaders, swap
  every image for an 8 × 8, hide the heaviest mesh) and time sync, start-up and stop separately. Measure a shader's
  per-sample cost by evaluating its graph twice at a sub-nanometre offset (same image, double the work).
- **Per-object session cost.** Start + stop grew ~55 ms per separate object (1,200 cubes: 72 s; joined: 6–10 s), so a
  dressed set's stop can be a fixed minute or more.
  - Long sessions amortise it. Joining static objects removes it but moves object-space procedural patterns.
  - Never leave a session without the renderer's stop call: the host process can hang in exit, unkillable, while the
    server keeps the scene in VRAM.
- Level of detail on procedural noise per ray type (fewer octaves on diffuse bounces) saved ≤ 7 % and shifted the
  indirect light 1–2 % when the kept octaves were renormalised. The mean-preserving version saved nothing (branches and
  attribute queries cost as much). Share the code instead.

## 7. Unused data and geometry correctness
- Materials with 0 users and images used only by them: harmless at render, but they bloat packed blends. Purge them at
  ingest (stage 4).
- Zero-emission materials (strength 0, or 1.0 with a black colour: a common asset-library convention) compile no
  emission closure in Cycles and no emitter in Octane: no action. Texture-driven emission that is ~99 % black is a mesh
  light in Cycles: set Emission Sampling to None at ingest.
- Scratch blend copies pile up to 100+ GB over a study: list them and ask before deleting.
- **Closed refractive meshes: check orientation by ray parity (stages 2 and 4).** A ray from just off a face's centre
  along its normal crosses the mesh an odd number of times when the normal points into the solid; flip those faces.
  Topology-based recalculation orients each connected shell on its own and can leave a separate inner shell wrong
  (measured: 0 faces fixed vs 1,577 by parity; the unfixed mesh rendered fireflies).

## 8. Several master lines
- When production splits shots across masters (e.g. a day line and a night line), every optimisation AND every art
  update (labels, prints, replacements) goes into each line.
- Each line is A/B'd on its own shots with its own packs' overrides. A test that borrows another shot's overrides can
  hide or invent a defect (a night window override on day stills; day stills on a night master render black).
