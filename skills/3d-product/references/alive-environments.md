# Environments that read as real: the process

Sets built from recipes read as "CG in a bad sense": no history, dead-flat procedural surfaces, rims and key twins with
no source, the product centred with no foreground, the camera at arbitrary heights. This process (after the methodology
*Making CG Feel Alive*, with a scene-reference track and a camera-reference track) replaces them with a lived-in place.
- **Choose** the environment with `environments.md` (claim, honesty filter, extravagance index).
- **Build** it with this file. Every environment goes through it, including a quick "add an environment": the ★ steps
  are the minimum.

The governing rules:
- **Agreement beats detail.** Shadow softness matches light size, highlights match roughness, grain matches exposure.
- **Causality beats density.** Every visible thing has a reason written in the bible.
- **Commit to one realism level.** A photoreal product in a sterile set is worse than a consistent stylisation.

The user's rules (standing):
- **Dress by what would really be there** around the product: its system and the resident's habits first (§5).
- **Never hide a visible prop to fix a composition.** Fix it with the camera. Hide only what no camera ray reaches over
  the whole shot, verified densely along the path, not only at the FIRST/KEY/LAST frames.
- **No interpenetration.** Touching or very close is fine; intersecting is not. Check it automatically (§5, §10).
- **Every environment gets the full realism process**, and research is always paired with reference images.
- **Props age; the product doesn't.** The product is rendered as designed (`wear-materials.md`).

## 0. Pick the lane (branch)
| Lane | When | The set's "history" | Aging budget |
|---|---|---|---|
| **A. Lived-in photoreal** | lifestyle, "in its place", editorial, storyboards | a set bible: who, what just happened, time stack | the room carries wear, dust and use; the product stays as designed |
| **B. Stylised-but-alive** (the Apple lane) | packshots, studio, abstract sets, launch films | a *fabrication story*: how the set would really be built (painted cyc with a real cove radius, CNC plinth, microcement) | roughness breakup 2–5 %, faint seams at sheet widths (~1.2 × 2.4 m), soft contact dust at plinth bases |

Both lanes share steps 3 and 5–10. In lane B, physics still lives in materials and light, and the abstraction lives
in the environment and motion. Natural elements inside an abstract set follow full photoreal logic.

## 1. ★ Write the bible before you build (lane A) or the fabrication story (lane B)
Answer in the project's thinking doc:
- the claim, in one line;
- **who** lives or works here and for how long;
- **what just happened** (props chained into an event the viewer can reconstruct);
- the **time stack** (original build → renovations → current use, each with its own materials);
- the **economy** (money shows as maintenance, not ornament);
- the **region** (outlets, door hardware, signage language, brick bond, mains voltage);
- the **rules**:
  - palette lock: one dominant hue family, one secondary, one accent reserved for the story;
  - 3–5 materials;
  - an exclusions list.

Add a **wear map** from circulation: worn paths, glossy touch points, dust on high horizontals. **If the bible can't
justify a prop, cut it.** Decide the orientation for the light you want (e.g. a west-facing window for an evening sun
streaming in).

## 2. ★ Pair research with reference images (always)
Two background tracks, as in `research-protocol.md`. Both deliver URLs and *measurements*, never downloads.
- **Scene references:** real photographs of the kind of place. Measure product frame share, camera height, lens,
  depth layers and foreground, light direction and patches, palette ratios, prop counts, visible imperfections.
- **Camera and coverage references:** film stills and brand shoots of one room. Measure heights by body position, the
  lens set, foreground share, the light schedule, lens character magnitudes.

The defaults in §5, §7 and §9 were measured this way for lived-in interiors. Re-use them as starting values, and
re-measure for a different kind of place.

## 3. ★ Assets: real statistics, a complete shell, your own hero supports
- **Kit assets (a kit-asset library through its desktop downloader app).** There may be no MCP; drive the app through
  background app control.
  - Settings: target the Blender version in use, textures **4k png**. Record where downloads land in the site profile.
  - Search boxes: clear the field with the ✕ first, or type with `overwrite_existing`, because positional insert fails
    in the background.
  - Kits are 1–2.5 GB each. The download icon sits at the card's lower right.
  - Downloading needs the user's approval; a standing "download anything of use" covers the kit library. Log what you took (kit, asset, size).
- **Load kit USDs with a converter** that imports at real scale (metres) and rebuilds every MaterialX Standard Surface
  network as a Principled BSDF:
  - map base colour × base, metalness, roughness, IOR, coat, sheen, subsurface, transmission, emission, opacity →
    alpha, normal map, height → bump;
  - turn architectural glass into a thin pane (§6);
  - print the converted materials and look for any left unconverted (an instanceable material not un-instanced).
- **Build the whole architecture** (Jack Fisk: build for 360°).
  - A complete room gives real bounce, real reflections and a reverse angle for free.
  - Outside the windows, place real things at real distances (in a city: street trees at 8–15 m, buildings across the
    street at 25–40 m, a ground plane at street level). Never leave an HDRI's synthetic lower hemisphere in the view.
- **Hero supports you model yourself** (the table, cabinet or plinth the product stands on):
  - B-rep with fabrication logic: ~3 mm shadow gaps, routed pulls, tapered legs;
  - edge radii by manufacture: 1–1.5 mm machined or veneered, ~3 mm solid wood;
  - import through a path that bakes the glTF Y-up conversion (a bare import lays the part on its side);
  - skin it with a *scanned* material, mapped per part along its real construction (`reference-detailing.md`,
    "Patterned materials follow the object's construction");
  - finish rules: oiled wood ≈ satin, roughness min 0.38–0.42, or grazing views mirror the window and read as paint;
    tint the veneer to its finish (oil darkens and warms).
- **Measure a kit material's albedo before trusting its name.** A material named for one species can be another
  colour entirely, and tinting won't rescue it. Open the base colour map and check its linear mean and p5–p95
  luminance against the real material (oiled walnut or teak runs about 0.03–0.12 linear); swap the texture if it
  misses. Name the material in the bible after what it *looks* like.

## 4. ★ Layout and scale, with previs cameras first
- Real units and human anchors: doors, sockets at their real heights, an everyday object of known size.
- Put the product where the light *and* the bible put it.
- **Block the storyboard cameras before dressing:** each frame gets a body-position height, a lens from the set, a
  stop, a light state and a story beat. Dress to the lens but build the whole room.
- A top-down **plan render** (ortho, ceiling hidden) shows where the sun patches land. Aim the sun by geometry: check
  it can actually reach the product through an opening, not through a wall.
- **Probe the room's real geometry first:** wall faces, each window's glass islands (x-range, sill height, reveal
  depth), the corners. Place the hero support where the brief and the windows allow (a table in front of a window
  works only where the glass starts above the table top).
- **A low sun can't light a surface just below a sill.** The window's bottom rail and reveal shade it; at about +6–10°
  the beam clears the surface and lands beyond its front edge, at about +15° it falls onto the top. Pick the elevation
  per frame (a higher afternoon sun for frames that must show the product and its system, a low golden sun for mood).
- **Check the sun's whole path outside:** buildings across a street block a low sun into upper floors (e.g. 24–30 m
  blocks cut a third-floor window at +10° across a 20 m street). Put a gap on the sun's line, as a real street would
  have. A tree exactly on the line throws a full shadow instead of dapple; move it until only its crown's edge crosses
  the beam. A kit block rotated 180° lands at world x ∈ [cx − b, cx − a] for local extents [a, b]: check the extents.

## 5. ★ Dress in context: the product's system first, then layers, then fill
**Ask what would really be here if someone lived or worked here** (a standing rule). Before placing a single
prop, list:
- the product's **system**: what it plugs into, sits on and is used with, and where its consumables live (e.g. an
  espresso machine means a grinder, beans, cups, a water source and a socket). Build them from period-correct
  research, not a kit's generic stand-ins;
- the **resident's habits**: what they do here, what they bought recently, what they leave out.

Frames that show "a few objects scattered around" read as staged CG even when every object is photoreal. Dressing only
the bible's *event*, without the system and the background layer, reads as unintentional.

**Layers, in order:**
1. Architecture.
2. Hero props (unique, never reused).
3. Set dressing (furniture, soft goods, lamps).
4. Background dressing.
5. Breakdown from the wear map: roughness drift ±2–6 %, a patchy dust film on up-facing normals, mostly a roughness
   effect.
6. **Life pass:** the drink going cold, the book left open, the throw half off the chair, the chair turned. At blue
   hour the life pass includes the street: light a random ~35 % of the neighbouring buildings' window panes (one
   `Random Per Island` per pane, 2500–3800 K, 0.3–1.1× brightness) and turn the room's own sconces on.

- **Props age; the product doesn't.** A prop seen at insert range or closer needs its physical history: a slight bow
  from what it holds, bevelled fold edges (Bevel modifier, angle-limited), rub wear where contents press, scuffed
  corners. A razor-flat box with a perfect print reads as CG next to real materials. The product stays factory-finish.
- **Clean up kit leftovers after cuts.** Removing part of a kit can leave its contents inside your new props. List
  every object inside your new props' volumes and remove or move them.
- **No interpenetration.** After dressing, run an automated overlap check in the scene build: BVH-tree overlap between
  every pair of placed objects, tolerance ~1 mm. Fail and print the offenders before rendering; resolve by nudging
  along the contact normal. Fix the generator, not the instance.
- **Hide only the unseen.** A per-shot hide list is a render trim, computed from visibility over the whole camera path
  and verified densely. If an audit says "hide X", replace it with a camera fix (or, rarely, a plausible re-dress with
  a note).
- **Counts (measured on real lived-in interiors):**
  - product + 3–6 objects on its support, asymmetric;
  - 2–4 plants, one trailing and one tall;
  - ≥ 5 kinds of imperfection in the room, none on the product;
  - one human trace per hero.
- **Colour comes from objects, not walls.** Place each accent at least twice, across different objects. Anything
  brighter than the product near it goes; the squint test finds it.
- **Graphics are generic and logo-free.** Kit props can carry real marks: keep them out of focus or out of frame.
- **Repetition hunt from the camera:** the same small object twice in one frame is a tell. Delete one.
- **Vary instances** by rotation and ±5 % scale.

**Fill numbers (measured from photos of real homes and real setups of the product type):**
- **A support surface (sideboard, table):** the product + 5–7 objects in 3 groups, 30–40 % of the top left empty.
  Heights: tall 460–610 mm at the end away from the view, medium 250–400, low 100–200. The product is never dead
  centre.
- **Under a window:** keep everything ≤ ~300 mm (or below the sill) so the view stays; the one tall item goes at the
  wall end.
- **Wall art:** centre at 1450–1525 mm, 100–250 mm above furniture, ~2/3 of the furniture's width, 50–75 mm gaps in a
  cluster, 1–3 pieces per wall (one large, one small). Let an object partly hide one piece (a third of real rooms do).
- **A corner:** 3–4 things at three heights: a tall plant 1.7–2.2 m by the window, something mid-height (an instrument,
  a lamp or leaning art), something low (a crate, stacked books), and art behind them partly hidden.
- **Density:** a close-up of one surface holds 10–20 objects; a wide of the room holds 40–60.
- **Cables:** show one or two tidy runs in the wides (real homes show them; brand shots hide them). Every cable has a
  source and a destination.
- **Causality checks:** test every prop against heat, sun, power and use (e.g. heat-sensitive things stay out of sun
  patches, a plant's species suits its window, an appliance from another mains region needs its converter, equipment
  isn't stacked where it would overheat).

**Build what kits lack** procedurally, at real sizes, varied per instance: books (rows with a leaning end book;
stacks), media on shelves (spines out, some pulled or leaning), wall shelving, framed prints (your own abstract art,
mat, glazing), radiators, outlets on conduit, cables as curves. Build the product's system components from the
period's real designs, laid out in mm.

## 6. ★ Light only what the place would light
- **The sun comes from the sky map, split.**
  - Clamp the map (e.g. a `MINIMUM` at 60) to paint out its sun.
  - Add a Sun lamp at 0.5°, within 10° of the map's sun, rotating the map so they agree.
  - Colour temperature follows elevation: +10° ≈ 3300 K, +6° ≈ 2900 K, +4° ≈ 2600 K.
- **Windows are thin panes:** Transparent + a front-face-only Fresnel gloss. The sky strength sets the cool shadow
  fill, which makes golden hour vibrant: warm patches against cool shade.
- **Haze is a whisper:** σ ≈ 0.006 m⁻¹ for a 10 m room. σ 0.03 reads as brown fog; real interior photographs show
  almost no god rays.
- **Practicals:**
  - off by day;
  - after sunset, a lamp is always in frame: a point light inside a real shade, 2700–3000 K, its own light group;
  - **the lamps are the key at blue hour.** A lamp in frame whose pool is the key, plus one off-frame; lamps make
    pools, not washes. Under-powered lamps leave the room dim, and lifting it in the grade (≈ +2 EV) turns it into a
    grey day; over-powered off-frame lamps wash a wall evenly;
  - the window at blue hour is the sky map tinted to 9000–12000 K, at a strength that roughly balances the lamp-lit
    room. The camera WB sits toward the lamps (3800–4800 K) so the window goes blue.
- **Exposure:** log2(π/E_key) as the start, then expose for the room. Patches sit 2–3 stops over the shade and the
  window 1.5–3 stops over the room.

## 7. ★ A DP's camera
**Storyboard tiers: W → M → CU → ECU → CU → M → W** over one light schedule. ECUs show details the product really has
(verified against the detailed model): a lit indicator, a knurled control, a printed label. Never invent a feature for
a detail shot. **Macros in Blender (thin lens, no bellows factor):** to match a real 100 mm macro at magnification m,
set focal = 100·(1+m) mm, distance = 100·(1+m)/m mm, f-stop = N·(1+m). A 100 mm camera at 0.4 m frames 4× too wide
and is 1.25× too shallow. Dust goes on props in macro (≈ 1 speck/cm², 0.1–0.3 mm), never on the product.

Defaults for a lived-in interior (measured from film and brand coverage of single rooms):
| Frame | Lens (full frame) | Height | Product share | Foreground |
|---|---|---|---|---|
| establish | 28 mm, f/5.6 | standing 1.50–1.65 m, **level + shift_y** | 8–12 % | a chair back, a lamp |
| medium | 35–40 mm, f/2.8 | seated in an armchair 1.05–1.20 m | 12–25 % | 10–35 % of frame, 1–3 EV darker |
| hero | 40–50 mm, f/2.8 | seated 0.95–1.2 m, 8–15° down | 20–32 % | product on a third, 30–40 % clean space |
| insert | 65–85 mm, f/2.8–4 | 0.85–0.95 m | cropped | a part or prop soft |
| macro | 100 mm, f/5.6 | at the surface, 0.35–0.5 m away | > 100 % | — |

Every frame keeps at least 3 depth layers, the hero 4: foreground, product, room, exterior. Foregrounds sit in the
lens's height band (one far below the lens drops out of frame). Wides and mediums stay level; only details tilt.

**When the light won't serve the beat, retitle the beat; don't cheat the sun.** If the last sun lands on the wrong
part, the beat becomes what the light does ("the last light slides across the base"). A second invisible sun would
break the causality audit.

## 8. ★ Previs loop, then renders
- **Previs:** 960×540, 32 spp (measured ≈ 30 s a frame in Cycles on a laptop-class GPU). Tile the frames into contact
  sheets and fix one thing per pass; expect several passes.
- **Board:** 1600×900, 160 spp EXR, for storyboard frames.
- **Final:** 2048×1152, 640 spp EXR, light groups key / world / practical with light-group denoising, for the hero.

## 9. ★ Post like a photograph, then finish every shot in its own Resolve project
**Save each comp as a DaVinci Resolve project, so it can be opened and adjusted** (`finishing.md`).
- Every frame renders with light groups (key, world, practical) and data passes; every emitter is in a group, or the
  groups don't sum to the beauty.
- Write lens-applied plates, one file per group plus halation, and the solved grade.
- Build one Resolve project per shot, with colour management copied from a verified project:
  - the plate on a timeline;
  - a Fusion comp with a Loader per group, the solved gains, additive merges and film grain;
  - the look LUT on node 1;
  - a rendered TIFF checked against the numpy twin;
  - `ExportProject` → a `.drp` per shot.
- Never grade only in numpy when the pipeline promises Resolve.

The order a photon meets glass, film and print:
1. Lens optics per light group or beauty, with measured magnitudes:
   - distortion k1 −1.2 % at 28 mm, −1.0 % at 35–40, −0.6 % at 50–65, −0.3 % at 85–100;
   - lateral CA 0.8–1.1 px at 4K;
   - vignette by stop (0.32 at f/2.8 wide, 0.18 at f/4, 0.10 slower, halved on long lenses);
   - PSF glare, veil and modern ghosts.
2. Halation only above scene-linear 1.5: red-orange, σ ≈ 9 px at 2K, 10 %.
3. A bounded solved grade to the frame's regime:
   - **golden** (golden and sunset interiors): **low-key by design.** L1 1–6, L50 18–40, L99 85–98, z2 20–55 %,
     crush ≤ 1 %, clip ≤ 2.5 %, C99 ≤ 65, b* 5–25 (the warm cast is the light, not an error). WB 5200–6200 K. A bright
     interior regime (L50 55–70) is wrong here: it lifts the frame > 1 EV, blows the sky and flattens saturation into
     a catalogue frame;
   - **night** (blue hour): b* −6…12, a* −2…6, Cmid ≤ 28, WB 3800–4800 K;
   - **anchor the product:** the cost also holds the product's median L* (Object Index mask) in a band (golden 10–24,
     night 5–16 for a dark product), so a sun patch can't grey it. Only final-quality EXRs carry the pass;
   - **search around the by-eye exposure** (the state's look-dev exposure ±1.25 EV), with saturation 0.85–1.1 and film
     contrast 1.05–1.4. A film curve sits about 0.5–0.8 EV darker than AgX, so a ±0.75 EV window pins wides at the
     bound.
4. **Per-channel film grain last:** Kodak 5248 proportions (R/G/B size 3.3/2.9/2.5 px at 2K, strength
   0.42/0.46/0.85). G σ ≈ 2 codes by day and 3 at dusk, grain 25 % coarser at dusk, weighted to the mid-tones.

## 10. ★ Audit before delivery (the ★ items)
- View transform chosen and never Standard. Scene-linear EXR.
- Bible, wear map and palette lock are written. Real units and human anchors are in.
- Micro-bevels on your own parts. Roughness varied on every hero surface. Breakdown follows the wear map.
- Scatter by rule with exceptions. Hero props unique. Clutter follows use.
- The sun is split and aimed, with thin-glass windows. Every light is motivated. Haze is a whisper.
- Real focal lengths, stops and heights. Foreground and depth layers present.
- Grain per channel, after optics and defocus.
- **Audits:**
  - overlap check: zero interpenetrating pairs visible to any camera;
  - hide lists: every hidden object is unseen over the whole path;
  - repetition hunt from the camera;
  - squint test: the product wins the value and colour hierarchy;
  - scale test: DoF, texel density and atmosphere agree;
  - causality test: pick 10 random details, and the bible must explain each;
  - context test: the product's system is present, and no surface, wall or corner in frame is empty by accident;
  - silhouette test.

## Verdicts
- A complete kit room with real exterior depth, a split and aimed low sun, and a lived-in bible read as photographs
  at previs quality (32 spp). Procedural recipe sets never did, at any quality.
- The biggest single wins:
  - thin-glass windows: sun through real windows, with leaf shadows from real trees and plants on real walls;
  - the camera at body heights with real lenses;
  - colour moved from walls to objects.
- The late fixes (a low-key grade, a real albedo, aged props, lamps as the blue-hour key) each moved the frames more
  than any extra sample count.
- Don't:
  - put the product in front of a window the room's geometry forbids (know the room);
  - shoot a long-lens insert of the product on a flat printed prop (it reads as a poster; back off to a shorter lens
    with a prop in the foreground);
  - place a foreground far below the lens's height band.
- Sunset interiors land at the exposure bound: honest for the light, darker than the rest. At blue hour, a brighter
  sky tint or a second practical in frame is the lever before lifting exposure.
