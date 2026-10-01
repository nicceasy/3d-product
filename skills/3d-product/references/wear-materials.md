# Wear, smudges, dust: the layer stack and its masks

The default is the finish as designed (§ "Intent vs age"). This file is how to build wear when the brief asks for it,
and how to make each phenomenon read on camera.

## Architecture
- **One Principled BSDF and one Bump node,** fed by a 7-channel bus (Color, Metallic, Roughness, Height, Coat,
  CoatRough, Sheen).
- **Each layer is a masked fill of the bus** (a node group per layer). Layer order:
  1. micro-scratches
  2. edge wear to substrate
  3. touch polish
  4. cavity grime
  5. fingerprints and smudges
  6. water spots
  7. dust (last, so it sits on top)
- **Levels:**
  - `hero-clean`: zero wear.
  - `lightly-used`: a few scratches, chips only on the sharpest edges, a little grime, 1–2 prints, light dust.
  - `field-worn`: 30–60 % of convex edges bare, grime, 4–6 prints and smears, dust, water spots on glossy tops.
- **The material spec** carries: the base finish (colour, metallic, roughness, bare-substrate colour and roughness,
  gloss, coat), the level, the mask source and its distances, fingerprint projectors placed in world mm (location,
  rotation), a touch-polish zone (location, radius), and any emissive glyph (dots behind invisible micro-holes: count,
  pitch, centre, strength, colour, dot radius).

## Three mask sources: pick by representation
| Source | How | Cost | Where it's right |
|---|---|---|---|
| **SDF-native** (vertex attribute) | at build time: edge = mean-curvature smoothstep (convex r 0.25–2 mm), cavity = SDF ambient occlusion (5 steps to 3 mm, −0.08 bias), sky = upward soft visibility; stored as vertex-colour RGB | **zero at render** (measured ≈ 3× faster than live masks on a field-worn macro) | SDF parts. Wear lands only where curvature is truly high: crisp chips at gaps and lips |
| **Live ray masks** | Bevel-node edge (r 1–2 mm, 8–16 samples); inside-AO for modelled fillets (d ≈ 2R); AO cavity 3–5 mm; AO with a +Z normal for sky | about +20 % per mask, 3.2× for all four | B-rep meshes (large flat triangles defeat Pointiness and GN curvature), look-dev. The edge band is broader: it lights whole rims |
| **Baked** | Smart UV plus an EMIT bake of the live masks at 2k (seconds per part) | baseline at render | B-rep finals, and any animation |

Traps:
- AO masks need a *true* distance field. Approximations (superquadrics, plan outlines scaled by min(a, b)) under-read
  distance a few mm out and flood the cavity mask. Normalise the field (f/|∇f|).
- Hidden internal faces (the plane where two parts split) read as full cavity. They're harmless, but they skew
  averages.
- Node-group caches must be revalidated when the scene resets between specs.
- The glTF importer's own material shows the raw mask colours if your material key doesn't match the part name (check
  the importer's case handling).

## What each phenomenon needs to read on camera
- **Edge wear on anodise:** tiny bright chips on the sharpest convex edges, where the oxide is thinnest. Never in
  cavities.
- **Fingerprints:** ridges 0.45 mm apart; the deposit pulls roughness toward about 0.3, so gloss gets hazier and matte
  gets darker and glossier. They only show against a **reflected softbox**: without a reflection on the glossy face, a
  print is invisible.
- **Dust:**
  - At product scale, shading specks do the job.
  - At macro, real GN particles at 0.05–1 per mm² plus 2 % fibres (measured: 1 M instances in ~10 s).
  - Raking light makes specks read; they glow as tiny bright points in dark frames.
- **Swirl scratches:** only analytic groove normals with random orientations make the circular arcs round a light.
  Bump, roughness-only and anisotropic versions do not.
- **Restraint:** advertising is hero-clean plus one macro cue (dust in the focal plane, or a faint print off the hero
  line). Use lived-in levels only when the story says so.

## Emissive parts are materials too
See `camera-post.md`: an edge-lit light guide (LED hotspots, a fall-off floor, etched dots, a clear glass lobe), glass
plus emission, plain emission, and a glyph overlay.

## Intent vs age, and a measured dust layer
- **Default: the finish as designed** (a standing rule). Reference photos of real products are usually old units:
  dust, a grey bloom on rubber, lint in coves, burnished handling zones, fingerprint smudges, wipe arcs on acrylic,
  pitted and dulled metal. Those are age, not the material. Render the designer's finish (texture, sheen, edges,
  print) unless the brief asks for patina; keep age as a switch, off by default, and show the user both when it is in
  question. The same holds for geometry (`manufacturing-variation.md`).
- **When age is wanted, measure it** on the photos: specks per cm² and their size (measured: a used unit ≈ 20 /cm²,
  Ø ≈ 0.16 mm median; a well-kept unit ≈ 4 /cm²), film strength, where lint collects.
- **Recipe:**
  - up-facing mask: smoothstep(N·Z 0.6 → 0.9);
  - specks: a 2-D Voronoi on object XY, one feature per cell (cell = √(100/density) mm), radius 0.05–0.15 mm per
    cell, colour ≈ 0.2 grey, roughness → 0.75;
  - a film: ≈ 3 %, 0.3 grey, +0.04 roughness;
  - lint: the same specks at 3× density under an AO cove mask (3 mm);
  - burnish: soft ellipses of −0.08 roughness;
  - smudges: noise blobs of +0.13 roughness at 20 % cover;
  - pits: dark specks (albedo × 0.4) on bead-blasted metal.
