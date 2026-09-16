# Installing Puresteel

> Development line: **Puresteel 1.0 "Burak"**  
> Base: Debian 13 (Trixie) · Desktop: KDE Plasma · Installer: Calamares

Puresteel is distributed as a hybrid live/install ISO. You can boot it from USB, test the live environment, and install it with Calamares.

## Recommended requirements

- x86-64 CPU
- 8 GB RAM or more
- 40 GB or more free storage
- UEFI-capable system
- Internet connection recommended

Lower-spec systems may still boot, but the recommended values leave enough headroom for KDE Plasma, Flatpak applications and gaming/creator workloads.

## Write the ISO to USB

Use a raw-image capable tool such as:

- GNOME Disks
- KDE ISO Image Writer
- Fedora Media Writer
- Balena Etcher
- Rufus in DD mode
- `dd` on Linux

Example:

```bash
sudo dd if=live-image-amd64.hybrid.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

Replace `/dev/sdX` with the **whole USB device**, not a partition such as `/dev/sdX1`.

> `dd` overwrites the selected device. Verify the target device before running the command.

## Boot the live system

1. Boot the USB in UEFI mode.
2. Start the Puresteel live environment.
3. Confirm that keyboard, networking, display and audio work.
4. If relevant, check your graphics hardware before installing.
5. Launch the Puresteel installer from the desktop/application menu.

## Install with Calamares

Calamares guides you through:

- language and locale
- keyboard layout
- time zone
- partitioning
- user creation
- bootloader installation

For a clean installation, automatic partitioning is the simplest option. Manual partitioning is available for users who need custom layouts or multi-boot setups.

Always back up important files before changing disk partitions.

## Graphics notes

Puresteel includes support for Intel, AMD and NVIDIA systems.

### Intel

Intel integrated graphics and newer Intel discrete graphics use the Linux kernel/Mesa graphics stack together with Intel firmware packages.

### AMD

AMD APUs and discrete Radeon GPUs use the Linux kernel/Mesa stack, primarily through the `amdgpu` driver on supported hardware.

### NVIDIA

Puresteel includes Debian's proprietary NVIDIA driver stack and related hybrid-graphics components.

After booting or installing on NVIDIA hardware, you can verify the driver with:

```bash
nvidia-smi
```

For detailed graphics diagnostics, open **Puresteel Center → Drivers**.

## After installation

Useful checks:

```bash
cat /etc/os-release
uname -r
zramctl
swapon --show
sysctl vm.swappiness
flatpak list
dpkg --print-foreign-architectures
```

Check the Puresteel APT repository:

```bash
cat /etc/apt/sources.list.d/puresteel.sources
sudo apt update
```

Puresteel-owned packages, including Puresteel Center, can then be updated through normal APT upgrades.

```bash
sudo apt full-upgrade
```

## Puresteel Center

Puresteel Center provides a graphical interface for:

- updates
- applications
- graphics/driver status
- software sources
- backups
- system reports

See [PURESTEEL_CENTER.md](PURESTEEL_CENTER.md).

## Troubleshooting

If the system does not behave as expected, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

For pre-release images, real-hardware testing is strongly recommended before relying on Puresteel for critical work.
