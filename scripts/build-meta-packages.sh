#!/bin/bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$REPO/build/packages"
VERSION="$(tr -d '[:space:]' < "$REPO/packages/puresteel-center/VERSION")"
mkdir -p "$OUT"

build_meta() {
    local name="$1" depends="$2" desc="$3"
    local stage
    stage="$(mktemp -d)"
    mkdir -p "$stage/DEBIAN"
    cat > "$stage/DEBIAN/control" <<EOF
Package: $name
Version: $VERSION
Section: metapackages
Priority: optional
Architecture: all
Maintainer: Puresteel Project <repo@puresteel.local>
Depends: $depends
Description: $desc
 Puresteel component metapackage used to keep the distribution roles explicit.
EOF
    local deb="$OUT/${name}_${VERSION}_all.deb"
    dpkg-deb --root-owner-group --build "$stage" "$deb" >/dev/null
    rm -rf "$stage"
    echo "$deb"
}

build_meta puresteel-base "systemd-sysv, network-manager, flatpak, zram-tools, puresteel-platform (>= $VERSION)" "Puresteel base system"
build_meta puresteel-desktop "cinnamon-core, lightdm, slick-greeter, nemo, puresteel-branding (>= $VERSION), puresteel-default-settings (>= $VERSION), puresteel-recovery (>= $VERSION)" "Puresteel Cinnamon desktop"
build_meta puresteel-gaming "steam-installer, wine, winetricks, gamemode, mangohud" "Puresteel gaming stack"
build_meta puresteel-creator "ffmpeg, flatpak" "Puresteel creator stack"
build_meta puresteel-developer "build-essential, git, curl" "Puresteel developer stack"
