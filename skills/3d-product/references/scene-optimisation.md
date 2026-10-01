# Scene optimisation before any production render

A dressed set (thousands of objects, millions of triangles, gigabytes of packed textures) can need twice a GPU's memory.
This is how to make it fit and render fast without changing a pixel, and when not to bother. Measure before you trim:
trims pay only when a shot would otherwise go out of core.

## 1. The scene audit: hide only what no ray reaches, prove it by render
1. **Cast visibility over the whole camera path, per shot, without rendering.** Sample the path through the same timing
   curve the animation uses:
   - pass 1: every 4th frame plus FIRST / KEY / LAST, a 256 × 144 ray grid with a 2 % margin past each edge;
   - pass 2: every frame at 128 × 72 with a 3 % margin, for motion between pass-1 samples;
   - rays start at clip start, origins jittered over the aperture when DOF is on;
   - they continue through up to 8 transmissive / alpha / volume layers (glass, clear covers, leaves);
   - one reflected ray from every glossy, metal, glass or texture-roughness surface (+2 jittered for glossy and rough),
     and reflected rays continue through glass;
   - result per object, shot and frame: D (direct), T (through glass), Rs / Rg / Rr (reflection off sharp / glossy /
     rough surfaces). Honour ray-visibility flags and the per-frame hide state.
2. **Candidate list per shot** = objects no ray of any kind reaches, minus the rules:
   - **never the enclosure or the outdoors** (walls, floors, ceilings, beams, doors, windows, street, neighbouring
     buildings, trees, foliage), even when unseen: they shade and bounce. Measured: removing an unseen street and floor
     slab changed a shot's local light by up to ΔE00 ≈ 20; an unseen tree shades a window;
   - never product parts (they shade and mirror each other at close range);
   - never emitters active in the shot's light state (an unseen lamp still lights the room);
   - keep parts under 5 cm whose siblings are seen (small ticks and details fall between ray samples).
3. **Verify by group render** at FIRST, KEY and LAST: Cycles 480 × 270, 64 spp, fixed seed, the same texture cap on both
   sides. FULL vs FULL − list passes when mean ΔE00 < 0.5, p99 < 2 and ≤ 4 cells of the 4 × 4-binned image are above
   ΔE00 2. Anything that fails goes back in the scene.
   - Discard one warm-up render per session: Metal's first render differs from every later one by mean ΔE00 ≈ 0.1. The
     true noise floor is ≈ 0.02.
4. **A global safe-off list** (objects no shot's ray reaches: behind walls, other rooms) is hidden in every shot. Expect
   few: a glossy product, glass and metal mirror the room, and in a dressed interior most objects are seen only in
   reflections.
5. Re-run the audit whenever a camera moves, the set is re-dressed or the product model changes: the lists are keyed
   by object name.

**Typical savings (measured, dressed interior):** ≈ 40 % of the objects hidden per shot (median), but only ≈ 3–7 % of
the triangles, materials and texture pixels: most of the weight is in what the camera or the reflections see.

**Don't:** trim by bounding box in the frustum. It keeps anything with a bbox corner in view and drops the outdoors and
everything the product mirrors: measured, almost every shot changed at KEY, the worst by mean ΔE00 ≈ 20 (the view
outside a window gone).

**When not to trim (measured in an Octane kept-alive session, the master in-core at ≈ half the card).** Trimmed vs
untrimmed:
- warm frame and cold start: the same within 1 %;
- first frame after a shot switch: the trimmed session ≈ 1.45× slower (a switch toggles hundreds of objects and Octane
  recompiles them);
- peak VRAM: untrimmed ≈ +1 % of the card; images identical within noise.
Trims also carry a risk only a trimmed-vs-untrimmed render catches: a hidden object is absent for the whole shot, while
verification runs only at F/K/L (an object seen only in a reflection between the checked frames).
- **Rule:** trim for memory, not for speed. When the scene fits in-core, render untrimmed.
- Trims still earn their keep on the Cycles path when a shot would otherwise go out-of-core.

**Applying it:** toggle the hides at render time from the saved lists, never save them into the scene; a job builder
applies the shot's list to the untrimmed scene. In the Octane architecture the per-shot hides travel in the animation
pack; the master carries only the global list (`octane-production.md` §3).

## 2. Textures and GPU memory
- **Budget the card first** (e.g. 24 GB on a high-end consumer GPU). Capping alone rarely fits a dressed set (measured:
  capping at 2048 cut need by ≈ 30 % and the shot still went out-of-core at ≈ 2 min/frame). Trims plus caps until the
  shot fits in-core, then measure.
- **Cap set textures at load** (2048 px for Cycles jobs; the Octane converter caps 8-bit images at 1024). The product,
  its prints and labels and the HDRI keep full size.
- Packed images reach Octane as float RGBA buffers (16 bytes per pixel) through shared memory: a few gigapixels of
  textures cost ~15 s of Octane startup and ~8 s of stop per session.
- Denoise on CPU or not at all when a card is full: OIDN on a full card hung at a fixed sample.

## 3. Heavy geometry
- Find it before it costs: a 3 M-triangle prop costs ~10 s of first-frame Blender-side sync in Octane (cached
  afterwards). Hide it where the audit says it's unseen; otherwise keep it (never decimate the product).
- B-rep glTFs have 2 triangles per flat face; densify only faces that deform (`manufacturing-variation.md`).
- Octane re-exports only meshes that are "Reshapable proxy" or deform-modified. Keep shape keys, deform modifiers and
  animated modifier values off static objects; bake a deformation into the mesh or carry its value in the pack. Mesh
  type settings (Global / Scatter / Movable / Auto) behave the same.

## 4. Session and launch overheads
- **Cycles on a render node: always `--factory-startup`.** A user add-on (Octane) forced a full scene re-sync every
  frame: ≈ 10× the per-frame sync. (Octane jobs are the exception: they need the add-on.)
- **Keep the scene loaded.** Loop variants inside one Blender session; hundreds of packed images take tens of seconds
  to load.
- Persistent data on for Cycles sequences and preview loops (a camera-only change ≈ 1–2 s at 640 × 360).
- **Octane:** the kept-alive session (`octane-production.md` §3), static geometry cached from frame 2, resource cache
  'All', and OSL → native nodes or bakes where parity is invisible (cutting all OSL links took startup-to-first-sample
  from ≈ 75 s to ≈ 4 s). One converted master + packs instead of one converted scene per shot.
- Multi-GPU Cycles on one frame is slower on most heavy frames (each device uploads the whole scene): render one frame
  per GPU, frames claimed dynamically (`render-farm.md`).

## 5. Unused data (costs file weight only)
- Materials with 0 users and images used only by them: harmless at render, but they bloat packed blends.
- Zero-emission materials (strength 0, or 1.0 with a black colour: a common asset-library convention) compile no
  emission closure in Cycles and no emitter in Octane: no action. Texture-driven emission that is ~99 % black is a mesh
  light in Cycles: set Emission Sampling to None.
- Scratch blend copies pile up to 100+ GB over a study: list them and ask before deleting.

## 6. Gate before production
- Every per-shot list render-verified at FIRST / KEY / LAST; the global list verified on every shot.
- The shot fits in VRAM in-core (check `used_memory` in Octane's frame-buffer stats or the Cycles log).
- Per-frame time measured on a 10-frame chunk at the production config, and the total estimate written down before
  the queue starts.
