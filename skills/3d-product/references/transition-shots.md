# Transition shots: time-of-day markers, and reflections that tell the story

Short abstract shots placed at the film's lighting transitions. They make the change of light legible through what the
product reflects, so they double as the "establishing" shots for each new time of day (the author: the establishing shots
and the interstitials "are the same thing, they serve to show the lighting transitions"). The product becomes the
screen on which time passes.

Related: `lighting.md` §6 (reflections and flags) and §9 (light tells time), `editing.md` §6 (insert slots),
`camera-motion.md` §0 (simple moves), `composition-exploration.md` (the general composition search).

## 1 · Where and how many
- **One per lighting transition, 3–4 in a 2-minute film**, about 2.5–3 s each. More reads as padding.
- Each slot is defined as data before any search (`editing.md` §6): its neighbours at the cut, the light state it
  carries (the new state, or the step between two), the similarity rule, whether it must move, and the story state.
- It carries the **new** state when it opens a phase (the first frame the audience sees in that light), or the
  midpoint when it bridges two. In the grade it is a stepping stone on the colour path (`finishing.md` §4).

## 2 · Rules
- **Search earlier work first:** stamped compositions, unused frames and old options. Build new only if nothing fits.
- **Compose in grey, light only the KEY.** The composition is judged in grey; each option's KEY is then lit in its
  slot's state in the final engine. Nothing else is rendered until the user picks.
- **Present many options, in rounds** (e.g. 10, then 15, then 15 with a new idea each round), with a one-line idea per
  option. The user chooses; all options are kept.
- **Vary the angles:** oblique, low, high, grazing, from the side and from behind the reflector. Never face-on and
  symmetrical (keep ≥ 12° off any face's normal).
- **No roll. Simple moves** (`camera-motion.md` §0): static, or one constant generator that slides the reflection
  across the surface. **A slot next to a still shot must move** (no two stills in a row).
- **The product keeps its story state** (§7). Covers and glass are never removed to clean a frame; the camera changes
  instead.
- The grey renderer can't show transmission or reflection in transparent parts: judge those on the lit KEYs, not the
  grey sheet.

## 3 · The physics that makes a reflection read
- **Fresnel: graze.** A dielectric (n ≈ 1.5: glass, acrylic, lacquer, vinyl) reflects about 4 % face-on and barely more
  until grazing: 9 % at 30° above the surface, 17 % at 20°, 25 % at 15°, 39 % at 10°, 61 % at 5°. Cameras 2–15° above
  the reflecting plane get 5–15× the face-on reflection.
- **Something bright must sit on the mirror ray.** Reflect the camera ray about the surface normal: it must land on the
  window, the sky, a lamp or a lit wall. A dark or tinted transparent surface with nothing bright to mirror simply
  vanishes on screen.
- **Dark behind the reflector.** Reflection competes with what is seen through (or beneath) the surface. Tinted glass,
  black gloss and dark vinyl mirror best; **dusk and night turn tinted glass into a dark mirror** where a lamp or a
  lit window reads as a sharp image.
- **Flat beats tilted.** A flat surface seen at a grazing angle across its whole length (a closed cover, a top) mirrors
  the room far more than a raised or tilted panel, which mostly transmits toward the camera. Measured once on a smoked
  acrylic cover: the reflection's share of the cover's light was 0.16 raised vs 0.64 closed (≈ 4×).
- **Thick edges and corners catch light:** chamfers, corners and the edge of a thick transparent sheet pipe light along
  themselves; a bright line on an edge draws the object in the dark.
- **Black gloss is a time display:** it mirrors the window by day and the lamp at night, so the same frame shows the
  time of day by what appears in it.
- **Two-layer frames:** through a transparent reflector, the detail beneath (what) with the reflection laid on top
  (when). One frame carries both the product and the time.
- **Reflections move at known rates:** a camera arc slides a reflection across a flat surface; a rotating reflector
  sweeps its reflection at 2× its own angle. A slow arc or truck is usually the only move these shots need.

## 4 · The search: sample, score, pick by eye
1. **Subjects:** points on the reflector (centre, top edge, corners, side edges, the part beneath it) in the product's
   local coordinates.
2. **Sample ~200 random cameras per round:** a random subject; azimuth ≥ 12° off the face normal on either side, out to
   behind the reflector; elevation **weighted to grazing** (about two thirds at 1.5–14°, one third at 14–70°); frame
   width log-uniform; lenses from a real set (50–135 mm); the subject placed within the middle 30 % of the frame.
3. **Reject** views where a ray from the subject to the lens hits anything other than the reflector, and cameras inside
   geometry.
4. **Quick-light each survivor in its slot's light state:** 320×180, 16 spp + denoise, with the glossy (direct +
   indirect) × colour, transmission (direct + indirect) × colour and object-index passes.
5. **Score on the reflector's mask:**
   - frac = the reflector's share of the frame;
   - share = glossy / (glossy + transmission) (how much of its light is reflection);
   - struct = std of log(1 + 50·glossy) inside the mask (a flat sheen scores low);
   - rel = mean glossy / mean frame (the reflection's weight against everything else);
   - score = √min(frac, 0.6) · share · (0.4 + struct) · min(rel, 2).
6. **A contact sheet per slot** of the top 30–40 with their numbers. Run the composition analysis on each candidate
   (`composition-analysis.md`) and the cut checks against both neighbours' cut frames
   (`scripts/comp_analysis.py cuts`); print the results on the sheet. The score and the analysis find candidates;
   **pick by eye**, for an idea you can say in one line.
7. **Write the options as data** (id, slot, subject, camera az/el/W/f/N/placement, the one-line idea, the move) and hand
   them to the final-engine agent as a JSON with each KEY's world camera.
8. Show the grey option sheet, then the lit KEY sheet. ★ The user picks; the picks are re-lit in their exact slot
   states and their moves built and gated like any shot.

## 5 · Families: one frame, several times of day
The strongest option is often a **family**: the same camera at 2–4 slots, lit in each slot's state. Cut into the film
at intervals, it shows time passing directly (a time-lapse motif, like a clock shot), and each member reads at once
because the audience already knows the frame. Rules: never adjacent to a similar shot, spaced across the film; the
product's state may differ between members only as the story allows (§7). Families of a flat reflector (grazing the
top), of a two-layer frame and of a black-gloss mirror all worked.

## 6 · The light switches on in shot
The motivated moment when practicals first come on can be a transition shot itself: **the product in front, the
practical behind it, switching on during the shot.** It replaces an off-screen ellipsis with an on-screen event.
- Composition search by projected geometry: the lamp (shade and bulb) in frame and at least ~0.3 m behind the product;
  the lamp near a third line; the product's signature parts in frame; the window in frame if it is the clock.
  Candidate styles: a product detail in the foreground with the lamp soft behind; the lamp just above the product's
  edge; a wider frame with the window.
- The switch-on is a light event, so the camera is static or a very slow single move, and it happens at a readable
  moment (≥ 1 s in).
- Build variants for each product state the story might need at that moment (e.g. a cover open and closed).
- After it, every shot is in the lamps-on state; before it, none are.

## 7 · Continuity against the story state
A transition shot is still inside the story: its product state (cover angle, mechanism positions, indicators, what is
on the product) must equal the story's state at that edit time, checked numerically against the neighbours' LAST and
FIRST. A strong frame in the wrong state (e.g. a closed cover while the story has it open) breaks the story unless one
of these is true:
1. the slot moves to a moment where that state holds (before the product opens, after it closes);
2. the story changes so the state holds there (the product operates in that state, and the change to it is shown or
   implied by an ellipsis earlier);
3. the state change itself becomes a beat (shown on a mechanism, or implied by a cut the audience can read);
4. otherwise, choose a different family whose state matches.
Write which one applies next to the option; never ship a transition that silently contradicts its neighbours.

## 8 · Measure, gate and show
- Gate, measured from the cameras and the story data and printed per slot:
  - the similarity rule against both neighbours at the cut (view directions ≥ 30° apart, or frame widths ≥ 1.5×
    apart; `scripts/motion_qa.py cuts`);
  - it moves if a neighbour is still; no roll; a simple move under its speed ceiling (`camera-motion.md` §7);
  - the story state equal to the neighbours' at that edit time (§7);
  - the composition analysis passes on its FIRST, KEY, LAST and cut frames (`composition-analysis.md`);
  - its lit KEY shows the slot's light state through a reflection the user can name (the score's share and rel terms
    reported).
- Once placed, a transition is a shot like any other: the stage-9 re-gate covers it after any cut change
  (`camera-motion.md` §7).
- Show: per round, the grey option sheet (with ideas), then the lit KEY sheet; after the pick, the KEY strip of the
  whole film with the transitions in place (`finishing.md` §4).
