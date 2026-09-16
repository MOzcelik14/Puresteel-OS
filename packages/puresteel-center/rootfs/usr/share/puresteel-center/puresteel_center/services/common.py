import os
import shutil
import subprocess
from pathlib import Path

def run(args, timeout=60, env=None):
    try:
        proc = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=timeout, check=False, env=env
        )
        return proc.returncode, proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)

def command_exists(name):
    return shutil.which(name) is not None

def helper_path():
    candidates = [
        Path("/usr/lib/puresteel-center/puresteel-helper"),
        Path(__file__).resolve().parents[2] / "packaging" / "helper" / "puresteel-helper",
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return ""

def privileged(action, *args, timeout=3600):
    helper = helper_path()
    if not helper:
        return 1, "Puresteel privileged helper is not installed."
    if os.geteuid() == 0:
        return run([helper, action, *args], timeout=timeout)
    if not command_exists("pkexec"):
        return 1, "pkexec is not available."
    return run(["pkexec", helper, action, *args], timeout=timeout)
