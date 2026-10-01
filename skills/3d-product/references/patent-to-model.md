# From a patent (or any line drawing) to an accurate model

A design patent's drawings are often an engineering plan in disguise: measured properly, at a verified scale, they can
close on a manual's published numbers to under a millimetre. The whole method is measurable: deskew, read line centres,
fix one scale, build a B-rep that cites its pixels, and draw the model back over the drawing to prove it.

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
  - Make moving parts a list and pose them with `Location`s about their real axes (a pivot, a hinge axis).
  - Solve poses from constraints, e.g. the swing angle that puts a part's tip at a given radius.
- **Check closure against specs you did not fit** (a mechanism's published lengths and angles, a diameter, a
  clearance). If the drawing closes on them, it is a plan, and the rest can be trusted to the same precision.

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
- **Perspective check:** draw the B-rep with `project_to_viewport(…, focus=dist)` in perspective, beside the patent's
  perspective figure. Match az/el/dist by eye in 2–3 passes. It makes a strong board image.

## 6. Hand off to detailing and rendering
- Next: `reference-detailing.md` (photos, part-by-part research, camera-matched QA, material audit).
- Export glTF per pose (each moving part's positions combined) into a cache, with part names that match the material
  keys.
- Graphics: draw alpha textures at 24–40 px/mm and map them by the part's **Generated** coordinates (its bounding box)
  with a facing mask. No UVs are needed.
- The accuracy sheet, a chart of the mechanism's geometry against its specs and the perspective match open the board:
  they prove the render is the patent.
