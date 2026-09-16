from datetime import datetime
from .common import command_exists, run

def _section(title, command, timeout=25):
    code, out = run(command, timeout=timeout)
    return f"\\n=== {title} ===\\n{out if out else '(no output)'}\\n"

def generate():
    parts=[f"Puresteel System Report\\nGenerated: {datetime.now().isoformat(timespec='seconds')}\\n"]
    parts.append(_section("Kernel", ["uname","-a"]))
    parts.append(_section("OS Release", ["sh","-c","cat /etc/os-release 2>/dev/null"]))
    parts.append(_section("Memory", ["sh","-c","free -h 2>/dev/null"]))
    parts.append(_section("Disk", ["sh","-c","df -hT 2>/dev/null"]))
    parts.append(_section("PCI Graphics", ["sh","-c","lspci -nnk 2>/dev/null | grep -A3 -Ei 'VGA|3D|Display' || true"]))
    parts.append(_section("NVIDIA", ["sh","-c","nvidia-smi 2>&1 || true"]))
    parts.append(_section("DKMS", ["sh","-c","dkms status 2>/dev/null || true"]))
    parts.append(_section("Failed Services", ["sh","-c","systemctl --failed --no-pager 2>/dev/null || true"]))
    parts.append(_section("Journal Errors", ["sh","-c","journalctl -p 3 -b --no-pager -n 120 2>/dev/null || true"], timeout=35))
    return "".join(parts)
