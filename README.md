<p align="center">
  <img src="config/includes.chroot/usr/share/pixmaps/puresteel-installer.png" width="128" alt="Puresteel logo">
</p>

<h1 align="center">Puresteel</h1>

<p align="center">
  <a href="README.md">English</a> · <a href="README.tr.md">Türkçe</a> · <a href="https://mozcelik14.github.io/Puresteel-OS/">Website</a>
</p>

---

Puresteel is an independent Debian 13 (Trixie) based Linux distribution built around KDE Plasma. It combines a clean desktop, gaming and creator tooling, broad graphics support, a graphical installer, and Puresteel's own system-management and update infrastructure.

**Current stable release: Puresteel 1.0 "Burak".**

## Build the ISO with one command

On a Debian, Ubuntu or Linux Mint style host:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | bash
```

The bootstrap script installs the required host tools, fetches the stable Puresteel source, builds the hybrid ISO and writes the ISO plus its SHA256 checksum to the directory where the command was started.

For manual and development builds, see [docs/BUILD.md](docs/BUILD.md).

## At a glance

| | |
|---|---|
| **Base** | Debian 13 (Trixie) |
| **Architecture** | amd64 + i386 multiarch for compatibility |
| **Desktop** | KDE Plasma / SDDM / Wayland |
| **Installer** | Calamares |
| **Init** | systemd |
| **Graphics** | Intel, AMD and NVIDIA; hybrid-GPU support |
| **Applications** | APT + Flatpak / Flathub |
| **Shell** | Fish + Starship |
| **Updates** | Debian APT + signed Puresteel APT repository + Flatpak |

## Puresteel Center

Puresteel ships its own Qt 6 / PySide6 system management application. It brings everyday administration tasks into one interface:

| Module | Purpose |
|---|---|
| **Updates** | Check and install APT and Flatpak updates through Polkit-protected actions |
| **Applications** | Search, install and remove APT and Flatpak software |
| **Drivers** | Inspect Intel, AMD and NVIDIA GPUs, kernel drivers, firmware, DKMS, Vulkan and VA-API |
| **Sources** | Inspect APT sources and manage Flatpak remotes |
| **Backup** | Back up user data, settings and package lists |
| **System Reports** | Collect kernel, disk, memory, GPU, service and journal diagnostics |

Puresteel Center supports Turkish and English and is packaged independently so it can be updated without rebuilding the ISO.

[Puresteel Center documentation →](docs/PURESTEEL_CENTER.md)

## Package updates

Puresteel-owned packages are distributed through a signed APT repository hosted with GitHub Pages. The ISO bundles the current Puresteel packages locally; installed systems receive newer Puresteel packages through normal APT updates.

[Update and repository documentation →](docs/UPDATES.md)

## Graphics support

- **Intel** — integrated graphics and Arc-class discrete graphics through the Linux/Mesa stack
- **AMD** — integrated and discrete Radeon graphics through `amdgpu` / Mesa
- **NVIDIA** — Debian proprietary driver stack, DKMS, Vulkan and hybrid graphics integration
- **Hybrid systems** — Intel + NVIDIA, AMD + NVIDIA and other multi-GPU layouts supported by the underlying Linux stack

The 1.0 live image has been validated on an Intel + NVIDIA laptop with an RTX 3050, including successful `nvidia-smi` operation in the live environment.

[Hardware documentation →](docs/HARDWARE.md)

## Gaming and creative software

The default image includes Steam, Wine, Winetricks, i386 multiarch, Vulkan libraries, Heroic Games Launcher, ProtonUp-Qt, Kdenlive, Audacity, TubeConverter, ONLYOFFICE Desktop Editors, Zen Browser, VLC and Audacious. Flatpak applications are installed system-wide from Flathub.

## Power-user defaults

Puresteel includes Fish, Starship, Fastfetch, btop, htop, Git, curl, wget, Vim, Nano, fzf, ripgrep, fd-find, bat, tmux and archive utilities. ZRAM is enabled with zstd compression and Puresteel-specific memory tuning.

## Desktop and branding

Puresteel uses its own GRUB, Plymouth, SDDM, wallpaper, icon and Calamares branding while keeping the visual system deliberately minimal.

## Installation

Write the generated hybrid ISO to a USB drive, boot the Puresteel live environment in UEFI mode and launch the Calamares installer from the desktop.

[Installation guide →](docs/INSTALL.md)

## Documentation

- [Website](https://mozcelik14.github.io/Puresteel-OS/)
- [Installation](docs/INSTALL.md)
- [Building Puresteel](docs/BUILD.md)
- [Puresteel Center](docs/PURESTEEL_CENTER.md)
- [Updates and APT repository](docs/UPDATES.md)
- [Hardware and graphics](docs/HARDWARE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Changelog](CHANGELOG.md)
- [Release notes](RELEASE_NOTES.md)

## Release status

Puresteel 1.0 "Burak" is the first stable release line. Development continues on the repository after the 1.0 tag; the release tag remains the reproducible source reference for the stable build.

## Licensing

Puresteel combines software distributed under multiple upstream licenses. Debian packages, Flatpak applications and third-party components retain their own licenses. The image may include Debian non-free firmware and proprietary NVIDIA components where configured.
