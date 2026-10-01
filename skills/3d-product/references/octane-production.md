# Octane production: one master, animation packs, a kept-alive session

How to take an approved Cycles film to Octane finals on a render node. Measured on a multi-GPU node (four high-end
consumer GPUs capped at 200 W) with the OctaneBlender add-on and OctaneServer Studio 31.10 in Blender 5.2, 1080p unless stated.
Add-on behaviour below was verified on 31.10: re-verify after any add-on update. Related: `cycles-production.md` (the
other path), `scene-optimisation.md`, `render-farm.md`.

Contents: 1 When Octane · 2 Running it (the interactive session) · 3 The production architecture · 4 Converting the
scene · 5 The render config (realism ≤ 2×) · 6 Sampling: what works, what doesn't · 7 Realism ladder verdicts · 8 FKL in
Octane, then sequences · 9 Timings · 10 Open questions · 11 Verified traps

## 1. When Octane
- **Finals go to Octane for the light, not for speed.** Octane carries sun and sky through glass and clear or smoked
  acrylic (a cover, glazing) and chrome cleanly at 1024–1536 spp. Cycles reaches the same transport only unbiased, and
  then with fireflies everywhere. With both engines unbiased they match (measured: frame ΔE00 ≈ 2.5–3.3; a region
  under a glass cover 16 → 4). The production differences are Cycles' own biases (`cycles-production.md` §5).
- **Cycles stays for everything iterative:** workstation previews, look-dev, grey box, compositions, FKL previews.
- Compare engines 1:1: matched light (grey-card calibration first), the same GPU count on both sides, matched noise.

## 2. Running it (the interactive session)
- **On a Windows node, Octane jobs must run inside the logged-in console session (Session 1).** Over plain ssh a job
  runs in Session 0; the add-on ships meshes and packed images through `Local\` shared memory, which the server
  (Session 1) can't open, and the render silently shows only the environment. Launch through a one-off interactive
  scheduled task (`schtasks /create /it /sc once` → `/run` → `/delete`) wrapped in a script that logs to a file and
  writes a done marker.
- Leave out `--factory-startup` for Octane (it disables the add-on). Cycles jobs on the same node keep it.
- `scene.octane.prefer_image_type = "HDR"` gives 32-bit scene-linear Rec.709 (imager bypassed); DEFAULT returns 8-bit
  sRGB. Import one small harness in every job that sets HDR + 32-bit ZIP EXR and times every stage.
- `scene.octane.devices` is ignored; the server's preferences choose the GPUs (all by default).
- Start OctaneServer in the console session with a one-off `/it` task. Restart it only under the site's standing
  policy (recovery restarts by the overnight supervisor, `render-supervision.md`); otherwise ask the user.
- `stop_render()` can't be skipped between two renders in one Blender session: the second hangs
  ("MapViewOfFile failed: 5").

## 3. The production architecture
**ONE converted Octane master scene + a small animation pack per shot, applied in ONE kept-alive session.** Measured:
a pack costs seconds and kilobytes per shot; converting each shot's own blend costs minutes and gigabytes (≈ 13× the
time, ~10⁵× the disk).

| Step | Where | Output |
|---|---|---|
| 1. Build the Cycles side once (Blender `-b --factory-startup`, CPU only) | workstation | the packed master source, the light states as JSON, the object list |
| 2. Convert once (converter + fixes, bakes the render config) | node, interactive session | the Octane master |
| 3. Bake a pack per shot (`fkl`, `seq`, `val`) | workstation | one JSON per shot and kind |
| 4. Drive the packs | node, interactive session | 32-bit EXRs |

- **The master build** runs the approved shot harness read-only: the master model, the rig, the labels, the material
  fixes, blackbody emitters, the scene audit's global off list hidden. Nothing per shot is trimmed there: every per-shot
  hide comes from the pack. Textures capped at 2048 (the converter caps 8-bit images at 1024). Remove drivers the
  converter can't carry and bake their values per frame into the pack. Every light state's Cycles parameters go to JSON.
- **A pack** is one JSON: per frame the camera (loc, rot, lens, focus, f-stop, shift, aperture), the rig and mechanism
  channels, driven values, state-dependent materials (an indicator), the hidden list (only where it differs from the
  pack default) and the light state; per pack the frame range, key frames, haze radius and notes.
  - `fkl`: FIRST / KEY / LAST exactly as the approved stills.
  - `seq`: the whole shot at 24 fps. The camera runs through FIRST → KEY → LAST on one path parameter s(t) (a
    non-negative mix of velocity profiles, so the move can be moving on frame 1 and land on LAST at zero velocity);
    each camera parameter is a monotone Hermite in s. The product's mechanisms follow their own schedule (§11).
  - `val`: one validation frame with an explicit hidden list.
- **The driver** keys each pack on its own frame block (1000·(k+1) + f). Before each frame it applies the frame's static
  state where it differs from the last: visibility, set moves, state-dependent materials, the light state (sun
  direction, colour and calibrated power; sky power and tint; lamps; state-dependent emitters by their reference power),
  the haze radius. One `start_render`, a delta sync per step, one stop at the end.
- **The kept-alive step:** `RenderEngine.frame_set` + the add-on's own `render_update` delta sync, wait for max
  samples, write the EXR with OIIO. Validated against stock `-a` frames: the difference equals the noise floor between
  two independent renders, and frame-to-frame noise decorrelates identically. It uses a private add-on API.

## 4. Converting the scene
Use a Cycles → Octane graph compiler with an exact OSL port of Cycles' noise and hash. Production options: bump OSL
scale 1.0; anisotropy sign measured per material; no light blocker on glass (Octane carries light through it);
band-limited bump.

Converter bugs to check at FKL on every new scene:
1. **Emission colours > 1** are clamped by Octane's RGB socket (an indicator loses half its luminance): normalise the
   colour to max 1 and carry the factor in the power.
2. **BOX-projected images** become one flat XY projection (streaks on vertical faces): bake Cycles' exact box mapping
   into a UV layer made the active render layer (Octane UV set 1).
3. **Prints mapped by Generated / Object coordinates** baked into UV sets 2/3 are ignored by Octane, so the prints
   vanish: when the vector is an affine map of object-space P, build an OSL projection that evaluates it.
4. **Point lamps** → Octane sphere lights with blackbody emission, kept at energy 0 so the light rig powers them per
   state.
5. **Haze radius per shot:** the environment medium is a camera-centred sphere; set its radius to the farthest interior
   point the camera sees over the shot + 0.5 m (a 48 × 27 ray grid at FIRST / KEY / LAST, glass as the boundary), so the
   boundary never crosses the frame and the outdoors isn't fogged.
- **State-dependent emitters** (lamps, screens, neighbours' windows) are 0 in a daylight state, and the converter builds
  no emission for zero. Convert them at a reference state where they are all on, and scale by state in the driver.

Calibration facts:
- Sun (measured): Octane directional power ≈ 0.48 × the Cycles sun strength in W/m² for a 3700 K sun given as RGB
  (1, .604, .304), with the light-transform link on (without it the add-on points the sun straight down); within
  0–3 % on grey patches. Re-check for another colour.
- HDRI: export through OIIO (Blender's `Image.save` sRGB-encodes it: the sky comes out ≈ 4× dark). Rotation: §11.
- Texture emission with surface brightness on and power P = radiance P × colour, 1:1 with Cycles strength.
- The engine switch alone doesn't convert materials (a default Principled becomes a default Universal, albedo 0.7);
  lights emit from an Octane emission node, not the Blender power.
- Octane OSL constant-folds signed-int overflow wrongly (the Cycles hash): pass a runtime seed. Procedural micro-bump
  glitters: band-limit bump noise to 0.1 mm. Object Info Random is exact
  (hash_uint2(hash_string(name), 0) / 0xFFFFFFFF).
- **Added lights** (`lighting.md` §5): blackbody emission with Normalize on, Surface Brightness off (it carries an extra
  7/π), Double Sided off for cards; out-of-frame sources Camera Visibility off and Visible on Specular on; one Light Pass
  ID per Cycles light group. No published W → Octane power factor exists: calibrate once (a 1 m² emitter at 5000 K, 2 m
  from an 18 % card, linear EXRs from both engines; solve the Octane power; re-check at 2700 K and 6500 K) and record
  the factor in the driver. Analytic Quad / Disk / Sphere lights are less noisy than mesh lights. Portals only with the
  PT kernel, covering every opening.
- Unsupported in OSL: Voronoi and Wave textures fall back to none. Generated coordinates or Object Info shared by
  hundreds of meshes (instanced dressing) take the first mesh's values. Check them at FKL.

## 5. The render config: "realism ≤ 2×" (realism within ~2× production time; called the realism config below)
| Setting | Value |
|---|---|
| Kernel | Path tracing, coherent ratio 1.0 + static noise, 1536 spp, adaptive off, no denoiser |
| Transport | GI clamp 100, diffuse / specular / scatter depth 16 / 32 / 16, caustic blur 0 |
| Metals | Universal "RGB IOR" on parts whose photo-matched F0 ≥ 0.85 (aluminium: (1.56, 7.71) / (1.02, 6.63) / (0.63, 5.46)); "Artistic" elsewhere |
| Acrylic (PMMA) covers | IOR 1.4917, roughness ≥ 0.03, absorption; **no dispersion** |
| Windows | thin wall + fake shadows: measured sun transmission 0.887 against the physical 0.891, already right |
| Air | environment medium: density 0.005 (0.003–0.01), scattering 1, absorption 0.05, invert absorption **False**, Schlick 0.7, radius per shot |
| Emitters | blackbody lamps (≈ 2700 K) and practicals; indicators as a black body at their approved luminance (a red LED ≈ 1400 K) |
| Output | `prefer_image_type = HDR`, 32-bit ZIP EXR, imager neutral |

Measured against the fast production config (§6): ≈ 1.55× the time, flicker 1.55× and sizzle 1.24× (still clean, no
blotches), ≈ +10 % frame light (the unclamped light). A maximum-realism config (GI clamp off, 3072 spp, coherent 0.5 +
static noise, cover dispersion) costs 3.4× the realism config for the same look: not worth it.

## 6. Sampling: what works, what doesn't (sweep at 540p kept-alive, confirm at 1080p on 10 frames)
**Works:**
- **The kept-alive session:** ≈ 4× faster per frame than stock `-a` at PT 1024 (stock pays a ~60 s kernel JIT compile
  and a ~26 s stop every frame; the session pays them once per chunk).
- **Coherent ratio with static noise ON:** 0.25 / 0.35 / 0.5 / 0.75 = −15 / −19 / −26 / −38 % time at the same noise;
  1.0 + static noise −57 %, with flicker equal to Cycles production. Without static noise, coherent 0.75 flickers 4.3×
  (blotches).
- Static geometry is cached from frame 2 (sync ≈ 10× faster, near zero kept-alive). Resource cache 'All'.

**Don't:**
- Adaptive sampling: it engages (bright smooth areas converge; dark glossy lacquer never does) but at matched noise
  nothing beats fixed spp. Prove any sampler with the noise pass (`use_pass_noise`), never by the setting.
- NRC: noise × 4.3 at × 4.8 time.
- GI clamp off for production: noise +48 % (fireflies).
- Depths 3/8: −9 % time for −4 % light (bias).
- Direct Lighting kernel: biased (ΔE00 ≈ 9). PMC: 2.3× time (reference stills only).
- The AI denoiser (or Octane's OIDN) on realism frames: it erased ≈ 25 % of fine detail energy (grooves, print) and
  flickers 1.7× raw. At production spp (256–512) it also leaves single-pixel speckle and blotchy mottling on dark
  lacquer and dark plastic; post OIDN on the raw beauty is clean (`finishing.md` §1). A driver option that writes the
  denoised beauty as RGBA, the raw beauty as extra layers and a header flag lets the finishing chain choose.
- Path termination power 0.1, parallel / tile samples ≠ 32, AI light, light sampling rates: no gain at matched noise.
- A bigger CUDA JIT cache: every session hashes a new kernel.

**Matched noise, honestly:** measure display RMSE against an independent 4096-spp reference rendered with a different
seed. Cycles is deterministic (seed 0): an image and a seed-0 reference share samples and under-report noise.

## 7. Realism ladder verdicts (one physical feature per rung)
- Only three things change the picture a lot: unclamped transport through glass (+4–10 % light), air (sunbeams, +4–5 %
  light at σ 0.005) and true caustics. Spectral sun, dispersion, measured metals ≤ 1–2 ΔE00.
- **Photon kernel: excluded.** Against a high-spp PMC reference it over-counts (frame 1.76×, up to ≈ 12× on some
  surfaces); PT's light through glass matched PMC within ≈ 3–7 %.
- **Dispersion only on a hero glass part, and not with coherent 1.0:** the pair gives coloured blotches
  (per-wavelength paths); on window glass dispersion only adds chroma noise.
- **Real window slabs under PT** block the direct sun (−15 %); keep thin wall + fake shadows.
- **Haze bug to avoid:** absorption (0,0,0) with invert on means σa = density (smoke, albedo 0.5, about half the light
  gone). Use the §5 values and read them back.
- A blackbody sun changes calibration, not realism: keep the calibrated RGB sun.
- Keep the thin-lens camera (the Realistic-lens camera has fixed preset lenses; post owns lens character).

## 8. FKL in Octane, then sequences (a hard gate)
1. Bake `fkl` packs for one act; drive them; finish through the same look as the approved Cycles previews.
2. **Main checks every FKL frame itself** against the approved previews: 1:1 crops of prints and labels (the §4 bugs),
   anything under glass, dark glossy finishes (noise, mottle), the set, focus on the subject, region luminance ratios
   (Octane vs Cycles), the conversion warnings list.
3. Only then an explicit **"go" per shot or act** from the user. Agents stop and wait at this gate.
4. Sequences in kept-alive chunks of 20–50 frames (+~100 s fixed per chunk: cold frame + stop). Overwrite off,
   placeholders, one EXR per frame; the corrupt-frame check after any interruption (`render-farm.md`).

## 9. Timings (measured once on a four-GPU node, high-end consumer GPUs at 200 W, 1080p)
| Config | Per frame |
|---|---|
| Octane stock `-a`, cache All | ~120 s (sync ≈ 1 + startup ≈ 60 + sampling ≈ 30 + stop ≈ 26) |
| Octane kept-alive, PT 1024 | ≈ 30 s |
| + coherent 0.75 + static noise | ≈ 18 s |
| + coherent 1.0 + static noise (production) | ≈ 13 s |
| **Realism config** (1536 spp) | **≈ 20 s** (22–41 s warm with motion blur on a heavy set) |
| Max realism | ≈ 68 s |
| Cycles production, 4 GPUs on one frame / 1 GPU per frame × 4 | ≈ 10 s / ≈ 7 s throughput |

- **Startup:** ~75 s to first sample, ~95 % of it the per-session OSL JIT (cutting all OSL links: 74 → 4 s). Packed
  textures add ~15 s start + ~8 s stop (a few GP of images); a 3 M-triangle mesh ~10 s of first-frame sync; ~25 s fixed
  stop. The first frame of a pack ≈ 80–90 s; a delta sync ≈ 0.5 s per step.
- **Review rates (kept-alive, MB on):** The realism config at 512 spp (the animatic setting) 10–14 s per frame (lamp-lit, darker
  states ≈ 1.3× a daylight state); light PT 64 spp (diffuse depth 2, specular 6) ≈ 1 s sampling; Direct Light (diffuse
  GI, 64 spp) 1.5–1.8 s, no faster than light PT; a session start ≈ 100 s; a shot switch ≈ 25 s untrimmed. A 6 fps
  animatic costs ≈ 13 s per frame all-in. Plan review passes from these (`editing.md` §7).
- The driver's adaptive "plateau" stop stays opt-in: while a texture load held the sample count it wrote a frame at 1
  sample.

## 10. Open questions
- A point-light power factor (Octane blackbody power per Cycles point-light watt) must be calibrated (§4, §11
  Practicals) before any lamp-lit shots; a guessed one is off by an order of magnitude.
- OSL materials → native Octane nodes or bakes would remove most of the per-chunk startup.
- Anisotropy strength and sign: match each anisotropic material in isolation before the master bakes it.

## 11. Verified traps
Each was measured in production. Numbers are measured ratios.

**Motion blur in the kept-alive path.**
- The add-on samples objects at F−1 / F / F+1.
- `clamp_motion_blur_data_source` must be False, or the offsets collapse to 0 when frame_start == frame_end.
- Key the neighbours: FKL packs as brackets at F = base + 4f; sequences as contiguous frames with two margin frames.
- Turn on `use_motion_blur` for the camera and every rig mesh. The cost is +1.5 %.

**Emitters.**
- A black-body emitter with Surface brightness ON needs power = **27.4 × the Cycles emission strength** (Normalize on;
  1 m² quad over an 18 % card). An uncalibrated factor left an indicator 13× dim.
- Find glowing set emitters with an **emitter-only pass** (sun, sky and product emitters off; everything else as the
  beauty). UV-sample each emissive map on its objects to see which can glow at all.

**The converter's Specular = 2 × level over-lights rough dielectrics under grazing light.** It's a lobe-shape
difference, not roughness. Set Specular per material against the approved stills. Measured starting values: printed
paper labels 0.3, oiled wood 0.5, foliage 0.25; a dark lacquer at 1.0 reads ×1.25–1.55 (keep it if it helps the product
read). Match material names carefully: a substring rule ("Leaf") misses or catches the wrong materials.

**Asset-library window glass (a common kit-library pattern) is ONE reflecting interface.**
- In Cycles it is Mix(Fresnel 1.52 × (1 − Backfacing), Transparent, Glossy 0.8).
- A thin-wall Specular reflects at both faces, which lays a veil of the room over the view outside (outdoors ×1.2–1.3).
- Fix: Reflection ×0.5 and transmission ×0.975. Outdoors → 1.00–1.03, the room unchanged.
- The same pattern often adds a milky layer: Mix(a `_refraction` map at 0.95–0.98; a white Principled; the glass), a
  2–5 % diffuse veil. A single Specular drops it. By day the outdoors swamps it; with only interior lamps it is most of
  the pane's light (the window rendered ×0.14 without it). Put it back only with the daylight calibration re-checked.

**Random Per Island.**
- The converter's OSL folds Geometry Random Per Island to a constant 0.5, so every island looks the same.
- Bake Cycles' exact value instead: a DisjointSet over the mesh edges in order (union by rank + path compression), the
  root of each face's first vertex, then lookup3 `hash_uint_to_float`. This is pixel-exact.

**Light through a glass or acrylic cover.**
- Octane carries sky and sun through a cover (most of the light on what lies under it comes through the cover).
- Cycles blocks most of it: glass gets no direct-light sampling, and stills clamp indirect light.
- Result: whatever lies under a cover reads ×1.3–3.3 brighter and cooler in Octane. That is physically right; decide it
  with the user, don't "fix" it back.

**Driver.**
- **Encode the user's standing visibility rules as driver gates.** A rule such as "the glass cover is never missing"
  becomes a check at load (a pack whose hidden list names a protected object is refused) and per step (every protected
  object renders), logged per step. A rule held only in a brief is lost the first time a pack is regenerated.
- A shot built separately (a replacement, its own file) renders through the same kept-alive loop and finish chain as
  the rest, so its look matches its neighbours.
- `has_pending_updates` is not a restart. Detect a restart by the sample count dropping, or a large pack switch can write
  the previous frame.
- Take an "unchanged" shortcut only with the old full buffer on screen, and never on the cold start.
- A session can hang with the GPUs idle and the server healthy. Run a watchdog that kills the run (PID confirmed) and
  resumes, skipping existing frames.
- **The server itself can hang** after a GPU driver reset with every card still present: it keeps running and holding
  VRAM but refuses clients, and the GPUs sit at 0 %. Relaunching the client can't fix it: kill the server and the
  client (PIDs verified), start the server in the console session, then relaunch with skip-existing. The overnight
  supervisor does this by itself (`render-supervision.md`).
- The watchdog must read progress ON THE NODE and verify its kill. Reading a log's mtime through the workstation's SMB
  cache makes a live run look hung; `wmic` is gone from current Windows, so a `wmic` kill silently does nothing (use
  `taskkill /F /PID` or `Stop-Process` and check the process is gone). A relaunch that shares the server with a live run
  gives several clients and stale frames. Never relaunch while any driver process is alive.
- A pack that renders a subset of frames must list them explicitly.
- Node overrides of link-only pins (Bump / Normal) must unlink, not set a value.

**Sequences follow the product's official schedule, not the camera's s(t).**
- The shot list's mechanism channels carry each motion with its physics: eases on lifts, constant speeds on swings, a
  motor's run-down as ω₀·e^(−t/τ), steps on indicators (`camera-motion.md`, `editing.md` §4).
- The bake fails loudly if the stills' mechanism states or the audited cameras are missed.
- Stills can carry states that no continuous motion reaches (a spin angle chosen for legibility). Pin them at KEY, or at
  LAST where a print must stop legible.
- Stills composed on idealised geometry vs a motion played under a contact solver (a warped disc, a sagging part): prove
  the difference is only that known effect (the idealised solve at each still's own state reproduces the still), then
  accept it by name.
- Every bake takes the approved stills' own candidate data, not the current spec: a bake from the spec silently drops
  per-still extras (an added fill).

**Practicals: where the emitter sits inside the lamp's hardware.**
- Blender ≥ 4.0 point lights default to `use_soft_falloff = True`: an oriented disk through the centre. Off, it is a true
  sphere of the light's radius. Octane's emissive sphere behaves like the true sphere.
- In free space the two differ only within a few radii (r 3 cm: ×1.36 at 5 cm, ≤ 0.4 % beyond 45 cm).
- Inside a lamp's metal (cross-bars, sockets, switches) they are shadowed differently: measured ×1.27 on what the lamp
  lit directly and ×1.85 on its own shade.
- Measure a practical Octane vs Cycles with soft falloff on and off before blaming the converter. To match an approved
  soft-falloff look, carry a per-lamp factor; for a physical rig, put a small emitter where the filament is.

**Octane Mix material: Amount is the weight of the FIRST material (Amount 1 = all first).** Cycles' Mix Shader is the
opposite (Fac 0 = all first). A converter or a hand-built Mix that copies Fac inherits the inversion (symptom: a pane
meant to be clear reads milky; a shade meant to be 35 % translucent is 65 %).
- Rule: Octane Amount = 1 − Cycles Fac (or build the Mix with the sockets swapped). Never copy the Fac.
- A texture-driven Fac (a map at 0.95–0.98 with the milky layer first) inverts per pixel: use 1 − map.
- Audit every master for it: list every OctaneMixMaterial with what feeds First / Second and compare with the Cycles Mix
  Shader it came from (Fac, input 1, input 2).

**Per-shot HDRI.** Swap the world RGB image, rotate the spherical projection and set the power per pack. The rotation
that puts an equirect's anchor column u (the sun, or the glow) at compass azimuth az (scene +x north, +y west): Cycles
mapping Z = 180 − 360·u + az; Octane Rotation Y = −Z − 90. Prep: clamp the HDRI (MIN ≈ 60) so the sun light owns the
disc; paint the disc out entirely when the sun is set (blue hour); replace the ground (el < 0) by the sky's own
below-horizon mean so no photographed ground shows through a window. Match power on the approved states' sky brightness,
not on the photographs' stops.

**Diagnostics.**
- Compare engines at air 0: haze adds 0.02–0.11 to dark finishes and the outdoors.
- 256-spp A/Bs are unreliable on dark glossy areas (±15–30 %); judge at ≥ 1536 spp.
- Build the Cycles side of any comparison from the approved stills' own state; a job file from another path read ×2.8
  outdoors.
- Timings: §9.

**Share polling (macOS SMB).**
- A `[ -f path ]` on the share can say "missing" for about 30 minutes after the file lands (negative cache). Poll with a
  directory listing.
- Never let two finishers write one pack's outputs; ffprobe the clips.
