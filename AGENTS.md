# Still Linux — repository instructions

This repository is the canonical source for **Still**, a Linux/Crostini browser based on the MIT-licensed design and behavior of [Office Commun's Search](https://github.com/driceroland/Search). Never distribute using upstream's reserved Search name or icon.

## Mandatory start
1. Read `CHATGPT_HANDOFF.md`, `docs/PROGRESS.md`, `plans/SEARCH_LINUX_EXECUTION.md`, and `docs/OPERATIONS.md`.
2. Inspect live `main`, open PRs/issues, exact commit statuses, relevant code and tests. Historical handoffs are evidence, not instructions overriding current state.
3. Execute the highest-priority READY source task. Make a focused branch and PR with tests and rollback. No parallel worker protocol is required.
4. Update the **single** canonical roadmap, progress, changelog, and handoff in the same PR. Do not claim locally tested code is installed or user-accepted.
5. Never merge a RED PR or silently modify release data, browser profiles, tokens, privileged permissions, or published release assets.

## Engineering contract
- Default: native GTK4 + WebKitGTK 6.0 on Debian 13, rendering accelerated unless Crostini data disproves it. Never disable the sandbox or TLS validation to mask bugs.
- **Priority:** Arc-like sidebar, spaces and tab organization; reliable crash-safe persistence; responsive native UI; deliberate Chrome extension compatibility research; measured memory/latency.
- Original upstream Search macOS **v1.0.15** is feature-parity reference, with later `main` changes classified as unreleased. Screenshot and source comparisons must be evidence-backed.
- Preserve private tabs from persistence, keep profile cookie jars genuinely isolated when implemented, and never treat a Space with shared cookies as a signed-out profile.
- Chrome extensions: do not claim WebKitGTK supports Chrome Web Store. Run an architectural engine/API spike and keep unsupported APIs explicit. Never execute unpacked code with privileged browser permissions by default.
- Follow Craft Anything's **observe → measure → implement → compare → log unknowns → verify** approach; preserve traceable screenshots and exact-source evidence.
- Changes need unit tests for logic, E2E/browser tests for UI or security when possible, and real Crostini acceptance where containers cannot render.
- No auto-merge unless exact-head checks pass and the diff is reviewed. GitHub source merge != packaged Linux release or device validation.
- Report PASS/FAIL/NOT RUN honestly. Keep rollback from old release and schema backup before migration.

## File ownership
`still/core.py`: data and tab/space model. `still/app.py`: GTK integration. `still/style.css`: design tokens. `tests/`: deterministic regressions. `docs/`: evidence and operations. `plans/SEARCH_LINUX_EXECUTION.md`: the ONE current implementation roadmap.

## Handoff update format
At the top of `CHATGPT_HANDOFF.md`: exact main SHA; branch/PR head; tests/CI; source-vs-device-vs-release status; decisions; defects; next file-level action and acceptance; rollback. Avoid long duplicated historical prose.

