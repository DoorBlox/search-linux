# Real Chromebook acceptance — owner action

This is a **device test**, not something the CI container can assert.

1. `./install-crostini.sh`; `./run.sh --diagnose`; `./run.sh`. If Wayland fails, `./run.sh --x11`. Never disable the WebKit sandbox.
2. Test `https://example.com`, Wikipedia, GitHub; Ctrl+T/W/Shift+T; URL/search input; back/forward; pin/unpin.
3. Create Personal/Work/Research Spaces; switch dock dots and Ctrl+Alt+1..3; check correct tabs, pinned rows and last active tab; reload browser and verify names/tabs persist.
4. Private Ctrl+Shift+N: visit a synthetic private URL, close, inspect `~/.local/share/still-browser/state.json`; URL, title and tab ID must NOT be in disk state.
5. Before any migration, back up `~/.local/share/still-browser`. Test schema-v1 migration on a disposable XDG_DATA_HOME directory, not the real profile.
6. Compare UI against upstream screenshot using the same resolution and zoom; capture light/dark, active, pinned and Space popup states.
7. Performance: compare Qt prototype to Still on same Chromebook; 3 runs each, record cold launch, peak/idle PSS, CPU, 5 live tabs, 20 restored lazy tabs, Figma/Docs scroll, video. Inspect `/proc/<pid>/smaps_rollup` rather than summing RSS.
8. Report GPU/compositor errors and exact distro `/etc/os-release` and package versions; no personal passwords or private tabs in screenshots.

Acceptance status remains NOT RUN until logs and real UI evidence are recorded.
