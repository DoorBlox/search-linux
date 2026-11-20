# Evidence-driven Search → Linux replication

Derived from observed engineering practices of [Craft Anything](https://github.com/storytold/craft-anything): inspect actual evidence, capture multiple states/viewports, extract design tokens, track unknowns separately, implement, compare, verify and iterate. Do not confuse inferred behavior with observed functionality.

## Source hierarchy
1. Upstream Search tagged v1.0.15 source at its release commit.
2. README and actual code modules (`Side.swift`, `TabBar.swift`, `Spaces.swift`, `Design.swift`).
3. Release CHANGELOG; label Unreleased separately.
4. Published screenshot and help pages, then manual reference observations.
5. User Crostini device screenshots and performance traces for Linux implementation.

## Capture per screen
- Version/ref commit; OS/browser/viewport/scale/appearance; tab and Space state.
- Screenshot: baseline, hover, active, focus-visible, drag, empty, loading, error, narrow window, dark mode.
- Exact metric notes: sidebar width, row height, pinned tile gap, typography, active-pill radius, spacing, icon size.
- Keyboard+pointer behaviors and persistence after restart.
- Implementation screenshot at identical viewport; mismatch table severity, fix, rerun; unknowns for anything not verified.

## Acceptance
No screenshot-only claim: UI controls must operate. Unit model tests + integration smoke + a11y keyboard tests + Crostini visual comparison. A native GTK alternative to a macOS-only API must be documented as an equivalence mapping, not silently counted as identical.

## Unknowns registry
Record question, current assumption, severity, evidence required, source ref and status in `docs/REPLICATION_UNKNOWNS.md`. Do not substitute a speculative match.
