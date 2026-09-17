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

`puresteel-hw-report` prints an anonymized JSON report intended for the GitHub hardware report template. It deliberately omits hostname, username, serial numbers, MAC addresses and IP addresses.
