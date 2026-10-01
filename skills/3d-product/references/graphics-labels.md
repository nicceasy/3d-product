# Graphics and labels on products: designed from references, printed as physical materials, verified in shot

Stage 3 (materials) for any printed surface the camera reads: labels, nameplates, dials, packaging, legends. Tracing
an existing product's print from photos is in `reference-detailing.md` (last sections); this file covers designing new
graphics in a real genre's typography, turning them into physical print materials, and proving them in every shot
before the final.

## 1. Research the category's layout grammar first
**Why:** a graphic reads as real when it follows the conventions of its kind and era; invented layouts read as
props.
1. Find about five real examples per design, each verified at the source (release or edition, year, maker), and
   read the layout from photos of the actual object, not from covers or renders.
2. Write the grammar they share: zones (where the logo band, the data row, the title, the track or spec list, the rim
   or legal text sit, as fractions of the face), the hierarchy, type classes (one size per class across the face),
   case and tracking, the number of inks, ground colours.
3. Typeface names from photos are lookalikes: label them unverified and use them as direction.
4. Invent every name; nothing on the graphic may be a real artist, product or mark.

## 2. Reconstruct the reference typography exactly, then set your own
**Why:** "as close to pixel perfect as possible" is a measurement problem; type set by eye drifts in size, baseline
and tracking, and the user sees it at once.
1. **Deskew the reference photo first** (projection-profile variance over small rotations): even ~1° of rotation
   inflates the boxes of long lines. Rectify a round face to a true circle at its real diameter
   (`reference-detailing.md`, tracing).
2. **Measure every line's box:** ink height (cap and x-height), width, baseline, alignment (centred, flush, on an arc)
   and its distance to the face's edges and centre.
3. **Size per class, not per line:** lines that share a class (tracks, credits, legal) share one size and condensing,
   taken from the class medians, as on the real object.
4. **Fit the reference string first:** set the reference's own text in the chosen face and fit size, x-condensing and
   tracking until its box matches the measured one. That proves the face and the scale; then set your own string with
   the same size and scale on the measured baseline.
5. **Check overlaps and margins:** an overlap report between consecutive lines, and every line inside the face with
   its margin to the edge and any hole (a legal line once ran off the bottom).
6. **Reproduce the reference's letter interplay** (interlocks, overlaps, a dot inside a counter). If the invented name
   can't make the same shapes, change the name: the look wins over the copy (the author: change the name if you have
   to, "i want to get that look correct").
7. Iterate with the user in small visible steps (nudges, a colour wash, five colour options of one word); version
   every step.

## 3. Texture output
- Map the face exactly like the art it replaces (same UV extent, centred on the same point, same resolution class, e.g.
  4096 px), so a swap changes only the image.
- Keep the RGBA master; for engines that ignore alpha, write **flattened** copies: transparent holes take the old art's
  hole colour, the outside of the face takes its edge colour. Colour maps sRGB; data maps linear.
- A check-only view (straight down on the face in the shot's own light) proves it reads the right way round, centred,
  and fills the face.

## 4. Physical print materials
**Why:** a print is ink or foil on paper or plastic: flat colour alone looks pasted on, and a real foil only reads
where it mirrors a light.
- **Maps from one design file:** albedo (sRGB); a foil mask (linear 0..1: metallic weight, the foil taking its ink
  colour as the metal's colour); roughness (paper ~0.6 with fibre variation, foil ~0.2 with faint streaks); a height map
  (paper tooth, flattened under the foil, a slight deboss of the foil) → a tangent-space normal, **gentle**: the paper
  should only break up highlights. Paper as a dielectric of IOR ~1.5.
- **Verify a map's effective strength by measurement, not by its slider.** A mix or blend node may weight the opposite
  input from the one assumed (a "slight" 8 % paper normal once rendered at nearly full strength and looked like
  sandpaper). Render map on and off, measure the change (highlight break-up, high-pass energy), and prefer baking the
  strength into the map over a mix amount.
- **Foil needs its mirror ray:** at most angles it barely differs from flat ink. Check it at an angle where it mirrors
  a lamp or window (sweep the azimuth), and show the user foil and ink versions side by side.

## 5. Prove it in every shot before the final
1. **Visibility by ray sampling over the whole cut:** a few hundred sample points per printed face; a point counts
   when it is in frame and the first opaque hit on its camera ray is the face (glass and volumes see-through, the
   shot's hidden objects removed). Per shot: the share of frames with ≥ ~2 % of the face visible, the largest visible
   fraction, the largest on-screen size, and the best frame. That list is the set of shots to confirm.
2. **Confirmation stills** of every visible shot at final quality, through each shot's own finishing chain, plus 1:1
   crops of the largest occurrences. Approve before any full render.
3. **Motion tests for anything specular** (foil, gloss print, a spinning face): a few seconds per case, so glints and
   shimmer are judged moving.
4. **Search every per-shot override** (render packs, shot files, material overrides) for the old asset: an override
   that swaps an image per shot silently brings the old art back after a master-level change.
5. Version up: only the print material or image changes in a new master version; originals untouched.
