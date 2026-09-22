#!/usr/bin/env bash
# Produce a monotonically versioned Debian package series from the validated main commit.
set -euo pipefail
cd "$(dirname "$0")/.."
base="$(tr -d '[:space:]' < packages/puresteel-center/VERSION)"
upstream="${base%-*}"
if [[ ! "$upstream" =~ ^[0-9][0-9A-Za-z.+~]*$ ]]; then
    echo "Invalid source upstream version: $upstream" >&2
    exit 1
fi
stamp="$(TZ=UTC date -d "@$(git show -s --format=%ct HEAD)" +%Y%m%d%H%M%S)"
sha="$(git rev-parse --short=12 HEAD)"
version="${upstream}+git${stamp}.${sha}-1"
dpkg --validate-version "$version"
printf '%s\n' "$version"
