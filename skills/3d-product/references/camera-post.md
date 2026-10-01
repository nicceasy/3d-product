# Camera realism in post, emitters that look real, film character

A real camera leaves fingerprints: diffraction, glare, lens geometry, sensor noise, grain. A render has none, and
that absence reads as CG. This file is the physically correct way to add them, plus how emitters must be built to look
like real electronics.

## The chain, in the order a photon meets it
Work on the scene-linear EXR, never on a display image.

**Optics:**
1. One FFT convolution combines three terms:
   - a spectral diffraction PSF tail: |FFT(iris)|² at ~31 wavelengths, binned to the sensor pitch;
   - veiling glare: a glare-spread kernel with η of 1–2 % for a modern lens and 4–8 % for a vintage one;
   - the anamorphic streak, if the lens is anamorphic.
2. Ghosts mirrored through the centre, for very bright sources only.
3. Distortion and lateral CA, applied in a single remap.
4. Vignetting: cos⁴ multiplied by an optical term.

**Sensor:**
5. Exposure.
6. Optional film halation.
7. Per-channel soft clip.
8. Poisson–Gaussian noise: shot noise plus read noise, grain growing with the square root of the signal.

**Display:** a hue-preserving view (Khronos PBR Neutral) is fine for look-dev of emitters. **For finals, apply the
optics only, per light group** (optics are linear, so the sum is exact), then the film curve and grain
(`finishing.md` §1, `realism-finishing.md`): PBR Neutral's toe crushes low-key blacks.

Measured: a few tenths of a second per frame at 960 px, several seconds at 4K on a laptop CPU; a correct glare step
conserves energy within 0.3 %.

**Don't use the compositor's Glare node for this:** its Streaks and Star add 120–170 % energy; real spikes hold about
2 %. Spike count is n for an even number of blades and 2n for an odd number; rounded blades kill the spikes.

## Lens characters: match the render camera
The iris is baked into the render (bokeh shape), so the post lens must describe the same lens: the same blade count,
the same anamorphic ratio, the same f-number.

| Character | Iris | η (glare) | Streak | Use |
|---|---|---|---|---|
| Clean product | 15 rounded blades, f/8 | 0.6 % | — | packshots |
| Modern cine | 13 rounded blades, f/2.8 | 1.5 % | — | default for storyboards and macro |
| Vintage | 6 straight blades, f/5.6 | 6 % | — | hexagonal bokeh, starbursts, character |
| Anamorphic | 11 blades, ratio 2, f/4 | 3 % | blue, faint | oval bokeh, night, futuristic |

Previews at 960 px show only about ¼ of a 4K starburst tail. That's correct, not a bug.

## Physical camera rules
- **Place the camera at the lens's real working distance.** Then focal = 36·dist/field, and f-number = focal /
  entrance pupil. A short-distance pinhole camera gives wide-angle perspective and absurd blur: it reads CG.
- **Macro depth of field is a fraction of a millimetre.** Put the focal plane on purpose, across one feature (one row
  of holes, one line of text, one face).
- **Renderers don't simulate diffraction.** Cycles (and Octane's thin lens) render f/28–f/32 macros razor-sharp; a real
  lens at N_eff 40–55 (N_eff = N(1 + m)) is diffraction-limited. The first dark ring (2.44·λ·N_eff) overstates what you
  see: the Airy MTF at 1080p Nyquist equals a geometric disc of d = N_eff/24 px. Gate the named subject at
  √(CoC² + d²) ≤ 2 px and pick the N at the minimum (`fkl-frames.md`).
- **Practicals for bokeh** are placed emissive spheres, warm, in the part of the background the camera actually sees
  (with a camera looking down, that's *below* the product's base). Near glossy set pieces make them invisible to glossy
  rays, or they mirror into big streaks.

## Emitters that look real
- **Set emitters by luminance ratio to the key**, not by watts. Emission S renders as pixel S.
- **Look-dev: PBR Neutral** keeps saturation; AgX desaturates and hue-shifts emitters. **Finals: the film curve**
  (`finishing.md` §1): hot emitters must go orange → yellow → white as on film (ARRI / 2383 print); hue-preserving
  views turn them salmon or pink, a CG tell.
- **Structure:** flat emission looks fake. Build the real part:
  - an edge-lit light guide: brightest at the side-fire LEDs (angular Gaussians plus a floor), an etched-dot extraction
    texture, over a clear or smoked lobe;
  - glass-pixel domes; LED dies behind diffusers;
  - light through invisible micro-holes as soft dots on a dark, blasted metal field.
- **Spill, glare and haze** carry the colour. The core clips; the halo, the floor reflection and the haze stay saturated.
- **Light linking** only with a physical reason (`realism-finishing.md` §2): a product-only strip without it paints the
  base as well, or, linked, leaves the set unlit. Tag set pieces (bases, walls) so links can target product vs set.

## Dramatic futuristic grammar
- low key, 8–16:1;
- one moving light;
- one accent colour covering ≤ 10 % of the frame;
- practicals 3–6 EV over the key;
- haze τ 0.05–0.15;
- a macro plane of focus across one feature;
- a dark base (black, or honed stone);
- far warm practicals as bokeh.

Shot types: macro razor-DOF detail, low-angle hero, silhouette against an emitter, reflection shot, light-reveal sweep,
through-glass shot, extreme foreground bokeh framing.

## Film character on finished EXRs: denoise → mist → grain
Applied to converged, finished EXRs, after the render and before delivery.

**Chain:** colour-only denoise → lens (optional) → edge softness / mechanical vignette (optional) → halation (optional)
→ mist → colour look (a frozen, named version) → grain.

**Denoise.** OIDN colour-only (Blender's compositor used purely as an image processor, about 1 s/frame), only on noisy
*converged* frames.
- Measured: render noise from a few codes to ≈ 0.1, with no boil in motion (frame-to-frame change went down).
- Flicker blamed on "the denoiser" comes from in-render denoising at low spp, not from a colour-only pass on converged
  frames.
- An in-render AI denoiser (Octane's) left speckle and blotchy mottling on dark lacquer and dark plastic at 256–512 spp
  where post OIDN on the raw beauty was clean: post OIDN is the default for both engines (`finishing.md` §1).

**Pro-Mist-like diffusion.** Energy-conserving: a fraction s of all light is scattered into a wide halo.
- 1/8 is s 0.04; 1/4 is s 0.08.
- It costs no highlight chroma.
- It does lift blacks (measured: floor L* +1.3 at 1/8, +2.5 at 1/4). "1/4 held" drops the widest veil: the glow of 1/4
  with the black lift of 1/8.

**Grain.** Display domain, fresh per frame (seed = frame), blue coarsest, strongest in the mids, floor-protected.
- 35 mm fine-like: σ 1.0–1.7 codes at 0.43 px.
- Coarser (matched to a scanned film reference): σ 1.4 at 0.83 px.

**Grain vs delivery (measured σ loss).**

| Grain | Loss at 16 Mb/s H.264 | Loss at 8 Mb/s |
|---|---|---|
| Fine 35 mm | 35 % | 58 % |
| Coarser | 11 % | 46 % |

Deliver ProRes, or H.264 ≥ 40 Mb/s, or use the coarser grain for streaming; re-measure σ after the real encode.

**Add-ons.**
- Halation at 0.04 is invisible; 0.3 shows as a thin orange fringe on bright rims.
- A lens pack (CA ~1.5 px, vignette, edge softness) at 85–135 mm reads mainly as vignetting: keep it off by default.
