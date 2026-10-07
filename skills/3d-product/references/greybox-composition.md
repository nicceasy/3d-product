# Grey-box lock-in: moves between stamped compositions

The process for storyboards with camera moves, in the author's order ("composition and first key last
frames should happen before motion"):
1. Research what to show (the product's functions and unique elements) and how to move (moves, rack focus, bokeh,
   composition), both with reference images.
2. **Compose stand-alone stills first**, analysed against composition principles (`composition-analysis.md`): the 50
   compositions at preview cost (`composition-exploration.md`), or grey-box stills from this harness. The user stamps
   them.
3. **Render ≥ 30 grey-box moves from the stamped compositions**, straight from render, with no comp. The KEY is a
   stamped composition; FIRST and LAST are where a legal simple move puts the camera.
4. Analyse every end frame as a composition, and every move as a move.
5. The user picks.
6. FIRST / KEY / LAST in the lit preview (stage 8), then production.

Grey box first because a camera, a pose and a DOF choice cost seconds in clay and hours in a lit sequence. Moves second
because a move chosen before its frames are composed gives weak ends: a pair lock-in run first filled the frame edge
to edge with the product in 64 of 68 frames, and the FIRST frames extrapolated along those moves were the weakest
frames of the film [measured].

## The harness (stills and moves)
- **Build the set once**, then per shot:
  - swap in the posed product (cached exports per pose: each mechanism at its story states);
  - clay every material except glass and emitters, so windows and practicals still light the set and make bokeh;
  - render each frame with real DOF to EXR (Combined, Depth, Object Index: product / subject / any secondary part);
  - write JSON with the camera, focus, the projected subjects and the frames' focus points, plus ray-cast occlusion
    (the first hit from the camera to each subject);
  - allow a metadata-only rerun that rewrites the JSON without rendering.
  Measured: ≈ 15 s per frame at 1280×720, 64 spp on a laptop-class GPU (measured once); the set build ≈ 12 s.
- **Physical camera spec:**
  - Inputs: `subject`, `az` (0 = front), `el`, `W` (field width at the subject, mm), `f` (real lens), `N` (real
    f-number), `place` (u, v) where the subject lands in frame, and `focus`.
  - Derived: m = 36/W, s = f(1 + 1/m), Blender focal = f(1 + m), Blender f-stop = N(1 + m).
  - A hold-location option pans or tilts from the KEY camera.
  - DOF depends only on m and N; focal length sets perspective and bokeh size.
- **Post:** EXR → PNG in the exact view transform the previews use, plus metric depth and the index mask; then
  `comp_analysis.py frame` on every frame (`composition-analysis.md` §1).

## Sampling moves: legal simple moves only
Per stamped KEY, sample the moves `camera-motion.md` §0 allows, nothing else:
1. **Generator:** push or pull, arc, crane, truck or pedestal, pan or tilt; or a legal pair (push + boom, arc + track)
   with the secondary ≤ 0.25 of the primary.
2. **Direction:** both signs.
3. **Rate:** under the speed ceiling (`camera-motion.md` §0), sized for the planned duration; sample about half and
   all of the size that duration allows.
4. **t_KEY:** where the KEY sits in the shot: at the start, the middle or the end.
5. **Pre-gate** both ends by geometry (`composition-analysis.md` §B), and every 12th in-between for clearance and
   occlusion.
6. **Render** FIRST and LAST; the KEY once per composition.

A move too small to read within the planned duration at the ceiling is not a move: hold, or cut. Two stamped
compositions that no legal move joins are a cut, never an aperture ramp, a lens swap or a zoom.

## Scoring: the ends as compositions, the move as a move
- **The composition test (a gate).** FIRST and LAST each pass `composition-analysis.md` §C and the image checks of
  §E; the §D items are reported. Clay can't show colour or a glossy black face, so §E3 and G9 wait for the lit
  preview (stage 8). A move whose end fails is repaired by its direction, rate or t_KEY, or dropped.
- **The move test (ranks the survivors):**
  - **F**: DOF and rack readability (blur at the projected subjects, px at 1920);
  - **H**: one dominant change over threshold (scale ×1.25, arc or pedestal 12°, truck 20 % of the field, rack 12 px
    each way, plus the mechanism when the pose changes). A second camera change stays ≤ 0.25 of the first (the
    simple-move rule); a rack or the mechanism may ride along;
  - the pair metrics: subject displacement, scale change, parallax, rack swap;
  - score = 0.6 × the pair score + 20·F/4 + 20·H/4.
- **The shot rules** (`composition-analysis.md` §G2): one subject explored or one clear relay; the subject moves
  ≤ 15 % W between frames, or along a line visible in both.
- **Outputs:** a clean FIRST | KEY | LAST strip per move (for picking), the annotated strip (the analysis tiles), and
  a ranking.

## Lessons
- **"Reasonable but present" DOF** (a ceiling on blur, not a target):

  | Shot | DOF | Stop |
  |---|---|---|
  | ECU | 1.3–3.5 mm | f/5.6–8 |
  | CU | 4–7 mm | f/4–5.6 |
  | MCU | 11–21 mm | f/4–5.6 |
  | MS | 90–130 mm | f/5.6–8 |

  A rack reads only when the planes are ≥ 5 DOF apart (≥ 12 px each way at 1920).
- **Bokeh:** look down the set's longest clear depth (`composition-analysis.md` §A2, §E5), never into a wall a few
  hundred mm behind the product. Top-downs have no defocused plane.
- **The set limits the camera:** the traps and clearances are measured before sampling (`composition-analysis.md`
  §A2). A camera behind the product may look through an open cover: choose a pose or angle where the cover reads
  (`lighting.md` §6).
- **What clay hides:** printed legends, logos and labels vanish. Shots that depend on them can't be judged in plain
  clay (keep the ink, `greybox-animation.md`).
- **Look at every strip yourself.** A scorer catches out-of-frame subjects and shallow racks. It can't see that a frame
  is mostly background furniture.
