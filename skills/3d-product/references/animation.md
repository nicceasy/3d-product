# Animation, timing & the teaser film

What a 15-second product teaser (8 shots plus an end card on a 96 BPM grid) proved about turning storyboard frames into
a film. The rules hold for any short product film; longer films add `editing.md` and `camera-motion.md`.

**Motion is a render element.** Easing, camera moves, cuts, light over time and sound each claim something about
the product, just as light and material do. A spring says there is a detent under your thumb. A linear slide
says a machine is moving the camera. A studio light that dies as the object lights itself says *the product is the
light*.

Contents:
1. Pipeline
2. Pacing
3. Keyframes → shots
4. Easing
5. Camera realism in motion
6. Light over time
7. Sound
8. The animation spec
9. Costs
10. Traps

---

## 1 · The teaser pipeline (what worked, in order)
1. **Three research tracks in parallel:** ID and style, reveal-film pacing, and animation and timing. Agents fetch
   text sources, not media; they tag each claim with its evidence level. References go on the board as links;
   reference images are for private use only.
2. **Spec + physics check before modelling.** Research specs can fail physics: a light source placed in a part that
   moves away from its power, a lens whose focal length can't be made at that diameter. Fix them on paper (move the
   source to a fixed part, change the optic) before any geometry exists.
3. **Model with named parts that match the animation's moving groups**, and build the product's states as flags
   (open/closed, on/off), so the stills and the animation share one source.
4. **Plan the shots on a music grid first**, as a table: beat, board frame, change A → B, and the rule at each end (§3).
   A short film cut to a beat is music-first like this. A longer film timed by its mechanisms is picture-first, with
   the music map and a temp track laid at the animatic (`sound-design.md` §0).
5. **Look-dev stills per shot at both keyframes** (960×540, 64 spp). Fix light, exposure and framing here; it's 10×
   cheaper than in motion.
6. **Animatic** (640×360, 16 spp, all frames; measured ≈ 3 min for 15 s on a laptop GPU) → cut with the score →
   review a filmstrip (a frame every 0.5 s) and a camera-speed timeline.
7. **Finals.** 1920×1080 at 64–128 spp, per-shot spp, 180° shutter, one render sequence per shot. Then edit into an
   H.264 BT.709 file plus HEVC 10-bit with film grain 0.006.
8. **Board + write-up + skill.**

## 2 · Pacing (15 s = 360 f at 24 fps)
- **8 shots + end card:** 2.5 / 1.25 / 1.25 / 1.25 / 0.625 / 0.625 / 2.5 / 2.5 (hero), then a 2.5 s card. The shape
  is long–short–short–short–flurry–long–long.
  - 6–8 shots is the persuasion peak for ads; premium films cut less.
  - Apple's event teasers run 14–16 s.
- **96 BPM** gives 15 f per beat and 6 bars in exactly 15 s. Every cut lands on a bar, half-bar or beat, and every
  sound cue lands on a film frame.
- **Where things land** (fractions of a 15 s teaser):

  | Time | Beat |
  |---|---|
  | 0 s | brand cue: a light line on black |
  | ⅓ (5.0 s) | first full silhouette |
  | ½ (7.5 s) | the act (the mechanism doing its thing) |
  | ⅔ (10.0 s) | hero on the drop |
  | ⅚ (12.5 s) | end card; tagline one beat later |
- **Light escalates in five steps:** edge line → rim with a first warm hint → the device's own light → full reveal →
  calm, product-lit.

## 3 · Keyframes → shots: the rules
- **Which end is the storyboard frame?**
  - A shot that *arrives* at its idea (a settle, a reveal, a light-wipe, a glint reaching a mark) keeps the board frame
    at its **END**.
  - A shot that *departs* from an idea (something about to change: a click, a pulse, a twist) keeps it at its **START**.
  - Generate the other frame by stating the one nameable change A → B. (In a longer film, the move is chosen so that
    FIRST, KEY and LAST are each a strong composition: `fkl-frames.md` §1.)
- **The boundary-velocity rule.** A keyframe the viewer sees settle has zero velocity; a cut point keeps moving.
  - Author each end's slope as a multiple of the average speed (`slopes [v_start, v_end]`).
  - Exit fast into a cut (`accel`) and enter the next shot moving (`slopes(1.5, 0)` arrives at 1.5× and lands at 0),
    not with a land-from-rest ease, which stalls the cut.
- **Continuity across a cut:**
  - When the same subject appears at a similar size, change the angle by ≥ 30°, or it's a jump cut (a 6° change reads
    as a jump; 40° doesn't).
  - Keep the direction of travel (az increasing stays increasing), because a reversal reads as a jolt.
- **Staging:** lock the camera while the object moves; move the camera while the object is still. Give each shot one
  idea.
- **Keep the object fixed and sweep the light.** On a still macro, a moving light is the motion (a glint travelling
  round a chamfer).
- **Avoid two similar shots in one film.** Two oblique views of the same part two shots apart read as a repeat: turn
  one into something else (e.g. a top-down axial push).

## 4 · Easing: the family used
| Ease | Curve | Use | Says |
|---|---|---|---|
| `moco` | bezier(0.25, 0, 0.75, 1), peak 1.33× average | default camera move, light ramps | an expensive rig, no judder |
| `cut_cut` / linear | constant | moves seen only in the middle (start and stop off-screen), light sweeps, rotating display stands | a machine is moving the camera |
| `enter_settle` | (⅓, ⅓, ⅔, 1) | arrives moving, lands on the board frame | "here it is" |
| `accel` | (0.5, 0, 0.9, 0.6) | into the drop / hard cut | momentum |
| `slopes(1.5, 0)` | entry at 1.5×, lands at 0 | the shot after an accelerating cut | inherits the momentum, then rests |
| `part` | (0.45, 0, 0.55, 1) | mechanisms (twist, lift) | mass on a guide |
| spring | ζ 0.6, response 0.45 of the segment | a detent's last few percent | a detent under your thumb |
| `out_cubic` | (0.33, 1, 0.68, 1) | light pulses decaying, titles | energy leaving |

- Cameras never get easeInOutCubic or quint: their peaks of 2.9–5.9× average judder at 24 fps.
- Springs are only for the last few percent: bezier to the detent, then a spring (9.5 % overshoot, settles in 3–4 f).
- Moving holds: after the hero lands, keep a 1–2 % dolly so the frame reads as film, not a still.
- For longer films the camera rule is constant speed with cuts mid-move (`camera-motion.md` §0); these eases stay for
  mechanisms, light and teaser grammar. The one camera exception is the ease budget (a start or a stop the viewer
  sees: an opener from a hold, the final settle, a move seen whole), and its profile is `moco`.

## 5 · Camera realism in motion (the biggest single fix)
- **Camera paths and motion review live in `camera-motion.md`:** one rig with one progress and one aim, never
  per-axis keys; review every shot as a grey playblast with a speed strip, then the edit.
- **The frame is 36 × 20.25 mm on 16:9** (sensor fit AUTO keeps the width), not 36 × 24. Vertical field =
  20.25·dist/focal. Assuming 36 × 24 crops the top and bottom of every framing.
- **Macro:**
  - Put the camera at the real working distance: about 330 mm for a 100 mm macro at 1:2.
  - Choose **focal = 36·dist/field width**.
  - Set the blur from the real entrance pupil: **f-number = focal / pupil** (100 mm f/4 → 25 mm pupil).
  - A long focal at a short distance ("100 mm at 110 mm") gives wide-angle perspective and a blur far larger than any
    real macro makes. At the real working distance the plane of focus is about ±0.5 mm and slides along the surface,
    and the frame looks photographed.
- **Focus on the surface, not the target:** `focus_dist_mm = dist − radius` for an orbit about an axis.
- **Keep the shutter at 0.5** (180°), with 0.25 for flash shots. Measured: motion blur costs only +3–11 % on a laptop
  GPU.

## 6 · Light over time: techniques that carried the story
| Technique | How (spec) | Expresses |
|---|---|---|
| **Glint travelling round a chamfer** | a small source crossing overhead (light `loc_mm` keys, linear) while the camera arcs. The glint sits where the ring normal bisects camera and light, so a source at tangent offset t slides the glint by ~t/400 rad. Add a big dim overhead card so the whole ring reads as a line | a precise machined edge |
| **Kicker that rides with the camera** | key the light's position on the same azimuth as the camera, so its reflection stays put in frame | a constant accent without a crawling band |
| **Light-wipe cut** | the emitter ramps to a very high strength (≈ 3000) over the last 4 f (`ease: in`) and the cut hides inside the white | wake-up, energy |
| **Flux-conserving zoom beam** | key `flux_W` on a spot: power = flux·4π/Ω(cone). A narrow spot is far more intense than a wide flood at the same flux (8° vs 50°: 38×), so the beam widens *and dims* | a real optic (fixed power widens the beam *and brightens* it, which is wrong) |
| **Beam → glow handover** | when one of the product's lights gives way to another, ramp the first's flux to 0 as the mechanism moves while the second (a glow, an internal warm point light) ramps with `moco`; haze glows around it (mesh emitters scatter in volumes) | one light becomes another |
| **The studio falls away** | at the end card, key and backdrop go to 10–25 % and the product's own light stays | the product is the light |
| **Product-only light** | `"link": "product"` on a light gives Cycles light linking to a collection of the model's parts. Rims then never paint the floor | a flag/cutter, done in software |
| **Environment as rim** | a huge dim gradient card ≈ 20 m behind, *above the frame*: it arrives only as reflection in a glossy floor and as rim on metal | place and time of day without a CG sky wall |
| **Light-guide fall-off** | glow `falloff` k: emission × (floor + (1−floor)·e^(−k·z)) along generated Z | a light guide fed from one end |

## 7 · Sound (a synthesized temp score; a film's real sound: `sound-design.md`)
- Sine partials, filtered noise and one pad; no drums. The pad resolves (e.g. open fifths → a major chord) at the
  product's payoff.
- A sub bloom on the drop, and bells on the title and tagline.
- Every cue sits on a film frame: a detent click on the spring snap, a ping on a light pulse, an inhale into the
  light-wipe.
- Check it by spectrogram plus RMS per bar: the drop bar should be clearly the loudest (measured: ≈ 4–20× the others).
- It's a temp track to cut against. Replace it with a composed score before anything leaves the studio.

## 8 · The animation spec (`spec["anim"]`, read by the pipeline's animation library inside Blender)
- `camera` keys: target_abs_mm, az, el, dist_mm, lens, fstop, focus_mm | focus_dist_mm, roll.
- `parts`: loc_mm and rot_deg about the part centre.
- `lights[i]`: energy_W | **flux_W**, color, spot_deg, loc_mm + target_mm.
- `emission`: a part or any scene object (e.g. a card).
- Also: `motion_blur`, `range`, `step`.
- Eases can be a name (§4), a bezier list, `{"spring": {...}}` or `{"slopes": [v0, v1]}`.
- Keys are written per frame as LINEAR, so Blender's own interpolation never adds a second ease.
- Useful helpers in a shot script: place lights relative to the camera azimuth (a ring at az, r, z, t); lens from
  field and distance. An edit script writes the EDL and renders cuts, fades, grain and titles to H.264 BT.709 and HEVC
  10-bit plus a contact sheet.

## 9 · Costs (measured once on a laptop-class GPU, Cycles Metal, 1920×1080)
- Metal macro at 128 spp: about 12 s/frame. Dark hero with a floor at 96 spp: about 6.7 s/frame. Haze beam at
  128 spp: about 16 s/frame.
- A whole 15 s teaser: about 1 h. The preview animatic: about 3 min (≈ 1/20 of the finals).
- Denoiser blotching shows in dark bead-blasted metal at 64 spp, so macros get 128.

## 10 · Traps (teaser)
- The frame is 36 × 20.25 mm on 16:9 (see §5).
- A gradient emissive material with its Strength socket linked ignores Strength keyframes: scale Color instead.
- Tiny sources have huge radiance: a thin, very low-wattage strip grazing rough metal is still a wide band. Judge the
  band, not the watts.
- A glossy floor behind a back-lit product is a sheen band, so shoot macros in a void (`background: none`).
- AR-coated glass reflects about 1 %, so cards must be 8–14× brighter than for bare glass.
- A backdrop card near the camera is seen by the frame's top rays before they reach the floor. Push it far (≈ 20 m)
  and widen it.
- Blender spot power is per 4π sr (see `flux_W`).
- A camera `el` near 90 is degenerate for to_track_quat, so top-down is el 85 (or use a construction with no look-at,
  `camera-motion.md` §0).
- Write the shot script *before* launching a background run: a silently failed write leaves the old script rendering
  the wrong mode at full resolution.
