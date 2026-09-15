#!/bin/bash
set -e
set -o pipefail

cd "$(dirname "$0")"

echo "[Puresteel] Cleaning..."
sudo lb clean

echo "[Puresteel] Regenerating config..."
lb config

echo "[Puresteel] Restoring branding..."
rm -f config/bootloaders/splash.svg
cp branding/grub-splash.png config/bootloaders/splash.png
cp branding/grub-theme.txt config/bootloaders/grub-pc/live-theme/theme.txt
cp branding/grub-theme.cfg config/bootloaders/grub-pc/theme.cfg

echo "[Puresteel] Building ISO..."
sudo lb build 2>&1 | tee build.log
