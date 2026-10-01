# Finding strong compositions of a product

The user's bar for every FIRST, KEY and LAST frame: **a subject the viewer can name** (a part, or a reflection, colour
or shape) and **a strong stand-alone composition**; more of the whole product than of its components; the product's
pose and the light used as composition tools; research from minimalist painting, graphic design and art; and a set of
about 50 strong compositions, all outstanding before anything is uploaded. Compose stills first; moves connect
composed frames later.

## The grammar that worked (research, evidence from the references)
- One nameable subject that wins ≥ 2 of 4 attention cues · the product as a **figure against a ground** (an automated
  lock-in tends to fill the frame edge to edge with the product, which makes it wallpaper, not a shape) · 2–3 value
  masses that ARE the objects · few shapes, one dominant · no tangents, bold crops · long lines level (≤ 0.5°) or
  clearly diagonal (≥ 10°) · light, shadow and reflection as shapes · one colour accent in a neutral field.
- **Archetypes named from real references**, mapped onto each product's own shapes: Black Slab (a dark mass), Kelly
  Window (a bright opening), Rothko Stack (stacked value bands), Albers Plan (nested squares in plan), Sugimoto Theater
  (a bright window mirrored in a glass plane), Hammershøi Sun Patch (a patch of light on a surface), Newman Zip (one thin
  line crossing a field), Arcs (concentric circles or grooves), profiles, rhythm rows.
- **No image metric predicted the author's verdicts (AUC ≤ 0.65)**: measurements gate and rank, the eye chooses.

## The process
1. Write down the product's vocabulary (shapes, colour notes, reflective surfaces and what they mirror, the range of
   motion of every mechanism) and the set's measured traps (props that frame or block views, lines that align at a
   given elevation, near-misses at a given azimuth, edges that go "almost level" in an azimuth band, lenses that put
   the camera behind furniture).
2. Archetypes, not cameras: each carries a mode (calm, dynamic, symmetric, field, macro), principles, camera ranges and
   the pose × light × placement setups.
3. Sample 20–30 cameras per archetype × setup; **pre-gate by geometry before rendering** (occluders, subject hidden,
   tangents, near-level lines, whole product in frame). Measured: ≈ 80 % die here, at ≈ 0.5 s each.
4. Preview in the **final look** at 640×360 (measured: 1–2 s per camera change on a laptop GPU with persistent data).
5. Gate (subject, sharpness, edges, tangents, lines, glossy black surfaces turning silver…) → rank within the
   archetype's mode → contact sheets → the eye pass (below; "OK" is a reject) → repair by diagnosis (below).
6. Select with quotas: ≥ 60 % whole or most of the product (≥ 30 % whole), ≤ 3 per archetype, ≥ 4 light states
   including dusk, the colour accent present in a share of frames, some frames with a visual element as the subject,
   and **no near-duplicates at thumbnail size**. A plain-language justification per frame.
7. Finals: one keyed .blend (frame i = composition i) → the render node, one Blender per GPU, each frame its own EXR.

**Eye-review checklist** (yes/no, most important first):
1. Can I name the subject in ≤ 4 words within one second?
2. Squinting, do I see 2–3 big value masses, with the subject (or the product) one of them or on their boundary?
3. Is there one dominant shape, with nothing fighting it?
4. Does the frame show enough of the product for its role, as a figure against a ground, not wallpaper?
5. Are all four frame edges intentional: no near-misses, no nicks, bold crops?
6. No tangents: no edges kissing, no line continuing another, nothing growing out of the product?
7. Are the long lines level or clearly diagonal, nothing "almost level"?
8. Is the empty space one calm shape (could a line of type sit in it)?
9. Is it balanced, asymmetrically or truly symmetrically, and not almost symmetric?
10. Is there at most one colour accent, on or pointing to the subject?
11. Does the light make a shape (patch, line, reflection, shadow) that helps the subject rather than fogging the frame?
12. Are the divisions unequal and deliberate (no halves, no equal gaps unless it is a rhythm)?
13. Does the eye enter, travel along a line and stop on the subject, rather than leave the frame?
14. Would I print it and hang it: a clear read at a glance and a second read up close?
15. Across FIRST → KEY → LAST, is it one subject explored or one clear relay, with every frame composed?

**Repair by diagnosis.** Each keeper gets about 8 variants; each changes **one factor** and targets the failing gate or
the eye note, so a parent | variant sheet shows which single change helped, and the best twin goes forward.
| Diagnosis | Variant |
|---|---|
| nick / near-miss | field ×1.12 or ×1.25, or a fill fraction of ≈ 0.72 |
| near-level line | az ±6 or ±12 (past 10°), or a true plan (el 90) |
| tangent | el ±2.5, az +3 |
| soft subject | focus on the subject's visible surface, one stop down (within the diffraction gate, `fkl-frames.md` §2) |
| cut subject | re-centre, field ×1.15 |
| subject doesn't win | another light first, then one stop open |
| glossy black surface mirroring a bright window | az ±15, or a dusk light state |
| foreground occluder | az ±8, a longer lens |
Hints can also change the pose (a mechanism's angle, a printed part's rotation) or the light state (a lower sun, dusk).

## What the lead's review rounds added (the part the automation missed)
- A first round tends to have beautiful light but repeat two camera families (e.g. many high three-quarters with a
  cover raised, many overhead plans) and let the set's props compete → **cap the families** (≤ 3 high three-quarter,
  ≤ 4 plans, ≤ 4 close-ups of one detail) and fix competing props with the camera; never hide a visible prop or a
  cover, hide only what no ray reaches (`fkl-frames.md` §4 item 2).
- Look for what is missing, as a checklist of types: eye-level slabs, pure profiles, a glass plane against a window,
  the product small under a large window, window light on a textured wall, shadow grids across a surface.
- Replace the weakest frames (a weak silhouette, near-duplicates, clutter) with small precise subjects (a notch, a
  rest, a few keys and a light) and a leading line (a long edge of the furniture).
- Rebuilding a scene file for a fix can silently drop objects that shape the light (e.g. outdoor buildings shading a
  window) → re-render fixes from the approved file, and diff each fix against the approved image outside the change.
- Technical: aim frontal and plan frames by lens shift, not yaw (yaw tilts level lines into the "almost level" band);
  size whole-product frames by fill fraction, not field width; focus on the visible surface, not a bounding-box centre;
  a glossy black surface mirrors bright windows at most daylight eye-level angles (dusk or plan views keep it black).
