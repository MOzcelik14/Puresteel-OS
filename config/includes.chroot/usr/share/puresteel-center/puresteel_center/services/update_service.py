\
from .common import command_exists, privileged, run

def apt_updates():
    if not command_exists("apt"):
        return [], "apt command not found"
    code, output = run(["apt", "list", "--upgradable"], timeout=60)
    if code != 0:
        return [], output
    result = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("Listing"):
            continue
        name = line.split("/", 1)[0]
        version = line.split()[1] if len(line.split()) > 1 else ""
        result.append((name, version))
    return result, ""

def flatpak_updates():
    if not command_exists("flatpak"):
        return [], ""
    code, output = run(["flatpak","remote-ls","--updates","--columns=application,version"], timeout=60)
    if code != 0:
        return [], output
    result = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        result.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""))
    return result, ""

def install_all():
    messages = []
    code, out = privileged("apt-upgrade")
    messages.append(out)
    if code != 0:
        return code, "\n".join(messages)
    if command_exists("flatpak"):
        c2, o2 = run(["flatpak","update","-y"], timeout=3600)
        messages.append(o2)
        if c2 != 0:
            return c2, "\n".join(messages)
    return 0, "\n".join(messages)
