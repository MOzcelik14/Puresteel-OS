#!/usr/bin/env bash
# Static content checks against the actual ISO; NOT a fresh-install emulator.
set -euo pipefail
ISO="${1:-}"
if [[ -z "$ISO" || ! -f "$ISO" ]]; then
    echo "Usage: $0 /path/to/puresteel.iso" >&2
    exit 2
fi
for tool in xorriso unsquashfs; do
    command -v "$tool" >/dev/null 2>&1 || { echo "Missing $tool" >&2; exit 1; }
done
TEMP="$(mktemp -d)"
trap 'rm -rf "$TEMP"' EXIT
xorriso -osirrox on -indev "$ISO" -extract /live/filesystem.squashfs "$TEMP/filesystem.squashfs" >/dev/null
SQUASH="$TEMP/filesystem.squashfs"
for file in \
    usr/local/bin/puresteelctl \
    usr/local/bin/puresteel-info \
    usr/local/bin/puresteel-first-run \
    usr/local/bin/puresteel-snapshots \
    usr/local/sbin/puresteel-recovery \
    etc/grub.d/09_puresteel_recovery \
    usr/lib/puresteel-center/puresteel-helper \
    etc/sddm.conf.d/10-puresteel.conf \
    etc/skel/.config/kdeglobals \
    usr/share/sddm/themes/breeze/theme.conf.user \
    usr/local/bin/puresteel-wifi \
    usr/local/bin/puresteel-desktop-init; do
    if ! unsquashfs -cat "$SQUASH" "$file" >/dev/null 2>&1; then
        echo "Missing inside live filesystem: $file" >&2
        exit 1
    fi
done
if ! unsquashfs -cat "$SQUASH" var/lib/dpkg/status > "$TEMP/status"; then
    echo "Missing installed dpkg database in filesystem" >&2
    exit 1
fi
for name in puresteel-center puresteel-platform puresteel-recovery puresteel-branding puresteel-default-settings; do
    if ! grep -Fxq "Package: $name" "$TEMP/status"; then
        echo "Package is not registered inside ISO: $name" >&2
        exit 1
    fi
done
echo "Static ISO filesystem and installed-package checks PASSED."
echo "Calamares and Recovery still require fresh-install QEMU testing."
