# Installing Puresteel OS 1.0 "Burak"

## Requirements

Recommended minimum:

- x86-64 CPU
- 8 GB RAM
- 40 GB free storage
- UEFI-capable system
- Internet connection recommended

## Create installation media

Write the ISO to a USB drive using a raw-image capable tool such as GNOME Disks, Fedora Media Writer, Balena Etcher, Rufus in DD mode, or `dd`.

Example on Linux:

```bash
sudo dd if=Puresteel-OS-1.0-Burak-RC1-amd64.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

Replace `/dev/sdX` with the whole USB device, not a partition.

## Boot

1. Boot the USB in UEFI mode.
2. Start the Puresteel live environment.
3. Verify networking, display and input devices.
4. Launch **Install Puresteel OS**.

## Calamares installation

The installer guides you through:

- language and locale
- keyboard layout
- partitioning
- user creation
- bootloader installation

For a clean installation, automatic partitioning is the simplest option. Advanced users may use manual partitioning.

## After installation

Recommended checks:

```bash
cat /etc/os-release
zramctl
swapon --show
sysctl vm.swappiness
flatpak list
wine --version
dpkg --print-foreign-architectures
```

On systems with NVIDIA hardware:

```bash
nvidia-smi
```

For hybrid-GPU offload:

```bash
puresteel-nvidia-run <application>
```

Example:

```bash
puresteel-nvidia-run glxinfo
```

## RC1 note

This is a release candidate. Back up important data before installing on production hardware.
