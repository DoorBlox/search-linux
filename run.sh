#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ "${1:-}" = "--diagnose" ]; then
  printf 'Still Crostini diagnostic\n'
  uname -sr
  printf 'DISPLAY=%s WAYLAND_DISPLAY=%s GDK_BACKEND=%s\n' "${DISPLAY:-}" "${WAYLAND_DISPLAY:-}" "${GDK_BACKEND:-default}"
  dpkg-query -W gir1.2-gtk-4.0 gir1.2-webkit-6.0 python3-gi 2>&1 || true
  exec /usr/bin/python3 -c 'import gi; gi.require_version("Gtk", "4.0"); gi.require_version("WebKit", "6.0"); from gi.repository import Gtk,WebKit; print("GTK4 + WebKitGTK6: OK")'
fi
if [ "${1:-}" = "--x11" ]; then
  export GDK_BACKEND=x11
  shift
fi
if [ "${1:-}" = "--software" ]; then
  export WEBKIT_DISABLE_COMPOSITING_MODE=1
  shift
fi
# Do not disable the browser sandbox or TLS verification.
exec /usr/bin/python3 -m still "$@"
