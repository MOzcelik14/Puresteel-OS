# Puresteel ISO integration QA

This is a release gate, not a list of assumptions. Do not publish a new Plasma ISO as stable until a
fresh ISO has been built and these tests have been recorded. A successful
syntax/package workflow does not prove an installed system boots.

## Current release-gate status

Code/package CI and the read-only terminal-menu tests do not count as a tested Plasma release. The current public GitHub release contains no downloadable Plasma ISO. The QEMU and hardware boxes below remain intentionally unchecked until test evidence exists. The optional ISO smoke job is a static payload check, **not an automated Calamares GUI installation**.

## Automated static checks

```sh
python3 -m unittest discover -s tests -v
./scripts/build-center-package.sh
./scripts/build-meta-packages.sh
./scripts/build-component-packages.sh
./build.sh
./scripts/smoke-iso.sh path/to/puresteel.iso
```

`smoke-iso.sh` checks file presence inside the *built* live filesystem
and its installed-package manifest. It is not a substitute for boot testing.

## QEMU fresh installation

On an x86_64 Linux host with QEMU installed:

```sh
qemu-img create -f qcow2 puresteel-qa.qcow2 48G
qemu-system-x86_64 -enable-kvm -m 4096 -smp 4 \
  -drive file=puresteel-qa.qcow2,format=qcow2,if=virtio \
  -cdrom path/to/puresteel.iso -boot d -vga virtio
```

If KVM is unavailable, remove `-enable-kvm` (slower). Do NOT attach the
computer's physical disk to QEMU. Run Calamares on the throwaway virtual disk,
shut down, remove the ISO and boot the installed qcow2. Repeat once under
UEFI/OVMF with a fresh virtual disk if firmware/EFI coverage is required.

### Record pass/fail for each test

- [ ] Live boot reaches KDE Plasma Wayland; Puresteel Breeze Light wallpaper and SDDM render.
- [ ] Calamares completes without modifying disks other than the qcow2.
- [ ] Installed system boots with SDDM/Plasma and also offers X11 fallback.
- [ ] First Run appears exactly once and persists its completion marker.
- [ ] Language, Puresteel Breeze Light and Dark, icon, wallpaper, hardware and power profile apply.
- [ ] SDDM password login opens a matching-password kdewallet via PAM; no Wi-Fi prompt repeats after login.
- [ ] Existing agent-owned Wi-Fi connections can be migrated only with user consent; `puresteelctl wifi` leaks no PSK.
- [ ] Plasma X11 fallback remains available for NVIDIA testing.
- [ ] No KDE PIM/Akonadi/Discover or large creator/gaming apps are preinstalled.
- [ ] Puresteel Center and all cards remain accessible at 1366x768.
- [ ] Profile apply/reboot persists; Doctor displays both swap and ZRAM.
- [ ] The seven ISO-selected Puresteel packages are registered with dpkg; optional role metapackages are not preinstalled.
- [ ] `puresteelctl snapshot create` creates a listed, restorable snapshot.
- [ ] Safe Update aborts if Timeshift fails (use a THROWAWAY VM to force failure).
- [ ] Safe Update records one real snapshot ID in last-update-snapshot JSON.
- [ ] GRUB Puresteel Recovery opens console on the installed VM.
- [ ] SDDM repair enables `sddm.service` (not LightDM) from the Repair GUI and GRUB Recovery.
- [ ] Dolphin `admin://` opens via `kio-admin` after explicit Polkit approval.
- [ ] Undo Last Update displays recorded snapshot, verifies it exists and requests confirmation.
- [ ] After disposable test change, Timeshift restores a chosen snapshot.
- [ ] `puresteel-info` and crash report contain no SSID, username, MAC, IP or raw journal logs.
- [ ] `scripts/release-artifacts.sh` manifest matches installed packages in ISO.

## Real hardware (opt-in only after VM tests)

NVIDIA offload, DKMS across kernel upgrades, Wi-Fi, PipeWire, high-refresh
display, suspend/resume, battery reporting, Secure Boot and MOK require
compatible physical hardware. Do not claim them passed merely because a CI
job or QEMU boot succeeded. Maintain a backup of personal data separate
from Timeshift and never test destructive rollback against an irreplaceable
workstation.
