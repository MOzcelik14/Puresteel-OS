# Puresteel Center

Puresteel Center is Puresteel's Qt 6 / PySide6 system-management application. Its goal is to collect the distribution's everyday administration tools in one place instead of spreading them across several unrelated utilities.

## Modules

### Home

Shows quick access to the most common tasks and summarizes the main management areas.

### Updates

- checks APT updates
- checks Flatpak updates
- can install system package updates through a privileged helper
- keeps the GUI itself unprivileged

### Applications

- searches the APT catalog
- searches Flatpak
- installs and removes applications
- presents both package ecosystems from one interface

### Drivers

The Drivers page is vendor-neutral and is designed for **Intel, AMD and NVIDIA** systems.

It can inspect:

- detected GPUs
- active kernel driver
- available kernel modules
- NVIDIA driver state / `nvidia-smi`
- DKMS status
- `nouveau` state
- `switcheroo-control`
- graphics firmware packages
- Vulkan availability
- VA-API availability

Puresteel treats Intel and AMD graphics primarily as kernel + firmware + Mesa stacks, while NVIDIA's proprietary driver stack is managed separately.

### Sources

- displays APT source files
- lists Flatpak remotes
- adds/removes user Flatpak remotes

System APT source editing is intentionally conservative to reduce the risk of breaking the package manager through an accidental repository change.

### Backup

Can archive selected user data and system/package information, including:

- Documents
- Pictures
- Music
- `.config`
- manually installed APT package list
- installed Flatpak application list

### System Reports

Collects troubleshooting information such as:

- kernel and OS information
- memory usage
- filesystem usage
- PCI graphics devices
- NVIDIA status
- DKMS status
- failed systemd services
- recent journal errors

Reports can be saved to a text file for debugging or bug reports.

## Languages

The interface currently supports:

- Turkish
- English

The selected language is stored with Qt settings and restored on the next launch.

## Privilege model

Puresteel Center does **not** run the whole GUI as root.

Privileged operations use this design:

```text
Puresteel Center GUI
        │
        ▼
      pkexec
        │
        ▼
Polkit authorization
        │
        ▼
/usr/lib/puresteel-center/puresteel-helper
        │
        ├── apt upgrade
        ├── apt install/remove
        └── graphics stack repair actions
```

The helper accepts a fixed set of actions instead of arbitrary shell commands.

Relevant files in the package include:

```text
/usr/bin/puresteel-center
/usr/share/puresteel-center/
/usr/lib/puresteel-center/puresteel-helper
/usr/share/polkit-1/actions/org.puresteel.center.policy
/usr/share/applications/puresteel-center.desktop
```

## Packaging

Puresteel Center is maintained as a Debian package source inside:

```text
packages/puresteel-center/
```

Current version information is stored in:

```text
packages/puresteel-center/VERSION
```

Build the package:

```bash
./scripts/build-center-package.sh
```

Publish a new version into the Puresteel APT repository:

```bash
./scripts/release-center.sh 1.4.0-1
```

This script requires the private Puresteel archive signing key. It rebuilds Center and component packages, signs the APT repository, and also stages the current `.deb` files in `config/packages.chroot/` so future ISO builds include matching package versions locally. The committed online repository still contains older signed packages until a separate signed release is published. Never publish unsigned metadata.

## Updating installed systems

Once a newer package has been published to the signed Puresteel repository, installed systems receive it through normal APT updates:

```bash
sudo apt update
sudo apt full-upgrade
```

This means a Puresteel Center update does not require downloading a new ISO.

## Development status

Puresteel Center is still under active development. Before a final Puresteel release, privileged package operations, backup behavior, graphics actions and package-manager edge cases should be tested on real installed systems as well as in the live environment.
