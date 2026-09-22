#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

PKGROOT="packages/puresteel-center"
ROOTFS="$PKGROOT/rootfs"
VERSION="${PURESTEEL_PACKAGE_VERSION:-$(tr -d '[:space:]' < "$REPO/packages/puresteel-center/VERSION")}"
OUTDIR="build/packages"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$OUTDIR"
cp -a "$ROOTFS/." "$STAGE/"
# Source-tree Python caches are not release artifacts.
find "$STAGE" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "$STAGE" -type f -name '*.pyc' -delete
mkdir -p "$STAGE/DEBIAN" "$STAGE/usr/share/puresteel-center"
chmod 755 "$STAGE/DEBIAN"
printf '%s\n' "$VERSION" > "$STAGE/usr/share/puresteel-center/PACKAGE_VERSION"

cat > "$STAGE/DEBIAN/control" <<EOF
Package: puresteel-center
Version: $VERSION
Section: admin
Priority: optional
Architecture: all
Maintainer: Puresteel Project <repo@puresteel.local>
Depends: python3, python3-apt, python3-pyside6.qtcore, python3-pyside6.qtgui, python3-pyside6.qtwidgets, polkitd, pkexec, flatpak, pciutils, dkms, mesa-utils, vulkan-tools, vainfo
Recommends: switcheroo-control, power-profiles-daemon
Description: Puresteel system management center
 Puresteel Center manages updates, applications, graphics drivers,
 profiles, software sources, backups and system reports from Plasma.
EOF

cat > "$STAGE/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -f /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi
exit 0
EOF
chmod 755 "$STAGE/DEBIAN/postinst"

DEB="$OUTDIR/puresteel-center_${VERSION}_all.deb"
dpkg-deb --root-owner-group --build "$STAGE" "$DEB" >&2

echo "$DEB"
