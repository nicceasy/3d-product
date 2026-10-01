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
material research → swatch calibration at the photo's mm/px → per-component material audit ──────┘ the pairs agree
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
  trough, weight on its vane). Check poses (rest, raised, working, end of travel) in detail views from angles the
  photos don't show.
- **Printed marks as relief geometry** (build123d `Text` extruded 0.03 mm) for parts that move or are seen in macro
  (scales, dials, nameplates); textures by Generated coordinates for large fixed prints. Logotypes: vector paths from
  measured letter widths in units of cap height, not a font stand-in.
- **Where production and drawing disagree, build production and record the drawing.** The patent is the design claim;
  the product the user wants rendered is the one in the photographs (catalogue heights over drawn heights; a production
  part without the drawing's trim). Keep the patent variant behind a flag and let the overlay show the difference.
  Where evidence conflicts and a hard constraint exists (a mechanism's published geometry fixes a distance), the
  constraint decides.

## 5. Camera-matched photo QA (the instrument that finds most errors)
1. For each useful photo, pick 6–9 landmarks with known model coordinates, spread over the frame and in depth (controls,
   screw heads, body corners, hinge caps, window ends). Read their pixels on the original image.
2. Solve the camera (position, yaw, pitch, roll, focal; least squares). 4–10 px rms is good; > 15 px means a wrong
   landmark or a wrong model part (that is information).
3. Render the model through that camera (Blender lens = f·36 / long side, roll in Blender's sign) and compare side by
   side and as a 50 % blend. Offsets become pixels: part lengths, component positions, radii and spacings are found
   this way.
4. Re-solve with alternative hypotheses to decide between sources (e.g. two sources' control positions; if the rms
   difference is small, it is inconclusive → keep the drawing). Project circles or outlines from the solved camera onto
   the photo to test radii and positions.
5. Traps: landmarks all on one side extrapolate badly; too few points slide to an orthographic solution (pin f); the
   roll sign flips between a solver and Blender; phone photos at the frame edge carry lens distortion.

## 6. Materials: research, calibrate, audit
- **Measure the photo, then calibrate in isolation.** Build 3–4 swatch plates (with the part's own edge radius), light
  them like the photo (for a sheen texture: a window at the mirror angle, exposure set so the sheen sits mid-grey),
  render at the photo's mm/px and put a 1:1 crop of the photo beside them. One variable per swatch. A measured bump
  value can be invisible; a single noise scaled up looks like sandpaper from above; **two noise scales plus a coarse
  roughness mottle** (e.g. 0.4 mm ×1.5 + 1.2 mm ×1.0 + a 5 mm mottle for a textured lacquer) match in the sheen and
  stay quiet head-on.
- **Audit every identifiable component:** component → reference crop (user photo, or the closest variant, or a cited
  source) → the same crop from a camera-matched render lit like the photo → the material settings → a verdict. Two or
  three rounds; write a material audit doc with the physical material, the reference, the settings and what changed.
  Include the props.
- **Light the audit like the photo, not like a studio.** A large overhead panel greys a dark glossy prop that the
  photo's small lamp shows dark with one band; a studio backdrop can block the photo's window light entirely.
- **Intent vs age.** Photos of an old unit show dust, bloom, lint, burnish, smudges, pitting and dulled plating. Render
  the finish as designed unless the brief asks for patina: keep the age layer as a switch, off by default
  (`wear-materials.md`). The design finish (grain, blast, diamond cut, gloss, stipple, print) stays.

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
6. **Keep the real colour.** Don't brighten or desaturate a texture into a different material (a brightening chain can
   turn one wood species into another). Target the measured mean colour of reference photos of the real finish under
   neutral light, keep the texture's own contrast, and set roughness and coat by the real finish (render intent, not
   age).
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
