#!/bin/bash
set -e
set -o pipefail

cd "$(dirname "$0")"

echo "[Puresteel] Cleaning..."
sudo lb clean

echo "[Puresteel] Regenerating config..."
lb config --bootappend-live "boot=live components quiet splash username=puresteel hostname=puresteel"

echo "[Puresteel] Restoring branding..."
rm -f config/bootloaders/splash.svg
cp branding/grub-splash.png config/bootloaders/splash.png
cp branding/grub-splash.png config/bootloaders/grub-pc/splash.png
cp branding/grub-theme.txt config/bootloaders/grub-pc/live-theme/theme.txt
cp branding/grub-theme.cfg config/bootloaders/grub-pc/theme.cfg

echo "[Puresteel] Building Puresteel Center package..."
DEB="$(scripts/build-center-package.sh)"
mkdir -p config/packages.chroot
find config/packages.chroot -maxdepth 1 -type f -name 'puresteel-center_*.deb' -delete
cp -f "$DEB" config/packages.chroot/

echo "[Puresteel] Bundled $(basename "$DEB")"
test -f "config/packages.chroot/$(basename "$DEB")"

echo "[Puresteel] Building ISO..."
sudo lb build 2>&1 | tee build.log
