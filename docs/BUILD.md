# Building Puresteel

Puresteel uses Debian `live-build` to generate an amd64 hybrid ISO.

## Host requirements

A Debian/Ubuntu/Mint-style host works well. Install the common build dependencies:

```bash
sudo apt update
sudo apt install -y \
  git curl wget ca-certificates gnupg \
  dpkg-dev apt-utils debootstrap debian-archive-keyring \
  squashfs-tools xorriso isolinux syslinux syslinux-common \
  grub-pc-bin grub-efi-amd64-bin mtools dosfstools rsync \
  qemu-system-x86 ovmf make
```

Puresteel development currently expects a modern `live-build`. If your distribution ships an old release, install the current Debian Live Team version from Salsa instead of relying on a legacy package.

```bash
sudo apt remove -y live-build || true
rm -rf /tmp/live-build
git clone https://salsa.debian.org/live-team/live-build.git /tmp/live-build
cd /tmp/live-build
sudo make install
```

Verify:

```bash
which lb
lb --version
```

## Clone the project

```bash
git clone https://github.com/MOzcelik14/Puresteel-OS.git
cd Puresteel-OS
```

## Build

```bash
./build.sh
```

The build script:

1. cleans the previous live-build chroot state,
2. regenerates the live-build configuration,
3. restores Puresteel GRUB branding,
4. builds the hybrid ISO,
5. writes the full output to `build.log`.

The current live boot parameters include:

```text
boot=live components quiet splash username=puresteel hostname=puresteel
```

## Puresteel packages during ISO builds

Puresteel-owned packages are bundled into the image through `config/packages.chroot/`.

This is deliberate: the ISO build does not depend on GitHub Pages being reachable. Installed systems still receive later Puresteel package updates from the signed Puresteel APT repository.

Example:

```text
config/packages.chroot/
└── puresteel-center_1.0.1-1_all.deb
```

## Puresteel Center package

Build the current Center package without publishing it:

```bash
./scripts/build-center-package.sh
```

Release a new Center version and update APT metadata:

```bash
./scripts/release-center.sh 1.0.2-1
```

See [UPDATES.md](UPDATES.md) before publishing package updates.

## Test the ISO in QEMU

Example UEFI/KVM test:

```bash
qemu-system-x86_64 \
  -enable-kvm \
  -m 8G \
  -smp 8 \
  -cpu host \
  -bios /usr/share/ovmf/OVMF.fd \
  -cdrom live-image-amd64.hybrid.iso \
  -boot d
```

Virtual machines are useful for boot, desktop, Calamares and basic application testing. Real hardware is still required for meaningful Intel/AMD/NVIDIA, Wi-Fi, suspend/resume, audio and gaming validation.

## Signing key

The Puresteel APT repository is signed with a private GPG key. The private key is intentionally **not** stored in Git.

After moving to a new development machine, import your backed-up private key:

```bash
gpg --import Puresteel-APT-PRIVATE-KEY.asc
gpg --list-secret-keys
```

Never commit the private signing key to the repository.

## Before pushing

Useful checks:

```bash
git status
bash -n build.sh
bash -n scripts/build-center-package.sh
bash -n scripts/release-center.sh
```

For Puresteel Center Python sources:

```bash
python3 -m compileall -q packages/puresteel-center/rootfs/usr/share/puresteel-center
```

## Related documentation

- [Installation](INSTALL.md)
- [Puresteel Center](PURESTEEL_CENTER.md)
- [Updates / package repository](UPDATES.md)
- [Hardware](HARDWARE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
