#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

if [ "$#" -gt 1 ]; then
    echo "Usage: $0 [version]" >&2
    exit 2
fi

if [ "$#" -eq 1 ]; then
    VERSION="$1"
    if ! printf '%s' "$VERSION" | grep -Eq '^[0-9][0-9A-Za-z.+:~-]*-[0-9A-Za-z.+~]+$'; then
        echo "Invalid Debian version: $VERSION (example: 1.0.2-1)" >&2
        exit 2
    fi
else
    VERSION="${PURESTEEL_PACKAGE_VERSION:-$(tr -d '[:space:]' < packages/puresteel-center/VERSION)}"
fi

APTROOT="docs/apt"
POOL_ROOT="$APTROOT/pool/main/p"
DIST="$APTROOT/dists/stable"
KEY_IDENTITY="${PURESTEEL_KEY_IDENTITY:-Puresteel Archive Signing Key <repo@puresteel.local>}"

FPR="$(gpg --with-colons --list-secret-keys "$KEY_IDENTITY" 2>/dev/null \
    | awk -F: '$1=="fpr"{print $10;exit}')"

if [ -z "$FPR" ]; then
    echo "Puresteel archive signing key not found; no repository files were changed." >&2
    echo "Import the ORIGINAL archive private key on this machine (do not create a replacement)." >&2
    exit 1
fi
# A new key under the same display name would strand existing installations.
PUBLIC_KEY="$APTROOT/puresteel-archive-keyring.asc"
if [ ! -s "$PUBLIC_KEY" ]; then
    echo "Original published archive public key is missing. Refusing release." >&2
    exit 1
fi
PUBLISHED_FPR="$(gpg --batch --with-colons --show-keys "$PUBLIC_KEY" 2>/dev/null |
    awk -F: '$1=="fpr"{print $10;exit}')"
if [ -z "$PUBLISHED_FPR" ] || [ "$FPR" != "$PUBLISHED_FPR" ]; then
    echo "Signing private key does not match the published Puresteel APT public key." >&2
    exit 1
fi
if [ "$#" -eq 1 ] && [[ -z "${PURESTEEL_PACKAGE_VERSION:-}" ]]; then
    printf '%s\n' "$VERSION" > packages/puresteel-center/VERSION
fi
# Every Center/metapackage/component must carry exactly the same Debian version.
export PURESTEEL_PACKAGE_VERSION="$VERSION"

DEB="$(scripts/build-center-package.sh)"
META_OUTPUT="$(scripts/build-meta-packages.sh)"
COMPONENT_OUTPUT="$(scripts/build-component-packages.sh)"
mapfile -t META_DEBS <<< "$META_OUTPUT"
mapfile -t COMPONENT_DEBS <<< "$COMPONENT_OUTPUT"
if [ "${#META_DEBS[@]}" -ne 5 ] || [ "${#COMPONENT_DEBS[@]}" -ne 4 ]; then
    echo "Incomplete Puresteel package build: refusing to sign repository." >&2
    exit 1
fi
mkdir -p config/packages.chroot "$DIST/main/binary-amd64"
find config/packages.chroot -maxdepth 1 -type f -name "puresteel-*.deb" -delete
ALL_DEBS=("$DEB" "${META_DEBS[@]}" "${COMPONENT_DEBS[@]}")
for built in "${ALL_DEBS[@]}"; do
    [ -s "$built" ] || { echo "Missing package: $built" >&2; exit 1; }
    name="$(dpkg-deb -f "$built" Package)"
    pool="$POOL_ROOT/$name"
    mkdir -p "$pool"
    # Preserve historical releases and install matching artifacts into the new ISO.
    cp -f "$built" "$pool/"
    cp -f "$built" config/packages.chroot/
done

# Keep the two newest rolling versions per package; preserve manual releases.
# This caps GitHub Pages and repository history growth in routine rolling builds.
if [[ -n "${PURESTEEL_ROLLING_RELEASE:-}" ]]; then
    for directory in "$POOL_ROOT"/*; do
        [[ -d "$directory" ]] || continue
        mapfile -t obsolete < <(find "$directory" -maxdepth 1 -type f -name '*+git*_all.deb' | sort -Vr | tail -n +3)
        if (( ${#obsolete[@]} )); then rm -f -- "${obsolete[@]}"; fi
    done
fi

pushd "$APTROOT" >/dev/null

apt-ftparchive packages pool/main > dists/stable/main/binary-amd64/Packages
gzip -9c dists/stable/main/binary-amd64/Packages \
  > dists/stable/main/binary-amd64/Packages.gz

apt-ftparchive \
  -o APT::FTPArchive::Release::Origin="Puresteel" \
  -o APT::FTPArchive::Release::Label="Puresteel" \
  -o APT::FTPArchive::Release::Suite="stable" \
  -o APT::FTPArchive::Release::Codename="stable" \
  -o APT::FTPArchive::Release::Architectures="amd64 all" \
  -o APT::FTPArchive::Release::Components="main" \
  -o APT::FTPArchive::Release::Description="Puresteel package repository" \
  release dists/stable > dists/stable/Release

# CI signs non-interactively using a passphrase file; local GPG release remains usable.
GPG_FLAGS=(--batch --yes --local-user "$FPR")
if [[ -n "${PURESTEEL_GPG_PASSPHRASE_FILE:-}" ]]; then
    [[ -s "$PURESTEEL_GPG_PASSPHRASE_FILE" ]] || { echo "Missing signing passphrase file" >&2; exit 1; }
    GPG_FLAGS+=(--pinentry-mode loopback --passphrase-file "$PURESTEEL_GPG_PASSPHRASE_FILE")
fi
rm -f dists/stable/InRelease dists/stable/Release.gpg
gpg "${GPG_FLAGS[@]}" \
  --clearsign -o dists/stable/InRelease dists/stable/Release
gpg "${GPG_FLAGS[@]}" \
  --armor --detach-sign -o dists/stable/Release.gpg dists/stable/Release

popd >/dev/null

gpg --armor --export-options export-minimal --export "$FPR" \
  > "$APTROOT/puresteel-archive-keyring.asc"

mkdir -p config/archives
cp "$APTROOT/puresteel-archive-keyring.asc" \
   config/archives/puresteel.key.chroot


mkdir -p \
  config/includes.chroot/usr/share/keyrings \
  config/includes.chroot/etc/apt/sources.list.d

cp "$APTROOT/puresteel-archive-keyring.asc" \
  config/includes.chroot/usr/share/keyrings/puresteel-archive-keyring.asc

PAGES_BASE="${PURESTEEL_PAGES_BASE:-https://mozcelik14.github.io/Puresteel-OS}"
cat > config/includes.chroot/etc/apt/sources.list.d/puresteel.sources <<EOF
Types: deb
URIs: ${PAGES_BASE}/apt
Suites: stable
Components: main
Architectures: amd64
Signed-By: /usr/share/keyrings/puresteel-archive-keyring.asc
EOF

echo
echo "Prepared ${#ALL_DEBS[@]} signed-repository Puresteel packages at version $VERSION"
echo "APT repo: ${PAGES_BASE}/apt"
if [[ -n "${PURESTEEL_ROLLING_RELEASE:-}" ]]; then
    python3 scripts/verify-apt-repository.py --require-version "$VERSION"
else
    python3 scripts/verify-apt-repository.py --require-current
fi
echo "Publish docs/apt to Pages only after reviewing and testing the packages."
