# /3d-product

**I built everything I know about hardware product motion into a free Claude Code skill, so you can tell beautiful product stories from the command line.**

![A 1976 Braun PS 550 turntable at night, lid up, a lamp on beside it. A frame from the film made with this skill.](assets/hero.jpg)

`/3d-product` is a one-shot pipeline for product films. You give Claude Code a prompt and a reference (a design patent, a few photos, a video), and it builds the film the way a product-film crew would: research first, a model measured from the drawings, materials as designed, a set that looks lived in, grey-box compositions, first, key and last frames for every shot, an animatic, an overnight render, sound, and a graded finish. Claude drives Blender, Octane or Cycles, and DaVinci Resolve by script. You direct in plain English and make the calls at each gate.

## The proof

The film above was the test: 98 seconds of a 1976 Braun PS 550 turntable across one evening, modelled from its US design patent (D251,557) and reference photos, rendered in Octane on four GPUs and finished by script. I made it without using Blender, Octane or DaVinci Resolve myself. The skill came out of the nine days it took.

![The 27 shots of the finished film, from afternoon sun to night.](assets/film-27-shots.jpg)

![The patent's perspective drawing beside the model drawn the same way.](assets/patent-to-model.jpg)

## What it gives you

1. **No 3D software or compositor to operate.** You direct in plain English; the skill runs Blender, Octane and Resolve by script.
2. **A start from a patent or a few photos.** The model is measured from the drawings: the demo sits within a median 0.4 mm of the patent.
3. **Shots locked before you pay for them.** Grey-box compositions, first, key and last frames and playblasts come first. The full render happens once.
4. **Renders you can sleep through.** A small shell script watches the GPUs overnight, restarts anything that hangs and finishes the frames, without spending AI credits on babysitting.
5. **Notes that become rules.** Every note you give can become a standing rule, so the next film starts where the last one ended.
6. **Sets that look lived in.** Rooms are dressed with what would really be there, and checked so no two objects pass through each other.
7. **Film grammar built in.** Simple camera moves, cuts on the product's own motion, light that tells the time of day, a touch of operator drift.
8. **Sound included.** Soundscapes and original music fitted to the cut, mixed and loudness-checked.
9. **It runs on what you have.** A setup probe picks the engine: Cycles on a laptop for previews, Octane on a GPU machine for finals.
10. **Review from anywhere.** Every pass lands as stills and contact sheets on a FigJam board, and as review videos in a synced folder you can open on a phone.
11. **Every stage measured.** Each stage ends with numbers against pass values (a compositional analysis on every frame, motion checks on every camera move, loudness steps and entries on the mix), and the scene is weighed against a budget from the first build, so nothing has to be cut down at the end.

![A grid of clay renders: the grey-box composition lock-in.](assets/greybox-lock-in.jpg)

## Install

In Claude Code, add this repo as a plugin marketplace and install the plugin:

```
/plugin marketplace add nicceasy/3d-product
/plugin install 3d-product@3d-product
```

Or with npm (Node 18 or later), which copies the skill into `~/.claude/skills/3d-product`:

```
npx 3d-product
```

Add `--project` to install it into the current project's `.claude/skills/` instead, `--force` to update an existing copy (the old one is kept in `skill-backups/`), or run `npx 3d-product uninstall` to remove it.

Or with the skills CLI:

```
npx skills add nicceasy/3d-product
```

Or copy the skill folder by hand:

```
git clone https://github.com/nicceasy/3d-product.git
cp -R 3d-product/skills/3d-product ~/.claude/skills/
```

Claude picks the skill up on its own when you ask for a product film, a packshot or a render from a patent. You can also call it by name.

## Use

Some ways to start:

- "Use /3d-product to make a 60-second launch film of this speaker from these photos."
- "Model US design patent D251,557 accurately and render a hero packshot."
- "Storyboard a teaser for this lamp: research first, then give me grey-box options."
- "Take this CAD model and put it in a lived-in room at golden hour."

The pipeline stops and waits for you at five points: the film's intention, the compositions and shot list, the cut, the music, and the go for each act of the render. Everything else is gated by checks it runs itself.

## Requirements

- [Claude Code](https://claude.com/claude-code)
- Blender 5.x (built and tested on 5.2)
- Python 3.11 or later with numpy, scipy, Pillow, scikit-image and OpenEXR; build123d for B-rep modelling
- ffmpeg
- DaVinci Resolve Studio for the scripted finish (tested on 21.1)

Optional:
- An NVIDIA GPU machine with Octane (OctaneRender for Blender and OctaneServer, tested on 31.10) for finals. Without it the pipeline renders in Cycles.
- FigJam, through the Figma MCP server, for review boards.
- An AI music generator for soundscapes and temp music. The demo generated them with Stable Audio 3 Medium and Sonilo through Comfy Cloud, and its final songs were composed in Suno; check each service's licence and plan before commercial use.

Run `scripts/probe_setup.py` first (stage 0.5). It checks your machines read-only and recommends a render path.

## What's inside

```
skills/3d-product/
  SKILL.md        the pipeline: sixteen gated stages, the rules over every stage, orchestration
  references/     one file per stage or topic: lighting, camera motion, editing, sound, finishing, traps
  scripts/        setup probe, scene weight check and budget example, "reads" lighting metric,
                  compositional analysis, motion QA, loudness checker, macro focus calculator,
                  overnight render supervisor template, FigJam section builder
```

## Notes

- Every frame is path-traced from a 3D scene, and no image model touches the rendered frames. The soundscapes and the original music takes are AI-generated; the final songs were composed in Suno with those takes as reference.
- The PS 550 is a demonstration subject. Braun is a trademark of its owner, and this project isn't affiliated with Braun. US design patent drawings are public domain.
- The skill keeps its rules as general principles. Keep your own project notes, tools and measurements outside the skill folder.

## Sources and credits

Built by [Nick Conn](https://www.nickconn.com), directing [Claude Code](https://claude.com/claude-code).

### Sources

The skill's rules came from reading first and measuring second. These are the sources its references draw on. Each rule in the skill was checked on real renders before it went in, so where a source and the skill disagree, the skill says why.

#### Manuals and guides

- [Blender Manual](https://docs.blender.org/manual/en/latest/) and the [Cycles source code](https://projects.blender.org/blender/blender) (Blender Foundation). Material values were read from the source, not from tutorials.
- [OctaneRender for Blender documentation](https://docs.otoy.com/blender/) (OTOY).
- Scott Benson's Octane optimisation guides for OTOY: [Render Settings and Optimization](https://help.otoy.com/hc/en-us/articles/24245587834907-Render-Settings-Optimization), Scene Optimization, and Lights and Emission. The tuning order in the Octane path is his.
- [DaVinci Resolve Reference Manual](https://www.blackmagicdesign.com/support/family/davinci-resolve-and-fusion) (Blackmagic Design).
- Daria Fissoun, [*Colorist Guide to DaVinci Resolve 20*](https://www.blackmagicdesign.com/products/davinciresolve/training) (Blackmagic Design, 2025). The rule to build looks by hand on the panels comes from here.
- [build123d documentation](https://build123d.readthedocs.io/).

#### Standards

- [ITU-R BS.1770](https://www.itu.int/rec/R-REC-BS.1770): loudness and true peak (the loudness checker's K-weighting and gating).
- [EBU R 128](https://tech.ebu.ch/publications/r128) and [EBU Tech 3342](https://tech.ebu.ch/publications/tech3342): loudness normalisation and loudness range.
- [ITU-R BT.709](https://www.itu.int/rec/R-REC-BT.709): display encoding for measurement and delivery.
- [ITU-R BT.1359](https://www.itu.int/rec/R-REC-BT.1359): sound and picture timing tolerances.
- G. Sharma, W. Wu, E. N. Dalal, [The CIEDE2000 color-difference formula](https://doi.org/10.1002/col.20070) (2005): the ΔE00 checks.

#### Materials and light

- B. Walter, S. Marschner, H. Li, K. Torrance, [Microfacet Models for Refraction through Rough Surfaces](https://www.graphics.cornell.edu/~bjw/microfacetbsdf.pdf) (EGSR 2007).
- E. Heitz, [Understanding the Masking-Shadowing Function in Microfacet-Based BRDFs](https://jcgt.org/published/0003/02/03/) (JCGT 2014).
- C. Kulla, A. Conty, [Revisiting Physically Based Shading at Imageworks](https://blog.selfshadow.com/publications/s2017-shading-course/imageworks/s2017_pbs_imageworks_slides_v2.pdf) (SIGGRAPH course, 2017).
- O. Gulbrandsen, [Artist Friendly Metallic Fresnel](https://jcgt.org/published/0003/04/03/) (JCGT 2014).
- B. Burley, [Physically-Based Shading at Disney](https://blog.selfshadow.com/publications/s2012-shading-course/burley/s2012_pbs_disney_brdf_notes_v3.pdf) (SIGGRAPH course, 2012).
- Academy Software Foundation, [OpenPBR Surface](https://academysoftwarefoundation.github.io/OpenPBR/).
- [Physically Based](https://physicallybased.info/), a database of measured material values.
- I. Motoyoshi, S. Nishida, L. Sharan, E. Adelson, [Image statistics and the perception of surface qualities](https://doi.org/10.1038/nature05724) (Nature, 2007).
- R. Fleming, R. Dror, E. Adelson, [Real-world illumination and the perception of surface reflectance properties](https://doi.org/10.1167/3.5.3) (Journal of Vision, 2003).
- P. Debevec, J. Malik, [Recovering High Dynamic Range Radiance Maps from Photographs](https://pauldebevec.com/Research/HDR/) (SIGGRAPH 1997).
- F. Hunter, S. Biver, P. Fuqua, [*Light: Science and Magic*](https://www.routledge.com/Light-Science-and-Magic-An-Introduction-to-Photographic-Lighting/Hunter-Biver-Fuqua/p/book/9781138816411) (Routledge).

#### Composition, camera and cutting

- X. Hou, L. Zhang, [Saliency Detection: A Spectral Residual Approach](https://doi.org/10.1109/CVPR.2007.383267) (CVPR 2007): the saliency term in `comp_analysis.py`.
- N. Otsu, [A Threshold Selection Method from Gray-Level Histograms](https://doi.org/10.1109/TSMC.1979.4310076) (1979): the squint masses.
- L. Liu, R. Chen, L. Wolf, D. Cohen-Or, [Optimizing Photo Composition](https://doi.org/10.1111/j.1467-8659.2009.01616.x) (Eurographics 2010).
- B. Gooch, E. Reinhard, C. Moulding, P. Shirley, [Artistic Composition for Image Creation](https://doi.org/10.2312/EGWR/EGWR01/083-088) (EGWR 2001).
- S. Palmer, J. Gardner, T. Wickens, [Aesthetic issues in spatial composition](https://doi.org/10.1163/156856808784532662) (Spatial Vision, 2008).
- S. Amirshahi et al., [Evaluating the Rule of Thirds in Photographs and Paintings](https://doi.org/10.1163/22134913-00002024) (Art & Perception, 2014): why the thirds score is advisory.
- T. Flash, N. Hogan, [The coordination of arm movements](https://doi.org/10.1523/JNEUROSCI.05-07-01688.1985) (1985): the minimum-jerk model behind operator drift.
- J. Cutting, [The evolution of pace in popular movies](https://doi.org/10.1186/s41235-016-0029-0) (2016).
- Edward Dmytryk's [rules for editors](https://www.provideocoalition.com/seven_rules_for_film_and_video_editors/), from *On Film Editing*.
- Karen Pearlman, [*Cutting Rhythms*](https://www.routledge.com/Cutting-Rhythms-Intuitive-Film-Editing/Pearlman/p/book/9781032399447) (Routledge).
- Apple, [Apple Watch reveal film](https://www.youtube.com/watch?v=1f-jqBkqTvk) (2014): the pacing reference for the demo edit.

#### Sound and music

- Walter Murch: [interview at Transom](https://transom.org/2005/walter-murch/) and ["Stretching Sound to Help the Mind See"](https://www.filmsound.org/murch/stretching.htm); *In the Blink of an Eye*. The law of two-and-a-half is his.
- Michel Chion, [*Audio-Vision: Sound on Screen*](https://cup.columbia.edu/book/audio-vision/9780231185899) (Columbia University Press).
- C. Krumhansl, E. Kessler, [Tracing the dynamic changes in perceived tonal organization](https://doi.org/10.1037/0033-295X.89.4.334) (1982): key detection.
- Eight Apple product films, measured for loudness, spectrum and tonality (for example [AirPods Pro 3](https://www.youtube.com/watch?v=EMmKs8vMKhU)).

#### Film emulation

- Eastman Kodak motion picture film data: [VISION3 500T 5219](https://www.kodak.com/content/products-brochures/Film/VISION3-500T-Color-Negative-Film-7219-TECHNICAL-DATA.pdf), [VISION3 250D 5207](https://www.kodak.com/en/motion/product/camera-films/250d-5207-7207/), [VISION Color Print Film 2383](https://www.kodak.com/content/products-brochures/Film/KODAK-VISION-Color-Print-Film-2383-3383-data-sheet.pdf).
- Steve Yedlin, [On Color Science](https://www.yedlin.net/NerdyFilmTechStuff/OnColorScience/) and [On Film Grain Emulation](https://yedlin.net/NerdyFilmTechStuff/OnFilmGrainEmulation.html).
- The demo's print look follows the 8×10 colour negatives and chromogenic prints of [Stephen Shore](https://en.wikipedia.org/wiki/Stephen_Shore)'s *Uncommon Places*.

#### Tools it drives

[Claude Code](https://claude.com/claude-code) (Anthropic) · [Blender](https://www.blender.org) and Cycles · [OctaneRender](https://home.otoy.com/render/octane-render/) (OTOY) · [DaVinci Resolve Studio](https://www.blackmagicdesign.com/products/davinciresolve) (Blackmagic Design) · [build123d](https://github.com/gumyr/build123d) on [Open CASCADE](https://dev.opencascade.org) · [FFmpeg](https://ffmpeg.org) · [NumPy](https://numpy.org), [SciPy](https://scipy.org), [scikit-image](https://scikit-image.org), [Pillow](https://python-pillow.org), [OpenEXR](https://openexr.com) · [FigJam](https://www.figma.com/figjam/) through the Figma MCP server · optional AI music through [Comfy Cloud](https://www.comfy.org/cloud).

#### The demo film

- **Product.** The Braun PS 550, designed by Dieter Rams, modelled from [US design patent D251,557](https://patents.google.com/patent/USD251557S/en) (filed 1976). Braun's manuals and catalogues on the [Internet Archive](https://archive.org/details/braun-ps-550-s-bedienungsanleitung) and collector sites such as [Radiomuseum](https://www.radiomuseum.org/r/braun_ps550ps_55.html) and [HiFi-Wiki](https://www.hifi-wiki.de/index.php/Braun_PS_550) were used as reference only. Braun is a trademark of its owner; this project isn't affiliated with Braun.
- **Set.** [KitBash3D](https://kitbash3d.com) and [Greyscalegorilla](https://greyscalegorilla.com) assets through [Cargo](https://cargo.kitbash3d.com), used under their licence. The skies are Greyscalegorilla HDRIs.
- **Sound effects.**
  - ["Turning the Vinyl Turntable on"](https://freesound.org/s/648314/) by Cpfcfan10, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Excerpted and pitch-shifted.
  - ["lightSwitchClink"](https://freesound.org/s/64457/) by nicStage, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Excerpted and pitch-shifted.
  - Other effects from [Freesound](https://freesound.org), CC0.
- **Music.** Two songs by Nick Conn, composed in [Suno](https://suno.com) with the film's original generated records as reference and Claude's prompts. The original records were generated with [Stable Audio 3 Medium](https://huggingface.co/stabilityai/stable-audio-3-medium) (Stability AI) and [Sonilo](https://sonilo.com) through [Comfy Cloud](https://www.comfy.org/cloud); the soundscapes with Stable Audio 3.
- **Labels.** Two fictional record labels with their own names and art, laid out after measurements of real centre labels.


## License

[MIT](LICENSE)
