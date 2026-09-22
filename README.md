<p align="center">
  <img src="config/includes.chroot/usr/share/pixmaps/puresteel-installer.png" width="128" alt="Puresteel logo">
</p>

<h1 align="center">Puresteel</h1>

<p align="center">
  <a href="README.md">English</a> · <a href="README.tr.md">Türkçe</a> · <a href="https://mozcelik14.github.io/Puresteel-OS/">Website</a>
</p>

---

Puresteel is an independent Debian 13 (Trixie) based Linux distribution focused on a clean desktop, gaming and creator tooling, broad graphics support, a graphical installer, and Puresteel's own system-management and update infrastructure.

The current Puresteel desktop stack is **KDE Plasma 6 + SDDM + Breeze Light, Wayland with X11 fallback**, shipped with a full gaming, creator and developer toolkit.

## Build the ISO with one command

### Linux

On a Debian, Ubuntu or Linux Mint style host:

```bash
curl -fsSL https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh | bash
```

### Windows 10 / 11

Run this in PowerShell:

```powershell
irm https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/windows-build.ps1 | iex
```

The Windows builder uses WSL2 and a Debian/Ubuntu environment automatically. If WSL is not installed yet, the first run starts the Windows WSL/Debian setup. Windows may ask for one restart or initial Linux-user setup; afterwards, run the same command again.

**Direct ISO download (temporary public R2 development URL):** [Puresteel-Latest.iso](https://pub-6bd67d084cc74faa8573569db4b21336.r2.dev/Puresteel-Latest.iso) · [SHA256](https://pub-6bd67d084cc74faa8573569db4b21336.r2.dev/Puresteel-Latest.iso.sha256). The `r2.dev` address is rate-limited; use a custom R2 domain before broad public distribution.

**Rolling ISO:** every merge to `main` triggers a full GitHub Actions ISO build once CI passes. [See the latest successful ISO artifact](https://github.com/MOzcelik14/Puresteel-OS/actions/workflows/validate.yml). Permanent public downloads require a Cloudflare R2 bucket configured by the repository owner. [Rolling build and R2 setup →](docs/ROLLING.md)

For manual and development builds, see [docs/BUILD.md](docs/BUILD.md).

## At a glance

| | |
|---|---|
| **Base** | Debian 13 (Trixie) |
| **Architecture** | amd64 + i386 multiarch |
| **Desktop** | Plasma 6 / SDDM / Wayland + X11 |
| **Installer** | Calamares |
| **Init** | systemd |
| **Graphics** | Intel, AMD and NVIDIA; hybrid-GPU support |
| **Applications** | APT + Flatpak / Flathub |
| **Shell** | Fish + Starship |
| **Updates** | Debian APT + signed Puresteel APT repository + Flatpak |

## Puresteel Center

Puresteel ships its own Qt 6 / PySide6 Center 2.0 system management application with modules for updates, applications, drivers, sources, backup and system reports. Turkish and English interfaces are supported.

[Puresteel Center documentation →](docs/PURESTEEL_CENTER.md)

## Graphics support

- **Intel** — integrated graphics and Arc-class discrete graphics through Linux/Mesa
- **AMD** — integrated and discrete Radeon graphics through `amdgpu` / Mesa
- **NVIDIA** — Debian proprietary driver stack, DKMS, Vulkan and hybrid graphics integration
- **Hybrid systems** — Intel + NVIDIA, AMD + NVIDIA and other multi-GPU layouts supported by the Linux graphics stack

An earlier Cinnamon image was tested on an Intel + NVIDIA RTX 3050 laptop. The full Plasma rolling edition still requires separate fresh-install and hardware verification.

[Hardware documentation →](docs/HARDWARE.md)

## Gaming and creative software

The rolling ISO includes Steam launcher and 32-bit dependencies, Wine (32/64-bit), Winetricks, Heroic as a system Flatpak, Kdenlive, Audacity, FFmpeg and developer tools. ProtonUp-Qt and ONLYOFFICE are also preinstalled as system Flatpaks. Steam may download upstream client updates on first launch; games and Proton versions are not bundled.

## Power-user defaults

Puresteel includes Fish, Starship, Fastfetch, btop, htop, Git, curl, wget, Vim, Nano, fzf, ripgrep, fd-find, bat, tmux and archive utilities. ZRAM is enabled with zstd compression and Puresteel-specific memory tuning.

## Desktop and branding

Puresteel uses KDE Plasma 6 with SDDM and a Puresteel Breeze Light default, branded wallpaper, icons, GRUB, Plymouth and Calamares. An X11 session is retained for GPU compatibility. System language switching is available through Puresteel Language Settings.

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

## Release history

The published `v1.0.0` tag is preserved as the original Puresteel 1.0 "Burak" release. The new Plasma migration is developed separately and does not rewrite that historical release.

## Licensing

Puresteel combines software distributed under multiple upstream licenses. Debian packages, Flatpak applications and third-party components retain their own licenses. The image may include Debian non-free firmware and proprietary NVIDIA components where configured.
