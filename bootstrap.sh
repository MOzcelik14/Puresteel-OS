#!/usr/bin/env bash
# Puresteel ISO builder: readable terminal UI, honest progress and full logs.
set -Eeuo pipefail

REPO="https://github.com/MOzcelik14/Puresteel-OS.git"
DEFAULT_REF="main"
WORKDIR="${PURESTEEL_WORKDIR:-$HOME/.cache/puresteel-builder}"
OUTPUT_DIR="${PURESTEEL_OUTPUT_DIR:-$PWD}"
REF="${PURESTEEL_REF:-$DEFAULT_REF}"
ISO_NAME="${PURESTEEL_ISO_NAME:-Puresteel-Plasma-amd64.iso}"
VERBOSE=0
PREVIEW=0
CURRENT_STAGE="Initialization"
LOG=""
LB_TMP=""

usage() {
    cat <<'HELP'
Puresteel Plasma 6 ISO Builder

Usage: bash bootstrap.sh [--preview] [--verbose] [--help]

  --preview   Show the terminal UI without sudo, downloads, writes or ISO build.
  --verbose   Show APT, live-build and Git output while saving the full log.
  --help      Show this help.

Environment:
  PURESTEEL_REF         Git branch or tag to build (default: main).
  PURESTEEL_WORKDIR     Clone/build directory (default: ~/.cache/puresteel-builder).
  PURESTEEL_OUTPUT_DIR  ISO, checksum and log destination (default: current directory).
  PURESTEEL_ISO_NAME    Output ISO filename (default: Puresteel-Plasma-amd64.iso).
  NO_COLOR              Disable ANSI colors.

This BUILDS a live ISO; it does not install Puresteel onto the host.
HELP
}

for arg in "$@"; do
    case "$arg" in
        --preview) PREVIEW=1 ;;
        --verbose) VERBOSE=1 ;;
        --help|-h) usage; exit 0 ;;
        *) printf 'Unknown option: %s\n' "$arg" >&2; usage >&2; exit 2 ;;
    esac
done

C_BLUE="" C_GREEN="" C_RED="" C_DIM="" C_BOLD="" C_RESET=""
if [[ -t 1 && -z "${NO_COLOR:-}" && "${TERM:-}" != "dumb" ]]; then
    C_BLUE=$'\033[1;36m'
    C_GREEN=$'\033[1;32m'
    C_RED=$'\033[1;31m'
    C_DIM=$'\033[2m'
    C_BOLD=$'\033[1m'
    C_RESET=$'\033[0m'
fi

banner() {
    printf '\n%s' "$C_BLUE"
    case "${LC_ALL:-${LC_CTYPE:-${LANG:-}}}" in
        *UTF-8*|*utf8*|*UTF8*)
            printf '%s\n' \
                '╭────────────────────────────────────────────╮' \
                '│                                            │' \
                '│          P U R E S T E E L                 │' \
                '│          ISO BUILD SYSTEM                  │' \
                '│                                            │' \
                '│  Debian 13  ·  Plasma 6  ·  amd64          │' \
                '╰────────────────────────────────────────────╯'
            ;;
        *)
            printf '%s\n' \
                '+--------------------------------------------+' \
                '|                                            |' \
                '|          P U R E S T E E L                 |' \
                '|          ISO BUILD SYSTEM                  |' \
                '|                                            |' \
                '|  Debian 13  /  Plasma 6  /  amd64         |' \
                '+--------------------------------------------+'
            ;;
    esac
    printf '%s' "$C_RESET"
    printf '  Source       %s\n' "$REF"
    printf '  Destination  %s\n' "$OUTPUT_DIR"
    printf '  Image        %s\n' "$ISO_NAME"
    printf '  Mode         %s\n' "$([[ "$PREVIEW" -eq 1 ]] && printf 'PREVIEW' || { [[ "$VERBOSE" -eq 1 ]] && printf 'verbose' || printf 'quiet + log'; })"
}

step() {
    CURRENT_STAGE="$2"
    printf '\n%s  [→] %02d/05  %s%s\n' "$C_BLUE" "$1" "$2" "$C_RESET"
}

step_ok() {
    printf '%s  [✓] %02d/05  %s%s\n' "$C_GREEN" "$1" "$2" "$C_RESET"
}

note() { printf '%s  [i] %s%s\n' "$C_DIM" "$*" "$C_RESET"; }

fail() {
    printf '\n%s  [!] %s%s\n' "$C_RED" "$*" "$C_RESET" >&2
    if [[ -n "$LOG" && -s "$LOG" ]]; then
        printf '  Recent build output (%s):\n' "$LOG" >&2
        tail -n 22 "$LOG" >&2 || true
    fi
    exit 1
}

on_error() {
    local code="$1" line="$2"
    trap - ERR
    printf '\n%s  [!] FAILED during %s (exit %s, line %s)%s\n' \
        "$C_RED" "$CURRENT_STAGE" "$code" "$line" "$C_RESET" >&2
    if [[ -n "$LOG" && -s "$LOG" ]]; then
        printf '  Last 22 log lines:\n' >&2
        tail -n 22 "$LOG" >&2 || true
        printf '  Full log: %s\n' "$LOG" >&2
    fi
    exit "$code"
}

cleanup() {
    if [[ -n "$LB_TMP" && -d "$LB_TMP" ]]; then
        rm -rf -- "$LB_TMP"
    fi
}

trap cleanup EXIT
trap 'on_error "$?" "$LINENO"' ERR
trap 'printf "\nInterrupted; no ISO was published.\n" >&2; exit 130' INT
trap 'printf "\nTerminated; no ISO was published.\n" >&2; exit 143' TERM

run_logged() {
    printf '\n>>> ' >> "$LOG"
    printf '%q ' "$@" >> "$LOG"
    printf '\n' >> "$LOG"
    if [[ "$VERBOSE" -eq 1 ]]; then
        "$@" 2>&1 | tee -a "$LOG"
    else
        "$@" >> "$LOG" 2>&1
    fi
}

banner
if [[ "$PREVIEW" -eq 1 ]]; then
    note "Preview only: no sudo, downloads, files or ISO build."
    for n in 1 2 3 4 5; do
        case "$n" in
            1) label="System checks" ;;
            2) label="Build dependencies" ;;
            3) label="Puresteel source" ;;
            4) label="ISO build" ;;
            5) label="Checksum & export" ;;
        esac
        printf '  [ ] %02d/05  %s\n' "$n" "$label"
    done
    printf '\n  Output ISO   %s/%s\n' "$OUTPUT_DIR" "$ISO_NAME"
    printf '  Preview complete. Nothing was installed or generated.\n'
    exit 0
fi

step 1 "System checks"
for cmd in apt-get sudo git df realpath sha256sum; do
    command -v "$cmd" >/dev/null 2>&1 || fail "Required command missing: $cmd (APT-based hosts only)."
done
OUTPUT_DIR="$(realpath -m -- "$OUTPUT_DIR")"
WORKDIR="$(realpath -m -- "$WORKDIR")"
HOME_REAL="$(realpath -m -- "$HOME")"
if [[ "$WORKDIR" == "/" || "$WORKDIR" == "$HOME_REAL" || "$WORKDIR" == "$OUTPUT_DIR" ]]; then
    fail "Unsafe PURESTEEL_WORKDIR: $WORKDIR"
fi
case "$OUTPUT_DIR/" in
    "$WORKDIR/"*) fail "Output directory must not be inside the disposable build directory." ;;
esac
[[ "$ISO_NAME" == *.iso && "$ISO_NAME" != */* && "$ISO_NAME" != "." && "$ISO_NAME" != ".." ]] ||
    fail "PURESTEEL_ISO_NAME must be a filename ending in .iso, without directories."
mkdir -p -- "$OUTPUT_DIR" "$(dirname -- "$WORKDIR")"
LOG="$OUTPUT_DIR/puresteel-bootstrap.log"
: > "$LOG"
note "Log: $LOG"
sudo -v
for location in "$OUTPUT_DIR" "$(dirname -- "$WORKDIR")"; do
    AVAILABLE_KB="$(df -Pk -- "$location" | awk 'NR==2 {print $4}')"
    [[ "${AVAILABLE_KB:-0}" =~ ^[0-9]+$ && "$AVAILABLE_KB" -ge 31457280 ]] ||
        fail "At least 30 GiB free space is required on the output and build filesystems ($location)."
done
step_ok 1 "System checks"

step 2 "Build dependencies"
note "Installing packages; full APT output goes to the log."
run_logged sudo apt-get update
run_logged sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git curl wget ca-certificates gnupg po4a \
    dpkg-dev apt-utils debootstrap debian-archive-keyring \
    squashfs-tools xorriso isolinux syslinux syslinux-common \
    grub-pc-bin grub-efi-amd64-bin mtools dosfstools rsync make python3
needs_live_build=1
if command -v lb >/dev/null 2>&1; then
    LB_VERSION="$(lb --version 2>/dev/null | head -n1 | tr -cd '0-9' || true)"
    if [[ -n "$LB_VERSION" && "$LB_VERSION" -ge 20240000 ]]; then
        needs_live_build=0
        note "Using live-build $(lb --version | head -n1)"
    fi
fi
if [[ "$needs_live_build" -eq 1 ]]; then
    note "Installing current Debian Live Team live-build."
    run_logged sudo apt-get remove -y live-build
    LB_TMP="$(mktemp -d)"
    run_logged git clone --depth=1 https://salsa.debian.org/live-team/live-build.git "$LB_TMP/live-build"
    run_logged sudo make -C "$LB_TMP/live-build" install
    rm -rf -- "$LB_TMP"
    LB_TMP=""
fi
step_ok 2 "Build dependencies"

step 3 "Puresteel source"
note "Cloning ref: $REF"
rm -rf -- "$WORKDIR"
run_logged git clone --depth=1 --branch "$REF" "$REPO" "$WORKDIR"
step_ok 3 "Puresteel source"

step 4 "ISO build"
note "Working directory: $WORKDIR"
note "This is a REAL build; progress is recorded in $LOG."
cd -- "$WORKDIR"
run_logged bash ./build.sh
[[ -s live-image-amd64.hybrid.iso ]] || fail "Build finished without a nonempty live-image-amd64.hybrid.iso."
step_ok 4 "ISO build"

step 5 "Checksum & export"
run_logged cp -f -- live-image-amd64.hybrid.iso "$OUTPUT_DIR/$ISO_NAME"
(
    cd -- "$OUTPUT_DIR"
    sha256sum -- "$ISO_NAME" > "$ISO_NAME.sha256"
)
step_ok 5 "Checksum & export"

printf '\n%s  ───────────────────────────────────────────%s\n' "$C_GREEN" "$C_RESET"
printf '%s  PURESTEEL ISO BUILD COMPLETE%s\n' "$C_BOLD$C_GREEN" "$C_RESET"
printf '  ISO       %s/%s\n' "$OUTPUT_DIR" "$ISO_NAME"
printf '  SHA256    %s/%s.sha256\n' "$OUTPUT_DIR" "$ISO_NAME"
printf '  Log       %s\n' "$LOG"
printf '  Build log %s/build.log\n' "$WORKDIR"
printf '%s  ───────────────────────────────────────────%s\n\n' "$C_GREEN" "$C_RESET"
