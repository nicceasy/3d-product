# Camera motion: simple moves, the operator layer, gates, and the motion-review playblast

The author's rules for camera moves in product films, and how to build, gate and review them for any product. Simple moves (§0) are the base; the operator
layer (§6) is the default on top of them.

## 0 · The rule: SIMPLE MOVES (a standing rule; it overrides the spline rig in §2)
The user rejected moves threaded through several stills: "moving in too many dimensions. Camera is turning floating
changing direction ... I want the move to be simple!"
- **At most two motion sources, the aim and the body. At most two animated dimensions: one primary plus one subtle
  secondary** (secondary/primary ratio ≤ 0.25, default 0.10–0.20).
- **Construction, anchored on the approved KEY:** camera(t) = G(r·(t − t_KEY)) · KEY, where G is one constant-rate
  move:
  - scaling about the aim (a push or pull, linear in ln distance);
  - an arc about the vertical through the aim;
  - a crane (an elevation arc about the aim);
  - a translation (a truck, pedestal or slide, with the aim parallel);
  - a pan or tilt about the lens (≤ ±10°, with the body static).

  A pair is the product of two generators. The frame-to-frame change is identical on every frame, so the motion
  vector never changes and nothing can wobble.
- **Legal pairs, with the aim locked:** push/pull + boom (a log spiral) and arc + track (an azimuth spiral). Anything
  else is one move or a cut.
- **Group moves:** when several shots share a move (a match-cut pair, a family of views), give them the same generator
  and rate, each anchored on its own KEY, so the motion continues across the cut.
- **The aim never follows a moving part.** It is locked on its KEY pixel, parallel with the body, or panning at a
  constant rate. Lock the camera while a mechanism acts; move it while the object rests. **The one named exception:**
  when the user asks for it, a camera may ride a moving part rigidly (its translation only, no rotation) so the part
  holds still in frame while the world moves past; the operator layer (§6) then turns the rigid ride into a lagged
  follow.
- **No look-at, no up vector.** Orientation is the move's rotation composed with the KEY's, so a top-down shot cannot
  flip. Lens, roll, shift and f-stop are constant. Focus follows the aim; a rack uses up the secondary slot.
- **No roll**, ever, unless the brief names it.
- **Constant speed from the first frame to the last. No ramps or settles inside a shot** (cuts come mid-move).
- **Speeds (rules of thumb at 24 fps, 180° shutter):** push 2–9 %/s of the field; arc/crane 1.6–2.5°/s, under the
  lens cap (85 mm 3.8°/s, 100 mm 3.2°/s, 135 mm 2.4°/s with a sharp background; aim for half); truck/slide about
  4 % W/s. A top-down *rotation* reads as roll: use a slide.
- **FIRST and LAST are outcomes of the move**, not anchors. To convert an older multi-axis move:
  1. split its change into components;
  2. keep the largest as the primary;
  3. keep one legal subtle secondary, if there is one;
  4. drop everything else;
  5. re-review FIRST and LAST as compositions.
- **Show:** a top view and a side view of each shot's body path and aim, with the grey playblast of every shot plus
  the edit (§4).

## 1 · Why moves look wrong (causes, measured)
- **Per-axis keys, or a separate ease on each channel.** X, Y, Z, rotation, lens and focus each accelerate on their own
  timing. The speed wanders (±9 % measured) and the path bends into S-curves. Auto-clamped Bézier flattens each channel
  at its own extreme.
- **Splines in a parameter that isn't arc length.** A Catmull-Rom or Hermite through waypoints wobbles in speed (×1.2);
  a C1 waypoint is a step in acceleration, which reads as a bump.
- **Orientation interpolated instead of aimed.** Splining quaternions makes the subject swim across the frame with
  reversals, even when every still puts it on the same pixel.
- **World-up look-at near vertical** (elevation ≳ 60°) makes the roll twitch.
- **Focus interpolated, not measured**, which leaves the subject soft between keys.

## 2 · History: the spline rig (superseded by §0; keep for moves the brief explicitly wants complex)
- **Body:** a C2 spline through the stills' world matrices, re-parameterised by arc length, driven by one progress curve
  with an entry ramp, cruise and settle.
- **Metric:** arcs, orbits, pushes and pulls use *relative* speed |dC/dt| / |A − C| when the camera-to-aim distance varies
  more than 1.15×; otherwise world m/s. Record the choice and gate in it.
- **Look:** aim at a target in a *parallel-transported* frame; roll and framing offset are separate smooth channels.
- **Aim hand-off between subjects:** one target on a C2 curve, or (1 − w)·S1 + w·S2 with w = smootherstep. On moving
  parts, zero-lag smoothing of the part's known path (σ 0.15 s); never hard-pin a moving part.
- **Focus:** measured every sub-frame; racks in dioptres (1/d), monotone, starting 4–8 frames after the KEY and landing
  ≥ 24 frames before LAST.
- **Lens:** unit-focus breathing f·d/(d − f); zooms in ln f; dolly-zoom with the lens ∝ distance.
- **One rig module feeds every consumer** (the preview renderer, the final engine's packs, visibility audits, QA,
  playblasts). Several copies of the path code are how moves drift apart.

## 3 · Gates (240 Hz sub-frames, central differences, margin frames 0 and N+1)
These run on the base move; the operator layer on top has its own gates (§6).
For simple moves (§0):
- the relative transform per frame is constant (≤ 1e-6 rad, 1e-3 mm);
- ≤ 2 legal generators; lens, roll and shift constant; KEY exact;
- the subject stays in frame; no occlusion (sample every 6th frame);
- camera clearance to the set ≥ 20 mm (BVH);
- image flow under the ceiling.

For any move:
| Gate | Limit |
|---|---|
| cruise speed max / min | ≤ 1.10, no interior dip or bump > 3 % of cruise speed |
| acceleration step | ≤ 0.1 × cruise speed per second; jerk ratio at 240 Hz / 24 fps ≤ 2 |
| direction of travel turns | ≤ 30°/s |
| aim rate ω | C2, a single hump (no interior bump > 10 % of its peak) |
| subject swim | pinned to the stills' pixel; 0 velocity reversals |
| image flow | target ≈ 5 px/frame, ceiling ≈ 11 px/frame at 1920 wide (the 7-second rule) |
| focus error | ≤ 10 % of the half depth of field |
| FIRST/KEY/LAST exactness | ≤ 0.5 mm, 0.01°, 0.01 mm lens |

A KEY anchored to a mechanism, rack or light event is locked. Intended exceptions are named per shot in the data. Flow
over the ceiling means lengthening the shot or reframing it; never exceed it silently.

## 4 · Motion review: playblast every shot, then the edit (the review format)
The numbers catch the jumps; the user judges the feel. Every camera change goes to review as a playblast of **all**
shots, not a few before/after clips:
1. **Render grey playblasts** (Workbench) of every 24 fps frame of every shot from the current camera source; check the
   camera file is older than the frames (a stale film looks right and is wrong). The shot's KEY set state, no DOF, no
   blur, 960×540 JPEG. Rule of thumb: ≈ 0.2–0.3 s/frame on a laptop GPU, so a 5-minute film takes ≈ 15 min in two
   processes.
2. **Compose for review:**
   - one **H.264 clip per shot** with a caption bar (shot, title, act, frame/N, shot time, film time, a FIRST/KEY/LAST
     flag) and a **motion strip** under the picture: camera speed (in the rig's metric), aim rate and lens, each scaled
     to its own peak, with F/K/L ticks and a playhead. A jump shows as a kink under the playhead;
   - the **edit**: every shot in film order, straight cuts, plus a phone copy (< 28 MB);
   - per-shot stats (peak and mean speed and aim rate, peak frame-to-frame change) and the FKL frames for a sheet.
3. **Publish** flat to the review folder (`SKILL.md` stage 13) and send the phone edit.
4. **Review order:** the edit first for flow and cuts, then the flagged shots one at a time with the strip. Fix in the
   rig, re-run QA, and re-playblast *every* shot: retimes change the cuts, and new in-betweens change what is visible.
5. **Only then** re-run unseen-object trims on the final cameras (checked densely along the whole move) and render lit
   animatics or finals (`editing.md` §7).

## 5 · Traps
- A playblast rendered before the cameras were rebuilt: compare file times, or the frame count against the camera file.
- World speed on a push or arc falls as the camera nears the subject although its relative speed is constant. Read the
  strip in the metric the rig gates in.
- A peak-normalised strip exaggerates tiny moves (0.5°/s looks like a wave): read the printed peak first.
- Cuts that carry motion: the aim rate at the cut should continue into the next shot. Check it in the edit, where the
  per-shot clips can't show it.

## 6 · The operator layer: imperfections a real operator makes (the default on top of simple moves)
The user found the simple moves "unnaturally steady" and approved a layer of small, real-operator imperfections at the
first strength shown ("just the amount we're looking for"). It is a layer on the simple move, never a replacement:
the move's generator, rate, lens, roll and the mechanism stay untouched.

**What real operated motion is (measured in published shake data and practice):** mostly slow, random-walk-like drift,
not tremor. Recorded handheld shake puts 75–100 % of its power below 0.5 Hz and only 0–2.5 % at 5–12 Hz; a support's
own ring (a tripod at 8–30 Hz) lies above the 12 Hz limit of 24 fps and shows only as blur. "A person operated this"
comes from slow things: a hand on a dragged head, a push whose speed breathes, a follow that runs ~0.1–0.2 s late, an
occasional small bump or a jib's soft bounce. Noise-based shake tools look synthetic because they spread power evenly
per octave, which puts far too much above 2 Hz.

**Thresholds (px at 1920 wide):** shake becomes noticeable at ~0.5–0.8 px of translation; a 10 Hz oscillation is
visible down to ~0.2 px; slow drift against the frame edge is detectable at ~1–2 px/s. So: drift at or just above the
drift threshold, everything fast below the shake threshold.

**The model.** Per shot, deterministic (seeded from the shot's id), in camera-local axes:
M_op(f) = M_move(τ(f)) · T_local(dx, dy, dz) · R_local(pan, tilt), no roll; τ(f) = f + ε(f) is the speed breathing.
Every channel is re-centred so the KEY is exact: c(t) − c(t_KEY)·exp(−½((t − t_KEY)/σ)²) with σ ≈ 0.9 s, a correction
slower than 0.3 Hz that can't add jitter. Amplitudes are specified in px on the KEY focus plane and converted per shot
to degrees and millimetres (on a close-up 1 mm of camera travel can be 5–27 px, so translation noise stays
sub-millimetre).

| Channel | Rig it imitates | Rule of thumb |
|---|---|---|
| Drift (pan, tilt) | a hand on a fluid head's bar | 1/f^1.2–1.5 noise band-passed 0.05–0.7 Hz, ~1–2 px RMS per axis (pan a little more on arcs) |
| Support resonance | jib / dolly or slider / tripod | jib ~0.9 Hz, ζ ~0.1, ≤ 0.6 px; dolly or slider ~3–3.6 Hz, ζ 0.15–0.2, ~0.15 px; a static head ~2.4 Hz, ~0.12 px |
| Bumps | wheel grit on a track, a slider's carriage | ~1 per 60–120 mm travelled, ~0.4–0.6 px, a damped ring (~3 Hz, ζ ~0.3) |
| Speed breathing | a hand-pushed dolly, a swung jib | ±1–2 % of the move's rate (RMS ~1 %), 0.08–0.6 Hz |
| Focus puller | a human on the focus | a lag of ~0.1–0.12 s on the target distance, error ≤ 10–15 % of the half depth of field |
| Ride (a camera following a moving part) | an operator following | a first-order lag (τ ~0.12 s, gain ~0.9) on the part's motion instead of a rigid ride: about 40 % of a slow bob stays in frame |

No handheld preset for slow premium moves: measured on the same shots, handheld is ~10–20 px RMS and 15–20× the
velocity, and it breaks the simple-moves rule.

**Gates (every rendered frame, handles included):** KEY exact (0 px, matrix identical); subject offset RMS ~1–3 px,
peak ≤ ~5 px (≤ ~8 px at a frame corner); offset velocity RMS ≤ ~0.4 px/frame; high-frequency residual (minus a
9-frame moving average) RMS < 0.3 px; ≥ 95 % of the offset's power below 1.5 Hz and < 5 % above 3 Hz; rotation peak
≤ ~0.1°; speed deviation within ±1–3 %; the KEY focus point well inside the frame; the largest frame-to-frame step of
the offset ≤ ~0.8 px; camera clearance unchanged (±2 mm) and ≥ 20 mm; no frame-to-frame step that crosses geometry.

**Review:** grey playblasts of every shot from both camera sets with the same scene state, side by side (current |
operator) with a motion strip on a fixed scale (the subject's offset in px, ±6 px; the speed deviation, ±3 %), plus
each shot full size played A then B, and the edit. Then the user judges the amount; keep a gain control (1 = the
approved amount).
