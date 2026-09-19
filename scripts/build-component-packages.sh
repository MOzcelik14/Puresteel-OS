#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

REPO="$(cd "$(dirname "$0")/.." && pwd)"
IN="$REPO/config/includes.chroot"
OUT="$REPO/build/packages"
VERSION="$(tr -d '[:space:]' < "$REPO/packages/puresteel-center/VERSION")"
mkdir -p "$OUT"

build_component() {
    local name="$1" deps="$2" description="$3" stage path relative
    stage="$(mktemp -d)"
    mkdir -p "$stage/DEBIAN"

    copy() {
        for path in "$@"; do
            [[ -e "$path" || -L "$path" ]] || continue
            relative="${path#"$IN"/}"
            mkdir -p "$stage/$(dirname "$relative")"
            cp -a "$path" "$stage/$relative"
        done
    }

    case "$name" in
        puresteel-platform)
            copy "$IN"/usr/local/bin/puresteel* \
                 "$IN"/usr/local/sbin/puresteel-profile \
                 "$IN"/usr/local/sbin/puresteel-oem-prepare \
                 "$IN"/usr/share/applications/puresteel-*.desktop \
                 "$IN"/usr/share/nemo/actions/puresteel-*.nemo_action \
                 "$IN"/usr/share/doc/puresteel/OEM.md \
                 "$IN"/usr/share/doc/puresteel/SECURE-BOOT.md \
                 "$IN"/usr/share/puresteel/channels.conf \
                 "$IN"/etc/xdg/autostart/puresteel-*.desktop \
                 "$IN"/etc/puresteel/channel
            ;;
        puresteel-recovery)
            copy "$IN"/usr/local/sbin/puresteel-recovery \
                 "$IN"/etc/grub.d/09_puresteel_recovery \
                 "$IN"/etc/systemd/system/puresteel-recovery.service \
                 "$IN"/usr/share/doc/puresteel/RECOVERY.md
            ;;
        puresteel-branding)
            copy "$IN"/usr/share/backgrounds/puresteel \
                 "$IN"/usr/share/themes/Puresteel-* \
                 "$IN"/usr/share/icons/Puresteel \
                 "$IN"/usr/share/sounds/Puresteel
            ;;
        puresteel-default-settings)
            copy "$IN"/etc/dconf/db/local.d/00-puresteel \
                 "$IN"/etc/fish/conf.d/puresteel.fish \
                 "$IN"/etc/xdg/fastfetch/config.jsonc \
                 "$IN"/etc/sysctl.d/99-puresteel-memory.conf \
                 "$IN"/etc/skel/.config/fastfetch \
                 "$IN"/etc/skel/.config/fish \
                 "$IN"/etc/skel/.config/starship.toml
            ;;
        *) echo "Unknown component: $name" >&2; rm -rf "$stage"; return 2 ;;
    esac

    cat > "$stage/DEBIAN/control" <<EOF
Package: $name
Version: $VERSION
Section: admin
Priority: optional
Architecture: all
Maintainer: Puresteel Project <repo@puresteel.local>
Depends: $deps
Description: $description
 Puresteel maintained distribution component, upgradable through APT.
EOF
    if [[ "$name" == "puresteel-default-settings" ]]; then
        cat > "$stage/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
if command -v dconf >/dev/null 2>&1; then dconf update; fi
exit 0
EOF
        chmod 755 "$stage/DEBIAN/postinst"
    fi
    local output="$OUT/${name}_${VERSION}_all.deb"
    dpkg-deb --root-owner-group --build "$stage" "$output" >&2
    rm -rf "$stage"
    echo "$output"
}

build_component puresteel-platform "python3, python3-gi, gir1.2-gtk-3.0, puresteel-center (>= $VERSION), polkitd, pkexec, pciutils" "Puresteel tools, welcome, doctor and system control"
build_component puresteel-recovery "puresteel-platform (>= $VERSION), timeshift, initramfs-tools, grub-common" "Puresteel recovery console and rollback"
build_component puresteel-branding "papirus-icon-theme" "Puresteel artwork, themes, icons and wallpapers"
build_component puresteel-default-settings "puresteel-branding (>= $VERSION), dconf-cli, fish" "Puresteel Cinnamon, terminal and memory defaults"
