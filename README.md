<p align="center">
  <img src="config/includes.chroot/usr/share/pixmaps/puresteel-installer.png" width="128" alt="Puresteel logo">
</p>

<h1 align="center">Puresteel</h1>

<p align="center">
  Debian 13 · KDE Plasma · amd64 · Intel / AMD / NVIDIA · Flatpak · Steam / Wine
</p>

<p align="center">
  <a href="README.md">English</a> · <a href="README.tr.md">Türkçe</a> · <a href="https://mozcelik14.github.io/Puresteel-OS/">Documentation</a>
</p>

---

Puresteel is an independent Debian 13 (Trixie) based Linux distribution built around KDE Plasma. It combines a clean desktop, gaming and creator tooling, broad graphics support, a graphical installer, and Puresteel's own system management and update infrastructure.

The current development target is **Puresteel 1.0 "Burak"**.

## At a glance

| | |
|---|---|
| **Base** | Debian 13 (Trixie) |
| **Architecture** | amd64 + i386 multiarch for compatibility |
| **Desktop** | KDE Plasma / SDDM / Breeze Dark |
| **Installer** | Calamares |
| **Init** | systemd |
| **Graphics** | Intel, AMD and NVIDIA; hybrid-GPU support |
| **Applications** | APT + Flatpak / Flathub |
| **Shell** | Fish + Starship |
| **Updates** | Debian APT + signed Puresteel APT repository + Flatpak |

## What makes Puresteel different

### Puresteel Center

Puresteel ships its own Qt 6 / PySide6 system management application. It brings the everyday administration tasks of the distribution into one interface:

| Module | Purpose |
|---|---|
| **Updates** | Check APT and Flatpak updates; install system updates through Polkit |
| **Applications** | Search, install and remove APT and Flatpak software |
| **Drivers** | Inspect Intel, AMD and NVIDIA GPUs, kernel drivers, firmware, DKMS, Vulkan and VA-API |
| **Sources** | Inspect APT sources and manage Flatpak remotes |
| **Backup** | Back up user data, settings and package lists |
| **System Reports** | Collect kernel, disk, memory, GPU, service and journal diagnostics |

Puresteel Center supports **Turkish and English** and is packaged as a normal Debian package so it can be updated independently from the ISO.

[Read the Puresteel Center documentation →](docs/PURESTEEL_CENTER.md)

### Signed Puresteel package repository

Puresteel-owned packages are published through a signed APT repository hosted with GitHub Pages. The ISO installs its bundled Puresteel packages locally; installed systems then receive newer Puresteel packages through normal APT updates.

```text
Puresteel source
      │
      ├── build .deb
      │
      ├── signed Puresteel APT repository
      │          │
      │          └── apt update / apt full-upgrade
      │
      └── ISO build → bundled current .deb
```

[Read the update and package repository documentation →](docs/UPDATES.md)

### Graphics support

Puresteel is not tied to a single GPU vendor.

- **Intel** — integrated graphics and Arc-class discrete graphics through the kernel/Mesa stack
- **AMD** — integrated Radeon graphics and discrete Radeon GPUs through `amdgpu` / Mesa
- **NVIDIA** — proprietary Debian driver stack, DKMS, Vulkan and hybrid graphics integration
- **Hybrid systems** — Intel + NVIDIA, AMD + NVIDIA, and multi-GPU layouts supported by the underlying Linux graphics stack

[Read the hardware documentation →](docs/HARDWARE.md)

### Gaming and creative software

The default image includes the foundations for Linux gaming and media work:

- Steam
- Wine / Wine64 / Wine32
- Winetricks
- i386 multiarch and 32-bit Vulkan libraries
- Heroic Games Launcher
- ProtonUp-Qt
- Kdenlive
- Audacity
- TubeConverter
- ONLYOFFICE Desktop Editors
- Zen Browser
- VLC and Audacious

Flatpak applications are installed system-wide from Flathub.

### Power-user defaults

Puresteel includes Fish, Starship, Fastfetch, btop, htop, Git, curl, wget, Vim, Nano, fzf, ripgrep, fd-find, bat, tmux and archive utilities. ZRAM is enabled with zstd compression and the system ships with Puresteel-specific performance defaults.

## Desktop and branding

Puresteel uses a consistent dark visual identity across the boot and desktop experience:

- custom GRUB artwork
- Puresteel Plymouth boot splash
- Puresteel SDDM background
- Puresteel wallpaper
- Breeze Dark defaults
- Puresteel icon overrides
- Puresteel-branded Calamares installer

## Build from source

Puresteel uses Debian `live-build`.

```bash
git clone https://github.com/MOzcelik14/Puresteel-OS.git
cd Puresteel-OS
./build.sh
```

A modern `live-build` installation and the required host tools are needed before building.

[Full build guide →](docs/BUILD.md)

## Installation

Write the generated hybrid ISO to a USB drive, boot the Puresteel live environment in UEFI mode, and launch the Calamares installer from the desktop.

[Installation guide →](docs/INSTALL.md)

## Documentation

- [Installation](docs/INSTALL.md)
- [Building Puresteel](docs/BUILD.md)
- [Puresteel Center](docs/PURESTEEL_CENTER.md)
- [Updates and APT repository](docs/UPDATES.md)
- [Hardware and graphics](docs/HARDWARE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Changelog](CHANGELOG.md)
- [Development notes](RELEASE_NOTES.md)

## Project status

Puresteel is under active development. The repository tracks the current 1.0 "Burak" development line; test images should be treated as pre-release software until a final release is explicitly published.

Real-hardware testing is especially valuable for installation, suspend/resume, Wi-Fi, audio, multi-monitor setups, hybrid graphics and gaming workloads.

## Licensing

Puresteel combines software distributed under multiple upstream licenses. Debian packages, Flatpak applications and third-party components retain their own licenses. The image may include Debian non-free firmware and proprietary NVIDIA components where configured.
