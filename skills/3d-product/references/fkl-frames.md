# FIRST / KEY / LAST: the quality bar, the harness, the independent audit

The FKL frames are the plan for motion and for the production render: a weak or soft frame becomes a weak shot, and a
wrong frame caught at FKL costs minutes where a rendered sequence costs about an hour of rig time.

## 1. The bar (the author's words)
"make sure every single one of them is perfect. They need to justify their existence. Make sure EVERYTHING IS TIGHT.
subject to subject, strong comp to strong comp, intentional motion, subject in focus every time."
- Every FKL frame serves the film's intention (`SKILL.md` stage 1), is a composed still with a subject you can name in
  ≤ 4 words (a part, or a reflection, colour, shape, light patch or shadow), and passes the compositional analysis
  (`composition-analysis.md`).
- **The KEY is a stamped composition. FIRST and LAST are outcomes of the move chosen for them; the move is chosen so
  they are strong.** The stage-7 lock-in (`greybox-composition.md`) picks the generator, direction, rate and t_KEY by
  rendering both ends and analysing them. A weak FIRST or LAST is repaired by the move's direction, its rate or t_KEY,
  never by posing the end by hand. **Never extrapolate a move that wasn't chosen for its ends.** Why: ends composed as
  free stills don't survive the simple-move rule (when a film's moves were simplified after its FIRST and LAST had been
  composed freely, about a fifth of FIRST and a third of LAST frames moved by more than 10 % W, the worst by 40–64 %
  [measured]), and FIRST frames extrapolated along a move chosen for its KEY alone were the weakest frames of a film.
- Stage 9 adds only the operator layer, the timing and the cut. Any camera or cut change there re-runs the analysis on
  the new ends and the edit's in and out frames (`camera-motion.md`, `editing.md`); a frame that fails comes back here.
- **The named subject is sharp in every frame:** combined blur ≤ 2 px at 1920 wide (§2), measured on the subject's
  object-index mask from the depth pass. No KEY caught mid-rack.
- **One lens and one aperture per shot** unless the zoom is the idea. No aperture ramps, lens swaps or zooms to join
  two approved comps into one move: two comps no legal move joins are a cut.
- **Dark frames read through light or camera**, never a +EV grade.
- **Exceptions travel with the user's acceptance.** A frame that fails a gate stays only if the user accepted it at
  stage 7 or here, quoted and recorded with the frame (e.g. a dusk silhouette whose darkness is the point). The audit
  checks the frame still matches what was accepted and doesn't re-open it. An agent's
  own reason is not an exception.
- **Cuts are frames too:** shot N's LAST → shot N+1's FIRST is audited like a frame pair.

## 2. The harness
Frames are data, and one harness renders all of them, so every frame shares the same model, rig and rules.
| Step | What it does |
|---|---|
| Spec → frame data | each frame in product-local mm: subject, az, el, W (field at the subject), f (real lens), N (real f-number), place (u, v), pose, light state, card, set and its dressing log; the KEY reused by its stamped comp's id with its exact parameters; FIRST and LAST computed from the chosen move (generator, direction, rate, t_KEY) |
| Render | headless Blender (`-b --factory-startup`); builds the set once; the master model, the camera rig, the film-wide safe-off list, blackbody practicals, rotational blur on spinning parts at their real rate, black cards, mid-rack focus in dioptres; 32-bit EXR + a JSON of gates per frame |
| Analysis | `comp_analysis.py frame` and `reads_metric.py` on every preview (`composition-analysis.md` §1) → `<frame>.analysis.json` + an annotated tile |
| Preview | the frozen preview look named for stages 7–8 (`composition-analysis.md` §0) at EV 0, plus any per-frame EV recorded in the spec; the EXR untouched |
| Sheets | per-act FIRST \| KEY \| LAST sheets, clean and annotated, published to the review folder |
| Hand-off | the shot JSON: every frame's orbit parameters, world camera, pose, light and gates, and per shot the motion (`greybox-animation.md`, the numeric hand-off) |
| Focus | on the visible surface of the subject, never a bounding-box centre; per-frame overrides recorded in the spec |

Measured: previews at 960×540, 256 spp + OIDN cost ≈ 30–40 s/frame on a laptop-class GPU (measured once). The Blender camera
from the physical spec: m = 36/W, distance s = f(1 + 1/m), Blender focal f(1 + m), Blender f-stop N(1 + m) (the pupil
f/N is kept).

**Focus measurement (the gate formula).** Cycles renders blur on the sensor = (F/N)·(F/s)·|d − s|/d, with F and N the
Blender focal and f-stop, s the focus distance and d the depth; pixels = blur / 36 mm × 1920. Don't use the thin-lens
magnification F/(s − F): it over-reads blur by s/(s − F) (measured ×3.7 at close-ups, ×2 at mid shots).

**Diffraction isn't rendered, so gate it.** Cycles, and Octane's thin lens, render f/28–f/32 macros razor-sharp. A real
lens at N_eff 40–55 (N_eff = N(1 + m), the Blender f-stop) is diffraction-limited: the Airy pattern's first dark ring
is 2.44·λ·N_eff across (λ 0.55 µm) = 2.9–3.9 px at 1920 on a 36 mm frame.

That ring overstates the blur you see. Compare like with like instead: the Airy MTF at 1080p Nyquist (26.7 lp/mm)
equals a geometric disc of **d = N_eff / 24 px** (a 2 px disc ⇔ N_eff 48).

The focus gate for the named subject is then **√(CoC² + d²) ≤ 2 px**:
- One N per shot, chosen to minimise that sum. For a fixed focus, N_opt ≈ √(CoC·N_eff·24), using the CoC measured at
  the current N_eff.
- Parts outside the named subject may fall off, as a real macro's do.
- If no N reaches 2 px, place the focus better or reframe minimally (a wider W); don't stop down further.

A gate without diffraction passes macros that look sharp in the render but that no real lens could deliver (measured:
macros at N_eff 41–55 summed 2.3–2.9 px while every rendered frame looked sharp). Nothing is added in the finish: the
gate keeps the settings to ones a real lens can deliver.

## 2b. Macro: depth of field, aperture units, mirrors, and diagnosing "too blurry"
**Depth of field is millimetres at high magnification:** total DoF ≈ 2·N·c·(1 + m)/m² (m = sensor width / frame width,
c = the acceptable blur on the sensor). Measured: a ~0.6× close-up at f/8 holds about 2 mm, so a subject whose named
points span a few millimetres (a front edge, a print behind it, a body behind that) goes soft with the focus "on it".
1. Name the points that must be sharp and their depths along the view axis (from the depth pass or the model).
2. **Stop down within the diffraction gate (§2) and move the focus plane to split the named depth** (the minimax point,
   not the nearest surface). `scripts/macro_focus.py` scans f-numbers and focus offsets with diffraction and prints the
   choice, the Blender values and the Octane aperture. If nothing passes, reframe a little wider or name fewer points;
   never stop down past the minimum.
3. **Check the engine's aperture units.** Blender takes an f-stop (use N(1 + m) with focal f(1 + m) so the real pupil
   f/N is kept); Octane's thin-lens aperture is the pupil **radius in cm** = f/(20·N) with f in mm (verified on the
   add-on used; re-verify on another version by rendering a defocused point and measuring the disc). A diameter in a
   radius field halves the depth of field.
4. **Mirror-like surfaces show a defocused reflection of what lies behind the camera.** A glossy black disc or panel in
   the foreground of a macro reflects the room; the reflected objects' virtual images sit far behind the focus plane, so
   they are soft at any aperture and read as a beige smear. Stopping down can't fix it. Choose the camera's azimuth and
   elevation so the mirror ray finds dark or cool surfaces, and **probe it with rays, not exposure:** a grid of rays over
   the mirror's screen region, reflected at the surface, with a histogram of what they hit and the mean Fresnel weight
   per object; pick the camera whose histogram is dark. This is also how a black finish stays black in a close-up.
5. **Diagnose "too blurry" by elimination, one variant per suspect** at the KEY in the final engine: motion blur off, the
   in-render denoiser vs a post denoise of the raw beauty, the aperture value read back from the engine, a stopped-down
   focus-split variant. Measure edge sharpness on a known print edge in each. Once measured: motion blur was not the
   cause; the depth of field and the in-render denoiser were; the soft foreground was a defocused reflection.

## 3. Gates per frame (the compositional analysis, with its numbers)
Every FIRST, KEY and LAST runs the full analysis in `composition-analysis.md`, with the same code as stage 7:
- the geometric pre-gate (§B: clearance ≥ 20 mm, no foreground occluder, the set hiding ≤ 12 % of the product, the
  subject's visibility ≥ 0.8, the hull padding, glass covers, 0 intersections);
- the frame gates G1–G9 and the dead zones (§C), G3 by the formula in §2 here;
- the composition items D1–D8 (§D: placement on an anchor or centred, eye path, divisions, space, masses, balance,
  size against its role's band, thumbnail), ranked, each † met or explained;
- the scene–subject harmony checks (§E: tone, rivals, colour, light, depth and scale, set);
- the shot rules (§G2) across each FIRST → KEY → LAST, and the cut rules (§G3) on every cut.

A fail is fixed here (§5) or carries the user's quoted acceptance (§1).

## 4. The independent audit (a fresh agent, never the builder)
The auditor runs the analysis itself (`comp_analysis.py frame` and `cuts`, `reads_metric.py`) on every frame and cut
and judges against `composition-analysis.md` §C–§G, so the checks are shared code, not prose. It writes an audit JSON
(frames, shots, cuts, counts) and marked act sheets, one report per act. Verdicts: pass / fix / replace /
cut_or_merge, each with the issue, a concrete fix (with its content direction, `shots-and-script.md` §7) and the
measurements.

**Frame checklist (where the faults hide; look here first):**
1. The subject sliced by the frame edge (a nick, not a bold crop), or a logotype cut through its letters (G2, G5).
2. Rivals: a prop brighter, sharper or more contrasty than the subject, especially cut by an edge (a patterned box, a
   pale surface, a bright bar behind the set) (G4, E2). Fix it with the camera, or move it plausibly like a
   photographer and log it; never hide a visible prop, and never remove a glass cover (`lighting.md` §6). Only objects
   no ray reaches over the whole move may be hidden.
3. A glass cover that doesn't read: the camera behind the product (azimuth > 100° off its front) or nothing bright on
   the cover's mirror ray. Re-angle to the front or three-quarter front.
4. Dead-black thirds and shapeless dark faces (the dead-zone gate).
5. Edges in the "almost" band: long edges 0.5–10° off level or plumb (a cover edge, a window pane) (G7).
6. Focus off the subject: on a surface behind the subject's visible face, or on a neighbouring part (G3).
7. The subject too small to win (≈ 0.1 % of the frame), or the colour accent not registering in the render (G1, E3).
8. Placement drifting near an anchor, or a dominant line on the 50 % line (D1, D3).
9. The key light's side flipping between neighbouring shots without an ellipsis (E4).
10. The spec's LAST not reached (the part meant to fill a third stays small).
11. Material traps in the light: black lacquer reads grey-beige in flat low sun around 15°; use a lower sun (≈ 5°) or
    a card.

**Shot checklist (motion):**
- The ends are the move's outcomes: FIRST and LAST computed from the chosen move, not posed separately (§1).
- The shot rules (`composition-analysis.md` §G2): explored or relayed; the subject moves ≤ 15 % W between frames or
  along a visible line; every 12th in-between keeps G5 and G6; focus targets unoccluded on every frame.
- Speeds against R5 (`greybox-animation.md`): push ≤ 10 %/s of the field (medium; 6 slow), arc ≤ 4°/s, truck and pan
  ≤ 6.5 % W/s, judder ceiling 14.3 % W/s at 24 fps. **First-draft moves typically run 2–5× over** because durations
  are set before move sizes. Set each move's size from its duration, or lengthen the shot to 8–10 s when the move is
  the story. Compute the speeds numerically before rendering the FKL.
- One change per shot: several changes in one short shot (a swing, an aim change, a push, an aperture ramp and a rack
  in ≈ 5 s) fails.
- Hacks: aperture ramps, lens changes mid-move, a LAST sized by fill fraction that hides a pull-out, a reversing zoom,
  a crane whip at the cut (a burst of > 10°/s in the first half second).

**Cut checklist (N LAST → N+1 FIRST; measured with `comp_analysis.py cuts`, definitions in `composition-analysis.md`
§G3):**
- eye jump ≤ ~25 % W (15–19 % is the limit when motivated); screen direction kept; the brightest region moves
  ≤ 50 % W unless the cut is a light cut;
- **no jump cut:** scale ≥ ×1.5 or angle ≥ 30°, or the cut is an act break on a light change;
- **pose continuity, numerically:** every mechanism's state in N's LAST (each hinge angle, each pivoting part's swing and
  lift, each rotor's state, which side of a two-sided part faces up) equals N+1's FIRST. An action is split at the cut and
  matched on action, never replayed across it;
- **a planned match cut shares its framing** (the same elevation, or plan views on both sides): the match breaks when
  one side leaves it;
- **a mechanism in motion at the cut:** the A shot ends where the B shot picks up. If A's LAST shows the part at rest at
  full travel while B's FIRST shows it still moving mid-travel, the part jumps back. Cut A mid-travel, at the value B
  enters on.

**Light checklist (every frame):** run `scripts/reads_metric.py <ids> --root=<shots dir>` (R7). R1 void share > 0.30
fails (warn > 0.20); R2 outline separation < 0.20 fails when the product is the frame's main shape (warn < 0.40); R3
subject is warn-only. Brightness doesn't separate reads from fails, so the fix is a light from the decision table
(`lighting.md` §5), never exposure. Low-sun and dusk frames fail most (measured: nearly half of a first pass, almost all
of them low sun and dusk), so their light is planned per state in the grey box, not rescued in the grade. **Every added
fill is physically plausible, measured:** a real surface lit by real light, its radiance in the scene-linear EXR ≤ ~1×
a sunlit white card (in sun) or ≤ ~3–4× the local shaded surface (in shade). An emitter posing as a diffuse object
fails (measured: 16–166× the local shaded surface).

**Notes checklist:** every user note is honoured in the frames it names; an ambiguous note was read explicitly and
confirmed with the user before the build.

**Exceptions checklist:** every frame that fails a gate carries the user's quoted acceptance (§1); none rests on an
agent's reason.

## 5. Fix, re-audit, check, hand on
1. The builder fixes by diagnosis and re-renders only the changed frames; the auditor re-checks those.
   - A KEY: one factor per variant (`composition-exploration.md`, repair by diagnosis).
   - A FIRST or LAST: the move's direction, rate or t_KEY (§1), re-checked at both ends and at the KEY.
2. **Main checks every shot itself** (1:1 crops of prints, the subject's focus, luminance ratios) and then declares
   "cameras final for Act X". A shot that can't be made strong within its own frames goes back to the composition
   loop (stage 7): a new comp, or the shot folded or moved.
3. **Before any engine time for that act:**
   - **The restore check.** Composition-time dressing must not leak into production. Diff the scene against each
     frame's dressing log: every logged move present, nothing else moved, no visible object hidden. Then re-run
     `comp_analysis.py frame` on the act's previews (props cut, kisses, tangents, rivals). Why: per-composition hides
     once leaked into the shot list, grew shot by shot, and were caught by the user only at the animatic, after
     sequences had started.
   - **The realism manifest, read back from the saved master** (`alive-environments.md` §10.4): every realism feature
     it records (displacement, edge units, bevels, glass layers) is on for finals, or off with the user's quoted
     agreement. Re-run the silhouette audit (`alive-environments.md` §10.3) and the hot-spot audit (`lighting.md` §6)
     on the FKL frames. Why: a fix the user approved was once switched off by the next harness and carried into the
     final engine's master, and the user found the straight edge again in the final week.
   - **Texture sizes from on-screen need**, now that the cameras are final. Per surface, the texels it needs = the
     pixels per metre it gets on screen at its largest over every frame ÷ its UV density. Keep a 2× margin: halve a map
     only when the halved size still holds twice the need; formats unchanged. A/B every changed map at 1:1 crops on the
     frames where its surface is largest. Measured once: −24 % texture memory per card, sampling time unchanged (it
     buys memory and start-up, not speed). Caps and the VRAM budget: `scene-optimisation.md` §2.
4. Only then the production engine's FKL for that act (`octane-production.md` §8, or `cycles-production.md`).
5. Show the user per act: FIRST | KEY | LAST sheets (clean and marked), the audit verdicts, the numbers that changed.

## Measure and gate
What stage 8 measures, how, and what passes:
| What | How | Pass |
|---|---|---|
| Composition, every FIRST, KEY and LAST | `comp_analysis.py frame` on the 960×540 preview + depth + index + camera + brief JSON; the pre-gate and §E4–E6 scene side (`composition-analysis.md`) | §B, §C and §E pass; every † in §D met or explained |
| Subject focus | G3: √(CoC² + (N_eff/24)²), median on the subject mask (§2) | ≤ 2 px at 1920 |
| Reads, every frame | `reads_metric.py` (`lighting.md` §5) | R1 void ≤ 0.30; R2 separation ≥ 0.20 when the product is the main shape |
| Added fills | radiance in the scene-linear EXR (§4, light checklist) | ≤ ~1× a sunlit white card in sun; ≤ ~3–4× the local shaded surface in shade |
| Shots | the shot rules (`composition-analysis.md` §G2) and speeds (§4) | explored or relayed; subject travel ≤ 15 % W; one dominant change; under the speed ceilings; every 12th in-between keeps G5 and G6 |
| Cuts | `comp_analysis.py cuts` on N LAST → N+1 FIRST | eye jump ≤ 25 % W; ≥ 30° or ≥ ×1.5; brightest region ≤ 50 % W; every mechanism state equal |
| Exceptions | the frame's record | each one quoted from the user |
| Dressing restore | the scene diffed against the dressing logs (§5) | 0 unlogged changes; 0 visible objects hidden |
| Realism manifest | read back from the saved master (§5) | every feature on, or off with the user's quoted agreement |
| Texture sizes | on-screen need per surface over every frame (§5) | ≥ 2× margin kept; 1:1 A/B shows no change |

**Gate.** The audit passes on every frame, shot and cut; main has checked every shot and declared the act's cameras
final; the restore check, the realism manifest and the texture sizes pass before the production engine's FKL.

**The user sees** per act: FIRST | KEY | LAST sheets, clean and annotated (the analysis tiles), each frame's
justification line, the audit verdicts, the numbers that changed since the last round, and every exception with the
user's quote.
