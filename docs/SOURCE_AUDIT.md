# Original Search source audit (2026-11-20)

Upstream: https://github.com/driceroland/Search; release v1.0.15 (2026-11-18). Latest checked main SHA at audit: 319ef8be6a9bca700a530f1ecdb061f559f43b87. Main also contains Unreleased changes and ROADMAP ideas; neither is evidence of released features.

README, LICENSE, CONTRIBUTING.md, NOTES.md, CHANGELOG.md, ROADMAP.md, SECURITY.md, Design.swift, Side.swift, TabBar.swift, Prefs.swift, SettingsIndex.swift, Shortcuts.swift and AI.swift were inspected.

License: MIT, copyright Office Commun. Original Search name/icon reserved by upstream README. Keep Still identity.

Upstream key behavior: very small WebKit Mac browser; vertical/top tabs, pinned icons, lazy restore, Spaces, profile-scoped state, 2–4 pane split, searchable libraries, network-level blocker, custom CSS element hiding, reader mode, PiP, passkeys/macOS Keychain, Chrome Web Store extensions using WKWebExtension + shims, opt-in bench/MCP agents, no compulsory cloud account or telemetry.

Upstream AI.swift sets AI.shipped=false, so it is not a shipping parity promise. Mac-only keychain/Apple Passwords/WebKit extension controller cannot be copied onto Linux.

Primary design file gives near-neutral ground and active-pills, not a colorful dashboard: Side.swift defines pinned squares, tabs on a grey wash, and column, with optional icon-only mode.

Craft Anything source inspected: README, AGENTS.md and crates/ai/src/rebuild/brief.rs/check.rs. Follow its evidence -> build -> compare -> unknowns method, not its exact tooling or architecture.
