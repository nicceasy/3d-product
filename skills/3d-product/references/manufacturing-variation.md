# Manufacturing variation: no perfect plane, parallel or circle

Real parts are never perfectly flat, parallel or round, and a render that is reads as CG. The user's standard: natural
geometric variation driven by each part's material and process, applied where it would really occur, falling off
toward stiff transitions (edges, bends, bosses, mounts); **factory-new spec** (no age: no heat arch, creep, storage
warp or aged rubber); and **just subtly perceptible**, behind a level switch that can be dialled back.

## Procedure
1. **Evidence first, per part:** material + process → the deformation modes that process really makes (moulding warp,
   panel sag under its own weight, wall lean from draft and cooling, as-pressed dish and edge warp on a disc, ovality on
   a bent tube, play in guided parts) → an amplitude per mode, labelled [sourced / measured / derived / assumed]. Keep
   the evidence in a research doc and a spec file keyed by part and mode.
2. **Measure real units in photos:** sub-pixel edge fits; line straightness against a straight edge in the same frame;
   draft from the left–right silhouette slope difference on a level camera. Photos of old units show age (a heat arch,
   creep): the straightest specimen sets the factory value.
3. **Set amplitudes by finish, not size** (visibility is the finish's):
   - gloss shows slopes of ~10⁻³ rad as bent reflections;
   - satin metal shows ovality as highlight width;
   - matte paint shows nothing below ~0.5°: only silhouettes and gap widths.

   Textbook dish values of a few hundredths of a mm are invisible; pick per finish.
4. **Pick the operator per mode** (compare at matched peak amplitude in strip-light renders):
   - panel sag: a plate solve (cotangent-Laplacian biharmonic with clamped stiff edges);
   - a perimeter arch: a harmonic fill driven by the boundary;
   - wall lean: compact (1−q²)² envelopes;
   - a disc: analytic modes (dish about its support ring, k2 + k3 edge warp, track eccentricity);
   - a bent tube: the section's ovality formula;
   - assemblies: rigid pose offsets (keys in their guides, a floating chassis, a seat's roll).
5. **Densify only the target faces** (B-rep glTFs carry 2 triangles per flat face) and keep the original vertices
   exactly; level 0 swaps the original meshes back (bit-exact).
6. **Levels behind one switch, seed fixed:** 0 = off (default), 1 = factory-new, 2 = just perceptible. Flag any feature
   that level 2 pushes past factory / QC values.
7. **Measure perceptibility** by ΔE on the smooth regions of a fixed-light A/B render. Measured rule of thumb: p99 ΔE
   ≈ 1.8 (< 1 JND) is invisible at full frame; p99 ΔE ≈ 3 is just perceptible (a reflected window mullion visibly bends
   on a gloss panel).
8. **Validate:** protected interfaces (seats, hinge corners, tube ends) move ~0; no new interpenetration; parts that
   ride on a deformed part stay on it; coordinates finite; no flipped faces.

## Verdicts
- Evidence-per-mode with an operator per mode works.
- Don't: noise, or mixes of eigenmodes: they make window reflections wave.
- Don't: one operator for everything. A plate solve used for all modes put steps in wall lean at pockets, turned a
  disc's warp into a single bump and an arch into a uniform lift.

## Traps
- Densified planar faces inherit the glTF's flat-shading flag, and Blender ignores custom normals on flat faces →
  per-triangle "teeth" in strip-light renders. Set smooth shading on the re-filled faces.
