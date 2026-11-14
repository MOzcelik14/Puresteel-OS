from datetime import datetime
import io
from pathlib import Path
import tarfile
from .common import command_exists, run

def _section(title, command, timeout=25):
    code, out = run(command, timeout=timeout)
    return f"\\n=== {title} ===\\n{out if out else '(no output)'}\\n"

def _optional_section(title, binary, args=(), timeout=25):
    if not command_exists(binary):
        return f"\\n=== {title} ===\\n({binary} not installed)\\n"
    return _section(title, [binary, *args], timeout=timeout)

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
    parts.append(_optional_section("Puresteel Doctor", "puresteel-doctor"))
    parts.append(_optional_section("Secure Boot", "puresteel-secureboot", ("status",)))
    parts.append(_optional_section("Battery", "puresteel-battery"))
    parts.append(_section("Journal Errors", ["sh","-c","journalctl -p 3 -b --no-pager -n 120 2>/dev/null || true"], timeout=35))
    return "".join(parts)


def create_support_bundle(output_path):
    """Create a compressed .tar.gz support bundle with non-sensitive system diagnostics."""
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    files = {
        "system-report.txt": generate(),
        "puresteel-doctor.txt": _optional_section("Puresteel Doctor", "puresteel-doctor"),
        "puresteel-hw-report.txt": _optional_section("Hardware Report", "puresteel-hw-report"),
        "journal-errors.txt": _section(
            "Journal Errors",
            ["sh", "-c", "journalctl -p 3 -b --no-pager -n 200 2>/dev/null || true"],
            timeout=35,
        ),
    }
    with tarfile.open(target, "w:gz") as archive:
        for name, content in files.items():
            data = content.encode("utf-8", errors="replace")
            info = tarfile.TarInfo(name=f"puresteel-support-bundle/{name}")
            info.size = len(data)
            info.mtime = int(datetime.now().timestamp())
            archive.addfile(info, io.BytesIO(data))
    return str(target)
