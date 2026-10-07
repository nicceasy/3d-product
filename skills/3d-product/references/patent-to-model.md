# From a patent (or any line drawing) to an accurate model

A design patent's drawings are often an engineering plan in disguise: measured properly, at a verified scale, they can
close on a manual's published numbers to under a millimetre. The whole method is measurable: deskew, read line centres,
fix one scale, build a B-rep that cites its pixels, and draw the model back over the drawing to prove it. Other sources
(supplied CAD, the maker's drawings, press renders, photos, footage) follow the same rule: measure, fix one scale, build
parts that cite their source, and prove the model on a source you did not build from.

## 0. Geometry sources, by authority
- **Highest first:**
  1. supplied CAD (STEP: import it, name the solids, keep its tolerances);
  2. the maker's orthographic drawings (manual figures, CAD line drawings), scaled on two published dimensions that
     must agree;
  3. near-orthographic press renders at a known mm/px;
  4. design-patent drawings (§1–5);
  5. camera-solved photos and footage frames (`reference-detailing.md` §5; footage as a ~1 fps library,
     `research-protocol.md`);
  6. judgement, written as a labelled estimate (`reference-detailing.md` §4).
- **Hold one source out.** Validate on a source not used to build (an unrelated photo or frame). Measured once: ~2 mm
  rms along a ~9 m length, sub-pixel at that frame. A value left free in a solve that returns the drawing's number
  (within ~0.3 %) confirms both.
- **Size first when sources are thin.** Gate the overall and key dimensions against published values. Between assets
  that appear together, relative size matters most.

## 1. Get the drawings (with permission)
- Google Patents links the PDF on `patentimages.storage.googleapis.com`.
  - **Ask before downloading** (filename, source, size).
  - Research agents must only *cite* it: WebFetch saves PDFs.
- `pdfimages -png file.pdf sheet` (poppler) gives the original 1-bit sheets (typically 300 dpi). Rasterising the PDF
  would give a resampled copy instead.
- Crop the figures by connected components: `ndi.label(binary_dilation(ink, 25))`, keep the large boxes.
- US design-patent drawings are public domain, so they can go on the board. Product photos found by research cannot:
  they are reference only.

## 2. Measure, don't eyeball
- **Deskew each figure.**
  - Scans sit 1–2° off, which is a 2–3 % error on long edges.
  - Use the projection profile: rotate over −3…3° in 0.05° steps and keep the angle that maximises
    var(row sums) + var(col sums).
- **Read edges as line centres.**
  - Print the ink runs along a scanline at chosen positions.
  - Lines are 5–12 px thick at 300 dpi. Always use their centres, never the outer edges.
- **Circles:** use `skimage.transform.hough_circle` with a radius range per feature.
- **Scale:**
  - Check that the sheets share one scale: compare the same dimension across views (expect agreement within a few px).
  - Then read heights and positions at the plan scale.
  - Anchor it to one trusted real dimension (e.g. the overall width from the manual), then check a second one you did
    not fit; they should agree to well under 1 %.
- **Read drafting conventions:**
  - A **double line is a step or wall seen from above**, not two edges. The inner line is the floor edge; the outer
    line is the lip.
  - Streak hatching marks surface/shading, not geometry.
  - A perspective figure may be **printed rotated**. Rotate it upright before interpreting it.
  - Design patents often draw a transparent part as opaque. The claim is the shape; research gives the material.
- Write every number into a measurement doc in px and normalised by the anchor dimension, each with the figure it came
  from.

## 3. Research in parallel, while measuring
- **Tracks:**
  - identity and specs: which product, dimensions, manuals;
  - details and materials: finishes, colours sampled from photos, typography, wear;
  - story, light and photographic references (see `research-protocol.md`).
- **Order.** Measuring and the overall envelope can start with stage 0. The detail budget, the pose list and hero-part
  tessellation wait for stage 1's feature list, because they depend on what the film shows.
- **Rule:** the patent is the geometric authority for the *design claimed*; the product the user wants rendered is the
  one in the photographs. The production product supplies the third dimension, the heights where photos and catalogue
  agree, materials, colours, graphics and every part the drawing simplifies. Where the two disagree (a drawn part that
  production changed; a drawn overall height vs the catalogue's and the photos'), build production, keep the patent
  variant behind a flag, and let the overlay show the difference.
- Where evidence conflicts and a hard constraint exists (a mechanism's published geometry fixes a distance between two
  axes), the constraint decides.
- The drawing is only the start: the detail pass (`reference-detailing.md`) camera-matches photos of the real product
  and changes what the drawing cannot show (floating parts, wrong lengths, materials).

## 4. Build: B-rep, one named solid per part
- Map drawing px → model mm with two functions (one per axis), so every feature position cites its pixel.
- **Plan outlines:**
  - Build them as 2-D faces, then extrude or cut.
  - Blend concave junctions (a circle meeting a straight edge) with a **morphological closing**,
    `offset(offset(face, +r), −r)`.
  - Do **not** 2-D-fillet a build123d Sketch: it re-centres the result and can silently drop geometry.
- **Steps:** cut the wall at the drawing's *inner* line and fillet the lip, so the fillet's tangent edge lands on the
  outer line.
- **Poses:**
  - Group moving parts by how they move, each group with its real axis (a pivot, a hinge axis). A pose is a rigid
    `Location` about that axis, applied to the rest-pose parts (§7).
  - Solve poses from constraints, e.g. the swing angle that puts a part's tip at a given radius: scan from rest toward
    the target, stop at the closest approach, bisect. A scan from the wrong side can return the wrong branch (a pin
    outside its slot), so check the branch in the pose matrix (§6).
  - Level and seat parts with the mechanism's own adjustment (discrete settings, then a continuous remainder such as a
    screw), never by tilting or best-fitting the whole.
- **Check closure against specs you did not fit** (a mechanism's published lengths and angles, a diameter, a
  clearance). If the drawing closes on them, it is a plan, and the rest can be trusted to the same precision. A derived
  performance curve (an error over the working range) is checked against the published maximum.

## 5. QA: draw the model over the drawing
The overlay is the instrument:
- **Projection:** OCCT hidden-line removal (`shape.project_to_viewport(origin, up, look_at)`), orthographic, with the
  axis mapping per view (Z-up model, front along −Y):
  - Front: X = x, Y = z.
  - Rear: X = −x.
  - Top: X = x, Y = y.
  - Left side: X = −y.
  - Bottom (rear up): X = −x.
- **Register by the body centre only.** Use one shared px/mm scale and fit nothing else, so a wrong height or position
  shows up as distance.
- **Metrics:**
  - model → ink distance (median and p90, in mm);
  - **ink coverage**: structural ink within 6 px of a model edge, with hatch dashes removed (components ≤ 5 px tall
    and < 400 px wide at 300 dpi). Coverage measures *missing* features.
- **Targets (rules of thumb):** median ≤ 0.4 mm, p90 ≲ 3 mm, coverage ≳ 70 %. The rest is lettering, hatching and
  genuine ambiguities in the drawing (hidden hinges and the like); name each.
- **Deliberate deviations.** Where production differs from the drawing by decision (a height, a changed part), list
  the expected offset per view beside the overlay numbers; the targets apply to the remaining edges.
- **Perspective check:** draw the B-rep with `project_to_viewport(…, focus=dist)` in perspective, beside the patent's
  perspective figure. Match az/el/dist by eye in 2–3 passes. It makes a strong board image.

## 6. Overlaps, contact and the pose matrix
Touching is fine; overlap is not. Measure it on solids and on meshes, in every pose the film uses. Why: a lifted part
1.1 mm inside a closed cover, a solver branch that put a pin outside its slot, and a lift that left its carried part
behind in approved renders were each found late. These checks find them in minutes.
1. **Solids, at build time (exact).** Candidates are solids of different parts whose boxes overlap. Compute the
   boolean common volume per pair in forked workers with a time cap. Report pairs above a volume floor (1 mm³ worked),
   summed per part pair and grouped by cause. A fault that repeats per instance is fixed once, in the generator.
   Measured: the first runs on two new models found 31 and 444 pairs; both went to 0.
2. **Meshes (after deformation, densification or import).** BVH candidates within a few mm, refined to exact distances
   in double precision. A vertex is inside only when the nearest face's normal, the signed distance and three
   ray-parity casts agree. Single-precision BVHs misread by up to 0.2 mm on long CAD sliver triangles (measured).
3. **Designed embeds** (a pin in its bore, feet in a housing, a screw in its hole) are declared with their depths. A
   first build has no baseline, so its gate is absolute: 0 undeclared overlaps. Between versions: 0 new overlaps and
   the declared depths unchanged.
4. **The pose matrix.** Every moving group's poses × every state of the other groups (a cover open or closed × a moving
   part at rest, lifted or working × …), plus the product states the story implies (empty, loaded). Per cell:
   - constraint residuals (a target radius exact; a pin inside its slot's range; the solver's branch);
   - clearance to the nearest part, against the research minimums;
   - contact where designed (0 ± tolerance);
   - carried parts at distance 0 from their carriers across each rig's whole range: nothing floats, nothing is left
     behind.
5. **Re-run on every new pose.** The shot list adds poses after stage 2, so the matrix is keyed to it: each new cell
   passes before its FIRST/KEY/LAST frames.

## 7. Keep it light while you build
The product's own triangles were rarely the weight. The weight came from modelling choices that stop an engine caching,
instancing or baking, and they were found only at production, when approved looks had frozen them. The budget comes
from stage 0.5 (`scene-optimisation.md` §0); this is the modelling side.
1. **Tessellate by screen need, not one global tolerance:** chord ≤ ¼ px at the part's closest framing in the film;
   glass ≤ 0.05 mm; unseen faces (undersides, internals behind covers) coarse. Exact normals carry the shading
   (`hard-surface.md` §2b). Triangles cost memory and sync, not sampling, so spend them where the screen needs them.
2. **Detail where the film looks** (`reference-detailing.md` §4). Parts no shot resolves stay simple.
3. **Instance repeats** (fasteners, keys, feet, modules): one mesh, N instances. Never N copies baked into one mesh or
   N copies of the mesh data. Engines share geometry only for unmodified mesh data.
4. **Static parts stay static.** Apply modifiers on the master. No shape keys, deform modifiers or drivers on parts
   that only move rigidly. A deformation that depends on a pose is baked per shot or carried as a value in the shot's
   data. Why: engines re-export a deforming mesh every frame and cache a static one (measured: sync 15.3 → 1.4 s from
   frame 2 once the parts were static).
5. **UVs on every part, at build time.** One island per face group, oriented by the real pattern direction (brush,
   grain, print rows), at true scale. Prints and labels get their own UV layer, set as the active render layer: not
   Generated or Object coordinates, not box projection. Why: materials stay image-based and bakeable in any engine.
   Coordinate-mapped prints vanished and box projections streaked after conversion to a second engine
   (`octane-production.md` §4), and parts without UVs forced object-space procedurals that compiled every session
   (measured ~80 s). Check with a stripe-card render per part (`reference-detailing.md`, patterned materials).
6. **One rest-pose tessellation plus a pivots file.** Export each part once, in the rest pose, with every moving
   group's axes, pivots and ranges in a JSON beside it. Poses are rigid transforms about those axes. Why: posed exports
   re-tessellate (different vertex counts), which breaks correspondence for variation, contact solvers and
   comparisons.
7. **Collections by role:** the static product, then one collection per moving group (stage 4 adds enclosure,
   outdoors, dressing and emitters). Audits, trims, light linking and per-shot packs key off them; a flat scene makes
   every later audit name-based.
8. **A weight line with every build:** `blender -b <master>.blend --python scripts/scene_weight.py -- --out
   weight.json --budget budget.json` (read-only, seconds). It reports triangles per object and the heaviest,
   instancing, multiplying modifiers, shape-keyed objects, shader programs, images and emitters. Add the build
   seconds. A part over ~10 % of the product's triangles [J], or heavy and never framed, gets a decision now: coarsen,
   instance or replace.

## 8. Hand off: one engine-agnostic master, published
- **The master:** plain meshes with exact custom normals and UVs; Principled and image materials keyed by part name;
  the rest pose plus the pivots file; modifiers applied; variation levels as swappable mesh data, level 0 kept
  (`manufacturing-variation.md`). Fixes go into new versioned files, with a CHANGES file written last
  (`reference-detailing.md` §4 has its format).
- **Each version is a frozen release:**
  - the Blender file and a glTF;
  - a manifest: per part the name, triangles, materials, world matrix and deformation peaks; the sources' hashes; the
    build seconds;
  - the validation report;
  - one diagnostic still (level 0 vs master);
  - a one-command rebuild.
- **Consumers never edit the builder's folder.** They load through an importer that records the version, check for a
  newer one before every render (a pointer file and an exit code), and update in place, keeping poses and instances. A
  watcher may build the release when the version's CHANGES file, written last, appears.
- **Graphics:** draw alpha textures at 24–40 px/mm and map them through the part's print UV layer (§7).
- Next: `reference-detailing.md` (photos, part-by-part research, camera-matched QA, material audit).
- The accuracy sheet, a chart of the mechanism's geometry against its specs and the perspective match open the board:
  they prove the render is the patent.

## Measure and gate
Stage 2 passes on numbers. Each row is run on the first build and again on every version.

| Measure | How | Pass |
|---|---|---|
| Overlay on the drawing | HLR projection registered by the body centre only (§5) | median ≤ 0.4 mm, p90 ≲ 3 mm, coverage ≳ 70 %; deliberate deviations listed per view |
| Closure | specs you did not fit, derived curves against published maxima (§4) | a second dimension within 1 %; specs within their stated precision |
| Camera match | a landmark solve per photo (`reference-detailing.md` §5) | 4–10 px rms; > 15 px means a wrong landmark or a wrong part |
| Held-out source | the model through a solved camera on a source not used to build (§0) | sub-pixel to a few px at that frame [J]; a larger residual names the part that is off |
| Size | overall and key dimensions against published values (§0) | within the source's precision |
| Mesh QA | `hard-surface.md` §2b | chord ≤ ¼ px at the closest framing (glass ≤ 0.05 mm); normal error p99 ≤ 0.5°; slivers < 5 % on gloss; no pole leaning > ~15° |
| Overlaps | solids by exact common volume, meshes in double precision (§6) | 0 undeclared above 1 mm³; declared embeds listed with depths |
| Pose matrix | every cell (§6) | residuals within tolerance; clearances ≥ the research minimums; carried parts at 0 mm |
| Variants | each variant exported as its own file (`reference-detailing.md` §1) | each passes size, overlap and overlay |
| Version check | the new master against the previous one | same parts and names; placement unchanged to ~0.001 mm; finite; 0 flipped faces; 0 new overlaps |
| Weight | `scene_weight.py --budget` (§7) | the product inside its share of `budget.json`; every outlier has a written decision; build seconds recorded |

**Sheet:** the accuracy sheet (overlay numbers per view, the spec chart); the photo-match sheet (private if it holds
user photos); the pose-matrix table; a strip-light sweep of the gloss parts; before/after crops per fix; the weight
line.
