# Lighting: grey box first, motivated light, named states, a product that reads

One place for the lighting stage. Detail lives in: `realism-finishing.md` §2 (the lighting gatekeepers, measured),
`alive-environments.md` §6 (location light), `environments.md` §6 (units, museum, practicals), `elements.md` §1–3
(what each light says), `glass-light.md` §6 (glass), `animation.md` §6 and `greybox-animation.md` (light over time),
`scene-optimisation.md` §0 (the budget each stage is measured against).

Contents: 1 Order of work · 2 Motivated light by branch · 3 Light states · 4 Emitters · 5 The product must read (R7) ·
6 Reflections, flags and hot spots · 7 Light over time · 8 Lights that converge · 9 Light tells time (a film's day →
night) · 10 Measure and gate

## 1. Order of work: grey box first
1. **Grey box:** mid-grey clay (≈ 0.4) on everything except glass and emitters, so windows, glass covers and practicals
   still light the set and make bokeh. Keep printed marks as dark ink on the clay: prints are composition (plain clay
   frames print shots blind). Low resolution (960×540), ~8 spp + OIDN, persistent data: a couple of seconds per frame
   on a laptop GPU. Look at light *shapes*: patches, shadow bars, rims, the reflections in the glossy parts. Every
   emitter sits in its own light group from this first render, so level and noise can be read per light (§8).
2. **Beauty look-dev on single frames:** real materials at 960×540, one variable per image, captioned sheets.
3. **Calibrate energies on 3 frames before rendering 12.** First guesses at window and scrim energies can be several
   stops off. Calibrate only after the in-render albedo audit (`alive-environments.md` §10.2): albedo compounds through
   every bounce, so energies set on wrong albedos are wrong twice.
4. Name and freeze the **light states** (§3) before compositions: every later tool (composition search, FKL harness,
   production packs) keys them by name.
5. **Design for convergence while you place the lights** (§8), not at the final: the per-light noise budget, the
   hot-spot audit (§6) and seconds per frame per state go on the light-state sheet. Fixed later, each of these changed
   an approved look.
6. **Judge the light-state sheet with the product in its real materials** (§10). The reads gates can't be measured in
   clay: a clay product never voids.
7. **Materials and light are coupled.** Any material change after this stage re-runs the light-state sheet (reads,
   fills, levels, convergence).

## 2. Motivated light by branch
**Location** (`alive-environments.md` §6): only what the place would light.
- The sun is split from the sky map: clamp the map so the sun lamp owns the disc, and add a Sun lamp (0.5°, the real
  disc) within 10° of the map's sun. Aim it by geometry (window opening → subject) and check with an ortho plan render.
- Colour temperature follows elevation (rules of thumb: +10° ≈ 3300 K, +6° ≈ 2900 K, +4° ≈ 2600 K; higher afternoon
  sun ≈ 3500–4500 K).
- Windows are thin panes (front-face Fresnel gloss); refracting panes block shadow rays.
- **Haze is opt-in.** Start every light state without it. Add a volume only for a named job (depth separation in a
  wide, a beam the story needs). A/B it on the state's KEY and record in the state:
  - the visible gain;
  - the seconds per frame it adds;
  - its share of the noise (from the light passes);
  - the level it adds to dark finishes.

  Why: a volume can be the most expensive light in the frame and is often invisible in a room. Measured: a
  window-shaft beam ≈ 50 min per 1080p frame at defaults; a room haze added 0.02–0.11 to dark lacquer and 4–7 % of the
  night noise. Both were cut for render time. If kept in an interior: σ ≈ 0.006 m⁻¹ in a 10 m room (0.03 reads as
  brown fog); in Octane the environment medium at ~0.005 with its radius set per shot (`octane-production.md` §4–5).
- Practicals off by day; after sunset a lamp is in frame and is the key; lamps make pools, not washes. Build them to
  converge (§8): a point light buried in a shade spends most of its samples inside the lamp.

**Studio** (`realism-finishing.md` §2, `elements.md` §1–2): the realism gatekeepers, in priority order.
- No product-only light linking without a physical reason: keep the product key and add a **set-only twin at 25–30 %**
  (~4 % under a macro lens) for the pool, the contact shadow and the bounce.
- A **room at 0.5–2 % of the key** (an HDRI, or walls and flags), never world 0: glossy metal needs something to
  reflect.
- Sources ≥ 5° (strips ≈ 0.09 × distance, or 16–40 mm); practicals reflect *and* spill.
- Camera white balance at the key's CCT, except golden hour, neon and warm practicals (daylight WB keeps warm warm).
- Metal: large soft cards and white or black sweeps. Glass: dark field, bright field or a gradient ground, never the
  metal rig (`glass-light.md` §6). Black lacquer reads when its mirror direction holds a large soft source 30–45° *off*
  the camera's mirror angle; a white room lifts glossy black to grey, so flag above and beside it (camera-invisible
  negative fill).

## 3. Light states: name them once, use them everywhere
A **light state** is the full, frozen record of the light for a shot, so every tool and engine reproduces it exactly.
1. **Fields a state records:**
   - sun: elevation, azimuth, irradiance (W m⁻²), CCT, angular size;
   - sky / environment: which map, strength, tint, rotation;
   - practicals: which are on, power, CCT;
   - state-dependent emitters: indicators, screens, neighbours' windows, street lamps;
   - state-dependent material values: a window's diffuse layer, a cover's roughness, emitter powers (item 7);
   - camera: exposure and white balance;
   - cost: seconds per frame at the preview config and the convergence record (§8).
2. **Name by what changes:** daylight states by sun elevation (e.g. `s20` = sun at 20°, `s3` = 3°), after-sunset
   states by a dusk index (`d1`, `d2`, … deepening). The name alone tells the order in the day.
3. **One sun path for the film:** one azimuth track, elevation moving one way (§9). A small per-shot azimuth cheat is
   allowed only when logged.
4. **One state per shot.** The film's light arc advances with the acts (`shots-and-script.md` §2; a film that moves through the day: §9 below).
5. Store the table once (a JSON the scene builders read) and record it in the render packs of every engine.
6. Probe the states that matter before committing: a state where the sun is too high can turn black gloss grey; one too
   low may not reach the subject (§9.6).
7. **One master for every state.** A state may need different material values (a window's diffuse layer, emitter
   powers, a cover's roughness). Store them in the state record and let the builder or render driver apply them, so one
   master file serves every state. Why: masters split by state drift apart, and every later fix has to be made twice.
   Measured once: an outdated label rendered in one line, and the window glass behaved differently in the other.

## 4. Emitters
- **Blackbody for every practical:** lamps 2700 K (in Cycles, energy × 0.495 keeps a lamp's luminance when switching
  from white to 2700 K blackbody); a red indicator LED as a ~1400 K black body, set by luminance. Sun and sky are the
  only non-blackbody emitters (the rule that makes a Cycles → Octane port exact: the converter makes them black bodies
  on the Octane side).
- **Every emitter in a light group**, including emissive props added late, or the groups won't sum to the beauty
  (check the sum within 1 %). Denoise Cycles groups separately, in the compositor, with albedo and normal.
- Set emitters by luminance ratio to the key, not watts: practicals +2 to +3.5 EV over what they light. The core
  clips; the halo, spill and haze carry the colour.
- Emitters need structure (`camera-post.md`): LED dies behind diffusers, light guides, glyphs through micro-holes.
- **A lamp in a shade or fixture is built to converge** (§8): an analytic sphere at the filament, the shade as its own
  emitter, the fixture excluded from the bulb's light.
- **Things that glow but aren't lights** (screens, dials, decals, lit neighbour windows, emissive kit props) stay
  visible to the camera and in reflections, but leave light sampling (§8).

## 5. The product must read (R7)
Machine rules: `scripts/lighting_rules.json` (metric, thresholds with calibration, decision table, placement and power
formulas, realism constraints, engine notes); the check: `scripts/reads_metric.py`.

**On black gloss, three-point lighting happens in the reflections.** A lacquer face shows only what lies on its mirror
ray (the family of angles), so key, fill and rim are *bright things in the room the product mirrors*, not lamps aimed
at it. Lacquer reflects ~4 % face-on to ~9 % at 60°: for a black face to read as textured black (L* 18–28) the thing
it mirrors must be about as bright as a white card in the key light (face L* ≈ 21–32); a room surface at ¼ of the key
leaves it at L* 7–14, a hole. Choose a fill by its luminance and position, not by the illuminance it puts on the
product. A low sun behind the product is usually already the rim and top reflection for cameras facing it; what a
failing frame lacks is most often the front fill.

**"Reads" is two measured gates** (`reads_metric.py`, on the preview + object index + depth):
| Gate | Measure | Warn | Fail |
|---|---|---|---|
| R1 void | share of the frame that is product, L* < 10 and structureless (local σ < 1.5) | 0.20–0.30 | > 0.30 |
| R2 merges | share of the outline (background behind the product) with ΔL* ≥ 8 | < 0.40 | < 0.20 when the product is the main shape (whole, or ≥ 50 % of the frame) |
| R3 subject | the named part against its ring | ring ΔL* < 5 and rms < 5 (warn only) | — |

Mean or median brightness does **not** separate frames that read from frames that fail: **never fix a fail with
exposure.** Low-sun and dusk states fail most often, and so do macros with a large black face.

**Decision table: read where the void or merge is (void split by world normals from depth), add one light, re-measure:**
| Failure | Light | Placement | Ratio / CCT | Motivated in a room as |
|---|---|---|---|---|
| Void on vertical faces (a black front face) | bounce fill seen in reflection | centred on the face's mirror ray r = 2(n·v)n − v, d = 1–3 × face width; its *edge* across r for a gradient | mirrored surface ≈ a key-lit white; as illuminance 25–50 % of the key by day; CCT of what it bounces | a sunlit floor patch, a pale wall, paper, pale furniture: real diffuse geometry lit by the sun |
| Void on top faces (top-downs) | overhead / window in the family of angles | az = camera az + 180°, el = camera el, beyond the product; top-downs → the ceiling | as above | tilt so the window sits in the top's mirror ray; the beam's bounce or a lamp shade on the ceiling |
| Void under tinted glass (a surface seen through a smoked cover) | sun into the enclosure, or the cover mirroring the window | cover surface as the top rule | a pass through glass costs 2·log2(1/T) stops (T 0.3 ≈ 3.5): only direct sun reads through | rotate sun azimuth / raise elevation within the state so the beam rakes the surface |
| R2 merge (outline = background value) | rim or kicker, or a background light | rim 135–180° from the camera, 30–60° up; kicker 110–150° near edge height; in the edge's family of angles | rim 1–2 stops *over* the key at the edge (edge L* 50–80), never equal | a bright pane or sunlit mullion edge on the outline's mirror ray; a lamp pool or sunlit wall behind |
| Dusk void | the practical becomes the key; sky = cool rim; lamp bounce = fill | key 30–60° off axis, 20–40° up; **the shade** (0.3–0.5 m, 9–28°), not the bulb, on the face's mirror ray | key:fill 4:1–8:1; key 2700 K; rim = dusk sky | table and arc lamps, positions cheated per shot (fixed within a shot, matching any in-frame lamp) |
| Flat face (lit, one value) | gradient reflection + negative fill | move the source so its edge crosses the face; a dark object on part of the mirror ray | 1–2 stop gradient across the face | dark furniture as the black card |
| Wet / grey black (face L* > 35) | negative fill | a dark object on the face's mirror ray (camera side, above and beside) | back to L* 18–28 | dark furniture, a doorway; in Cycles a flag the camera can't see |

**Fills must be physically plausible, and measured.** An emitter shaped like a cloth or a sheet of paper in shade is
easily set 10–100× too bright, as bright as a white card in full sun: that is a fake, and it reads as one. Every fill is
a real surface lit by real light, and its radiance is checked in the frame's scene-linear EXR against local references:
- a white surface in sun ≤ ~1× a sunlit white card;
- a white surface in shade ≤ ~3–4× the local shaded surfaces.
**No emitters posing as diffuse objects.** When the mirror ray finds nothing bright enough, try in this order:
1. extend along the ray to a truly sunlit surface (a floor sun patch; a card facing the window just outside the
   product's shadow);
2. a small sun-azimuth cheat, logged;
3. a motivated practical at real power;
4. a slight camera change;
5. otherwise leave the frame physically true and flag it.

**Placement and power.** Source centre = face point + d·r; size to fill the face: s ≥ L·(D_cam + d)/D_cam; sources
≥ 5°, soft ≥ 28° (size ≥ half the distance). Classic fallback where reflection geometry doesn't decide (diffuse parts,
labels): key 30–60° off axis and 30–45° up, fill on the lens axis, rim 135–180° off axis and 30–60° up. Ratios: fill
1.2–2 stops under the key by day (25–45 %), 2–3 stops (4:1–8:1) for evening; rim 1–2 stops over the key at the edge.
Name the convention (the ASC's (key+fill):fill gives 3:1 for a 1-stop difference). Power (Cycles, Normalize on): disk
area P = ρ·E_key·π(R² + d²) with ρ = E_fill/E_key; sun E_key = sun W/m² · cos i (take the state's irradiance: it falls
steeply as the sun lowers); point E = P/(4πd²). Check ratios on a grey card through light groups, never on the
product's glossy p90.

**Realism constraints for any added light:**
- Every added light names its room object and takes its shape, size and CCT (sun by state, ~3700 K in late afternoon
  falling to ~2000 K at sunset; sky 6500–15000 K; lamps 2700 K; a bounce the colour of its surface). Never a 5000 K
  fill from the room side in evening light.
- Shadows agree with the key's direction, or the source is too soft to cast one (bounce fills ≥ 28° do that).
- No product-only light linking (the set-only twin rule holds); an added fill that lights the product's base lights the
  furniture around it too.
- **Never hide a light from glossy rays:** a light missing from the reflections is the most visible cheat. Hide from
  the camera only what would be out of frame anyway (Cycles: Camera off, Glossy on).
- Bounce cards are real geometry (off-white, albedo 0.7–0.8) lit by the sun, so they follow the key through states and
  time-lapses. Never an emitter shaped like a diffuse object; every fill passes the radiance check above.
- One change per failing rule, then re-measure. A large, cool, powerful fill from the room side is the classic failure:
  it turns a black front into a flat grey slab and still leaves a surface under tinted glass black.

**Octane parity** (`octane-production.md` §4): blackbody emission with Normalize on, Surface Brightness off (it
carries an extra 7/π), Double Sided off for cards; out-of-frame sources Camera Visibility off and Visible on Specular
on; one Light Pass ID per Cycles light group. There is no published W → Octane power factor: calibrate once (a 1 m²
emitter at 5000 K, 2 m from an 18 % card, linear EXRs; measured: Cycles 100 W reads ≈ 0.42 on the card; solve the
Octane power, re-check at 2700 K and 6500 K) and record the factor in the driver.

**Process:** plan each light state's lighting during the grey box (which faces void, where the fill and rim live). Run
`reads_metric.py` on the light-state sheet, with the product in its real materials on 3–5 cameras per state (§10), and
again on every FKL frame. A frame that fails R1 or R2 is fixed by light, never by the grade.

## 6. Reflections, flags and hot spots
- Reflections are the lighting for metal; surroundings are the lighting for glass. Design what a glossy or dark
  surface mirrors first (e.g. a smoked cover mirrors the window).
- Flag a reflection that hides the subject with a camera-invisible black card (e.g. a window reflection on a cover
  hiding the part behind it).
- A large dark glossy surface (e.g. a black disc or panel) mirrors a bright window at most daylight eye-level and
  three-quarter angles and reads silver: dusk or plan views keep it black (gate it unless that surface is the subject).
- Anisotropic sheen on a spinning part doesn't rotate with it (only printed detail and dust do); a rotating glossy
  panel sweeps its reflection at 2× its angle.
- **Glass covers stay in every shot, at their story angle.** Never remove or hide a cover (or any visible part) to
  clean a composition; change the camera. A cover reads only through an edge highlight or a reflection, so frame it
  from the front or a three-quarter front: audit every camera's azimuth off the product's front, and treat > 100° (a
  view from behind) as a fail unless the cover still reads in the frame.
- **A tinted cover needs something bright to reflect, or it vanishes.** Find its mirror ray per shot (the window, a lamp,
  a lit wall); at dusk and night a tinted cover becomes a dark mirror (`transition-shots.md` §3).
- A soft fill panel that a low-angled glossy cover can see reads as a milky band on the cover: make fills
  reflection-invisible, or keep them out of the cover's mirror directions.
- **In a close-up, a mirror-like foreground shows a defocused reflection of the room behind the camera** (soft at any
  aperture). Choose the camera's azimuth and elevation by a ray probe of what the mirror sees (`fkl-frames.md` §2b), so
  it reflects dark or cool surfaces.

**Reflection and hot-spot audit (per light state, per planned camera family).** A hot spot is a small bright area (a
sky's sun glow, a window, a bare lamp) seen in a glossy surface or through rough glass. It is a tiny bright source for
every pixel that sees it, so it sets the sample count of the whole frame.
1. List what every glossy and transparent surface mirrors and refracts: ray-probe its mirror and refraction
   directions, or render once per light at low spp (24 spp is enough to find a mystery highlight).
2. Mark the unwanted reflections (a source that hides the subject, a coloured light on the wrong face) and the hot
   spots.
3. Fix them at the source, in this order:
   - rotate the environment: a sweep of stills at ~45° steps (8 frames), and the user picks;
   - move a practical;
   - add a camera-invisible flag.

   Change a material's roughness only with the user's OK: the material is the design intent (`glass-light.md` §5).
4. Never fix them with samples or a post filter. Measured: a sky hot spot seen through a glossy cover needed a 16k
   sample cap; after the environment was rotated, 4k matched it at equal noise. Post median filters went blotchy.
5. Re-run the audit on the FKL frames (stage 8): new cameras find new mirror rays.

## 7. Light over time
- One light event per shot, never during a mechanism's action. Reflections sliding with the camera are free.
- Real sun drift is invisible within a shot (the sun moves 0.25°/min: a shadow edge shifts a few millimetres in a
  shot, far under its penumbra). Time passes between cuts; show it once, as a deliberate time-lapse shot (e.g. a clock).
- A film whose light moves across time: §9.
- Teaser grammar (`animation.md` §6): a glint travelling round a chamfer, a light-wipe cut, a flux-true zoom beam, the
  studio falling away at the end card.

## 8. Lights that converge
A light's cost is its noise, not its watts. The light and glass choices made at this stage moved production render
time several-fold: a lamp buried in a shade, glowing props in light sampling, a hot spot in a cover, real shadows
under a cover (measured: ~9× from the lamp and glowing-prop fixes, ~2× from one hot spot). Scene weight moved it
20–25 %. Each was found at the final, and fixing it there changed an approved look. So design for convergence while
the lights are placed.
1. **Every light in its own pass** from the first lit preview (a light group in Cycles, a light pass ID in Octane),
   with the sun and the sky or environment separate. Keep them on every final too: a light that comes out wrong later
   is a comp gain, not a re-render (measured: 15 passes cost ~+7–10 % per frame and ~180 MB per 1080p frame).
2. **A noise budget per light.** On the worst frame of each state, per region (the darkest third first), compare each
   light's share of the light (its pass's mean) with its share of the noise (the variance of the difference between
   two seeds, per pass, or the noise pass). A light whose noise share is far above its light share (judgement: more
   than ~3×) is redesigned now. Measured: one table lamp in its shade carried ~90 % of a night frame's noise for 5–9 %
   of its light.
3. **Practicals built to converge.** A bulb inside a shade or fixture becomes:
   - an analytic sphere at the filament, at its real size;
   - the shade as its own emitter, fitted to the lit shade's measured brightness;
   - the fixture (shade, socket, cage) excluded from the bulb's light.

   Why: most of a buried bulb's rays hit its own fixture (measured once: 65 % blocked within 15 cm), so most of its
   samples are spent inside the lamp. Re-match the look after the swap: measure the pool and the shade against the old
   build and set per-lamp factors (measured once: the sphere lit its own shade ×1.85 and its pool ×1.27). Engine
   specifics: the engine's manual (or `/octane`, if installed: lamp inside a shade).
4. **Glowing props out of light sampling.** Screens, dials, decals, lit neighbour windows and emissive kit props stay
   visible to the camera and in reflections, but are not sampled as lights. A near-black emissive texture is a mesh
   light that costs samples and lights nothing: audit kit emitters at import (`alive-environments.md` §3b). Measured
   once: ~225,000 emissive prop triangles and ~3,600 m² of neighbour windows sat in light sampling. Items 3 and 4,
   with item 6, gave ~9× less render time at equal noise, and taking the glowing props out was about a third of it.
5. **No added light also blocks light.** A fill card or flag gets the visibility flags of what it is, so it doesn't
   shadow the key or the product.
6. **The glass sampling aid per cover state × light state.** For each cover state (open, closed) in each light state,
   render one preview with and without the engine's glass aid (fake or transparent shadows, thin wall). Keep the aid
   only where the levels agree within ~3 %. Why: an aid on an open, sunlit cover lets direct sun through as if the
   glass weren't there. Measured once: a label in direct sun rendered at 5.8× its correct level, found only in the
   final and fixable only by re-render. Real shadows under a cover converge very slowly (measured: adaptive stopped
   0.9 % of pixels there, against 88–95 % in a lamp-lit state), so know that state's cost now (item 9). Glass roughness
   per state: `glass-light.md` §5.
7. **Hot spots removed at the source** (§6), and **haze only with a measured cost** (§2).
8. **Fit the lights to a reference frame** when a photo or footage frame of the real place exists. Render each light
   group separately through the camera-matched view. Solve non-negative powers (NNLS) that best fit the reference in
   scene-linear, on flat ~24 px cells plus named patches, through the same look. Keep the residual map. A light the fit
   sends to zero is switched off: fewer lights, less noise. Re-fit after any material change. Measured once: the fit
   turned two hand-placed lights off and lifted the worst patch from 0.72 to 0.92 of the reference.
9. **Seconds per frame per state.** Render each state's worst frame in the final engine at a fixed preview config
   (resolution, cap, threshold) and write the seconds next to the state, so the expensive states are known before
   compositions are chosen. Daylit interiors converge slowest: their light is mostly indirect, and adaptive barely
   engages at a production cap. Lamp-lit night frames converge fast (measured: day 75–80 s against night 27–65 s per
   frame at one config). The budget it is held against: `scene-optimisation.md` §0.

**The convergence record**, one per light state, kept in the state record and on the light-state sheet:
- seconds to the production noise target (stage 6) at the preview config;
- adaptive's stopped share (the pixels that stopped before the cap);
- each light's share of the light against its share of the noise;
- the hot spots found and how each was removed;
- the glass-aid verdict per cover state;
- haze: none, or kept with its measured cost.

## 9. Light tells time (a film that moves through the day)
The light is the film's clock: the audience reads the time of day from it, so it must move one way and change only at
readable moments.
1. **A monotonic schedule mapped to edit time.** Name the phases (e.g. afternoon → late afternoon → golden → sunset →
   blue hour → night), map them to edit-time ranges, and interpolate the sun's elevation (and its azimuth drift toward
   the setting side) monotonically between them. **Each shot takes one state, sampled at its midpoint on that curve**;
   the light never runs backwards across a cut. Re-map whenever the edit changes (`editing.md` §5).
2. **Practicals come on once, at a motivated moment:** an ellipsis cut (time has passed; someone came back and switched
   them on, implied like any hand action) or on screen (a transition shot in which the lamp switches on,
   `transition-shots.md` §6). Never on, off and on again.
3. **The window is the audience's clock.** Keep it in the wide shots. **At night we must see out:** a dark navy sky with
   a faint glow near the horizon, street lamps, some neighbour windows lit (warm and cool, some dark), a faint
   reflection of the room on the glass. Never a milky, opaque pane: check every layer of the glass material at night
   (a 2–5 % milky or diffuse layer invisible by day can carry most of a night pane's light under interior lamps), and
   check engine conversions of mixed glass materials (`traps.md`: the Octane Mix inversion).
4. **An HDRI set per phase, from one matched series** (the same maker and location style, so the sky changes and the
   world doesn't). For each:
   - clamp it so the sun lamp owns the disc; after sunset paint any sun disc out;
   - replace the ground below the horizon with the sky's own below-horizon mean, never brighter than the sky, so no
     photographed ground shows through a window;
   - rotate it so its sun (or its glow) column sits at the scene's sun azimuth (the formula for Cycles and Octane is in
     `octane-production.md` §11);
   - **set its power from the approved light states' sky brightness, not the photographs' real stops.** A real day →
     night ramp spans ~15 stops; a film needs a **night floor about 4–5 stops under day** so the window still reads.
   - pick the HDRI per shot by sun elevation bands, one per phase.
5. **White balance follows the key.** By day the camera sits near the sun; with the lamps on, balance only partly toward
   the lamp (so lamps stay warm) and never neutralise the window (it stays blue). Check brand colours and labels under
   the lamp balance.
6. **Probe the low sun before promising it.** Below some elevation the sun can't reach a recessed subject (the product's
   own walls, a sill, a cover). Ray-probe the sun over the scene's azimuth range per shot; where it is blocked (once
   measured below ~6°), carry the sunset with a warmer grade on the last sunlit state, not a fake sun.
7. **Lift a dark shot with the sources it already has.** Rebalance sky/environment and practicals (e.g. environment
   ×2–2.5, lamps ×0.35–4), measured against the grade's target path (`finishing.md` §4). A large bounce panel added to
   lift a shot becomes its key: once measured, an 80 W panel overshot the target L* by 1.4–2.3× and pushed b* 26–38
   warmer than its target. Any bounce stays a whisper and invisible to glossy reflections.
8. **Low-angle glossy covers can show a physical band** (internal reflections off a tinted cover's front wall). Diagnose
   by elimination (environment split, the bounce off, a black flag on what it mirrors, absorption and roughness) and
   accept it by name if it is physical.
9. **Spot-check each phase's KEYs** in the final engine before any full pass, and show the user a KEY strip in edit order.
10. **Never too dark** (the author: "we dont want these too dark"): every shot, dusk and night included, reads rich, not
   murky, at a mean L* of about 16–18 or more after the grade. Lift through the light (point 7) when the grade's bounds
   can't reach it. Prop continuity (a cover's state, a lamp's position) may relax when the story spans hours; the user
   decides which continuity matters.

## 10. Measure and gate (stage 5)
The stage proves its own output on **the light-state sheet**: one row per light state; columns for 3–5 representative
cameras (front, three-quarter, top-down, a macro of the largest dark face, a back-lit view); the product in its real
materials (the set may stay clay, except glass and emitters).

| Measure | How | Pass |
|---|---|---|
| Reads | `reads_metric.py` on every tile | R1 void ≤ 0.30 and R2 separation ≥ 0.20 (warn at 0.20 / 0.40). A state that fails anywhere gets its fill or rim planned now from §5's table, never exposure |
| Fill radiance | each added fill in the scene-linear EXR against local references | in sun ≤ ~1× a sunlit white card; in shade ≤ ~3–4× the local shaded surfaces |
| Black | crush share; black gloss outside the light | crush ≤ 1 %; black gloss stays black outside the light |
| Groups | light groups summed against the beauty | within 1 %; every emitter in a group |
| Noise per light | §8.2, from the light passes | no light whose noise share is far above its light share (judgement: > ~3×) left unexplained |
| Reflections, hot spots | §6 audit per camera family | no unwanted reflection or hot spot left; any environment rotation picked by the user from the sweep |
| Glass aid | §8.6, per cover state × light state | aid kept only where the levels agree within ~3 % |
| Haze | §2 A/B | off, or kept with its gain and cost recorded |
| Cost | seconds per frame per state at the preview config (§8.9) | within the budget (`scene-optimisation.md` §0), or the excess shown to the user |
| Weight | `scripts/scene_weight.py --budget` on the lit master at the end of the stage | every line passes, or carries a written reason |
| Light fit (when a reference exists) | §8.8 residual map | worst patches explained; lights fitted to zero switched off |
| Brightness (a film through the day) | mean L* after the look | ≥ ~16–18 in every state (§9.10) |

**Show the user** the light-state sheet with R1/R2 on each tile, and per row the seconds per frame and the convergence
record (§8). For a film through the day, add the KEY strip in edit order (§9.9).
