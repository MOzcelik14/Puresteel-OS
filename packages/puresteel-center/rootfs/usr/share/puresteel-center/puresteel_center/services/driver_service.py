"""Repository-backed GPU discovery and safe driver planning for Debian Puresteel.

This module never guesses an unsupported driver version. Only packages exposed
by the configured APT sources are offered.
"""
import os
import re
from .common import command_exists, privileged, run

NVIDIA_NAME = re.compile(r"nvidia(?:-tesla-[0-9]+)?-driver")
GPU_ADDRESS = re.compile(r"^(?:[0-9a-fA-F]{4}:)?[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]\s")
FIRMWARE = {
    "NVIDIA": ("firmware-nvidia-graphics",),
    "Intel": ("firmware-intel-graphics", "firmware-intel-misc"),
    "AMD": ("firmware-amd-graphics",),
}


def vendor_from_line(line):
    low = line.lower()
    if "nvidia" in low:
        return "NVIDIA"
    if "advanced micro devices" in low or "amd/" in low or "ati " in low:
        return "AMD"
    if "intel" in low:
        return "Intel"
    return "Other"


def parse_gpu_blocks(output):
    blocks, current = [], []
    for line in output.splitlines():
        if GPU_ADDRESS.match(line):
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
        if not any(category in first.lower() for category in
                   ("vga compatible controller", "3d controller", "display controller")):
            continue
        vendor = vendor_from_line(first)
        driver, modules = "", ""
        for line in block[1:]:
            line = line.strip()
            if line.startswith("Kernel driver in use:"):
                driver = line.partition(":")[2].strip()
            elif line.startswith("Kernel modules:"):
                modules = line.partition(":")[2].strip()
        gpus.append({
            "vendor": vendor,
            "model": first.split(": ", 1)[-1].strip(),
            "pci_address": first.split(" ", 1)[0],
            "driver": driver or "—",
            "modules": modules or "—",
        })
    return gpus


def package_status(name):
    """Return installed version and available candidate; no status from guessed data."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9+.-]*", name):
        return {"installed": "", "candidate": ""}
    code, output = run(["env", "LC_ALL=C", "apt-cache", "policy", name], timeout=12)
    if code:
        return {"installed": "", "candidate": ""}
    installed = re.search(r"^\s*Installed:\s*(\S+)", output, re.MULTILINE)
    candidate = re.search(r"^\s*Candidate:\s*(\S+)", output, re.MULTILINE)
    def parse(match):
        return match.group(1) if match and match.group(1) != "(none)" else ""
    return {"installed": parse(installed), "candidate": parse(candidate)}


def driver_choices(gpus):
    if not any(g["vendor"] == "NVIDIA" for g in gpus):
        return []
    choices = {"nvidia-driver"}
    if command_exists("apt-cache"):
        code, output = run(["env", "LC_ALL=C", "apt-cache", "search",
                            "--names-only", "^nvidia(-tesla-[0-9]+)?-driver$"], timeout=20)
        if code == 0:
            for line in output.splitlines():
                name = line.split(" - ", 1)[0].strip()
                if NVIDIA_NAME.fullmatch(name):
                    choices.add(name)
    result = []
    for name in sorted(choices):
        state = package_status(name)
        if state["candidate"] or state["installed"]:
            result.append({"name": name, **state})
    return result


def simulate_install(name):
    if not NVIDIA_NAME.fullmatch(name):
        return 2, "Only repository-backed NVIDIA driver packages are supported."
    state = package_status(name)
    if not state["candidate"]:
        return 3, "No installable candidate for this driver in enabled APT sources."
    kernel = run(["uname", "-r"], timeout=5)[1].strip()
    headers = package_status("linux-headers-" + kernel) if kernel else {"installed": "", "candidate": ""}
    code, output = run(["env", "LC_ALL=C", "apt-get", "-s", "install", name], timeout=45)
    if code:
        return code, "APT could not produce a valid installation plan:\n" + output[-8000:]
    removed = [line.split()[1] for line in output.splitlines() if line.startswith("Remv ")]
    text = ["Requested driver: " + name,
            "Repository candidate: " + state["candidate"],
            "Installed version: " + (state["installed"] or "not installed"),
            "Running kernel: " + (kernel or "unknown"),
            "Matching headers: " + (headers["installed"] or "NOT INSTALLED"),
            "",
            "APT simulation:", output[-12000:]]
    if removed:
        text.append("\nAPT plans to REMOVE: " + ", ".join(removed))
        text.append("Puresteel refuses automated driver changes that remove packages.")
        return 4, "\n".join(text)
    if not headers["installed"]:
        text.append("\nInstall matching kernel headers before changing an NVIDIA DKMS driver.")
        return 5, "\n".join(text)
    return 0, "\n".join(text)



REPAIR_PACKAGES = {
    "nvidia": ("nvidia-driver", "nvidia-settings", "switcheroo-control"),
    "intel": ("firmware-intel-graphics", "firmware-intel-misc",
              "intel-media-va-driver-non-free", "mesa-vulkan-drivers",
              "mesa-va-drivers", "libvulkan1"),
    "amd": ("firmware-amd-graphics", "mesa-vulkan-drivers", "mesa-va-drivers",
            "libvulkan1", "xserver-xorg-video-amdgpu"),
}


def simulate_repair(vendor):
    packages = REPAIR_PACKAGES.get(vendor.lower())
    if not packages:
        return 2, "Unsupported graphics vendor."
    if any(not package_status(name)["candidate"] for name in packages):
        return 3, "A required package is missing from configured APT sources."
    if vendor == "nvidia":
        kernel = run(["uname", "-r"], timeout=5)[1].strip()
        if not package_status("linux-headers-" + kernel)["installed"]:
            return 5, "Matching running-kernel headers are missing."
    code, output = run(["env", "LC_ALL=C", "apt-get", "-s", "install",
                        "--no-remove", "--reinstall", *packages], timeout=45)
    if code:
        return code, output[-12000:]
    removed = [line for line in output.splitlines() if line.startswith("Remv ")]
    if removed:
        return 4, "APT would remove packages. Operation refused.\n" + output[-10000:]
    return 0, "Packages: " + ", ".join(packages) + "\n\n" + output[-12000:]


def collect():
    data = {
        "gpus": [], "kernel": "?", "nvidia": "Not installed",
        "dkms": "dkms unavailable", "switcheroo": False, "nouveau": False,
        "firmware": [], "vulkan": "Unknown", "vaapi": "Unknown",
        "choices": [], "headers": "", "secureboot": "Unknown",
    }
    code, kernel = run(["uname", "-r"], timeout=5)
    if code == 0:
        data["kernel"] = kernel.strip()
        data["headers"] = package_status("linux-headers-" + data["kernel"])["installed"]

    if command_exists("lspci"):
        data["gpus"] = parse_gpu_blocks(run(["lspci", "-nnk"], timeout=20)[1])
    data["choices"] = driver_choices(data["gpus"])

    if command_exists("nvidia-smi"):
        code, output = run(["nvidia-smi", "--query-gpu=name,driver_version",
                            "--format=csv,noheader"], timeout=15)
        data["nvidia"] = output if code == 0 else "Installed but unavailable:\n" + output[-700:]

    if command_exists("lsmod"):
        code, output = run(["lsmod"], timeout=10)
        data["nouveau"] = code == 0 and any(
            line.split()[0] == "nouveau" for line in output.splitlines()[1:] if line.split()
        )
    if command_exists("dkms"):
        code, output = run(["dkms", "status"], timeout=15)
        data["dkms"] = output if code == 0 else "DKMS status unavailable:\n" + output[-700:]
    if command_exists("systemctl"):
        data["switcheroo"] = run(["systemctl", "is-active", "switcheroo-control.service"], timeout=8)[0] == 0

    vendors = {gpu["vendor"] for gpu in data["gpus"]}
    for vendor in vendors:
        for name in FIRMWARE.get(vendor, ()):
            state = package_status(name)
            data["firmware"].append({
                "name": name, "installed": state["installed"],
                "candidate": state["candidate"],
            })

    if command_exists("vulkaninfo"):
        code, output = run(["vulkaninfo", "--summary"], timeout=20)
        data["vulkan"] = (
            "\n".join(x.strip() for x in output.splitlines() if "deviceName" in x) or "Available"
        ) if code == 0 else "Unavailable:\n" + output[-500:]
    else:
        data["vulkan"] = "vulkan-tools is not installed"

    if command_exists("vainfo"):
        code, output = run(["vainfo"], timeout=20)
        data["vaapi"] = "Available" if code == 0 else "Unavailable:\n" + output[-500:]
    else:
        data["vaapi"] = "vainfo is not installed"

    if command_exists("mokutil"):
        code, output = run(["mokutil", "--sb-state"], timeout=12)
        data["secureboot"] = output if code == 0 else "Unavailable / legacy boot"
    return data


def install_driver(name):
    code, output = simulate_install(name)
    if code:
        return code, output
    return privileged("driver-install", name, timeout=7200)


def repair(vendor):
    vendor = vendor.lower()
    code, preview = simulate_repair(vendor)
    if code:
        return code, preview
    return privileged("driver-repair", vendor, timeout=7200)
