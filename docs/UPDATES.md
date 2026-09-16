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
./scripts/release-center.sh 1.0.2-1
```

The release script performs the important packaging steps:

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
git commit -m "Release Puresteel Center 1.0.2"
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

## Signing key

The public key belongs in the repository and installed system.

The **private GPG signing key must never be committed to Git**. Keep an encrypted/offline backup. A developer setting up a new build machine must import the existing private key before publishing new repository metadata.

```bash
gpg --import Puresteel-APT-PRIVATE-KEY.asc
gpg --list-secret-keys
```

Losing the private key does not destroy the source code, but it prevents future packages from being signed as the same trusted Puresteel archive identity.

## Security model

APT verifies repository metadata against the Puresteel public key referenced by `Signed-By`. Users should not disable TLS or APT signature verification to work around repository errors.

If the package repository is unavailable, existing Debian packages remain usable; only Puresteel-owned package updates are affected until the repository returns.
