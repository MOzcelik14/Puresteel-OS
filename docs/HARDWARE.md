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
- Optional matching 32-bit NVIDIA/Vulkan libraries via Debian APT for gaming
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

Puresteel enables the `i386` foreign architecture in the installed image, but **does not preload large 32-bit game libraries into the minimal ISO**. The opt-in Gaming Pack installs Debian's Steam/Wine tools with `steam-libs-i386`, `libvulkan1:i386`, `mesa-vulkan-drivers:i386` and `libgl1-mesa-dri:i386`.

On a proprietary NVIDIA system, install matching `nvidia-driver-libs:i386` and `nvidia-vulkan-icd:i386` from your **enabled Debian repository** after verifying `nvidia-driver` is healthy and APT offers a matching version:

```bash
sudo apt update
apt-cache policy nvidia-driver nvidia-driver-libs:i386 nvidia-vulkan-icd:i386
sudo apt-get -s install nvidia-driver-libs:i386 nvidia-vulkan-icd:i386
```

Only install them if the simulation does not propose removal or an unwanted NVIDIA driver change. Do not install vendor-specific NVIDIA libraries on Intel/AMD-only machines. The generic i386 Mesa libraries are provided on demand through the Gaming Pack.

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
