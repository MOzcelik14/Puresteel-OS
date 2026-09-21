# Puresteel Recovery

Select **Puresteel Recovery** from GRUB when normal boot or the desktop is broken.

Available operations include broken-package repair, initramfs/GRUB rebuild, SDDM repair, NVIDIA DKMS rebuild, Puresteel Doctor, Timeshift listing/restore and the guided **Undo last Puresteel update** flow.

Timeshift restore remains interactive on purpose: always verify the selected snapshot and target disk before confirming.

For an older kernel, choose **Advanced options for Puresteel** in GRUB. `puresteel-kernel` lists installed kernels and highlights an alternate candidate without changing GRUB state automatically.
