# Intention, shots and script: written together with the compositions

Where this sits in the pipeline (the author: "overall intention should be first, composition shots and script should go
hand in hand"): the **intention** is stage 1, written before modelling (§0); the **shot list and script** are written in
stage 7 in one loop with the compositions (§5) until the user locks the list; the **edit and the script are finalised
at the animatic** (stage 9). The script is the source of truth: when a shot changes, fix the text first, then the data.

## 0. The intention comes first (stage 1)
Before any model or composition, write what the film is for and what it says: the audience and channel, the claim in
one sentence (the product's nature said as a film), the feeling it should leave, how it ends, what it must never imply;
then the story seed (format, logline, one line per act, target length), the light arc and the feature table. It opens
the shot list, and every composition and shot is judged against it: a shot that can't say how it serves the intention
is folded or cut from the film (its files stay).

### The feature table (the stage-1 gate, measured)
One row per feature: the product's signature functions and unique elements, from the research.
| Feature | Poses and product states that show it | What the model must carry | Shot ideas |
|---|---|---|---|
| one row each | each mechanism's state, each switch, each lit or unlit state | the pose, the switch, the clearance; whether the sources support it, or a named model gap | the beats that could carry it |

1. **Mark the one function only this product has.** It is the story's hinge.
2. **Every implied state gets a model state** (empty and loaded, open and shut, off and lit). The film shows no hand
   action as magic, so a state the story implies but never shows changing must still exist in the model.
3. **Every feature has a pose the model will support, or a named model gap keyed to the shots it would expose.** Gaps
   become stage-2 work items; stage 2 proves each pose (a clay pose rendered, clearances checked). Unresolved source
   conflicts from stage 0 join the gap list.
4. **Target length = planned shots × the format's average shot length** (the measured numbers in §4 and `editing.md`
   §2), not a number picked first.

**Gate.** The table is complete as above; the intention still fits a short paragraph (what for, what it says, how it
ends); ★ the user approves or redirects.
Why: a feature list without poses and model support lets a story promise a state the model can't show, and the gap is
found at the shot that needs it.

## 1. Where the shots come from (the inclusion rule)
Build the list from four sources and cross-reference every one of them in a table at the end of the spec:
1. shots the user marked **good** in a review;
2. shots the user left **notes** on (every note is a hard requirement, quoted verbatim in the shot);
3. the **stamped compositions** from the composition board (the thumbs-up comps become KEYs; FIRST and LAST come from
   the move chosen for each, §5);
4. shots with **no note**: kept. No note means undecided, not rejected (the author: "err on the side of keeping extra
   shots").
Only shots the user explicitly scrapped stay out, and their files stay on disk. Never delete shot files.

## 2. The story (drafted at stage 1, finished in the stage-7 loop)
Write these at the top of the spec, under the intention:
- **Logline** (3–5 sentences): one situation, one time span, a beginning and an end the viewer can feel.
- **Why this story:** read the user's picks and name the two or three things they lean toward (e.g. the whole object
  as a graphic; light as the subject). The story must give every pick a reason to be there.
- **Light arc:** one named light state per shot, advancing with the acts (`lighting.md` §3, §9). At most one shot shows
  light changing on screen (a deliberate time-lapse); everywhere else time moves between cuts.
- **Arc of scale:** parts → whole, paced so the whole object gets bigger as the film deepens. Component-only films read
  as repetitive; the user asks to see more of the product.
- **Rhymes:** alternate the product's shape families (e.g. circles: dials, discs, knobs; lines: edges, arms, shadows).
- **Bookends:** the first and last images answer each other (the same object in two lights; one indicator colour
  answered by another; a view through a cover answered by the cover closing).
- **Match cuts, named in advance:** a mechanism carried across two shots, a shape repeated across a cut (e.g. a circle
  in plan on both sides), a move continued across a cut (e.g. an axial pull-out). Each is designed as one motion on one
  clock (`greybox-animation.md`).
- **Acts table:** act, name, shots, light, duration.

Formats (R4 research): a **reveal** withholds the whole object (median arrival at 86.5 % of the runtime, then a 2.3–9 s
hold and a 3–9 % end card); a **demo** shows it working; a **ritual film** follows one use over one span of time. The
user has preferred the ritual shape: the object shown early, light marking time, bookends, ending on the product at
rest and the name.

## 3. Each shot, in the spec
| Field | Content |
|---|---|
| Title + sources | `NN · name (its sources: an earlier round's shot · a comp id · the user's note verbatim)` |
| **Story** | "from X to Y": one change the viewer can name (from the room to the object; from one part to the next) |
| Why | why this subject, and what the user's note or pick asked for |
| **FIRST / KEY / LAST** | the KEY: the stamped comp it is (cited); FIRST and LAST: the ends of the chosen move; each described as a composition with a nameable subject and its analysis (`composition-analysis.md`) |
| Motion | the move chosen in the lock-in (`greybox-composition.md`): generator, direction, size (push ×1.6, arc 30°, crane 45°, truck 90 mm), t_KEY, real lens and f-number, duration; what the product does |
| Light | the state, plus any flag or card the shot needs |
| Sound | what is heard: the music's state (playing, stopping, absent), the bed, the product's events; it seeds the spotting sheet (`sound-design.md` §2) |

Rules:
- **The product is alive in every shot** unless the story says otherwise: its motors run, its moving parts do their
  job, its indicators are lit.
- **One change per shot** (subject explored, or relayed from A to B along a line or motion the viewer can follow;
  the numbers in `composition-analysis.md` §G2).
- **Honour notes literally** ("keep the front button in focus" means no rack away from it; "the final frame should show
  the buttons at bottom right" means the LAST frame puts them there).
- **An ambiguous note gets an explicit reading, confirmed with the user before it is built.** "Way too much DOF" can
  mean too shallow or too deep: ask, don't guess.
- **Never replay an action across a cut.** When a mechanism spans two shots, split the action at the cut and match on
  action: every mechanism's state in shot N's LAST equals shot N+1's FIRST, checked numerically (`fkl-frames.md` §4).
- **A planned match cut shares its framing:** the same elevation, or a plan view on both sides. Check it on the FKL
  frames before rendering anything else.
- **No jump cuts** (the same view and field a few degrees apart): change scale by ≥ ×1.5 or the angle by ≥ 30°, or
  make the cut an act break on a light change.
- **Plan the light of dusk and low-light acts in the spec** (motivated lamps as the key, rim and fill). Unplanned, they
  crush: a first pass lost nearly every frame after sunset (product L* medians in single digits).

## 4. Pacing (R6)
Superseded at the edit by `editing.md` (the author's notes: holds by information, ASL ≈ 4 s, details ≈ 2.5 s, minimum
≈ 1.6 s, about 2 min). These are shot-list planning lengths with handles, not the final cut.
- ASL about 4.3–4.4 s (contemporary features 4.3 s). Clarity floor 90 f (3.75 s): 18 f to orient + 24 f to read A +
  ≥ 24 f of change + 24 f to read B. ECU/CU 90 f, act openers 120 f, MS 150–180 f, the hero 240 f.
- Each act opens on its longest shot; the climax lengthens.
- Hard cuts on the beat (a cut reads on the beat from 3 f before to 1 f after it); dips to black at most twice (before
  the reveal act, into the card); no whips, ramps or dissolves inside acts.
- One sun path for the whole film (a film that moves through the day follows `lighting.md` §9); the brightest large
  region may not jump more than 50 % W across a cut unless the cut is a light cut.
- Orientation: stay in the front hemisphere once the layout of the product's controls matters; cross the line only in
  abstract openers or at act boundaries.
- Budgets that worked: a 15 s teaser = 8 shots + card on a 96 BPM grid (`animation.md`); 60 s = 13 shots + card at
  80 BPM; a 3:30 film = about 40 shots in 7 acts.

## 5. The loop with the compositions (stage 7)
Comps, shots and script inform each other; run them as one loop. Compositions come before motion (the author:
"composition and first key last frames should happen before motion"):
1. **The intention and the story draft decide what to explore:** the beats, subjects, light states and poses the story
   needs, read against the product's vocabulary and the set's traps → the archetypes to sample
   (`composition-exploration.md`).
2. **Stand-alone compositions first**, each analysed (`composition-analysis.md`).
3. **The user stamps** the compositions on the board.
4. **Moves between stamped compositions:** the grey-box lock-in (`greybox-composition.md`). The KEY is a stamped comp;
   FIRST and LAST are the outcomes of a legal simple move and pass the same analysis.
5. **Write the list around the picks** (§1–§4): stamped comps become KEYs, with the moves the user picked; good and
   noted shots keep their place; notes are quoted.
6. **Close the gaps both ways:** a beat with no strong frame requests new compositions (sample only families under
   their caps); a weak or redundant shot is folded into a neighbour, or moved to the moment where its pose is true
   (matching its stamped comp); a comp that serves no beat stays on the board, out of the film.
7. **Iterate** (new comps → stamps → moves → the list updates, with a "changes since last round" note) until the user
   locks the shot list, with the film-level checks below run at the lock.
8. After FIRST / KEY / LAST (stage 8), **the animatic finalises the edit and the script** (stage 9): cut points, match
   cuts, act lengths, runtime. Change the script text first, then the data.

## 6. Gate and hand-off
**Film-level checks at the lock.** They are cheap on the spec and expensive at the edit; in one film all three were
found only at the edit, after the FKL frames had been approved. Run them on the spec cameras in shot order:
1. **Neighbour sameness:** no adjacent shots under 30° apart (√(Δaz² + Δel²) about the subject) and under ×1.5 in
   field. Fold the pair into one shot, or re-angle one of them.
2. **Placement across each cut:** the eye jump between the subjects' anchors ≤ 25 % W and screen direction kept,
   unless the cut is designed as a jump (`comp_analysis.py cuts` on the planned LAST → FIRST pairs;
   `composition-analysis.md` §G3).
3. **Covers that don't read:** any frame with a glass cover in it and the camera more than ~100° off the product's
   front, or nothing bright on the cover's mirror ray (`lighting.md` §6).

**Music on screen is picked with the shot list.** Any music that appears in picture (a printed label or package, a
track name on a display) is chosen now, with the list; until the pick, the shots that show it are held out of
production. Why: music chosen later forced new artwork and a re-render of every frame where it showed.

- Gate: the user locks the shot list; the cross-reference table accounts for every good, noted and stamped source and
  every scrapped shot; every shot says how it serves the intention; the film-level checks pass or the user accepted
  the exception (quoted); every stamped comp has its analysis and its dressing log; any on-screen music is picked or
  its shots are marked held.
- Hand-off: a spec script turns the list into frame data (frames as candidates: subject, az, el, W, f, N, place, pose,
  light, card, set and its dressing log; per shot the chosen move: generator, direction, rate, t_KEY) for the FKL
  harness (`fkl-frames.md` §2).
- Show: the spec, a board overview section, and one section per act as the FKL frames land.

## 7. One source of truth for the shot data
The shot JSON is the numeric hand-off that every later stage reads (FKL, trims, the production packs, the grade). Build
it from exactly two files: the spec and its builder.
- **Inline small data.** Focus overrides and fill-probe rows go in as literals, not side files.
- **Name every other input** in a `source` block: render outputs, the approved-comps manifest, the harness features,
  the master .blend, the safe-off list, the dressing logs.
- **The dressing log travels with the frames.** Each composition's dressing changes (the object, the delta in mm and
  degrees, why) are carried into its frames' set data, so the FKL restore check (`fkl-frames.md` §5) can diff the
  scene against them. Hiding is not a composition fix (`composition-analysis.md` §E6).
- **Check for staleness on every build.** Compare each frame's spec candidate (camera, pose, light, set, lights,
  card, fill, unhide, focus point, subject parts, grade EV) against the candidate recorded with its render, and write
  mismatches to `stale_frames`. One edit plus one rebuild then lists exactly the frames to re-render (it catches, for
  example, frames rendered before a film-wide hide).
- **Motion is part of the hand-off:** per-channel keys with the named ease, the camera interpolation and the timing.
  The sequence baker must evaluate those verbatim (the same camera path the scene trims were computed on), never
  re-interpolate through FIRST/KEY/LAST (`octane-production.md`, the pack checks).
- **Placement fixes state the content direction.** `place` [u, v] is where the subject lands: raising v moves content
  down, raising u moves it right. W is a dolly, so near and far parts move differently. Without the stated direction,
  fixes get the sign wrong repeatedly.
