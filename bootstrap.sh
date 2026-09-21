#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/MOzcelik14/Puresteel-OS.git"
DEFAULT_REF="main"
WORKDIR="${PURESTEEL_WORKDIR:-$HOME/.cache/puresteel-builder}"
OUTPUT_DIR="${PURESTEEL_OUTPUT_DIR:-$PWD}"
REF="${PURESTEEL_REF:-$DEFAULT_REF}"
ISO_NAME="${PURESTEEL_ISO_NAME:-Puresteel-Plasma-amd64.iso}"

say() { printf '\n\033[1;34m[Puresteel]\033[0m %s\n' "$*"; }
fail() { printf '\n\033[1;31m[Puresteel]\033[0m %s\n' "$*" >&2; exit 1; }

command -v apt-get >/dev/null 2>&1 || fail "This builder currently supports Debian, Ubuntu and Linux Mint style APT hosts."
command -v sudo >/dev/null 2>&1 || fail "sudo is required."

say "Puresteel Plasma 6 ISO builder"
sudo -v

AVAILABLE_KB="$(df -Pk "$OUTPUT_DIR" | awk 'NR==2 {print $4}')"
if [ "${AVAILABLE_KB:-0}" -lt 31457280 ]; then
    fail "At least 30 GiB of free disk space is required in the output filesystem."
fi

say "Installing build dependencies"
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git curl wget ca-certificates gnupg po4a \
    dpkg-dev apt-utils debootstrap debian-archive-keyring \
    squashfs-tools xorriso isolinux syslinux syslinux-common \
    grub-pc-bin grub-efi-amd64-bin mtools dosfstools rsync make python3

needs_live_build=1
if command -v lb >/dev/null 2>&1; then
    LB_VERSION="$(lb --version 2>/dev/null | head -n1 | tr -cd '0-9')"
    if [ -n "$LB_VERSION" ] && [ "$LB_VERSION" -ge 20240000 ] 2>/dev/null; then
        needs_live_build=0
        say "Using live-build $(lb --version | head -n1)"
    fi
fi

if [ "$needs_live_build" -eq 1 ]; then
    say "Installing a current Debian Live Team live-build"
    sudo apt-get remove -y live-build >/dev/null 2>&1 || true
    LB_TMP="$(mktemp -d)"
    trap 'rm -rf "${LB_TMP:-}"' EXIT
    git clone --depth=1 https://salsa.debian.org/live-team/live-build.git "$LB_TMP/live-build"
    sudo make -C "$LB_TMP/live-build" install
    rm -rf "$LB_TMP"
    trap - EXIT
fi

say "Fetching Puresteel source ($REF)"
rm -rf "$WORKDIR"
mkdir -p "$(dirname "$WORKDIR")"
git clone --depth=1 --branch "$REF" "$REPO" "$WORKDIR"

say "Building ISO — this can take a while"
cd "$WORKDIR"
chmod +x build.sh scripts/*.sh 2>/dev/null || true
./build.sh

test -f live-image-amd64.hybrid.iso || fail "Build completed without producing live-image-amd64.hybrid.iso"

say "Writing build files to $OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
cp -f live-image-amd64.hybrid.iso "$OUTPUT_DIR/$ISO_NAME"
(
    cd "$OUTPUT_DIR"
    sha256sum "$ISO_NAME" > "$ISO_NAME.sha256"
)

printf '\n\033[1;32mPuresteel build completed.\033[0m\n\n'
printf 'ISO:     %s\n' "$OUTPUT_DIR/$ISO_NAME"
printf 'SHA256:  %s\n\n' "$OUTPUT_DIR/$ISO_NAME.sha256"
cat "$OUTPUT_DIR/$ISO_NAME.sha256"
printf '\nBuild log: %s/build.log\n' "$WORKDIR"
