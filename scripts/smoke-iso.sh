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
# i386 foreign architecture and preinstalled gaming libraries must survive
# into the installed systems; the installed-package check below verifies them.
if ! unsquashfs -cat "$SQUASH" var/lib/dpkg/arch > "$TEMP/dpkg-arch"; then
    echo "Missing dpkg multiarch registry in live filesystem." >&2
    exit 1
fi
if ! grep -Fxq i386 "$TEMP/dpkg-arch"; then
    echo "i386 foreign architecture missing from live filesystem." >&2
    exit 1
fi
if ! unsquashfs -cat "$SQUASH" var/lib/dpkg/status > "$TEMP/status"; then
    echo "Missing installed dpkg database in filesystem" >&2
    exit 1
fi
# Verify installed status, not only package presence in a dpkg stanza.
python3 - "$TEMP/status" <<'PY'
import sys
from pathlib import Path

installed = set()
for paragraph in Path(sys.argv[1]).read_text(errors="replace").split("\n\n"):
    fields = {}
    for line in paragraph.splitlines():
        if ": " in line and not line.startswith((" ", "\t")):
            name, value = line.split(": ", 1)
            fields[name] = value
    if fields.get("Status") != "install ok installed":
        continue
    name = fields.get("Package")
    arch = fields.get("Architecture", "")
    if name:
        installed.add((name, arch))

expected = {
    "puresteel-center", "puresteel-platform", "puresteel-recovery",
    "puresteel-branding", "puresteel-default-settings", "steam-installer",
    "steam-devices", "wine", "wine64", "winetricks",
    "gamemode", "mangohud", "kdenlive", "audacity", "ffmpeg",
    "build-essential", "cmake", "ninja-build", "python3-venv", "git-lfs",
}
missing = sorted(name for name in expected
                 if not any(p == name for p, _ in installed))
multiarch = {
    "wine32", "steam-libs-i386", "libvulkan1", "mesa-vulkan-drivers",
    "libgl1-mesa-dri", "nvidia-driver-libs", "nvidia-vulkan-icd",
}
missing += sorted(name + ":i386" for name in multiarch
                  if (name, "i386") not in installed)
if missing:
    raise SystemExit("Missing full-ISO packages: " + ", ".join(missing))
print("Full-edition APT packages and i386 gaming drivers verified in ISO.")
PY

# Full-edition system Flatpaks and runtimes must be physically in the ISO.
for app in com.heroicgameslauncher.hgl net.davidotek.pupgui2 org.onlyoffice.desktopeditors; do
    if ! unsquashfs -ll "$SQUASH" "var/lib/flatpak/app/$app" | grep -Fq "$app"; then
        echo "Required system Flatpak missing inside ISO: $app" >&2
        exit 1
    fi
done
echo "Static ISO filesystem and installed-package checks PASSED."
echo "Calamares and Recovery still require fresh-install QEMU testing."
