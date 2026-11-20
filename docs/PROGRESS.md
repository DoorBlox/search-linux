# Source / CI / Crostini / Release status

**2026-11-20:** P01–P03 browser baseline **SOURCE MERGED** in PR #1 to main `105c21e4d2900aa36d3925cce63851e8eff218c0`; exact PR source head `49fe295fc3f80bdc7d7a46860a6d9fbfd606321d` passed `static-and-tests` CI. Crostini GUI, GPU performance and security runtime acceptance **NOT RUN**.

**Current source candidate:** P05 Arc-like groups/reordering in `feat/arc-tab-groups-organizing-20261120`; schema v3, migrated from v1/v2, group hierarchy and Space color controls. Local model suite for corresponding logic: 30 tests passed; GitHub exact-head CI pending. Do not mark it merged before confirmed CI and review.

| Unit | Source | CI | Device | Release |
|---|---|---|---|---|
| P01 native GTK/WebKit | Merged PR #1 | PASS on #1 exact head | NOT RUN | Not released |
| P02 browser shell | Merged PR #1 | PASS on #1 exact head | NOT RUN | Not released |
| P03 named Spaces & pins | Merged PR #1 | PASS on #1 exact head | NOT RUN | Not released |
| P05 groups and ordering | PR candidate branch | NOT RUN at current head | NOT RUN | Not released |
| P04 visual parity | Partial style tokens | NOT RUN | NOT RUN | Not released |
| P11 Chrome extensions | Architecture-only, issue #3 | NOT RUN | NOT RUN | Not released |

See issues #2, #3, #4 and the one `plans/SEARCH_LINUX_EXECUTION.md` roadmap.
