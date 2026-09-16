#!/bin/sh
sleep 2
plasma-apply-wallpaperimage /usr/share/backgrounds/puresteel/wallpaper.png >/dev/null 2>&1 || true
rm -f "$HOME/.config/autostart-scripts/puresteel-wallpaper.sh"
