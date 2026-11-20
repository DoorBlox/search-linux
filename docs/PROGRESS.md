# Source / CI / Crostini / Release status

As of 2026-11-20, main initialized. Exact current source and PR status must be retrieved live before editing.

| Unit | Source | CI | Crostini device | Release |
|---|---|---|---|---|
| P00 upstream audit | Docs prepared | NOT RUN | Not applicable | Not shipped |
| P01 native GTK/WebKit baseline | Local ZIP prior turn, repository upload in progress | 9 model tests previously passed locally | NOT RUN | Prototype only |
| P02 browser shell | Local ZIP prior turn, repository upload in progress | Python syntax previously passed locally | NOT RUN | Prototype only |
| P03 Arc-style Spaces v1 | Local implementation candidate | 20 unit tests passed in local container (2026-11-20), GUI NOT RUN | NOT RUN | Not shipped |
| P04 visual parity | Tokens and sidebar work started | NOT RUN | NOT RUN | Not shipped |
| P11 Chrome extension compatibility | Architecture research only | NOT RUN | NOT RUN | Not shipped |

Do not elevate local container results to GitHub CI or device PASS. Next: source check-in, focused PR exact head, Crostini tests. Other milestones remain TODO (see roadmap).
