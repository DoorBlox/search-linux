# Still Linux operations

## Work cycle
Observe current repository and upstream; pick the first READY roadmap ID; write acceptance before implementation; test a failing case; implement minimal reviewed changes; run relevant tests and source diff; open a focused PR; check exact head; update progress and handoff; merge safely. No six-agent choreography.

## Source labels
- **SOURCE:** merged or PR code and its exact SHA.
- **CI:** named checks on exact SHA, not previous branch results.
- **DEVICE:** tested by user on the specific Chromebook/Crostini system.
- **RELEASE:** installable packaged artifact validated for upgrade and rollback.

These are independent states. Never infer one from another.

## Branch and PR policy
`feat/<work-unit>-YYYYMMDD`, `fix/<work-unit>-YYYYMMDD`; one cohesive change per PR. Default to squash only after tests and review. Preserve `main` as a known buildable state. CI needs at least Python static/syntax, unit tests, shell syntax; add GTK/WebKit smoke on installed Linux image and browser fixture tests when available.

## Device acceptance (owner-assisted)
Run `./run.sh --diagnose`, then normal launch and `./run.sh --x11` only on broken Wayland. Capture: `uname -a`, `/etc/os-release`, installed GTK/WebKit versions, first-window time, 5 tabs, 20 restored tabs, idle PSS from `/proc/<pid>/smaps_rollup`, CPU use, graphics logs, screenshot at same viewport as Search reference. No screenshots of private accounts without redaction. Repeat tests at least three times. Stop if private data leak or security bypass.

## Recovery
Never mutate existing `~/search-linux` prototype data. Still data lives at `$XDG_DATA_HOME/still-browser` (default `~/.local/share/still-browser`); make offline backup before schema changes. Session writes are atomic, failing JSON is retained for recovery. Checkout previous reviewed commit to undo source. Disable feature behind a flag if possible; never silently wipe a user profile.

## Source of truth
One roadmap: `plans/SEARCH_LINUX_EXECUTION.md`. One status: `docs/PROGRESS.md`. One current handoff: `CHATGPT_HANDOFF.md`. Feature checklist: `docs/FEATURE_PARITY.md`. Release notes: `CHANGELOG.md`.

## Reproduction discipline (Craft Anything principles)
For each UI behavior preserve (a) upstream screenshot or implementation reference, (b) exact viewport+state, (c) measured geometry, (d) local implementation screenshot, (e) human-observable interaction test, (f) difference report and (g) unknowns with evidence needed. No estimated measurement presented as verified.
