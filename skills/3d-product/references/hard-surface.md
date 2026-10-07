# Hard-surface modelling: continuity, representations, hard problems

How smooth a surface must be, how to prove it on screen, and which representation (B-rep, constructed sweep, SDF,
mesh boolean, SubD, displacement) to use for each kind of part. Tool behaviour (OCCT, build123d, Blender, Cycles) is
general; the verdicts come from side-by-side sheets on real hard-surface products.

## 1 · Continuity, as measured on screen
- **Renders see G, not C.** Reflection lines are one order less smooth than the surface:
  - A G1 join (a rolling-ball fillet) breaks zebra stripes at the tangent line, and a flat face's highlight ends in a
    hard blob.
  - G2, G3 and G4 all flow cleanly, and are indistinguishable at normal viewing distance.
- **The order only shows at the joins.** At equal visual size (the same mid-point offset as the arc it replaces), G2,
  G3 and G4 corners have near-identical curvature profiles. The order changes only how κ leaves zero: κ ~ s^(n−1),
  visible on a log plot.
- **Fairness beats order.** For Bézier corners, the inner-control-point spread c matters far more than the order.
  - c ≈ 0.25 gives one fair curvature peak.
  - c ≥ 0.5 gives two peaks, so a "G3" surface reads like a crude chamfer.
  - Target: monotone κ with one peak, and a footprint 1.3–1.5 × the radius it replaces.
- **Build Gn by construction.** A Bézier of degree 2n+1 with n+1 control points on each tangent line is G_n (verified:
  dκ = 0 for G3, d²κ = 0 for G4).
  - Sweep fair profiles along fair plan curves: exact normals, no fillet solver.
  - OCCT fillets are G1 only, and OCCT `MakeFilling` G2 is broken.
- **What to use where:**
  - G1 rolling-ball fillets on machined metal. That's what CNC parts are, and it reads right.
  - G2 on every visible gloss blend.
  - G3 where long strip lines cross big blends, or on rotating-stand presentations.
  - G0 only on the one hero edge the design language asks for (a deliberate sharp lip).

## 2 · Surface QA instruments (run on every model)
- **Zebra tunnel.** An emissive striped cylinder around the part, invisible to camera rays, with a chrome QA material
  on the model (parameters: radius, stripe count, duty, axis angle, half/full, centre).
  - Unlike reflection-vector shaders, it gives flats visible stripes, because they have parallax.
  - Rotate it 0° and 45°.
- **Black lacquer** in a sparse tunnel (duty 0.2) shows the highlight a viewer actually sees.
- **Curvature false colour:** write curvature as vertex colours at build time and display them with a QA shader.
- **Traps:**
  - A 10 mm strip reflected in a 3.5 mm blend is less than 1 px wide, so tunnels need wide stripes.
  - Set the camera `clip_start` to 1 mm for macro.
  - Face winding must agree with the custom normals, or Cycles shades the surface as back-facing.

## 2b · Mesh QA on every export
The tessellation is what renders, so check it on every export, not once by eye. Why: a CAD kernel's apex fan on a
domed key (45 triangles meeting at the crown, slivers up to ~10⁶:1, the pole's normal 34° off) rendered a half-ring
highlight on every dome, and nothing caught it before the final film.
1. **Chord by screen need:** chord ≤ ¼ of the mm per pixel at the part's closest framing in the film. Example: a part
   100 mm across filling a 1920 px frame is ~0.05 mm/px, so chord ≤ ~0.013 mm. Glass ≤ 0.05 mm whatever the framing:
   refraction magnifies normal error. Unseen faces may be coarse.
2. **Exact normals:** export the surface normals as custom normals. Shading-normal error against the exact surface ≤
   0.5° at p99. A normal error of e° bends a reflection by 2e°.
3. **Slivers** (aspect > 8): < 5 % on gloss curved faces.
4. **Poles and apex fans** (dome crowns, cone tips, revolved profiles on their axis): compare each pole vertex's normal
   with the fitted surface. Where it leans > ~15° [J], re-mesh the cap as rings on the fitted surface with analytic normals,
   or replace the pole's corner normals with area-weighted face normals.
5. **Flat-shaded planar faces** ignore custom normals: smooth-shade them on import.
6. **Confirm** with a strip-light sweep (the zebra tunnel, §2) of the gloss parts at the hero framing.

Measured: halving the deflection (0.02 → 0.01 mm) took a filleted box from 2.8k to 9.5k triangles, with p99 normal
error 4.0° → 2.1°. Glass at 0.2 mm sawed its refracted rim band, while 0.05 mm matched 0.01 mm, at the same render
time. Triangles cost memory and sync, not sampling: spend them where the screen needs them.

## 3 · Representation by part type
| Part type | Representation | Why / notes |
|---|---|---|
| Machined / prismatic: bodies with fins, bosses, threads, knurls, engraving | **build123d B-rep** | OCC fillets ≤ ~1 mm (G1 is right for machining). Run risky fillets in a forked process and clamp the radius. Tessellate by screen need with exact normals (§2b). Threads as helicoid meshes in a B-rep insert. Engraving: `Text` then booleans. |
| Class-A skins: slabs, pebbles, caps | **constructed fair Gn sweeps** or **SDF** with order-n blends | An order-n smooth min/max (an even polynomial kernel in the signed difference) gives true C^n blends. The textbook \|a−b\| smin is only C2 on its centre line. |
| Three-edge convex corners (class A) | **SDF p-norm box** (rounded box with a p-norm vertex) | Symmetric superellipsoid vertex, G(p−1). Nested pairwise smooth-max makes an asymmetric "Y". |
| Organic / blended / organic-to-hard: yokes, grips, lattices | **SDF** | Organic body with a G2 smooth min, then a hard max with a plane for a spot face: the machined face cut into the organic form. Lattices (gyroid) fused with a smooth min. |
| Arrays and booleans on meshes | **Blender Manifold boolean** | measured ~9× faster than Exact (a 129-hole array into a 1.1 M-face skin in about half a second). Cut along the pull direction. |
| Micro-detail: knurl, texture, perforation lips | **SDF periodic fields**, or **adaptive true displacement** | Both macro-true. Displacement needs a region mask and costs about +50 % render time. Bump only for distant shots. |
| Soft art-directed forms | SubD (Blender) | It pillows every face unless the support loops are tight, so it's wrong for machined looks. |
| Blender bevel meshes | Bevel **plus Weighted Normal**, always | Without WN the flats shade with a gradient band. Profile shape 0.63 ≈ G2, 0.7 ≈ G3. |

## 4 · An SDF engine: what it needs
- **Primitives:** sphere, box, p-norm rounded box, plane, cylinder, torus, ellipsoid, a 2-D superellipse (plan
  distance), a graded hole field for perforation.
- **Operations:** union / intersect / subtract with order-n smooth blends; translate, rotate, shell, offset;
  **normalize(f) = f/|∇f|**, so offsets in mm mean mm for superquadrics and displaced fields.
- **Meshing:**
  - Dense-grid marching cubes for small parts.
  - **Narrow-band (sparse) marching cubes:** sample only blocks within reach of the surface; shared block faces give
    bit-identical vertices that merge exactly, so cost ∝ area/h².
  - Normals from the field gradient, so shading is as smooth as the field, not the facets.
- **Resolution:**
  - 0.1 mm for look-dev.
  - 0.035–0.045 mm for hero macros and where features are 0.3–1 mm (measured: ~3 M verts in about 4 min on CPU for a
    palm-sized hero top).
- **SDF-native wear masks** written as vertex colours at build time: edge = mean-curvature smoothstep; cavity = SDF
  ambient occlusion; sky = upward soft visibility. Zero render cost (`wear-materials.md`). AO needs a true distance:
  wrap approximate fields in normalize (≈ 3× the mask cost).
- **Export:** Z-up mm → glTF Y-up m, with normals included and winding fixed to match them.
- **Mirroring** a part flips handedness: reverse the faces.

## 5 · Hard problems: verdicts
| # | Problem | Winner | Also measured |
|---|---|---|---|
| 1 | Three-edge vertex blend | machined: B-rep rolling ball ≡ Bevel + WN; class A: SDF p-norm (p 3–5) | SDF nested smax (asymmetric Y), SubD (pillowed faces), Bevel without WN (gradient flats) |
| 2 | Graded perforation on a doubly curved cap | hero macro: SDF-native (dark depth, a 0.06 mm lip); speed: Manifold boolean (≈ 170× faster) | B-rep is fast on analytic skins only; a shader mask is fine below ~4–6 px per hole (cavity material: Specular 0) |
| 3 | Diamond knurl on a crowned ring | SDF periodic offset or adaptive displacement | bump: no silhouette, and a seam |
| 4 | Fins through a large blend with small root radii | B-rep: cut the fins, then fillet the root edges and break the tips (≈ 1 s for ~100 edges) | — |
| 5 | Organic form to a machined spot face | SDF: smooth-min organic, then a hard max plane with a ~0.08 mm break | — |
| 6 | Flush button with a constant along-surface gap | SDF: cut the gap where \|r − R\| < g/2 and f > −depth, so the button top *is* the host surface | — |
| 7 | Non-planar parting line | SDF: a slot where \|z − z_k(θ)\| < w/2, depth measured by f; top and bottom parts = body ∩ {z ≷ z_k} | — |
| 8 | Hundreds of oriented light-guide pixels on a curved face | Analytic pipe meshes built in each pixel's own frame (≈ 500 verts, exact normals, per-vertex data such as level / kelvin / polish / height): hundreds in well under a second, cheaper than GN instancing, and they carry data. Wells cut in the SDF through a thin skin, analytic sleeves down to the board beneath | full-depth marching-cubes wells explode the vertex count (≈ 10 M); Manifold refuses a non-watertight shell; an adaptive shell (0.04–0.8 mm) keeps a whole product under ~10 M verts |
| 9 | Gyroid lattice fused into a solid ring | One SDF: smin(lattice, ring), then a flush smax cut; mesh at ≈ wall / 2.3 | seconds for a few M verts |
| 10 | Knurl on a torus-like rim | SDF periodic offset in (arc length at R, true arc length round the section via a lookup), feathered by smoothstep in both directions | — |

## 6 · Realism numbers (manufacturing rules of thumb)
- Edge breaks 0.1–0.5 mm, and every visible edge ≥ 3 px at the hero framing.
- Draft 1–2°, and 3° or more when textured.
- Parting-line mismatch 0.02–0.05 mm.
- Anodise thins and lightens on sharp edges.
- Diamond-cut chamfers show bright bare aluminium.
- Bead blast renders at roughness ≈ 0.35–0.42.
