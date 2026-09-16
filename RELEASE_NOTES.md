# Puresteel 1.0 "Burak"

Puresteel 1.0 "Burak" is the first stable release of Puresteel, an independent Debian 13 (Trixie) based Linux distribution centered on KDE Plasma, broad graphics support, gaming and creator workloads, and its own system-management/update tooling.

## Highlights

- Debian 13 (Trixie) amd64 base
- KDE Plasma desktop on Wayland
- SDDM display manager
- Calamares installer
- custom GRUB, Plymouth, SDDM, wallpaper and icon branding
- Intel, AMD and NVIDIA graphics support
- hybrid graphics integration with `switcheroo-control`
- NVIDIA proprietary driver stack with DKMS and Vulkan support
- Puresteel Center system-management application
- signed Puresteel APT repository
- Steam, Wine, Winetricks and i386 multiarch
- Flatpak + Flathub
- Zen Browser
- Kdenlive
- Audacity
- TubeConverter
- ONLYOFFICE Desktop Editors
- Heroic Games Launcher
- ProtonUp-Qt
- Fish + Starship + Fastfetch
- ZRAM with zstd compression

## Puresteel Center

Puresteel Center provides modules for:

- Updates
- Applications
- Drivers
- Software Sources
- Backup
- System Reports
- About / system information

The interface supports Turkish and English. Privileged package and driver operations use a Polkit-protected helper instead of running the full GUI as root.

## Package updates

Puresteel-owned packages are distributed through a signed APT repository hosted through GitHub Pages.

The ISO includes the current `puresteel-center` package locally during build. Installed systems use the online repository for later package upgrades, so Puresteel Center and other Puresteel-owned packages can be updated independently from the ISO.

## Graphics and real-hardware validation

Puresteel includes support for Intel, AMD and NVIDIA graphics stacks. The 1.0 live image has been validated on an Intel + NVIDIA hybrid laptop with an RTX 3050. The proprietary NVIDIA driver loaded successfully in the live environment and `nvidia-smi` reported the GPU correctly.

As with any Linux distribution, behavior still varies by firmware, laptop design, GPU generation and peripheral hardware.

## Building the release

The stable source can be built locally with:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | bash
```

The builder prefers the `v1.0.0` source tag when available and produces:

```text
Puresteel-1.0-Burak-amd64.iso
Puresteel-1.0-Burak-amd64.iso.sha256
```

## Notes

The historical RC1 image used GNOME and predates the KDE migration, Puresteel Center, AMD support and the signed Puresteel package repository. It should not be used as a description of the final 1.0 system.

Puresteel is an independent project based on Debian and is not an official Debian project.
