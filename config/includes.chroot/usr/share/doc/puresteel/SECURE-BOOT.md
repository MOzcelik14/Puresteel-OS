# Secure Boot

`puresteel-secureboot status` reports firmware Secure Boot state, enrolled MOK certificates and DKMS state.

Puresteel does **not** ship a private module-signing key. To enroll your own DER public key:

`puresteel-secureboot enroll /path/to/public-key.der`

MOK enrollment normally completes in the firmware-side MOK Manager after reboot. End-to-end Secure Boot support is not considered validated until shim/GRUB/kernel and out-of-tree modules are tested on real UEFI hardware.
