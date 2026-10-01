# Editing: shot length, cutting on motion, pacing, the review ladder

The author's rules for editing product films, and a procedure that applies them to any product. Related: `camera-motion.md` (how each shot moves), `transition-shots.md` (the shots that carry a light
change), `lighting.md` §9 (light tells time).

## 1 · The user's rules
- **Duration follows the visual information consumed.** A complex frame, or a motivated subject-to-subject move, may
  hold. A simple detail doesn't. Texture alone never earns length; motion and colour do.
- **Never cut between visually similar shots:** merge them, or drop one. "Similar" = view directions < 30° apart AND
  frame sizes < 1.5× apart.
- **Cut on the product's motion.** A part is moving, and the cut goes to another view that expands the understanding of
  that motion. A still shot with nothing motivating it kills momentum.
- **Every story beat must be legible.** A state that changes between two shots with no explanation (an object gone, a
  side turned, a cover shut) is a bug: show the change or imply it with a cut the audience can read.
- **No gratuitous shots.** No cutting between controls with no action: make each control act (a press → its effect).
- **No "magic" product animation.** Only the product's own mechanisms move on screen: its keys, hinges, arms, motors,
  lights. Anything a hand would do (placing, lifting, turning over, plugging in) is implied through a cut: show the
  before state, cut, show the after state. An object floating by itself reads as CG.
- **Length:** a product ritual film lands around 2 minutes; a first assembly usually runs 2–3× too long.

## 2 · Transferable pacing numbers (from a frame-by-frame analysis of a reference launch film)
Use them as starting values, then let the information in each frame move them.
- ASL about 4 s outside an opening mystery section; median about 3.5 s; minimum about 1.6 s; about 70 % of shots between
  2.3 and 4.7 s.
- Holds by shot type: single-surface detail ≈ 2.5 s; a mechanism stroke ≈ 3.8 s; journeys and reveals 5–9 s.
- About half the hard cuts carry motion on both sides. A still shot is a single pause of ≤ 2.5 s between moving shots,
  never two stills in a row.
- Blocks of fast cuts (about 20 per minute) separated by a longer reveal. The film **slows into its climax**; it doesn't
  speed up.
- On a same-size cut, change the subject and the angle by ≥ 30°. Spend big brightness jumps only at section turns.
  Hold colour back, then release it.
- At most three transitions that aren't straight cuts, all at act breaks: a fade up, a wipe by a real object filling
  the lens, a flash to black.

**Analysing a new reference film:** `/analyze-youtube`, then log every shot (in/out, type, subject, what moves, the
cut type into the next, mean luminance and chroma). Derive ASL, the median, holds per type, the share of motion cuts,
and where the film speeds up or slows. Those numbers, not taste, set the first cut plan.

## 3 · Cut points for constant-speed moves
- Enter moving, with the KEY 0.75–1.5 s in. Leave a push or crane before it arrives. Leave a reveal about 1 s after the
  whole subject reads.
- Mechanisms:
  - enter 0.5–1 s before the cause;
  - a match on action enters in the first third of the action;
  - cut at rest ≥ 1 s after the stop, only to end a phrase.
- **Bring an event sooner by trimming the in point**, not by re-animating: if a mechanism starts too late after the cut,
  move the in point later by the wait (typically 0.5–1 s). The out point and the rest of the edit stay; recompute the
  runtime and the neighbours' cut logic.
- **Let a landing land:** hold about a quarter second after a part comes to rest before cutting (the author: "were
  cutting too soon"); cutting on the impact frame reads as cut too soon.
- The emotional beat gets one extra breath.
- Light-state changes belong on ellipsis cuts, never in the middle of continuous action (`lighting.md` §9).

## 4 · Mechanism channels make cuts motivated
Lay the product's mechanism chain end to end (e.g. open → press → spin up → run → stop → reset → close) and build the
edit around its **cause → effect** cuts: a key goes down, cut to the light coming on or the motor spinning up. If a
cause has no animated effect, add it as a product channel (a key depth, an indicator's emission, a motor's rpm with a
physical spin-up) rather than cheating with a cut. Physics holds across cuts: parts move only when the mechanism
allows (nothing lifts while a motor runs; a moving part clears every other part: collision-check it).

## 5 · Procedure: inventory → plan → paper edit → build → assemble
1. **Inventory:**
   - per shot, the product's motion events in shot time;
   - the motion windows, measured as the moving part's px/frame through the camera;
   - the similarity of every shot pair (view angle, size ratio, SSIM);
   - the story clock: what state (every mechanism, every indicator, the light) is each shot in?
2. **The cut plan as a table:** per shot, the source, the idea, the duration, the in → out logic, the cut type into the
   next. Durations are starting values set by information; measured motion moves them. List what is dropped and why
   (the files stay).
3. **Paper edit first** from existing playblast frames, with grey slates for shots still to be built. Check the runtime
   and the similarity of every adjacent pair before rendering anything new.
4. **Build the new and re-timed shots** under the simple-move rules (`camera-motion.md` §0), with 24 f of handle each
   side.
5. **Assemble frame-accurately** from a cut list (JSON). Gate:
   - ≤ target runtime, no shot < 1.6 s;
   - no adjacent pair too similar;
   - no two stills in a row;
   - every motion cut has the part visibly moving on the out side and the in side, or cuts ≤ 1 s after a stop;
   - mechanism and light-state continuity at every cut, with the ellipses declared.
6. **Review:** the edit with burn-ins (edit number, source, cut type, edit time, light state, the moving part's
   px/frame), ±1 s clips around every cut, and a sheet of the frames either side of every cut.

**Removing a shot re-gates its neighbours.** The two shots that now meet must pass the similarity, stills-in-a-row,
motion-cut and continuity gates; the light schedule re-maps to the new edit times; every later shot's timing shifts.
Renumber in a new edit version (never in place) and keep a map from old to new numbers.

**Changing an approved shot: version up, change only what the note targets.** When a note asks for a new angle, a
timing or a light on a shot that otherwise works, open the file that produced the approved result, save a new version,
and change only the parameters the note names; everything else (lights, materials, light state, grade, render
settings) is inherited. First prove the starting point reproduces the approved frame (a pixel diff of a re-render
against the approved frame), so any later difference is the change. Pick the shortest path that satisfies every
requirement and keeps continuity where continuity is wanted. Why: a replacement rebuilt through a new prep path came
back warmer, softer and off its neighbours; the author: "we shouldn't redo the entire scene, we should version up and
make the change that most likely leads to continuity". Brief agents the same way: the file to version up and the only
parameters they may touch.

**Follow the user's picks.** When the user arranges candidates on a board (a strip, a slot), build exactly that
arrangement; ask before producing parallel variants they didn't request.

## 6 · Insert slots are defined before anything is built
When the edit needs a new shot between two existing ones (a transition, an establishing beat), write the slot as data
first:
- its place (after which shot), its duration (a transition ≈ 2.5–3 s), and why it is there;
- **the neighbours at the cut:** each one's view direction, elevation and frame width at the subject, whether its
  camera moves and what part moves;
- **the light it carries:** the state before, the state after, or the step between (`lighting.md` §9);
- **the similarity rule:** view direction ≥ 30° from each neighbour at the cut, or a frame width ≥ 1.5× different;
- **motion:** if either neighbour is a still shot, the insert must move (no two stills in a row);
- the continuity it must respect (the story state at that moment).

A builder then searches compositions against that spec (`transition-shots.md` §3), and the paper edit carries a grey
slate naming the slot until the shot exists.

## 7 · The review ladder (what the user sees, cheapest first)
Each rung is a full pass of the film; move up only when the rung below is approved.
1. **Grey playblast** of every shot at 24 fps (`camera-motion.md` §4): motion and flow.
2. **FKL animatic** in the final engine: three lit frames per shot held at edit pacing: FIRST until the F–K midpoint,
   KEY until the K–L midpoint, LAST to the out point. Burn in the edit number and the light state. It judges light,
   composition and the light schedule across the whole film for about 3 renders per shot.
3. **Low-rate lit animatics:** every 6th frame (4 fps), then every 4th (6 fps), each a true 24 fps frame with correct
   motion blur (render F−1/F+1 or keep the pack contiguous and subsample only the render list). They judge motion in the
   real light before a full-rate render.
4. **Full rate**, per act, after the user's explicit go (`SKILL.md` stage 11).
- **Spot-check before every full pass:** after any light, material or camera change, render the few KEY frames it
  touches (a before/after sheet with the numbers), approve them, then run the pass. A pass re-rendered for one wrong
  value costs hours.
- **Budget the pass from measured ratios, not guesses** (measured on a 4-GPU Octane node at 1080p): a light path-trace
  preview at 64 spp costs ≈ 1/10 of the 512 spp animatic setting (≈ 1 s vs 10–14 s per frame); a Direct Light kernel at
  the same spp is no faster than light PT; each shot switch in a kept-alive session ≈ 25 s; a session start ≈ 100 s.
  So a 500-frame 6 fps animatic is ≈ 2 h of node time, and a 75-frame FKL animatic ≈ 25 min.
- Keep every rung's outputs under new tags; lower rungs never overwrite full-rate renders.

## 8 · Traps
- Details shown *before* a cause (a press) must show the effect's "before" state (motor stopped, indicator off, parts at
  rest), or the press explains nothing. Re-render them in that state; keep the cameras.
- An upward crane started earlier gets *lower*: it can't reach a higher neighbour's view legally. Merge by starting the
  move earlier, or reverse it (check the direction still matches the next shot).
- A rotationally symmetric part doesn't show spin in grey clay. The spin reads only in lit frames.
- A moving part lifted over or past another (a cover, an arm) collides: solve the path clear first.
- A similarity check on thumbnails misses same-angle pairs at different sizes; use the view-direction and size rule.
