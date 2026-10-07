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
- **Keep the scene light from the first import** (§3b). Weight is decided when an asset enters the set; trimming a
  dressed set at the end saves little and breaks shots.

## 0. Pick the lane (branch)
| Lane | When | The set's "history" | Aging budget |
|---|---|---|---|
| **A. Lived-in photoreal** | lifestyle, "in its place", editorial, storyboards | a set bible: who, what just happened, time stack | the room carries wear, dust and use; the product stays as designed |
| **B. Stylised-but-alive** (the Apple lane) | packshots, studio, abstract sets, launch films | a *fabrication story*: how the set would really be built (painted cyc with a real cove radius, CNC plinth, microcement) | roughness breakup 2–5 %, faint seams at sheet widths (~1.2 × 2.4 m), soft contact dust at plinth bases |

Both lanes share steps 3, 3b and 5–11. In lane B, physics still lives in materials and light, and the abstraction lives
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
  - Settings: target the Blender version in use. Download the texture resolution the tool offers (a high-resolution
    set is fine on disk), but **load the variant each asset's role needs** (§3b), never one size for everything.
    Record where downloads land in the site profile.
  - Search boxes: clear the field with the ✕ first, or type with `overwrite_existing`, because positional insert fails
    in the background.
  - Kits are 1–2.5 GB each. The download icon sits at the card's lower right.
  - Downloading needs the user's approval; a standing "download anything of use" covers the kit library. Log what you took (kit, asset, size).
- **Load kit USDs with a converter** that imports at real scale (metres) and rebuilds every MaterialX Standard Surface
  network as a Principled BSDF:
  - map base colour × base, metalness, roughness, IOR, coat, sheen, subsurface, transmission, emission, opacity →
    alpha, normal map, height → bump;
  - turn architectural glass into a thin pane (§6), including kit glass that drives transmission from a map (a thin
    pane by that map);
  - audit kit emitters (§3b);
  - print the converted materials and look for any left unconverted (an instanceable material not un-instanced).
- **Build the whole architecture** (build for 360°).
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
  luminance against the real material's reflectance, taken from a cited source (an LRV, a manufacturer's value) or from
  the measured mean of reference photos under neutral light. Write the target in sRGB and linear. Measured in kit
  libraries, errors ran 2–3× in both directions: an oiled mid-tone wood such as teak measured ~0.15–0.24 linear (LRV
  ≈ 23 and a photo mean) against 0.07 in render; a kit "white" paint sat at 0.41 against 0.80–0.85 real. Regrade or
  swap the texture to the measured mean, keeping its own contrast; never a chain of brightness and saturation tweaks
  (`reference-detailing.md`). Name the material in the bible after what it *looks* like. The in-render audit (§10.2)
  checks the result in the light.

## 3b. ★ Keep it light from the first import (pre-flight and budget)
Weight is decided when an asset enters the set, and it is found at the first final render, where fixing it changes
approved looks. You can't trim your way out of a heavy set afterwards: a glossy product and its glass mirror most of
the room, so audited trims of a dressed room saved only 3–7 % (measured). Build it light instead. Measured once: a room
dressed without a budget needed about twice a 24 GB card and rendered out of core; after optimisation the same room
used ~8 GB.

The budget (its numbers and the `budget.json` format) comes from the setup probe: `scene-optimisation.md` §0. The
probe tool is `scripts/scene_weight.py` (read-only).
1. **Probe every asset as it enters** (kit model, generated prop, exterior block): import it into an empty probe file
   and run `scene_weight.py` on it. Record:
   - triangles;
   - separate objects and duplicate groups;
   - materials and distinct shader programs, procedural nodes;
   - images: count, megapixels, bit depth, channels;
   - emissive materials and their emitting area;
   - glass layers.
2. **Keep a running budget table:** one line per asset, plus the set's total from `scene_weight.py --budget` (estimated
   GPU memory, objects, shader programs, emitters) and the preview seconds per frame. Flag every line over budget as it
   lands, not at the end.
3. **Load texture variants by role:**
   - product, prints, labels, HDRI: full size;
   - hero props near the product: 2–4K;
   - set dressing: 2K;
   - background, reflection-only and never-framed objects: 1K.

   Greyscale maps (roughness, metallic, height, masks) stay single-channel, 16-bit at most; a height map that only
   feeds bump needs no 32-bit float. Final sizes by on-screen need come once the cameras are final
   (`scene-optimisation.md`). Measured: one size (4K) for everything put a room at ~50 GB, and most of its large images
   were 32-bit height maps feeding bump.
4. **Flag heavy assets** (over the budget's single-asset line). Prefer a lighter variant, or a proxy that keeps the
   asset's job: a low-poly shade with an opacity map, or a measured emission for a shade that shapes a lamp's light.
   A/B the light it casts before swapping. Measured once: one never-framed woven shade was 46 % of a room's triangles
   and cost 8–10 s per render session.
5. **Instance repeats.** One mesh per duplicate group (books, cups, chairs, generated items). Join static clusters
   per material where no object-space pattern depends on the object. Why: some renderers pay per separate object per
   session (measured: ~55 ms each).
6. **Store per-instance variation as data the final engine reads:** an attribute or a UV offset baked per instance,
   not object-info randomness or shared generated coordinates. Measured: hundreds of meshes that used object info took
   the first mesh's values after conversion to another engine.
7. **Kit glass and kit emitters, at import.** Kit glass becomes a thin pane (§3, §6). List every emissive material
   with its share of non-black texels: a zero-emission convention costs nothing, but a near-black emission texture is
   a mesh light that lights nothing, so take it out of light sampling (`lighting.md` §8). Measured once: two kit
   emitters' maps were 99 % black.
8. **Delete what the bible excludes, at build** (rooms and fixtures no planned camera sees or mirrors, props that
   fail the bible), and purge unused data blocks after each import. Expect a small saving in an open, glossy room (measured: unseen rooms were ~1 % of
   the triangles). The real savings are texture sizes, shaders, emitters and single heavy assets.
9. **Never remove the enclosure or the outdoors for weight.** They shade and bounce: removing an unseen street and
   floor lit a room from below (measured: ΔE00 ≈ 20). Build exterior blocks lean instead: real silhouettes at real
   distances, low-resolution textures.
10. **A global safe-off list, once the previs cameras exist (§4):** the objects no ray reaches from any planned camera,
    directly, through glass or in a reflection (behind walls, other rooms). Verify it by group render: mean ΔE00 < 0.5,
    p99 < 2. Re-run it when the cameras change. It is a render-time toggle list, never a composition tool (§5, "Hide
    only the unseen").
11. **End of stage:** `scene_weight.py --budget` on the dressed master, and the renderer's own memory figure on one
    previs frame (the final word over any estimate). Both go in §11.

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
- **Confirm sun reach per light state:** the plan render plus a ray probe from the product toward the sun for every
  daylit state that promises sun on it (`lighting.md` §9.6).
- **Once the previs cameras exist, build the global safe-off list** (§3b.10).

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
   `Random Per Island` per pane, 2500–3800 K, 0.3–1.1× brightness) and turn the room's own sconces on. Lit
   neighbour windows glow for the camera and reflections but stay out of light sampling (`lighting.md` §8).

- **Props age; the product doesn't.** A prop seen at insert range or closer needs its physical history: a slight bow
  from what it holds, bevelled fold edges (Bevel modifier, angle-limited), rub wear where contents press, scuffed
  corners. A razor-flat box with a perfect print reads as CG next to real materials. The product stays factory-finish.
- **Clean up kit leftovers after cuts.** Removing part of a kit can leave its contents inside your new props. List
  every object inside your new props' volumes and remove or move them.
- **No interpenetration.** After dressing, run an automated overlap check in the scene build: BVH-tree overlap between
  every pair of placed objects, tolerance ~1 mm. Fail and print the offenders before rendering; resolve by nudging
  along the contact normal. Fix the generator, not the instance; limit how far a drop-to-support may reach, and clamp
  cables ≥ 0.5 mm off every surface. The gate is **0 interpenetrating pairs visible to any planned camera**; authored
  kit contacts no camera sees are listed, not chased (measured once: 827 pairs → 41, 0 visible).
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
- **Vary instances** by rotation and ±5 % scale, kept as instances (§3b.5).

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

**Build what kits lack** procedurally, at real sizes, as instances of a few meshes with the variation stored per
instance as data (§3b.6): books (rows with a leaning end book; stacks), media on shelves (spines out, some pulled or
leaning), wall shelving, framed prints (your own abstract art, mat, glazing), radiators, outlets on conduit, cables as
curves. Build the product's system components from the period's real designs, laid out in mm.

## 6. ★ Light only what the place would light
- **The sun comes from the sky map, split.**
  - Clamp the map (e.g. a `MINIMUM` at 60) to paint out its sun.
  - Add a Sun lamp at 0.5°, within 10° of the map's sun, rotating the map so they agree.
  - Colour temperature follows elevation: +10° ≈ 3300 K, +6° ≈ 2900 K, +4° ≈ 2600 K.
- **Windows are thin panes:** Transparent + a front-face-only Fresnel gloss. The sky strength sets the cool shadow
  fill, which makes golden hour vibrant: warm patches against cool shade.
- **Haze is opt-in** (`lighting.md` §2). Start without it; real interior photographs show almost no god rays. Add a
  volume only for a named job, with its render cost measured on the state's KEY. If kept: σ ≈ 0.006 m⁻¹ for a 10 m
  room (σ 0.03 reads as brown fog).
- **Practicals:**
  - off by day;
  - after sunset, a lamp is always in frame, 2700–3000 K, its own light group, **built to converge**
    (`lighting.md` §8): an analytic sphere at the filament, the shade as its own fitted emitter, the fixture excluded
    from the bulb's light. Why: a point light buried in its shade spends most of its samples inside the lamp
    (measured once: ~90 % of a night frame's noise for under a tenth of its light);
  - things that glow but aren't lights (screens, dials, lit neighbour windows) glow for the camera and in
    reflections, but stay out of light sampling;
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
  sheets and fix one thing per pass; expect several passes. Write the preview seconds per frame and the §11 numbers in
  the sheet's caption, so weight creeping in shows up on the pass that added it.
- **Board:** 1600×900, 160 spp EXR, for storyboard frames.
- **Final:** 2048×1152 EXR with light groups key / world / practical, for the hero; sampling and denoising follow the
  production policy (stage 6).

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

## 10. ★ Audits
The ★ checklist:
- View transform chosen and never Standard. Scene-linear EXR.
- Bible, wear map and palette lock are written. Real units and human anchors are in.
- Micro-bevels on your own parts. Roughness varied on every hero surface. Breakdown follows the wear map.
- Scatter by rule with exceptions. Hero props unique. Clutter follows use.
- The sun is split and aimed, with thin-glass windows. Every light is motivated. Haze only with a named job and a
  measured cost.
- Real focal lengths, stops and heights. Foreground and depth layers present.
- Grain per channel, after optics and defocus.

### 10.1 Quick audits (every pass of the previs loop)
- overlap check: 0 interpenetrating pairs visible to any planned camera, the rest listed (§5);
- hide lists: every hidden object is unseen over the whole path;
- repetition hunt from the camera;
- squint test: the product wins the value and colour hierarchy near it;
- scale test: DoF, texel density and atmosphere agree;
- causality test: pick 10 random details, and the bible must explain each;
- context test: the product's system is present, and no surface, wall or corner in frame is empty by accident;
- shape test: threshold the frame at its 80th luminance percentile; the main masses read as shapes, and in a product
  frame so does the product.

### 10.2 In-render albedo audit (after dressing, before stage 5 sets energies)
A texture map's mean (§3) is not what the camera sees: tints, mixes and layers change it. Measure it in the render.
1. Render one lit preview with the Diffuse Color, Diffuse Direct and Diffuse Indirect passes and object IDs.
2. For every visible object, take its median diffuse colour (linear) and compare it with the real material's
   reflectance (§3).
3. Flag anything below 0.02 or above 0.85, chroma outliers, and anything off by more than about ×1.5 (judgement).
   Hero supports and large areas sit within ~×1.3 of their target.
4. Fix before light energies are calibrated. Then check where the sun lands: shade colour comes from what the sun
   hits, so put something light in the beam if the bible allows.

Why: albedo compounds through every bounce, and bounce depth doesn't. Measured: 2× the wall albedo gave 5.2× the
light in a shaded corner, while 6 → 12 diffuse bounces changed a dressed room by 0.0 %. A dim room is a scene problem,
not a kernel problem.

### 10.3 Silhouette audit (measured), and the fix
A flat textured wall or an unbevelled edge on an outline is a ruler line. It reads as CG in a wide, however good its
texture. Find these lines by measurement, not by eye:
1. From the previs EXRs (depth, normals, object IDs), build three edge maps:
   - silhouettes: depth steps;
   - creases: normals more than ~38° apart within one object (anti-aliasing splits a 90° arris into two ~45° steps);
   - junctions: object changes with no depth step.
2. Keep pixel-straight runs of ≥ ~45 px (a Hough transform; ≥ 92 % of the run within 1 px).
3. Name the material under each run with a ray recast through the shot camera.
4. List knife edges: convex edges > 60° with no bevel faces.
5. Flag textured architecture (brick, stone, tile, rough plaster) on any outline, and unbevelled edges on props near
   the lens.
6. Fix the flagged runs (below), then re-run until no flagged run is visible in any planned camera.

Measured once: 434 straight runs in 13 frames, and the one the user had named was among those flagged.

**The fix.** A bump changes nothing at an outline, and modelled 10 mm recessed joints (cut and set back, UVs kept)
read the same as flat at shot distance. What works:
- for textured architecture, **render-time displacement from a map derived from the albedo** (raised material white,
  mortar black, small holes closed, ~0.5 mm softening, ~10 % fine detail), ~8 mm, smoothed normals at convex corners:
  corners step in at every joint and the units read raised (method: stage 3; engine specifics: the engine's displacement docs, or `/octane` if installed);
- real edge units (modelled bricks or stones along the corner);
- bevels on knife edges.

Costs (measured): edge units nothing (32 vs 31 s per frame); true displacement in Cycles +70 %; texture displacement
in Octane ~0 sampling time. Judge a fix at the corner, at 2×, in the shot's own light: a proof lit head-on hides relief.

### 10.4 The realism manifest
Every master records the realism features it carries, each with a switch that defaults on for finals:
- displacement maps;
- edge units;
- bevels;
- breakdown and wear switches;
- glass layers;
- per-state material values (`lighting.md` §3).

Store it with the master (a JSON beside it, or properties on the scene). A harness may switch a feature off for a grey
box only; a final may not, unless the user agrees. **Stage 8 (FKL) reads the manifest back from the saved file** and
re-runs the silhouette audit (§10.3) on the FKL frames. Why: a silhouette fix the user approved was switched off by
the next harness, carried into the final engine's master, and found again by the user in the final week.

## 11. Measure and gate (stage 4)
| Measure | How | Pass |
|---|---|---|
| Causality | 10 random details picked from the frames | 10/10 explained by the bible |
| Context and fill | the product's system listed; fill counts (§5) | system present; counts inside the measured norms, or a written reason |
| Overlap | BVH pairs at ~1 mm (§5) | 0 interpenetrating pairs visible to any planned camera; the rest listed |
| Repetition, squint, shape | §10.1 | no repeat inside a frame; the product wins value and colour near it |
| Texel density | screen pixels per metre ÷ texels per metre on hero surfaces, at the closest planned framing | ≥ 1 texel per pixel (judgement) |
| Silhouette | §10.3 | 0 flagged straight runs visible in any planned camera |
| Albedo | §10.2 | nothing visible below 0.02 or above 0.85; hero supports and large areas within ~×1.3 of target |
| Sun reach | plan render + ray probe per daylit state (§4) | the sun reaches what each state promises |
| Weight | `scripts/scene_weight.py --budget` on the dressed master (§3b) | every line passes or carries a written reason; each flagged asset fixed or accepted with a reason |
| Memory | the renderer's own figure on one previs frame | in core on the smallest render card, with the headroom `scene-optimisation.md` §0 sets |
| Safe-off list | group render with and without it (§3b.10) | mean ΔE00 < 0.5, p99 < 2 |
| Preview cost | seconds per frame at the previs config (§8) | written on the sheet; within the budget |
| Realism manifest | §10.4 | written; every switch on |

**Studio** (lane B, a builder from a JSON spec): the light ratios, read from light groups on a grey card at the
product: the world 0.5–2 % of the key, the set-only twin 25–30 % of the key (~4 % under a macro lens). Overlap, weight,
memory and the realism manifest as above.

**Show the user** the previs contact sheet with these numbers in its caption, and the budget table beside it.

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
