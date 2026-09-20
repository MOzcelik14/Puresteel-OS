# Puresteel platform layer

Puresteel adds a distro-specific management layer on top of Debian 13 and Cinnamon.

## Daily commands

- `puresteelctl status`
- `puresteelctl doctor`
- `puresteelctl snapshot create`
- `puresteelctl update`
- `puresteelctl gpu status`
- `puresteelctl battery`
- `puresteelctl firmware status`
- `puresteelctl health all`
- `puresteelctl logs`
- `puresteelctl secureboot status`
- `puresteelctl flatpak repair`
- `puresteelctl kernel`

## Recovery

Use **Puresteel Recovery** from GRUB for package repair, initramfs/GRUB repair, LightDM recovery, NVIDIA DKMS rebuild, Timeshift restore and the last-update rollback workflow.

## Secure Boot

Puresteel can report Secure Boot/MOK state and enroll a DER public key supplied by the owner. Private signing keys are never bundled in the image or repository. End-to-end Secure Boot validation still requires signed boot artifacts and real-hardware testing.

## Release integrity

`scripts/release-artifacts.sh IMAGE.iso` creates SHA256, package manifest and provenance metadata. It creates an armored detached GPG signature only when a signing key is explicitly configured.

## Hardware reports

`puresteel-hw-report` prints a limited, share-oriented JSON report intended for the GitHub hardware report template. It deliberately omits hostname, username, serial numbers, MAC addresses and IP addresses.

## Packaging and updates

`build.sh` bundles real versioned Debian packages for Puresteel Center, platform tools,
Recovery, themes/branding, desktop defaults and five role metapackages. The matching
files in `config/includes.chroot` remain the build's single source of truth during
this migration; they are also owned by the installed component packages so an existing
machine can receive future updates through APT. `scripts/release-center.sh` stages
all ten packages in the signed stable repository, not just Center. Publishing the
signed `docs/apt` tree remains an explicit maintainer action.

Safe Update blocks APT when a pre-update Timeshift snapshot cannot be created and
verified. Use `puresteelctl update --no-snapshot` only when intentionally accepting
that risk. Recovery's Undo Last Update reads the actual snapshot ID and requires
confirmation of the target and filesystem before invoking Timeshift.

`puresteel-info` and `puresteel-crash-helper` include only allowlisted diagnostics.
`puresteel-logs` is **private** and can contain personal information. Hardware
models themselves may be unique even in the allowlisted report.

Validation jobs check syntax, component packages and no-root safety regression tests.
A successful CI job does **not** prove that Calamares, GRUB Recovery or a real NVIDIA
machine works; those remain explicit integration tests in `docs/QA.md`.

## GPU driver manager

The Center GPU & Drivers page discovers only NVIDIA driver metapackages visible
in enabled Debian APT repositories. It shows the active PCI kernel drivers,
package candidates and installed versions, matching running-kernel headers,
DKMS, firmware, Secure Boot, Vulkan and actual `vainfo` exit status.

Before installing or repairing, Puresteel runs an APT simulation with
`--no-remove`; the privileged helper repeats package allowlist, GPU presence,
kernel headers, APT candidate and removal checks. It refuses potentially
package-removing NVIDIA transitions instead of guessing that a replacement is
safe. The UI uses QThread workers; no long APT transaction runs on the GUI
thread. A successful APT transaction does **not** mean the driver became active
without a reboot: DKMS and hardware must be tested on the installed machine.
