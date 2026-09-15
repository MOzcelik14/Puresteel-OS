# Puresteel OS

**Puresteel OS 1.0 "Burak"** is a Debian 13 (Trixie) based GNU/Linux distribution built for power users, developers, creators and gamers.

Puresteel keeps Debian as its technical base while providing a preconfigured GNOME desktop, gaming stack, creator applications, hybrid-GPU support and a Calamares-based graphical installer.

## Release

Current release: **Puresteel OS 1.0 "Burak" RC1**

Base: Debian 13 (Trixie)  
Architecture: amd64  
Desktop: GNOME  
Init: systemd  
Installer: Calamares

## Highlights

- Debian 13 (Trixie) base
- GNOME desktop
- systemd + live-config-systemd
- Calamares graphical installer
- Puresteel branding and custom boot artwork
- ZRAM using zstd, 50% RAM capacity, priority 100
- `vm.swappiness=4`
- NVIDIA proprietary driver stack
- Intel + NVIDIA hybrid graphics support with switcheroo-control
- Steam, Wine, Winetricks and i386 multiarch support
- 32-bit and 64-bit Vulkan libraries for gaming
- Flatpak + Flathub integration
- Zen Browser
- Kdenlive
- Audacity
- TubeConverter
- ONLYOFFICE Desktop Editors
- ProtonUp-Qt
- Heroic Games Launcher
- Fish shell as the default user shell
- Starship prompt
- Fastfetch
- JetBrainsMono Nerd Font

## Browser policy

Puresteel ships Zen Browser from Flathub as its primary browser. Firefox ESR, Chromium and GNOME Web are intentionally excluded from the default image.

## Building

The project uses Debian `live-build`.

```bash
./build.sh
```

The build script regenerates the live-build configuration, restores Puresteel boot branding and builds the hybrid ISO.

## Installation

Boot the ISO in UEFI mode and launch **Install Puresteel OS** from the live desktop.

See [docs/INSTALL.md](docs/INSTALL.md) for more details.

## Verification

For RC1, verify the ISO with:

```bash
sha256sum -c Puresteel-OS-1.0-Burak-RC1-amd64.iso.sha256
```

Expected SHA256:

```text
a95da3206e60384651058eb35811e6a02b258d7f53c2d87dc2cfeaf6f42faadb
```

## Status

Puresteel OS 1.0 "Burak" RC1 is a release candidate. Core live boot, GNOME and Calamares installation have been tested. Additional real-hardware testing is recommended before declaring the image final, especially for NVIDIA hybrid graphics, suspend/resume, audio and Wi-Fi across different machines.

## License

Puresteel OS contains software distributed under many free and open-source licenses, plus optional/non-free Debian components such as proprietary NVIDIA drivers and firmware. Individual packages retain their upstream licenses.
