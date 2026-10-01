# Grey-box composition lock-in

The user's process for storyboards with camera moves:
1. Research what to show (the product's functions and unique elements) and how to move (moves, rack focus, bokeh,
   composition), both with reference images.
2. Render ≥ 30 grey-box pairs (KEY frame + LAST frame), straight from render, with no comp.
3. Analyse them against composition principles.
4. The user picks about 10.
5. Full renders, comped and graded.

Grey box first because a camera, a pose and a DOF choice cost seconds in clay and hours in a lit sequence.

## The lock-in harness (what it must do)
- **Build the set once**, then per shot:
  - swap in the posed product (cached exports per pose: each mechanism at its story states);
  - clay every material except glass and emitters, so windows and practicals still light the set and make bokeh;
  - render each frame with real DOF to EXR (Combined, Depth, Object Index: product / subject / any secondary part);
  - write JSON with the camera, focus, the projected subjects and both frames' focus points, plus ray-cast occlusion
    (the first hit from the camera to each subject);
  - allow a metadata-only rerun that rewrites the JSON without rendering.
  Measured: ≈ 15 s per frame at 1280×720, 64 spp on a laptop-class GPU (measured once); the set build ≈ 12 s.
- **Physical camera spec:**
  - Inputs: `subject`, `az` (0 = front), `el`, `W` (field width at the subject, mm), `f` (real lens), `N` (real
    f-number), `place` (u, v) where the subject lands in frame, and `focus`.
  - Derived: m = 36/W, s = f(1 + 1/m), Blender focal = f(1 + m), Blender f-stop = N(1 + m).
  - A hold-location option pans or tilts from the KEY camera.
  - DOF depends only on m and N; focal length sets perspective and bokeh size.
- **Post:** EXR → PNG in the exact view transform the final uses, plus metric depth and the index mask.
- **Analyse** each frame and the pair:
  - placement against thirds / phi / spiral eye / Westhoff / centre with the null hit rate, spiral flow credited only
    when edges follow it, leading lines, balance, dominance, negative space, metric depth layers, thin-lens DOF,
    bokeh, edge tension and tilt, and a pair score for the move;
  - **F** (DOF and rack readability: blur at the projected subjects, px at 1920) and **H** (one dominant change over
    threshold: scale ×1.25, arc/pedestal 12°, truck 20 % of the field, rack 12 px each way, plus the mechanism when the
    pose changes);
  - score = 0.6 × the pair score + 20·F/4 + 20·H/4;
  - outputs a clean stacked pair (for picking) and an annotated pair (overlays) per shot, plus a ranking.

## Lessons
- **Composition evidence:** thirds and golden-spiral placement barely predict preference. The spiral scored 0 on
  every honest test. Inward bias, lead room, converging lines, depth layers and eye-trace continuity do the work.
  Report the grid, but don't worship it.
- **A still pair reads as a move** only with one dominant change over threshold. A second camera change must stay
  under half of the first; a rack or the mechanism may ride along.
- **"Reasonable but present" DOF** (a ceiling on blur, not a target):

  | Shot | DOF | Stop |
  |---|---|---|
  | ECU | 1.3–3.5 mm | f/5.6–8 |
  | CU | 4–7 mm | f/4–5.6 |
  | MCU | 11–21 mm | f/4–5.6 |
  | MS | 90–130 mm | f/5.6–8 |

  A rack reads only when the planes are ≥ 5 DOF apart (≥ 12 px each way at 1920).
- **Bokeh:** look down the set's longest depth, never into a wall a few hundred mm behind the product. Top-downs have
  no defocused plane.
- **The set limits the camera:** measure the clearance around the product in every direction (neighbouring props, the
  wall behind, a window embrasure) before sampling cameras. Ray-cast occlusion finds props blocking cameras. A camera
  behind the product may look through an open cover: choose a pose or angle where the cover reads (`lighting.md` §6).
- **What clay hides:** printed legends, logos and labels vanish. Shots that depend on them can't be judged in plain
  clay (keep the ink, `greybox-animation.md`).
- **Look at every pair yourself.** A scorer catches out-of-frame subjects and shallow racks. It can't see that a frame
  is mostly background furniture.

## After the beauty round (what the user's review added)
- The lock-in scores KEY/LAST pairs, but the user judges **FIRST, KEY and LAST each as a stand-alone composition with
  a subject**. Extrapolated FIRST frames are the weakest frames of a film. Score all three.
- A subject can be a component *or* a visual element (a reflection, a colour, a shape). A frame with no nameable
  subject fails no matter how good its grid placement is.
- Component-only framing gets repetitive ("way too focused on individual components"). Balance macro details with
  frames where the whole product, or a large part of it, makes the shape.
- Posing the product (every mechanism's state, what it is doing) and the light are composition tools, not fixed
  givens: explore them together with the camera.
