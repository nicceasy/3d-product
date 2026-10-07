# Reference-driven detailing: from a drawing to a product that matches its photographs

A model built from a drawing (`patent-to-model.md`) is right in plan and wrong in the details a camera sees. The user's
standard: go beyond the drawing and look at photos of the individual elements, piece by piece (surfaces, edges,
materials, every part from screws to dial marks). This file is that process. On a real product it found a floating
moving part, sub-assemblies up to 20 % short, parts a few mm out of place, a surface texture 2.5× too weak and a dozen
wrong materials: all invisible in the drawing and all measurable in photos.

## 0. The loop, in one screen
```
identify the product and its variants ─┐
gather references (drawing, user photos, web photos, manuals, exploded views, catalogues)
research part by part (D-tracks: mechanics · controls/housing · surfaces/materials), photos measured, evidence-tagged
build/patch the B-rep part by part (one named solid per part, real axes, nothing floats)
camera-matched photo QA (solve each photo's camera → render through it → side by side / blend) ──┐ repeat until
material research → swatches passed by number → per-component audit (patch ratios) ──────────────┘ the pairs agree
decide intent vs age (render the finish as designed unless the brief says otherwise)
storyboard → finish → board; the skill and memory get the new traps and tools
```
Budget for it: the detail pass takes longer than the first model, and every round changes something real.

## 1. Identify the product and sort the references by variant
- Product families mix variants that look alike and differ in exactly the details you are about to model (controls,
  indicators, part colours, fitted components, logos, accessories).
- Make a reference table first: one row per photo with what it is, its variant, what it is good for (texture, a part,
  proportions) and its resolution. Deduplicate by md5 (users' photo sets often contain duplicates).
- Rule: take a detail only from the variant you are building, or from a part the research shows is shared (the same
  moulding across variants) — never from a part that differs between them.
- Every variant in the table becomes a generator flag. Each variant is exported as its own file and passes the same
  gates: sizes against published values, overlaps, overlays (`patent-to-model.md` § Measure and gate). Never mix parts
  from different variants or site types in one build.
- The user's photos are private reference: analyse them, never republish them (no board, no artifact). QA sheets that
  contain them stay local.

## 2. Gather references: what to look for, where
Ask research agents for URLs (no downloads) and read the user's photos with the Read tool. Sources that pay off:
| Need | Where | What it gives |
|---|---|---|
| How a part works and what it is called | service manuals and exploded views (often quoted on forums, manual archives, museum sites), the patent's text | part names and numbers; how a mechanism really moves (a tilt vs a translation) |
| Close-ups of parts | enthusiast forums, collector and museum galleries, auction and dealer listings (many angles, often high-res) | scales, pointers, fasteners, markings |
| Dimensions | operating manuals (tech data), brochures with plan drawings, catalogues | overall sizes, the constraints a mechanism must meet |
| Markings and typography | frontal photos, brochures | logotype letter widths in units of cap height |
| Materials and finishes | manuals (finish named in the spec), repair threads, photos under raking light | a texture that lives in the sheen, the true material of a "glass" part |
| Colour | photos with a neutral in frame (a white wall), several lights | ratios, not absolutes, when no grey card exists |
- Treat every claim with evidence tags [S] source / [S2] snippet / [V] measured / [D] derived / [J] judgement, and
  keep a variant table (which colour or part belongs to which model).

## 3. Research part by part: the D-tracks
Launch three background agents in one message, each with the same context block (the user's words, the stack, the
model's current part list and file paths, the reference table):
- **D1 mechanism and moving parts:** what each part is, how it moves (axes, groups, ranges), how to pose it, what the
  current model gets wrong with exact numbers, and a pose table.
- **D2 controls, housing and markings:** positions and sizes of every control and mark, edge radii, the rear and
  underside, what the model gets wrong, as B-rep numbers.
- **D3 surfaces and materials:** per part, the physical material and finish process, then measured photo values:
  colour (lit/shadow, sRGB + linear), highlight width as a roughness cue, micro-texture feature size and rms (high-pass
  at a known mm/px), edge highlight width and contrast, dust density. The deliverable is a table keyed by the renderer's
  material names, plus the 3–5 changes that matter most.

Prompt rules that matter:
- read images with Read or PIL, **never a browser on file://** (an agent can hang for hours);
- no GPU renders while the lead renders (CPU/GPU contention made builds ~20× slower);
- URLs only; the report file path; a ≤ 15-line TL;DR;
- if an agent is silent for > 20 min, check its transcript's last timestamp and restart it with a narrower brief
  rather than waiting.

## 4. Build and patch the model part by part
- **Frames per assembly.** A local frame per moving assembly (along the part, outboard, up), with the research's numbers
  written in their own frame, shifted once at the end. Parts go into groups by how they move: static, swing (vertical
  axis), tilt (horizontal axis carried by the swing). Pose with `Location` rotations about the real axes; never
  translate a jointed part.
- **Nothing floats.** Every moving part touches its carrier (axle through bearings, pin in its slot, tube in its
  trough, weight on its vane). Measure it in the pose matrix (`patent-to-model.md` §6), then look at the poses (rest,
  raised, working, end of travel) in detail views from angles the photos don't show.
- **Printed marks as relief geometry** (build123d `Text` extruded 0.03 mm) for parts that move or are seen in macro
  (scales, dials, nameplates); textures in the part's print UV layer for large fixed prints (`patent-to-model.md` §7).
  Logotypes: vector paths from measured letter widths in units of cap height, not a font stand-in.
- **Every number in the generator carries its source tag:** the tags of §2 plus [F] for a value fitted in a solve.
  Each version's CHANGES file has a fix table (# · item · old → new · evidence), a "not changed" list, and a closing
  section: where the model is off, and what is still a guess.
- **When evidence runs out, decide with a labelled estimate.** Take the mean of the independent sources and bound it by
  hard constraints (a fastener must clear its neighbour). Write the value with its uncertainty (± or one-sided), and
  name the one measurement that would settle it, with the model's prediction for it. Change it later as a new version,
  by one documented rule. Why: waiting for evidence that doesn't exist stalls the build; an estimate with its bounds and
  its test can be checked and replaced.
- **Detail where the film looks.** Before a remodel, show the defect at the shot's own framing (a before/after crop)
  and say what the fix costs. Hero-visible parts get the detail; the rest stay at the level the shots resolve. The user
  may stop a remodel once they see it.
- **Where production and drawing disagree, build production and record the drawing** (`patent-to-model.md` §3): the
  patent variant behind a flag, the overlay showing the difference, a hard constraint deciding where one exists.

## 5. Camera-matched photo QA (the instrument that finds most errors)
1. For each useful photo, pick 6–9 landmarks with known model coordinates, spread over the frame and in depth (controls,
   screw heads, body corners, hinge caps, window ends). Read their pixels on the original image.
2. Solve the camera (position, yaw, pitch, roll, focal; least squares). 4–10 px rms is good; > 15 px means a wrong
   landmark or a wrong model part (that is information). Leave the focal length free; pin it only when the points are
   too few, and reject a pinned fit whose rms is clearly worse (measured: free ~6–10 px; a lens pinned from another
   frame 20–35 px).
3. Render the model through that camera (Blender lens = f·36 / long side, roll in Blender's sign) and compare side by
   side and as a 50 % blend. Offsets become pixels: part lengths, component positions, radii and spacings are found
   this way.
4. Re-solve with alternative hypotheses to decide between sources (e.g. two sources' control positions; if the rms
   difference is small, it is inconclusive → keep the drawing). Project circles or outlines from the solved camera onto
   the photo to test radii and positions.
5. Hold one photo or frame out of the solve set and check the model through its camera last (`patent-to-model.md` §0).
6. Traps: landmarks all on one side extrapolate badly; too few points slide to an orthographic solution (pin f); the
   roll sign flips between a solver and Blender; readings near the frame edge carry lens distortion (measured once: a
   length read ~12 mm long), so take dimensions from near the centre.

## 6. Materials: research, calibrate, audit
1. **Measure the photo, per part, at its mm/px:** the lit and shadow colour (linear); the highlight width (FWHM, mm);
   the high-pass rms and feature size of log luminance, in the sheen (grazing) and head-on.
2. **Calibrate on swatches and pass them by number.** Build 3–4 swatch plates with the part's own edge radius, light
   them like the photo (for a sheen texture: a window at the mirror angle, exposure set so the sheen sits mid-grey),
   render at the photo's mm/px, one variable per swatch, with a 1:1 crop of the photo beside them. Write the photo's and
   each swatch's numbers side by side; a swatch passes when both views sit inside the photo's spread. Why: a measured
   bump value can be invisible, and one that matches at grazing can look like sandpaper head-on (measured once: a
   lacquer grain 2.5× too weak until calibrated). Two noise scales (e.g. 0.4 mm ×1.5 + 1.2 mm ×1.0 for a textured
   lacquer) matched in the sheen and stayed quiet head-on.
3. **Re-judge mottle and bump at the closest framing the shot list uses.** Render that framing at preview quality
   twice, with two seeds: a pattern that stays put is the material, not noise. Keep only a mottle that is invisible
   there or reads as the real finish. Why: texture tuned at the photo's scale read as blotches in a close-up (measured
   once: a few-mm roughness mottle and a full-strength bump; fixed by mottle off and bump at 25 %).
4. **Albedo in a physical range, measured, never inferred from a name.** Target each finish's reflectance from a cited
   source (an LRV, a maker's value) or from the measured mean of reference photos under neutral light; write it in sRGB
   and linear. Never reach a target with a chain of brightness and saturation tweaks: it turns one wood or paint into
   another. Regrade or swap the texture to the measured mean, keeping its own contrast. Measured in kit libraries,
   errors ran 2–3× both ways: a "walnut" that rendered cherry-pink; a mid-brown hardwood veneer at 0.07 linear against
   ~0.15–0.24 real; a "white" paint at 0.41 against 0.80–0.85. Stage 4 re-checks albedo in the render, in the dressed
   set.
5. **Audit every identifiable component:** component → reference crop (user photo, or the closest variant, or a cited
   source) → the same crop from a camera-matched render lit like the photo → the material settings → a verdict. Two or
   three rounds; write a material audit doc with the physical material, the reference, the settings and what changed.
   Include the props.
6. **Audit by numbers where a reference image exists.** Push render and reference through the same look and measure
   scene-linear ratios (render / reference) on named patches of every identifiable component. Before changing a
   material, diagnose the miss:
   - a patch that mirrors something the render lacks (a person, a cable, a bright wall) is an environment gap;
   - a whole-region bias is the light: fit the audit light to the reference first;
   - only a ratio that stays off under fitted light is the material.

   Change one factor per round (base colour or roughness) and re-measure. Measured once: ratios of 0.63–2.17 became
   0.89–1.09 in two passes, and the eye-only audit had missed the 1.5–2× errors.
7. **Light the audit like the photo, not like a studio.** A large overhead panel greys a dark glossy prop that the
   photo's small lamp shows dark with one band; a studio backdrop can block the photo's window light entirely.
8. **Inventory every glass layer.** List each transparent material and its layers: windows as thin panes (front-face
   Fresnel); kit glass that drives transmission from a map, rebuilt as a thin pane by that map; each milky or diffuse
   layer with its weight; each mix's input convention. Check each in every light state. Measured once: a 2–5 % milky
   layer, invisible by day, carried 82 % of a night pane's light.
9. **Materials and light are coupled.** Lights are fitted to the materials they lit, so a material change after stage
   5 re-runs the light-state sheet (reads, fills, levels).
10. **Intent vs age.** Photos of an old unit show dust, bloom, lint, burnish, smudges, pitting and dulled plating.
    Render the finish as designed unless the brief asks for patina: keep the age layer as a switch, off by default
    (`wear-materials.md`). The design finish (grain, blast, diamond cut, gloss, stipple, print) stays.

## 6b. Keep it light while you build (materials)
Material weight is decided when the material is built: texture sizes, shader structure, emitters, displacement. Found
at production, each fix changes an approved look. The budget is in `scene-optimisation.md` §0; this is the material
side.
1. **Texture size by role and closest framing.** Product, prints and labels at what their closest framing resolves;
   props and set by role (`scene-optimisation.md` §0). Image files, not packed: packed images can reach a second engine
   as float RGBA, 16 B/px (measured). Measured once: sizing maps by on-screen need cut VRAM 10.9 → 8.3 GB per card,
   images identical at 1:1.
2. **Greyscale maps single-channel** (roughness, metallic, height, masks), Non-Color, 16-bit at most. A height map that
   only feeds bump needs no 32-bit float.
3. **Shared, parameterised procedurals.** Count the distinct procedural graphs per material as you build. Product
   procedurals come from a few shared node groups (one structure, the numbers as inputs); set materials prefer images
   or bakes. Measured after conversion: ~0.26 s per procedural node plus ~0.38 s per distinct shader of session
   start-up; folding the distinct shaders into about a quarter as many shared ones cut sampling 22–25 %, images
   identical.
4. **Bake what the final engine converts badly.** Before a material is approved, list its features the final engine
   converts badly: procedural textures it can't run, box projection, Generated or Object coordinates shared across
   instances, an emission colour above 1, a mix's input order (`octane-production.md` §4). Bake or rebuild them now, in
   a versioned copy. Wear masks for finals are baked or SDF-native (`wear-materials.md`).
5. **Emission only where a light is meant.** A glowing decal, screen or print is still a mesh light: turn its emission
   sampling off and keep it visible to the camera and in reflections. Measured: taking ~225k emissive prop triangles
   out of light sampling was about a third of a 9× time gain at equal noise.
6. **Displacement only where an outline needs it** (silhouette detail); bump everywhere else. Measured: texture
   displacement in the final engine cost ~0 sampling time; Cycles true displacement cost +70 %, and adaptive
   subdivision at 1 px ran out of memory in a close-up (2.5 px for close-ups).

## 7. Hand-off
- The project's thinking doc gets a phase for the detail pass: what each matched photo changed (before → after), the
  decisions and what stays open.
- The board gets model-only images (detail views, pose checks, swatches, overlays, the material table). The user's
  photos and the private QA sheets never go on it.
- The skill gets the new tools and traps (this file, `pipeline-commands.md`, `traps.md`), the changelog a dated line.

## Tracing printed graphics from photos
Graphics drawn from memory are "not even close"; trace the user's photo. (Designing new graphics in a real genre's
typography, physical print materials and proving labels in every shot: `graphics-labels.md`.) The method, for a flat printed disc or panel
(a label, a dial face, a nameplate):
1. **Rectify exactly.** Fit the graphic's outer edge as a conic (least squares, trimmed to ≤ 2.5 px residual). For a
   circle photographed at an angle, a known centre point (a hole, a spindle) is the image of the circle's centre, so its
   polar w.r.t. the edge conic is the vanishing line → send it to infinity, then an affine takes the ellipse to the
   circle at its real diameter; rotation from the text rows (projection-profile variance). An ellipse-only (affine)
   unwarp leaves 1.5–2° of perspective and a mm-scale centre offset. Check the photo isn't mirrored before flipping
   anything.
2. **Ink map** = projection of each pixel onto the local paper → ink colour axis (paper from a masked blur of confident
   paper only, so big white shapes don't pull the reference), then local-max normalisation so small dim type reaches
   full ink. Pixel-trace only the big shapes (the logo).
3. **Set type as type.** Small print is ~10 px tall in a phone photo; any pixel trace breaks up. Identify the face, set
   each line in it (extended widths via a horizontal stretch) and fit size, tracking and position by blur-matched
   correlation (render blurred to the photo's measured edge σ; grid + FFT offset + Powell polish). Fit **per style
   jointly** (lines that share a style share face, size and tracking), not per line.
4. **Pick weights by ink area in linear light** (sRGB → linear before measuring coverage; blurred half-covered pixels
   read too bright in gamma), calibrated on the logo: correlation can't tell Medium from Bold under blur.
5. Verify in Blender: a top-down emission render of the mapped graphic in a real job file (reads true, not mirrored).

## Patterned materials follow the object's construction (wood grain, stone, weave, brushed metal)
The eye knows how things are made. A pattern that runs the wrong way (a tabletop's grain running front-to-back, grain
wrapping round an edge, identical figure on every door, one repeat across a long panel) reads as fake before any colour
or roughness error does. This applies to the product and to hero props and furniture alike.
1. **Research the real construction, per part** (a research track with photos of real examples, evidence-tagged): what
   is solid and what is veneered or laminated; which way the pattern runs on each part and why; how neighbouring panels
   are matched; how edges are finished. For case furniture in wood the pattern is: tops along their length, doors
   vertical, a bank of drawers as one continuous horizontal sheet, rails and legs along their axis, edges as separate
   solid lippings with the grain along each edge, often mitred at the corners. Other materials have their own rules
   (book-matched stone slabs, a weave running along each panel and matched at seams, a brush direction set by the
   machining).
2. **Write a per-part table:** the pattern direction on each surface, the matching and layout, the edge treatment.
3. **Map per part:** a new, versioned UV layer with one island per part or face group, oriented by the table; edges and
   lippings get their own islands. Never one box projection over the whole object (it runs the pattern along one world
   axis on every part).
4. **True scale across the pattern.** Research the real feature sizes (e.g. fine stripes a few mm apart, bands tens of
   mm apart, figure 150–300 mm wide), measure the texture's feature spacing in pixels, and set the texel density so
   they land at real size (≥ 2048 px/m across the pattern). Too big reads as a toy, too small shimmers. **Stretch only
   along the pattern** (up to ~2×) to cover a long part without a repeat: stretching along the fibre is invisible,
   across it is not.
5. **Consecutive leaves, never identical:** neighbouring panels take neighbouring regions of the texture, so they read as
   siblings; a wide panel is made of several leaves from different regions, with faint joints parallel to the pattern.
   No visible repeat anywhere a camera can see.
6. **Keep the real colour** (§6.4): the measured mean of the real finish, the texture's own contrast, and roughness and
   coat by the real finish (render intent, not age).
7. **Check it:**
   - a **stripe-card UV check**: swap the texture for a directional stripe card and render every part's views; each
     stripe must follow the table;
   - before/after audit views under neutral light, plus the research's list of fake-material tells (none present);
   - a **motion check for shimmer** on a moving shot: a few consecutive frames, a high-pass of log luminance on
     registered frames; the energy must change smoothly (no frame jumps) and show no moiré at 1:1;
   - lit KEYs of the shots where the part shows, before and after, in the final engine.
8. **Port to the final engine as versioned copies:** run the same UV script on copies of the engine masters, rebuild
   the material to match (bake any parameter the engine's material lacks, such as a normal strength, into the texture;
   remove conversion leftovers such as a box projection or a stray sheen), never edit a master in place.

## Measure and gate
Stage 3 (materials). Stage 2's gate is in `patent-to-model.md`.

| Measure | How | Pass |
|---|---|---|
| Swatches | photo vs swatch: lit/shadow colour, highlight FWHM, high-pass rms and feature size at grazing and head-on, at the photo's mm/px (§6.1–2) | both views inside the photo's spread |
| Patch ratios | render / reference, scene-linear, through the same look, camera-matched and lit like the reference (§6.6) | each named patch within ±10 %, or a written cause |
| Albedo | each finish against its cited or measured reflectance (§6.4) | hero-support and large-area materials within ×1.3 [J] |
| Closest framing | each glossy part at its closest planned framing, preview quality, two seeds (§6.3) | no seed-stable blotch that isn't the real finish |
| Glass layers | the inventory, each layer in each light state (§6.8) | every layer listed with its weight and mix convention |
| Prints | rectification residual (tracing, above); each map's strength rendered on/off; visibility per shot by ray sampling (`graphics-labels.md` §4–5) | residual ≤ 2.5 px; strengths measured and written; every visible shot confirmed |
| Patterned parts | stripe-card UV render; shimmer test on a moving shot (patterned materials, above) | every stripe follows the table; no frame jumps, no moiré at 1:1 |
| Material cost | `scene_weight.py` on the material file, plus a line per material: texture MB at the chosen sizes, distinct procedural graphs, glass layers, emitters (§6b) | inside the stage's share of `budget.json`; every outlier has a written decision |

**Sheet:** the swatch sheet with photo and swatch numbers side by side; the audit sheet with the ratio table; the
material cost list. Sheets that hold user photos stay private.
