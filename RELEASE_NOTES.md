# Puresteel 1.0 "Burak" — development notes

Puresteel 1.0 "Burak" is the current development line of Puresteel, a Debian 13 (Trixie) based Linux distribution focused on a clean KDE Plasma desktop, broad graphics support, gaming/creator workloads and its own system-management/update tooling.

The project has moved beyond the original GNOME-based RC1 design. Current development images use KDE Plasma, Puresteel Center, Intel/AMD/NVIDIA support and a signed Puresteel package repository.

## Current highlights

- Debian 13 (Trixie) amd64 base
- KDE Plasma desktop
- SDDM with Puresteel branding
- Breeze Dark defaults
- Calamares installer
- custom GRUB / Plymouth / wallpaper / icon branding
- Intel, AMD and NVIDIA graphics support
- hybrid graphics integration with `switcheroo-control`
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

Puresteel Center currently provides modules for:

- Updates
- Applications
- Drivers
- Software Sources
- Backup
- System Reports
- About / system information

The interface supports Turkish and English. Privileged package/driver actions use a Polkit-protected helper instead of running the full GUI as root.

## Package updates

Puresteel-owned packages are distributed through a signed APT repository hosted through GitHub Pages.

The ISO includes the current `puresteel-center` package locally during build. Installed systems use the online repository for later package upgrades, so Puresteel Center can be updated without downloading a new ISO.

## Testing priorities before final 1.0

Real-hardware testing should continue across:

- Intel-only graphics systems
- AMD-only graphics systems
- NVIDIA-only systems
- Intel + NVIDIA hybrid laptops
- AMD + NVIDIA hybrid laptops
- Wi-Fi chipsets from multiple vendors
- audio devices
- suspend/resume
- multi-monitor setups
- Calamares installation on real UEFI hardware
- Steam/Proton workloads on Intel, AMD and NVIDIA GPUs
- Puresteel Center privileged actions
- APT repository upgrades on installed systems
- backup/restore workflows

## Release status

The repository should be treated as **pre-release development** until a final Puresteel 1.0 image is explicitly published.

The old RC1 ISO, checksum and GNOME-specific notes are historical and do not describe the current development image.
