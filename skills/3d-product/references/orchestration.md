# Orchestration: roles, briefs, user gates, permissions, status, hand-offs

Runs through every stage of the pipeline (SKILL.md stage 14). Who does what, how work is briefed and handed off, where
agents stop for the user, and how status is reported.

- **Roles.** Main (the lead) plans, checks every checkpoint itself, talks to the user and owns every "go". Builders own
  one study folder and import shared libraries read-only. The **independent auditor** is a fresh agent, never the
  builder. The engine agent runs the render nodes. Research agents deliver URLs and measurements, no downloads, no
  GPU while the lead renders; a quiet agent (20 min) is restarted with a narrower brief.
- **Briefs** carry the question, the standing rules that apply (quoted), what may not be touched (for a change:
  the file to version up and the only parameters to change), the budget, "the first complete build at once", the first
  checkpoint (≤ 60 min, `<study>/checkpoints/NN_*.jpg` + a STATUS.md line), the cadence, and the stage's Measure and
  gate section. Hard rules also become gates in the tools (a driver refuses a pack that hides an always-visible part).
- **User gates where agents stop:** the intention (1), the composition stamps each round and the locked shot list (7),
  the animatic and the final cut (9), the music pick and the sound lock (9.5), the "go" per act after the FKL in the
  final engine (11). Render gates the user sets ("no re-renders until…") hold until lifted.
- **Permissions.** A subagent blocked on work the user explicitly asked for is not a stopping point: main does it itself
  on the user's instruction (also user-approved downloads, which subagents can't take on relayed word). If main is
  blocked too: stop that outcome, finish the rest, give the exact allow-rule text; never route around a block (moving
  the work elsewhere counts) or ask another agent to retry. Render-node kills, reboots and server restarts follow the
  site's policy (`site-profile-example.md`); Resolve is saved and quit through its API; workstation processes: ask.
- **Status is measured, never predicted:** frames counted on the node (never through a share), GPU load, file times;
  "not yet confirmed" until new output lands; ETAs from the measured rate. When the user asks main to watch overnight,
  a check-in loop wakes main on stall, node down, supervisor gone, done, or every ~100 min (`render-supervision.md`
  §7). Main relays checkpoints as they land, never a pending agent's result. One owner per background watch.
- **Hand-offs are files:** parallel agents exchange versioned JSON specs, never prose; new tags per output (differing
  by more than case: APFS/SMB are case-insensitive); masters copied, never edited; poll a share's new folders over ssh
  (the SMB cache hides them). **Sheets before passes:** a spot-check sheet precedes every full pass, and main reviews
  every sheet by eye before the user sees it.
- **Hygiene.** Ask before deleting anything (scratch blends, superseded outputs; use the Trash). Paid APIs: log the
  balance before and after. Keys load in-process, never printed.

## Briefing a stage's agent
- Quote the stage's **Measure and gate** section from its reference into the brief: the agent's checkpoint carries
  those numbers, not prose.
- For any skill-writing agent: generic first principles only (no shot numbers, product nouns or study paths); review
  its diff for leakage before reporting done.

