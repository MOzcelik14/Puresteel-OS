# Building Puresteel

Puresteel uses Debian `live-build` to generate an amd64 hybrid ISO.

## One-command build

On a Debian, Ubuntu or Linux Mint style APT host:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | bash
```

The bootstrap script:

1. verifies `sudo` and available disk space,
2. installs the required host build dependencies,
3. installs a current Debian Live Team `live-build` when the host version is missing or too old,
4. fetches the stable Puresteel source,
5. builds the ISO,
6. writes the ISO and SHA256 checksum to the directory where the command was started.

The expected output is:

```text
Puresteel-1.0-Burak-amd64.iso
Puresteel-1.0-Burak-amd64.iso.sha256
```

By default the bootstrap script prefers the `v1.0.0` tag when it exists. For development testing you can override the source ref:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | PURESTEEL_REF=main bash
```

## Manual build

Install the common dependencies:

```bash
sudo apt update
sudo apt install -y \
  git curl wget ca-certificates gnupg po4a \
  dpkg-dev apt-utils debootstrap debian-archive-keyring \
  squashfs-tools xorriso isolinux syslinux syslinux-common \
  grub-pc-bin grub-efi-amd64-bin mtools dosfstools rsync \
  make python3 qemu-system-x86 ovmf
```

Puresteel expects a modern `live-build`. If your distribution ships a legacy release, install the current Debian Live Team version from Salsa:

```bash
sudo apt remove -y live-build || true
rm -rf /tmp/live-build
git clone https://salsa.debian.org/live-team/live-build.git /tmp/live-build
sudo make -C /tmp/live-build install
```

Verify:

```bash
which lb
lb --version
```

Clone Puresteel:

```bash
git clone https://github.com/MOzcelik14/Puresteel-OS.git
cd Puresteel-OS
```

Build:

```bash
./build.sh
```

The build script cleans the previous live-build state, regenerates the configuration, restores Puresteel GRUB branding, rebuilds the current Puresteel Center `.deb`, bundles it into `config/packages.chroot/`, and builds the hybrid ISO while writing output to `build.log`.

The live boot parameters include:

```text
boot=live components quiet splash username=puresteel hostname=puresteel
```

## Puresteel packages during ISO builds

Puresteel-owned packages are bundled into the image through `config/packages.chroot/`. This makes ISO generation independent of the online Puresteel APT repository.

Installed systems still receive newer Puresteel-owned packages through the signed Puresteel repository.

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

Virtual machines are useful for boot, desktop, Calamares and basic application testing. Real hardware remains important for GPU, Wi-Fi, suspend/resume, audio and gaming validation.

The 1.0 live image has been validated on an Intel + NVIDIA hybrid laptop with an RTX 3050, including successful NVIDIA driver operation in the live environment.

## Signing key

The Puresteel APT repository is signed with a private GPG key. The private key is intentionally not stored in Git.

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
bash -n bootstrap.sh
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
