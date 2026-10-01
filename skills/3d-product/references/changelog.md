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
