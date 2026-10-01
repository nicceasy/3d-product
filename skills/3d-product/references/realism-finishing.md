# Realism: light that behaves, measured targets, finishing in DaVinci Resolve Studio

> **Current default: `finishing.md`.** The look is the reference-matched "gentle" chain (§8) at EV 0 with no white
> balance. A bounded solver toward absolute targets (§3, §7) no longer grades frames: on motivated warm light it lifts
> blacks and bleaches the sun. Its measured targets stay as diagnostics; §1–2 (why renders read as CG, the lighting
> gatekeepers) and §4–6 (Resolve plumbing and proofs) hold for any project.

## 0 · Finishing a new frame: the recipe
1. **Light it with the gatekeepers (§2)** and read the image *and* the numbers: crush, world/key ratio, the set's
   median, the reads gates (`lighting.md` §5).
2. **Final render:** 32-bit float EXR (ZIP), every emitter in a light group, the groups denoised separately so they sum
   to the beauty (check the ratio ≈ 1).
3. **Plates:** lens optics applied per light group (§4.2).
4. **Look:** the current chain (`finishing.md` §1). Use the targets below (§3, §7) as diagnostics: read where a frame
   sits outside them, and fix the light first.
5. **Finish in Resolve** (§4) and verify every delivered frame against its numpy twin (L50 within ±1.5). A frame that
   equals its "all gains = 1" twin means the comp was bypassed (§5).
6. **Sheet** the frames for review.

## 1 · Why renders read as CG (measured, not guessed)
Measured: frames a film critic praised as photographic vs a typical low-key CG render, same metrics.

| | Real frames | Typical low-key CG |
|---|---|---|
| Median L\* | 31 | 4 |
| Mid-tones (L\* 30–70) | 36 % | 11 % |
| Crushed pixels (max RGB ≤ 4) | ≈ 1 % | 38 % |
| C\*99 | 26 | 52 |
| Hue entropy | 0.44 | 0.26 |
| b\* | +2.8 | +7.2 |

Frames called "fake" differ from real ones mostly by chroma (+40 %, including saturated shadows) and a warm cast. Tonal
range barely differs.

**The biggest lever is the scene, not the grade.** The CG read comes from:
- keys light-linked to the product only;
- world = 0;
- practicals that neither reflect nor spill;
- a void around the product.

## 2 · Lighting gatekeepers, in priority order
1. **No product-only linking without a physical reason.** If the mood needs control, keep the product key linked and
   add a **set-only twin at 25–30 %**. That gives the pool, the contact shadow and the bounce.
2. **Put a room in the void.** An HDRI, or walls and flags, at **E_world/E_key ≈ 0.5–2 %** on the product, calibrated
   from light groups. Glossy metal then shows structure and reads as metal.
3. **Sources ≥ 5°.** Widen strips to about 0.09 × distance, or to ≥ 16–40 mm.
4. **Practicals must reflect and spill:** visible to glossy rays and lighting what's near them.
5. **Haze fills the set:** a volume spanning camera → background, σ 0.04–0.1 /m in a studio (a whisper, ~0.006 /m, in a
   room: `lighting.md` §2), with noise.
6. **Scale:** entrance pupil ≈ 10–15 mm for heroes (perceived scale ≈ 4.6 mm ÷ pupil).
7. **Balance:** camera white balance near the key's CCT. A saturated accent emitter stays hot; don't warm the whole frame.

Every emitter goes in a light group (key, rim, fill, world, practical) so the groups sum to the beauty. Apply the steps
cumulatively on one frame and measure after each, to see what each buys.

Don't rebalance widened sources on the product's p90 key luminance: the glossy highlight spreads, and the lights get
boosted by about 3 stops.

## 3 · Grade targets (low-key)
Measured on film frames; use as diagnostics.

| Metric | Target |
|---|---|
| L1 / L5 | 1.5–4 / 2.5–6 |
| L50 | 8–20 |
| L99 | 50–80 |
| Zones <10 / 10–30 / 30–70 / 70–90 / ≥90 | ≤ 40 / ≥ 30 / 15–30 / 0.5–5 / ≤ 0.5 |
| Crush | ≤ 1 % |
| C\*99 | ≤ 40 with emitters |
| C\* in shadows / mids | ≤ 8 / ≤ 15–18 |
| a\* / b\* | ±2 / 0 to +5 |
| Grain σ at mid-grey | 1.5–3 codes |

Other rules:
- **Display rendering:** not PBR Neutral for finals; its toe squares values below scene 0.08 and crushes blacks. A
  per-channel film curve sends hot emitter cores orange → yellow → white like film; starting values for low-key: grey
  out 0.12, contrast 1.15–1.35, toe floor 0.0025; chroma: Oklab s = C/L knee 0.12 → 0.22, sat 0.8–0.9, highlight
  desat 0.35. (On sunlit colour, carry chroma through a luminance curve instead: §8.)
- **Diagnose per frame, don't guess:** a numpy twin of the chain, grid-searched on exposure, WB, sat, contrast and light
  group gains against these ranges, shows how far a frame sits from them and in which direction. Fix what it finds in
  the light.
- A frame lit mostly by its own emitters can't meet the mid-chroma target. Compare it with night film references
  instead (measured: C99 ≈ 47, ~63 % deep shadow).

## 4 · The Resolve Studio pipeline (verified end to end on 21.1)
**Scripting:**
- External Python: set `RESOLVE_SCRIPT_API` / `RESOLVE_SCRIPT_LIB` / `PYTHONPATH`; `DaVinciResolveScript` then loads in
  a venv, numpy included.
- The built-in MCP (File › Setup AI Assistants) wraps the same API (13 tools, 60 s per script). Saved scripts are
  better for repeatable work.

**Pipeline:**
1. **Blender → EXR.**
   - Each light group denoised in the compositor with albedo/normal, 32-bit ZIP.
   - The main EXR keeps all passes (32-bit ZIP).
   - The denoised groups sum to the beauty within 0.5 %.
2. **Plates.**
   - Lens optics only (PSF glare, veil, CA and distortion, vignette; `camera-post.md`) plus ~0.65 px softness, applied
     **per layer**. That is exact because optics are linear: lens(Σgᵢ·LGᵢ) = Σgᵢ·lens(LGᵢ).
   - Write:
     - a plate EXR (RGBA half PIZ), the Media Pool clip;
     - **one single-layer file per light group**;
     - a data EXR: Mist, Depth, Normal, Crypto, float.
3. **Project colour management, by script.** Set it in stages, reading each key back:

   | Key | Value |
   |---|---|
   | `colorScienceMode` | `davinciYRGBColorManagedv2` |
   | `isAutoColorManage` | `0` |
   | `rcmPresetMode` | `Custom` |
   | `separateColorSpaceAndGamma` | `1` |
   | `colorSpaceInput` / `colorSpaceInputGamma` | `Rec.709` / `Linear` |
   | `colorSpaceTimeline` / `colorSpaceTimelineGamma` | **`DaVinci WG`** (not "DaVinci Wide Gamut") / `DaVinci Intermediate` |
   | `colorSpaceOutput` / `colorSpaceOutputGamma` | `Rec.709` / `sRGB` |
   | `inputDRT` / `outputDRT` | `None` |
   | `colorSpaceOutputGamutMapping` | `None` |
   | `timelineWorkingLuminanceMode` / `timelineWorkingLuminance` | `Custom` / `10000` |

4. **Fusion comp:**
   - One Loader per light-group file.
   - BrightnessContrast `Gain` per group.
   - Merge `Operator=Over`, `Gain=0` (alpha gain), `SubtractiveAdditive=1`: a pure add of light.
   - FilmGrain with `LogProcessing=1`. `MasterStrength` 0.052 ≈ σ 2 codes at grey, with a film-like tone shape
     (−4 stops ≈ ¼ of mids).
   - MediaOut1.
5. **Colour page:** node 1 gets `Graph.SetLUT(1, "<folder>/<name>.cube")`.
   - The LUT (65³, installed under `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/<folder>/`) runs
     in timeline space: DI decode → DWG→709 → WB, exposure, chroma, film curve → display-linear 709 → 709→DWG → DI
     encode.
   - Output DRT None, so Resolve's output transform only encodes sRGB.
   - Accuracy: on real frames p99 < 1 code; chart ramp < 1 code.
6. **Deliver:** `tif`/`RGB16`, single-clip mode, MarkIn = MarkOut = item start. Resolve inserts `_` before the frame
   number when the name ends in a digit.

## 5 · Traps (each verified)
- **Import:** `MediaPool.ImportMedia([{"FilePath": ...}])` returns `[]` for single EXR stills. Pass plain path strings.
- **Scripted comp edits don't render:** tools added or wired live via the API show on the Fusion page, but the Color
  page and Deliver ignore them. **Save the comp and `TimelineItem.ImportFusionComp(path)`.**
  - A test that "matches identity" proves nothing until a deliberate change (a 4× gain) shows up.
- **MediaOut expects the clip's input space** (Rec.709/Linear here), not timeline-gamut linear as the manual suggests.
  An extra 709→DWG CST desaturates every colour (a saturated orange loses about a third of its chroma) while greys stay
  exact. Loaders of Blender linear-709 EXRs go straight to MediaOut.
- **Loader EXR layer selection is ignored when set by script:** `BaseLayerName` and `Clip1.OpenEXRFormat.RedName`
  ("lg_key.R" etc.) all read the first layer, so N groups give N× the beauty. Write one file per light group.
- **File names:** Fusion treats trailing digits as a frame number (`chart_lin709.exr` → frame 709). Harmless for
  stills; avoid for sequences.
- **Checking a render without the UI:** `Timeline.GetCurrentClipThumbnailImage()` returns the Color-page image (base64
  RGB 8-bit).
- **`SetFusionOutputCache`** rejects every value tried. It isn't needed with the import route.
- **Colour-page limits:** the API can't add nodes or set OFX parameters. Put the look in a LUT/DCTL, per-frame values in
  per-frame LUTs, and OFX in Fusion (`ofx.com.blackmagicdesign.resolvefx.*` via `SetInput`).
- **Clip label:** the clip shows "Input Gamma: Rec.709" even with the project input Linear. A ramp proves Linear is used.
- **A comp file Resolve can't parse imports as an EMPTY comp, silently, and the plate renders straight through.**
  - Example: a line added after a block's final `Version = 1`, which has no trailing comma.
  - Symptom: every delivered frame equals its "all gains = 1" twin.
  - Fix: make the comp writer add the missing comma; re-parse before import.
- **Rebuild each item's comp from a fresh `AddFusionComp()`, and delete every other comp after the import.** With two
  comps present, Resolve renders the live-built one, whose edits it ignores: a pass-through.
- **Verify every delivered frame against its twin** (L50 within ±1.5). This catches both failures above at once.
- **Any solver needs credible bounds:**
  - ±1.5 EV, room ≤ 8×, 4500–7500 K, contrast 1.05–1.4;
  - highlight targets (L99, ≥ 90 zone, clip) weighted softly: they come from film frames, and glossy speculars
    legitimately exceed them;
  - unbounded, a solver will drop exposure several stops and multiply the room to hide one specular.
- **Emitter-lit night frames** need night targets (from night film references). Low-key targets light up the room and
  kill the beat.
- **Computer-use screenshots of Resolve** fail ("audio/video capture failure") while the display sleeps. The API and
  render measurements keep working.

## 6 · Verify the plumbing on every new setup
Push a linear chart (a 17-step grey ramp from −10 to +6 stops, plus colour patches) through an identity LUT: grey must
equal sRGB(lin) within 1 code. Then through the look LUT, compared with numpy.

## 7 · Daylight and normal-key targets (measured on 15 reference photographs)
Low-key film targets (§3) don't apply to a calm daylight product. The median is set by walls and sweeps, not by the
product, and a product's matt black sits at **L\* 18–28**, not 2–6 (a museum photograph of a black product measured 22).

| Regime | L50 | L1 / L5 | Crush | Clip | C99 | Cast b\* |
|---|---|---|---|---|---|---|
| Interior daylight (a room in frame) | 55–70 | 2–10 / 8–22 | ≤ 0.2 % | ≤ 2 % (window only) | ≤ 45 | +2…+6 (slide warmth) |
| Studio light sweep | 75–85 | 10–20 / 18–30 | 0 | ≤ 1 % | ≤ 20 | ±1 |
| Studio dark graded sweep (a catalogue hero) | 35–45 | 2–4 / 3–6 | ≤ 0.3 % | ≤ 0.3 % | ≤ 10 | −3…+1 |
| Macro on a black product | 20–35 | 1.5–4 / 2.5–6 | ≤ 0.3 % | ≤ 0.3 % | ≤ 30 | 0…+3 |

- **Starting values:** day: WB 5500, sat 0.92, film grey 0.13, contrast 1.15, floor 0.003; dark: WB 5600, contrast
  1.25.
- **Judge each frame by the regime it actually shows.** A macro that is mostly black product sits near that surface's
  own floor however it's graded; a detail filling the frame is a macro, not an interior. A grade can't add contrast the
  light doesn't have.
- **Negative fill is part of daylight realism.** In a white room glossy black lifts to grey. Photographers flag above
  and beside the product; in Cycles that is a flag the camera can't see but the product reflects.

## 8 · Reference-matched look, "gentle": keep the render's light, borrow the reference's colour
**Verdict.** On warm, motivated light (low sun through windows), a bounded solver toward absolute targets costs the
frames their light quality. Measured on golden-hour KEYs, it lifted blacks to L* 3–5 (the milky look), pushed exposure
up on most shots, turned warm light redder, bleached sunlit surfaces, neutralised the sun's warmth and left visible
noise.

**The replacement:**
- Keep the render's own light: EV 0, no white balance (a low sun stays warm).
- A film curve on luminance with the reference's floor (L* ≈ 1.5) and a cream print white (L* ≈ 95).
- Carry each pixel's colour through the shoulder, or sunlit highlights wash to cream ("washed-out highlights").
- A near-neutral trim so lit greys don't go sepia.
- The reference's colour-light (e.g. teal-black → olive shadows → gold mids). Restrict a warm-shadow pull to warm hues
  (≈ 20–150°), or cool blue-grey reflections flip to teal or red.
- Highlight chroma soft-limited so amber can't go neon.
- No statistical colour transfer.

**How to work on it:** single KEY frames and cached EXRs only, with checkpoints every ~30 min. Freeze every shipped
version under a name and never edit one in place; an overwrite makes a reviewed version unreproducible.

**LUT for Resolve:** a 65³ cube reaches ~0.7 codes mean error (p99 ~2.5, measured). Port it to a DCTL if Resolve must
match to the pixel.

**Character on top:** `camera-post.md`, "Film character on finished EXRs".
