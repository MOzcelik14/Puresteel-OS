\
import re
from .common import command_exists, privileged, run

def _vendor_from_line(line):
    low = line.lower()
    if "nvidia" in low:
        return "NVIDIA"
    if "amd" in low or "advanced micro devices" in low or "ati " in low:
        return "AMD"
    if "intel" in low:
        return "Intel"
    return "Other"

def _parse_gpu_blocks(text):
    blocks = []
    current = []
    for line in text.splitlines():
        if re.match(r"^[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9a-fA-F]", line):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)

    gpus = []
    for block in blocks:
        first = block[0]
        if not any(x in first.lower() for x in ("vga compatible controller", "3d controller", "display controller")):
            continue
        vendor = _vendor_from_line(first)
        driver = ""
        modules = ""
        for line in block[1:]:
            s = line.strip()
            if s.startswith("Kernel driver in use:"):
                driver = s.split(":", 1)[1].strip()
            elif s.startswith("Kernel modules:"):
                modules = s.split(":", 1)[1].strip()
        model = first.split(":", 2)[-1].strip()
        gpus.append({
            "vendor": vendor,
            "model": model,
            "driver": driver or "—",
            "modules": modules or "—",
        })
    return gpus

def _pkg_installed(name):
    if not command_exists("dpkg-query"):
        return False
    code, _ = run(["dpkg-query", "-W", "-f=${Status}", name], timeout=6)
    return code == 0

def collect():
    data = {
        "gpus": [],
        "kernel": "?",
        "nvidia": "Not installed",
        "dkms": "dkms unavailable",
        "switcheroo": False,
        "nouveau": False,
        "firmware": [],
        "vulkan": "Unknown",
        "vaapi": "Unknown",
    }

    code, out = run(["uname", "-r"])
    if code == 0:
        data["kernel"] = out

    if command_exists("lspci"):
        _, out = run(["lspci", "-nnk"])
        data["gpus"] = _parse_gpu_blocks(out)

    if command_exists("nvidia-smi"):
        code, out = run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            timeout=15
        )
        data["nvidia"] = out if code == 0 else "Installed, not active"

    _, lsmod = run(["sh", "-c", "lsmod 2>/dev/null || true"])
    data["nouveau"] = "nouveau" in lsmod

    if command_exists("dkms"):
        _, out = run(["dkms", "status"], timeout=15)
        data["dkms"] = out or "No DKMS modules"

    if command_exists("systemctl"):
        code, _ = run(["systemctl", "is-active", "switcheroo-control.service"], timeout=8)
        data["switcheroo"] = code == 0

    firmware_pkgs = (
        "firmware-nvidia-graphics",
        "firmware-intel-graphics",
        "firmware-intel-misc",
        "firmware-amd-graphics",
        "firmware-misc-nonfree",
    )
    data["firmware"] = [pkg for pkg in firmware_pkgs if _pkg_installed(pkg)]

    if command_exists("vulkaninfo"):
        code, out = run(["vulkaninfo", "--summary"], timeout=20)
        if code == 0:
            devices = [l.strip() for l in out.splitlines() if "deviceName" in l]
            data["vulkan"] = "\n".join(devices[:6]) if devices else "Available"
        else:
            data["vulkan"] = "Unavailable"
    else:
        data["vulkan"] = "vulkan-tools not installed"

    if command_exists("vainfo"):
        code, out = run(["sh", "-c", "vainfo 2>&1 | head -40"], timeout=20)
        data["vaapi"] = "Available" if code == 0 else out[:500] or "Unavailable"
    else:
        data["vaapi"] = "vainfo not installed"

    return data

def repair(vendor):
    vendor = vendor.lower()
    if vendor == "nvidia":
        return privileged("nvidia-reinstall")
    if vendor == "intel":
        return privileged("graphics-repair-intel")
    if vendor == "amd":
        return privileged("graphics-repair-amd")
    return 1, f"Unsupported vendor: {vendor}"
