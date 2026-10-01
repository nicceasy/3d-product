# Research first, every step

This is standing policy in this skill. **No pipeline step starts from memory.** Before
concept, modelling, materials, lighting, camera, story or animation work, research that step:
- the domain's best practices;
- references at the highest level;
- known hard problems and failure modes;
- measured numbers;
- what our tools can actually do on this machine.

Then write down a decision. Why: research repeatedly changed a design before a single render (an optical product
redesigned, a spec that failed physics checks), exposed tool limits before they cost a day (a CAD kernel's broken
continuity filling, CAD meshes defeating curvature-based masks), and independently confirmed what tests later showed.

## Research is always paired with reference images (a standing rule)
Every research track returns **reference images with its findings**, never text alone: for each claim or direction,
the images that show it (URL of the page and of the image, what it shows, why it is relevant, what to measure in it).
- Agents look at the images themselves (the in-app browser's screenshots; the Read tool for local files), not only at
  captions or alt text, and say what they saw.
- Deliver a **reference sheet per track**: a table of image URLs grouped by topic, each with a one-line "what it shows"
  and "use it for". The lead reviews the key images before deciding.
- Saving copies needs the user's permission per file (filename, source, size). Without it, keep URLs and
  in-session views only. Third-party images are private reference: never on a board or artifact.
  - A board may show our own renders and charts made from the images' measurements.
  - It may also show the images as links.
- Measured references beat mood references: when an image sets a target (a colour, a light ratio, a texture), measure
  it and write the number next to the link.

## When
| Step | What to research before touching it |
|---|---|
| Concept / ID | current design language, 2–3 style directions, product precedents and sizes, physics of the core function, manufacturing process |
| Modelling | the representation for each part type, continuity targets, the hard problems this form contains and how practitioners solve them, the tool's real capabilities (run feasibility tests) |
| Materials / CMF | real finishes and their numbers (Ra, anodise thickness, IOR, coatings), wear physics, reference photographs (as links); measure the user's photos per part (colour lit/shadow, highlight width, texture rms and feature size at a known mm/px, edge highlight) and calibrate on swatches (`reference-detailing.md` §6) |
| Detailing a real product | photos of each part (forums, museum galleries, auction listings, manuals' exploded views), how each part works and is named, variant differences; camera-match the photos (`reference-detailing.md`) |
| Lighting | reference films and photographs of the product class, luminance ratios, practicals, haze, the rig's physics (flux, spread) |
| Camera | lens and sensor behaviour for the look (working distance, pupil, iris, glare, noise), shot vocabulary with lens and aperture numbers |
| Story / animation | pacing of the best films in the category (measured lengths, shot counts), easing and camera-move numbers, music grid |
| Post / delivery | view transforms for emitters, encoding (BT.709 tags, bit depth), energy-correct glare |
| Sound / music | the craft (spotting, worldizing, beds, perspective, loudness for the channel), sources and their licences, reference films measured (loudness curves, spectra, events against cuts and motion), music references turned into a generation brief; no audio download without the user's own OK (`sound-design.md`) |
| Graphics / labels | about five verified real examples per design, read from photos of the object; the category's layout grammar; typefaces as unverified lookalikes (`graphics-labels.md`) |
| Camera operation | how real supports move (drift spectra, resonances, operator lag), perception thresholds in px (`camera-motion.md` §6) |
| Realism / grade | measured targets from real footage the user trusts (`/analyze-youtube` + a frame-statistics tool): tone zones, black floor, chroma, cast, grain; what the finishing app can do by script (Resolve) |

## How: parallel research agents
1. Split the study into 3–4 **tracks** that don't overlap, and launch them as background agents in one message.
   Typical splits:
   - a realism study: grade numbers · lighting realism · the finishing app's scripting API · the linear workflow;
   - a new-form study: hard surface · wear shading · camera and emissives · concepts;
   - a real product from a patent: identity and specs (which product, manuals, dimensions) · details and materials
     (finishes, photo colour samples, typography, wear) · story, light and photographic references (catalogue
     conventions, sets, measured daylight targets). Measure the drawing *while* they run.
   A detail pass on a real product uses **D-tracks**, one per family of parts, each ending in "what the model gets wrong, with numbers":
   D1 mechanism and moving parts (service manual, exploded views, pose table), D2 controls, housing and markings
   (positions, radii, typography, rear/underside), D3 surfaces and materials (per part: material, finish process,
   photo-measured colour/roughness/texture/edge highlight, a table keyed by the renderer's material names). See
   `reference-detailing.md` §3.
2. Give each agent the **context**: stack, machine, constraints, and what the user asked for, in their words.
3. Ask for **deliverables, not surveys**:
   - decisions and numbers;
   - a catalogue of hard problems with a solution per representation;
   - a recommended architecture or pipeline;
   - references as URLs, each with a one-line "what it shows";
   - a TL;DR of 15 lines or fewer.
4. Ask for **feasibility checks on this machine**: small headless tests of under a minute, with API names verified on the installed Blender and OCCT versions. That's how the Blender 5.2 API traps and the OCCT enum bug were found.
5. Every claim gets an **evidence tag**:
   - [S] fetched source
   - [S2] search snippet
   - [V] verified locally
   - [D] derived
   - [J] judgement
6. **Rules to state in every research prompt:**
   - no downloads (cite URLs; images are private reference only and never republished);
   - no installs;
   - write to the project's `research/Rk_<topic>.md`;
   - copy any test scripts next to the report (scratch space is temporary);
   - read the user's images with the Read tool or PIL, **never a browser on file://** (an agent hung there for
     two hours); no GPU renders while the lead is rendering;
   - if an agent's transcript shows no activity for 20 minutes, stop it and relaunch with a narrower brief.
   - Agents have still curl-fetched source files, and WebFetch auto-saves PDFs. So also say "don't WebFetch .pdf URLs (the fetch tool saves them); cite them". Repeat the
     rule in every prompt and tell the user if it is broken anyway.
7. While the agents run, build **instruments** that don't depend on their answers (e.g. a zebra tunnel, curvature combs, SDF kernels).
8. When they land, read the TL;DRs and the sections you need, and write a **"Phase n · Research lands → decisions"** entry in
   THINKING.md that says which recommendations were adopted, which were contradicted by our own tests, and why.
9. **Test what research says against renders.** Research sets hypotheses; renders decide, and captions record what the
   image shows. (Measured once: research predicted a ray-mask cost of 3.2×, and the render measured 3.2×.)

## Research prompt template
```
You are the research agent for track <Rk>, "<topic>", in a product-visualisation study. Write to <path>.
Context: <stack, machine, versions; what the user asked for, verbatim>.
Deliverables (concrete, quantitative, decisions): 1 <theory/physics with numbers> 2 <approaches per representation
with pros/cons/failure modes> 3 <hard-problem catalogue> 4 <references: URL + one-line what it shows> 5 <recommended
architecture/pipeline> 6 <feasibility tests in scratch/<rk>/ with exact API names>.
Rules: no downloads (URLs only), no installs; tag claims [S]/[S2]/[V]/[D]/[J]; 4–7k words; end with a 15-line TL;DR.
Fast loop: write the TL;DR + recommended decisions FIRST, as a checkpoint within 30–45 min; then the detail. Any test
plan you propose carries its machine-time estimate and fits <budget> (cut it until it does).
Return a <300-word summary of the key decisions.
```
Research is time-boxed like everything else (`fast-feedback.md`): the lead reads the first checkpoint and redirects
the track, rather than waiting for the full document.

## References on the board
- Put references in FigJam as **links with a one-line note**, never as downloaded images. A research section per study
  carries the track summaries and a references box.
- Where a measured chart can stand in for a reference (teaser lengths, curvature plots), make it from the data.

## Delegating builds
Once research has fixed the architecture, whole products can go to builder agents. Give them:
- the spec section and the research sections to read;
- the libraries they may import but must not edit;
- a folder they own;
- the QA and look-dev deliverables;
- best-camera spec dicts for reuse in the storyboard.

Review their sheets before using the models.

