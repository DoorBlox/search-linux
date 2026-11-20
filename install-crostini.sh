#!/bin/sh
set -eu
printf 'Installing native GTK4/WebKitGTK browser dependencies (Debian 13)...\n'
sudo apt-get update
sudo apt-get install -y python3 python3-gi gir1.2-gtk-4.0 gir1.2-webkit-6.0 xdg-utils
printf 'Installed. Run: ./run.sh\n'
