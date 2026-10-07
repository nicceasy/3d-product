---
name: 3d-product
description: A one-shot pipeline for hardware product films in Blender, from a prompt and a reference (a design patent, photos, a video, CAD) to finished, graded sequences - a setup probe that picks the best hardware and engine, research first, the film's intention, modelling from drawings and photos, materials as designed, lived-in or studio environments, grey-box lighting, compositions with a measured compositional analysis, shot list and script together, FIRST/KEY/LAST frames, motion and the animatic, production readiness, an Octane or a Cycles production path run unattended by a plain-shell supervisor, sound design and music, DaVinci Resolve finishing and film emulation, and review on FigJam and a synced folder; every stage measured and gated, and the scene kept light from the first build against a budget. Use it whenever the user wants to concept, model, render, light, compose, storyboard, animate, film or finish a physical product (devices, audio gear, lamps, lenses, appliances) - product shots, packshots, CAD-to-render, patents or drawings, launch films, teasers, camera moves, renders that look CG, lived-in or studio sets, kit assets, scene weight, VRAM and render-time budgets, Cycles or Octane settings, render nodes, overnight renders, labels and printed graphics, sound design, music and the mix, grading, grain, film emulation and delivery - even if they don't say "3d-product".
---

# Product animation: a prompt and a reference → finished sequences (Octane or Cycles)

A tested pipeline (Blender 5.2, Octane 31.10, DaVinci Resolve Studio 21.1) written as general principles: every stage
says what works, what it measures, the gate before moving on and what the user sees; detail lives in `references/`.
Keep your own worked examples, measurements and tools in a study-notes folder outside the skill and reuse them (see
"Keeping the skill alive"). History: `references/changelog.md`; failures: `references/traps.md`.

## Run it end to end (the one-shot recipe)
Input: a prompt and a reference. Output: graded sequences (Octane or Cycles), review videos in a synced review
folder, stills on FigJam.
★ = the user decides; agents stop and wait there. Everything else is gated by measurement and shown as a checkpoint.

| # | Stage | Measured gate before moving on | The user sees |
|---|---|---|---|
| 0 | Brief intake + research | coverage matrix, conflicts register, regime targets; nature + lead element | brief + reference sheet, ≤ 60 min |
| 0.5 | Probe the setup | `setup.json`, bench seconds per host and rung, `budget.json` | the setup and the recommendation |
| 1 | **Intention** | feature × pose × model-support table; target length by arithmetic | ★ go / redirect |
| 2 | Modelling | overlay, photo-match and held-out residuals; mesh QA; 0 undeclared overlaps in every pose; weight line | overlay + photo-match sheets |
| 3 | Materials + textures | swatches by number, patch ratios, albedo bands, closest-framing check; material cost line | swatch + audit sheets |
| 4 | Environment: location or studio | causality, 0 visible overlaps, albedo + silhouette audits, realism manifest; set in core on budget | previs sheet with its numbers |
| 5 | Lighting, grey box first | reads in every state on real product materials; convergence record per state | light-state sheet |
| 6 | Engines, kernels, settings | matched noise at the noise target, temporal metrics, archetype per state, costed output spec | speed / quality table |
| 7 | **Compositions, shots and script, together** (a loop) | compositional analysis on every comp; every source cross-referenced | ★ stamps comps each round; ★ locks the shot list |
| 8 | FIRST / KEY / LAST | analysis + CoC + reads + manifest read-back + independent audit + main's check | per-act sheets |
| 9 | Motion, animatic and final cut | motion QA, analysis re-run on every moved frame, edit gate | ★ approves the animatic and the cut |
| 9.5 | **Sound and music** | events on their frames, key/tuning/tempo, loudness steps and entries | ★ picks the music by ear; ★ approves the lock |
| 10 | Production readiness | weight in budget, renderer memory in core, per-shot sampling swept, estimate written | the machine-time estimate |
| 11 | Production render: Octane or Cycles path | FKL in the final engine level-checked vs approved; counts, jump scan | ★ explicit "go" per act |
| 12 | Finishing | frames match their numpy twins, grain re-measured after encode, version stamped | graded clips |
| 13 | Review + delivery | videos in the review folder, stills on the board, Resolve project, full paths | the finished film |

Stage 1 sets the intention every later stage serves. Stages 2–6 build the product and its world once, **light from the
first file**; 7–9 decide the film at preview cost (compositions first, then the frames, then the motion and the cut);
9.5 builds the sound on the near-final cut while 10–12 spend the machine time. A fix loops back one stage, not to the
start. Orchestration (`orchestration.md`: roles, briefs, user gates, permissions, status) runs through all of it.
**Roles, not machines:** stage 0.5 finds what fills each role: the *workstation* (scenes, jobs, previews, boards),
*render nodes* (throughput), *shared storage*, the *finishing host*. One machine can hold all of them.

## Rules over every stage
- **Research first, paired with reference images** (`research-protocol.md`): parallel background tracks, URLs + what
  to measure in each image, evidence tags, TL;DR first. Research sets hypotheses; renders decide.
- **Measure every stage.** Each stage ends with a measured record: numbers against stated pass values, the tool or
  method, and a sheet; its reference holds a **Measure and gate** section. The eye still decides (verdicts are
  semantic), but after the numbers, never instead of them. A gate that a user note breaks is reported with a fix.
- **Light from the start** (`scene-optimisation.md` §0). Stage 0.5 writes `budget.json` from the smallest render card
  and the machine-time budget. Every 3D stage (modelling, materials, environment, lighting) writes a weight line for
  what it built (`scripts/scene_weight.py --budget`) and fixes outliers where they are made: heavy assets, textures
  above their role, distinct shader programs, emitters that light nothing, lights that don't converge. Stage 10 only
  verifies. Why: weight found at production can't be replaced; measured, one never-framed prop held 46 % of a scene's
  triangles, out-of-core frames ran ~18× slower, and lamps redesigned for noise after approval changed approved looks.
- **Fast feedback loops, vital** (`fast-feedback.md`): a visible result within 30–60 min, a checkpoint every 1–2 h, a
  machine-time budget before anything runs. Climb the cost ladder: 640 px clay → 960×540 → 1:1 crops → full res only
  to confirm; one frame → FIRST/KEY/LAST → one shot → all shots. **Deliver the first complete build at once.**
- **Only what works.** Failures are one-line "don't"s or live in `traps.md`. Comfy and AI image passes are out (in
  testing they bent the scene and invented content); AI music is in (stage 9.5).
- **Version up, never overwrite** (models, generators, caches, looks): copy → edit the copy → new versioned outputs →
  CHANGES.md last. Never alter the user's originals or delete shot files. **A change request versions up the approved
  file and changes only what the note targets**, first proving the start reproduces the approved frame (`editing.md`).
- **Always 32-bit float EXR (ZIP), scene-linear, a light group per emitter**; review JPGs and MP4s derive from them.
- **Set render settings completely, every time** (both engines): reset to defaults, apply one complete spec, read it
  back, log its hash with every frame. A saved scene keeps whatever was last set (measured: frames ran to the cap).
- **Render intent, not age:** the factory finish and factory-new geometry; dust and wear only as a switch, off.
- **The user's notes are hard requirements**; keep extra shots (no note ≠ rejected); "scrap" = move on, keep the files.
- **Prove the plumbing, predict then measure, look before you judge:** a known chart and a deliberate 4× change through
  any new pipeline; numerical twins; captions corrected to what the image shows; before/after proofs in the light that
  reveals the change, with a difference map.
- **Review surfaces:** videos to a synced review folder (iCloud Drive or similar; one shallow folder per review
  section, nothing else there), stills and sheets to the FigJam board, every deliverable reported with its full local
  path in its own code block. User photos and
  third-party images are private reference: never on a board or artifact.

---

## 0 · Brief intake and research
**Why.** Every later choice follows from what the product *is*; research has changed products before a single render.
**Do.**
1. Name the product's nature in one sentence and pick the **lead element** that proves it (`elements.md` §11).
2. Identify the product and its variants: one row per reference (what, variant, use, resolution), deduplicated by md5
   (`reference-detailing.md` §1). A patent PDF: ask before downloading. Footage: frames at ~1 fps into one library.
3. Launch the research tracks in one message (`research-protocol.md` template, each with a budget and a 30–45 min
   TL;DR): P1 identity and specs, P2 details and materials, P3 story, light and photographic references with measured
   targets, R1 *features* (signature functions as shot ideas, plus model gaps). Reference video: `/analyze-youtube`,
   then measure frames. Run stage 0.5 with the brief so budgets are in measured seconds.
4. Open the study folder (THINKING.md, STATUS.md, research/, checkpoints/) and a FigJam board (`figjam-board.md`).
**Measure** (`research-protocol.md` Measure and gate): a reference-coverage matrix (part × view × variant); a conflicts
register, each with how it will be decided; a targets table per light regime measured on references.
**Gate.** Nature + lead element; variant table; matrix, register and targets; every hero part has ≥ 2 independent
sources or a labelled estimate; a one-page brief (problem, object, ritual, promise). **Show.** The brief, the reference
sheet, the nature sentence.

## 0.5 · Probe the setup
**Why.** Pick the best setup available, not an assumed one, and set the budgets everything is built to.
**Do.**
1. `python3 ~/.claude/skills/3d-product/scripts/probe_setup.py --out <study>/setup.json [--deep] [--bench]
   [--priority realism|speed]`: reads `~/.config/3d-product/site.json` (example `scripts/site.example.json`) and probes
   read-only in ~4–7 s: GPUs, Blender, Octane, Resolve or the numpy look chain, ffmpeg, nodes over ssh, shares, link.
2. Read the recommendation: the finals path (Octane when a node has the add-on and a server and the brief needs light
   through glass; Cycles otherwise), node, GPUs per frame, preview host and ladder, finishing host, storage, notes.
3. Bench each rung once (the probe times one local clay frame; time the others into the setup notes), record the
   user's per-project constraints, and write **`budget.json`** (`scripts/budget.example.json`; keys in
   `scene-optimisation.md` §0). A node running another project's queue counts as missing. No node: all roles local.
**Don't:** install, restart or kill anything to make a probe pass. **Gate** (`site-profile-example.md` Measure and
gate): every role filled or marked missing; bench seconds and `budget.json` written. **Show.** Setup, seconds, budget.

## 1 · Intention
**Why.** The author's rule: "overall intention should be first". What the film is for and says decides the light, the scale, the
subjects and the story; every later composition and shot must serve it.
**Do.** Write it at the top of THINKING.md; the shot list opens with it.
1. **What the film is for and says:** audience and channel, the claim in one sentence (the product's nature as a film),
   the feeling, how it ends, what it must never imply (the honesty filter, `environments.md` §1).
2. **The story seed** (`shots-and-script.md` §2): the format, a logline, one line per act, the target length (planned
   shots × the format's measured average shot length; 15 s ≈ 8 shots; a ~2 min ritual ≈ 25–30 shots).
3. **The light arc:** named light states, one per shot; if time passes, a monotonic schedule on edit time (`lighting.md`
   §9) with each transition marked by a shot (`transition-shots.md`).
4. **The feature table** (`shots-and-script.md` §0): feature → the poses and product states that show it → whether the
   model supports each → shot ideas. Gaps and stage-0 conflicts become stage-2 work items.
5. A new, designed product: brief → design tokens → physics first (optics, caustics, OKLCH, Beer–Lambert;
   `hard-surface.md`, `glass-light.md`).
**Gate.** The intention fits a short paragraph; every feature has a supported pose or a named gap keyed to its shots.
**Show.** ★ The intention, logline, light arc and feature table; the user may redirect.

## 2 · Modelling
**Why.** For a real product the photographs are the judge; a pixel offset is a model error until proven otherwise. The
tessellation is what renders, and what is built here is carried by every later frame.
**Do.** Measuring and the envelope may start with stage 0; detail budget, poses and hero tessellation wait for ★ 1.
1. **Sources by authority** (`patent-to-model.md` §0): supplied CAD → the maker's drawings → press orthographics →
   design patents → camera-solved photos and footage → judgement. One verified scale, `MEASURE.md`; build123d B-rep,
   **one named solid per part**; overlay QA by HLR on every figure (median ≤ 0.4 mm, p90 ≤ 3 mm); specs you did not fit
   must close. **Hold one source out** and validate on it.
2. Detail from references (`reference-detailing.md`): D-tracks, patch part by part, variants as generator flags (each
   exported and gated, never mixed); **camera-match** each useful photo (4–10 px rms); every number tagged with its
   source; a labelled estimate (value ± uncertainty, the measurement that would settle it) where evidence ends.
3. New products: representation by part type (`hard-surface.md`), the zebra tunnel on every hero surface.
4. Moving parts as rigid groups posed about real axes, poses solved from constraints (scan, bisect, check the branch).
   **The pose matrix** (`patent-to-model.md` §6): every group's poses × the others' states, plus every pose the shot
   list adds; residuals, clearances, designed contact, carried parts at distance 0. Nothing floats.
5. Secondary forms (`manufacturing-variation.md`): levels 0/1/2 as baked mesh data, level 0 default; propose a level
   from a strip-light A/B; the user confirms it on FKL frames.
6. **Keep it light while you build** (`patent-to-model.md` §7): tessellate by screen need (chord ≤ ¼ px at the part's
   closest framing; glass ≤ 0.05 mm; unseen faces coarse), instance repeats, static parts static (modifiers applied, no
   shape keys or drivers), UVs at build with prints in their own UV layer, one rest pose + a pivots file, collections
   by role. **Publish one engine-agnostic master per version** (§8): manifest, validation report, importer.
**Measure** (`patent-to-model.md` Measure and gate; `hard-surface.md` §2b): overlay and camera-match rms, held-out
residual, size gate, **mesh QA** (normal error p99 ≤ 0.5°, slivers < 5 % on gloss, no leaning poles), overlap volume
per part pair (declared embeds listed), the pose matrix, a weight line against `budget.json`.
**Gate.** 0 undeclared overlaps in every matrix cell (absolute on a first build; "no new" only between versions);
residuals and clearances in tolerance; contact where designed; mesh QA clean; every variant gated; weight in budget or
each outlier decided. **Show.** Overlay and photo-match sheets (private if they hold user photos), fix crops, the weight.

## 3 · Materials and textures
**Why.** Realism is light, not texture; but every component must still be the right physical material, as designed,
at a cost the final engine can carry.
**Do.** (`reference-detailing.md` §6, §6b)
1. Measure each part on the photos (colour lit/shadow, highlight width, texture rms and feature size at a known mm/px),
   then **calibrate on swatches** under the photo's light, one variable per swatch, **passed by number** (grazing and
   head-on inside the photo's spread).
2. **Audit every identifiable component** (→ `MATERIAL_AUDIT.md`), props too. Where a reference frame exists, **audit
   by patch ratios** (render/reference, scene-linear, same look) and diagnose each miss as environment, light or
   material before changing anything.
3. **Albedo from a cited source or a measured photo mean**, never a name or a brightening chain (kit libraries measured
   2–3× off both ways). Judge every mottle and bump at the **closest planned framing**, two seeds.
4. Intent, not age: separate design finish from wear; age layer `dust=0` by default.
5. Prints and labels traced from photos, not drawn, mapped through the print UV layer; relief for macro-visible marks.
   New graphics: `graphics-labels.md`. Patterned materials follow the object's construction (per-part UVs by the real
   pattern direction, true scale, consecutive leaves; stripe-card and shimmer checks).
6. **Keep it light** (§6b): texture size by role, greyscale maps single-channel, procedurals from a few shared
   parameterised groups (measured: 124 distinct converted shaders → 29 shared cut sampling ~25 %), bake what the final
   engine converts badly, emission only where a light is meant.
7. **Silhouette detail is displacement** (brick, stone, tile at corners): a bump never changes an outline; derive the
   map from the albedo, judge it at the corner in the shot's light (engine settings: `/octane`, if installed); record it in the realism manifest.
8. Glass: every transparent layer listed and checked per light state; roughness is a per-state trade (`glass-light.md`
   §5). **Don't:** a Base Color tint on glass (use volume absorption).
**Measure** (`reference-detailing.md` Measure and gate): swatches, patch ratios, albedo vs target, the two-seed check,
the glass layer list, a **material cost line** (texture MB, distinct procedural graphs, glass layers, emitters).
**Gate.** Patches within ~±10 % or a written cause; albedo within ~×1.3 of target; every component checked in writing.
A material change after stage 5 re-runs the light-state sheet. **Show.** Swatch and audit sheets with their numbers.

## 4 · Environment: location or studio
**Why.** A set that can't explain itself reads as CG; the product without its system breaks causality faster than any
material flaw. A set built heavy can't be trimmed light later: the weight is in what the camera and reflections see.
**Choose the branch** (claim first, `environments.md` §1): **LOCATION** when the claim is the product in its life (a
film whose light marks time, a storyboard in one place); **STUDIO** when it is the object alone (packshots, launch
abstraction, glass and optics demos); both → build the location, shoot studio sets from the same model; **NATURE** →
**/3d-nature**, then stage 5.
**LOCATION** (`alive-environments.md`, every time, even for "just add an environment"):
1. The set bible: who, what just happened, the time stack, region, palette lock, 3–5 materials, exclusions, a wear map;
   orient the room for the light you want. Research paired with measured reference images.
2. Real assets (a kit library; USD + MaterialX → Principled, thin glass): a complete shell and a real exterior; hero
   supports modelled; the room probed before anything is placed. **Pre-flight every asset at import** (§3b): a probe
   per asset, texture variants by role, heavy assets flagged and decided, repeats instanced, kit glass → thin panes, kit
   emitters audited, bible exclusions never imported; never remove the enclosure or the outdoors (they shade, bounce).
3. Previs cameras before dressing; a top-down plan render to aim the sun by geometry; sun reach per light state.
4. **Dress in context: the product's system first**, then hero props → dressing → background → breakdown → life pass,
   filled by the numbers. Colour from objects, each accent twice. Props age; the product doesn't.
5. **No interpenetration:** a BVH overlap audit between every pair of props (~1 mm); fix the generator, not the instance.
6. **Audits** (§10): quick audits (causality, repetition, squint, shape, scale); the **in-render albedo audit** (before
   any light energies); the **silhouette audit** (straight runs and knife edges, fixed by displacement, edge units or
   bevels); the **realism manifest** (every realism feature of the master, each switch on for finals).
7. Composition-time dressing is logged at stage 7; **hide only what no ray reaches over the whole move**.
**STUDIO** (a builder from a JSON spec, `pipeline-commands.md`): metal on a sweep or cards; glass on dark / bright field
or a gradient ground; a fabrication story; the gatekeepers (`lighting.md` §2); camera-invisible flags for black gloss.
**Measure** (`alive-environments.md` §11): causality 10/10, context, fill counts, overlaps, repetition, squint, texel
density, silhouette runs, albedo bands, sun reach, the budget table (`scene_weight.py`) and the renderer's own memory on
one previs frame, preview s/frame. Studio: world/key 0.5–2 % and set-only twin 25–30 % from light groups.
**Gate.** 0 interpenetrating pairs visible to any planned camera (the rest listed); no flagged silhouette run visible;
albedo in band; the set in core on the smallest card within budget; the global safe-off list verified (mean ΔE00 < 0.5,
p99 < 2). **Show.** The previs contact sheet with these numbers in its caption, and the budget table.

## 5 · Lighting, grey box first
**Why.** Renders read as CG mostly because of the light; light shapes are composition. The lights also set most of the
render bill: measured, the light setup moved render time ~9× at equal noise.
**Do.** (`lighting.md`)
1. Grey box: clay on the set except glass and emitters, prints as ink; 960×540, 8 spp + OIDN for previews; a light
   group per emitter from the first frame. Energies only after the albedo audit.
2. Motivated light by branch: location = the sun split from the sky map and aimed by geometry, thin-glass windows,
   practicals after sunset; studio = the gatekeepers (a set-only twin at 25–30 %, a room at 0.5–2 % of the key, sources
   ≥ 5°, WB at the key's CCT). **Haze is opt-in** (§2): a named job, A/B'd, its cost recorded.
3. **Name the light states once** (sun, sky, lamps, exposure, state-dependent material values), one per shot; **one
   master serves every state** (§3). Blackbody practicals (tungsten ~2700 K); every emitter in a light group.
4. **On black gloss, three-point lighting happens in the reflections** (§5): key, fill and rim are bright things on
   each face's mirror ray; a fill is a real surface lit by real light, its radiance measured in the EXR.
5. **"Reads" is two measured gates** (`scripts/reads_metric.py`): R1 void share > 0.30 fails; R2 outline separation
   < 0.20 fails. Clay can't fail them, so the light-state sheet shows **the product in its real materials** on 3–5
   cameras per state. Never fix a fail with exposure: pick the light from §5's table.
6. **Lights that converge** (§8): a pass and a noise budget per light (noise share vs light share); a bulb in a shade
   becomes an analytic sphere at the filament with the shade as its own emitter; glowing props out of light sampling;
   no added light also blocks light; the glass sampling aid per cover × light state only where levels agree within
   ~3 %; a light fit to a reference frame where one exists.
7. **Reflections and hot spots** (§6): fix at the source (an environment rotation sweep the user picks from, a moved
   practical, a flag), never with samples or a post filter.
8. **A film that moves through the day** (§9): monotonic on edit time, practicals on once at a motivated moment, the
   window as the clock (at night we see out), one HDRI series, WB follows the key. Plan dusk and low sun here.
**Measure** (`lighting.md` §10): R1/R2 per state and camera, fill radiance, crush, groups sum to the beauty, and the
**convergence record** per state (seconds to the noise target, adaptive's stopped share, per-light noise share, hot
spots removed). **Gate.** R1/R2 pass in every state; crush ≤ 1 %; groups within 1 %; no light whose noise share far
exceeds its light share; seconds within budget. **Show.** The light-state sheet (states × 3–5 cameras) with numbers.

## 6 · Engines, kernels and render settings
**Why.** The engine decides what light is possible; the settings and the architecture decide the render bill.
**Do.** (`cycles-production.md`, `octane-production.md`; Octane engine detail in **`/octane`**, a separate skill if
installed, or the Octane manual)
1. **Choose the finals path by the brief, then the hardware:** sunlight through glass in a scene → **Octane** where a
   node has it; metal, plastic, lacquer, throughput → **Cycles**; a glass product in a studio → Cycles + a LuxCore
   caustic layer (`glass-light.md` §7). Previews, compositions and FKL previews: Cycles on the workstation (960×540,
   256 spp + OIDN) through a **frozen preview look** (view transform + a neutral grade).
2. **Pick the architecture and measure its fixed costs:** the scene kept loaded across frames (kept-alive session or
   persistent data), one master + per-shot packs where a conversion exists, `--factory-startup` and one GPU per frame
   for Cycles nodes; decompose a frame into sync, start-up, sampling, stop (measured: fixed costs were ~75 % of a stock
   per-frame Octane job). This decides how stage 9 authors motion.
3. **No denoiser by default:** sample to the noise target (residual ≤ the film grain's σ in the darkest third, 1:1).
   A colour-only post denoise of converged frames only when the user asks; keep the raw beauty.
4. **Sampling archetypes per light state** (cap × threshold on each state's worst frame vs an independent high-sample
   reference; adaptive proven with a sample-count AOV): *converging*, *cap-bound*, *scene-bound* (fix in stage 3 or 5).
5. **Temporal checks** on a still and a moving range: level jitter, sizzle, screen-lock correlation of the residual.
6. **Output spec, complete and costed:** beauty and raw beauty; a light pass per emitter role summing to the beauty;
   diffuse/specular splits; Z, normals; **IDs for the product's parts**; costed on one frame (measured ~+10 %/frame).
**Don't (measured):** NRC, the Photon kernel, coherent 1.0 + dispersion, coherent > 0 without static noise, a denoiser
inside the render (erases fine detail; speckle and mottle on dark finishes).
**Gate** (`cycles-production.md` §9–10, both paths). Every state meets the noise target in its budgeted seconds; temporal
metrics no worse than production; finals vs preview engine within ±10 % per region in every state after a grey-card
calibration, or the difference is physical and accepted by name. **Show.** The speed / quality table with crops.

## 7 · Compositions, shots and script, together
**Why.** The author: "composition shots and script should go hand in hand", and "composition and first key last frames
should happen before motion". Compositions come first; the shot list is built around the stamped ones; every
composition and shot serves the intention.
**The loop** (`composition-analysis.md`, `composition-exploration.md`, `greybox-composition.md`, `shots-and-script.md`):
1. **The intention and the story draft decide what to explore:** beats, subjects, light states and poses, read against
   the product's vocabulary and the set's measured traps → the archetypes to sample.
2. **Stand-alone compositions first:** archetypes → 20–30 cameras each → **geometric pre-gate** (measured kill rate
   41–77 %) → previews in the frozen preview look → the analysis → eye pass ("OK" is a reject) → repair one factor →
   50 selected with quotas → finals on the render node → the board → ★ the user stamps (read back with `use_figma`).
3. **Compositional analysis, required** on every candidate (`composition-analysis.md`): the pre-gate; frame gates
   G1–G9 with their numbers (subject, intact, focus, wins, edges, tangents, lines, reads, glossy black); the analysis
   (placement on an anchor or centred, never drifting; eye path; divisions; negative space; masses; balance; size by
   role); **scene–subject harmony** (tone, rivals and clutter, colour, light, depth and scale, set); then the eye pass.
   Code measures (`scripts/comp_analysis.py frame | sameness | cuts`), the eye decides; each frame gets its numbers
   and a one-line justification on the board.
4. **Grey-box lock-in, always, between stamped compositions:** ≥ 30 legal simple moves (a generator, a rate under the
   ceiling, the planned duration), KEY = a stamped comp, the other end passing the analysis too; physical cameras
   (focal f(1+m), f-stop N(1+m)), clay except glass and emitters, real DOF, scored as a move; 1280×720, 64 spp.
5. **Write the shot list and script around the picks** (`shots-and-script.md`): stamped comps, shots marked good,
   quoted notes (hard requirements), unmarked shots (kept). Per shot: "from X to Y", how it serves the intention,
   FIRST / KEY / LAST, the move, the light state, what is heard. **Never replay an action across a cut**; a match cut
   shares its framing; no jump cuts (≥ ×1.5 or ≥ 30°). Music that appears on screen is chosen now.
6. **Close the loop:** a beat with no strong frame requests new compositions; a weak shot is folded or moved. At the
   lock, run the film-level checks (neighbour sameness, placement across cuts, covers that read). ★ The user locks.
Craft that held: aim by lens shift, not yaw; focus on the visible surface; move props like a photographer, each move
logged (object, delta, why); hiding is not a composition fix.
**Gate** (`composition-analysis.md` Measure and gate). Every frame passes the gates and harmony checks, or carries an
exception the user accepted (quoted, it travels with the frame); every † item met or explained; every source
cross-referenced; ★ the shot list locked. **Show.** Each round: the board with stamps and each frame's numbers, then the
shot list with its cross-reference and the changes since the last round.

## 8 · FIRST / KEY / LAST
**Why.** The bar, in the author's words: "subject to subject, strong comp to strong comp, intentional motion, subject in focus every
time." A wrong frame caught here costs minutes; in a sequence it costs an hour of rig time.
**Do.** (`fkl-frames.md`)
1. Frames as data: a spec → one harness (master, rig, safe-off list, practicals, spin blur, cards, racks in dioptres) →
   EXR + previews → the shot JSON. **FIRST and LAST are outcomes of the move chosen for them** (stage 7): a weak end is
   repaired by direction, rate or t_KEY, never by extrapolating a move that wasn't chosen for its ends.
2. Gates in the harness: the analysis, **CoC on the subject ≤ 2 px at 1920** on its mask, **reads on every frame** (a
   fail goes back to stage 5), fill radiance, the **realism manifest read back** with the silhouette and hot-spot audits
   re-run, a restore check of composition-time dressing. **Close-ups** (§2b): split the subject's depth and stop down
   within diffraction (`scripts/macro_focus.py`); a mirror-like foreground must reflect dark (a ray probe).
3. An **independent auditor** (a fresh agent) checks every frame, shot and cut (§4); every cut N LAST → N+1 FIRST: eye
   jump ≤ ~25 % W, ≥ 30° or ≥ ×1.5, every mechanism's state equal across the cut.
4. The builder fixes by diagnosis; the auditor re-checks; **main checks every shot itself**, then declares "cameras
   final for Act X". Then size set textures by on-screen need (2× margin, A/B at 1:1) and confirm the variation level.
**Gate** (`fkl-frames.md` Measure and gate). Audit pass on every frame and cut; main's check. **Show.** Per-act FIRST |
KEY | LAST sheets (clean and marked, with the numbers) on the board.

## 9 · Motion, animatic and final cut
**Why.** Motion is a render element: easing, speed and mechanism timing claim mass and precision. The animatic is
where timing is seen for the first time, so the edit and the script are finalised here.
**Do.** (`camera-motion.md`, `greybox-animation.md`, `editing.md`, `animation.md`)
1. **Simple moves** (`camera-motion.md` §0): one constant move per shot anchored on the approved KEY, ≤ 2 animated
   dimensions (a primary + a subtle secondary ≤ 0.25); the aim locked, parallel or panning at a constant rate; lens,
   roll and shift constant; no easing except the written ease budget (an on-screen start or stop, a final settle).
   **Then the operator layer** (§6): slow 1/f drift under ~0.7 Hz, 1–2 % speed breathing, a 0.1–0.2 s follow lag;
   camera-local, KEY exact, gated in px.
2. **Speed ceilings** (push ≤ 10 %/s of the field, arc ≤ 4°/s, truck/pan ≤ 6.5 % W/s) computed before render. Racks in
   dioptres, only across ≥ 5 DOF. Lock the camera while a mechanism acts.
3. Mechanisms on physical curves (a hinged cover by hand: minimum jerk 2.5–3 s; a lift 0.75–1 s ease-out; a motor
   spin-up τ ≈ 0.4 s, coast τ 1.6–2 s), the product alive in every shot. **Animate light:** rigid parts on pivots
   driven by per-frame channels the production path can carry; nothing live that the converter can't carry; riding
   parts get sub-frame QA on the saved shot file (`greybox-animation.md`).
4. **The hand-offs are files:** the shot JSON and the **per-frame edit JSON** every consumer reads (operator layer,
   render packs, spotting, grade ramp, conform). Cut points (`editing.md` §3): enter moving, leave before arrival.
5. **Cut it like the reference** (`editing.md`): about 2 min, holds set by information, cuts on the product's motion, no
   similar neighbours. Inventory → plan → paper edit → build → assemble, gated; one transition shot per light change
   (`transition-shots.md`). The final shot plays through the end hold, never frozen. VO-led films time from silence
   detection and per-segment transcription.
6. **Finalise the edit and the script at the animatic** (SHOTLIST.md / SCRIPT.md first, then the JSONs). **After any
   camera or cut change, re-run the analysis** on the new FIRST, LAST, the edit's in/out frames and every 12th
   in-between, and the cut checks on the real cut frames; a failing frame goes back to stage 8.
**Measure** (`camera-motion.md` §7, `editing.md` §5; `scripts/motion_qa.py`): per move, constant increment, legal generators, speed,
image flow, clearance ≥ 20 mm, 0 occluded focus frames, KEY exact, operator px gates, FIRST/LAST shift vs the approved
stills; per cut, runtime, shot lengths, similarity, motion on both sides, continuity; the packs' cameras identical to
the approved source. **Gate.** All pass or the exception is named; the script matches the cut. **Show.** ★ The motion
review after every camera change (a grey playblast of *every* shot + the edit), then the review ladder (`editing.md`
§7), each approved; no lit rung before the playblast is approved.

## 9.5 · Sound design and music
**Why.** Sound is the last layer that carries the story; the user judges it by ear and by how it moves ("avoid big
changes in volume"). It is spotted from the animation data, so it starts on the near-final cut, beside stages 10–11
(a beat-grid teaser is music-first, `animation.md` §1).
**Do.** (`sound-design.md`)
1. Research first; a sound script with the music map, confirmed with the user before the first build; a temp track or
   tempo map at the animatic.
2. The spotting sheet from the edit JSON's channels, regenerated per edit version: events on their frame or one late;
   beds never cut, perspective eases ±3 dB around cuts; source music worldized; the music the star.
3. Quiet parts as tonal beds (a sub pedal on the tonic, sparse open intervals, no broadband noise), sweeteners in key.
   Measure every take's key, tuning and tempo: generators ignore what is asked.
4. AI music, quality first: complete natural pieces, raw takes to the user by ear first, phrase-aware fits with no
   stretch, endings that ring; a fault inside a song is isolated and resynthesised. The user's ears decide.
5. Loudness: −16 LUFS-I, ≤ −1 dBTP; **gate the steps, not the range** (no short-term change above ~3 LU/s at a
   transition); entries after a song or near-silence rise from ≤ −30 to −40 dB over ~2 s; stems sum to the master.
   Verbal level notes map to numbers on the named layer only; a note that moves a synced event flags its chain.
**Gate** (`sound-design.md` §12; `scripts/loudness_profile.py`). Events at 0 to +1 frame; key, tuning and
tempo measured with beds tuned to them; loudness, steps and entries pass (a fail from a user note reported with a fix);
stems residual ≤ ~−50 dB. **Show.** The first build at once, then each version on the latest picture with its loudness
PNG; ★ the user picks the music by ear and approves the lock.

## 10 · Production readiness: verify the budgets, sweep sampling, estimate
**Why.** The scene was kept light from stage 2 on; this stage proves nothing regressed, fixes each shot's sampling on
its final frames, and turns measured seconds into the machine-time bill before anything is queued. Optimising here is
the exception, used when a measurement fails.
**Do.** (`scene-optimisation.md`)
1. **Weight check:** `scripts/scene_weight.py --budget budget.json` on the production master vs the stage-5 record;
   **memory measured by the renderer** on one key frame per light state, in core within the budget.
2. **Visibility audit as verification** over every final camera path (direct, through glass, off reflections): the
   global safe-off list proven at FIRST / KEY / LAST (mean ΔE00 < 0.5, p99 < 2); **never the enclosure or the
   outdoors**, never product parts or lit emitters. Trim per shot only when a shot would go out of core (measured:
   speed trims saved 0.6 % per frame and risked a missing reflection).
3. **Sampling per shot, before the estimate:** from the state's archetype, sweep cap × threshold on two frames per shot
   against a high reference (`octane-production.md` §6, `cycles-production.md` §9), scored by region (darkest third first) and seconds. A shot far
   above its archetype goes back to stage 5 or 3, never to a bigger cap blind.
4. **One complete settings spec per shot**, read back, its hash logged per frame.
5. **Estimate:** Σ (frames × measured s/frame with passes on) + sessions × (start-up + stop) + switches × switch cost +
   finishing, against the machine-time budget; cut by decision, never by dropping passes.
**Don't:** trim by bounding box in the frustum (it drops the outdoors and everything reflections see).
**Gate** (`scene-optimisation.md` Measure and gate). Weight in budget or accepted; every shot in core at the
renderer's figure; lists render-verified; every shot has a swept, hashed spec; the estimate written and in budget; a
rebuilt master passes an A/B (renderer time, every region ±3 %, 1:1 crops). **Show.** The budget record stage by stage
and the estimate table (shot, frames, s/frame, hours) before the queue starts.

## 11 · Production render: the Octane path or the Cycles path
**Why.** The same gates feed both paths; only the render step differs. Nodes are for throughput, after approval.
**Octane** (`octane-production.md`; load **`/octane`**, if installed, for every engine decision): ONE converted master + a small
animation pack per shot in ONE kept-alive session (~30 s and 50–100 KB per shot vs ~6.5 min and ~5.7 GB to convert
each); on Windows launch through an interactive-session task (ssh jobs run in session 0). **Cycles**
(`cycles-production.md`, `render-farm.md`): one packed .blend per shot, `--factory-startup`, one Blender per GPU,
frames claimed over placeholders.
**Both paths, in order:**
1. **FKL in the final engine first**, per act, through the approved look, with a **key-frame level check** vs the
   approved frame (same look, grain off: level ±5 %, mid-tone colour ≤ ~2 ΔE, unless the change was asked for). **Main
   checks every FKL frame itself** (1:1 prints, under glass covers, dark gloss noise, focus). Then ★ the "go" per shot
   or act. **The gate re-opens** for every shot whose master, rig, spec or sampling changed after its approval.
2. Sequences: overwrite off, placeholders, one EXR per frame; the first frame of every run opened and its layers
   listed; after any interruption test recent frames. **Light passes with every final** (a wrong light is a comp gain).
3. **Jump-scan every finished shot** (consecutive-frame difference at 1/8 res): a step > ~3× the shot's median or
   exactly zero (a stale buffer) is explained, and the frame's metadata checked.
4. **Unattended runs: a plain-shell supervisor owns the run, never an agent** (`render-supervision.md`,
   `scripts/render_supervisor_template.sh`): node, share, session, power cap (never raised), GPU count, server, hang
   check, relaunch with skip-existing and a cap, drift alerts (a frame > ~1.5× its estimate, a spec-hash change,
   missing passes). Finishing runs as frames land.
**Gate** (`render-supervision.md` Measure and gate). "Go" given; frame counts complete on the node; per-frame time
within the estimate; jump scan clean. **Show.** FKL in the final engine beside the approved previews, then each shot.

## 12 · Finishing
**Why.** Keep the render's light; borrow a reference's colour. A first solver was judged "missing a lot of the light
quality from the original renders".
**Do.** (`finishing.md`)
1. **Choose the finish once per film:** the gentle look chain or **film emulation** (§7); never both solvers.
2. Gentle chain per frame: (a post denoise only if the user chose it) → EV 0, no WB by day → Pro-Mist-like 1/8 → a
   reference-matched look → 35 mm grain fresh per frame → 16-bit → ProRes 422 HQ + H.264. **A film whose light moves
   is graded as one gradient** (§4): a smooth path on the KEY strip, bounded per-shot trims (±1.5 EV, 4500–7500 K,
   sat 0.85–1.15), then the cuts graded jointly (§4b). Beyond the bounds, fix the light.
3. **Film emulation** (§7): the physical chain in density; one look per film; lab-style timing on a common reference
   object (6×6-px block means on product-part masks), per shot only printer lights or exposure, within trim caps; an
   author → critic → blind-ID loop with frozen signatures; re-solved timing carries approved lifts forward. It runs in
   Resolve as a per-shot DCTL on the scene-linear plates with calibrated grain, verified against its twin.
4. Resolve by script (load **`/resolve`**, if installed; otherwise the Resolve manual): linear EXR input; per-shot Fusion comps rebuilding the beauty from the
   light passes (prove the sum, then relight); the grade split into base / shot / look / timeline; looks built by hand,
   explored too far with a dial-back range (§2); white balance after colour; FX at "noticeable".
5. **Highlights, glare, shot-to-shot colour** (§6): recover blown areas with a light-driven local burn + a soft
   roll-off; glare only above a threshold and only on shots the user names; a colour-temperature outlier moves to its
   neighbours' midpoint. Realism targets (`realism-finishing.md`) run as diagnostics: a miss is fixed in the light.
6. Freeze every shipped look under a name; stamp name + md5 on every output. The mix rings out over the final hold.
**Don't:** solve exposure or WB per shot on motivated light; per-channel curves on sunlit colour; PBR Neutral or AgX.
**Gate** (`finishing.md` Measure and gate). Every frame matches its numpy twin; grain re-measured after the delivery
encode; film emulation: the critic's verdict and the timing table within its caps. **Show.** Graded clips.

## 13 · Review and delivery
1. **The review folder holds review videos only** (iCloud Drive or any synced folder the user can open on a
   phone): `<review root>/<NN>_<Section>/`, flat: the full-res MP4 plus a phone
   copy if needed. Stills, sheets and documents stay local and go on the board. Superseded sections move to a local
   archive, never deleted (ask before any retroactive cleanup).
2. **FigJam** (`figjam-board.md`): a section per act or round, tiles at native 1920×1080 with a caption and a notes
   box, boards near 1:1–1.6:1 (columns, never one long strip); notes read back with `get_figjam`.
3. Resolve: one project per film with a bin per act, `.drp` exported. Every deliverable reported with its full absolute
   local path in its own code block, and its review folder.
**Gate** (`fast-feedback.md` Measure and gate). Every checkpoint on the board, every video in the review folder; notes read back
and turned into requirements.

## 14 · Orchestration (`orchestration.md`)
Main (the lead) plans, checks every checkpoint itself, talks to the user and owns every "go"; builders own one study
folder; the **independent auditor** is a fresh agent; briefs quote the standing rules, what may not be touched, the
budget, the first checkpoint and the stage's Measure and gate section. User gates: 1, 7 (stamps, lock), 9, 9.5, 11.
Status is measured, never predicted (frames counted on the node); hand-offs are versioned JSON files; a blocked agent's
user-asked work is done by main, never routed around a block; ask before deleting anything.

---

## References (read when)
| File | Read when |
|---|---|
| `fast-feedback.md` | **always**, before planning any test, sweep, render round or agent brief |
| `research-protocol.md` | **before every stage**: tracks, prompt template, rules, reference images; stage 0's gate |
| `scene-optimisation.md` | **§0 at stages 0.5–9** (the budget and each stage's weight line); stage 10 readiness |
| `site-profile-example.md`, `orchestration.md` | stage 0.5: roles, `setup.json`, bench, budget; roles, briefs, gates, permissions, status |
| `elements.md` | stages 0–1: what each render element says; the lead element per product nature |
| `patent-to-model.md`, `reference-detailing.md`, `hard-surface.md`, `manufacturing-variation.md` | stages 2–3: sources, overlaps and poses, mesh QA, light builds, the master, variation, materials |
| `wear-materials.md`, `graphics-labels.md`, `glass-light.md` | stage 3: wear as a switch; labels and graphics; glass, caustics, gels, LuxCore |
| `/3d-material` (a separate skill, if installed) | stage 3: what every BSDF value does, material reading, and the measured photo-match workflow (match a material to reference photos or footage: shadows, mids, highlights, falloff) |
| `environments.md`, `alive-environments.md` | stage 4: choosing the set; bible, import pre-flight, dressing, audits, realism manifest |
| `lighting.md`, `realism-finishing.md` | stage 5: light states, reads, lights that converge, hot spots; realism targets |
| `cycles-production.md`, `octane-production.md`, **`/octane`** (separate, if installed) | stages 6 and 11: path, architecture, noise policy, archetypes, output spec; Octane engine detail |
| `composition-analysis.md`, `composition-exploration.md`, `greybox-composition.md`, `shots-and-script.md` | stages 1 and 7: the measured analysis, the 50, the lock-in, story, the loop |
| `fkl-frames.md` | stage 8: the bar, harness, CoC, close-ups, audit checklists |
| `camera-motion.md`, `greybox-animation.md`, `editing.md`, `transition-shots.md`, `animation.md` | stage 9: moves, mechanisms, the edit JSON, review ladder, transitions, teasers |
| `sound-design.md` | stage 9.5: spotting, beds, music, loudness steps and entries, notes → numbers |
| `render-farm.md`, `render-supervision.md` | stage 11: jobs, queues, power; the supervisor, alerts, check-ins |
| `finishing.md`, `camera-post.md`, **`/resolve`** (separate, if installed), `figjam-board.md` | stages 12–13: look chain, one gradient, highlights, film emulation; lens, grain; Resolve; boards |
| `pipeline-commands.md`, `approaches.md`, `apple-rubric.md`, `traps.md`, `changelog.md` | commands and scripts; CMF verdicts; judging packshots; failures; history (append) |

## Keeping the skill alive
After a session that tests something new or overturns a verdict: the general principle goes in the stage's reference
(rule, why, procedure, transferable numbers labelled as measured) and the study's specifics (tool
paths, per-shot values, measurements) in your own study notes, outside the skill; edit the stage here if its method changed; update the stage's Measure and
gate section when a gate or threshold changes; traps to `traps.md`, a dated line to `changelog.md`. No shot numbers,
part names or study paths in the skill. Archive the skill before a large rewrite (`~/.claude/skills/3d-product_archive/<date>_<label>/`). Keep
SKILL.md under 500 lines; detail belongs in the references.
