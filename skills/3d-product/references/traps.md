# Traps and API notes (Blender 5.2, Cycles, Octane, other kernels, OCCT, DaVinci Resolve, FigJam, render nodes)

Each trap is a tool or engine behaviour, the symptom it produces, and the fix. Numbers labelled "measured" were measured
once on a real scene; treat them as orders of magnitude. Add new traps under the tool they belong to, phrased for any
project.

Contents: Environment and shell · Blender 5.x API · Passes, EXRs and masks · Cycles light · Cycles materials and QA ·
Glass, caustics and haze · Other kernels · OCCT and build123d · Meshes, glTF, USD and kit assets · HDRI worlds, windows
and sun · Camera, lens and focus · Animation and motion blur · Look-dev, calibration and photo matching · Measuring
renders · Scenes, trims and render state · Octane · DaVinci Resolve scripting · Resolve looks (Fusion and OFX) · Grade
solver and grading · FigJam · Probing a setup · Agents, orchestration and permissions · Film light, grade, transitions
and materials · Prints and labels · Unattended renders · Sound and music · Production renders · History: Comfy Cloud and
diffusion passes

## Environment and shell
- build123d and cadquery can't share a venv (conflicting OCP wheels); uninstalling one breaks the other.
- python.org Python on macOS has no CA certs: use `certifi` (`ssl.create_default_context(cafile=certifi.where())`).
- download.blender.org is behind a Cloudflare challenge for curl; on a Mac use `brew install --cask blender`.
- **zsh does not word-split unquoted `$VAR`:** `blender … -- $SHOTS` passes ONE argument, and `for x in $L` / `set -- $L`
  loops once (it made directories with spaces in their names). Use bash scripts, arrays, explicit pairs or `${=VAR}`.
- The system `python3` lacks the project's packages (PIL, trimesh, numpy): run project scripts with the project venv's
  interpreter.
- `pkill -f` / `kill` by a `grep -E` pattern can match the shell running it (its own command line contains the pattern)
  and kill it. Find the PID, check its command line, kill by PID.
- A Write or edit that fails (e.g. the file wasn't read first) leaves the old script on disk: check the file before
  launching a long background run.
- A table or script edited with `str.replace` can miss silently. Assert every replacement, or rewrite the table whole.
- **Case-insensitive filesystems (APFS on the Mac, NTFS/SMB on a Windows share):** tags, packs or folders that differ
  only by case ("glb" / "glB", "b" / "B") are the SAME path: the later write overwrites the earlier one and renders
  land in one folder. Use case-distinct tags ("gl0" / "glA" / "glB"; "0" for "before").
- The macOS SMB client can hide NEW folders on a share for up to ~20 min from a polling loop (a listing of the parent
  refreshes it). Poll progress over ssh on the render node, not through the mount.
- Parallel lanes racing on staged inputs read half-written files (measured: "png inflate error -3"). Stage atomically
  (write to tmp, then `os.replace`) before the lanes start.
- macOS has no `timeout` command: use `perl -e 'alarm N; exec @ARGV' <cmd>` (or GNU coreutils' `gtimeout`).
- **`multiprocessing.Pool` in a script fed on stdin (`python - <<EOF`) loops forever on macOS.** The default spawn
  start method re-imports `__main__` from a file, and stdin has none, so every worker dies at start-up and the Pool
  respawns it: no output, a CPU busy for hours and an error log that grows without bound (measured: 9.8 GB in 19 h,
  unnoticed because it ran in the background). Put parallel jobs in a real script file, prefer
  `concurrent.futures.ProcessPoolExecutor` (it fails fast with BrokenProcessPool), and give every background job a
  time limit and a size check on its log.
- **Python modules:** a module run as the Blender script is `__main__`; importing it by name from a helper creates a
  second copy with its own globals (edits in `__main__` don't show there, and a helper that registers into the imported
  module registers into the copy: pass the registry explicitly or `update()` it). A helper module named like a library
  module (e.g. `comp.py`) shadows it when its folder comes first on `sys.path`. `from build123d import *` rebinds
  short names such as `M`: import your own modules under distinctive aliases.

## Blender 5.x API
- glTF imports in **metres**: light energy must scale with R² when the scale changes.
- After `mesh.transform()`, creating objects or changing `location`, call `bpy.context.view_layer.update()` before
  reading `bound_box` / `matrix_world` or composing matrices. Stale matrices put lights at the origin and rendered a
  grounded part as a half-arch.
- `Material.use_nodes` / `World.use_nodes` are deprecated (always nodes). The compositor is a node group
  (`scene.compositing_node_group`); the Composite node is gone.
- `Action.fcurves` is gone: use `bpy_extras.anim_utils.action_get_channelbag_for_slot(...).fcurves`.
- Edge Angle marks convex edges positive; Evaluate on Domain / Evaluate at Index are renamed FieldOnDomain /
  FieldAtIndex; the default camera clip start of 0.1 m clips macros.
- `light.volume_factor` is EEVEE-only. In Cycles, keep a light out of volumes with `object.visible_volume_scatter = False`.
- EEVEE loses emitters seen through glass. OSL custom cameras render corrupted frames on Metal (CPU / OptiX only).
- Re-importing the same glb shares mesh data, so baking transforms on the new copy moves the earlier copies (parts sank
  or vanished). Give each import a private mesh copy when `mesh.users > 1`.
- After `bpy.data.objects.remove`, drop the object from every Python list too; a later access raises
  `ReferenceError: StructRNA … removed`.
- A cached node group dies when the scene resets between specs: revalidate caches before reuse.
- A camera at elevation 90° is degenerate for `to_track_quat`: use 85°, or build the orientation without a look-at.
- `world_to_camera_view` z is planar depth along the view axis, and Blender focuses a plane: set `focus_distance` to
  (point − cam)·forward, not the Euclidean distance.
- `image.copy().scale(...)` scales an in-memory copy, and Cycles renders that dirty buffer, not the file: usable for a
  camera-ray-only blurred world while lighting keeps the full map.
- Keyframes on a socket that is driven by a link do nothing (an emission ramp keyed on Strength while a gradient fed
  it): key the input the shader actually reads.
- Finding objects by a name substring picks the wrong ones ("Glass" matched a lamp's bulbs, and a kit room kept every
  window pane in one object): select by measured geometry (jambs, bounds), not by name.

## Passes, EXRs and masks
- Pass names: `Diffuse Color`, `Glossy Direct`, `Object Index` (not IndexOB; look up both), `Depth`, `Noisy Image`,
  `Combined_<group>`. Blender writes a multi-part EXR: read every part.
- Cryptomatte EXR layers use lowercase r/g/b/a: a loader that sorts channels gets a,b,g,r (ids ↔ coverage swapped). Some
  manifest hashes decode to NaN: map ids with a dict over `np.unique`, not `searchsorted`.
- The Depth pass has inf in the sky: casting to float16 overflows. Clip before saving.
- Depth under volumes and DOF is speckled per pixel. Clean it (grey-closing on disparity, or a per-bin median) before
  deriving focus / CoC masks; a Gaussian blur of a CoC map is wrong too (in-focus close-ups turn to "defocus").
- **Light groups:** light-group passes are not denoised: scale each by `Combined / Noisy Image`, or denoise each group in
  the compositor with albedo and normal. The ratio trick amplifies grain in near-black glass. The groups sum to the
  beauty only if **every** emitter (practicals, emissive parts, emissive props added later) sits in a group: sweep for
  emission after building, or the comp loses them.
- An emitter under glass shows up in transmission paths, not in the Emission pass: use its light group.
- A mask that counts every object with index > 0 as the product includes the set when set pieces carry an index (and
  curve objects at the frame edge). Reserve index ranges (product 1 … n, set ≥ a fixed offset, or set = 0) and build the
  product mask from the product range.
- A metric that needs a pass (a product-L* anchor from Object Index) works only on renders that write that pass: preview
  EXRs often don't.
- A frame can be all product (macros): guard percentiles against empty masks.

## Cycles light
- **Spot power is per 4π sr:** widening the cone at fixed power *adds* light. Specify flux.
- **`use_soft_falloff`** (on by default since 4.0) makes a point light an oriented disk through its centre; off, it is a
  true sphere. In free space they differ only within a few radii, but a practical's light placed inside the lamp's
  hardware is shadowed differently (measured ×1.3 on the pool, ×1.9 on a shade). Decide it per practical; any engine
  port with sphere emitters sees the "hard" version.
- Small area lights have huge radiance: a few mW on a 4 × 120 mm strip grazing rough metal was still a band.
- Glossy floor + back light = a sheen band behind the product; macros go in a void; rims use light linking.
- A backdrop card a few metres back is hit by the frame's top rays before the floor: put it ~20 m out and wide. A
  dark-field floor patch must be sized from the camera frustum, or its edge shows.
- **Product-only light linking is the biggest CG tell:** no bounce, no contact shadow (measured: 38 % of a frame digital
  black). Use set-only twins. A light linked to "the product" also includes every other imported model unless set
  pieces are marked as set.
- Rebalancing widened sources on the product's p90 key luminance spreads the glossy highlight, boosts the lights ~3
  stops and kills the mood. Rebalance on the frame's target, not on a highlight.
- Practicals mirrored in a glossy plinth read as light shafts: make the plinth non-glossy there, and place practicals
  where the camera actually looks.
- Emitters behind refractive light pipes barely light the set (caustic paths). Add a hidden area light at the emitter
  face aimed at the surface as the spill proxy, and say so in the caption.
- Fills faked with emitters shaped like objects (cloths, sleeves) in shade measured 16–166× the shaded surface beside
  them, as bright as a white card in full sun. Every fill is a real surface lit by real light, checked in the
  scene-linear EXR (in sun ≤ ~1× a sunlit white card; in shade ≤ ~3–4× the local shaded surface).
- A blue-hour frame lit by weak practicals gets lifted by the grade into a grey day. Make the lamps the key in the
  render, and set camera WB to 3800–4800 K so the window goes blue.
- Dusk and low-light shots render crushed (product L* medians 3–8, measured) when their light isn't planned in the spec.
- Look-dev energies from first guesses ran ~4 EV hot: calibrate powers on 2–3 frames before rendering a set.
- Cycles has zero natural vignetting: add it in post.
- The denoiser blotches dark rough metal at 64 spp in motion; use 128 for macros.
- Adaptive-subdivision displacement at 1 px in a close-up ran out of GPU memory on Metal: 2.5 px for close-ups, off for
  extreme close-ups, `max_subdivisions` 8.

## Cycles materials and QA
- AgX bleaches bright 2700 K blackbody to peach: use a saturated amber emission colour. AgX also desaturates bright
  saturated key colours: judge hue in the finishing grade, not in AgX look-dev.
- Black anodising reads silver under an overlit floor: it only shows what it reflects.
- A perforated grille shader with holes below pixel size averages to its land colour: at 0.62 metallic it reads as a
  white box. Use ~0.40 for anodised aluminium.
- Oiled wood from a scanned veneer mirrors the window at grazing angles and reads as paint: floor its roughness (~0.42).
- Kit material names lie about colour (a "walnut" was a pink cherry-like albedo): measure the base colour's linear mean
  before building a hero support on it.
- A material map keyed by part name must match the importer's case (some pipelines lower-case names): a miss silently
  shows the importer's default (vertex-colour) material.
- **Zebra QA:** a strip light reflected in a small blend can be < 1 px, so zebra tunnels need wide stripes; reflected-ray
  zebra shaders give flats no stripes (use a physical tunnel). In an end-on tunnel (axis toward the camera) the stripes
  show a straight split down the middle: that is the tunnel's axis, not a crease. Confirm with a 45° tunnel.
- Glass light pipes (volume absorption, frosted walls) render far slower than metal: budget them separately and
  look-dev at ~96 spp first.

## Glass, caustics and haze
- **Cycles 5.2 has no dispersion** (no input, no kernel code). An RGB split takes three copies; spectra need LuxCore.
- **Caustic killers:** `sample_clamp_indirect` (a clamp of 10 removed 95 % of focal energy, measured), Filter Glossy > 0,
  OIDN on sparse caustics, a radius-0 light. For glass: clamp 0, Filter Glossy 0, lights ≥ a few mm, ≥ 256 spp before
  denoise.
- **Small lights behind glass are invisible to path tracing** (a 6 mm LED, dichroic shadows): use a bigger light,
  LuxCore, or a light inside the glass. Light behind glass seen through glass (S-D-S) defeats BIDIRVM too.
- **Principled transmission tints on the way in and out** (tint² per pass): a smoked glass tint of ~0.32, not 0.08.
  Base Color tints glass like cellophane (thickness-blind): tint with Volume Absorption, σ = density·(1 − colour)/m.
  Principled Volume's Color is *scattering*.
- Plan a tinted colour at the viewing path length, not face-on: longer paths drift hue (tangerine read salmon).
- A prism placed by eye can TIR the beam: solve its rotation for minimum deviation with every wavelength passing.
- **Thin window glass:** Transparent + Fresnel Glossy renders a black curved panel if back faces reflect (the Fresnel
  node inverts the IOR on back faces and returns total internal reflection past ~41°; with no refraction the ray
  ping-pongs to black). Multiply the Fresnel by (1 − Backfacing). A Glass BSDF pane blocks shadow rays and the interior
  stays dark; kit panes that drive transmission from a map do the same: mix in a front-face-only thin pane by that map.
- A camera looking through a raised tinted cover sees soft mush; a camera behind the product hides the cover entirely.
  Audit azimuths off the front.
- **Haze by optical depth** τ = σ × path length. A tall dense haze veils everything and glows from every fill: keep fills
  out of the volume. Measured: σ 0.35–1 /m for side-on beams in a tabletop set; σ 0.03 /m across a 10 m room is τ 0.3,
  brown fog, so interiors want ~0.006 /m. A side camera needs moderate anisotropy (g ~0.35): forward scatter (g 0.6)
  sends the light away from a side view.
- A beam volume filling a real window shaft is very slow at defaults (measured ~50 min per 1080p frame): raise
  `volume_step_rate` (4) and turn off reflective caustics in beam shots.
- A strip light reflected in rippled water clips at grazing Fresnel (0.35–0.6 on water) at a few W: keep it ≤ ~2 W.

## Other kernels
- Mitsuba / LuxCore see area lights as geometry: keep them out of the frustum (the black-wall bug). Procedural Blender
  shaders don't port to either.
- Mitsuba `llvm_*` variants need `brew install llvm`; use `metal_ad_rgb` / `metal_ad_spectral` on Apple Silicon.
- **LuxCore:** `fieldofview` applies to the long axis; film rows are bottom-up; pyluxcore segfaults in C++ teardown at
  interpreter exit, so end scripts with `os._exit(0)` (else macOS crash dialogs); `interiorior` with `cauchyb` is
  Cauchy **A**, not n_d; a `spot`'s `coneangle` is the *half* angle; area lights exported as two-sided quads double the
  light (make them one-sided, facing the scene); a matte floor vs Cycles' Principled floor made an 8× exposure mismatch
  (use `glossy2` ks 0.04); laser `gain` scales with beam area; `WaitForDone()` deadlocks with halttime (poll
  `HasDone()`).

## OCCT and build123d
- Fillet radius ≥ half a face segfaults (fork the build and clamp); fillets on sphere / cylinder lips and on booleaned
  lips fail at larger radii (try r, 0.7r, 0.5r and log each failure); `MakeFilling` with GeomAbs_G2 throws (enum bug);
  OCCT fillets are G1 (circular section).
- `Triangle()` raised a TopoDS mismatch: use a Polyline. Check a lens's edge thickness CT − 2·sag > 0 before revolving.
- Helical B-rep threads can take > 60 s: use a helicoid mesh insert.
- A knurl whose grooves run through the rounded ends of a cylinder made one boolean take 40 s: stop the grooves ~0.5 mm
  short of the fillets (a plain rim, as real knurled parts have).
- build123d 0.13: `fillet(vertices, r)` on a 2-D Sketch returns a *re-centred* sketch and can drop a joined bulge (blend
  concave corners with `offset(offset(face, +r, kind=Kind.ARC), −r, kind=Kind.ARC)`); `edges().filter_by(Axis.X)` finds
  nothing on a rotated box (fillet first, then place it); `Plane.YZ.offset(d)` + `extrude` can go the opposite way (move
  the part by its bounding box instead); `project_to_viewport(origin, up, look_at)` is orthographic HLR, `focus=` makes
  it perspective.
- `extrude(face, taper=deg, dir=-Z)` gives a clean drafted pocket wall; a `loft` between offset faces also works, but
  fillets on the taper are more reliable.
- Fillet selections by region can misfile an edge (an arc centre inside the wrong region): select by geometry (distance
  to holes) and chain-fillet whole loops.
- **SDF:** the textbook |a−b| polynomial smooth-min is only C2 on its centre line, and nested pairwise smax makes
  asymmetric "Y"s: use an even-kernel smin of order n and p-norm boxes. Ambient-occlusion masks need a true distance:
  normalise approximate fields, or cavities flood.
- A thin cylindrical cove shell seen from inside rendered as a black blob: build a cove as an L block with its concave
  edge filleted.

## Meshes, glTF, USD and kit assets
- glTF is Y-up. trimesh exports need the Z-up → Y-up rotation done by hand and `include_normals=True`, else Blender gets
  sideways meshes with recomputed normals; face winding must agree with custom normals. A code-CAD glb imported bare
  lies on its side: import through the step that bakes the conversion.
- Blender imports glTF with **QUATERNION rotation** (`rotation_euler` reads 0): motion-blur keys on `rotation_euler` are
  ignored until `rotation_mode = "XYZ"`. Unbaked, a Tangent node's `RADIAL` axis must be `Y`; after baking it is `Z`.
- **USD + MaterialX kits:** Blender 5.2's USD importer keeps geometry and material names but leaves Standard Surface
  node trees empty: rebuild each material from its own USD with `pxr`. Instanceable prims return no children until
  `SetInstanceable(False)`.
- Kit rooms are furnished: removing a piece leaves companions floating or inside a new prop. Probe every object inside
  new props' volumes after cuts. Names lie about size, content and colour (a "mug" was a 29 cm vase). Props can be baked
  into bigger meshes: cut by vertex region with bmesh.
- Rotating a kit block 180° maps local x [a, b] to world [cx − b, cx − a]: getting it wrong parked a building on the
  sun's line.
- A drop-to-support with a long ray reach lands props on their neighbours' tops: limit the reach and check contacts.
- Auto-grounding shifts every world coordinate: disable it when cameras are placed in world units.
- **Cargo (Kitbash3D) has no MCP.** Driven in the background, its search box ignores positional typing (clear it with ✕
  or type with `overwrite_existing: true`, then return); pages load late (take a second screenshot before reading a
  grid); a click on an off-screen card scrolls instead of opening. **Never reuse an `element_index` after the page
  changes** (a stale index pressed a Download button twice). The "Describe the Vibe" popup is AX-transparent: clicking
  its ✕ by coordinate presses the card underneath, so leave it open. Use one- or two-word searches.
  `~/.kitbash3d/cargo_v1.sqlite` table `DOWNLOADED_ASSETS` is the authoritative download log.

## HDRI worlds, windows and sun
- imageio has no .hdr backend in a plain venv: read HDRIs in Blender (`bpy.data.images.load` → `pixels`) to find the sun
  or window azimuth (φ = 2π(0.5 − u)), then rotate by θ = α − target (a Mapping Z rotation moves a feature to α − θ).
- An HDRI world is infinitely far away. A modelled floor or water plane under it re-reflects the map's near objects into
  endless columns with no contact line: show the map's own ground and let the support run out of frame, or cover the
  whole lower frame with the modelled surface.
- A near object in a panorama keeps its angular size at any camera distance: compose where the map's own composition
  works, not around the product.
- A 2k panorama is soft past ~24 mm (texels magnified 3.5–5.6×): upscale 4× with a wrap-padded seam, or use a long lens
  with real DOF.
- **Aim a sun by geometry**, the line from the window (or a gap between piers) through a point on the subject, and check
  it with an ortho plan render. Eyeballed directions landed 500 mm off, and a sun drifting toward a wall reaches props
  along it only through the brick.
- A low sun through a window whose glass starts just above a surface never lights that surface (the bottom rail and the
  reveal shade it): use ~+15° for frames that need sun on it.
- A tree exactly on the sun's line blocks low rays completely (a full shadow, not dapple): offset it so only the crown's
  edge crosses the beam. Tall city blocks blot out a 10–15° sun at 25–40 m: leave a gap on the sun's line, or raise the
  sun.
- Put mullions and window bars between the product and the camera axis, never directly behind the product.
- A cyclorama cove starts at back − bend: with its back closer than its bend radius the curve rises in front of the
  product and buries what stands behind the centre. Keep the back well beyond the bend (≥ 5/3 of it).
- A studio backdrop standing between the product and a window light placed behind it blocks the light entirely. QA and
  swatch views use no backdrop.

## Camera, lens and focus
- **Macro depth of field is millimetres** (≈ 2·N·c·(1 + m)/m²; ~2 mm at f/8 and 0.6×): focus "on the subject" leaves
  the rest of a deep subject soft. Split the depth and stop down within the diffraction gate (`fkl-frames.md` §2b,
  `scripts/macro_focus.py`).
- A glossy foreground in a macro mirrors the room behind the camera, defocused at any aperture (a beige smear that
  stopping down can't fix): choose the camera by a ray probe of what the mirror sees.
- 16:9 frames are 36 × 20.25 mm (sensor fit keeps the width): frame by vertical field = 20.25·dist/focal, or heads get
  cut.
- Macro in Blender is a pinhole: a "100 mm lens 110 mm away" is wide-angle with a 36 mm aperture. Use the working
  distance: focal = 36·dist/field, f-number = focal/pupil.
- Shift + fit: solve the fit unshifted, then apply the shift (else double counting).
- A framing target given as an offset from the bounding-box centre mis-frames silently when read as an absolute point:
  name absolute targets explicitly.
- **Renderers don't simulate diffraction:** Cycles' and Octane's thin lens render f/28–f/32 macros razor-sharp, where a
  real lens at N_eff 40–55 is diffraction-limited. Gate it: the named subject must pass √(CoC² + d²) ≤ 2 px, with
  d = N_eff/24 px @1920 (the geometric disc whose MTF at 1080p Nyquist matches the Airy pattern's). Choose N at the
  minimum; if nothing reaches 2 px, place focus better or reduce magnification (`fkl-frames.md`).
- **Blur on the sensor** is (F/N)(F/s)|d − s|/d. A focus gate built on the thin-lens magnification F/(s − F) over-reads
  blur by s/(s − F) (×3.7 at close-ups, ×2 at mid shots).
- Ray-cast from the camera to the subject before trusting a side or rear framing: props hugging the product block it.
- Camera-matching to photos: the solver's roll and Blender's `rotate_axis("Z")` have opposite signs (check one render
  against the photo first); few or one-sided landmarks slide the solve to an orthographic answer (f → ∞), so spread them
  in depth or pin f.

## Animation and motion blur
- QA on the generator misses what the saved file plays: check contact mechanisms on the saved file's keyed curves at
  sub-frames (≈ 240 Hz). Motion blur interpolates between frame keys inside the shutter: compare the key-lerped surface
  with the true one at sub-frames (`greybox-animation.md`, contact mechanisms).
- Motion blur spins a part about its bounding-box centre: an off-centre part needs an explicit pivot.
- A rotationally symmetric part shows no motion blur: give its print asymmetric marks.
- Check the pose at the rendered frame, not at rest: a rig that keys rotation 0 → 2·deg and renders frame 1 sweeps
  parts ±deg/2 around +deg, and an emitter placed out of frame at rest swept into view and smeared.
- Durations set before move sizes made most first-draft moves 2–5× over the speed limits: size moves from durations.
- **Match cuts:** a cut specified with the first shot's LAST at the end of an action and the next shot's FIRST mid-action
  made the part jump back (measured 41°); first drafts also replayed actions across cuts, and one side of a shared-plan
  match left the plan. Split actions at the cut; check pose continuity and the shared framing.
- Aperture ramps, lens swaps and fill-fitted LAST frames (a hidden dolly) used to join two approved comps into one move
  are rejected by the motion audit (`camera-motion.md` §0).
- A shape key with a driver makes the part a deforming mesh (re-exported every frame by some engines): bake it or carry
  its value in the animation data.

## Look-dev, calibration and photo matching
- A literature material recipe can be right in **shape** and wrong in **energy**: test it in isolation (black world, one
  light), then in the set.
- A research-measured bump can be invisible in the render, and one that matches at grazing looks like sandpaper
  head-on: calibrate on swatches at the photo's mm/px under the photo's light, one variable per swatch, pass them by
  number in both views, then re-judge any mottle or bump at the closest planned framing with two seeds (a photo-scale
  mottle read as blotches in a close-up).
- Dust specks at 0.35 grey read as white stars on black lacquer; 0.2 grey with roughness 0.75 matches photographed faint
  specks (they brighten in the sheen, not in diffuse light).
- **Dark glossy or anisotropic surfaces** (a grooved disc, brushed metal): a white room or a huge overhead panel lifts
  the whole surface grey (the anisotropic lobe sees it everywhere). Use a camera-invisible overhead flag (a black card
  with a hole for the lens), and match the photo's light size before judging a material. A 45° softbox gives a broad
  sheen; a narrow strip at about 25° gives a wedge.
- Photos of an old unit show age (dust, bloom, pitting, dulled plating): decide intent vs age with the user; render the
  finish as designed and keep age as a switch.
- **Drawings and patents:** a perspective figure can be printed rotated 90° (read sideways it suggests the wrong hinge);
  scans sit 1–2° off (deskew before measuring); a double line is a step seen from above, not a gap; lines are 5–12 px
  thick, so measure their centres.

## Measuring renders
- Cycles is deterministic (seed 0): an image and a seed-0 reference share samples, and RMSE under-reports noise.
  Measure against an independent seed.
- Metal's first render in a session differs from every later one (mean ΔE00 ≈ 0.1): discard a warm-up render before A/B
  tests.
- A preview denoiser shows detail the path-traced final doesn't: compare final and preview before writing a caption.
- To find a mystery highlight, render once per light at low spp (four 24-spp renders beat guessing).
- Never trust a caustic / photon kernel without an unbiased reference: one over-counted by 1.8–12× per region
  (measured).
- A render driver's adaptive "plateau" stop wrote a frame at 1 sample while a texture load held the sample count: keep
  plateau stops opt-in and check sample counts in the frame metadata.

## Scenes, trims and render state
- **A per-shot override can undo a master change:** packs or shot files that swap an image or material per shot
  silently brought the old art back after the master was updated. Search every override list for the old asset and
  version those too.
- A bounding-box-in-frustum trim changed nearly every shot (worst mean ΔE00 20, measured): it drops the outdoors and
  everything glossy or glass parts mirror. Use the ray-cast audit (`scene-optimisation.md`).
- Unseen objects can still light a shot (a street and a floor slab together lit a room from below). Never trim the
  enclosure or the outdoors.
- A freshly saved blend for a subset of frames dropped the outdoor objects that shade the window: frames came out 2–9 %
  brighter (one 2×). To change one thing in an approved frame, re-render its original blend with a load-time script.
- Multi-GPU Cycles on one frame can be slower than one GPU (a 16 GB scene uploaded per device): measure before assuming.
- Cables and leads have sharp bends where they drop behind furniture: tuck them in rear or side views.
- Copying a finishing pipeline: rename its output prefixes (LUTs, plates) first, or the copy overwrites the original's
  files.

## Octane
Facts for OctaneBlender / OctaneServer 31.10 on a Windows render node; the production method is in
`octane-production.md`.

**Running it**
- **The thin-lens aperture is the pupil RADIUS in cm** = f/(20·N), f in mm (100 mm at f/8 → 0.625). A diameter there
  halves the depth of field. Verified on 31.10; re-verify on another version with a defocused point.
- **The server can hang after a GPU driver reset** with every card still present: it holds VRAM, refuses clients, GPUs at
  0 %. A client relaunch can't fix it: kill server and client (PIDs verified), start the server in the console session,
  relaunch with skip-existing.
- The in-render AI denoiser leaves single-pixel speckle and blotchy mottling on dark lacquer and dark plastic at
  256–512 spp; post OIDN on the raw beauty is clean. Keep the raw beauty in the EXR when testing it.
- Run Blender jobs in the logged-in session (Session 1). Over plain ssh, Session 0 can't reach the server's shared
  memory and renders only the environment.
- Set `prefer_image_type = HDR` for linear EXRs. `scene.octane.devices` is ignored: the server preferences pick the GPUs.
- `stop_render()` can't be skipped between two renders in one Blender session: the second hangs ("MapViewOfFile failed:
  5"). That hang is the client's: kill only your own hung Blender, not the server (a hung server is the case above).
- **One Octane client at a time.** Starting a second Blender with the Octane add-on enabled on the render node, even for
  a read-only query in another session, connects to the same server and resets it: the running render stalls (GPUs drop
  to 0 %, the client's memory collapses) and never recovers. Query scenes with `--factory-startup` or wait for the render
  to finish; queue the next job on the previous job's done marker, never on a timer.

**Per-frame cost**
- Every stock render session JIT-compiles a fresh OSL kernel (~25 MB, ~60–73 s, a new hash every time, so no
  `CUDA_CACHE_MAXSIZE` helps; the converter leaves `a_reload=True` on OSL nodes) and pays a ~26–36 s stop. A per-frame
  `-a` job therefore costs ~2 min a frame. Render a chunk in ONE kept-alive session (delta sync): measured ~30 s per
  warm 1080p frame on a 4-GPU node.
- Static meshes are cached from frame 2. Only 'Reshapable proxy' or deform-modified meshes re-export.

**Sampling**
- Adaptive sampling "does nothing" until expected exposure matches the imager exposure (1 at a neutral imager, which
  is how finals render) and min < max. Prove it by the renderer's time against a flat-cap render and with the noise
  pass, never by the setting. Set it inside one complete spec after a reset: a value left over from an earlier session
  lingers in the saved scene (`cycles-production.md` §9.4).
- Octane applies noise threshold, min samples and expected exposure without restarting a running render: in a live
  sweep, force a clean restart for every same-frame step (hop to another frame and back).
- Coherent ratio 0.5 = −25 % sampling at equal noise; test ≤ 0.35 for flicker, with static noise. Coherent > 0 without
  static noise flickers (measured 4.3×); coherent 1.0 with dispersion gives coloured blotches.

**Transport**
- Window glass needs alpha / fake shadows, or the sun never enters an interior.
- Octane carries light through a tinted cover that Cycles (caustics off) treats as opaque: a real engine difference, not
  a migration error.

**Converting a Cycles scene (check each at FKL on any new scene)**
- **The Octane Mix inversion:** Octane's Mix material weights the FIRST socket by Amount (1 = all first), the reverse of
  Cycles' Mix Shader Fac. Converting Fac straight across inverts the mix (a 2–5 % milky glass layer became 95–98 %, and a
  night window read as a lit wall). Use Amount = 1 − Fac and audit every Mix in a converted master.
- **Don't assume any mix node's convention:** a Mix *texture* blending a normal map with flat at a nominal 8 % rendered
  at nearly full strength (sandpaper), the opposite of the Mix material's rule above (measured once). Render the map on
  and off and measure, or bake the strength into the map (scale the normal's xy, renormalise) and drop the mix.
- Emission colours > 1 are clamped by Octane's RGB socket (an LED lost half its luminance): normalise the colour to max 1
  and move the factor into the power.
- BOX-projected image textures convert to one flat XY projection (streaks on vertical faces): bake Cycles' box mapping
  into the active render UV layer.
- Prints mapped by Generated / Object coordinates and baked into extra UV sets vanish (Octane ignores those sets there):
  evaluate the affine object-space map in OSL instead. Generated coordinates / Object Info shared by hundreds of meshes
  take the first mesh's values.
- Point lamps need sphere lights with blackbody emission, kept at energy 0 so a light rig can power them per state.
  Emitters at 0 in the conversion state get no emission node: convert at a reference state where every emitter is on,
  then scale per state.
- The environment medium is a sphere around the camera: too big a radius fogs the outdoors (measured −53 % light), too
  small crosses the frame. Radius per shot = the farthest visible interior point + 0.5 m.
- Haze with absorption (0,0,0) and invert absorption on is smoke (σa = density, albedo 0.5): set invert off, absorption
  0.05, scattering 1, and read the values back.
- Octane OSL constant-folds signed-int overflow wrongly (Cycles' hash): pass a runtime seed. Procedural micro-bump
  glitters: band-limit bump noise to ~0.1 mm. Voronoi and Wave textures are unsupported in the OSL port.
- The directional sun needs its light-transform link, or the add-on points it straight down. Export the HDRI through
  OIIO (`Image.save` sRGB-encodes it: sky 4× dark). Octane environment rotation = −rz − 90.

## DaVinci Resolve scripting (21.1)
- Resolve must run in the logged-in session: on a Windows node, launch it with a one-off `/it` scheduled task, not over
  ssh.
- **Project colour settings:** `SetSetting` refuses colour-space keys until they are set in dependency order:
  `colorScienceMode` → `isAutoColorManage` → `rcmPresetMode` → `separateColorSpaceAndGamma` → spaces and gammas → DRTs
  → luminance. Read every key back. The timeline colour space string is `DaVinci WG`.
  `Timeline.SetSetting('useCustomSettings','1')` resets colour science.
- **Media:** single EXR stills import only as plain path strings and ignore start/end frame (import a 2-frame sequence).
  Loader EXR layer selection set by script is ignored: one file per layer / light group.
- **`AppendToTimeline([{..., "startFrame": a, "endFrame": b}])` treats `endFrame` as EXCLUSIVE:** passing the inclusive
  cut-out loses a frame per clip and drifts every marker placed from a running sum. Pass `b + 1`, check
  `TimelineItem.GetDuration()`, and place markers at `item.GetStart() − timeline.GetStartFrame()`.
- **Fusion comps:** live scripted Fusion edits don't render (save and `ImportFusionComp`); MediaOut wants the clip's input
  space; a `.comp` Resolve can't parse imports EMPTY and the plate renders through (rebuild from a fresh comp, delete
  the others, and verify every delivery against its numpy twin).
- **Renders:** `SetRenderSettings({...})` returns False and applies nothing if any key is rejected (H264_NVIDIA takes
  neither an int bitrate nor "Best" for `VideoQuality`): set keys in small groups and read the job back with
  `GetRenderJobList()` before `StartRendering`. One broken comp fails the whole job: parse the timecode from
  `GetRenderJobStatus()['Error']` and disable that item.
- Non-ASCII names (an em dash) arrive in the scripting sandbox as mojibake and can crash the result serializer: use ASCII
  names for bins, timelines, markers and files.
- `Folder` has no `SetName`: rename a bin by creating a new one, `MoveClips(clips, target)`, `DeleteFolders([old])`.
- Resolve's free and Studio apps have the same bundle name: ask the running app (`GetProductName()`).
- **Long sessions:** the project slows as scratch timelines pile up (measured 152 comps: 87 → 408 s; delete them between
  batches); Resolve bloats (35 GB after ~4 h and ~1,500 comp imports; imports 0.3 → 15 s each): build on the Media
  page, save and restart when builds crawl.
- A proof that the comp is live (delivery closer to the solved twin than to the gains-1 twin) is inconclusive when the
  gains move few pixels: compare on the changed pixels only, and rely on a chart's 4× gain proof.

## Resolve looks (Fusion and OFX)
The Colour-page API only sets LUT (from Resolve's own LUT folders), CDL, node on/off and DRX, so build every FX and look
as a Fusion comp: `ofx.com.blackmagicdesign.resolvefx.<Name>` + SetInput, save, `ImportFusionComp`. A batch of ~50 stills
builds in seconds.
- OFX main input is **`Source`**: `ConnectInput("Input")` returns False and the render fails later. Check return values.
- Fusion reads trailing digits as frame numbers: name still copies so they end in letters. Tool names must be unique in
  a comp. Use a saturated-magenta dummy so a comp that silently fails to apply shows up.
- **Native Fusion tools** (FileLUT, OCIO*, BrightnessContrast, ColorGain, Custom) process in DaVinci Wide Gamut linear,
  not in the image's numbers (a ColorGain of 1.2/1/0.8 on grey rendered 1.41/1.03/0.69): wrap them in CST V2 (DWG →
  Rec.709 linear before, back after). Identity chains pass, so plumbing checks never see it.
- CST V2 to a display gamma adds a scene→display OOTF even with tone mapping off: output the DRT to Rec.709/Linear and let
  RCM encode.
- `SetLUT` rejects LUTs outside Resolve's LUT folders; Fusion `FileLUT` / `OCIOFileTransform` take absolute paths.
  Blender's OCIO config loads in Fusion `OCIOColorSpace` (exact AgX / Filmic / PBR Neutral).
- ACES Transform OFX: input AP0 linear; the output is 2.4-encoded (decode with Gamma 1/2.4). The shipped ACES LMT "Kodak
  2383" CLF won't process: use the Film Looks 2383/3513 LUTs with a Cineon-log input.
- Film Look Creator has 238 inputs and every module ON by default: start from `GlobalPresetCleanSlate` plus the
  `*IsEnable` flags.
- Custom Tool: no `tan`; `^`/`pow` give 0; NumberIn clamps to 0–1; the second image is `r2/g2/b2`; `min()`/`max()` work.
- Glow and Light Rays thresholds are frame-critical in DWG/DI: sweep them per shot. Prism Blur's VignetteSize darkens the
  whole frame, and its aberration isn't radial (use LensDistortion with split R/B for lateral CA). ApertureDiffraction
  and LensReflections take their source from alpha: put a luma high-pass in alpha so big bright areas don't bloom, then
  reset alpha to 1.
- The Timeline node graph has 0 nodes by script (no timeline LUT). DRX is XML with hex blobs; `ApplyGradeFromDRX` of a
  grabbed still is exact.

## Grade solver and grading
- A KEY strip that reads as one gradient can still hide a warm-to-cold jump at a cut (the eye compares OUT with IN). A
  luminance-weighted mean-light colour missed one; measure the colour as displayed and grade the cuts
  (`finishing.md` §4b).
- **Bounds:** unbounded, a solver chases film highlight targets on glossy speculars (−3 EV, room ×13.5). Keep ±1.5 EV,
  room ≤ 8×, 4500–7500 K and soft highlight weights. Centre the exposure window on the light state's by-eye exposure,
  ±1.25 EV: a film curve runs 0.5–0.8 EV darker than AgX, so a ±0.75 EV window pinned wides at the bound.
- A target band can contradict the frame (a macro that is 80 % black surface can't reach a mid-tone median): judge each
  frame by the regime it actually shows. A golden-hour interior graded with a daylight regime flattens (+1.25 EV, sky
  ×4): use a low-key regime.
- A grade can't add contrast the light doesn't have, and a per-shot trim that hits its bounds is a light problem (a
  ~2-stop practical / exterior imbalance between neighbours can't be graded smooth): fix the light and re-measure.
- White balance can't undo chroma pushes: after printer lights or a CDL slope, a von Kries WB fixes neutrals but a
  sunlit label stays neon.

## FigJam (use_figma)
- Connector labels need `c.text.fontName` set before `characters` (the default font is empty).
- ShapeWithText clips unless height ≥ the measured text height (Inter Medium 16, 150 %, width − 96) + 80.
- `upload_assets` → POST multipart `file`; images land as 400×300 FRAMEs named after the file: resize to the image
  aspect and reparent into sections.

## Probing a setup
- Cycles' `compute_device_type` is a dynamic enum: its items can't be listed from `bl_rna`; try each backend and catch
  the error (`scripts/probe_setup.py`).

## Agents, orchestration and permissions
- An agent that opened images in a browser via `file://` hung for two hours with no output. Read images with the Read
  tool or PIL; check a quiet agent's transcript timestamp and restart it with a narrower brief.
- A research agent rendering while the lead renders makes every build 10–20× slower (CPU/GPU contention): say "no GPU".
- The permission classifier can block a subagent's kill of its own leftover render or a render-server restart, even
  where the user pre-authorised kills (subagents don't see the chat). Main does it with the user's authorisation, or the
  user adds the allow rule; never route around it.
- Don't write files on a blocked agent's behalf without the user's OK (it launders the permission).
- Running scripts that write caches into another project's folder, or moving the build elsewhere to dodge a block, is
  blocked as modifying shared resources / a bypass: scope agents to their own folder and give the user the exact allow
  rules.
- Screenshots via computer use fail while the display sleeps; API calls and render measurements keep working.
- Probing YouTube frames: mid-roll ads replace frames, captions inside letterbox bars fool bar detection, and the JS tool
  times out at 45 s. `/analyze-youtube` handles all three.
- A note like "way too much DOF" is ambiguous (too shallow or too deep): confirm a note's reading before building it.
- **A subagent blocked by a permission check on work the user explicitly asked for is not a stopping point** (the
  user: "i did not ask you to stop there"). The lead does that work itself on the user's instruction; only if the lead
  is blocked too, stop and give the exact allow-rule text. Never ask another agent to retry a blocked action, never
  route around it. Likewise a download the user approved in chat: subagents treat relayed approval as no approval, so
  the lead does it or the user approves directly.
- **Hidden iteration before the first build:** an agent tuned a metric through seven unseen versions while the user
  waited ~40 min ("This is taking way too long"). Deliver the first complete build at once, iterate after; say so in
  every brief.
- **A rebuild instead of a version-up:** a replacement shot rebuilt through a new prep path came back warmer, softer and
  off its neighbours. Start from the approved file, prove it reproduces the approved frame (a pixel diff), change only
  what the note targets.
- **Duplicate wait loops:** an agent re-armed a wait loop every ~10 min without ending the last (seven piled up). One
  owner per watch; list background tasks and end duplicates.
- **Status before evidence:** "restarted" is not "rendering". Report counted frames, GPU load and file times; say "not
  yet confirmed" until new output lands; compute an ETA from the measured rate.

## Film light, grade, transitions and materials
- A night window that reads as a milky, glowing wall: a small diffuse or milky layer in the glass (invisible by day) lit
  by the interior lamps, or a converted Mix that weights the wrong input (the Octane Mix inversion above). Check every
  glass layer in the night state; the audience must see out.
- Light that runs backwards across a cut, or practicals that come on, go off and come on again, breaks the film's clock.
  Map the light to edit time monotonically and re-map it whenever the edit changes (`lighting.md` §9).
- A low sun may never reach a recessed subject (the product's own walls blocked it below ~6°, measured). Ray-probe the
  sun per shot before promising raking light; carry the sunset in the grade instead.
- A big bounce panel added to lift a dark shot becomes its key (measured: overshot the target L* by 1.4–2.3× and turned
  the frame orange). Rebalance the existing sky and practicals first, measured against the grade's target.
- A soft bounce seen in a low-angled glossy cover reads as a milky band; make fills reflection-invisible. A remaining
  pale band on a tinted cover at a low angle can be physical (internal reflection off its wall): diagnose by
  elimination, then accept it by name.
- Driving a grade with the neutral-pixel white point in mixed light: the least chromatic pixels sit where lamp and
  window cancel, so the point jumps between neighbours. Use the whole frame's light colour; weight content-dominated
  frames (a big coloured label) low.
- The grey renderer can't show reflection or transmission in transparent parts: a transition option judged in grey can
  look empty and be the best lit frame. Judge reflections only on lit KEYs.
- A raised or tilted transparent cover mostly transmits toward the camera; a flat one seen grazing mostly reflects
  (≈ 4× the reflection share, measured once). Search closed / flat states too before giving up on reflections.
- A strong abstract frame in the wrong product state (a cover closed while the story has it open) breaks continuity:
  check the story state before showing options as candidates (`transition-shots.md` §7).
- A camera behind the product hides its glass cover: audit azimuth off the front (> 100° fails unless the cover reads).
- Box-projected textures run a directional pattern (wood grain) along one world axis on every part (a top's grain ran
  front-to-back). Map per part by construction (`reference-detailing.md`, patterned materials).
- A brightening / desaturating chain applied to a wood texture turned one species into another: target the measured
  colour of the real finish instead.

## Prints and labels
- Some engines ignore an image's alpha: write flattened copies (holes in the old art's hole colour, outside the face in
  its edge colour), keep the RGBA master.
- Measuring a reference's type on an un-deskewed photo inflates long lines' boxes (~1° is enough): deskew first.
- Foil reads like flat ink unless its mirror ray finds a light: judge it at an angle that mirrors a lamp or window, and
  in motion.
- Type set per line drifts; lines of one class must share one size (the real object does).

## Unattended renders
- A watchdog that watches a process exits after a node reboot ("no process found"), and a queue script then moves to
  the next session and drops the rest of the run: one supervisor owns the run (`render-supervision.md`).
- Counting frames or reading a log's age through a network mount: the client's cache hides new files or makes a live run
  look hung. Count and time on the node.
- A vendor GPU tool's startup profile can restore full power after a reboot: re-apply the cap from the site's cap file
  at every logon, after the tool; never raise it from a script.
- Overnight watching by an agent costs credits and dies with the session: the user ruled it out.

## Sound and music
- **Generators ignore requested keys**, treat tempo as a hint (some within ~1–2 %, some ignore it) and never follow a
  varying tempo: measure key, tuning and tempo of every take (`sound-design.md` §5).
- A measured tuning offset (+20 cents) failed to reproduce on a second method; the music was at A440. Cross-check a
  surprising number before tuning anything to it.
- `rubberband -M <timemap> -D <dur>` can print "NaN … no time stretch will happen" and silently drop the time map AND
  the `-p` pitch shift. Assert the output's duration and tuning after every call; prefer one constant `-t` stretch.
- An assembler that trimmed the music to its texture stem's length cut the ring-out off. Lengths come from the music.
- A look-ahead limiter delays the master by its look-ahead (ffmpeg `alimiter`, 1 ms = 48 samples at 48 kHz): measure the
  offset against the pre-limiter sum and trim it, or the master is late against the stems and the picture.
- A layer normalised on its loudest event leaves its quieter events below hearing: measure each placed event, or
  normalise each before placing.
- A distilled ("turbo") music model ignored the brief's negative constraints (vocals and keys on an instrumental
  brief); some models end a piece early: ask for longer pieces and use the natural ending.
- Codec residue exposed in a decay ("crunchy", "vibrating") with no clipping: measure HF share, stereo correlation and
  wobble in the tail (`sound-design.md` §8). An AI listener did not hear it; the user did.
- A start texture (surface noise, hiss) left running after the last chord reads as a fault: textures only at starts.
- A video editor's scripting API may set only static clip volume and whole-frame fades (no volume curves, EQ or
  plug-ins): render the mix in code and host the stems.
- Mains hum (50/60 Hz and harmonics) in a room tone clashes with the music's key: notch it, or synthesise any hum in
  key.
- A cloud workflow host's model list can differ from published docs and research: dump its full node list before
  planning (per-node lookups can 404).
- Loudness curves time-stamped at the window's end (a live meter) lag their cause by half a window: analyse with
  centred windows so steps and dips line up with the picture's marks.

## Production renders
- **Blender 5.x multilayer EXR**: `image_settings.file_format = "OPEN_EXR_MULTILAYER"` no longer exists; set `image_settings.media_type = "MULTI_LAYER_IMAGE"` first; `file_format` is then `"OPEN_EXR_MULTILAYER"` (the only value it accepts). Light-group passes need it.
- **Blender Python, changing objects while iterating `collection.all_objects`**: the iterator stops early (setting `hide_render` on 114 objects touched 2). Iterate over `list(collection.all_objects)`.
- **Static noise ON on a moving camera** reads as dirt on the lens (the residual noise is screen-locked). OFF at ≥ 8k cap
  costs no visible flicker.
- **Inline PowerShell through ssh** (`$_`) is eaten by the remote shell: counts read 0 → false hangs → a shot marked done
  at 29 %. Script files on the node; prove the count on a known folder.
- **A network share caches a new folder as missing:** a run looked hung for 8 min and was restarted. Count on the node.
- **Driver version bumps vs the busy lock:** a lock matching one driver name can't see the next; match the family.
- **Pausing a queue:** a newline-separated PID list fails `kill` in zsh; orphaned launchers waiting on the lock race the
  restarted supervisor. Kill by single verified PIDs, list before and after.
- **Follow geometric normal** displacement cracks convex corners; use smoothed normals.
- **Re-solved auto-timing** cancels per-shot lifts; carry approved values forward (`finishing.md` §6).
- **A proof that shows nothing:** head-on light flattened a 10 mm relief; check with a difference map, then light it raking.

## History: Comfy Cloud and diffusion passes
Comfy and AI image passes left the pipeline; don't propose them. Their traps (Comfy Cloud API, partner nodes, hosted
image models, LoRA / σ scheduling, registration of re-composed frames) are not kept here.
