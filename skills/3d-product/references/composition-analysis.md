# Compositional analysis: measure every frame, then judge it by eye

Required at stage 7 for every candidate composition, at stage 8 for every FIRST, KEY and LAST, and again at stage 9
after any camera or cut change. The author's rule: "with composition, it is required that we do the compositional analysis so
that the scene and subject fit harmoniously in the composition." The brief that started it asked for grey-box renders
"analyzed against composition principles", naming the rule of thirds, leading lines and the Fibonacci spiral.

## 0 · The rule, the why, and how it runs
**Rule.** No composition goes to the user, into the shot list or into the FKL harness without a measured analysis
that shows three things:
1. the subject wins its frame;
2. the frame's geometry is deliberate (placement, lines, divisions, edges);
3. the scene supports the subject and doesn't compete with it.

**Why.**
- Verdicts are semantic. No image metric separated accepted frames from the rejected ones
  better than AUC 0.65 (n = 32 vs 34) [measured], and canonical paintings score no higher than ordinary frames on
  global statistics. No score chooses a frame.
- The flaws are measurable: a subject sliced by an edge, a near-miss, a line almost level, a tangent, a rival prop, a
  merge with the background, a soft subject, a dead third. In one film they took five audit rounds of up to 120
  frames to clear [measured]. At composition cost each one costs seconds.
- Placement the user names ("left third to right third", "more centred") needs a recorded decision, not a drift.

**How it runs: code measures, the eye decides.**
1. The scene side (Blender, no render) runs the geometric pre-gate (§B) and the harmony checks that need the scene
   (§E4–E6).
2. One tool per frame measures the image (§C, §D, §E1–E3). It writes `<frame>.analysis.json` and an annotated tile:
   the thirds and phi grid, the declared anchor, the detected lines and eye path, the subject and product masks,
   rivals, the quiet region, and the numbers.
3. The eye pass (§F) reads the clean tile first, then the annotated one. "OK" is a reject.
4. The numbers and a one-line justification travel with the frame: onto the board, into the shot spec, into the FKL
   audit.

**Where it runs.**
| Stage | Frames | Input |
|---|---|---|
| 7 | every candidate that passes the pre-gate; every stamped composition | preview, 640×360, 16 spp + denoiser |
| 7, lock-in | FIRST and LAST of every sampled move (`greybox-composition.md`) | grey box, 1280×720 (§E3 and G9 wait for stage 8: clay has no colour or gloss) |
| 8 | every FIRST, KEY and LAST | FKL preview, 960×540 |
| 9 | after any camera or cut change: the new FIRST and LAST, the edit's in and out frames, every 12th in-between (the trigger lives in `camera-motion.md` and `editing.md`) | the motion preview |

**One look for judging.** Tone and colour gates move with the grade, so stages 7–8 judge through one frozen preview
look: the view transform plus a neutral grade, named before stage 7. When the final look is chosen (stage 12), re-run
§E1, §E3 and the dead-zone gate on the KEY strip.

**Conventions.** Lightness is OKLab L (0–1); chroma is OKLCH C. The squint image is OKLab L blurred by a Gaussian of
σ = 1 % of the width, then resized to 96 px wide. Blur and CoC are px at 1920 wide (scale by width ÷ 1920); every other
distance is a share of the frame width (% W) or height (% H). Analyse at ≥ 960 px wide. [measured] = a number from
runs; [judgement] = a threshold chosen and used, which worked.

## 1 · The tools
`scripts/comp_analysis.py` (flags: `--help`):
| Subcommand | Measures | Inputs | Writes |
|---|---|---|---|
| `frame` | the image-measurable gates of §C (G1, G2, G4, G5, G6 on contours, G7, dead zones; G3 when given depth and the camera), §D1–D8, §E1–E3 | the preview image; optionally the depth EXR; the subject mask, or the object-index EXR with the subject's and product's ids; the camera JSON (lens, f-stop, focus, sensor) for CoC; the brief JSON (size bands by role, placement policy, edge padding, mode) | `<frame>.analysis.json` + an annotated tile |
| `sameness` | thumbnail similarity across a folder of previews (§G1) | a folder | pairs ≥ 0.72 flagged |
| `cuts` | eye jump, angle, scale, brightest-region jump (§G3) | out/in frame pairs with their masks and camera JSONs | one row per cut |

Also: `scripts/reads_metric.py` (the R1/R2 reads gates, part of G8; `lighting.md` §5) and `scripts/macro_focus.py`
(N and the focus split for close-ups; `fkl-frames.md` §2b).

**G3 has one implementation for stages 7 and 8** (the formula in `fkl-frames.md` §2; the tool's default is Blender's
(F/N)(F/s)|z−s|/z, and `coc_model: "thinlens"` is there only for comparison). A composition scorer with a different
blur formula once over-read blur ×2–3.7 and misjudged frames for two days [measured].

**How the tool classes items (calibrated on 117 audited frames):**
- **Gates** (a fail repairs or rejects): G1, G2, G3, G4 (≥ 2 of 4 cues and no rival), G5, G6, G7, dead zones; E1a
  only when neither tone nor focus separates the subject; E1b, E1c, E2a (prop rivals), E3 (field chroma, hue clusters,
  accent size).
- **† items** (a fail owes a written reason): G1b, G5b and G5p (a blob or a product part at an edge), D1/D1b, D3, D7,
  E1d, E2b–E2d, E3b. Six of these are gates in the tables below, but they failed many frames the user accepted, so
  the tool reports them as owed reasons. Restore any of them as a gate in the brief when a film needs it.
- **It can't see** an object that isn't in the index (an unindexed wire passed). Keep every visible object indexed.
- **Calibrate per film:** on that set, G7 near-level lines, E1b and E3's warm field chroma failed frames the auditor
  had accepted by eye. Record those acceptances as exceptions, quoted, rather than loosening the thresholds.
- The brightest-region jump in `cuts` is new and uncalibrated: it failed 2 of 5 cuts that an audit passed. Report it.

The scene-side checks (§B, §E4–E6) are a method, not a shipped tool: Blender's `scene.ray_cast`, `BVHTree` and
`world_to_camera_view` over the posed product and the set.

## A · Once per set and brief (before sampling)
1. **The vocabulary:** the product's shapes, colour notes, reflective faces and what they mirror, and every
   mechanism's range.
2. **The set's traps, measured by projection, not by eye.**
   - For each long set edge (furniture tops, sills, jambs, window bars, shelf lines), solve the elevations and
     azimuths where it aligns with, kisses or continues a product edge, and where it falls 0.5–10° off level.
   - Measure the clearance around the product in every direction, and the lenses that put the camera behind
     furniture.
   - Measure the longest clear depth behind the product: that is where bokeh lives.
   - Write all of it as bands the sampler avoids.

   Why: whole families of views died for set reasons (frontal eye-level views were impossible with window bars just
   behind the product), and sampling into them wasted hundreds of renders [measured].
3. **Framing targets from the brief**, written into the brief JSON the tool reads:
   - the size band per role (the size table below);
   - the placement policy (anchors, or centre by default);
   - edge padding (≥ 3 % by default; more when the brief asks for breathing room);
   - each archetype's mode (§D);
   - the subject list, from the intention and the feature table (`shots-and-script.md` §0).
4. **Cheap previews:**
   - Compose in the master, never in a trimmed copy: objects outside every frame still shade windows (a trimmed save
     once made finals 3–7 % brighter, once 2× [measured]). Gate each final against its preview's mean brightness
     (look at anything beyond ≈ 5 %).
   - Build the set once per session with persistent data; cap set textures (the product, prints and labels exempt);
     keep instancing.
   - Group candidates by pose and light: a camera change costs 1–2 s, a pose 3–5 s, a light 5–30 s [measured].

## Size by role: the one table
One table, keyed by role, replaces the per-reference fill numbers. Write the bands into the brief before sampling.
**The brief overrides them**: an instructional film may want the subject large and centred, so write that band
instead. Solve whole-product cameras by fill (the projected hull spans the target inside the edge padding), not by
field width: sizing by fill cut edge failures from ≈ 35 % to ≈ 5 % of candidates [measured].

| Role or genre | Measure | Default band | Source |
|---|---|---|---|
| establish (a set or room film) | span: projected product width ÷ frame width | 8–12 % | measured on film and brand coverage of single rooms |
| medium | span | 12–25 % | same |
| hero in a set | span | 20–32 %, on an anchor, 30–40 % clean space | same |
| insert | the part, cropped | the subject passes G1 | — |
| macro | a part fills the frame | > 100 % span | — |
| object in space (studio, calm) | product area ÷ frame area | 20–45 % (< 15 % reads lost, > 60 % cramped) | judgement |
| packshot, or a graphic whole-product frame (the product is the shape) | span of the limiting dimension (height in landscape) | 55–78 % | measured on 18 reference packshots |
| field or scale archetype (small under a large window, in a patch of light) | area | 3–15 % | judgement |
| no role yet (exploration) | area, by scope | whole 4–40 %, most 15–60 % | judgement |

Scope: **whole** = ≥ 95 % of the projected hull in frame with ≥ 3 % clear on every edge; **most** = ≥ 60 % in frame;
**part** = < 60 %.

## B · Geometric pre-gate (scene side, no render)
Run on every sampled camera before it renders, ≈ 0.3–0.5 s each [measured].
| Check | How (Blender) | Pass |
|---|---|---|
| Camera clearance | `BVHTree.find_nearest` from the camera to all geometry | ≥ 20 mm |
| Foreground occluder | a 16×9 grid of rays from the lens; the first hit of each | no set object in front of the subject that would render defocused, unless it is a declared soft foreground layer |
| Set hiding the product | rays to points sampled on the product's camera-facing surface | ≤ 12 % blocked |
| Subject visible | the same for the subject | in frame, visibility ≥ 0.8 |
| Whole-product hull | project the hull's vertices | ≥ 95 % in frame, ≥ the edge padding on every edge |
| Lines and tangents | the long feature edges of the product and the set, projected, then clipped by visibility (points along each edge, ray-tested) | G6 and G7 (§C); hidden back edges are excluded, or they make false tangents |
| A glass cover | the camera's azimuth off the product's front | ≤ ~100°, with something bright on the cover's mirror ray (`lighting.md` §6), unless the cover is the subject |
| Intersections | BVH overlap, the posed product against the set | 0 |

Measured kill rate: 41–77 % of sampled cameras per round, over four rounds [measured]. A round that kills almost
nothing is sampling timidly; one that kills almost everything has unmeasured traps (§A2).

## C · Frame gates (a fail is repaired or rejected)
| Gate | Measurement | Pass [judgement] |
|---|---|---|
| G1 subject defined | named in ≤ 4 words; a mask: the part's index, or a derived mask for an element subject (below) | ≥ 0.3 % of the frame. A dot subject (an indicator, one button): ≥ 0.02 % and 4 of 6: the sharpest thing; the brightest or most contrasty; the only saturated hue; on an anchor; where ≥ 2 lines converge; clean space ≥ 3× its diameter |
| G2 subject intact | the silhouette in frame; ray visibility | ≥ 95 % and ≥ 0.8. A declared bold crop: ≥ 60 % in, and the edge cuts ≥ 10 % of its extent. Seen through glass: the glass's reflection over it ≤ 30 % of its own luminance |
| G3 subject in focus | √(CoC² + (N_eff/24)²), the median over the subject mask; focus on the visible surface | ≤ 2 px. A declared "the defocus is the subject" frame: squint ΔL to its ring ≥ 0.12 instead |
| G4 subject wins | four cues: (a) squint ΔL between the subject and a ring 4 % W wide ≥ 0.10; (b) mean \|Laplacian\| inside ≥ 1.5× the frame's median outside; (c) the saliency share inside the dilated subject ≥ 1.5× its area share; (d) ≥ 50 % of the frame's accent pixels on it | ≥ 2 cues, and no rival: no connected non-subject region larger than the subject that wins ≥ 2 cues itself |
| G5 edges | gaps and crossings at each edge, for the product silhouette and the subject | no near-miss (0 < gap < 1.5 % of that dimension); no nick (crossing an edge by < 8 % of its own extent, or touching it along < 3 % of it); whole frames keep the padding; no thin luminance band hugging an edge (a step within ≈ 1.5 % of it over ≥ 55 % of its length); no small prop cut into a sliver (< 0.4 % of the frame) or parked 0.1–0.6 % W from an edge |
| G6 tangents | projected 3D edges plus mask contours | no two contours parallel within 2° and 0 < gap ≤ 0.6 % H over ≥ 3 % W; no endpoint within 0.5 % W of another contour without crossing it; no contour continuing another (collinear within 1° and 0.5 % H, gap ≤ 3 % W); no prop outline running within 0.3 % W of the product's over ≥ 2.5 % W. Clear overlap or clear separation passes |
| G7 lines | the 1–2 longest straight contours (≥ 25 % W); roll; verticals | ≤ 0.5° or ≥ 10° off the frame axes; roll 0 ± 0.2° and verticals ≤ 0.5° unless a tilt is declared |
| G8 technical and reads | physical camera (focal f(1 + m), f-stop N(1 + m)); exposure as planned; `reads_metric.py` | R1 void ≤ 0.30 (warn > 0.20); R2 outline separation ≥ 0.20 when the product is the main shape (warn < 0.40) |
| G9 glossy black | a mirror-ray probe over the face (`fkl-frames.md` §2b) | reads black, unless it is the subject |
| Dead zones | each third's mean L and std; unlit faces | no near-uniform black third without a shape (the measured fault: L ≈ 0.07, std ≈ 0.002); a shapeless dark face ≤ 20–30 % of the frame height |

**Derived masks for element subjects** [judgement]:
- a reflection: the glossy pass over the reflecting part ≥ 0.6× its p99;
- a light patch: that light's group ≥ 0.5× its p99, in components ≥ 0.3 % of the frame;
- a shadow: the sun group < 0.05× its lit median on that surface;
- an accent: C ≥ 0.07 and a hue ≥ 60° from the frame's chroma-weighted mean hue; a lit indicator: L ≥ 0.85 and
  C ≥ 0.10.

**Fixes.** A dead zone or a merge is fixed with light (`lighting.md` §5) or by aiming, never with exposure. A rival is
fixed with the camera, then with light; never by hiding a visible prop. The other repairs: `composition-exploration.md`,
repair by diagnosis.

Why these gates: slices and near-misses were the most frequent fault in five audit rounds (102 frame entries), then
near-level lines (51) and rivals (20) [measured]; two later projects asked for padding ("breathing space on the
edges").

## D · Composition analysis (reported and ranked; † = needs a written reason when missed)
Rank within the frame's mode, never against one universal ideal.
| Mode | What it is | Diagonal share of edge energy (15–75°) | Quiet share | Balance |
|---|---|---|---|---|
| calm | horizontals dominate | ≤ 0.15 | 0.40–0.70 | DCM ≤ 0.06 |
| dynamic | diagonals or arcs dominate | ≥ 0.30 | 0.30–0.60 | DCM ≤ 0.20; tension is fine if the move resolves it |
| symmetric | the subject on the vertical centre line | — | 0.35–0.70 | symmetry ≥ 0.85; a centre division is allowed |
| field | the product small in a large field | 0.10–0.35 | 0.55–0.85 | DCM ≤ 0.20 |
| macro | a part fills the frame; figure–ground applies to the subject | 0.10–0.35 | 0.25–0.60 | DCM ≤ 0.20 |

**D1 · Placement † (the placement policy).**
- Placement is a decision, recorded per frame: **centred**, or **on a named anchor**.
  - Centred: symmetric or frontal subjects, and the default when the brief asks for centre.
  - Anchors: the thirds (1/3, 2/3), the phi grid (0.382, 0.618), the diagonal-method nodes (0.281, 0.719 of the
    width).
- Pass: the subject-mask centroid within 3 % W of its declared anchor or the centre. Between 3 and 6 %, nudge it on.
- **Drifting** is 6–15 % W from every anchor and from the centre: the "almost" of placement. It needs a written reason
  or a fix.
- **Lead room:** a directed subject (a part that points, a row of controls, a part about to move, or the direction of
  the camera's move) faces into the frame, with 55–65 % of the width free on the side it faces.
- Report which system the subject lands on; never score one above another. The anchors together cover about half the
  frame, so landing on one proves little [measured]. The golden spiral scored 0 in every honest test [measured]: it is
  not a mechanism.
- Fix placement by lens shift, not yaw: yaw tilts level lines into the dead band.
- Why: an off-centre subject that sits near no anchor reads as an error (the author: "the subject is off center.
  Confusing composition").

**D2 · Eye path and leading lines.**
1. Entry: the frame centre or the brightest region.
2. Lines: ≥ 2 lines ≥ 15 % W long whose extensions pass within 5 % W of the subject, at least one entering from an
   edge or a corner. Detect them on luminance and depth edges, weighted by luminance contrast: a depth edge the light
   doesn't show leads nowhere.
3. Terminus: the subject.

A frame fails D2 when its strongest line or brightest accent leads out of the frame or to a rival. By chance about 7 %
of a frame's line energy converges on any point [measured], so the score ramps from 0.07 to 0.25. In clay only light
draws lines, so keep printed marks as ink.

**D3 · Divisions and the horizon †.** No dominant horizontal or vertical (a horizon, a furniture edge, a sill, the
product's own long edge) within ±3 % of the 50 % line, unless the frame is declared symmetric: put it on a third or
out of frame. Adjacent intervals differ by > 10 %, unless it is a rhythm row. A crop cuts a crossing shape by ≥ 8 % of
its extent.

**D4 · Negative space.** Quiet pixels: the luminance gradient (blurred at σ ≈ 0.3 % W) < 0.2× its p99, or CoC ≥ 12 px,
outside the subject. The quiet share sits in the mode's band; the largest quiet region holds ≥ 60 % of all quiet, with
solidity ≥ 0.8; the largest empty rectangle is ≥ 12 % of the frame (a line of type fits).

**D5 · Masses.** On the squint image, a 3-level Otsu map: 2–7 masses of ≥ 2 % each; the largest ≥ 1.5× the next; the
product (whole or most frames) or the subject (part frames) matches one class with IoU ≥ 0.7 (zero marks below 0.3).

**D6 · Balance.** The weight map (saliency × sharpness × accent); DCM is its centroid's distance from the frame centre,
over the half-diagonal; symmetry is measured on edge energy. Targets per mode (table). Never "almost symmetric": a
symmetry of 0.60–0.80 with the subject within 5 % W of the centre is penalised.

**D7 · Size and figure †.** The product or subject share sits in its role's band (the size table). For whole or most
frames, ≥ 70 % of the product silhouette lies off the frame border (zero marks below 30 %), and the silhouette
contrast in paired 2 % W bands inside and outside it is ≥ 0.18 (zero below 0.04). Why: an automated lock-in filled
the frame edge to edge with the product in 64 of 68 frames [measured]; that is wallpaper, not a figure.

**D8 · Thumbnail and crop.** At 96 px wide the subject's ΔL to its ring is ≥ 0.10 (zero below 0.04) and the product
silhouette's contrast ≥ 0.12 (zero below 0.03). Crop stability: if moving any edge inward by ≤ 8 % raises the score
by > 5 points, move the camera to that crop and re-score.

## E · Scene–subject harmony (a fail is repaired or rejected)
**E1 · Tone** (image).
- The subject separates from its ring: G4 cue (a) ≥ 0.10.
- The product outline separates from what lies behind it: reads R2 ≥ 0.20 (warn < 0.40).
- A dark product stands on or against a ground ≥ ~1.5 stops lighter, or has a rim or reflection line along its
  silhouette [measured on 16 interior references].
- The background sits ≥ 1 EV from the subject, or is distinct in hue.
- Fix with light or the camera; never with exposure.

**E2 · Rivals and clutter** (image).
- No non-subject region ≥ 1.5 % of the frame is brighter than 1.3× the product's mean, or holds ≥ 20 % of the frame's
  brightest 3 %.
- No set object is sharper than the subject.
- Squint masses ≤ 7.
- No prop cut into a sliver, and no prop outline merging with the product's (G5, G6).
- An off-centre subject is balanced by a soft mass or bokeh, never by a second sharp detail.
- Fix with the camera, then light, then a plausible logged re-dress (§E6). Never a hide.

**E3 · Colour** (image, in the render under the shot's white balance).
- Field chroma p90 ≤ 0.08.
- At most 2 hue clusters.
- One accent (as derived in §C): 0.1–4 % of the frame (up to 12 % when a label is the hero).
- The accent sits on the subject or points to it: ≥ 30 % of the accent pixels on the subject or product, ideally ≥ 70 %.
- Measure it in the render, not in the material: a coloured part once rendered at C ≈ 0.02 [measured]. Colour comes
  from objects, and each accent appears at least twice across a film.

**E4 · Light** (scene side, plus the light-group passes).
- The key comes from a source the scene establishes: a window, a visible or known practical.
- The key's side relative to the camera stays continuous with the neighbouring shots, unless an ellipsis is declared.
  List the key's azimuth relative to each camera in shot order; a key cheated across for one shot breaks it.
- No second invisible sun: retitle the beat instead (`alive-environments.md` §7).
- The light makes at least one bounded shape on or within 10 % W of the subject: a patch, rim, reflection or shadow
  (the derived masks, §C) of ≥ 0.3 % of the frame, solidity ≥ 0.75, edge contrast ≥ 0.10. No shapeless reflection over
  ≥ 20 % of the frame.
- The light state matches the frame's slot in the light arc (`lighting.md` §9).

**E5 · Depth and scale** (scene side, plus the depth pass).
- ≥ 2 depth layers, ≥ 3 for a hero; metric layers sit beyond ±0.5 in log₂(z ÷ z_subject):
  - a soft foreground: CoC ≥ 40 px, 5–25 % of the frame, at an edge, 1–3 EV darker;
  - a sharp subject;
  - a background at CoC ≥ 20 px.
- Bokeh looks down the set's longest clear depth (§A2), never into a surface a few hundred mm behind the product.
- The lens stands at a real working distance and a human or rig height; depth of field, texel density and atmosphere
  agree (the scale test, `alive-environments.md` §10).

**E6 · Set and context** (scene side).
- Nothing visible is hidden for composition. Hiding is a render trim, computed later from visibility over the whole
  path (`scene-optimisation.md` §1).
- A prop may move plausibly, by a few cm. Each move goes into the composition's **dressing log** (the object, the
  delta in mm and degrees, why), passes the intersection check, and stays continuous across neighbouring shots.
- A glass cover keeps its story state and reads (§B).
- Where the set shows around the product, it shows the product's system (`alive-environments.md` §5); no surface or
  corner is empty by accident.
- Why: per-composition hides grew shot by shot and leaked into the sequences (one prop hidden in every shot, another
  in nearly half). The user caught it at the animatic, after sequences had started [measured].

## F · Eye pass and record
Yes or no, most important first. Each question sits beside the numbers it maps to; the numbers order the pass, the
eye answers it.
| # | Question | Numbers |
|---|---|---|
| 1 | Can I name the subject in ≤ 4 words within one second? | G1 |
| 2 | Squinting, do I see 2–3 big value masses, with the subject (or the product) one of them or on their boundary? | D5 |
| 3 | Is there one dominant shape, with nothing fighting it? | G4, E2 |
| 4 | Does the frame show enough of the product for its role, as a figure against a ground, not wallpaper? | D7, the size table |
| 5 | Are all four frame edges intentional: no near-misses, no nicks, bold crops? | G2, G5 |
| 6 | No tangents: no edges kissing, no line continuing another, nothing growing out of the product? | G6 |
| 7 | Are the long lines level or clearly diagonal, nothing "almost level"? | G7 |
| 8 | Is the empty space one calm shape (could a line of type sit in it)? | D4 |
| 9 | Is it balanced, asymmetrically or truly symmetrically, and not almost symmetric? | D6 |
| 10 | Is there at most one colour accent, on or pointing to the subject? | E3 |
| 11 | Does the light make a shape (patch, line, reflection, shadow) that helps the subject rather than fogging the frame? | E4 |
| 12 | Are the divisions unequal and deliberate (no halves, no equal gaps unless it is a rhythm)? | D3 |
| 13 | Does the eye enter, travel along a line and stop on the subject, rather than leave the frame? | D1, D2 |
| 14 | Would I print it and hang it: a clear read at a glance and a second read up close? | D8 |
| 15 | Across FIRST → KEY → LAST, is it one subject explored or one clear relay, with every frame composed? | §G2 |

**The record.** Per frame: the analysis JSON, the annotated tile, and a plain-language justification of ≤ 2 lines (the
subject, why the frame is strong, how the scene supports it through tone, light or line). It is published with the
frame on the board.

**Exceptions travel with the user's acceptance.** A frame that fails a gate stays only when the user accepted it; the
acceptance is quoted and recorded with the frame (for example, a dusk silhouette whose darkness is the point). It
travels into the shot spec and the FKL audit, where the auditor checks that the frame still matches what was accepted
and doesn't re-open it. An agent's own reason is not an exception.

## G · Set level and shot level
**G1 · The set of compositions.**
- Sameness: `comp_analysis.py sameness` scores each pair as the mean of the squint correlation, the 3-level Notan
  agreement and the subject-box IoU. Pairs ≥ 0.72 are flagged [judgement; a finished set of 50 peaked at 0.56,
  measured]. Then the eye rule: the same camera in another light or pose is the same composition.
- Family caps and quotas: `composition-exploration.md`, step 6.

**G2 · Each shot** (FIRST → KEY → LAST, at the stage-7 lock-in and at stage 8).
- **Explored or relayed.** Explored: the same subject in all three frames, changed by ≥ 12° of view or ≥ ×1.25 of
  scale. Relayed: subject B is visible in A's frames (soft is fine), or A and B are joined by a line or motion the move
  follows; at most one relay per shot. Fails: a rack with no subject change, three unrelated subjects, a subject that
  is "the room".
- The subject moves ≤ 15 % W between frames, or along a line visible in both.
- One dominant change over threshold (H, `greybox-composition.md`).
- In-betweens: every 12th frame keeps G5 and G6 for the subject (a tangent that flashes past in < 6 frames is
  allowed); the focus targets are unoccluded on every frame; camera clearance ≥ 20 mm.

**G3 · Cuts and neighbours** (`comp_analysis.py cuts`). Measure on the frames the viewer actually sees at the cut: the
composed LAST and FIRST at stage 8, and the edit's out and in frames once the edit trims handles (stage 9).
- Eye jump ≤ 25 % W between the subject-mask centroids (or the aim pixels); 15–19 % is the limit when the cut is
  motivated.
- Angle √(Δaz² + Δel²) about the subject ≥ 30°, or scale (the ratio of field widths at the subject) ≥ ×1.5, or the
  cut is an act break on a light change.
- The brightest region jumps ≤ 50 % W, unless the cut is a light cut.
- Every mechanism's state is equal across the cut.
- A planned match cut shares its framing.
- Neighbours: no adjacent shots under 30° apart and under ×1.5 in scale. Run this at the shot-list lock
  (`shots-and-script.md` §6), not first at the edit.

## Measure and gate
What stage 7 measures, how, and what passes:
| What | How | Pass |
|---|---|---|
| The set's traps | projection, once per set (§A2) | written as bands before any sampling |
| Every sampled camera | the geometric pre-gate (§B), scene side | every row |
| Every preview | `comp_analysis.py frame` + `reads_metric.py` | §C and §E pass; each † in §D met or explained |
| Scene-side harmony | key side per shot, light shapes, depth layers, dressing log (§E4–E6) | every item |
| The eye | the 15 questions (§F) | a yes on each, and a justification line |
| The set of 50 | `comp_analysis.py sameness`; caps; quotas | no flagged pair left unexplained; caps and quotas met |
| Lock-in moves | both ends through §C and §E; F and H | the ends pass; one dominant change |
| The shot list | §G3 on the spec cameras in shot order | no neighbour pair under 30° and ×1.5; every glass cover reads |

**Gate.** Every frame on the board passes §B, §C and §E, or carries the user's quoted acceptance; every † in §D is met
or explained; the analysis JSON and the annotated tile exist for every frame on the board.

**The user sees** the composition board: the clean tiles for picking, each with its justification line and key
numbers (the subject, the anchor or centre, the size share against its role's band, the gate closest to failing), the
annotated tiles beside them, a sameness sheet for the set, and the changes since the last round.

## Cost
Measured on a laptop-class GPU unless stated.
| Step | Settings | Time |
|---|---|---|
| Geometric pre-gate | scene side | 0.3–0.5 s per camera |
| Composition preview | 640×360, 16 spp + denoiser, persistent data | 0.6–2 s per camera; 3–5 s per pose; 5–30 s per light; set build 15–18 s |
| Analysis | per frame | 0.2–0.5 s |
| Grey-box lock-in | 1280×720, 64 spp | ≈ 15 s per frame; set build ≈ 12 s |
| FKL preview | 960×540, 256 spp + denoiser | 31–38 s per frame (128 spp is enough for a composition re-check) |
| Composition finals | 1920×1080, 1024 spp, on render-node GPUs | ≈ 52 s per frame; 50 frames ≈ 13 min on 4 GPUs |

One round's funnel: about 3,700 sampled cameras plus 650 repair variants → 1,900 previews → 600 passed the gates →
120 shortlisted → 50 kept [measured]. Nothing renders at full resolution before the stamps.
