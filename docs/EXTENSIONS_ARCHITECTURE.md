# Chrome extension compatibility — platform decision gate

**Status: architecture spike only, not installed/working.** Upstream Search uses `WKWebExtension` and macOS-specific `ExtensionShims.swift`. Linux WebKitGTK does not expose that Safari extension controller. Reusing its Swift extension logic is not enough.

Three candidates:
1. **WebKitGTK6 + bridge:** lowest native footprint, but implementing MV3, DNR, worker lifecycle, store installation, content scripts, panel, OAuth and native messaging would be an enormous custom browser security surface.
2. **Chromium Embedded Framework (CEF):** likely closest engine behavior, but embedding, binary distribution and API completeness need tests, GPU/Crostini size pressure may increase.
3. **Electron:** practical extension loading and mature UI, but official `session.loadExtension` exposes only a supported subset of Chrome APIs, and Chromium bundling may be slow/heavy.

Evaluation matrix (each marked PASS/FAIL/NOT RUN): unpacked MV3 load, background service worker, content script in iframe, declarativeNetRequest, tabs/query/create, scripting, storage sync/local, messaging, permissions, popup, sidePanel, OAuth, nativeMessaging, Web Store CRX3 signature/integrity, per-profile isolation, private-mode permission gating, upgrade/revoke. Test uBlock Origin Lite, Vimium C, Bitwarden/1Password and a synthetic permission-abuse extension. Do not fetch/run arbitrary CRX without explicit user action and a permission review.

Decision rule: maximize verified compatibility while meeting real Crostini PSS/startup/scroll targets. A dual-engine architecture is possible only after threat model and profile separation. Unsupported APIs remain explicitly unsupported; never call it full Chrome compatibility before tests.
