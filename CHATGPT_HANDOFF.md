# Still Linux — ChatGPT handoff

**Checkpoint: 2026-11-20 · repository initialization.**

- Canonical repository: `DoorBlox/search-linux`.
- Current initial `main` commit at creation: `cd77e5629799467eba4df23b9da21b506b590882`; requery before each write.
- Active implementation branch: `feat/arc-spaces-foundation-20261120`.
- Upstream reference: `driceroland/Search` release `v1.0.15`; never mistake `main` Unreleased as shipped.
- Architecture: GTK4 + WebKitGTK6 first, CPU fallback only for diagnosed GPU defects. Alternative Chromium engine is a research spike for extensions, not an approved migration.
- User priorities: faithful Arc-like vertical sidebar/pins/Spaces, real Chrome extensions where feasible, ultra-fast Crostini execution, verified design against upstream, ORBIT-level documentation/CI with one development lane.
- Existing previously delivered native ZIP was tested only at Python model/syntax level; Crostini UI launch, security isolation and performance are NOT RUN.
- A local Spaces v2 prototype is being integrated; never mark device acceptance complete from unit tests alone.

## Immediate next executable work
1. Land source baseline in repository plus tests, then edit `still/core.py` for v1→v2 space-compatible persistence and `still/app.py` for compact space dock.
2. Add unit tests: Space create/rename/switch, cross-space selection, private-tab leakage, v1 migration, corrupt file, atomic save.
3. Run exact-head CI and review PR diff; merge only when checks succeed.
4. Ask owner to run `./install-crostini.sh` and `./run.sh`, record UI screenshot and benchmarks before making a speed claim.
5. Research extension engines against 1Password, uBlock Origin Lite, Bitwarden, Vimium C and a synthetic MV3 extension; record feature/API scores.

## Continuation
Read `AGENTS.md`, roadmap, operations, progress, and recent PRs. Do **not** invent progress or assume tests happened. Update this file with exact SHA/PR and the next action after changes.
