# Lighting: grey box first, motivated light, named states, a product that reads

One place for the lighting stage. Detail lives in: `realism-finishing.md` §2 (the lighting gatekeepers, measured),
`alive-environments.md` §6 (location light), `environments.md` §6 (units, museum, practicals), `elements.md` §1–3
(what each light says), `glass-light.md` §6 (glass), `animation.md` §6 and `greybox-animation.md` (light over time).

Contents: 1 Order of work · 2 Motivated light by branch · 3 Light states · 4 Emitters · 5 The product must read (R7) ·
6 Reflections and flags · 7 Light over time · 8 Gate · 9 Light tells time (a film's day → night)

## 1. Order of work: grey box first
1. **Grey box:** mid-grey clay (≈ 0.4) on everything except glass and emitters, so windows, glass covers and practicals
   still light the set and make bokeh. Keep printed marks as dark ink on the clay: prints are composition (plain clay
   frames print shots blind). Low resolution (960×540), ~8 spp + OIDN, persistent data: a couple of seconds per frame
   on a laptop GPU. Look at light *shapes*: patches, shadow bars, rims, the reflections in the glossy parts.
2. **Beauty look-dev on single frames:** real materials at 960×540, one variable per image, captioned sheets.
3. **Calibrate energies on 3 frames before rendering 12.** First guesses at window and scrim energies can be several
   stops off.
4. Name and freeze the **light states** (§3) before compositions: every later tool (composition search, FKL harness,
   production packs) keys them by name.

## 2. Motivated light by branch
**Location** (`alive-environments.md` §6): only what the place would light.
- The sun is split from the sky map: clamp the map so the sun lamp owns the disc, and add a Sun lamp (0.5°, the real
  disc) within 10° of the map's sun. Aim it by geometry (window opening → subject) and check with an ortho plan render.
- Colour temperature follows elevation (rules of thumb: +10° ≈ 3300 K, +6° ≈ 2900 K, +4° ≈ 2600 K; higher afternoon
  sun ≈ 3500–4500 K).
- Windows are thin panes (front-face Fresnel gloss); refracting panes block shadow rays.
- Haze is a whisper: σ ≈ 0.006 m⁻¹ in a 10 m room (0.03 is brown fog). In Octane: the environment medium at ~0.005
  with the radius set per shot (`octane-production.md` §4–5).
- Practicals off by day; after sunset a lamp is in frame and is the key; lamps make pools, not washes.

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
   - camera: exposure and white balance.
2. **Name by what changes:** daylight states by sun elevation (e.g. `s20` = sun at 20°, `s3` = 3°), after-sunset
   states by a dusk index (`d1`, `d2`, … deepening). The name alone tells the order in the day.
3. **One sun path for the film:** one azimuth track, elevation moving one way (§9). A small per-shot azimuth cheat is
   allowed only when logged.
4. **One state per shot.** The film's light arc advances with the acts (`shots-and-script.md` §2; a film that moves through the day: §9 below).
5. Store the table once (a JSON the scene builders read) and record it in the render packs of every engine.
6. Probe the states that matter before committing: a state where the sun is too high can turn black gloss grey; one too
   low may not reach the subject (§9.6).

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

**Process:** plan each light state's lighting during the grey box (which faces void, where the fill and rim live),
and run `reads_metric.py` on every FKL frame; a frame that fails R1 or R2 is fixed by light, never by the grade.

## 6. Reflections and flags
- Reflections are the lighting for metal; surroundings are the lighting for glass. Design what a glossy or dark
  surface mirrors first (e.g. a smoked cover mirrors the window).
- Flag a reflection that hides the subject with a camera-invisible black card (e.g. a window reflection on a cover
  hiding the part behind it).
- A large dark glossy surface (e.g. a black disc or panel) mirrors a bright window at most daylight eye-level and
  three-quarter angles and reads silver: dusk or plan views keep it black (gate it unless that surface is the subject).
- Anisotropic sheen on a spinning part doesn't rotate with it (only printed detail and dust do); a rotating glossy
  panel sweeps its reflection at 2× its angle.
- To find a mystery highlight, render once per light at 24 spp.
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

## 7. Light over time
- One light event per shot, never during a mechanism's action. Reflections sliding with the camera are free.
- Real sun drift is invisible within a shot (the sun moves 0.25°/min: a shadow edge shifts a few millimetres in a
  shot, far under its penumbra). Time passes between cuts; show it once, as a deliberate time-lapse shot (e.g. a clock).
- A film whose light moves across time: §9.
- Teaser grammar (`animation.md` §6): a glint travelling round a chamfer, a light-wipe cut, a flux-true zoom beam, the
  studio falling away at the end card.

## 8. Gate
- The product reads in every state and shot: `reads_metric.py` R1 void ≤ 0.30 and R2 separation ≥ 0.20 (warn at 0.20 /
  0.40); a fail is fixed by light from the decision table, never by exposure.
- Every added fill is a real surface lit by real light and passes the radiance check (in sun ≤ ~1× a sunlit white
  card; in shade ≤ ~3–4× the local shaded surfaces).
- Black lacquer black outside the light; no digital black (crush ≤ 1 %).
- Light groups sum to the beauty within 1 %; every emitter in a group.
- Show the user a light-state sheet: the product in each state, same camera.

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
