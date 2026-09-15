# Changelog

## Puresteel OS 1.0 "Burak" RC1

Initial public release candidate.

### Base system

- Debian 13 (Trixie) amd64 base
- systemd as the only supported init system
- GNOME desktop
- Calamares graphical installer
- Hybrid ISO with UEFI boot support

### Performance

- ZRAM enabled with zstd compression
- ZRAM capacity set to 50% of system RAM
- ZRAM swap priority set to 100
- `vm.swappiness=4`
- No default swapfile in the live system

### Graphics and gaming

- NVIDIA proprietary driver stack included
- Intel/NVIDIA hybrid graphics support
- switcheroo-control integration
- Steam installer
- Wine + Wine32
- Winetricks
- i386 multiarch
- 32-bit and 64-bit Vulkan libraries

### Applications

- Zen Browser
- Kdenlive
- Audacity
- TubeConverter
- ONLYOFFICE Desktop Editors
- ProtonUp-Qt
- Heroic Games Launcher
- VLC
- Audacious

### Terminal and developer experience

- Fish as the default user shell
- Starship prompt
- Fastfetch
- JetBrainsMono Nerd Font
- btop, htop, git, curl, wget, vim, nano, fzf, ripgrep, fd-find, bat and tmux

### Branding

- Puresteel OS 1.0 "Burak" identity
- Custom Calamares branding
- Custom installer launcher
- Custom GNOME wallpaper
- Custom boot splash
- Puresteel system logo for GNOME and Fastfetch

### Removed from defaults

- Firefox ESR
- Chromium
- GNOME Web
- Android Studio
