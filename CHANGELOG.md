# Changelog

## Puresteel 1.0 "Burak" — current development line

Puresteel 1.0 is under active development. The repository has moved significantly beyond the original RC1 layout.

### Desktop and system

- Debian 13 (Trixie) amd64 base
- systemd-only init
- KDE Plasma desktop
- SDDM display manager
- Breeze Dark defaults
- Calamares graphical installer
- hybrid live/install ISO with UEFI support

### Puresteel Center

- introduced Puresteel Center, built with Qt 6 / PySide6
- Turkish and English interface
- update management for APT and Flatpak
- APT + Flatpak application search/install/remove
- Intel / AMD / NVIDIA graphics diagnostics
- software-source viewer and Flatpak remote management
- backup tooling
- system report generation
- privileged system operations routed through a Polkit-protected helper
- packaged as `puresteel-center` Debian package

### Puresteel package repository

- added signed Puresteel APT repository
- package metadata published through GitHub Pages
- Puresteel Center packaged as a normal `.deb`
- ISO builds install Puresteel-owned packages locally from `config/packages.chroot/`
- installed systems use the online signed repository for future Puresteel package updates
- added package build/release scripts

### Graphics and hardware

- NVIDIA proprietary driver stack
- DKMS integration
- `switcheroo-control` hybrid graphics integration
- Intel graphics firmware and media acceleration packages
- AMD graphics firmware and Mesa stack
- Intel and AMD CPU microcode
- Intel / AMD / NVIDIA detection in Puresteel Center
- 64-bit and 32-bit Vulkan libraries for gaming compatibility

### Performance

- ZRAM enabled with zstd compression
- ZRAM capacity set to 50% of system RAM
- ZRAM swap priority 100
- `vm.swappiness=4`

### Gaming

- Steam installer and device rules
- Wine / Wine64 / Wine32
- Winetricks
- i386 multiarch
- 32-bit and 64-bit Vulkan libraries
- Heroic Games Launcher
- ProtonUp-Qt

### Applications

System and Flatpak defaults include:

- Zen Browser
- Kdenlive
- Audacity
- TubeConverter
- ONLYOFFICE Desktop Editors
- VLC
- Audacious
- KDE Discover with Flatpak backend

### Terminal and power-user environment

- Fish as default user shell
- Starship prompt
- Fastfetch
- JetBrainsMono Nerd Font
- btop / htop
- Git, curl, wget
- Vim / Nano
- fzf, ripgrep, fd-find, bat, tmux
- archive utilities

### Branding

- minimalist Puresteel visual identity
- custom GRUB artwork and theme
- Puresteel Plymouth splash
- custom SDDM background
- Puresteel wallpapers
- Puresteel application/system icons
- Puresteel-branded Calamares installer

### Browser policy

- Zen Browser is installed from Flathub
- Firefox ESR, Chromium and GNOME Web remain excluded from the default image

---

## Historical: Puresteel 1.0 "Burak" RC1

The first public release candidate used GNOME and an earlier Intel/NVIDIA-focused graphics setup. It predates the KDE migration, Puresteel Center, AMD support and the signed Puresteel APT repository.

Historical RC1 SHA256:

```text
a95da3206e60384651058eb35811e6a02b258d7f53c2d87dc2cfeaf6f42faadb
```
