# Puresteel updates and package repository

Puresteel uses two update sources:

1. Debian repositories for the base operating system.
2. The signed Puresteel APT repository for Puresteel-owned packages.

Flatpak applications are updated separately through Flatpak/Flathub.

## Repository URL

Installed systems are configured to use:

```text
https://mozcelik14.github.io/Puresteel-OS/apt
```

The source definition is installed as:

```text
/etc/apt/sources.list.d/puresteel.sources
```

and references the Puresteel archive key at:

```text
/usr/share/keyrings/puresteel-archive-keyring.asc
```

## Why the ISO does not fetch Puresteel packages from GitHub Pages during build

Puresteel-owned packages are also copied to:

```text
config/packages.chroot/
```

This allows `live-build` to install them locally into the image. The ISO build therefore does not depend on GitHub Pages, TLS availability or network access to the Puresteel package host.

After installation, newer Puresteel package versions are fetched from the signed online repository through APT.

## Repository layout

The repository is published under `docs/apt/` so GitHub Pages can serve it directly:

```text
docs/apt/
├── dists/
│   └── stable/
│       ├── InRelease
│       ├── Release
│       ├── Release.gpg
│       └── main/
│           └── binary-amd64/
│               ├── Packages
│               └── Packages.gz
├── pool/
│   └── main/
│       └── p/
│           └── puresteel-center/
└── puresteel-archive-keyring.asc
```

`InRelease` and `Release.gpg` are generated with the Puresteel archive signing key.

## Publishing Puresteel Center

The package source is stored in:

```text
packages/puresteel-center/
```

Build without publishing:

```bash
./scripts/build-center-package.sh
```

Release a new package version:

```bash
./scripts/release-center.sh 1.4.0-1
```

The source package version is currently `1.4.0-1`, but the committed signed APT index still lists `puresteel-center` version `1.0.1-1`. Merging source code does not update installed systems. Publishing a new version requires the matching signing **private key**, regenerated component packages, signed indexes and a separate commit; do not publish unsigned or mismatched metadata. The release script performs the important packaging steps:

1. updates `packages/puresteel-center/VERSION`,
2. builds the `.deb`,
3. copies the current package into `config/packages.chroot/`,
4. copies the package into the APT pool,
5. regenerates `Packages` / `Packages.gz`,
6. regenerates the repository `Release` metadata,
7. signs the repository,
8. exports the public archive key,
9. updates the installed-system APT source/key material.

Then commit and push the changed repository files:

```bash
git add -A
git commit -m "Release Puresteel components 1.4.0"
git push
```

GitHub Pages publishes the updated repository after the push.

## Updating an installed Puresteel system

```bash
sudo apt update
sudo apt full-upgrade
flatpak update
```

When a newer `puresteel-center` package is available, APT will treat it like a normal package upgrade.

## Verify the online repository

Check the signed metadata:

```bash
curl -I https://mozcelik14.github.io/Puresteel-OS/apt/dists/stable/InRelease
```

Check the package index:

```bash
curl -I https://mozcelik14.github.io/Puresteel-OS/apt/dists/stable/main/binary-amd64/Packages.gz
```

Inspect the Center entry:

```bash
curl -fsSL \
  https://mozcelik14.github.io/Puresteel-OS/apt/dists/stable/main/binary-amd64/Packages.gz \
  | gzip -dc \
  | sed -n '/^Package: puresteel-center$/,/^$/p'
```

## Check a signed release before publishing

The public archive can be verified **without the private signing key**:

```bash
python3 scripts/verify-apt-repository.py
```

The command checks both OpenPGP signatures, signed Release/index SHA256 hashes, the gzip index, all referenced Debian package hashes/sizes and package control metadata. GitHub CI runs the same read-only check. To verify a newly prepared release matches the source version, use:

```bash
python3 scripts/verify-apt-repository.py --require-current
```

**Current release blocker:** the signed online index still advertises Puresteel Center `1.0.1-1`, while source is `1.4.0-1`. The original private key that matches `docs/apt/puresteel-archive-keyring.asc` is required to advance the signed archive. Do not commit a private key or replace the key with an unrelated one. Once the original key is available on a trusted maintainer machine, run `./scripts/release-center.sh 1.4.0-1`, inspect the changes, and publish only after release tests. Changing `main` alone cannot publish a valid signed APT release.

## Protect the main branch

Repository administrators must enable a GitHub branch protection rule or ruleset for `main`: require a pull request, require the `validate` and `windows-powershell-syntax` status checks, block force-pushes and branch deletion, and avoid bypassing the checks. Leave the optional nightly `iso-smoke` job **out** of required checks because ordinary pull requests deliberately skip it. This is a GitHub Settings permission, not a repository file; connected CI credentials do not have administration permission to set it.

## Signing key

The public key belongs in the repository and installed system.

The **private GPG signing key must never be committed to Git**. Keep an encrypted/offline backup. A developer setting up a new build machine must import the existing private key before publishing new repository metadata. The release script now verifies the private-key fingerprint against the already-published public key **before changing the version**; it refuses a new unrelated key so existing installations are not silently stranded.

```bash
gpg --import Puresteel-APT-PRIVATE-KEY.asc
gpg --list-secret-keys
```

Losing the private key does not destroy the source code, but it prevents future packages from being signed as the same trusted Puresteel archive identity.

## Security model

APT verifies repository metadata against the Puresteel public key referenced by `Signed-By`. Users should not disable TLS or APT signature verification to work around repository errors.

If the package repository is unavailable, existing Debian packages remain usable; only Puresteel-owned package updates are affected until the repository returns.
