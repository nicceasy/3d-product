# Render elements → the nature of the product

Every element of a product render makes a claim about the product. A big soft light says *calm, continuous,
premium*; a small hard light says *precise, optical, alive*; a long lens says *dignified object*; a caustic says
*this glass does something*. This reference runs **from the smallest element of a render up to the concept**, and for
each element gives what it expresses, the recipe that works (with numbers), and how it fails. Detail: `glass-light.md`
(glass, light, colour), `approaches.md` (metal / CMF verdicts).

How to use it: write the product's nature in one sentence, pick the **lead element** that proves it (§11),
then choose every other element so it does not contradict the lead.

Contents: 1 Light sources · 2 Light shaping · 3 Light colour · 4 Material · 5 Light transport (kernel) ·
6 Camera · 7 Colour & tone · 8 Composition · 9 Passes & comp · 10 Geometry · 10b Surface, wear, lens character ·
11 Concept (lead elements) · 12 Story (elements over time) · 12b Motion & time · 13 Checklist

---

## 1 · Light sources: size, distance, number
| Element | Expresses | Recipe that works | Fails when |
|---|---|---|---|
| Large soft source (1–5 R, overhead) | calm, continuous surfaces, premium metal | a soft top + gradient strips + flags; energy ∝ R² | used on glass: glass has nothing to refract, the product vanishes |
| Strip lights / rims behind | silhouette, edge, form language; the "reveal" | two strips (e.g. 30 × 500 mm) behind at 5600–8000 K; everything else black | rims leak onto the floor and flatten the black |
| Small hard source (≤ 10 mm) | precision, sparkle, optics working; caustics | a 3–12 mm spot at the angle that focuses through the glass onto the table | path tracing can't find it through glass → black shadows (use a light-tracing engine or a bigger light) |
| Many small sources (bokeh) | environment, place, night, mood | 30–70 emissive spheres at 7–20 R, f/1.8–2.8 | too bright/many → the product loses the frame |
| A light inside the product | the product *is* a light | emissive part + a light *inside* the glass (seeded glass): a documented cheat | a real LED behind glass: only light tracing reaches it |
| Set-only twin of a product light | the product *stands on* something: contact, weight, bounce | the product key stays linked; a twin at 25–30 % lights only the set | flooding the tabletop under a macro lens (use ~4 %); rebalancing by the brightest glossy pixels |
| A room at 0.5–2 % of the key | a place; metal that reads as metal | an HDRI or walls, strength calibrated from the world/key light-group ratio | world 0: glossy metal becomes a black graphic; > 2 % lifts a low-key mood |

## 2 · Light shaping: fields, flags, gobos, volume
| Element | Expresses | Recipe | Fails when |
|---|---|---|---|
| Dark field (black patch over a big panel) | glass as bright outlines: precious, jewel-like | patch sized from the camera frustum ×1.08 | patch too small → the panel shows round the frame |
| Bright field | glass as dark edges: clinical, scientific, honest | panel directly behind | on tinted glass: colours wash out (blown) |
| Gradient ground | the glass draws itself: self-contained, sculptural | one card, bright at the floor fading up | the card's edge shows in frame |
| Flags / black cards | control of what a mirror-like surface shows | flags on the mirror ray of the camera | forgotten after moving the camera |
| Textured gobo (spot) | context, time, place (window = home, blinds = afternoon) | a spot projecting a window, slats, dots or an image | sharp everywhere → reads as projection, not window |
| Physical cookie | real windows: sharp near, soft far | small source, cookie near the product | large source → the penumbra erases the pattern |
| Product's own gobo/beam | the product's *function* is light | beam spot + haze (~1/m, anisotropy 0.25 for side-on cameras) | haze lit by fills (keep fills out of the volume) |

## 3 · Light colour: gels, temperature, additive colour
| Element | Expresses | Recipe | Fails when |
|---|---|---|---|
| Gels on a neutral product | brand colour without colouring the product | OKLCH L 0.80 C 0.13, lowest channel ≥ 0.05; one hue family + a white key | AgX desaturates them (PBR Neutral for look-dev; check finals through the film curve, whose per-channel shoulder skews saturated highlights toward yellow/white) |
| Split tone (complementary rims) | drama, dimensionality, "tech" | e.g. teal h200 / magenta h330 rims on black anodising, white key | overlit floor → black metal reads silver |
| Temperature contrast | time of day; warm product in a cool world | 2200 K source vs 12000 K window | two temperatures fighting in one surface |
| Additive RGB keys | colour from light alone; playfulness; physics | three keys 120° apart, wide cones: CMY shadows | narrow cones → three separate pools |
| Light × material colour | colours multiplying: material honesty | a gel matching the material, or its complement to make it vibrate | analogous gels on analogous material → mud |

## 4 · Material: how the product is made
| Element | Expresses | Recipe | Fails when |
|---|---|---|---|
| Metal micro-detail (blast bump, polished chamfer, AO cavity) | machining, craft, scale | never remove it: it is the largest single quality lever on metal | on black anodising under hot light (reads silver) |
| Glass IOR | how much of the world the object holds; jewel vs vessel | 1.49 acrylic · 1.52 crown/K9 · 1.78 SF11 · 2.15 CZ | as a "look" knob: it moves focus and composition |
| Thin-film coatings | optical seriousness; the purple/green of real lenses | 100–240 nm per element, film n 1.38 | invisible unless a broad dim source fills the element |
| Volume tint (Beer–Lambert) | solid, honest coloured material; depth at edges | invert Beer–Lambert at the *viewing* path length (`glass-light.md` §2.4) | Base Color tint (cellophane); planning face-on (hue drifts) |
| Frost 0.12 | soft light, "premium translucent", richer colour | Principled roughness 0.12 | 0.3 turns it into a lamp shade |
| Dichroic film | precision + colour play; two colours per part | film 300–480 nm at n 2.2 | a small light (black shadows) |
| Seeded glass | light made visible inside clear glass | Volume Scatter 2–4/m inside the glass | alone (needs a light inside the glass) |

## 5 · Light transport: which kernel can tell the truth
| Element | Expresses | Recipe | Fails when |
|---|---|---|---|
| Caustics | the glass *acts* on the world | LuxCore BIDIR / PATHOCL + hybrid, composited under Cycles | Cycles PT (finds a small share), MNEE (right shape, under half the energy) |
| Spectra | optical truth; wonder | LuxCore `glass` with Cauchy A/B (A ≠ nd) | Cycles (no dispersion); an RGB split = 3 copies |
| Projection through optics | the product works | LuxCore light tracing from the emitter through the modelled lens | Cycles (empty wall) |
| Light inside glass seen through glass | the glow of a light product | cheat: a light inside the glass | every kernel (specular–diffuse–specular) |

## 6 · Camera: distance, attention, character
| Element | Expresses | Recipe | Fails when |
|---|---|---|---|
| Long lens (100–400 mm) near the midline | dignity, object-ness, the packshot | a hero at the lens's real working distance | too long → flat, no form |
| Low camera | monumentality | el 3–6° for reveals | the horizon line cuts the product |
| Shallow DOF | attention, intimacy, miniature | f/1.8–4, focus on the feature | on a packshot (the hero must be sharp) |
| Bladed iris | a real camera's character | 9 blades (bokeh nonagons) | barrel cat's-eye without purpose |
| Bokeh through the product's glass | the product as a lens | coloured lights behind a glass sphere | a background too busy |
| Lens profile (Lensfun or own prescription) | photographic authenticity; "shot with our lens" | applied in scene-linear before the view | on hero packshots (keep clean) |
| Macro | craft detail, coatings, knurl | 150–200 mm, frame one element | without a broad source (nothing to see) |

## 7 · Colour & tone
| Element | Expresses | Recipe | Fails when |
|---|---|---|---|
| View transform | saturation fidelity vs highlight grace | look-dev: PBR Neutral (colour) / AgX (metal); **finals: the film curve** (`finishing.md` §1) | PBR Neutral / AgX on low-key finals: their toes crush blacks (tens of % digital black) and hot emitters go salmon |
| Black floor & chroma restraint | photographed, not rendered | crush ≤ 1 %, chroma p99 ≤ 30–40, shadows ≤ 8 C*, cast b* 0–5 (measured on film frames) | digital-zero blacks; a warm, over-saturated grade |
| One hue family + a neutral anchor | discipline, premium | hue families 1–2, spread ≤ 25°, ≥ 20 % neutral (`glass-light.md` §11) | three families in a packshot (fine only as a deliberate physics demo) |
| Where colour lives | brand strategy | in exactly one place: the light, the material, the temperature, or the object | colour in all of them at once |
| Withheld colour | narrative payoff | monochrome until the payoff frame | colour everywhere from frame 1 |

## 8 · Composition
| Element | Expresses | Recipe | Fails when |
|---|---|---|---|
| Fill 20–45 % | object in space, calm | measure the product's share of the frame | < 15 % (lost) or > 60 % (cramped) |
| Family / multiples | a range, colourways, choice | staggered diagonal, one light for all | duplicate imports sharing mesh data (make each copy's data unique) |
| Cutaway / exploded | engineering, what's inside | a half-section; explode along the product axis | cut faces unlit (light the section) |
| Ground & horizon | place, weight | dark glossy floor for glass; a cyc for families | visible floor edges (use a cyc or wall) |

## 9 · Passes & comp: directing light after the render
| Element | Expresses | Recipe |
|---|---|---|
| Light groups | colour as a post decision | white lights in groups → numpy recolour (exact) |
| Caustic layer | physics you can grade | LuxCore − Cycles, masked by Object Index, blurred |
| Bloom above 1.0 only | a lens's veiling glare | 3/12/40 px, k 0.25–0.35 |
| Volume pass | beam density as a slider | Combined + (k − 1)·Volume |
| Denoised light groups → Resolve | lighting decided after the render, photographically | denoised group EXRs → lens optics per group → Fusion Loaders, gains, additive merges → look LUT (`realism-finishing.md` §4) |

## 10 · Geometry: what is physically possible to show
- B-rep with named parts (materials, explodes, STEP). Prescription-driven optics; physics-driven dimensions.
- Glass: closed, outward normals (lint), fused cemented pairs, ≥ 0.6 mm clearances, ≤ 0.05 mm chord.
- Metal: 0.2 mm chord is enough; G2 corners are the open problem (OCCT fillets are G1).

## 10b · Surface, wear and lens character (detail: `hard-surface.md`, `wear-materials.md`, `camera-post.md`)
| Element | Expresses | Recipe that works | Fails when |
|---|---|---|---|
| Continuity (G1 vs G2+) | machined vs moulded / "class A" | G1 rolling-ball on CNC metal (reads true); G2+ built by construction (fair Gn sweeps, SDF order-n blends, p-norm corners) on consumer skins | a G1 join on a gloss class-A skin → Mach bands; SubD on a machined part → pillowed flats |
| Fairness (one curvature peak) | calm, expensive, inevitable | inner-control spread c ≈ 0.25; footprint 1.3–1.5 × R | c ≥ 0.5 → two peaks → a "G3" corner reads like a chamfer |
| The one crisp edge | precision, the brand's cut | a single G0 kerf/chamfer (0.08–0.1 mm break) against continuous fields | many sharp edges → noise; no sharp edge → melted |
| Wear placement (only on request: render intent, not age) | honesty, age, touch | edge wear only where curvature is truly high (SDF-native masks), grime in cavities, dust on sky-open tops, polish where the thumb lives | broad ray-mask bands; wear in cavities; dust on undersides |
| A macro cue (dust, one print) | "this is a photograph" | one speck in the focal plane, one print on gloss seen against a softbox, in an otherwise hero-clean frame | uniform dirt; prints on faces no light reflects in |
| Emitter structure | real electronics, not a CG glow | LED hotspots + fall-off + etched dots (light guide), glyphs through invisible micro-holes, glass pixels with domes | flat emission; emitters brighter than their spill and haze can carry |
| Lens character (post) | a real camera was there | post optics matched to the render camera's iris: energy-correct diffraction, veiling glare, CA, vignette, sensor noise; anamorphic ovals for night/futurism | compositor streaks (+120–170 % energy); a bokeh shape that doesn't match the spikes |
| Plane of focus at macro | attention, scale, craft | camera at the working distance, f-number from the pupil, the focal plane laid across one feature | "everything sharp" macros (read as CG) |

## 11 · Concept: the lead element follows from the product's nature
| Nature of the product | Lead element (prove it) | Supporting elements | Avoid |
|---|---|---|---|
| Precision optical instrument (a lens, a scope) | coatings + refraction in a dark pool; a cutaway ray diagram | dark field, gels on black metal, long lens, macro | soft top light (kills the pool) |
| Light as the product (a lamp, a projector) | the light itself: beam in haze, spectrum, glow column | withheld colour, temperature contrast, bloom where earned | lighting the product brighter than its light |
| Translucent consumer object (tinted plastic showing internals) | colour through thickness (Beer–Lambert), internals | transillumination, gobo × colour, a colourway family | Base Color tint; a white ground washing the colour out |
| Machined metal object | reflections of big soft cards on micro-detailed metal | long lens, near-white or pure black ground | hard small lights; noisy environments |
| Dark monolith with one cut of light | the cut: a single emissive line or field in an otherwise dark, continuous object | low key 8–16:1, the product's own light as the key in the opening frames, rims only on the continuous surfaces, warm practicals as bokeh | lighting the dark body brighter than its own light |
| Tool that transforms (one mode into another) | the transformation itself, e.g. one light handing over to another (beam → glow) | a flux-true beam in haze, the mechanism's own easing, warm vs cool for the two modes, the studio falling away at the end | cutting away from the change; lighting the product brighter than its own light at the end |
| Solid crystal / lens object | the caustic in its own shadow | a small hard key at the focusing angle, the hybrid comp | a raised stand that moves the focus off the table (check it) |
| Black glossy object in a room | its reflections: the room it mirrors (`lighting.md` §5) | a front fill as a lit room surface, a rim from the window, negative fill | fills that aren't real surfaces; fixing voids with exposure |

**Physics first:** before look-dev, trace the optics, check the product works (thin lens / ball lens), predict the
caustic, plan colour in OKLCH / Beer–Lambert (`glass-light.md` §2). It can change the product before a single render.

## 12 · Story: arranging elements over time
Grammar: **black open** (one edge of light) → **edge reveal** (rims, shape before surface) → **mechanism** (what makes
it work, backlit) → **physical proof** (the product acting on the world) → **payoff** (the one saturated / most
spectacular frame) → **hero with a neutral anchor** (at rest, in context) → **end card**. Each frame answers one
question; the lead element is withheld until the payoff.

## 12b · Motion & time: elements that only exist in a film (detail: `animation.md`)
In a cut film, `camera-motion.md` §0 (simple, constant-speed moves; cuts mid-move) overrides the camera easing below;
easing still governs mechanisms and teaser moves that start and stop on screen.
| Element | Expresses | Recipe that works | Fails when |
|---|---|---|---|
| Easing family | mass and who's moving it | camera: a gentle ease (peak ≈ 1.33× mean speed); mechanism: its own ease; a detent = bezier + spring (ζ 0.6); linear only when the start and stop are off-screen | cubic/quint on a camera → judder; springs on whole moves → toy |
| Boundary velocity | whether the film breathes or flows | a settle has zero velocity and a cut keeps moving; the next shot enters at the speed the last one left | a shot that starts from rest after an accelerating cut: the film stalls |
| Camera move type | attention and hierarchy | orbit = the object is sculpture; push = look closer; pull-back + rise = "here is all of it"; axial push = into the product's light | the camera moving while the mechanism moves: two ideas at once |
| Macro camera | craft and scale | real working distance, focal = 36·dist/field, f-number = focal/pupil → a ±0.5 mm plane of focus sliding over the detail | a short-distance pinhole: wide-angle perspective, absurd blur, reads CG |
| Light over time | life, energy, what the product *does* | a glint travelling round a chamfer; light-wipe cuts; a flux-true zoom beam; beam → glow; the studio falls away | light that changes without a cause in the story |
| Cut rhythm | confidence | cuts on a musical grid, long–short–flurry–long; ≥ 30° or a clear size change on a cut (`editing.md`) | even cutting ("slideshow"); jump cuts on the same angle |
| Sound | weight and touch | every cue on a film frame (0 to +1 frame, never early): a click on a detent's snap, a tone on a light's pulse, a tonal bed tuned to the music; the method in `sound-design.md` | broadband ambience as "quiet"; music that ignores the picture |

## 13 · Checklist per shot
1. What is the product's nature in one sentence? Which element proves it (§11)?
2. Does the physics guarantee it (trace / thin lens / Beer–Lambert / caustic prediction)?
3. Which kernel can carry that light (§5)? If none, what is the labelled cheat?
4. Are light, material and colour telling the same story (one hue family, colour in one place)?
5. Is the camera saying the right thing about scale and attention?
6. Does the light behave (the gatekeepers in `realism-finishing.md` §2: no unexplained product-only linking, a room,
   practicals that reflect and spill, a black floor)? Measure it (crush, floor, mids, chroma, cast) before trusting
   the eye.
7. Render once, direct in comp (groups, layers, bloom, volume); finish (`finishing.md`); score; look again.
8. In a film: which end of the shot is the board frame (arrives → END, departs → START)? What is the one change A → B?
   What velocity does it enter and leave with? Is the angle ≥ 30° from the neighbouring shot?
