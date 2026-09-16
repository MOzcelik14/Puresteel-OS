from .common import command_exists, privileged, run


def apt_updates():
    if not command_exists("apt"):
        return [], "apt command not found"

    # apt prints a scripting warning to stderr. Suppress stderr here so it can
    # never be mistaken for an upgradable package by the UI.
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
        if (
            lower.startswith("listing")
            or lower.startswith("warning:")
            or "apt does not have a stable cli interface" in lower
        ):
            continue

        # Real apt-list entries contain repository metadata after a '/'.
        # Example: package/trixie-security 1.2.3 amd64 [upgradable from: 1.2.2]
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


def flatpak_updates():
    if not command_exists("flatpak"):
        return [], ""

    code, output = run(
        ["flatpak", "remote-ls", "--updates", "--columns=application,version"],
        timeout=60,
    )
    if code != 0:
        return [], output

    result = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        result.append(
            (parts[0].strip(), parts[1].strip() if len(parts) > 1 else "")
        )
    return result, ""


def install_all():
    messages = []

    code, out = privileged("apt-upgrade")
    messages.append(out)
    if code != 0:
        return code, "\n".join(messages)

    if command_exists("flatpak"):
        c2, o2 = run(["flatpak", "update", "-y"], timeout=3600)
        messages.append(o2)
        if c2 != 0:
            return c2, "\n".join(messages)

    return 0, "\n".join(messages)
