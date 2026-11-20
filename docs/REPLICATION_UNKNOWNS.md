# Open evidence gaps

| ID | Question | Severity | Evidence to resolve | State |
|---|---|---|---|---|
| U01 | Does GTK4 + WebKitGTK6 run smoothly on this Chromebook's Wayland/XWayland? | Critical | Native run logs, PSS, video, 5/20 tabs, 3 repeats | OPEN |
| U02 | Is the Spaces sidebar visually faithful on 100%, 125%, 150% ChromeOS scales? | High | Same-resolution screenshots against Search upstream | OPEN |
| U03 | Can Chromium extension API requirements be met without breaking low-memory goal? | Critical | CEF/Electron/WebKit test matrix on real MV3 extensions | OPEN |
| U04 | Is hardware WebAuthn/passkeys exposed through Crostini web engine? | High | Real WebAuthn smoke with opt-in user credentials | OPEN |
| U05 | What process model bounds background tab memory without breaking active media? | High | WebKit process profiling and keep-awake tests | OPEN |
