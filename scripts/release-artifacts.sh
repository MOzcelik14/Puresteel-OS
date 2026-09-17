#!/usr/bin/env bash
set -euo pipefail
ISO="${1:-}"
if [[ -z "$ISO" || ! -f "$ISO" ]]; then echo "Usage: $0 path/to/image.iso" >&2; exit 2; fi
OUT="${ISO%.*}"
sha256sum "$ISO" > "$ISO.sha256"
dpkg-query -W -f='${Package}\t${Version}\n' 2>/dev/null | sort > "$OUT-packages.txt" || true
python3 - "$ISO" > "$OUT-provenance.json" <<'PY'
import json,os,platform,subprocess,sys,datetime
iso=sys.argv[1]
def cap(c):
 try:return subprocess.run(c,text=True,capture_output=True,check=False).stdout.strip()
 except Exception:return ''
print(json.dumps({'schema':1,'artifact':os.path.basename(iso),'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'git_commit':cap(['git','rev-parse','HEAD']),'builder_kernel':platform.release(),'builder_arch':platform.machine()},indent=2))
PY
if command -v gpg >/dev/null 2>&1 && [[ -n "${PURESTEEL_SIGNING_KEY:-}" ]]; then
  gpg --batch --yes --local-user "$PURESTEEL_SIGNING_KEY" --armor --detach-sign "$ISO.sha256"
  echo "Signed checksum with configured key."
else
  echo "Checksum and provenance created. Set PURESTEEL_SIGNING_KEY to create a GPG signature."
fi
