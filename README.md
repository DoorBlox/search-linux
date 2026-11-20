# Still Browser for Linux

**A quiet, native Linux browser with Arc-like Spaces and sidebar tabs, inspired by Office Commun's [Search](https://github.com/driceroland/Search).**

**Current status: source prototype, 0.2.x development.** Source-level Python tests pass on GitHub Actions. **Graphical startup, memory usage, rendering and site compatibility have NOT yet been verified on the target Chromebook.** Still is **not** a completed 1:1 port, does **not** yet support Chrome Web Store extensions, and has no password-vault implementation.

## Run on ChromeOS Crostini (Debian 13)

Open your Crostini Terminal, then:

```sh
git clone https://github.com/DoorBlox/search-linux.git
cd search-linux
./install-crostini.sh
./run.sh
```

If you already cloned this repository, run `git pull --ff-only` inside it (avoid discarding local modifications). If your graphics session crashes, try `./run.sh --x11`. Use `./run.sh --diagnose` to get platform/package diagnostics. `./run.sh --software` is a **slow last-resort troubleshooting option**, not the recommended normal launch.

The old Qt test app in `~/search-linux` is independent of Still's files and remains untouched. This repository stores data in `~/.local/share/still-browser/`. **Back up this directory before upgrading from an earlier Still prototype,** as schema 1/2 migrates to schema 3 on the next save.

## What is currently implemented

- GTK4 + WebKitGTK6 (native Linux WebKit engine; no bundled Chromium); normal accelerated rendering preferred
- Tabs with session restoration (lazy WebView creation), horizontal or compact vertical layout, pinned site tiles
- Arc-like **Spaces**: named workspaces, a compact Space dock, color picker, keyboard switching, per-Space tabs
- Collapsible **tab groups** inside each Space, right-click contextual grouping, move to another Space, up/down ordering
- Omnibox, back/forward/reload, local history and bookmarks, find-in-page, zoom, downloads
- Private tabs with ephemeral WebKit network session and no persisted tab URL/title/ID
- Automatic unit tests, single authoritative roadmap, decision/unknown registers, and exact-source CI

**Important boundaries:** Spaces currently share regular browsing cookies. They organize tabs but do **not** isolate accounts; proper profiles are planned separately. Group tab ordering uses menu commands, not drag-and-drop yet. Native visual matching, ad blocking, split view, password/passkey handling, page translation, Apple integrations and Chrome extension support are not yet implemented.

## Shortcuts

| Keys | Action |
|---|---|
| Ctrl+T / Ctrl+W / Ctrl+Shift+T | New / Close / Reopen tab |
| Ctrl+Shift+N | New private tab |
| Ctrl+L | Address and search |
| Ctrl+K | Tab switcher |
| Ctrl+1…9 / Ctrl+Tab | Switch tabs within current Space |
| Ctrl+Alt+1…9 | Switch Spaces |
| Ctrl+F / Ctrl+R | Find / Reload |
| Ctrl+Shift+B | Bookmark |
| Ctrl+Shift+S | Toggle side/top tabs |
| Ctrl+S | Fold/unfold tab sidebar |

Tabs and Spaces can also be managed by right-click and by the Space title at the top of the column.

## Tests and device acceptance

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q still tests
sh -n run.sh && sh -n install-crostini.sh
```

These tests cover browser models and source syntax but cannot prove that WebKitGTK renders properly on ChromeOS. Follow `docs/CROSTINI_TEST_PROTOCOL.md` for actual graphical and performance acceptance. Issues [#2](https://github.com/DoorBlox/search-linux/issues/2), [#3](https://github.com/DoorBlox/search-linux/issues/3), and [#4](https://github.com/DoorBlox/search-linux/issues/4) track UI polish, extensions and real-device verification.

## Architecture, references, and credits

The current implementation is Python/PyGObject for the GTK window and WebKitGTK for web content. The browser’s user-visible UI is based on the neutral, restrained tab/Space behavior of Search's SwiftUI frontend. [Search](https://github.com/driceroland/Search) is MIT-licensed, copyright Office Commun. **The original “Search” product name and icon are reserved and are not reused here.** Still is not the official Search Browser for Linux.

The project uses:
- `AGENTS.md` — development/review instructions
- `CHATGPT_HANDOFF.md` — current exact-SHA checkpoint
- `plans/SEARCH_LINUX_EXECUTION.md` — **one** canonical roadmap
- `docs/PROGRESS.md` — source/CI/device/release statuses
- `docs/REPLICATION_CONTRACT.md` — evidence-driven UI comparison inspired by [Craft Anything](https://github.com/storytold/craft-anything)
- `docs/EXTENSIONS_ARCHITECTURE.md` — extension-engine compatibility gate
- `docs/OPERATIONS.md` — release discipline inspired by [ORBIT](https://github.com/DoorBlox/orbit)

Privacy and security protections must remain in place; do not disable TLS or sandbox checks to fix site issues. Contributions should use focused PRs with tests, rollback and up-to-date handoff.
