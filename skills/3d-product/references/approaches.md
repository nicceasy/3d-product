# Approaches tested: method verdicts for metal / CMF packshots

Which methods work for a studio packshot of a hard-surface product, and why. Each verdict was measured on one
benchmark product (brushed and bead-blasted metal, a grooved grip, smoked glass, a glowing element, a textile) with
the same camera and an automated rubric plus an eye score against launch-film references (`apple-rubric.md`).
Update a verdict here only with new evidence, dated.

Contents: 0 Quality bar · 1 Concept · 2 Modelling · 3 Pipeline · 4 Lighting · 5 Materials/CMF · 6 Composition ·
7 Render kernels · 8 Passes & compositing · 9 AI passes (history) · 10 Camera · 11 Storyboard · 12 Realism verdicts

---

## 0 · The quality bar
- **What:** sample real launch-film hero images pixel by pixel into a rubric; automate the measurable half.
- **Why:** it turns taste into numbers and catches process mistakes instantly (wrong ground value, clipping, framing).
- **Limit:** the automated half saturates (most competent renders pass); realism lives in the eye half (edges,
  reflections, materials, camera). Macro and x-ray references fail framing checks by genre.

## 1 · Concept
- **Brief → design tokens → morphological chart → silhouette sweep — WORKS.** A one-page brief (problem, object,
  ritual, promise), tokens (size, radius family, parting gap, feature counts), then a dozen silhouettes from token
  ranges in seconds. Every downstream model shares the same numbers; keep the tokens as a file the CAD script imports.
  Silhouettes judge proportion only.
- **AI concept images — PARTIAL (history).** Good for design language (details worth adopting), bad at dimensions
  (proportions drift) and invents details. Use for language only.

## 2 · Modelling (same design, four methods, each zebra-tested)
| Method | Verdict | Why |
|---|---|---|
| **B-rep code-CAD** (build123d), named solids per part | WORKS ★ | exact dimensions, per-part materials, exploded views, STEP; clean zebra. OCCT fillets are G1, so G2 roll-offs need swept curvature-continuous profiles or surface patches (`hard-surface.md`) |
| SubD from Python (profile cages + Catmull-Clark) | WORKS for soft forms | naturally smooth; crisp mechanical detail needs dense support loops; no dimensions or STEP |
| SDF + marching cubes | PARTIAL | fastest to write, beautiful blends; needs ≤ 0.2 mm voxels to hold reflections, no sharp features |
| AI image-to-3D | DOESN'T | right massing in minutes, but lumpy surfaces (zebra breaks everywhere), one fused part, no glass, no dimensions; massing underlay only |

## 3 · Pipeline
- **Tessellation tolerance + split normals — WORKS.** Sweep the linear deflection; ~0.004 mm / 0.08 rad was the
  sweet spot (measured once). Flat shading breaks a chamfer highlight into dashes: normals matter more than face count.
  Tighten the tolerance per part where highlights run (chamfers, knurls) rather than globally.
- **Scene-as-code shot specs — WORKS ★.** See `pipeline-commands.md`.

## 4 · Lighting (same product and camera; only the light changes)
| Rig | Verdict | Why |
|---|---|---|
| three-point + cyclorama | DOESN'T | clipping, blown glass, a grey ground |
| stock HDRI studios | PARTIAL | fast and real, but clutter in the glass, window shadows, colour casts |
| single top softbox | PARTIAL | clean but flat |
| gradient cards + black flags | WORKS | defined edges |
| **house white** (cards + flags + a card on the mirror ray + shadow catcher to an exact ground value) | WORKS ★ | a single graded highlight on flat glass |
| **house dark** (rim strips + top strip + grazing sides, pure black) | WORKS ★ | form from rims |
- **Key insights:** metal shows what it reflects, so lighting is reflection design; put one gradient card on the
  camera's mirror ray so flat glass gets one graded highlight; black flags at about ±65° give a cylinder its form;
  energy scales with R² (glTF arrives in metres); each camera needs its reflection cards re-aimed.

## 5 · Materials / CMF
- **Bead-blasted aluminium** (roughness ~0.40 with variation, blast bump, a polished chamfer mask, cavity) — WORKS ★.
  Removing the micro-detail layer (chamfer polish + cavity + blast) is the single biggest drop: aluminium reads as
  plastic.
- Polished metal reads chrome and busy; lathe-turned radial anisotropy is subtle; dark graphite shows form best;
  low-chroma anodising works; glossy ceramic white reads as plastic; a knit holds at 3/4, not at macro; a glowing
  element needs a saturated amber (AgX bleaches a bright 2700 K blackbody to peach) and must sit under the glass;
  Principled transmission tints glass twice (smoked ≈ 0.32, not 0.08).

## 6 · Composition and lens choice
- 35 mm reads cheap (top ellipse vs base); 85–150 mm is the house range; a very long lens at the product's midline
  reads most like a launch film; top-down needs its own reflection design; negative-space and edge-crop frames work at
  16:9.

## 7 · Render kernels (same exported scene, exposure-matched)
| Kernel | Verdict |
|---|---|
| **Cycles + OIDN** | WORKS ★: procedurals, light groups, passes; 64 spp is the look-dev default |
| EEVEE (ray-traced) | preview only: loses emitters under glass |
| Mitsuba 3 RGB / spectral | physics reference (measured metals), no denoiser |
| LuxCore path | adds nothing for a product; needed only for spectra and dispersion (`glass-light.md`) |
- Measured cost ratios (one scene, one laptop-class GPU): Cycles 64 spp ≈ 1/4 the time of 512 spp and near-identical
  after OIDN; EEVEE ≈ Cycles 64 spp; Mitsuba ≈ Cycles 512 spp; LuxCore path ≈ 2× Cycles 512 spp.
- Non-Blender kernels don't port procedural shaders and treat area lights as geometry (keep them out of frame).

## 8 · Passes and compositing
- **Light-group relighting — WORKS ★.** One EXR with key / fill / rim / emitter / world groups gives any relight in
  ~100 ms instead of a re-render (measured: ~1/200 of the render time). Apply the renderer's exact view transform via
  OpenColorIO so the comp matches the render. Denoise groups (or scale by the beauty's denoised/noisy ratio; it amplifies grain in
  near-black glass). Plan the groups before rendering.
- **Glow only what emits.** Take glow from the emitter's light group (an emitter under glass sends its light as
  transmission; the Emission pass is empty). A global bloom + CA + vignette + grain comp fails the background,
  highlight and neutrality checks.

## 9 · AI passes (history: removed from the pipeline)
- Unmasked AI edits held edges but rewrote semantics (glass became hollow, one material became another, the ground
  changed). Masked, controlled diffusion gave the most photographic materials but no model is pixel-locked: repeated
  features get re-cut and glass semantics drift. Not a recipe.

## 10 · Camera realism — WORKS ★
- DOF in real units (the product macro lives at f/4–8); bladed iris; cat's-eye from a real lens-barrel occluder
  parented to the camera (OSL custom cameras corrupt frames on Metal); axial CA from per-channel focus renders;
  shutter motion blur; a post-lens model in scene-linear before the view transform (`camera-post.md`). Launch-film
  heroes stay clean: no lens profile on packshots.

## 11 · Storyboard — WORKS
- Problem → object → ritual → detail → promise in launch-film grammar. The strongest frames use light as meaning.

## 12 · Realism verdicts (detail in `realism-finishing.md`)
| Step | Before | Verdict now | Why |
|---|---|---|---|
| Light for low-key product frames | product-only light linking, world 0 | set-only twins at 25–30 %, a room at ~1 % of the key, practicals that reflect and spill, haze filling the set | unlinking + a room alone cut crush from ~72 % to ~14 % (measured once) |
| Display rendering for finals | a neutral display transform | a per-channel film curve | film stocks put −4 stops far higher than a neutral transform does |
| Comp and finish | numpy relight | denoised light groups → Fusion relight in Resolve → look LUT → delivery | every frame matches its numpy twin |
| Grade settings | by eye | solved per frame against realism targets, bounded, per beat | crush, median L\*, chroma and cast all land in range |
| Hue variety | — | a single-hue palette is a design choice; add a cool ambient step only if the brief allows | measured, not fixed |
