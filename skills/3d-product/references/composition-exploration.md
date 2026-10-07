# Finding strong compositions of a product

The user's bar for every FIRST, KEY and LAST frame: **a subject the viewer can name** (a part, or a reflection, colour
or shape) and **a strong stand-alone composition**; more of the whole product than of its components; the product's
pose and the light used as composition tools; research from minimalist painting, graphic design and art; and a set of
about 50 strong compositions, all outstanding before anything is uploaded.
**Order (the author: "composition and first key last frames should happen before motion"):** stand-alone compositions
first, each analysed (`composition-analysis.md`); then the user's stamps; then the moves, sampled only between stamped
compositions (`greybox-composition.md`).

## The grammar that worked (research, evidence from the references)
- One nameable subject that wins ≥ 2 of 4 attention cues · the product as a **figure against a ground** (an automated
  lock-in tends to fill the frame edge to edge with the product, which makes it wallpaper, not a shape) · 2–3 value
  masses that ARE the objects · few shapes, one dominant · no tangents, bold crops · long lines level (≤ 0.5°) or
  clearly diagonal (≥ 10°) · placement deliberate, on an anchor or centred · light, shadow and reflection as shapes ·
  one colour accent in a neutral field. The numbers for each: `composition-analysis.md` §C–§E.
- **Archetypes named from real references**, mapped onto each product's own shapes: Black Slab (a dark mass), Kelly
  Window (a bright opening), Rothko Stack (stacked value bands), Albers Plan (nested squares in plan), Sugimoto Theater
  (a bright window mirrored in a glass plane), Hammershøi Sun Patch (a patch of light on a surface), Newman Zip (one thin
  line crossing a field), Arcs (concentric circles or grooves), profiles, rhythm rows. Each carries a mode (calm,
  dynamic, symmetric, field, macro) that sets its targets (`composition-analysis.md` §D).
- **No image metric predicted the author's verdicts (AUC ≤ 0.65)**: measurements gate and rank, the eye chooses.

## The process
1. **Once per set and brief** (`composition-analysis.md` §A): the product's vocabulary; the set's traps measured by
   projection and written as bands the sampler avoids; the size band per role, the placement policy and the edge
   padding written into the brief.
2. **Archetypes, not cameras:** each carries a mode, principles, camera ranges and the pose × light × placement
   setups.
3. **Sample** 20–30 cameras per archetype × setup and **pre-gate them by geometry before rendering**
   (`composition-analysis.md` §B). Measured: 41–77 % die per round, at ≈ 0.5 s each.
4. **Preview** in the frozen preview look at 640×360, 16 spp + denoiser (measured: 1–2 s per camera change on a laptop
   GPU with persistent data; group candidates by pose and light, which cost 3–30 s to change).
5. **Analyse every preview** (`composition-analysis.md`): the frame gates (§C) and the harmony checks (§E) gate; the
   composition items (§D) rank within the archetype's mode → contact sheets → the eye pass (§F; "OK" is a reject) →
   repair by diagnosis (below).
6. **Select** with quotas: ≥ 60 % whole or most of the product (≥ 30 % whole), ≤ 3 per archetype, ≥ 4 light states
   including dusk, the colour accent present in a share of frames, some frames with a visual element as the subject,
   and **no near-duplicates** (`comp_analysis.py sameness`, then the eye rule; `composition-analysis.md` §G1). A
   plain-language justification per frame.
7. **Finals:** one keyed .blend (frame i = composition i) → the render node, one Blender per GPU, each frame its own
   EXR. Each composition's dressing log (`composition-analysis.md` §E6) is saved with it.
8. **★ The user stamps** the board (read back with `use_figma`, `figjam-board.md`). Stamped compositions become KEYs;
   the moves are sampled from them next (`greybox-composition.md`).

For a short film or a set already known, grey-box stills from the lock-in harness can stand in for the preview-cost 50;
either way every frame is analysed before the stamps.

**Repair by diagnosis.** Each keeper gets about 8 variants; each changes **one factor** and targets the failing gate or
the eye note, so a parent | variant sheet shows which single change helped, and the best twin goes forward.
| Diagnosis | Variant |
|---|---|
| nick / near-miss | field ×1.12 or ×1.25, or re-solve the camera by fill to its role's band (the size table) |
| near-level line | az ±6 or ±12 (past 10°), or a true plan (el 90) |
| tangent | el ±2.5, az +3 |
| placement drifting (6–15 % W from every anchor) | lens shift onto the nearest anchor, or onto the centre |
| a dominant line on the 50 % line | el or lens shift until the line sits on a third, or leaves the frame |
| soft subject | focus on the subject's visible surface, one stop down (within the diffraction gate, `fkl-frames.md` §2) |
| cut subject | re-centre, field ×1.15 |
| subject doesn't win | another light first, then one stop open |
| a rival prop | the camera first, then light, then a plausible move of a few cm, logged; never a hide |
| a dead third or a shapeless dark face | aim up, or light it (`lighting.md` §5); never exposure |
| glossy black surface mirroring a bright window | az ±15, or a dusk light state |
| foreground occluder | az ±8, a longer lens |
Hints can also change the pose (a mechanism's angle, a printed part's rotation) or the light state (a lower sun, dusk).

## What the lead's review rounds added (the part the automation missed)
- A first round tends to have beautiful light but repeat two camera families (e.g. many high three-quarters with a
  cover raised, many overhead plans) and let the set's props compete → **cap the families** (≤ 3 high three-quarter,
  ≤ 4 plans, ≤ 4 close-ups of one detail) and fix competing props with the camera; never hide a visible prop or a
  cover, hide only what no ray reaches (`composition-analysis.md` §E6). Every per-frame gate can pass while the set
  as a whole repeats itself: that is what the sameness measure is for.
- Look for what is missing, as a checklist of types: eye-level slabs, pure profiles, a glass plane against a window,
  the product small under a large window, window light on a textured wall, shadow grids across a surface.
- Replace the weakest frames (a weak silhouette, near-duplicates, clutter) with small precise subjects (a notch, a
  rest, a few buttons and a light) and a leading line (a long edge of the furniture).
- Rebuilding a scene file for a fix can silently drop objects that shape the light (e.g. outdoor buildings shading a
  window) → re-render fixes from the approved file, and diff each fix against the approved image outside the change.
- Technical: aim frontal and plan frames by lens shift, not yaw (yaw tilts level lines into the "almost level" band);
  size whole-product frames by fill, not field width; focus on the visible surface, not a bounding-box centre; a glossy
  black surface mirrors bright windows at most daylight eye-level angles (dusk or plan views keep it black).
