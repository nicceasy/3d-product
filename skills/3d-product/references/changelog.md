# Changelog

Append a dated line whenever a session tests something new, overturns a verdict or changes a default (see "Keeping the
skill alive" in `SKILL.md`). Keep project specifics (shot numbers, part names, paths) in your own study notes.

## 1.0.0 · October 2026 · first public release
- Built over nine days of studies that ended in a 98-second film of a 1976 hardware product, modelled from its design
  patent and reference photos, rendered in Octane and finished by script.
- Sixteen gated stages, from the brief and a hardware probe to review and delivery, with the user's decisions marked
  (★): intention, compositions and shot list, the cut, the music, and the go for each act of the render.
- Two production paths (Octane: a converted master scene, animation packs and a kept-alive session; Cycles: one
  `.blend` per shot), chosen by `scripts/probe_setup.py` for the hardware it finds.
- References for every stage, written as general principles: the rule, why, a procedure, and numbers labelled as
  measured. Known failures and their fixes are in `traps.md`.
- Scripts: the setup probe, the "reads" lighting metric with an example calibration, a loudness checker for the mix,
  a macro depth-of-field calculator, a plain-shell overnight render supervisor template with example site hooks, and a
  FigJam section builder.

## 1.1.0 · October 2026 · every stage measured, the scene light from the start
- **Every stage ends with a measured record.** Each stage's main reference gains a "Measure and gate" section: numbers
  against stated pass values, the tool or method, and a sheet. The eye still decides, after the numbers.
- **Light from the start.** A `budget.json` is written at stage 0.5 from the smallest render card and the machine-time
  budget (`scripts/budget.example.json`); every 3D stage writes a weight line with `scripts/scene_weight.py --budget`
  and fixes outliers where they are made (`scene-optimisation.md` §0). Stage 10 becomes production readiness: verify
  the budgets, sweep sampling per shot on the final frames, one complete hashed settings spec per shot, then the estimate.
- **Modelling:** geometry sources ranked by authority with one source held out; mesh QA on every export (chord by
  screen need, exact normals, slivers, poles; `hard-surface.md` §2b); overlaps measured on solids and meshes in every
  pose of a pose matrix; keep-it-light build rules (instancing, static parts static, UVs at build, one rest pose plus a
  pivots file); a published, versioned, engine-agnostic master (`patent-to-model.md` §0, §6–8).
- **Materials and environments:** swatches passed by number, patch-ratio audits, albedo from cited values; asset
  import pre-flight and texture variants by role; in-render albedo and silhouette audits; silhouette detail by
  displacement derived from the albedo; a realism manifest read back at FIRST/KEY/LAST.
- **Lighting:** the light-state sheet on real product materials; haze opt-in with its cost; lights that converge
  (analytic bulbs with the shade as its own emitter, glowing props out of light sampling, glass sampling aids checked
  per state); reflection and hot-spot audits; a convergence record per state.
- **Engines:** no denoiser by default (sample to a noise target tied to the grain); sampling archetypes per light state;
  temporal metrics; a complete, costed output spec with part IDs. Octane adaptive sampling re-measured: it pays where
  pixels converge; static noise is a per-shot trade.
- **Compositions:** new `composition-analysis.md` (pre-gate, frame gates G1–G9, placement, eye path and balance,
  scene–subject harmony, one size table by role) and `scripts/comp_analysis.py` (`frame`, `sameness`, `cuts`).
  Stand-alone compositions come first; the lock-in samples only legal simple moves between stamped compositions.
- **Motion and edit:** FIRST and LAST are outcomes of the move chosen for them; an ease budget; the edit frames file as
  the contract every consumer reads; the composition re-gate after any camera or cut change; new
  `scripts/motion_qa.py` (`shots`, `compare`, `cuts`, `regate`).
- **Sound:** gate the loudness steps and the entries, not the range; level notes mapped to numbers; a music map before
  the first build. `scripts/loudness_profile.py` reports the range only and adds an entry-ramp gate.
- **Production and finishing:** a key-frame level check before every sequence; jump-scans of finished shots; a
  pre-roll frame when a render resumes; supervisor drift alerts (`drift_check` hook); pausing a queue and optional agent
  check-ins (`render-supervision.md`); highlight recovery, size-guarded glare on named shots only and colour-temperature
  matching between neighbours (`finishing.md` §6); film emulation as an alternative finish (`finishing.md` §7).
- **Review:** the synced review folder holds review videos only; stills and sheets go on the board.
- New `orchestration.md` (roles, briefs, user gates, permissions, status). New traps under Production renders.
