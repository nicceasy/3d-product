# Glass, light and colour: physics first, the right kernel, caustics as a layer

How to design, model, light and render glass, lenses, translucent plastics, gels and caustics for any product. Each
item: the principle, why, and how.

Contents: 1 Research · 2 Concept · 3 Modelling · 4 Pipeline · 5 Materials · 6 Lighting · 7 Kernels ·
8 Passes & comp · 9 Camera · 10 Heroes & story · 11 Rubric

---

## 1 · Research before rendering
- **Three tracks in parallel:** optics & modelling, imagery & judging, rendering & caustics. Each is told to *measure on
  this machine*, not just read, and to deliver a labelled contact sheet plus a decisions list.
- **Why:** the facts that decide the pipeline are cheap to find and expensive to discover in look-dev:
  - Cycles (5.x) has **no dispersion**;
  - MNEE finds only part of the caustic energy (measured ≈ 37 % on a ball lens);
  - clamping, Filter Glossy and OIDN all eat caustics;
  - high-dispersion glass (SF11) and crown glass (BK7) behave very differently;
  - cemented doublets should be fused into one solid.
- Research agents' throwaway environments are large (several GB): clean them up.

## 2 · Concept: physics first
The cheapest step in a glass project. Physics can change a product before a single render.
### 2.1 Ray-trace the real optics
- A 2-D sequential tracer is enough: spherical surfaces + Snell, indices from nd/vd (Cauchy) or Sellmeier for the named
  glasses, rays launched as a brute-force pupil fan (keep the rays that clear every aperture).
- **Draw rays additively per wavelength** (white-on-black layers per λ, added in linear light): agreement reads white,
  separation reads as colour. That is the residual colour the camera should show, and a board diagram for free.
- Check the model's focal length and back focus against the prescription.
- Limits: 2-D (meridional) only, and it ignores supports: trace the product *on its stand*, not on the table.
### 2.2 "Does the product work?" checks
- Lensmaker + thin-lens equations before modelling further. An object inside f can never project: a projector's slide
  must sit just beyond f, and its focus travel follows from the throw range.
- Ball lens: EFL = nR / 2(n − 1). It sets where the focus lands (a stand or cup height, a caustic on the table).
### 2.3 Predict caustics in 2-D
- Histogram where traced rays hit the table → an irradiance strip. It shows which design concentrates light: measured,
  a thin blown shell ~1.7× open light versus a solid ball 2.7×, rising to ~35× at the key angle that focuses on the
  table. Choose the design and the key angle from this, before rendering.
### 2.4 Colour as data: OKLCH gels and Beer–Lambert
- **Gels:** pick in OKLCH (e.g. L 0.80, C 0.13), keeping the lowest RGB channel ≥ 0.05 so no channel dies.
- **Tints:** invert Beer–Lambert, σ = density·(1 − colour), to a tint + density for the target colour at a given path.
- Expect ~0.90 × the planned transmission through a slab: the missing 10 % is Fresnel at two faces (n ≈ 1.59).
- **Plan tinted colour at the viewing path, not face-on.** A 2.4 mm wall seen obliquely is ~9 mm of material; edges and
  oblique walls are longer paths and drift the hue (an orange planned face-on reads salmon).

## 3 · Modelling (B-rep)
- **Prescription-driven lenses:** each element's half-profile = an arc per spherical surface (a line for flats), a flat
  step to the element OD, revolved about the axis. **Fuse cemented pairs into one solid** (their Δn is tiny); draw the
  cement as a thin dark ring. A half-space intersection gives the cutaway.
- **Optics-driven dimensions:** a stand height from the back focus; a slide at its projection distance; a prism
  rotated to minimum deviation (a fixed model can totally internally reflect the beam: solve the angle).
- **Glass-safe internals:** keep parts ≥ 0.6 mm from glass walls (no coincident faces); make shells by offsetting the
  outer surface by −wall.
- **OCCT / build123d traps:**
  - a fillet on a sphere/cylinder lip fails: leave it sharp;
  - check a biconvex lens's edge: CT − 2·sag > 0, or the edge thickness goes negative;
  - `Triangle()` can raise a TopoDS mismatch: use a Polyline;
  - an over-fine export tolerance (0.002 mm) bloats the mesh file tens of MB for nothing.

## 4 · Pipeline
- **Tessellation:** refraction magnifies normal error. Glass ≤ **0.05 mm** chord (0.2 mm saws the refracted rim band;
  1 mm shatters it). Render time is flat; only file size grows.
- **Bounce budget:** bounces ≥ glass surfaces the ray crosses for the image (12 carries a 10-surface lens); **2–3× the
  surfaces for the internal reflections** that give a lens its layered depth (the extra bounces change well under 1 %
  of pixels, all inside the glass). A high default (64) costs nothing where unused.
- **Lint every glass part:** no non-manifold edges; signed volume positive (closed, outward normals). Orient a closed
  glass mesh's faces by ray parity, not by recalculating normals: measured once, a closed vase with 21 % inward faces
  fireflied, a normal recalculation fixed none of them and a ray-parity pass fixed them all.
- Describe the scene as data (lights with Kelvin, gobos, cookies, cards with refraction-target patterns, walls, haze,
  explodes, light groups) so the same spec can rebuild the scene in a second engine (§7).

## 5 · Materials
| Approach | Result | Verdict |
|---|---|---|
| IOR ladder 1.33 → 2.15 on a ball | higher n = shorter focus = smaller inverted world; the upper half turns to reflection | IOR is a composition control on spheres, not a look knob |
| Thin film (Principled Thin Film) 0/100/140/200/300 nm | neutral · magenta-violet+amber · blue+orange · yellow-green+blue · magenta | mix per element = "multicoated"; legible only with a broad dim source filling the element (macro) |
| RGB-split dispersion (3 Glass BSDFs at Cauchy IORs) | red/blue fringes on edges | fringes yes, spectra no (use a spectral engine, §7) |
| Tint by Base Color vs Volume Absorption | Base Color = cellophane (thickness-blind) | always volume |
| Frost (roughness 0 / 0.12 / 0.3) | satin makes colour *richer* | 0.12 for "premium translucent"; 0.3 is a lamp shade |
| Dichroic film (n ≈ 2.2) | reflects one colour, throws the complement | needs a big source; a small light gives black shadows |
| Seeded glass (a faint Volume Scatter inside the glass) | makes light *inside* clear glass visible | pair with a light inside the glass (§6) |

Common IORs: 1.49 acrylic · 1.52 crown/K9 · 1.585 polycarbonate · 1.78 SF11 · 2.15 cubic zirconia.

**Roughness is a per-state trade.** Render each glass cover in each light state at its closest framing.
- Mirror-smooth glass in sun flickers: keep roughness ≥ ~0.03 where sun refracts through it.
- A rough cover over a bright environment (a night window, a sky) turns that source into grain in every pixel behind
  it (measured once: it held a frame at a 4× higher sample cap until the source was moved out of the cover's view).
- Fix the source first: rotate the environment or flag the bright area out of the cover's view (`lighting.md` §6).
  Change the cover's roughness only with the user's OK: the material is the design intent.

**Every glass layer, in every light state.** List each transparent material's layers (a thin pane, a milky or diffuse
layer and its weight, a mix's input convention) and check each in every state: a 2–5 % milky layer invisible by day
can carry most of a night pane's light (`lighting.md` §9.3). A layer a state needs differently is a state value, not a
second master (`lighting.md` §3).

## 6 · Lighting
- **Surroundings are the lighting for glass.** Field lighting:
  - dark field: bright rims on black (a big panel hidden by a black patch sized from the camera frustum ×1.08);
  - bright field: dark edges on white;
  - **gradient ground:** one card bright at the floor fading up, so the glass draws itself.
  A metal rig (big soft cards) makes glass vanish.
- **Gels on black metal:** black anodising only shows what it reflects. Gel the rims (e.g. teal h200 / magenta h330 at
  OKLCH L 0.80 C 0.13), keep the key white, keep the floor dark (an overlit floor turns black metal silver).
- **Additive RGB keys** (120° apart, wide cones): white overlap, CMY shadows. Maximum colour, colourless product.
- **Temperature contrast:** 2200 K vs 12000 K is a palette without gels.
- **Gobos vs cookies:** a textured spot (gobo) is sharp everywhere and reads as projection. A physical cookie has a
  real penumbra = source size × (cookie→surface ÷ light→cookie): use a small source and a cookie near the product, or
  the pattern vanishes.
- **Haze** (opt-in, for a beam the story needs, with its cost measured: `lighting.md` §2): a Principled Volume box;
  side-on cameras need anisotropy ~0.25; keep fills out of the volume.
- **Glass sampling aids per state.** Fake or transparent shadows help convergence, but on an open cover in sun they
  let direct light through as if the glass weren't there. Keep an aid only where a with/without preview agrees within
  ~3 %, per cover state × light state (`lighting.md` §8).
- **View transform:** for look-dev, Khronos PBR Neutral keeps gel saturation (AgX pastelises, Standard clips, ACES 2.0
  sits between). For low-key finals use the film curve (`realism-finishing.md`, `finishing.md`) and check saturated
  gels through it: a per-channel shoulder moves bright saturated colour toward yellow/white.
- **Light inside glass (a labelled cheat):** a small LED inside a solid glass body is unreachable by path tracing
  through the glass. Put a spot *inside* the glass aimed where the glow should be, in seeded glass: a warm column in a
  clear body. Label it as a cheat.

## 7 · Kernels & caustics
**Principle: Cycles for glass seen by the camera; a light-tracing engine (LuxCore) for light passing through glass onto
the world. Composite the two.**
- **Bridge:** export the geometry (PLY) + the scene spec (lights with Kelvin, camera) and rebuild the scene in LuxCore
  with matched materials (glass → `glass`/`roughglass` with Cauchy A/B + thin film; tint → `clear` volume; scatter →
  `homogeneous`; floors → `glossy2` F0 0.04 to match Principled). Direct light then matches Cycles within ~2 %
  (measured).
- **Caustic in a shadow (measured against a reference):** Cycles PT with a small light finds ~20 %; a bigger light
  (60 mm) ~55 % but softens every shadow; MNEE ~45 % (right shape, crisp ring); LuxCore PATHOCL + hybrid close but
  grainy at equal time; **LuxCore BIDIRCPU closest, ~20 % error at 40 s**.
- **Spectra:** Cycles RGB split puts nothing on the wall; a spectrum gobo is an art-directed cheat; **LuxCore with
  Cauchy glass renders the real spectrum where the solver predicted it**, plus the ghost spectrum from one internal
  reflection. Note: Cauchy A ≠ nd.
- **Projection through optics:** LuxCore forms a gobo's image through a modelled lens; Cycles leaves the wall empty.
- **A light behind glass:** a bare Lambertian LED makes the body glow like opal in LuxCore (honest). A collimated source
  seen through glass is specular–diffuse–specular: every kernel fails, bidirectional VM included. Cheat it (§6).

## 8 · Passes & comp
- **Hybrid caustic layer:** A = Cycles (caustics off, passes on); B = LuxCore − A, masked by Object Index to
  floor-in-shadow (the kernels disagree slightly at spot edges), blurred 1.5–2.5 px; out = A + k·gel·B. Caustics
  become gradeable.
- **Light groups as gels:** render white lights in groups and recolour in numpy: exact (< 1/255), colourways in a
  fraction of a second.
- **Bloom only where earned:** threshold linear > 1.0, blur 3/12/40 px, k ≈ 0.25–0.35.
- **Beam as a pass:** volume direct/indirect passes; out = Combined + (k − 1)·Volume makes beam density a slider.

## 9 · Camera
- **Bokeh through glass:** coloured lights behind a glass sphere at f/1.8: the ball re-images them near the focal plane
  (a sharp inverted bokeh field inside a soft one). 9 blades = nonagons.
- **The product's own lens profile:** a chief-ray trace of its prescription gives distortion, lateral colour and
  relative illumination vs image height; apply it in scene-linear before the view transform.

## 10 · Heroes & story
- Heroes combine each phase's winner; frames with light through glass are hybrids (§8). A 3-D ray diagram (a cutaway
  lens in haze, coloured lasers converging at the focal plane) needs light tracing.
- Story grammar for a light product: black open → edge reveal → mechanism → physical proof (the beam in haze) →
  payoff (the only saturated frame, e.g. the spectrum) → hero with a neutral anchor → end card. **Withhold colour until
  the light earns it.**

## 11 · Glass & colour rubric
Measure every frame:
- clip % (blown / crushed);
- neutral % (OKLCH C < 0.03): ≥ 20 %;
- hue families (30° bins holding ≥ 10 % of chromatic pixels): 1–2;
- hue spread (chroma-weighted circular std): ≤ 25° inside a family;
- fireflies per megapixel: < 5;
- light share (energy in the brightest 2 %): packshot 3–10 %, story 20–45 %;
- edge contrast (95th percentile OKLab-L gradient).

Read the numbers with the brief: a white ground is "blown" by design, a night frame "crushed" by design.
