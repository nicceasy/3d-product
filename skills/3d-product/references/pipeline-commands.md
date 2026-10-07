# Tooling pattern and the shot-spec schema

What tools a product-film pipeline needs, why each exists, and the shape of the spec that drives them. This file is
the pattern, not a command list: each project's actual scripts, their arguments and recipes belong in your own tools index, kept with your study
notes outside the skill. Reuse those tools before writing new ones; version them
up rather than editing in place (a new v-numbered file).

Contents: 1 Principles · 2 The tool set · 3 The shot spec (schema) · 4 Command patterns

## 1. Principles
- **Scene as code.** Every render is built from a readable spec by a headless Blender run (`blender -b
  --factory-startup -P <builder> -- <spec>`). Why: hundreds of renders stay reproducible, diffs are readable, and the
  same spec renders identically on a laptop and on a render node.
- **One process, many variants.** Batch variants of a base spec in one Blender process (overrides as small JSON
  patches). Why: Blender start-up and scene load dominate short look-dev renders.
- **Everything a post tool needs travels with the render.** A multilayer 32-bit EXR with every pass and light group,
  plus a sidecar JSON (camera matrix, lens, focus, part ids, light state). Why: optics, grading and audits run
  later without re-opening the scene.
- **Versioned outputs, never overwritten.** Every pass writes to a new tagged folder (tags differ by more than case).
  Masters are copied, never edited.
- **Measure, don't eyeball.** Every tool that makes a judgement prints numbers (L\* percentiles, void share, CoC in px,
  overlap volumes) that a gate can read.

## 2. The tool set
| Tool | Job | Why it exists |
|---|---|---|
| **Environment + venv** | one project venv (Python, build123d/OCP, numpy, OpenImageIO/OpenEXR, OCIO) | CAD kernels conflict across venvs; system Python lacks the libraries (`traps.md`, Environment and shell) |
| **Model builder** | spec or parameters → B-rep → STEP + glTF, **one named solid per part**, poses as arguments | per-part materials, exploded views, animation and audits all key on part names |
| **Scene harness** | spec → Blender scene: import (unit and axis conversion baked), materials by kind, rigs, background, camera, passes, light groups | one place for every Blender trap; all tools share it |
| **Set builder** | location set from kit assets (USD + MaterialX rebuilt to Principled, thin glass) or a studio set from the spec | sets are rebuilt identically for every shot |
| **Shot / camera rig** | shot table (camera, lens, stop, focus target, light state, per-shot hides) → keyed cameras with aim targets | FKL frames, animatics and finals read the same table |
| **Light-state rig** | named light states as JSON (sun direction, sky, practicals, calibrated powers) applied by name | light continuity across shots and engines |
| **Audits** | ray-cast visibility, BVH overlap, focus/CoC gate, reads gates, material audit sheets | the gates of each stage run as code |
| **Render driver** | per engine: frames or chunks, kept-alive sessions, placeholders, overwrite off, **versioned animation packs**; a reset + one complete settings spec per shot, read back, its hash in every frame's metadata | reproducible sequences and cheap resumes; no lingering settings (`cycles-production.md` §9.4) |
| **Converter** | Cycles master → the other engine's master, with the known fixes (`octane-production.md` §4) | one engine-agnostic source |
| **Finish chain** | lens optics per light group → the film's one finish (the gentle look with one-gradient trims, or film emulation with lab timing) → grain → delivery, with a numpy twin of every Resolve step | the grade is checkable against a twin (`finishing.md`) |
| **Review publishers** | review videos to the synced review folder; stills and sheets to FigJam section builders (`scripts/figjam_section_builder.js`) | the user reviews every stage in the same places (`fast-feedback.md`) |
| **Setup probe** | hardware, engines and apps → `setup.json` (`scripts/probe_setup.py`) | picks the path before anything is built |
| **Render supervisor** | a plain-shell loop that owns an unattended run (`scripts/render_supervisor_template.sh` + a per-site hooks file, `scripts/supervisor_hooks.example.sh`; an optional `drift_check` hook alerts on slow frames, a changed spec hash or missing pass layers); finishing chains and conforms that wait on DONE markers | renders finish overnight without an agent or credits (`render-supervision.md`) |
| **Operator layer** | per-frame cameras → the same cameras with band-limited operator imperfections, KEY exact, metrics and gates | approved camera feel, reproducible by seed (`camera-motion.md` §6) |
| **Contact QA** | a saved shot file → sub-frame checks of a part riding another | correct mechanism animation in close-ups (`greybox-animation.md`) |
| **Macro focus** | f, field, named depths → f-number and focus offset with diffraction, engine values (`scripts/macro_focus.py`) | sharp deep subjects at macro magnification (`fkl-frames.md` §2b) |
| **Label builder + visibility** | reference measurements → re-set type → print maps (albedo, foil, roughness, normal); per-shot ray visibility of printed faces | labels that read as printed and are confirmed in every shot (`graphics-labels.md`) |
| **Sound engine** | per-frame channels → spotting sheet → components (beds, music, foley) → leveler → master + stems + loudness report → conform | sound built from the picture's own data, measured (`sound-design.md`) |
| **Scene weight** (`scripts/scene_weight.py`) | read-only, seconds: triangles and the heaviest objects, objects, shader programs, procedural and script nodes, images and their GPU bytes, mesh emitters (and those in light sampling), volumes, a VRAM estimate; PASS / FAIL per budget line | the per-stage weight record at the end of stages 2, 3, 4, 5 and at 10 (`scene-optimisation.md` §0.2) |
| **Budget** (`scripts/budget.example.json`) | the study's `budget.json`, written at stage 0.5: card and VRAM share, weight lines, hero collections, seconds per frame per light state, machine hours, the noise target | every 3D stage builds to it; stage 10 verifies against it (`scene-optimisation.md` §0.1) |
| **Composition analysis** (`scripts/comp_analysis.py`) | `frame`: one frame's composition measures; `sameness`: how alike candidate frames or neighbouring shots are; `cuts`: the OUT → IN step across every cut | the stage 7–8 composition gates as numbers |
| **Motion QA** (`scripts/motion_qa.py`) | reads the per-frame edit file: `shots` (speeds, image flow, constant increments, KEY exactness), `compare` (operator layer vs base cameras in px), `cuts` (angle and scale across each cut), `regate` (FIRST/LAST shift vs the approved stills; camera proof that packs carry the approved cameras) | the stage-9 motion gate as numbers (`camera-motion.md` §7) |
| **Loudness profile** (`scripts/loudness_profile.py`) | integrated loudness, true peak, loudness range, short-term and momentary curves with the film's marks, steps (gated), entry ramps (gated), dips, the short-term range (reported); exit code per gate | the sound gates read numbers, not impressions (`sound-design.md`) |

## 3. The shot spec (schema)
The harness reads one JSON per shot or still. Keep it flat and explicit; defaults live in the harness.
```json
{"models": [{"glb": "<model>.glb", "materials": {"<part or *>": {"kind": "<material kind>", "...": "..."}},
             "loc_mm": [0,0,0], "rot_deg": [0,0,0], "fit_mm": null, "set": false, "ground": true,
             "lightgroups": {"<part or *>": "<group>"}, "shade": "keep|flat|smooth|auto"}],
 "rig": "<named light rig>|none", "rig_params": {"hdri": "<file>", "world": 1.0, "rot": 0},
 "lights": [{"type": "area|spot|sun|point", "loc_mm": [0,0,0], "target_mm": [0,0,0], "flux_W": 0,
             "kelvin": 5600, "link": "product|set|[parts]", "lg": "<group>", "volume": true}],
 "flags": [{"loc_mm": [0,0,0], "target_mm": [0,0,0], "w_mm": 0, "h_mm": 0, "shadow": true}],
 "background": {"type": "catcher|cyc|floor|none", "color": [0,0,0], "rough": 0.3},
 "haze": {"density": 0.0, "size_mm": [0,0,0], "centre_mm": [0,0,0]},
 "camera": {"az": 0, "el": 0, "lens": 85, "fit": 0.66, "target_abs_mm": [0,0,0], "shift": [0,0], "dist_mm": null,
            "fstop": 0, "focus_mm": [0,0,0], "blades": 0},
 "motion": {"parts": ["<part>"], "deg": 0, "pivot_mm": [0,0,0], "shutter": 0.5},
 "render": {"engine": "cycles", "samples": 256, "res": [1920,1080], "view": "AgX", "exposure": 0,
            "passes": true, "lightgroups": true, "lg_denoise": true, "exr_codec": "ZIP", "exr_depth": 32},
 "out": "<file>.exr"}
```
- `fit` = share of the frame the bounding box fills (solved by projection). Prefer absolute world targets
  (`target_abs_mm`, `focus_mm`) over offsets from a bounding-box centre (`traps.md`, Camera, lens and focus).
- `set: true` keeps set pieces out of product-only links and masks; reserve an object-index range for the product.
- `.exr` output is multilayer with every pass; a `.cam.json` sidecar is written next to every render.
- Every emitter (lights, emissive parts, screens) belongs to a light group, or the groups won't sum to the beauty.
- **Material kinds** are named procedural recipes the harness registers, one per finish family: metals (bead-blast /
  anodised, polished, anisotropic machined), lacquer and paint (colour, roughness variation, orange peel, prints),
  rubber, glass (thin pane, tinted volume, frosted), light guides and emitters (blackbody or saturated colour),
  textiles, wood, stone, labels and prints, wear / dust layers (as switches), and QA kinds (mirror, zebra, isophote,
  curvature, clay). Each kind takes measured parameters (`reference-detailing.md` §6); the existing kinds and their
  parameters are listed in the tools index.

## 4. Command patterns
```bash
PY=<project venv>/bin/python
$PY <model builder> <out_dir> [--pose ...]                         # model → STEP + glb
blender -b --factory-startup -P <harness> -- <spec.json> [...]     # one still
$PY <batch tool> <base.json> <out_dir> 'a={"camera":{"el":18}}' 'b={"rig":"dark"}' --sheet <sheet.jpg>
blender -b --factory-startup -P <shot runner> -- previs|board|final <shot ...>   # shots from the shot table
blender -b <scene>.blend --factory-startup --python scripts/scene_weight.py -- --budget <study>/budget.json --out <weight.json>
$PY <finish chain> <frames>                                        # optics → look → grain → delivery
REMOTE=user@node ./run.sh <label>                                  # the same job on a render node (site profile)
```
Look-dev at 64 spp on a laptop-class GPU (seconds); finals at 256–1024+ spp on a render node. Hardware, paths and the
remote pattern come from the site profile (`site-profile-example.md`).
