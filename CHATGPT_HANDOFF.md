# Still Linux — ChatGPT handoff

**Current checkpoint: 2026-11-20.** Always requery before changes.

- Repository: `DoorBlox/search-linux`; current independent verified source main: `105c21e4d2900aa36d3925cce63851e8eff218c0`, from PR #1 (merged). Source PR #1 head `49fe295fc3f80bdc7d7a46860a6d9fbfd606321d` passed GitHub `static-and-tests`.
- Active branch: `feat/arc-tab-groups-organizing-20261120` (P05); code planned to integrate grouped sidebar, group model & v3 migrations. Check actual PR and SHA before claiming complete.
- Open priorities: issue #2 Arc tabs/groups; issue #3 extension host/engine compatibility; issue #4 Crostini graphics acceptance.
- Design reference: `driceroland/Search` v1.0.15. Main SHA `319ef8be6a9bca700a530f1ecdb061f559f43b87` inspected for extra source guidance only; main Unreleased != shipped.
- Architecture: native GTK4 + WebKitGTK6. **Chrome Web Store compatibility NOT implemented**, and a Space is currently only visual/session tab isolation, NOT a cookie-isolated profile.
- Original Qt prototype fails GPU/Wayland and software path causes tile memory exhaustion on the owner's Chromebook. Real performance benefit of GTK/WebKit is unverified.
- Test split: Python/model source checks vs GitHub CI exact commit vs actual Crostini GUI security/performance vs published release. No conflation.

## Next executable tasks
1. Verify P05 PR exact SHA and `static-and-tests` result, review the actual diff for accidental schema or privacy changes.
2. If green, merge source safely and update handoff SHA (do not call it device pass).
3. Obtain synthetic+owner assisted Crostini screenshot and benchmark for the device-gated GTK UX, using `docs/CROSTINI_TEST_PROTOCOL.md`.
4. Complete issue #2 remaining drag/drop and visual parity after hardware evidence.
5. Start issue #3 scoped CEF/Electron/WebKit MV3 extension API benchmarks; no unverified extension promise.

Conventions: `AGENTS.md`, `docs/OPERATIONS.md`, and the ONE `plans/SEARCH_LINUX_EXECUTION.md`. Craft Anything-style observe/measure/compare/unknowns. No multi-agent orchestration or unchecked hosted changes.
