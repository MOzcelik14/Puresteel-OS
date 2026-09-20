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

echo "[Puresteel] Building Puresteel packages..."
CENTER_DEB="$(scripts/build-center-package.sh)"
mapfile -t META_DEBS < <(scripts/build-meta-packages.sh)
mapfile -t COMPONENT_DEBS < <(scripts/build-component-packages.sh)
mkdir -p config/packages.chroot
find config/packages.chroot -maxdepth 1 -type f -name 'puresteel-*.deb' -delete
cp -f "$CENTER_DEB" config/packages.chroot/
# Optional Gaming/Creator/Developer roles stay in the signed APT repository.
for DEB in "${META_DEBS[@]}"; do
    case "$(basename "$DEB")" in
        puresteel-base_*.deb|puresteel-desktop_*.deb) cp -f "$DEB" config/packages.chroot/ ;;
    esac
done
for DEB in "${COMPONENT_DEBS[@]}"; do
    cp -f "$DEB" config/packages.chroot/
done

echo "[Puresteel] Bundled Center + 2 lean metapackages + ${#COMPONENT_DEBS[@]} maintained component packages"
test -f "config/packages.chroot/$(basename "$CENTER_DEB")"
test -f config/packages.chroot/puresteel-base_*.deb
test -f config/packages.chroot/puresteel-platform_*.deb
test -f config/packages.chroot/puresteel-recovery_*.deb

echo "[Puresteel] Building ISO..."
sudo lb build 2>&1 | tee build.log
