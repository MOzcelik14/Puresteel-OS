# Troubleshooting Puresteel

This page collects common checks for the live image, installed systems and Puresteel's own package/update infrastructure.

## Puresteel Center does not open

Run it from a terminal:

```bash
puresteel-center
```

If Python/Qt errors appear, verify the package is installed:

```bash
dpkg -l | grep puresteel-center
```

and check its files:

```bash
dpkg -L puresteel-center
```

## Puresteel Center reports no updates

Refresh APT manually:

```bash
sudo apt update
```

Then inspect the configured Puresteel source:

```bash
cat /etc/apt/sources.list.d/puresteel.sources
```

The repository URL should point to:

```text
https://mozcelik14.github.io/Puresteel-OS/apt
```

## Puresteel APT repository errors

Verify the online metadata:

```bash
curl -I https://mozcelik14.github.io/Puresteel-OS/apt/dists/stable/InRelease
```

Verify the installed public key exists:

```bash
ls -l /usr/share/keyrings/puresteel-archive-keyring.asc
```

Do not disable signature verification as a workaround.

## NVIDIA does not load

Check the GPU and active kernel driver:

```bash
lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'
```

Check DKMS:

```bash
dkms status
```

Check loaded modules:

```bash
lsmod | grep -E 'nvidia|nouveau'
```

Check the driver directly:

```bash
nvidia-smi
```

If `nouveau` is active unexpectedly, inspect Puresteel's modprobe configuration under `/etc/modprobe.d/`.

## AMD GPU issues

Check whether `amdgpu` or `radeon` is active:

```bash
lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'
lsmod | grep -E 'amdgpu|radeon'
```

Check firmware/graphics packages:

```bash
dpkg -l | grep -E 'firmware-amd-graphics|mesa-vulkan-drivers|mesa-va-drivers'
```

## Intel GPU issues

Check whether `i915` or `xe` is active:

```bash
lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'
lsmod | grep -E 'i915|xe'
```

Check Intel firmware packages:

```bash
dpkg -l | grep -E 'firmware-intel-graphics|firmware-intel-misc'
```

## Vulkan problems

```bash
vulkaninfo --summary
```

For Steam/Wine, also confirm i386 is enabled:

```bash
dpkg --print-foreign-architectures
```

Expected output includes:

```text
i386
```

## Flatpak problems

List remotes:

```bash
flatpak remotes
```

List installed applications:

```bash
flatpak list
```

Update:

```bash
flatpak update
```

## ZRAM / memory tuning

```bash
zramctl
swapon --show
sysctl vm.swappiness
```

## Failed services

```bash
systemctl --failed
```

Detailed logs for one service:

```bash
journalctl -u SERVICE_NAME -b
```

Recent high-priority boot errors:

```bash
journalctl -p 3 -b
```

## Calamares installation fails

Run the installer from the terminal if possible to capture output, and verify:

- the live system has enough free RAM,
- the target disk is visible,
- the machine was booted in the intended UEFI/legacy mode,
- the target filesystem is not mounted by another tool.

Before retrying destructive partitioning, back up important data.

## ISO build fails

Read the end of:

```bash
build.log
```

Useful syntax checks:

```bash
bash -n build.sh
bash -n scripts/build-center-package.sh
bash -n scripts/release-center.sh
```

If the failure mentions `puresteel-center`, confirm the local package exists:

```bash
ls -lh config/packages.chroot/puresteel-center_*.deb
```

Puresteel Center should be installed into the image from the local `.deb`; the ISO build should not require the online Puresteel repository.

## Collect a report

Puresteel Center → **System Reports** can generate a text report containing the most useful system diagnostics.

For manual reports, include at least:

```bash
cat /etc/os-release
uname -a
lspci -nnk
lsmod
dkms status
systemctl --failed
```
