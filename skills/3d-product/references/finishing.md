# Finishing: the look chain or film emulation, DaVinci Resolve by script, delivery

The entry point for the finishing stage. Detail: `realism-finishing.md` (measured targets, the Resolve plumbing and its
traps, §8 the gentle look), `camera-post.md` (lens optics, film character: mist, grain), `traps.md` (Resolve traps), the
Resolve manual (or a `/resolve` reference skill, if installed).

**Pick one finish per film, and say which.** Either the gentle look (§1) graded as one gradient (§4, §4b), or film
emulation (§7), whose lab timing (printer lights and exposure per shot) replaces the §4 / §4b trims, the look and the
grain. Never run both solvers on one film: each would undo the other's per-shot values.

## 1. The chain that works (per frame, scene-linear EXR in)
1. **Exposure 0 EV** per light state (no per-shot solve; a film whose light moves adds only the bounded §4 trim),
   **no white balance by day**: the render's own light is the look (a low sun stays warm). With practicals as the
   key, one partial balance toward the lamp per light state (`lighting.md` §9.5).
2. **Pro-Mist-like diffusion:** energy-conserving scatter `x − s·x + s·(K ∗ x)`, K = Gaussians σ 3/14/45/140 px at
   1080 lines. 1/8 = s 0.04 (the default); "1/4 held" = s 0.08 without the 140 px veil (the glow of 1/4, the black lift
   of 1/8). It costs no highlight chroma.
3. **Colour: a reference-matched look** (`realism-finishing.md` §8): a film curve on luminance (floor L* ≈ 1.5, print
   white L* ≈ 95, grey 0.18 → L* ≈ 48, contrast ≈ 1.6) with each pixel's colour carried through (sunlit colour keeps its
   chroma), a path to white, a near-neutral trim, the reference's colour-light (e.g. teal hue bump, gold light, olive
   shadows on warm hues only), chroma knees, colour by lightness, gamut mapping by chroma only.
4. **Grain in the display domain, fresh per frame** (seed = frame): 35 mm fine-like, σ 1.0–1.7 codes at 0.43 px,
   blue coarsest, mids strongest, the print floor protected.
5. 16-bit out → **ProRes 422 HQ** (10-bit 4:2:2) and **H.264 ≥ 40–50 Mb/s** (libx264 slow, tune grain), BT.709
   tagged. Fine grain loses 35 % of its σ at 16 Mb/s and 58 % at 8 Mb/s (measured); for streaming use a coarser grain
   (~0.8 px: −11 % at 16 Mb/s) or ~1.4× amplitude, and re-measure σ after the real encode.

Run it as one script over an EXR directory with parallel workers (a few seconds per frame per worker on a laptop CPU),
with a stills mode for sheets and a preview mode for drafts.

- **No denoiser by default** (`cycles-production.md` §9.1): finals are sampled to the noise target, so the chain starts
  at step 1. A colour-only OIDN pass (Blender's compositor as an image processor, about 1 s/frame) runs only when the
  user asks, and only on *converged* frames; there it adds no boil in motion. Measured: a film rendered at a third of
  the samples and denoised in post was rejected for artifacts. An in-render AI denoiser left single-pixel speckle and
  blotchy mottling (lifted blacks) on dark lacquer and dark plastic at 256 and 512 spp. Whenever a denoiser is tested,
  the raw beauty stays in the same EXR (extra layers plus a header flag), so the chain can choose without a re-render.
- **Realism targets as diagnostics, on each regime's KEY** (day, dusk, macro, night): measure L1 / L5 / L50 / L99, crush,
  clip, C99 and the cast against `realism-finishing.md` §3 (low key) or §7 (daylight and normal key). A miss is fixed in
  the light (stage 5), not in the grade.
- **Lens character is optional:** the lens pack (CA, vignette, edge softness) reads mainly as vignetting on 85–135 mm
  lenses: off by default. Halation only if the warm fringe is wanted in every sunlit shot.
- **Freeze every shipped look version under a name** (v1.0, v1.1, …) and stamp name + md5 on every sheet and clip
  (pin it through an environment variable the finisher reads). A version edited in place makes a reviewed frame
  unreproducible.

**Don't:**
- a bounded realism solver per shot toward absolute targets on motivated light (the §4 gradient trim is different:
  small bounded trims toward a smooth path between neighbours, on top of the per-state balance). On golden-hour frames
  it lifts blacks, pushes exposure up and neutralises the sun. Its measured targets stay useful as diagnostics
  (`realism-finishing.md` §3, §7);
- per-channel film curves on sunlit colour (they bleach it from about +1 stop);
- statistical colour transfer from a reference;
- PBR Neutral / AgX for finals (their toes crush low-key blacks).

## 2. DaVinci Resolve Studio 21.1, by script
**What Resolve is for here:** the edit (timelines per act, markers, the cut plan), the look as a LUT when the user
wants to grade in Resolve, ResolveFX, and the delivery render. Drive it through the API (an MCP bridge on a remote
machine, `DaVinciResolveScript` from a venv locally).

- **Assembly** (a cut plan as data → a build script): create the project, set `timelineFrameRate` "24" before any
  import, bins per act, `ImportMedia` EXR sequences, `AppendToTimeline` with **endFrame exclusive** in 21.1 (pass b + 1,
  check `GetDuration`), markers at `item.GetStart() − timeline.GetStartFrame()`, clip colours per act. ASCII names only.
- **The look in Resolve:** a 65³ LUT of the look (measured ≈ 0.7 codes mean error, p99 ≈ 2.5); port it to a DCTL for
  pixel parity. `SetLUT` only accepts LUTs inside Resolve's own LUT folders; Fusion `FileLUT` takes absolute paths.
- **Everything else as Fusion comps:** build by API, `comp.Save`, `TimelineItem.ImportFusionComp`, leave one comp per
  item. ResolveFX OFX main input is **`Source`**. Wrap every native colour tool in a ResolveFX CST V2 sandwich
  (DWG → Rec.709 linear before, back after): native tools run in DaVinci Wide Gamut and a per-channel gain comes out
  ~2× too strong. Keep the DRT output at Rec.709 / Linear and let RCM encode sRGB.
- **White balance after colour:** von Kries gains on the neutral base's near-neutral pixels (Oklab C < 0.02,
  20 ≤ L* ≤ 90), placed after the colour tools and before FX and the display transform, refined by two re-renders,
  then a display-linear trim. A 3-band trim removes shadow/highlight casts on neutrals (measured: the share of cast
  neutrals from about half to < 5 %); WB can't undo chroma pushes (a saturated label stays neon after printer lights).
- **FX at "noticeable":** the lowest level with local ΔE00 ≥ 3 on at least 2 of 4 frames (1:1 crops); measured
  starting points: halation 0.10, aperture diffraction 0.08 (pin-point source from a luma high-pass in alpha), lens
  reflections 0.16, radial CA 0.002 via LensDistortion split R/B (Prism Blur isn't radial). Light Rays and Glow
  thresholds are frame-critical: sweep them per shot. Exploring "too far" means 2–3× the tasteful maximum and still
  readable.
- **Exploring looks** (when the user asks for options):
  1. Rows = approaches. Each row carries a label, its too-far setting and a dial-back range.
  2. Columns = 3–4 regime frames (e.g. day, dusk, a macro, a label close-up). Every tile is full resolution with a notes
     box (`figjam-board.md`).
  3. Add a combination matrix (approach × finishing FX) on one hero frame.
  4. Re-show the colour approaches with white balance applied after the colour.
  5. Build each look by hand on the colour tools, never only a preset (the Colorist Guide's craft).
  6. Re-render the user's picks at the middle of their dial-back range.
- **Proof before trust:** push a chart through identity (grey = sRGB(lin) within 1 code), then a deliberate change (a
  4× gain) that must visibly land; a saturated-magenta dummy item shows any comp that silently didn't apply; check
  every delivered frame against its numpy twin.
- **Long sessions bloat** (measured: tens of GB after a few hours and ~1,500 comp imports; imports slowed ~50×): build
  on the Media page, delete scratch timelines between batches, save and restart Resolve when builds crawl.
- Save a `.drp` per project (`ExportProject`). The user likes one project per shot for stills, one project per film
  with a bin per act for sequences.

## 3. Measure and gate (stage 12)
| Check | Pass |
|---|---|
| The finish | named: the gentle look + one gradient, or film emulation (§7); never both solvers |
| Plumbing, on any new setup | a chart through identity: grey = sRGB(lin) within 1 code; a deliberate 4× change visibly lands |
| Twins | every delivered frame matches its numpy twin (L50 within ±1.5; a film chain in Resolve measured mean ΔE ≈ 0.1–0.4) |
| Version | the look's name + md5 stamped on every output |
| Realism diagnostics | each regime's KEY measured against its targets; misses sent back to the light |
| Regimes seen | the user has seen single KEY frames of every regime (day, sunset, dusk, macro) before all shots are finished |
| One gradient (gentle look, light that moves) | KEY-strip neighbour steps inside their caps (§4); every trim inside its bounds |
| Cuts | every OUT → IN displayed step inside its caps (§4b) |
| Film emulation (when used) | the critic's hard gates pass, the blind identification passes, the timing table sits inside its caps (§7) |
| Grain | σ re-measured after the delivery encode (fine grain lost 35 % of its σ at 16 Mb/s, measured) |
| Level and colour against the approved frames | a re-finished shot within ±5 % level and ~2 ΔE mid-tone colour of its approved version unless a change was asked for (judgement); an unchanged shot diffs at 0.00 codes |
| End hold | the final shot plays through the hold; the mix's length = the picture's (§5) |
| Final-edit audit | every frame of every plate on disk, beauty-only shots flagged, overrides in one versioned file (§6) |

## 4. Grade the film as one gradient (the KEY strip)
The user reads a film whose light moves through the day as a strip of its KEY frames, each blurred in the mind to one
colour. The grade makes that strip a smooth gradient: gradual steps from shot to shot, the story's direction kept (it
need not run cool → warm exactly). Most of it is small per-shot trims; what the trims can't reach goes back to the
light.
1. **Build the KEY strip** in edit order, including the transition slots, from the scene-linear EXRs through the look.
2. **Measure each KEY** (a numpy twin of the look at ~480×270, verified against the finished frames within 0.5 L*):
   - **primary: the frame's light colour** = the mean display-linear XYZ turned into a chromaticity and shown as
     CIELAB a*/b* at a fixed L* 76 (brightness removed);
   - **mean L\*** as its own axis;
   - secondary only: the white point of the neutral pixels (lowest-chroma third) and of the highlights, their CCT and
     Duv. **Don't drive the grade with the neutral white point in mixed light:** the least chromatic pixels sit wherever
     warm lamps and a blue window cancel, and jump wildly between neighbours.
   - flag **content-dominated frames** (a large coloured object: a label, a coloured light filling the frame): their
     mean is the object, not the light, so they get a low weight and their neighbours set their targets.
3. **Design the target path per phase:**
   - smooth the current path (Whittaker), with the curvature term cut at the one allowed jump (the lamps-on ellipsis);
     flagged and content frames at weight ~0.05;
   - soft **story ranges per phase** for b*, a* and L* (e.g. neutral afternoon, warmer golden, warmest sunset, a dip
     when the lamps come on against a blue exterior, warming into night; a* rising slowly as lamps take over; L*
     falling through the evening);
   - **monotone within each phase**;
   - **capped neighbour steps** (rules of thumb: Δb* ≤ 5, Δa* ≤ 3, ΔL* ≤ 6, so the light-colour ΔE between neighbours
     ≤ ~6); one bigger step allowed at the lamps-on ellipsis (Δb* ≤ 14, ΔL* ≤ 8). Tighter caps flatten the story
     (a lamp close-up and a window shot forced to one colour); looser ones read as steps;
   - L* as a band (target ± 4): inside it, exposure is left alone, so a dark macro may stay darker than a wide.
4. **Solve a bounded trim per shot**, in scene-linear Rec.709 before the look, on top of the per-light-state balance:
   x' = sat( diag(g(mired, Duv)) · 2^EV · x ), a camera-style WB gain normalised to luma 1. **That is exactly an ASC
   CDL** (Slope = g·2^EV, Offset 0, Power 1, Saturation s), so any grading tool reproduces it 1:1. A DP's bounds:
   - EV ±1.5;
   - WB 4500–7500 K, read as moving the camera off a 5600 K base;
   - Duv ±0.006;
   - saturation 0.85–1.15.

   Minimise the (b*, a*) error to target (content frames at low weight) plus L* outside its band, with small pulls
   toward identity; several starts.
5. **Anything beyond the bounds goes back into the LIGHT.** Re-solve a bound-hitting shot in a wide box to see what it
   wants; that is the list of light fixes (a shot that wants +2 EV needs more fill or sky; a practical/exterior
   imbalance of ~2 stops between neighbours needs the lamp or the environment rebalanced, `lighting.md` §9.7). Render
   the fix variants for just those KEYs, measure them with the same metric, pick, and re-run the solve.
6. Show the strip before and after, graphs of b*/a*/L* against edit order with the targets, and a table per shot (the
   node, before/target/after, neighbour ΔE, flags). Re-run whenever the KEY list changes (a new edit, a new transition
   shot): the transitions should land on the path as stepping stones.

### 4b. Grade the cuts, not only the KEYs (the white-balance pass)
**Why:** the eye compares the OUT frame of shot N with the IN frame of shot N+1. A strip of KEYs can read as one
gradient while a cut still jumps from warm to cold (the author: "the white balance is off between [two shots]. goes from
warm to cold ... make sure you do the white balance pass ... to smoothly transition throughout the sequence").
1. Measure every rendered frame of every shot through a numerical twin of the finish, in the **colour as displayed**
   (the blurred display colour of the frame) as the primary metric; a luminance-weighted mean-light colour missed a
   visible warm-to-cold cut.
2. Solve all shots jointly. Variables per shot: EV, warmth (mired) and Duv at the IN end and at the OUT end, ramped
   linearly across the shot. Objective: at every cut, hinge penalties on the displayed Δb* and Δa* above their caps
   (rules of thumb: |Δb*| ≤ 2.5, |Δa*| ≤ 2.0; mean-light |Δb*| ≤ 5, |Δa*| ≤ 4), small steps everywhere, each shot's
   mean pulled weakly toward its §4 target, an L* floor per end (the never-too-dark floor, `lighting.md` §9.10), and a
   pull toward the current grade.
3. Limits: each end inside the §4 DP bounds; the ramp within a shot capped (≈ 20 mired in all, ≤ 6 mired per second);
   exposure is not a white-balance tool (≤ ±0.25 EV). A light change the story puts inside a shot (a lamp switching on)
   stays inside it; no cut is exempt.
4. Show a cut table (OUT → IN, before and after, per cut) and the strip; apply it as a per-frame node in the finish.

**In DaVinci Resolve (plan; prove it on a chart before trusting):** a project in scene-linear Rec.709 (timeline gamma
Linear, colour-space-aware tools off) so a CDL slope is the twin's RGB gain with no colour-space sandwich; per clip, a
DRX template applied first (the API can't add nodes), then the per-state balance as a small DCTL (3×3 + gain), the
shot trim by `SetCDL` (ASC saturation uses Rec.709 luma, as the twin does), the look once on the timeline as a DCTL for
pixel parity (a 65³ cube is not accurate enough in lifted shadows), grain after the look. Proof: a chart through
identity (grey within 1 code), a deliberate 4× slope that must land, and every KEY exported from Resolve compared with
the twin's strip (L50 ±1.5, b* ±1). Save and quit Resolve only through its API.

## 5. The sound conform and the end hold
The approved mix is conformed to the finished picture by script after the picture conform. It runs automatically at
the end of the finishing chain (`render-supervision.md` §3; mix rules in `sound-design.md` §11).

**The final shot plays through the end hold; it is not a frozen frame.** When the mix rings past the cut:
1. Extend the final shot's render to ceil(mix length × fps) − cut frames, plus ~1 s of margin.
2. The camera's move and every running mechanism continue at their rates, evaluated in the rig with the operator layer,
   never extrapolated from packed frames. Focus is recomputed from the subject distance, never by extrapolating a rack.
3. Fade to black over the last ~1.5 s. Pad or trim the mix to the new length.
4. Put the extra frames in the stage 10 estimate. Rendered late, the extension costs a full re-render of the shot.

A frozen last frame is the fallback only when there is no time to render.

## 6. Highlights, glare and shot-to-shot colour
- **"Blown out" is usually the preview's clip, not the render.** Scene-linear EXRs keep 6–9× white in a sunlit sheen.
  Recover detail in two parts: a **local burn driven by the light itself** (a mask from heavily blurred log luminance,
  0.5–4 stops over the frame median, smoothstepped, up to −2.5 EV; low-frequency, so texture keeps its contrast) and a
  **soft roll-off** of what remains (a log shoulder on the max channel, hue kept). Where the EXR has no texture (a spun,
  defocused label), no grade invents it — say so.
- **Glare from extreme highlights only** (how Resolve's Glow and Aperture Diffraction work): isolate the excess over a
  scene-linear threshold (~4× white, soft knee), spread it with a power-law sum of Gaussians, **add** it after the grade
  burn. Guard size: subtract a ~0.8 %-of-width blur from the excess first, so windows and defocused lamps glow at their
  edges instead of veiling the frame. Rejected in review: a mist/diffusion filter (softens the whole frame), lens
  ghosts and starbursts (invisible at physical strength on 4–9× sources, gimmicky when boosted). **Apply only to the
  shots the user names** — a "whole sequence" request was withdrawn within minutes. Glare stays opt-in per named
  shot: a final cut may carry none (it was removed from one delivered cut).
- **Colour temperature between neighbours:** measure the mid-tone (L* 15–85) mean a*/b* of the outgoing shot's last
  frame and the incoming shot's first frame; move the odd shot to their midpoint with an exposure-neutral (sum-zero)
  printer-light or gain offset solved by finite differences (two probe renders, two refinements).
- **Auto-timing re-runs undo trims.** A closed-loop timing/match solver re-run on a new version re-times every shot and
  silently cancels deliberate per-shot lifts. Carry the approved per-shot values forward; re-solve only the shots whose
  plates changed; diff every unchanged shot against the delivered version (0.00 codes) before sending.
- **Final-edit audit before a conform:** every frame of every plate on disk for the cut's length, the passes each shot
  has (flag beauty-only shots), the mix's length = the picture's, overrides (new plates, longer shots replacing holds)
  in one versioned file the engine reads.

## 7. Film emulation (when the user wants a photochemical finish)
**Rule.** Emulate the physical chain in density, not as a display filter:
- lens and diffusion → layer exposures → the negative curve;
- grain in density per layer, fresh every frame;
- interimage → printer lights → the print curve and dyes → display.

Hold ONE look per film and time the shots like a lab: per shot, only printer lights or exposure change. This finish
replaces the gentle look, its grain and the §4 / §4b trims.

**Why.** Three things measured as the digital tells: a grade per shot, grain in display space, and white-balanced
practicals. A film finished this way passed an expert critic's gates and was delivered.

**Procedure:**
1. **Research archetypes into cards**, each with a frozen signature: stock, process, print or scan, grain, halation,
   era. Shortlist the ones the product survives. Measured: reversal stocks failed on a dark product in night sets,
   because the slide's maximum density swallowed the product's body.
2. **A common reference object balances the sets.** Use a part of the product with a diffuse finish: it is the one
   object in every shot.
   - Sample it as 6 × 6-px block means on its body, through the product-part masks rendered with the finals
     (`cycles-production.md` §9.5).
   - Reject gloss: keep the 15th–45th luminance percentile and the flattest 40 % of the blocks.
   - Take the median of log-chroma, not channel medians, over five frames per shot (first, ¼, key, ¾, last).
   - Frames that disagree mean the light changes inside the shot. Flag it; never keyframe the balance.
3. **Time per set, then per shot.**
   - Per time-of-day set: an exposure plus a partial chromatic adaptation toward the story's white.
   - Per shot: closed-loop timing on the *rendered output* until the reference matches its set. Measured: the per-set
     reference spread fell from 8–64 % to 0.2–4 %.
   - **Trim caps:** pass within ±2 printer points and ±0.25 EV; warn up to ±4 points and ±0.5 EV. Beyond that it is a
     light or render issue: flag it, unless the user asks for every shot matched.
4. **Measure near black correctly.** A dark reference sits at L* 3–5, where ΔE00 is nearly blind to chroma (measured: a
   43 % ratio spread read ΔE00 2.3). Pair the display ΔE00 (median ≤ 1, max ≤ 2) with:
   - ΔE00 after scaling the patch to L* 50 (median ≤ 1.5, max ≤ 2.5);
   - a log-chroma spread ≤ 0.08;
   - |Δa*| ≤ 1, with green–magenta errors weighted 2×.
5. **Author → critic loop.** An executor agent renders stills, keys and one motion shot per set. A critic agent then
   runs the hard gates, in this order:
   1. integrity;
   2. within-set and between-set consistency;
   3. the black floor, highlight roll-off and tone scale;
   4. colour physics;
   5. grain (σ, size, layer order, fresh per frame);
   6. halation, measured as a differential (the output minus a no-halation render);
   7. sharpness, banding and temporal behaviour;
   8. product readability against a neutral print.

   Then a fresh critic identifies a blind line-up (system, format, era, stock family). Then come visual scores 0–5 in
   nine categories, and the digital-tells list and the overdone list, which must both be empty.
   - **Fixes:** ≤ 5 per round, each in physical units on one parameter family. Never "make it more filmic".
   - **PERFECT** = every gate passes, every score is 5, the blind identification passes and nothing is overdone.
   - **Signatures freeze at round 1.** They may only be tightened, and only with evidence.
   - **Round limits:** 8 rounds per treatment (12 while failures are still falling), then swap the archetype.
   - **Render defects** are reported as render notes and never graded away.
6. **Cut from approved treatments only.** A detached queue renders each approved treatment's full cut with the locked
   mix, and the user picks from full cuts. A timing re-solved on a new version carries the approved per-shot lifts
   forward (§6: auto-timing re-runs undo trims).

**Bringing it into Resolve** (generic; Resolve's own traps are in `traps.md`):
1. **The project:** non-colour-managed YRGB, fed the scene-linear EXR plates.
2. **The chain:** compiled to one DCTL per shot, set in LUT mode on node 1. The shot's timing (exposure, flash, printer
   points) sits as named constants at the top of the file; edit the file, then Reload DCTL.
3. **Node 1's own primaries act before its LUT,** so they work as scene-side (camera exposure) trims only.
4. **Grain:** a Fusion Film Grain on the clip: log processing on, colour grain, per-layer strength from the engine's
   rms, a new seed per frame. Calibrate it against the reference engine's output grain: compare the high-pass residual
   (render − twin) per tone band with the engine's own grain residual.
   - Halation and bloom need their own Fusion or ResolveFX equivalent, calibrated the same way.
5. **Verify** Deliver-rendered frames against a numpy twin of the engine (measured mean ΔE ≈ 0.1–0.4). Then check the
   whole film frame-accurate against the engine's cut: check every item's offset, and render single frames and match
   each to its source.

**Gate.**
- The treatment's critic verdict.
- The timing table inside its caps.
- The user's pick from full cuts.
- In Resolve, the twin and frame-accuracy checks.
