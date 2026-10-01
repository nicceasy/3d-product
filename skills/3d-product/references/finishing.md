# Finishing: the look chain, DaVinci Resolve by script, delivery

The entry point for the finishing stage. Detail: `realism-finishing.md` (measured targets, the Resolve plumbing and its
traps, §8 the gentle look), `camera-post.md` (lens optics, film character: denoise, mist, grain), `traps.md` (Resolve
traps).

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

- **OIDN colour-only** (Blender's compositor as an image processor, about 1 s/frame) on noisy *converged* frames; it
  adds no boil in motion. Frames that are already clean go without. **This is the default for both engines.** An
  in-render AI denoiser is adopted only after an A/B on the darkest rough finishes: measured, it left single-pixel
  speckle and blotchy low-frequency mottling (lifted blacks) on dark lacquer and dark plastic at 256 and 512 spp, where
  post OIDN on the raw beauty was clean with equal detail. When testing it, write the raw beauty into the same EXR
  (extra layers plus a header flag) so the finishing chain can choose without a re-render.
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
- **Proof before trust:** push a chart through identity (grey = sRGB(lin) within 1 code), then a deliberate change (a
  4× gain) that must visibly land; a saturated-magenta dummy item shows any comp that silently didn't apply; check
  every delivered frame against its numpy twin.
- **Long sessions bloat** (measured: tens of GB after a few hours and ~1,500 comp imports; imports slowed ~50×): build
  on the Media page, delete scratch timelines between batches, save and restart Resolve when builds crawl.
- Save a `.drp` per project (`ExportProject`). The user likes one project per shot for stills, one project per film
  with a bin per act for sequences.

## 3. Gate
- Every delivered frame matches its numpy twin (L50 within ±1.5; the chart proof on any new setup).
- The colour version is stamped on every output.
- Grain σ re-measured after the delivery encode.
- The user has seen single KEY frames of every regime (day, sunset, dusk, macro) before all shots are finished.
- A film whose light moves: the KEY strip reads as one gradient (§4), and every trim is inside its bounds.
- Every cut's OUT → IN colour step inside its caps (§4b).

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

## 5. The sound conform
The approved mix is conformed to the finished picture by script after the picture conform: when the mix rings past the
cut, the picture holds its last frame and fades, and the mix is padded to the new length (`sound-design.md` §11). It
runs automatically at the end of the finishing chain (`render-supervision.md` §3).
