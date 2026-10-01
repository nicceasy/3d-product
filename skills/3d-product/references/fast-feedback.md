# Fast feedback loops: the rule over every step

> "Moving forward, we need to focus on faster feedback loops. This is vital." — the user, after an Octane test plan came
> back at ~30 h of render-node time ("it shouldn't take 30 hours to test… the important part is to COMPARE the engines").

Why: the expensive mistakes are plans and render rounds that run before the cheap version was seen.
- **A full test matrix before the first side-by-side.** An engine comparison planned as ~100 tests (~30 h) was cut to a
  4–6 h plan at preview resolution once one side-by-side existed.
- **A farm night before review.** A full beauty round of a whole film came back with ~15 % of shots scrapped and about
  half the rest changed. Most notes were about composition, camera moves, DOF and mechanism timing: all visible at
  grey-box cost.

The loops that work are short: single-frame grade tests (the author: "test on single frame renders at first so we can
see"), quick composition review rounds, fits that take seconds each.

## The rule
1. **Something visible early.** Within 30–60 min of starting anything, have something the user can look at: a frame,
   a side-by-side or a captioned sheet, labelled preliminary. Status lines don't count as results.
2. **Checkpoints, not a final report.** Show a new visible result every 1–2 h. Agents write each one to a checkpoint
   file and say so, and the lead relays it to the user.
3. **Budget before running.** Estimate machine time as tests × seconds each.
   - Over budget → cut the plan before running it: fewer levers, one factor at a time, and stop a line once it has
     answered its question.
   - Defaults: ≤ 1 h per look-dev question; ≤ 4–6 h of render-node time per study sweep.
   - A farm night only after a low-res version of the same thing was approved.
4. **Run the cheapest test that answers the question.** Climb the ladders below one rung at a time. Pay full cost only
   to confirm a winner or to deliver.
5. **The farm is for throughput, not iteration.** Iterate at preview cost on the workstation; render nodes render finals after approval.
6. **Deliver the first complete build immediately, then iterate.** When the user is waiting for a cut, a mix or a
   frame, the first version that works end to end goes to them at once; refinements follow as new versions. Measured:
   an agent iterating unseen on a metric through seven versions kept the user waiting ~40 min ("This is taking way too
   long").
7. **Don't turn a simple step into a study.** A step the user asks for plainly gets the one standard method, done in
   minutes (OIDN on the frames, then move on). Options belong only where the user asked for options. Example, the
   user: "Single frame denoise passes should not take 45 minutes. I just want a simple denoise filter applied
   before we do the rest of the camera fx and grain."

## Ladders (climb when the rung below has answered)
| Axis | Rung 1 (minutes) | Rung 2 | Rung 3 (confirm / deliver) |
|---|---|---|---|
| Resolution | 320–640 px wide: composition, motion, framing | 960×540: light, material, grade, engine comparison | 1:1 crops at full res (noise, detail, sharpness), then 1080p/4K finals |
| Sampling | low spp + denoise (look-dev) | target sampling on a crop (noise, time) | full frame at target sampling |
| Engine | Workbench / EEVEE clay (composition, moves) | Cycles / Octane preview | final engine, final settings |
| Scope | 1 frame | FIRST / KEY / LAST of one shot | one shot → all shots |
| Film | stills at both keyframes | 640×360 grey-box animatic (moves, timing, the cut) | beauty sequences |
| Look / grade | one frame, numerical twin on a cached EXR | the regime frames (day, dark sweep, macro) | all shots |
| Model changes | the most visible fix, before/after crop | all fixes on one camera | re-render (behind any render gate) |

## Speed-ups
- **Time scales with pixels, fixed costs don't.** Measure render time at low resolution, extrapolate, and confirm once at
  full size. Octane's `stop_render` costs ~4.4 s per frame (measured once); scene load is paid once per launch.
- **Keep the scene loaded.** Loop variants inside one Blender session (set → render → save) instead of one launch per
  test. A dressed set can carry hundreds of packed images (thousands of MP) that every launch reloads.
- **Run variants side by side on Cycles.** At preview size, one variant per GPU (pinned by PCI bus id) keeps
  every card busy. Octane's server picks its GPUs itself.
- **Border-render crops** answer detail and noise questions without rendering whole frames.
- **Numerical twins** (the finish chain's numpy twin on a cached EXR) answer grade questions without rendering at all.
- **Stop early.** A test line ends when its answer is clear; completeness is not a goal.

## Agent briefs
Every brief states:
- the question;
- the user's standing rules that apply (quoted), and what the agent may not touch;
- "deliver the first complete build at once, then iterate";
- the machine-time budget;
- the first checkpoint: what it contains, and by when (≤ 60 min);
- the checkpoint cadence;
- where checkpoint files go (`<study>/checkpoints/NN_<what>.jpg` + a line in STATUS.md).

Checkpoints ship full frames as well as sheets: 1920×1080 PNG per variant, with no captions and grain baked in, at
`<stream>/review/<checkpoint>/<shot>/NN_<variant>.png`, plus short clips wherever motion matters.

The lead publishes each section with the project's review publisher to one shallow folder in a synced review root
(iCloud Drive or similar, so the user can review on a phone): `<review root>/<NN>_Review_<Section>/`. A section folder
holds, flat:
- `00_contact_sheet.jpg`: every frame at full resolution;
- `<shot>_<NN>_<variant>.jpg` at JPEG q95, 4:4:4. q90 loses ~20 % of the grain;
- the MP4 clips.

The rule: one review root, shallow, JPG + MP4, and one full-res contact sheet per review section.

Research agents write their TL;DR and decisions first and deliver the detail after. The lead reads each checkpoint as
it lands and puts it in front of the user (SendUserFile or the board). The lead doesn't wait for the final report.

