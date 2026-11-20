# Still Linux — one canonical execution roadmap

**Owner intent:** faithful fast Linux port of Search v1.0.15, with Arc-like sidebar tabs and Spaces first, then Chrome extension compatibility, while keeping good ORBIT-style release discipline and Craft Anything-style evidence-driven replication. One developer lane; PRs are small, ordered and testable. No claim of 1:1 parity until evidence register is complete.

## Dependencies (acyclic)
P00 → P01 → P02 → P03 → P04 → P05; P02 → P06; P02 → P07; P02 → P08; P02 → P09; P03 → P10; P02 → P11; P05/P06/P07/P08/P09/P10/P11 → P12 → P13.

## Priorities, file boundaries, gates
| ID | Scope, prerequisites, implementation and acceptance | Primary files | Rollback |
|---|---|---|---|
| P00 DONE source audit | Freeze upstream v1.0.15, license/branding rules, test/feature matrix; compare CHANGELOG vs README and label Unreleased. | docs/SOURCE_AUDIT.md, docs/FEATURE_PARITY.md | revert docs |
| P01 READY native graphics | GTK4/WebKitGTK6 Crostini packaging, no forced software acceleration; launch, TLS, video and sandbox smoke on real Crostini. | run.sh, install-crostini.sh | use old ZIP, never merge data |
| P02 READY minimal browser | Lazy tabs, navigation, pinned slots, download/history/bookmark, session restoration/private separation. Test model & GUI. | still/app.py, still/core.py | previous known source, state copy |
| P03 ACTIVE Arc Spaces | Space dock, named/color spaces, per-space tabs and pins, Ctrl+Alt+1..9, migration v1→v2, history and privacy safeguards. Tests switching/reload/migration; signed-out cookie isolation explicitly excluded until profile stage. | still/core.py, still/app.py, still/style.css, tests/test_spaces.py | restore backup, v1 reader |
| P04 NEXT visual fidelity | Screenshot at same viewport, compare original sidebar row/pins/hover/active geometry, compact widths, light/dark, keyboard/focus, reduced motion. Accept no phantom settings. | still/style.css, still/app.py, docs/REPLICATION_EVIDENCE.md | CSS revert |
| P05 ACTIVE UX tabs | Drag reorder, dragging tabs across Spaces, groups, pinned folders, hover previews, last-active restore, close/undo, site icons and keyboard switcher. | still/tab* and GTK views | feature flags for rearrange |
| P06 navigation/data | Fuzzy local omnibox, clean links, history/bookmark search, downloads, per-site settings, permissions UI, robust progress/error states. | still/navigation*, still/app.py | previous model schema |
| P07 split/peek | 2–4 panes, persistent width, focus routing, link peek, restored sessions. | still/split* | split off, keep tabs |
| P08 privacy | Network-level blocking, per-site exceptions, reading mode, hide selector, CSS, site permissions; no sandbox weakening, tests for cross-origin. | still/privacy* | switch off optional filters |
| P09 identity/data | Profiles with isolated WebKit sessions, libsecret password integration (never plaintext), import/sync, no account/telemetry. | still/profiles*, still/vault* | backup/old profile data |
| P10 memory/performance | Lazy views, suspended tabs, Figma/Docs/YouTube Crostini baseline, PSS/CPU and 3-run medians vs Qt prototype, 20 tabs. No speed claims without numbers. | still/lifecycle*, tests/perf*, docs/PERFORMANCE.md | revert optimization |
| P11 EXTENSIONS ARCHITECTURE GATE | Evaluate CEF Chromium embedding, Electron subsets, WebKitGTK. Map MV3 service workers, DNR, permissions, content scripts, messaging, storage, OAuth and native messaging. Test uBlock Origin Lite, Bitwarden/1Password, Vimium C and synthetic MV3. Only then choose runtime; if compatibility demands Chromium accept measured memory tradeoff or dual-engine design. | docs/EXTENSIONS_ARCHITECTURE.md, spikes/* | no migration until supported tests |
| P12 browser automation | Explicit opt-in local Unix socket/MCP, agent-owned tabs, approval, revoke, no private access. Threat model + synthetic fixtures. | still/agent*, tests/agent* | disable socket |
| P13 parity/release | Full feature matrix, desktop integration, signed package, update/rollback, screenshot and real-device acceptance. No critical unverified security. | packaging/*, CHANGELOG.md | prior signed build |

Each step has a single owner (active ChatGPT session), independent acceptance, test evidence and rollback. No hidden parallel agents or automatic background progress.

## Never-claim rules
- GTK-only app is NOT Chrome extension capable. Electron `session.loadExtension` supports only a subset of Chrome APIs; Chromium Embedded Framework requires separate extension API verification. Run a real test matrix, not a theoretical yes.
- Spaces with a shared `NetworkSession` separate visible tabs, **not login cookies**. Sign-out isolation belongs in P09.
- A port of MIT code may replicate layout and behavior, but original Search name/icon must not be shipped.
- Do not label `SOURCE MERGED` as DEVICE PASS or RELEASED.
- User-provided Crostini logs indicate Qt software-rendered tile memory exhaustion; they do NOT prove WebKitGTK performance.

## Continuation checklist
Check live source/PR, read relevant upstream module, implement smallest READY item with tests, run CI exact SHA, compare screenshots, update one roadmap/status/handoff, then pick next item. Validate and retain backup/migration path before schema changes.
