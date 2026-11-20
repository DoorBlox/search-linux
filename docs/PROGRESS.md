# Still Linux — source, CI, device and release status

**2026-11-20.** Native Linux browser source has two completed focused PRs; device acceptance has **not** happened.

| Milestone | Source | GitHub exact-head CI | Chromebook device | Packaged release |
|---|---|---|---|---|
| P01 native WebKit/GTK launch | PR #1 merged to main `105c21e` | PASS `static-and-tests` | NOT RUN | No |
| P02 basic tabs/private/history | PR #1 merged | PASS on #1 head `49fe295` | NOT RUN | No |
| P03 Spaces | PR #1 merged | PASS on #1 head | NOT RUN | No |
| P05 collapsible groups/reordering menus | PR #5 merged `83bd046` | PASS on #5 head `0fbaf93` | NOT RUN | No |
| P04 visual 1:1 comparison | Basic neutral CSS, not equivalent complete UX | No visual checks | NOT RUN | No |
| P11 Chrome extensions | Architecture/compatibility research only, issue #3 | NOT RUN | NOT RUN | No |
| P09 login-isolated profiles | Not implemented | NOT RUN | NOT RUN | No |
| P07 split/peek | Not implemented | NOT RUN | NOT RUN | No |

**Outstanding:** Issue #4 needs owner device logs. Issue #2 needs full drag/drop and pixel comparison. Issue #3 needs verified engine test matrix and extension host. For complete priorities see `plans/SEARCH_LINUX_EXECUTION.md`.

Baseline source merge verification:
- PR #1 source head `49fe295fc3f80bdc7d7a46860a6d9fbfd606321d`, run `44655226370`, SUCCESS, main `105c21e4d2900aa36d3925cce63851e8eff218c0`.
- PR #5 source head `0fbaf9381a717b2d19d814efb0c3c37c6c1e6cdc`, run `44655830520`, SUCCESS, main `83bd04605f0a2633a16cb8000574d0a08372f1df`.

No GUI performance, security, or Chrome extension claim is justified by the model tests alone.
