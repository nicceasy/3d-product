---
name: 3d-product
description: A one-shot pipeline for hardware product films in Blender, from a prompt and a reference (a design patent, photos, a video) to finished, graded sequences - a setup probe that picks the best hardware and engine, research first, the film's intention, modelling from drawings and photos, materials as designed, lived-in or studio environments, grey-box lighting and composition, shot list and script together, FIRST/KEY/LAST frames, motion and the animatic, scene optimisation, an Octane or a Cycles production path run unattended by a plain-shell supervisor, sound design and music, DaVinci Resolve finishing, and review on FigJam and a synced folder, each stage gated. Use it whenever the user wants to concept, model, render, light, compose, storyboard, animate, film or finish a physical product (devices, audio gear, lamps, lenses, appliances) - product shots, packshots, CAD-to-render, patents or drawings, launch films, teasers, camera moves, renders that look CG, lived-in or studio sets, kit assets, Cycles or Octane settings, render nodes, overnight renders, labels and printed graphics, sound design, music and the mix, grading, grain and delivery - even if they don't say "3d-product".
---

# Product animation: a prompt and a reference → finished sequences (Octane or Cycles)

A tested pipeline (Blender 5.2, Octane 31.10, DaVinci Resolve Studio 21.1) written as general principles: every stage
says what works, the gate before moving on and what the user sees; detail lives in `references/`. Keep your own
worked examples, measurements and tools in a study-notes folder outside the skill and reuse them (see "Keeping the
skill alive"). History: `references/changelog.md`; failures: `references/traps.md`.

## Run it end to end (the one-shot recipe)
Input: a prompt and a reference. Output: graded sequences (Octane or Cycles) in a shared review folder and on a
FigJam board.
★ = the user decides; agents stop and wait there. Everything else is gated automatically and shown as a checkpoint.

| # | Stage | Gate before moving on | The user sees |
|---|---|---|---|
| 0 | Brief intake + research | nature sentence, variant table, research TL;DRs | brief page + reference sheet, ≤ 60 min |
| 0.5 | Probe the setup | `setup.json` written; render path and roles assigned | the setup and the recommendation |
| 1 | **Intention** | what the film is for and says, story seed, light arc, feature list | ★ go / redirect |
| 2 | Modelling | overlay + photo-match numbers, 0 new penetration, every pose verified | overlay and photo-match sheets |
| 3 | Materials + textures | every component audited against a reference | swatches + audit sheet |
| 4 | Environment: location or studio | bible + causality + 0 intersections, or measured gatekeeper ratios | previs sheet |
| 5 | Lighting, grey box first | reads gates (void, outline) pass in every light state | light-state sheet |
| 6 | Engines, kernels, settings | matched-noise table + flicker check | speed / quality table |
| 7 | **Compositions, shots and script, together** (a loop) | gated comps; every source cross-referenced; every shot serves the intention | ★ stamps comps each round; ★ locks the shot list |
| 8 | FIRST / KEY / LAST | harness gates + subject CoC + reads + independent audit + main's check | per-act sheets |
| 9 | Motion, animatic and final cut | speeds within limits, mechanisms physical, edit and script finalised | ★ approves the animatic and the cut |
| 9.5 | **Sound and music** | events on their frames, music measured (key, tuning, tempo), loudness profile passes | ★ picks the music by ear; ★ approves the lock |
| 10 | Scene optimisation | trims render-verified, fits VRAM, time estimated | the machine-time estimate |
| 11 | Production render: Octane or Cycles path | FKL frames in the final engine match the approved previews | ★ explicit "go" per act |
| 12 | Finishing | frames match their numpy twins, version stamped | graded clips |
| 13 | Review + delivery | review-folder section + board + Resolve project | the finished film |

Stage 1 sets the intention every later stage serves. Stages 2–6 build the product and its world once; 7–9 decide the
film at preview cost (compositions, shots and script together, then the frames, then the cut); 9.5 builds the sound on
the near-final cut while 10–12 spend the machine time. A fix loops back one stage, not to the start (a frame fault is
fixed in 8; only a shot that can't be made strong goes back to 7). Orchestration (stage 14) runs through all of it.

**Roles, not machines.** Stage 0.5 finds what fills each role: the *workstation* builds scenes and jobs and runs
previews, look-dev and boards; *render nodes* give throughput; *shared storage* holds jobs and frames both can reach;
the *finishing host* runs the look chain and Resolve. One machine can hold all of them (`site-profile-example.md`).

## Rules over every stage
- **Research first, paired with reference images** (`research-protocol.md`): parallel background tracks, URLs + what
  to measure in each image, evidence tags, TL;DR first. Research sets hypotheses; renders decide.
- **Fast feedback loops, vital** (`fast-feedback.md`): a visible result within 30–60 min, a checkpoint every 1–2 h, a
  machine-time budget before anything runs (≤ 1 h per look question, ≤ 4–6 h of render-node time per sweep). Climb
  the cost ladder: 640 px clay → 960×540 → 1:1 crops → full res only to confirm; one frame → FIRST/KEY/LAST → one shot
  → all shots. Render nodes are for throughput, not iteration. A plainly asked step gets the one standard method, in
  minutes. **Deliver the first complete build at once, then iterate**: no hidden rounds while the user waits.
- **Only what works.** Each stage gives the method that worked; failures are one-line "don't"s or live in `traps.md`.
  Comfy and AI image passes are out of the pipeline: in testing they bent the scene and invented content. AI music
  generation is in (stage 9.5). Realism comes from the scene, light, camera and linear finishing.
- **Version up, never overwrite** (models, generators, caches, looks): copy → edit the copy → new versioned outputs →
  a CHANGES.md written last. Never alter the user's originals; never delete shot files. **A change request versions up
  the approved file and changes only what the note targets** (an angle, a timing, a light): first prove the start
  reproduces the approved frame (a pixel diff); the shortest path that keeps continuity, never a rebuild (`editing.md`).
- **Always 32-bit float EXR (ZIP), scene-linear, a light group per emitter**; review JPGs and MP4s derive from them.
- **Render intent, not age:** the factory finish and factory-new geometry; dust and wear only as a switch, off.
- **The user's notes are hard requirements**; keep extra shots (no note ≠ rejected); "scrap" = move on, keep the files.
- **Prove the plumbing, predict then measure, look before you judge:** push a known chart and a deliberate 4× change
  through any new pipeline; keep numerical twins; correct captions to what the image shows.
- User photos and third-party images are private reference: analyse them, never put them on a board or artifact.

---

## 0 · Brief intake and research
**Why.** Every later choice follows from what the product *is*; research has changed products before a single render.
**Do.**
1. Name the product's nature in one sentence and pick the **lead element** that proves it (`elements.md` §11).
2. Identify the product and its variants: one row per reference (what it is, variant, what it's good for,
   resolution), deduplicated by md5 (`reference-detailing.md` §1). A patent PDF: ask before downloading (name,
   source, size); design-patent drawings are public domain and may go on the board.
3. Launch the research tracks in one message (`research-protocol.md` template, each with a budget and a 30–45 min
   TL;DR checkpoint): P1 identity and specs, P2 details and materials (finishes, photo colour samples, typography), P3
   story, light and photographic references with measured targets; R1 *features* (signature functions and unique
   elements as shot ideas, plus model gaps). Reference video: `/analyze-youtube`, then measure frames.
4. Open the study folder with THINKING.md (decisions per phase), STATUS.md, research/, checkpoints/; a FigJam board
   planned near 1.3:1 (`figjam-board.md`).
**Gate.** Nature + lead element written; variant table; TL;DRs landed or time box hit; a one-page brief (problem,
object, ritual, promise).
**Show.** The brief, the reference sheet (links + measurements), the nature sentence. **Read:** `elements.md`,
`research-protocol.md`, `fast-feedback.md`.

## 0.5 · Probe the setup
**Why.** The pipeline must pick the best setup available, not assume one: which engine can render finals, where
previews and finals run, and what can finish.
**Do.**
1. Run `python3 ~/.claude/skills/3d-product/scripts/probe_setup.py --out <study>/setup.json [--deep] [--bench]
   [--priority realism|speed]`. It reads the site config (`~/.config/3d-product/site.json`; example
   `scripts/site.example.json`) and probes read-only, in ~4–7 s: GPUs and backend, Blender and its devices, Octane,
   Resolve (Studio = scriptable) or the numpy look chain, ffmpeg, each node over ssh, shares and link speed.
2. Read the recommendation: the finals path (Octane when a node has the add-on and a running server and the brief
   needs light through glass; Cycles otherwise or with `--priority speed`), the render node, GPUs per frame, the preview
   host and ladder, the finishing host, storage, and notes (e.g. "launch Octane jobs in the interactive session").
3. No render node? Every role runs on the workstation: Cycles finals, one frame per job, longer budgets.
**Don't:** install, restart or kill anything to make a probe pass. **Gate.** `setup.json` written; every role filled
or marked missing. **Show.** A five-line summary of the setup. **Read:** `site-profile-example.md`.

## 1 · Intention
**Why.** The user: "overall intention should be first". What the film is for and what it says decides the light, the
scale, the subjects and the story, so it is written before modelling, and every later composition and shot must serve
it (stage 7 and the FKL audit check that each one does).
**Do.** Write it at the top of the study's THINKING.md; the shot list opens with it.
1. **What the film is for and what it says:** the audience and channel, the claim in one sentence (the product's nature
   from stage 0, said as a film), the feeling it should leave, how it ends, and what it must never imply (the honesty
   filter, `environments.md` §1).
2. **The story seed:** the format (`shots-and-script.md` §2: e.g. a ritual film with the object early, light marking
   time and bookends, or a reveal that withholds the object), a logline, one line per act, the target length (15 s ≈
   8 shots; 60 s ≈ 13 + card; a ~2 min ritual ≈ 25–30 shots).
3. **The light arc:** the named light states across the film, one state per shot; if time passes, a monotonic
   schedule on edit time (`lighting.md` §9) with each transition marked by a shot (`transition-shots.md`).
4. **The feature list:** the product's signature functions and unique elements (the R1 track), each with its pose.
5. A new, designed product: its concept belongs here too: brief → design tokens → physics first (ray-trace optics,
   predict caustics, OKLCH colour, Beer–Lambert tints; `hard-surface.md`, `glass-light.md`).
**Gate.** The intention fits in a short paragraph (what for, what it says, how it ends); every feature named has a pose.
**Show.** ★ The intention, the logline, the light arc and the feature list; the user may redirect. **Read:**
`shots-and-script.md` §1–2, `elements.md` §11–12, `animation.md` §1–2 (teasers).

## 2 · Modelling
**Why.** For a real product the photographs are the judge; a pixel offset is a model error until proven otherwise.
**Do.**
1. From a patent or drawing (`patent-to-model.md`): deskew, measure line centres, one verified scale, `MEASURE.md`;
   build123d B-rep, **one named solid per part**; overlay QA by HLR projection on every figure (median ≤ 0.4 mm, p90
   ≤ 3 mm). Check published specs you did not fit: if they close, the drawing is a plan.
2. Detail from references (`reference-detailing.md`): D-tracks (mechanism · controls/housing · surfaces), patch part by
   part, the patent kept as a variant flag; **camera-match** each useful photo (4–10 px rms) and compare in one frame.
3. New products: representation by part type (`hard-surface.md`: B-rep for machined parts, fair Gn sweeps or SDF for
   class-A skins, Manifold booleans for arrays), the zebra tunnel on every hero surface.
4. Moving parts as groups by how they move (static / swing / tilt), posed about real axes, poses solved from
   constraints (scan toward the target, stop at the closest approach, bisect). Nothing floats.
5. Secondary forms: manufacturing variation at **level 2** (just perceptible; level 1 is invisible), factory-new,
   per-part operators (`manufacturing-variation.md`).
6. **One engine-agnostic master, versioned:** plain meshes + custom normals, Principled / image materials, shape keys on
   simple drivers, level 0 kept; fixes into new versioned files with a CHANGES.md written last.
**Gate.** Validation clean (same parts and names, placement unchanged to ~0.001 mm, finite, 0 flipped faces, **0 new
interpenetration**), clearances met, contact exactly where designed, every pose checked from angles no photo shows.
**Show.** Overlay and photo-match sheets (private if they contain user photos), before/after crops of each fix.

## 3 · Materials and textures
**Why.** Realism is light, not texture; but every component must still be the right physical material, as designed.
**Do.**
1. Measure each part on the photos (colour lit/shadow, highlight width, texture rms and feature size at a known
   mm/px), then **calibrate on swatches** at the photo's mm/px under the photo's light, one variable per swatch
   (uncalibrated measured values are often several times too weak; two bump scales + a roughness mottle usually match).
2. **Audit every identifiable component** (→ `MATERIAL_AUDIT.md`): reference crop | the same crop of a camera-matched
   render lit like the photo | settings | verdict. Props too.
3. Intent, not age: separate design finish from wear before copying values; age layer `dust=0` by default.
4. Prints and labels: traced from photos, not drawn (hole-polar homography rectification, ink map, type set as type
   and fitted per style, weights by linear-light ink area; `reference-detailing.md` last section). Relief geometry for
   macro-visible marks; textures by Generated coordinates with a facing mask for large prints. **New graphics**
   (`graphics-labels.md`): a real category's layout grammar, the reference's type re-set from measured boxes (its own
   string fitted first), physical print maps (albedo, foil → metallic, roughness, a gentle paper normal) with each
   map's strength measured, flattened copies where alpha is ignored; confirmed in every shot that shows them.
5. **Patterned materials follow the object's construction** (`reference-detailing.md`, last section): per-part UVs by
   the real pattern direction, true scale across it, consecutive leaves, the real colour; stripe-card and shimmer checks.
6. Plan for Octane now: image textures and Principled convert cleanly; box projection and Generated/Object-coordinate
   prints need the converter fixes; every procedural chain becomes OSL (startup cost) (`octane-production.md` §4).
**Don't:** a cm-scale mottle on gloss (splotches); mirror-smooth glass in sun (flicker: roughness ≥ 0.03); a Base Color
tint on glass (use volume absorption).
**Gate.** Every component has a material checked against a reference, in writing. **Show.** Swatch and audit sheets.
**Read:** `reference-detailing.md` §6, `wear-materials.md`, `glass-light.md` §5.

## 4 · Environment: location or studio
**Why.** A set that can't explain itself reads as CG; the product without its system breaks causality faster than any
material flaw.
**Choose the branch** (claim first, `environments.md` §1: honesty filter, extravagance index, reflection plan):
- **LOCATION** when the claim is the product in its life: lifestyle, editorial, "where it lives", a film whose light
  marks time of day, a storyboard inside one place.
- **STUDIO** when the claim is the object alone: packshots, catalogue and silo frames, launch-film abstraction, glass
  or optics demonstrations (dark / bright field), a product that must stay isolated.
- A film that needs both builds the location, and shoots studio frames as separate sets from the same model.
- **NATURE** (landscapes, fields, hills, a product site in the land): build it with **/3d-nature** (a spec from the
  prompt, reference or drawing → terrain, instanced plants, measured sun/sky, haze and fog), then continue at stage 5.

**LOCATION** (the ★ steps of `alive-environments.md`, every time, even for "just add an environment"):
1. The set bible: who, what just happened, the time stack, the region, palette lock, 3–5 materials, exclusions, a wear
   map; orient the room for the light you want (a west window for evening sun).
2. Research paired with measured reference images (scene track + camera/coverage track).
3. Real assets (a kit library via its desktop downloader; USD + MaterialX → Principled, thin glass): a complete shell
   and a real exterior; hero supports modelled with scanned materials; kit albedo measured before a name is trusted;
   the room probed (windows, walls, lamps) before anything is placed (numbers: `alive-environments.md`).
4. Previs cameras before dressing; a top-down ortho plan render to aim the sun by geometry.
5. **Dress in context: the product's system first** (what it connects to and is used with, cables to a real outlet),
   then hero props → dressing → background → breakdown → life pass, filled by the numbers (`alive-environments.md`).
   Colour comes from objects, each accent twice. Props age; the product doesn't.
6. **No intersections:** a BVH overlap audit between every pair of props (~1 mm tolerance) as a build gate; fix the
   generator, not the instance.
7. Per-shot dressing like a photographer: move props plausibly per composition, tuck the leads; **hide only what no
   ray reaches over the whole move**, never a visible prop or a glass cover (fix the frame with the camera).
**STUDIO** (a builder from a JSON spec, `pipeline-commands.md`): metal on a white or black sweep or cards; glass on a
dark field / bright field / a gradient ground; a fabrication story (a painted cyc with a real cove, CNC plinths); the
gatekeepers (`lighting.md` §2); backdrop cards 20 m out; macros in a void; camera-invisible flags for glossy black.
**Gate.** Location: bible written, causality test (10 random details explained), 0 intersections, previs reviewed
(expect several passes at 960×540, 32 spp). Studio: world/key and twin ratios measured from light groups.
**Show.** The previs contact sheet.

## 5 · Lighting, grey box first
**Why.** Renders read as CG mostly because of the light, not the grade; light shapes are composition.
**Do.** (`lighting.md`)
1. Grey box: clay on everything except glass and emitters, prints kept as ink; 960×540, 8 spp + OIDN (a few seconds
   per frame on a laptop GPU).
2. Motivated light by branch: location = the sun split from the sky map and aimed by geometry, thin-glass windows,
   haze a whisper (σ ≈ 0.006 m⁻¹), practicals after sunset; studio = the gatekeepers (a set-only twin at 25–30 %, a
   room at 0.5–2 % of the key, sources ≥ 5°, practicals that reflect and spill, WB at the key's CCT).
3. **Name the light states once** (sun elevation and azimuth, W/m², K, sky, lamps, exposure; named e.g. by sun
   elevation) and use them everywhere; one state per shot.
4. **Blackbody practicals** (tungsten ~2700 K, luminance kept when switching from white; a red LED ~1400 K); sun and
   sky the only non-blackbody emitters; every emitter in a light group.
5. **On black gloss, three-point lighting happens in the reflections** (`lighting.md` §5): key, fill and rim are bright
   things the product mirrors, found on each face's mirror ray; a face reads only when what it mirrors is about as
   bright as a white card in the key light.
6. **"Reads" is two measured gates** (`scripts/reads_metric.py`): R1 void share > 0.30 fails; R2 outline separation
   < 0.20 fails. Never fix a fail with exposure: pick the light from `lighting.md` §5's table by where it fails.
7. Every added light is motivated and named; no product-only linking; never hide a light from glossy rays. **A fill is
   a real surface lit by real light**, its radiance measured in the EXR (in sun ≤ ~1× a sunlit white card).
8. **A film that moves through the day** (`lighting.md` §9): a monotonic schedule on edit time, one state per shot at
   its midpoint; practicals on once at a motivated moment; the window as the clock (at night we see out); an HDRI per
   phase from one matched series with a night floor ~4–5 stops under day; WB follows the key; probe the low sun.
9. **Plan each light state's lighting in the grey box**, dusk and low sun above all: unplanned low-sun and dusk frames
   fail "reads" almost every time.
**Gate.** R1 and R2 pass in every state; black gloss black outside the light; crush ≤ 1 %; groups sum to the beauty
within 1 %. **Show.** A light-state sheet (the product in each state, one camera) with the reads numbers.

## 6 · Engines, kernels and render settings
**Why.** The engine decides what light is possible; the settings decide the render bill. "This will absolutely change
rendering times" (the author).
**Do.**
1. **Choose the finals path by the brief, then the hardware** (`cycles-production.md` §1; stage 0.5 applies the
   hardware half): sunlight through glass or smoked acrylic in a scene → **Octane** where a node has it; metal, plastic,
   lacquer and throughput → **Cycles**; a glass product in a studio → Cycles + a LuxCore caustic layer (`glass-light.md`
   §7). Previews, grey box, compositions and FKL previews: always Cycles on the workstation (960×540, 256 spp + OIDN).
2. **Cycles production:** adaptive threshold 0.02, min 32, max 1024, denoiser off (OIDN colour-only after), clamp
   indirect 3, Filter Glossy 1.0, persistent data, **one GPU per frame** (multi-GPU on one frame is slower on big
   scenes). Those biases darken light under glass (unbiased Cycles agrees with Octane but with fireflies).
3. **Octane production, a realism config within ~2× of the fast one** (PT, coherent 1.0 + static noise, ~1536 spp, GI
   clamp 100, deep specular depths, RGB IOR metals, no dispersion, a whisper of air; `octane-production.md` §5).
4. **Sweep before quoting any time** (both engines): prove adaptive engages with a sample-count AOV, compare at matched
   noise against an independent 4096-spp reference (different seed), confirm on a 10-frame sequence with a flicker metric.
5. Output: 32-bit ZIP EXR, a light group per emitter (`lg_denoise` in Cycles), data passes; Octane
   `prefer_image_type = "HDR"`.
**Don't (measured):** Octane adaptive (no gain at matched noise), NRC (noise ×4.3, time ×4.8), the Photon kernel
(over-counts ~12× against PMC), coherent 1.0 + dispersion (coloured blotches), coherent > 0 without static noise (4.3×
flicker), a denoiser inside the render (erases ~25 % of fine detail; speckle and mottling on dark finishes): denoise
the raw beauty with OIDN in post.
**Gate.** A matched-noise table for the chosen path, flicker ≤ production, and (on an engine migration) a 1:1 region
check against the other engine after a grey-card calibration. **Show.** The speed / quality table with crops.

## 7 · Compositions, shots and script, together
**Why.** The user: "composition shots and script should go hand in hand". A shot list built around stamped
compositions exposes beats with no strong frame and shots whose pose doesn't match their comp, so this is one loop,
not three steps, and every composition and shot must serve the intention (stage 1).
**The loop** (`composition-exploration.md`, `greybox-composition.md`, `shots-and-script.md`):
1. **The intention and the story draft decide what to explore:** the beats, subjects, light states and poses the story
   needs, read against the product's vocabulary and the set's measured traps → the archetypes to sample.
2. **Grey-box lock-in, always:** ≥ 30 KEY/LAST move pairs straight from render, physical cameras (field W, real lens
   f, real N → Blender focal f(1+m), f-stop N(1+m)), clay except glass and emitters, real DOF, occlusion ray casts,
   scored (composition + DOF/rack + one dominant change), eye-checked; 1280×720, 64 spp.
3. **50 stand-alone compositions** (`composition-exploration.md`): archetypes (painting-derived: a black slab, a
   window, a zip…) → 20–30 cameras each → **pre-gate by geometry** (~80 % die) → previews in the final look → gates
   G1–G9 → eye pass ("OK" is a reject) → repair one factor → 50 selected with quotas (families capped, no
   near-duplicates) → finals on the render node → the board → ★ the user stamps (read back with `use_figma`).
4. **Write the shot list and script around the picks** (`shots-and-script.md`). Sources: stamped comps, shots marked
   good, shots with notes (quoted: hard requirements), unmarked shots (kept). The story: logline, why this story, light
   arc, arc of scale, rhymes, bookends, planned match cuts, an acts table. Per shot: "from X to Y", why the subject and
   how it serves the intention, FIRST / KEY / LAST as stand-alone comps (cited), the move, the product alive, the light
   state, any card, what is heard. Cuts by design: **never replay an action across a cut** (split it, match on action);
   a match cut shares its framing; no jump cuts (≥ ×1.5 or ≥ 30°). The edit sets the real pacing; ambiguous notes are
   confirmed with the user.
5. **Close the loop:** a beat with no strong frame requests new compositions (sampled only from families under their
   caps); a weak or redundant shot is folded into a neighbour or moved to where its pose is true; a comp that serves no
   beat stays on the board, out of the film.
6. Iterate (new comps → stamps → the list updates) until ★ the user locks the shot list.
Craft that held (`composition-exploration.md`): aim by lens shift, not yaw; size whole-product frames by fill; focus on
the visible surface; pose the product and move props like a photographer (hide only the unseen); re-render approved
finals from their blend.
**Gate.** Every frame passes G1–G9 or carries a written reason the user would accept; the cross-reference table
accounts for every good, noted, stamped and scrapped source; every shot says how it serves the intention; ★ the user
locks the shot list.
**Show.** Each round: the composition board with stamps and notes, then the shot list with its cross-reference and the
changes since the last round.

## 8 · FIRST / KEY / LAST
**Why.** The user's bar: "subject to subject, strong comp to strong comp, intentional motion, subject in focus every
time." Every frame justifies itself against the intention. A wrong frame caught here costs minutes; in a sequence it
costs an hour of rig time.
**Do.** (`fkl-frames.md`)
1. Frames as data: a spec → one harness (the master, the rig, the safe-off list, blackbody practicals, spin blur,
   cards, racks in dioptres) → EXR + previews in the final look → the shot JSON.
2. Gates in the harness (G1–G9), the **CoC on the subject ≤ 2 px at 1920** on its mask (formula and the diffraction
   rule in `fkl-frames.md`), **the reads check on every frame** (a fail goes back to stage 5), the fill radiance check.
   **Close-ups** (`fkl-frames.md` §2b): split the subject's depth and stop down within diffraction
   (`scripts/macro_focus.py`), check the engine's aperture units, and pick the camera so a mirror-like foreground
   reflects dark (a ray probe, not exposure).
3. An **independent auditor** (a fresh agent) checks every frame, shot and cut against `fkl-frames.md` §4 (slices,
   rivals, dead thirds, near-level edges, focus, accents, speeds, hacks joining two comps, covers that don't read);
   every cut N LAST → N+1 FIRST: eye jump ≤ ~25 % W, ≥ 30° or ≥ ×1.5, every mechanism's state equal across the cut.
4. The builder fixes by diagnosis; the auditor re-checks; **main checks every shot itself**, then declares "cameras
   final for Act X". A shot that can't be made strong goes back to stage 7 (a new comp, or fold or move the shot).
**Gate.** Audit pass on every frame and cut, and main's check. **Show.** Per-act FIRST | KEY | LAST sheets (clean and
marked) on the board and in the review folder.

## 9 · Motion, animatic and final cut
**Why.** Motion is a render element: easing, speed and mechanism timing claim mass and precision. The animatic is
where timing is seen for the first time, so the edit and the script are finalised here.
**Do.** (`camera-motion.md`, `greybox-animation.md`, `animation.md`)
1. **Simple moves** (`camera-motion.md` §0, a standing rule): one constant move per shot, anchored on the approved KEY.
   At most two animated dimensions, one primary plus one subtle secondary (≤ 0.25): push + boom, or arc + track.
   The aim is locked, parallel, or panning at a constant rate, and never follows a part. Lens, roll and shift are
   constant, there is no easing inside a shot, and FIRST and LAST come out of the move. Gate on the simple-move QA
   (constant relative transform, legal generators, KEY exact, clearance, occlusion, flow). **Then the operator layer**
   (`camera-motion.md` §6, the approved default): slow 1/f drift under ~0.7 Hz, speed breathing of 1–2 %, a 0.1–0.2 s
   follow lag, rare resonances and bumps; camera-local, KEY exact, gated in px. A rigid ride on a part: named only.
2. **Speed ceilings** (push ≤ 10 %/s of the field, arc ≤ 4°/s, truck/pan ≤ 6.5 % W/s; targets in `camera-motion.md` §0),
   computed before render. Racks in dioptres, only across ≥ 5 DOF. Lock the camera while a mechanism acts.
3. Mechanisms on physical curves (e.g. a hinged cover by hand: minimum jerk 2.5–3 s; a lift 0.75–1 s ease-out; a motor
   spin-up τ ≈ 0.4 s, coast τ 1.6–2 s; contacts solved every frame). The product alive in every shot; only its own
   mechanisms move on screen, and what a hand would do is implied by a cut. A part riding another gets sub-frame QA on
   the saved shot file (contact gap, rate, phase, continuity, blur interpolation; `greybox-animation.md`).
4. Cut points (`editing.md` §3): enter moving, leave before arrival; match on action = one motion on one clock.
5. The numeric hand-off is one shot JSON (orbit + world camera per FKL frame, timing, product and light channels);
   every renderer and the edit read it.
6. **Cut it like the reference** (`editing.md`): about 2 min, holds set by the information in each frame, cuts on the
   product's motion (cause → effect, driven by mechanism channels), no visually similar neighbours, every story beat
   legible, no magic animation. Inventory → plan → paper edit → build → assemble, gated; new shots enter as slots.
   **Transition shots** (`transition-shots.md`): 3–4 abstract reflection shots, one per lighting transition.
7. **Finalise the edit and the script at the animatic** (cut points, match cuts, act lengths, runtime; trim or fold
   what reads slow); every change goes into SHOTLIST.md / SCRIPT.md first (the source of truth), then the shot JSON.
**Gate.** Speeds within limits; the motion gates pass (or the exception is named); focus targets unoccluded; withheld
marks legible only where intended; the script matches the cut. **Show.** ★ The **motion review** after every camera
change (`camera-motion.md` §4: a grey playblast of *every* shot with a motion strip, plus the edit), then the review
ladder (`editing.md` §7: the FKL animatic, 4 and 6 fps lit animatics, KEY spot-checks before each pass), each approved.

## 9.5 · Sound design and music
**Why.** Sound is the last layer that carries the story, and the user judges it by ear and by how it moves ("avoid big
changes in volume"). It is spotted from the animation data, so it starts on the near-final cut, beside stages 10–11.
**Do.** (`sound-design.md`)
1. Research first (craft, sources and licences, reference films measured); a sound script with the music map.
2. The spotting sheet from the per-frame channels: events on their frame or one late, never early; beds never cut,
   perspective eases ±3 dB around cuts; source music worldized; the world near the threshold, the music the star.
3. Quiet parts as tonal beds (a sub pedal on the tonic, sparse open-interval partials, no broadband noise), sweeteners
   in key. Measure every music take's key, tuning and tempo: generators ignore what is asked.
4. AI music, quality first: complete natural pieces, raw takes to the user by ear before any fitting, phrase-aware
   fits with no stretch, endings that ring with the end card held; decay artefacts fixed by regenerating or a tail-only
   cleanup. An AI ear triages; the user's ears decide.
5. Loudness: −16 LUFS-I, ≤ −1 dBTP, short-term within about 6 LU, no step over about 3 LU/s, gentle dips, entry ramps
   (`scripts/loudness_profile.py`); stems sum to the master; the limiter's latency removed.
**Gate.** All of the above measured. **Show.** The first complete build at once, then each version on the latest
picture with its loudness PNG; ★ the user picks the music by ear and approves the lock.

## 10 · Scene optimisation
**Why.** A dressed location can need twice a GPU's memory (out-of-core renders crawl), and the wrong trim changes
almost every shot.
**Do.** (`scene-optimisation.md`)
1. **Scene audit per shot over the whole camera path:** visibility casts (direct, through glass, off reflections), the
   objects no ray reaches, **never the enclosure or the outdoors**, never product parts or lit emitters; verified by
   group render at FIRST / KEY / LAST (mean ΔE00 < 0.5, p99 < 2). The global safe-off list goes in the master.
2. Cap set textures at load (2048 px; the product, prints, labels and HDRI exempt); fit each shot in-core.
3. Heavy geometry: find it (a multi-million-triangle prop costs seconds of first-frame sync) and hide it where unseen.
4. Cycles on a render node with `--factory-startup` (another engine's add-on can force a re-sync every frame, ~10×).
   Octane: static geometry cached, the kept-alive session, cache 'All', OSL → native nodes (startup ~20× faster).
**Don't:** trim by bounding box in the frustum (it drops the outdoors and everything reflections see).
**Measure before you trim:** trims pay only where a shot doesn't fit in-core (in a kept-alive Octane session they saved
0.6 % per frame, cost +25 s per shot switch and risked a missing object: untrimmed won, with the global safe-off list).
**Gate.** Every list render-verified; the shot in-core; the per-frame time measured on a 10-frame chunk and the total
written down. **Show.** The estimate (frames × seconds) before the queue starts.

## 11 · Production render: the Octane path or the Cycles path
**Why.** The same gates feed both paths; only the render step differs. The render nodes are for throughput, after the
cheap stages have approved the film.
**Octane path** (`octane-production.md`): ONE converted master + a small animation pack per shot, applied in ONE
kept-alive session (~30 s and 50–100 KB per shot, against ~6.5 min and ~5.7 GB to convert each shot): build the master
on the workstation → convert it on the node in the server's session (converter + fixes, render config baked) → bake
per-shot packs → one driver applies them in turn. On Windows an ssh job runs in session 0 (environment only): launch
through an interactive-session task (stage 0.5 flags `needs_interactive_session`).
**Cycles path** (`cycles-production.md`, `render-farm.md`): one packed .blend per shot with trims and texture caps,
`--factory-startup`, one Blender per GPU, frames claimed over placeholders.
**Both paths, in order:**
1. **FKL in the final engine first**, per act, finished through the approved preview look.
2. **Main checks every FKL frame itself** against the approved previews: 1:1 prints and labels (in Octane: box
   projection, Generated-coordinate prints, emitter clamp), under glass covers, dark gloss noise and mottle, the set,
   focus on the subject, region luminance ratios. Then ★ the user's explicit "go" per shot or act.
3. Sequences: overwrite off, placeholders, one EXR per frame (Octane in kept-alive chunks); after any interruption
   test every recently written frame. Bulk data moves through shared storage; power as a budget, capped per the site.
4. **Unattended runs: a plain-shell supervisor owns the run, never an agent** (`render-supervision.md`,
   `scripts/render_supervisor_template.sh`): node, share, session, power cap (never raised), GPU count (reboot on loss
   per the site's policy), server, hang check, relaunch of incomplete shots with skip-existing, a relaunch cap, alerts.
   A finishing chain finishes each shot as its frames land; the picture and sound conforms run automatically after.
**Gate.** FKL approved and "go" given; frame counts complete; per-frame time within the estimate.
**Show.** FKL in the final engine beside the approved previews, then each shot as it lands (a push per arrival if asked).

## 12 · Finishing
**Why.** Keep the render's light; borrow a reference's colour. The user: the solver was "missing a lot of the light
quality from the original renders".
**Do.** (`finishing.md`)
1. Per frame: OIDN colour-only on the raw beauty (both engines) → EV 0, no WB by day → Pro-Mist-like 1/8 → a gentle
   reference-matched look → 35 mm grain in display, fresh per frame → 16-bit → ProRes 422 HQ + H.264 ≥ 40–50 Mb/s.
   This numpy chain needs only Python + numpy + OpenEXR + ffmpeg: it finishes on any host, alone without Resolve.
2. Resolve by script for the edit and delivery (`finishing.md` §2): timelines per act, FX as Fusion comps, white
   balance after colour, FX at "noticeable" (the lowest level with local ΔE00 ≥ 3 on ≥ 2 frames).
3. Freeze every shipped look under a name; stamp name + md5 on every output.
4. **A film whose light moves is graded as one gradient** (`finishing.md` §4): a smooth target path on the KEY strip,
   bounded per-shot CDL trims (±1.5 EV, 4500–7500 K, sat 0.85–1.15); beyond the bounds, fix the light. **Then grade the
   cuts** (§4b): all shots solved jointly with an IN → OUT white-balance ramp, every cut's displayed step capped.
5. The sound conform (§5): the picture holds the end card while the approved mix rings out, then fades.
**Don't:** solve exposure or WB per shot on motivated light; per-channel curves on sunlit colour; PBR Neutral or AgX.
**Gate.** Every frame matches its numpy twin; grain re-measured after the delivery encode. **Show.** Graded clips.

## 13 · Review and delivery
**Do.**
1. **Review folder** (iCloud Drive or any synced folder the user can open on a phone): one shallow folder per review
   section, `<review root>/<NN>_<Section>/`, flat: a full-res contact sheet, JPGs at q95 4:4:4 (q90 loses ~20 % of
   the grain), the MP4s; big sheets split per act for phones.
2. **FigJam** in one consistent style (`figjam-board.md`): a section per act or round, tiles at native 1920×1080 with a
   caption and a notes box, boards near 1:1–1.6:1 (columns, never one long strip); notes read back with `get_figjam`.
3. Resolve: one project per film with a bin per act (stills: one project per shot), `.drp` exported.
**Gate.** Every checkpoint is on both surfaces; notes read back and turned into requirements.

## 14 · Orchestration (runs through every stage)
- **Roles.** Main (the lead) plans, checks every checkpoint itself, talks to the user and owns every "go". Builders own
  one study folder and import shared libraries read-only. The **independent auditor** is a fresh agent, never the
  builder. The engine agent runs the render nodes. Research agents deliver URLs and measurements, no downloads, no
  GPU while the lead renders; a quiet agent (20 min) is restarted with a narrower brief.
- **Briefs** carry the question, the user's standing rules that apply (quoted), what may not be touched (for a change:
  the file to version up and the only parameters to change), the budget, "the first complete build at once", the first
  checkpoint (≤ 60 min, `<study>/checkpoints/NN_*.jpg` + a STATUS.md line) and the cadence. Hard rules also become
  gates in the tools (a driver refuses a pack that hides a part the user said is always visible).
- **User gates where agents stop:** the intention (1), the composition stamps each round and the locked shot list (7),
  the animatic and the final cut (9), the music pick and the sound lock (9.5), the "go" per act after the FKL in the
  final engine (11). Render gates the user sets ("no re-renders until…") hold until lifted.
- **Permissions.** A subagent blocked on work the user explicitly asked for is not a stopping point: main does it itself
  on the user's instruction (also user-approved downloads, which subagents can't take on relayed word). If main is
  blocked too: stop that outcome, finish the rest, give the exact allow-rule text; never route around a block (moving
  the work elsewhere counts) or ask another agent to retry. Render-node kills, reboots and server restarts follow the
  site's policy (`site-profile-example.md`); Resolve is saved and quit through its API; workstation processes: ask.
- **Status is measured, never predicted:** frames counted on disk, GPU load, file times; "not yet confirmed" until new
  output lands; ETAs from the measured rate. Main relays checkpoints as they land, never a pending agent's result. One
  owner per background watch.
- **Hand-offs are files:** parallel agents (camera, builder, engine, grade) exchange versioned JSON specs, never prose;
  new tags per output (differing by more than case: APFS/SMB are case-insensitive); masters copied, never edited; poll
  a share's new folders over ssh (the SMB cache hides them). **Sheets before passes:** a spot-check sheet precedes
  every full pass, and main reviews every sheet by eye before the user sees it.
- **Hygiene.** Ask before deleting anything (scratch blends, superseded outputs; use the Trash). Paid APIs: log the
  balance before and after. Keys load in-process, never printed.

---

## References (read when)
| File | Read when |
|---|---|
| `fast-feedback.md` | **always**, before planning any test, sweep, render round or agent brief |
| `site-profile-example.md` | stage 0.5: the roles, one real site's facts, the `setup.json` format (`scripts/probe_setup.py`) |
| `research-protocol.md` | **before every stage**: tracks, prompt template, rules, reference images |
| `elements.md` | stage 0–1: what each render element says; the lead element per product nature |
| `patent-to-model.md` | stage 2 from a patent or technical drawing |
| `reference-detailing.md` | stages 2–3 for any real product: variants, D-tracks, camera-matched QA, material audit, label tracing, patterned materials by construction |
| `hard-surface.md` | stage 2 for new hard-surface forms: continuity, representation per part, SDF, zebra QA |
| `manufacturing-variation.md` | stage 2: secondary forms, deformation levels, perceptibility |
| `wear-materials.md` | stage 3: wear, dust, prints (as a switch); mask sources |
| `graphics-labels.md` | stage 3 for labels and printed graphics: layout grammar, re-setting reference type, print materials (foil, paper), per-shot visibility and confirmation |
| `glass-light.md` | glass, lenses, translucent plastic, caustics, gels, gobos, haze, LuxCore |
| `environments.md` | stage 4: choosing (claim, honesty filter, extravagance index, reflection plan, channel) |
| `alive-environments.md` | stage 4 location: bible, assets, dressing, motivated light, DP camera, audits |
| `lighting.md` | stage 5: grey box, light states, blackbody, three-point in reflections (R7), the reads gates, glass covers, light tells time (§9) |
| `realism-finishing.md` | the measured realism targets, the lighting gatekeepers, Resolve plumbing, the gentle look |
| `octane-production.md` | stages 6 and 11, Octane path: sessions, the master + packs + kept-alive driver, the realism config, sweeps, verdicts, converter traps |
| `cycles-production.md` | stages 6 and 11, Cycles path: the path decision table, settings, GPUs per frame, light through glass, timings |
| `render-farm.md` | stage 11 on render nodes: jobs, queues, power as a budget, corrupt frames (the example site's farm) |
| `render-supervision.md` | stage 11 unattended: the plain-shell supervisor, finishing chains and conforms, verified status, power, task hygiene |
| `greybox-composition.md` | stage 7: the ≥ 30-pair grey-box lock-in, physical camera spec, DOF table |
| `composition-exploration.md` | stage 7: the 50 compositions: archetypes, pre-gate, gates, eye pass, quotas, repair table |
| `shots-and-script.md` | stages 1 and 7: intention, story, the loop with compositions, sources, bookends, match cuts, pacing |
| `fkl-frames.md` | stage 8: the bar, the harness, the CoC formula, close-ups (§2b: DoF, aperture units, mirrors, blur diagnosis), the audit checklists |
| `greybox-animation.md` | stage 9: timing engine, speed limits, mechanisms, contact QA at sub-frames, the edit, the numeric hand-off |
| `editing.md` | stage 9 and any cut: holds by information, cut on product motion, no magic animation, insert slots, reference-film pacing numbers, the paper-edit → assemble procedure, the review ladder and its costs |
| `transition-shots.md` | stage 9 when light changes across the film: abstract time-of-day shots, reflection physics, the sampled search and scoring, families, the light switching on, story continuity |
| `camera-motion.md` | stage 9 and any camera move: simple moves (≤ 2 dimensions, anchored on the KEY), why multi-axis moves jump, the gates, the motion-review playblasts (per shot + edit), the operator layer (§6) |
| `sound-design.md` | stage 9.5: research, spotting from the animation data, layers and perspective, tonal beds, measuring music, AI music, artefacts, loudness, assembly and the conform |
| `animation.md` | teasers and short films: easing family, camera realism in motion, light over time, sound |
| `scene-optimisation.md` | stage 10: scene audit, trims, texture caps, VRAM, launch overheads |
| `finishing.md` | stage 12: the look chain, Resolve by script, delivery encodes, grading a film as one gradient (§4), grading the cuts (§4b), the sound conform (§5) |
| `camera-post.md` | lens optics, emitters that look real, film character (denoise, mist, grain) |
| `figjam-board.md` | stage 13: board style, builders, board shape |
| `pipeline-commands.md` | command patterns and the studio spec schema (the tools index is in the study notes) |
| `approaches.md` | method verdicts for metal / CMF packshots |
| `apple-rubric.md` | judging packshots; launch-film shot grammar |
| `traps.md` | anything breaks (Blender, Cycles, Octane, OCCT, Resolve, FigJam, render nodes) |
| `changelog.md` | what changed and when; append to it |

## Keeping the skill alive
After a session that tests something new or overturns a verdict: put the general principle in the stage's reference
(the rule, its why, a procedure, transferable numbers labelled as measured) and the study's specifics (tool paths,
per-shot values, measurements) in your own study notes, outside the skill; edit the stage here if its method changed;
add traps to `traps.md` and a dated line to `changelog.md`. No shot numbers, part names or study paths in the skill.
Archive the skill before a large rewrite (`~/.claude/skills/3d-product_archive/<date>_<label>/`). Keep SKILL.md under
500 lines; the detail belongs in the references.
