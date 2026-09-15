# Puresteel OS 1.0 "Burak" RC1

Puresteel OS 1.0 "Burak" RC1 is the first release candidate of Puresteel OS, a Debian 13 (Trixie) based distribution focused on power users, developers, creators and gamers.

The release combines GNOME, Calamares, NVIDIA hybrid-graphics support, a complete Wine/Steam gaming foundation, Flatpak applications, ZRAM tuning and a Fish/Starship terminal environment in a single live and installable image.

## Download

**ISO:** `Puresteel-OS-1.0-Burak-RC1-amd64.iso`

**Size:** approximately 6.3 GB

**SHA256:**

```text
a95da3206e60384651058eb35811e6a02b258d7f53c2d87dc2cfeaf6f42faadb
```

## Important RC1 testing areas

Before the final 1.0 release, additional testing should focus on:

- NVIDIA hybrid laptops
- Wi-Fi firmware across multiple vendors
- audio devices
- suspend/resume
- multi-monitor setups
- Calamares installation on real UEFI hardware
- Steam/Proton gaming on real GPUs

## Known build note

During live-build cleanup, an `/dev/pts` logging warning may appear while temporary build-only packages are removed. The RC1 ISO build completes successfully despite this warning.
