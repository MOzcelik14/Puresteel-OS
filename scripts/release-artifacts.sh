#!/usr/bin/env bash
set -euo pipefail
ISO="${1:-}"
if [[ -z "$ISO" || ! -f "$ISO" ]]; then
    echo "Usage: $0 path/to/image.iso" >&2
    exit 2
fi
for tool in xorriso unsquashfs python3 sha256sum; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "Missing required release tool: $tool" >&2
        exit 1
    fi
done

OUT="${ISO%.*}"
TEMP="$(mktemp -d)"
trap 'rm -rf "$TEMP"' EXIT
# Package manifest MUST be extracted from the release image, not the build host.
if xorriso -osirrox on -indev "$ISO" -extract /live/filesystem.packages "$TEMP/packages" >/dev/null 2>&1; then
    LC_ALL=C sort -u "$TEMP/packages" > "$OUT-packages.txt"
else
    if ! xorriso -osirrox on -indev "$ISO" -extract /live/filesystem.squashfs "$TEMP/filesystem.squashfs" >/dev/null 2>&1; then
        echo "Cannot extract live filesystem from ISO; no manifest generated." >&2
        exit 1
    fi
    if ! unsquashfs -cat "$TEMP/filesystem.squashfs" var/lib/dpkg/status > "$TEMP/dpkg-status"; then
        echo "Cannot extract installed dpkg status from ISO." >&2
        exit 1
    fi
    python3 - "$TEMP/dpkg-status" "$OUT-packages.txt" <<'PY'
import sys
from pathlib import Path
rows = []
for record in Path(sys.argv[1]).read_text(errors="replace").split("\n\n"):
    fields = {}
    for line in record.splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, value = line.split(":", 1)
            fields[key] = value.strip()
    if fields.get("Status") == "install ok installed" and fields.get("Package") and fields.get("Version"):
        rows.append(fields["Package"] + "\t" + fields["Version"])
if not rows:
    raise SystemExit("No installed packages found in release image")
Path(sys.argv[2]).write_text("\n".join(sorted(set(rows))) + "\n")
PY
fi
test -s "$OUT-packages.txt"
sha256sum "$ISO" > "$ISO.sha256"
python3 - "$ISO" > "$OUT-provenance.json" <<'PY'
import datetime
import json
import os
import platform
import subprocess
import sys

iso = sys.argv[1]
def cap(args):
    try:
        return subprocess.run(args, text=True, capture_output=True, check=False).stdout.strip()
    except OSError:
        return ""

print(json.dumps({
    "schema": 1,
    "artifact": os.path.basename(iso),
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "git_commit": cap(["git", "rev-parse", "HEAD"]),
    "builder_kernel": platform.release(),
    "builder_arch": platform.machine(),
    "manifest": os.path.basename(iso) + " installed packages from ISO",
}, indent=2))
PY
if command -v gpg >/dev/null 2>&1 && [[ -n "${PURESTEEL_SIGNING_KEY:-}" ]]; then
    gpg --batch --yes --local-user "$PURESTEEL_SIGNING_KEY" --armor --detach-sign "$ISO.sha256"
    echo "Signed checksum with configured key."
else
    echo "Checksum and image package manifest created (unsigned)."
fi
