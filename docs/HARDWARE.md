# Hardware and graphics support

Puresteel targets standard x86-64 PCs and laptops and is designed to support Intel, AMD and NVIDIA graphics rather than a single vendor-specific setup.

## CPU support

Puresteel includes both Intel and AMD CPU microcode packages:

- `intel-microcode`
- `amd64-microcode`

The kernel is Debian's amd64 kernel package.

## Intel graphics

Puresteel includes the Intel firmware and userspace pieces required by modern Intel graphics stacks:

- `firmware-intel-graphics`
- `firmware-intel-misc`
- `intel-media-va-driver-non-free`
- Mesa Vulkan/DRI components

Depending on the hardware generation, the active kernel driver may be `i915` or `xe`.

This covers both integrated Intel graphics and newer Intel discrete GPUs supported by the Debian kernel/Mesa versions in the current release.

## AMD graphics

Puresteel includes support for AMD integrated and discrete Radeon graphics:

- `firmware-amd-graphics`
- `mesa-vulkan-drivers`
- `mesa-va-drivers`
- `libgl1-mesa-dri`
- `xserver-xorg-video-amdgpu`

Modern supported Radeon hardware normally uses the `amdgpu` kernel driver. Older hardware may use `radeon` depending on kernel support.

## NVIDIA graphics

Puresteel includes Debian's proprietary NVIDIA stack:

- `nvidia-driver`
- `nvidia-settings`
- `firmware-nvidia-graphics`
- `linux-headers-amd64`
- 32-bit NVIDIA/Vulkan libraries for gaming compatibility
- `switcheroo-control`

The NVIDIA kernel modules are built through DKMS. Puresteel also includes its own NVIDIA module aliases/configuration needed by the current Debian driver packaging.

Check NVIDIA status with:

```bash
nvidia-smi
```

## Hybrid graphics

Puresteel is intended to work on hybrid laptops and multi-GPU desktops, including layouts such as:

- Intel iGPU + NVIDIA dGPU
- AMD iGPU + NVIDIA dGPU
- Intel iGPU + AMD dGPU
- AMD iGPU + AMD dGPU

`switcheroo-control` is included for desktop-level GPU integration where supported.

The exact offload behavior depends on the GPU combination, kernel, compositor and application.

## Vulkan and 32-bit compatibility

Puresteel includes 64-bit and i386 Vulkan libraries needed for Steam/Wine gaming workloads.

The gaming package set includes:

```text
libvulkan1
libvulkan1:i386
mesa-vulkan-drivers
mesa-vulkan-drivers:i386
nvidia-driver-libs:i386
nvidia-vulkan-icd:i386
```

This is important for 32-bit Windows games running through Wine/Proton.

## VA-API

Puresteel includes VA-API components for hardware-accelerated video where supported by the GPU and driver stack.

Puresteel Center's **Drivers** page can inspect Vulkan and VA-API availability.

## Useful diagnostic commands

List GPUs and active drivers:

```bash
lspci -nnk | grep -A3 -Ei 'VGA|3D|Display'
```

Loaded graphics modules:

```bash
lsmod | grep -E 'nvidia|nouveau|amdgpu|radeon|i915|xe'
```

Vulkan:

```bash
vulkaninfo --summary
```

VA-API:

```bash
vainfo
```

DKMS:

```bash
dkms status
```

Hybrid graphics service:

```bash
systemctl status switcheroo-control
```

## Real-hardware testing

Virtual machines cannot validate vendor GPU behavior properly. Before a final release, Puresteel should be tested on several real systems covering:

- Intel-only graphics
- AMD-only graphics
- NVIDIA-only graphics
- Intel + NVIDIA hybrid laptops
- AMD + NVIDIA hybrid laptops
- multiple-monitor setups
- suspend/resume
- HDMI/DisplayPort audio
- Vulkan gaming workloads

## Reporting hardware issues

When reporting a graphics problem, include the output of:

```bash
uname -a
lspci -nnk
lsmod
dkms status
```

For NVIDIA systems also include:

```bash
nvidia-smi
```

Puresteel Center → **System Reports** can collect much of this information automatically.
