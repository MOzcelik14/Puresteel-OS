# Changelog

## Unreleased — Cinnamon development line

### Desktop migration

- replaced KDE Plasma with Cinnamon
- replaced SDDM with LightDM + Slick Greeter
- moved the development session from Wayland to Cinnamon on X11
- replaced Plasma Network Management with `network-manager-gnome`
- removed KDE Discover and its Flatpak backend; Puresteel Center remains the distribution-level application/update interface
- added Nemo, GNOME Terminal, Cinnamon translations, XApp desktop portal integration and recommended Cinnamon desktop support packages
- moved wallpaper, GTK theme, icon theme and terminal defaults to system-wide dconf defaults
- branded the Cinnamon application menu with the Puresteel `start-here-symbolic` icon
- added Puresteel branding to Slick Greeter
- removed KDE/SDDM-specific configuration and icon aliases

The released `v1.0.0` tag remains the KDE Plasma-based Puresteel 1.0 build. The Cinnamon line is development-only until a new stable release is published.

---

## Puresteel 1.0 "Burak" — stable

First stable release of Puresteel.

### Desktop and system

- Debian 13 (Trixie) amd64 base
- systemd-only init
- KDE Plasma desktop
- SDDM display manager
- Wayland session
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
- added package build and release scripts

### Graphics and hardware

- Intel graphics firmware and media acceleration support
- AMD graphics firmware and Mesa stack
- NVIDIA proprietary driver stack
- NVIDIA DKMS integration
- `switcheroo-control` hybrid graphics integration
- Intel and AMD CPU microcode
- Intel / AMD / NVIDIA detection in Puresteel Center
- 64-bit and 32-bit Vulkan libraries for gaming compatibility
- NVIDIA module alias handling fixed for the Debian `nvidia-current` module naming
- Nouveau disabled when using the proprietary NVIDIA stack
- live NVIDIA driver validated on an RTX 3050 hybrid laptop

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
- Puresteel live user identity and KDE branding

### Distribution and builds

- added `bootstrap.sh` for one-command local ISO generation
- bootstrap builder installs required host dependencies automatically
- stable builder prefers the `v1.0.0` release source
- GitHub Pages landing page updated for the stable release

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
