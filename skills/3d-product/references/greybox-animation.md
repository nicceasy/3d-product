# Grey-box animation pass: FIRST → KEY → LAST

Runs after the FKL frames (`fkl-frames.md`) and before production renders. Every approved FIRST/KEY/LAST shot becomes a
moving shot in grey clay, so timing, speed, mechanisms and cuts are judged before any expensive frame. How the camera
moves is `camera-motion.md` §0 (simple moves, anchored on the KEY); this file covers the order of work, speed limits,
mechanism physics, the cut rules, per-frame checks, review, and the numeric hand-off.

## Order of work
1. **Research** (parallel agents, reference frames paired with every finding): video types and the chosen format's
   beats (R4); easing, mechanism physics and light over time (R5); cutting, rhythm and the edit tool's scripting API
   (R6).
2. **Script:** a logline, the intention, a light arc, acts, and per shot: beat, intention, how it builds the whole,
   camera, product state, focus, light (for the beauty round), cut. The script is the source of truth: when the
   animation changes a shot, fix the script text first (`shots-and-script.md`).
3. **Spec each shot:** the ambient state (the product alive), mechanism keys, racks, special grammar (match cuts, probe
   slices, holds).
4. **Plan all shots without rendering:** timings, the per-frame checks, the edit plan. It costs minutes for a whole film
   and catches most speed and continuity faults.
5. **Render in script order, one shot at a time:** review it, fix it, write the finding into the log, *then* the next
   shot. A finding that changes the process (a new check, a new pass) is applied to the remaining shots and queued as
   re-renders for the finished ones.
6. A board section per act (GIF + KEY poster + review sheet), and the edit project at the end.

## Speed limits (R5, 24 fps, 180° shutter)
| Move | Medium | Slow |
|---|---|---|
| push / pull (in ln W, % of the field per second) | 10 %/s (pull up to 14) | 6 %/s |
| arc / orbit | 4°/s | 2.5°/s |
| truck, pan, slide (% of the frame width per second) | 6.5 % W/s | 4 % W/s |
| probe glide (linear) | 10 % W/s | — |
| creep (a moving hold) | 1 %/s | — |

- **Judder ceiling:** one frame width per 7 s = 14.3 % W/s (≈ 11 px/frame at 1920). A defocused background may run 2×.
- These are ceilings. `camera-motion.md` §0 gives the default rates for simple moves (push 2–9 %/s, arc 1.6–2.5°/s,
  under the lens cap).
- A push in ln W gives a constant perceived zoom rate (the camera's mm/s falls as it nears the subject).
- **Size the move from its duration**, or lengthen the shot to 8–10 s when the move is the story. Compute speeds
  numerically before rendering the FKL. Measured: first-draft moves typically run 2–5× over because durations were
  fixed first.
- **Racks** in dioptres, starting 4–8 f after the KEY, lasting 18–36 f depending on the other plane's blur swing, and
  landing ≥ 24 f before LAST; or "focus as a pointer" (tied to the path, with a lead). When the two planes are < 5 DOF
  apart the rack is a garnish: let the move lead.
- Retired: a C1 path through FIRST/KEY/LAST with an entry ramp, a cruise and a raised-cosine settle to a creep. It
  wobbled and its extrapolated FIRST frames were weak; replaced by constant-rate simple moves.

## Mechanisms on physical curves (rules of thumb)
A mechanism's curve claims its mass and its drive, so each one moves on the curve its physics gives it.
| Mechanism | Curve |
|---|---|
| A hinged cover lifted by hand | minimum jerk over 2.5–3 s, stopping dead; a strong ease-in (first 0.5 s < 10 % of the travel) |
| A cover lowered on a friction hinge | ease-out, landing softly |
| A cam or lever lift | 0.75–1 s ease-out, 1 − e^(−4u) |
| A swing driven by a spring or a motor | constant (e.g. ≈ 10°/s) with 4-frame ramps; show the full travel |
| Damped lowering (viscous damper) | a short ease-in, then constant (e.g. 2.5–3 mm/s); focus lands on the touch |
| A rotor at speed (a disc, a fan, a wheel) | constant rate: rpm × 6 / fps degrees per frame; spin-up τ ≈ 0.4 s, coast-down τ 1.6–2 s; print on it smears at the rim |
| A follower that must stay in contact | solve the contact every frame by ray cast (engage within ~1 mm, gap within a few µm); never key it by eye |
| Micro-life | small secondary motion from a real cause (a runout, a warp, an eccentric), a fraction of a degree |
| Indicator light | instant |

- **The product is alive in every shot** unless the story says otherwise; one light event per shot, never during a
  mechanism.
- Parts move only when the mechanism allows, and every moving part clears every other part (`editing.md` §4).

## Contact mechanisms: sub-frame QA (one part riding another)
When a shot is about a part riding another (a follower on a cam, a tip on a moving surface, a wheel on a track, a
roller on a belt), the user asks for the animation to be correct before anything else, and a close-up shows every
error. Measure on the **saved shot file as it plays** (its keyed curves at integer frames plus ~10 sub-frames per frame,
≈ 240 Hz), not on the generator that wrote it; a check on the generator misses keying and interpolation errors.
| Check | Rule of thumb |
|---|---|
| Contact gap (the riding point vs a ray cast to the surface) | within a few tens of µm at a fine contact (≤ ~20 µm), never penetrating, at every sub-frame |
| Rate | the driven rate exact per frame (e.g. rpm × 6 / fps degrees), in the right direction |
| Phase lock | a periodic deformation (a warp, a runout) locked to the rotation: fit it as a function of the rotation angle (residual small against the tolerance), its first harmonic matching the measured reference within ~15 %, and the follower's tilt correlating > 0.99 with it |
| Continuity across the cuts | the follower's position (radius, swing) at the shot's in and out equal to the neighbours' out and in |
| Intersections | BVH overlaps: only the intended contact touches |
| Camera follow (if the camera rides the part) | the part's screen drift against the KEY ≤ ~0.5 px |
| Surface motion | the surface under the contact moves the right way (its velocity against the tangent) |
| Motion-blur interpolation | the renderer interpolates between frame keys inside the shutter: compare the key-lerped surface with the true one at sub-frames; the error must be far under the contact tolerance |
A shot that passes all of them goes on; any fail is fixed in the solver, then the whole table is re-run.

## The cuts (R6), per shot
- IN = FIRST + 12 f (the head handle is never seen); KEY = IN + 18 f. Arrivals: OUT = LAST + 24 f. Departures (the move
  hands its momentum to the next shot): OUT at 90 % of the travel, still moving. Floor 90 f.
- **Match on action** (a part moves across the cut): design the pair as *one motion on one clock*. The A shot gets a
  pre-beat that states the still object, then the part moves and the edit leaves at 30–60 % of its travel. The B shot
  is the same curve shifted so its locked KEY state lands on its own frame, and the cut enters B on the frame whose
  part value is nearest A's last (≈ 1 f repeated). Same screen direction; an axial cut-in (×3, ≤ 10°) hides it best.
- **A match cut on a mechanism: the A shot ends where the B shot picks up.** If A's LAST shows the part stopped at full
  travel while B's FIRST shows it still moving mid-travel, the part jumps back on screen. Cut A mid-travel, shift B's
  curve so its KEY state lands on its own frame, and enter B at A's last value.
- **Never replay an action across a cut.** Check pose continuity numerically at every cut: every mechanism's state in
  N's LAST equals N+1's FIRST (`fkl-frames.md` §4). A planned match cut shares its framing (the same elevation, or plan
  views on both sides).
- **When the event lands before the camera settles, the settle is the hold:** OUT = LAST (no extra hold).
- **Probe and constant-speed glides are sliced**, not completed: a ≈ 5.5 s window containing the KEY, focus finding
  the target early, the cut leaving mid-glide.
- **Departures save frames:** past ≈ 90 % of a truck the object's edge and the room slide in; the cut never shows them.

## Checks every frame (logged per shot, read by the review sheet)
- **Focus targets occluded?** Ray-cast both focus points, with glass covers excluded. A rack target hidden behind a
  lip of the product fails, and a grey-box still will have hidden it too.
- **Withheld marks** (a reveal saves the name): each printed name or logo point in frame, facing the camera (dot the
  face's outward normal with the view ray; without it a rear view "sees" a print through the inside of a wall) and
  unoccluded, with its cap height and defocus → legible when cap ≥ 10 px @1920 and blur < cap. Print the table for
  every planned shot before anything renders. Fix by framing or, when the frame is locked, by light (keep the face in
  shadow with a black card), written into the script's light direction.

## Grey-box look
- Clay + **ink**: prints are composition (leading lines, legends, a withheld logo). Keep the product's print textures
  as dark ink over the clay. Plain clay frames print shots blind; carry the ink into the lock-in stills as well.
- Rotating parts keep an asymmetric print (a flat colour hides the spin); emitters and glass keep their materials.
- Measured: Cycles 960×540, 8 spp + OIDN, motion blur 0.5, persistent data ≈ 2.2–2.4 s/frame on a laptop-class GPU
  (measured once), so a 30-shot film (≈ 6,500 f) is a few hours.

## Review sheet
Strip FIRST · edit IN · KEY · mid · LAST · edit OUT (chronological), with plots of subject speed on screen, camera speed
(mm/s, °/s), blur of the KEY and LAST focus planes, the path / rack / mechanism progress, and the edit window as a light
band. A JSON carries the speeds, occlusions and the withheld table. Clips: ProRes 422 HQ .mov (for the edit), H.264
.mp4, a 12 fps GIF (board). FigJam's MCP screenshot renderer draws GIF fills blank: layer the KEY frame as a poster
under the GIF fill (`figjam-board.md`).

## Lighting as an animated element (directions for the beauty round)
- One light event per shot, never during a mechanism; reflections sliding with the camera are free.
- A rotating reflective cover sweeps its reflection at 2× its angle: time a flash mid-lift.
- An anisotropic sheen (grooves, brushing) does not rotate with a spinning part; only printed marks and dust do.
- A rack *through* a reflective cover needs the reflection flagged: the eye goes to the brightest sharp thing, and a
  reflection focuses at its virtual distance.

## What a first beauty round taught (the author's verdicts)
- **What works:** a named subject + an arc or orbit around it, or one long dynamic move, + optionally one mechanism
  event. A locked camera on one mechanism with focus landing on its moment reads; so does a glide along a row.
- **What fails:**
  - FIRST frames that were only extrapolated from the KEY/LAST move ("start frame needs better composition with follow
    through to final"). Compose FIRST, KEY and LAST as three stills that each stand on their own.
  - No subject, or a rack focus with no intention: every frame needs something the viewer can name, and the shot
    either explores that subject or moves from one subject to the next.
  - Too narrow: too many shots of individual components; show more of the product.
  - Moves too short or too timid where the action is big ("show the full move", "longer move").
  - DOF too shallow in an ECU: the "reasonable" table in `greybox-composition.md` is a ceiling on blur, not a target.
  - Small timing notes the grey-box review misses: a hinge starting a quarter second early, too little ease-in, a
    control on the wrong third, a button that should stay in focus. Look for them at the animatic.

## The animatic finalises the edit and the script
Cut points, match cuts on action, act lengths and the runtime are decided on a low-resolution animatic (`SKILL.md`
stage 9, `editing.md` §7); what reads slow or redundant is trimmed or folded there. Every change goes into the shot
list and script first, then into the shot JSON.

## The numeric hand-off
One shot JSON, built from the spec and its builder (`shots-and-script.md` §7), carries per shot:
- `story`, `light`;
- `frames` (FIRST / KEY / LAST), each with the orbit parameters (az / el / field W / real f / N / place / roll /
  subject / focus point), the Blender world camera (location, quaternion, hfov, Blender lens and f-stop, pupil, focus
  distance, shift), pose, light state, placement, card, set, gates and render paths;
- `motion`: duration, fps, `timing` (t_first / t_key / t_last), the interpolation rule, `product_channels` (every
  mechanism: keys + interpolation), `light_channels`, and `keys` per FKL frame.
Conventions are written in the file's own `conventions` block (product-local mm, az 0 = in front, Blender focal
f(1+m), f-stop N(1+m), m = 36/W). A baker turns it into per-frame packs for the production engine
(`octane-production.md` §3), evaluating the motion verbatim, never re-interpolating.
