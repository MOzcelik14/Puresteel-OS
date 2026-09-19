from .common import command_exists, privileged, run

CRITICAL_PREFIXES = (
    "linux-image", "linux-headers", "linux-base", "systemd", "grub", "shim",
    "nvidia", "firmware-", "initramfs-tools", "cryptsetup", "mesa-", "libgl", "libvulkan"
)


def apt_updates():
    if not command_exists("apt"):
        return [], "apt command not found"

    code, output = run(
        ["sh", "-c", "LC_ALL=C apt list --upgradable 2>/dev/null"],
        timeout=60,
    )
    if code != 0:
        return [], output

    result = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("listing") or lower.startswith("warning:") or "apt does not have a stable cli interface" in lower:
            continue
        if "/" not in line:
            continue
        fields = line.split()
        if not fields:
            continue
        name = fields[0].split("/", 1)[0]
        version = fields[1] if len(fields) > 1 else ""
        if name:
            result.append((name, version))
    return result, ""


def classify_apt(items):
    critical, normal = [], []
    for item in items:
        name = item[0].lower()
        (critical if name.startswith(CRITICAL_PREFIXES) else normal).append(item)
    return critical, normal


def flatpak_updates():
    if not command_exists("flatpak"):
        return [], ""
    code, output = run(["flatpak", "remote-ls", "--updates", "--columns=application,version"], timeout=60)
    if code != 0:
        return [], output
    result = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        result.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""))
    return result, ""


def install_all(safe=True):
    messages = []
    code, out = privileged("safe-upgrade" if safe else "apt-upgrade", timeout=7200)
    messages.append(out)
    if code != 0:
        return code, "\n".join(messages)

    if command_exists("flatpak"):
        c2, o2 = run(["flatpak", "update", "-y"], timeout=3600)
        messages.append(o2)
        if c2 != 0:
            return c2, "\n".join(messages)
    return 0, "\n".join(messages)
