# Environments around the product: choosing, construction approaches, light

> **Use this file to *choose* an environment; build it with `alive-environments.md`.** Sets built from the construction
> recipes below alone read as CG: no history, flat procedural surfaces, rims and key twins with no source, centred
> products, arbitrary camera heights. The choosing (claim, honesty filter, extravagance index, reflection plan), the
> image-based facts and the lighting units hold; the build process is `alive-environments.md`.

## 1. Choose the environment before building it
1. **Claim first, set second.** Write the claim in one sentence ("it belongs in a designer's home"). Reject any set
   that claims something else. The **honesty filter**: no set may imply a feature the product lacks (waterproof,
   portable, wireless, new). A mains-powered, non-sealed product outdoors or in a splash claims both.
2. **Rate every candidate on the extravagance index.** Score six criteria 0–3 and sum them:
   - competition with the product,
   - prop density,
   - chroma,
   - motion,
   - fantasy,
   - cost.

   The sum sets the level: 0–2 = L1, 3–5 = L2, 6–8 = L3, 9–11 = L4, ≥ 12 = L5. Subtlety is about how much the set
   *competes*, not about cheapness: macro is L2. Colour, fantasy and motion push a set up the scale fastest.
3. **Spread the levels.** Pick at least one L1 anchor, several L2–L3 sets, and one or two L4–L5 sets. Give every pick a
   different construction method, so the set also compares methods.
4. **Write a one-line brief per pick:** the claim, the light logic, and the **reflection plan**. Any glossy or dark
   surface carries the set on its skin, so design what it reflects first (e.g. a smoked or black gloss cover is a dark
   mirror).
5. **Keep the product's chroma.** The set stays neutral or borrows only the product's own accent colours (an accent on
   a control can become the set's architecture colour or a print on the wall).
6. **Thumbnail test.** The product must still read at 128 px wide. Keep ≤ 3 prop types on a tabletop and ≤ 1
   statement object in a room. Add one scale anchor: an everyday object of known size near the product's own size.
7. **Match the channel:**
   - marketplace: RGB 255 silo at ≥ 85 % fill;
   - hero banners: ≥ 30 % copy space;
   - social: 4:5;
   - OOH: bold crop.

   Render the silo and the moods from the same model and pass.
8. A **fantasy needs a reason taken from the product**: a product feature becomes the world (grooves become ripples;
   calm becomes an impossible architecture). Borrowed spectacle reads as costly signalling.

## 2. Construction approaches and what transfers
One set per approach, L1 (catalogue) to L5 (surreal); each lesson below was verified in renders.
| L | Approach | Light | What transfers |
|---|---|---|---|
| 1 | studio as code: graded cyc, overhead scrim *behind*, rim strip, flags, low front fill | scrim + rim | a dark cove needs a real bright gradient in the render: grading can't create a zone the light didn't |
| 1 | orthographic top view, covers hidden | one large source (~1.4 m) 45° **off the gloss's mirror angle** + a weak opposite fill | on the mirror angle black lacquer goes grey |
| 2 | gallery: plinth, wall, shadow gap, flush caption card; microcement + limewash | 3500 K spot at 30° from vertical, 4000 K wall grazer, 5200 K skylight | 3000 K everywhere reads brown; a neutral skylight fixes it |
| 2 | macro world on the detailed model (e.g. 60 mm f/4 at 23 cm) | a strip along the part, a rim on its end, void | macro only pays if the model is detailed (`reference-detailing.md`) |
| 2 | **HDRI only** (no lamps) + one modelled table | the map's own windows, rotated to camera-left | the cheapest honest daylight; frame so the table hides the HDRI floor |
| 2 | stone slab, wood body, modelled props | window spot through a leaves gobo, low fill | a soft gobo reads as bands; sharpen the edges for dapple |
| 3 | modelled period interior + window plate | window as key | the period-interior anchor |
| 3 | modelled glass pavilion (thin-glass panes) around an outdoor HDRI | the landscape through the glass | mullions *between* product and camera axis, never behind it |
| 3 | limewash alcove, round window, bench, haze | a sun aimed by geometry: window centre → a point on the product | haze σ 0.15 m⁻¹ is invisible at alcove scale, 0.35 reads; forward-scatter g 0.6 hides the beam from a side camera |
| 4 | abstract B-rep kit: arches, sphere, stepped plinth, filleted-L cove | hard sun + sky fill | a thin cylinder cove seen from inside renders black: use a filleted L block |
| 4 | emissive strips swept during the shutter on black gloss | the moving strip is the reveal | the motion rig renders at +deg and sweeps ±deg/2: place rest angles for that |
| 4 | night apartment: 3000 K lamp (point + emissive linen shade + a labelled key twin), indicator lit, blue-hour HDRI through thin glass | practical +2 to +3.5 EV over its pool; daylight WB keeps warm warm | the shade's rim must clear the bulb → product ray (bulb above the rim) |
| 5 | procedural black water (ripple normals) + caustic cookie spot + back strip | strip ≤ 2 W (grazing Fresnel 0.35–0.6 clips above); spot hidden from glossy | isolate lights one by one to find a mystery highlight |
| 5 | 360° panorama as world + Sun lamp at its sun + one modelled element | the map's low sun as a Sun lamp (≤ 10° off), 3000 K | no model water under an HDRI; frame along the map's corridor; upscale 2k maps |

## 3. Image-based recipes
- **Orientation (Blender, verified):** an equirect texel at u lights from azimuth φ = 2π(0.5 − u) (0 = +X, CCW). A
  Mapping Z rotation θ moves a feature at pixel azimuth α to world azimuth **α − θ**. Find the sun or window with
  Blender itself (imageio can't read .hdr): `bpy.data.images.load` → pixels → argmax of the upper hemisphere, and make
  a labelled preview strip with azimuth lines. Write down your camera rig's azimuth convention next to it.
- **HDRI only:** free to render and honest for daylight. The product must sit on a *modelled* surface framed so it
  hides the map's floor. Give the camera its own softened copy of the map through a camera-ray split (Light Path
  "Is Camera Ray" mixing a gain-adjusted, downscaled, Cubic-filtered copy); lighting and reflections keep the full map.
- **Modelled architecture around an HDRI:** walls, roof and floor are real, and the HDRI is the view and the light
  through the glass. Glazing is a thin pane (Transparent + Fresnel glossy, front faces only). Never use a Glass BSDF
  for windows: it blocks shadow rays and turns all window light into caustic noise.
- **Plates + catcher** need a matched HDRI + plate pair, which is rare for free. **Sun split** is for control (angle,
  light group, animation), not speed: measured 18–31 % noisier at 16 spp.
- **The HDRI ground trap:** the world is infinitely far away. A model water or floor plane under a map re-reflects the
  map's near objects into endless columns with no contact line. Either show the map's own ground, with the support
  running out of frame, or cover the whole lower frame with the modelled surface.
- **Angular size is fixed:** a near arcade in the map keeps its angular size at any distance. Frame where the map's
  composition works (along a corridor, into a gap), not where the product is.
- **Resolution:** a 2k map is soft past ~24 mm (texels magnified 3.5–5.6× at 28–50 mm). Use a 4k+ map, upscale with
  the seam wrap-padded (64 px left and right), or use a longer lens with real DOF.
- **Gaussian splats:** Blender 5.2 has no splat type (an add-on needs an install decision); Blender 5.3 has native
  splats.

## 4. AI recipes (retired)
Comfy and AI world / panorama passes left the pipeline; don't use or propose them.

## 5. Model-based recipes
- **Sets as B-rep**, one glb per set, named parts, materials attached by name in the spec. The working surface is z = 0
  under the product's feet.
- **Procedural materials** (texture-free, near-instant to build) cover abstract sets: limewash, terrazzo, microcement,
  concrete, stone, wood, linen, tile, ceramic, water (ripple centres, wavelength, amplitude, decay), a thin pane, a lit
  lampshade (linen + blackbody emission). For photoreal sets, prefer scanned materials (`alive-environments.md` §3).
- **Volumes:** a haze box σ 0.12–0.35 m⁻¹ for a visible beam in a small space. Denser isn't slower (shorter free
  path). g ≈ 0.35 for a side-on beam. Measured: biased volume ray-marching costs +15 % vs +32 % unbiased.
- **Caustics:** a procedural cookie on a spot (Voronoi distance-to-edge on warped UV) renders in seconds; MNEE through
  water measured ~6× slower and came out soft. Use the cookie for mood and LuxCore for true glass (`glass-light.md`).
- **Gobos:** a leaves gobo (noise through a smoothstep, tight lo/hi) and a caustic gobo skip the circular mask.
- **Motion blur on a spin:** parts spin about their pivot over the shutter; offset the rest pose by the rig's +deg.

## 6. Lighting that belongs to the environment (verified in Cycles)
- **Units:**
  - point and spot: E = P/(4πd²), and a spot cone does not concentrate power;
  - area: E = P/(πd²), and changing `spread` multiplies on-axis E (×42 at 30°), so re-meter after changing it;
  - sun: E = strength;
  - emission S renders as pixel S.
- **Exposure = log2(π/E_key)** puts an 18 % card at 0.18.
- **Black lacquer reads** when its mirror direction holds a large soft source: horizontal faces read the key, vertical
  faces read the floor. Aim the source 30–45° *off* the camera's mirror angle for a catalogue black.
- **Targets on a black product:** its main face at L\* 18–28 in daylight and studio, 8–18 low-key. The world is 0.5–2 %
  of the key. Keep reflections on a glossy top or cover in its rear third.
- **Museum:** spots 30° from vertical (this keeps the reflection off a glossy top), pool 3–10× the ambient, a wall
  grazer. Use neutral 3500 K spots with a 5200 K skylight, because 3000 K everywhere reads brown.
- **Practicals** sit +2 to +3.5 EV over what they light, must reflect *and* spill, and get their own light group. A key
  twin next to the lamp is allowed if labelled.
- **Coloured light keeps chroma only with highlights ≤ L\* 70.** Keep one neutral specular source. Neon cores clip
  5–7 stops, so the colour lives in halo and spill.
- **WB:** set it at the key's CCT, *except* golden hour, neon and warm practicals: use daylight WB there so warm stays
  warm. The ≥ 5° source rule is for artificial soft sources only. Sun, spots, bulbs and neon keep their true size.
- **Haze:** dense behind the product, τ ≤ 0.1 in front.

## 7. Finishing regimes
The finishing chain is `finishing.md` (lens optics per light group, a bounded solve against the beat's regime, the look
and film curve, grain). Regimes that environments add:
- **colour** keeps chroma where it is the point (C99 ≤ 55);
- **night** keeps warm practicals warm (b 2–10, L50 18–32);
- **void** is a black stage (L50 3–20, world locked);
- **highkey** is a bright haze;
- a product-filled top view is a **payoff** regime (product-dominant), not a light one.

The wrong regime costs more than any setting: a light regime on a product-filled top view added +1.25 EV and lost the
key colours; a dark regime on a black stage lifted the world ×6 until the reflection room showed as a grey wall. Lock
the world gain where the HDRI *is* the key.
