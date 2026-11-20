# Still Linux — ChatGPT handoff

**Checkpoint: 2026-11-20 · source merged, device acceptance pending.** Always requery before another source write.

## Live source and tests
- Repository: `DoorBlox/search-linux`.
- Verified `main` after **PR #1**: `105c21e4d2900aa36d3925cce63851e8eff218c0` (base GTK/WebKit shell/Spaces).
- Verified `main` after **PR #5**: **`83bd04605f0a2633a16cb8000574d0a08372f1df`** (Arc-like collapsible groups, group model/schema v3, Space color picker and sidebar menus).
- PR #1 exact head `49fe295fc3f80bdc7d7a46860a6d9fbfd606321d` had `static-and-tests` success in run `44655226370`.
- PR #5 exact head `0fbaf9381a717b2d19d814efb0c3c37c6c1e6cdc` had `static-and-tests` success in run `44655830520`. PR #5 squash merged to main at `83bd046...`.
- This documentation-only handoff update is in branch `docs/verified-handoff-and-crostini-onboarding-20261120`; check its PR and merge state separately.
- **Crostini GUI/performance/security runtime acceptance NOT RUN.** GitHub tests are model/syntax/shell checks only. No signed Linux release exists.
- Upstream Search release `v1.0.15` (2026-11-18); its main `319ef8be6a9bca700a530f1ecdb061f559f43b87` included unreleased code in source audit.

## Implementation
- Native GTK4/WebKitGTK6 one-window shell, basic tabs, shortcuts, bookmarks/history, private session, lazy tab restore.
- Named Spaces + dock + per-Space tab lists, named collapse/expand tab groups and right-click tab organization, colors and migrated schema v1/2→v3. **Regular Spaces share cookies; they are NOT signed-out profiles.**
- Current GUI is untested on ChromeOS. No Chrome extension engine is implemented, not even a synthetic MV3 extension.
- Original user logs concern Qt forced-software rendering `tile memory limits exceeded`; do not infer WebKit is fast until device profiling.

## Next executable tasks
1. User Crostini smoke for `main` per `docs/CROSTINI_TEST_PROTOCOL.md`, inspect launch/crash, screenshots, memory/PSS, cookie/private persistence and Space/group behavior. Record PASS/FAIL/NOT RUN in `docs/PROGRESS.md` and #4.
2. Issue #2: implement proper drag-and-drop reorder across Space/group, accessible context menus, icon-only bar, and compare same-viewport source screenshot. Add GUI interaction tests where available.
3. Issue #3: engine extension compatibility spike: WebKitGTK vs CEF/Electron Chromium subset; first synthetic MV3 APIs, then selected real extensions, with a security threat model. **Do not claim Chrome Web Store support** before evidence.
4. Iterate browser memory/performance based on Chromebook data, not synthetic predictions.

## Continuation protocol
Read `AGENTS.md`, `docs/OPERATIONS.md`, `docs/PROGRESS.md`, `plans/SEARCH_LINUX_EXECUTION.md`, review live issues, PRs, exact SHA and checks. One developer lane, no multi-agent protocol. Each safe source PR reviewed and exact-head green before merge. Source != CI != device != installed release. Keep main authoritative.
