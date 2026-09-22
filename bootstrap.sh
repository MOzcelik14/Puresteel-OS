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
PREVIEW_MENU=0
CHECK_ONLY=0
DIRECT=0
TEXT_MENU=0
TTY_READY=0
CURRENT_STAGE="Initialization"
LOG=""
LB_TMP=""

usage() {
    cat <<'HELP'
Puresteel Plasma 6 ISO Builder

Usage: bash bootstrap.sh [--menu | --build | --check | --preview-menu | --preview] [--verbose]

  (no args)       Interactive menu with a controlling terminal.

  --menu         Open interactive builder menu.
  --text-menu    Use numbered menu instead of whiptail.
  --build        Build immediately (unattended or WSL).
  --check        Read-only tool/disk check.
  --preview-menu Preview the menu without sudo, downloads or writes.
  --preview      Preview five build stages without sudo, downloads or writes.
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
        --preview-menu) PREVIEW_MENU=1 ;;
        --check) CHECK_ONLY=1 ;;
        --menu) DIRECT=0 ;;
        --text-menu) TEXT_MENU=1 ;;
        --build) DIRECT=1 ;;
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

# Unlike stdin, /dev/tty works while the script itself arrives via curl | bash.
open_tty() {
    if { exec 3<>/dev/tty; } 2>/dev/null; then
        if [[ -t 3 ]]; then TTY_READY=1; return 0; fi
        exec 3>&-
    fi
    return 1
}

read_tty() {
    local reply=""
    printf '%s' "$1" >&3
    IFS= read -r -u 3 reply || return 1
    REPLY="$reply"
}

use_whiptail() {
    [[ "$TTY_READY" -eq 1 && "$TEXT_MENU" -eq 0 && "${TERM:-dumb}" != "dumb" ]] &&
        command -v whiptail >/dev/null 2>&1
}

menu_preview() {
    banner
    printf '\n%s  ┌──────────── PURESTEEL MENU ────────────┐%s\n' "$C_BLUE" "$C_RESET"
    printf '  │  1. Create Puresteel ISO              │\n'
    printf '  │  2. Build settings                    │\n'
    printf '  │  3. Check system suitability          │\n'
    printf '  │  4. View previous build log           │\n'
    printf '  │  5. About Puresteel                   │\n'
    printf '  │                                        │\n'
    printf '  │  0. Exit                              │\n'
    printf '%s  └────────────────────────────────────────┘%s\n' "$C_BLUE" "$C_RESET"
}

choose() {
    local title="$1" description="$2"
    shift 2
    if use_whiptail; then
        # Save captured stdout on FD 4, draw UI on the terminal, capture choice.
        whiptail --title "$title" --menu "$description" 20 76 10 "$@" \
            4>&1 1>&3 2>&4 4>&-
    else
        if [[ "$title" != "Puresteel ISO Builder" ]]; then
            printf '\n%s\n' "$title" >&3
            while [[ "$#" -gt 1 ]]; do
                printf '  %s) %s\n' "$1" "$2" >&3
                shift 2
            done
        fi
        read_tty '  Selection: ' || return 1
        printf '%s\n' "$REPLY"
    fi
}

ask_setting() {
    local title="$1" current="$2" answer=""
    if use_whiptail; then
        answer="$(whiptail --title "$title" --inputbox "Cancel to keep the current value." \
            12 76 "$current" 4>&1 1>&3 2>&4 4>&-)" || return 1
    else
        read_tty "  $title [$current]: " || return 1
        answer="$REPLY"
        [[ -n "$answer" ]] || return 1
    fi
    SETTING_REPLY="$answer"
}

pause_menu() { read_tty $'\n  Press Enter to return... ' || true; }

valid_ref() {
    [[ "$1" =~ ^[a-zA-Z0-9][a-zA-Z0-9._/-]*$ ]] &&
        [[ "$1" != *'..'* && "$1" != */ && "$1" != *.lock ]]
}

valid_iso_name() {
    [[ "$1" == *.iso && "$1" != */* && "$1" != -* ]]
}

settings_menu() {
    local choice proposed
    while :; do
        choice="$(choose "Build settings" "Choose an option; settings apply only to this run." \
            1 "Source branch/tag: $REF" \
            2 "Image filename: $ISO_NAME" \
            3 "Output directory: $OUTPUT_DIR" \
            4 "Verbose log: $([[ "$VERBOSE" -eq 1 ]] && printf ON || printf OFF)" \
            0 "Back")" || return 0
        case "$choice" in
            1)
                if ask_setting "Source branch/tag" "$REF"; then
                    proposed="$SETTING_REPLY"
                    if valid_ref "$proposed"; then REF="$proposed"
                    else printf 'Invalid branch or tag.\n'; pause_menu; fi
                fi ;;
            2)
                if ask_setting "ISO filename" "$ISO_NAME"; then
                    proposed="$SETTING_REPLY"
                    if valid_iso_name "$proposed"; then ISO_NAME="$proposed"
                    else printf 'ISO filename must end in .iso, with no slash or leading dash.\n'; pause_menu; fi
                fi ;;
            3)
                if ask_setting "Output directory" "$OUTPUT_DIR"; then
                    proposed="$SETTING_REPLY"
                    if [[ -n "$proposed" && "$proposed" != -* ]]; then OUTPUT_DIR="$proposed"
                    else printf 'Invalid output directory.\n'; pause_menu; fi
                fi ;;
            4) VERBOSE=$((1 - VERBOSE)) ;;
            0) return 0 ;;
            *) printf 'Invalid choice.\n'; pause_menu ;;
        esac
    done
}

preflight() {
    local missing=0 cmd location probe available
    printf '\n  PURESTEEL REQUIREMENTS (read-only)\n'
    for cmd in apt-get sudo git df realpath sha256sum; do
        if command -v "$cmd" >/dev/null 2>&1; then printf '  [✓] %s\n' "$cmd"
        else printf '  [!] Missing: %s\n' "$cmd"; missing=1; fi
    done
    for location in "$OUTPUT_DIR" "$(dirname -- "$WORKDIR")"; do
        probe="$location"
        while [[ ! -e "$probe" && "$probe" != "/" ]]; do probe="$(dirname -- "$probe")"; done
        if command -v df >/dev/null 2>&1; then
            available="$(df -Pk -- "$probe" | awk 'NR==2 {print $4}')"
            if [[ "$available" =~ ^[0-9]+$ && "$available" -ge 31457280 ]]; then
                printf '  [✓] 30 GiB free: %s\n' "$location"
            else printf '  [!] Need 30 GiB free: %s\n' "$location"; missing=1; fi
        fi
    done
    if command -v lb >/dev/null 2>&1; then
        printf '  [i] %s\n' "$(lb --version 2>/dev/null | head -n1 || true)"
    else printf '  [i] live-build will be installed during build.\n'; fi
    printf '  No sudo requested. No changes made.\n'
    return "$missing"
}

previous_log() {
    local path="$OUTPUT_DIR/puresteel-bootstrap.log"
    if [[ -f "$path" ]]; then
        printf '\n  Recent output from %s:\n' "$path"
        tail -n 55 -- "$path"
    else printf '\n  No previous log at %s\n' "$path"; fi
    pause_menu
}

menu_loop() {
    local choice
    while :; do
        if ! use_whiptail; then menu_preview; fi
        choice="$(choose "Puresteel ISO Builder" "Debian 13 / Plasma 6 / amd64" \
            1 "Create Puresteel ISO" 2 "Build settings" \
            3 "Check system suitability" 4 "View previous build log" \
            5 "About Puresteel" 0 "Exit")" ||
            { printf '\nMenu closed; no ISO built.\n'; exit 0; }
        case "$choice" in
            1)
                if use_whiptail; then
                    whiptail --title "Build confirmation" --yesno \
                        "Build $REF to $OUTPUT_DIR/$ISO_NAME? This uses sudo and downloads build dependencies." \
                        12 76 3<&3 1>&3 2>&3 || continue
                else
                    read_tty '  Build with sudo? [y/N]: ' || continue
                    case "$REPLY" in y|Y|yes|YES|e|E|evet|EVET) ;; *) continue ;; esac
                fi
                return 0 ;;
            2) settings_menu ;;
            3) preflight || true; pause_menu ;;
            4) previous_log ;;
            5)
                printf '\n  Puresteel · Debian 13 · minimal KDE Plasma 6\n'
                printf '  Builds an installer ISO; does not install Puresteel on this machine.\n'
                printf '  https://github.com/MOzcelik14/Puresteel-OS\n'
                pause_menu ;;
            0) printf '\nMenu closed; no ISO built.\n'; exit 0 ;;
            *) printf 'Invalid choice.\n'; pause_menu ;;
        esac
    done
}

if [[ "$PREVIEW_MENU" -eq 1 ]]; then
    menu_preview
    note "Preview only: no sudo, downloads, directories or ISO build."
    exit 0
fi

if [[ "$CHECK_ONLY" -eq 1 ]]; then
    preflight
    exit "$?"
fi

if [[ "$PREVIEW" -eq 0 && "$DIRECT" -eq 0 ]]; then
    if ! open_tty; then
        printf 'Interactive menu needs a terminal; use --build for unattended builds, or --preview-menu.\n' >&2
        exit 2
    fi
    menu_loop
fi

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
for cmd in realpath; do
    command -v "$cmd" >/dev/null 2>&1 || fail "Required command missing: $cmd."
done
OUTPUT_DIR="$(realpath -m -- "$OUTPUT_DIR")"
WORKDIR="$(realpath -m -- "$WORKDIR")"
HOME_REAL="$(realpath -m -- "$HOME")"
# Only work below the user's cache. Never recursively delete a caller-chosen
# location, including an old clone from a previous build or a symlink target.
case "$WORKDIR/" in
    "$HOME_REAL/.cache/"*) ;;
    *) fail "PURESTEEL_WORKDIR must be a directory under $HOME_REAL/.cache (got: $WORKDIR)." ;;
esac
case "$OUTPUT_DIR/" in
    "$WORKDIR/"*) fail "Output directory must not be inside the build cache." ;;
esac
# The cache may be inside a broad destination such as the user's home;
# only the reverse (publishing the ISO inside a disposable build cache) is unsafe.
valid_ref "$REF" || fail "Invalid PURESTEEL_REF; use a branch/tag without spaces, .. or leading dashes."
valid_iso_name "$ISO_NAME" ||
    fail "PURESTEEL_ISO_NAME must be a filename ending in .iso, without directories or a leading dash."
for cmd in apt-get sudo git df sha256sum mktemp; do
    command -v "$cmd" >/dev/null 2>&1 || fail "Required command missing: $cmd (APT-based hosts only)."
done
mkdir -p -- "$OUTPUT_DIR" "$WORKDIR"
LOG="$OUTPUT_DIR/puresteel-bootstrap.log"
: > "$LOG"
note "Log: $LOG"
sudo -v
for location in "$OUTPUT_DIR" "$WORKDIR"; do
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
# Fresh unique checkout: previous root-owned live-build files are never reused
# or recursively removed. Keeping the checkout makes failures inspectable.
BUILD_DIR="$(mktemp -d "$WORKDIR/run.XXXXXXXX")"
SOURCE_DIR="$BUILD_DIR/source"
run_logged git clone --depth=1 --branch "$REF" "$REPO" "$SOURCE_DIR"
step_ok 3 "Puresteel source"

step 4 "ISO build"
note "Working directory: $SOURCE_DIR"
note "This is a REAL build; progress is recorded in $LOG."
cd -- "$SOURCE_DIR"
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
printf '  Build log %s/build.log\n' "$SOURCE_DIR"
printf '  Build cache %s (old runs are retained; remove only after checking)\n' "$WORKDIR"
printf '%s  ───────────────────────────────────────────%s\n\n' "$C_GREEN" "$C_RESET"
