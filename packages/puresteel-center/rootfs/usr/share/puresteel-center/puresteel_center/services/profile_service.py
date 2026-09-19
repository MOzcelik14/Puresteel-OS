from pathlib import Path
from .common import privileged, run

PROFILES = ("balanced", "gaming", "creator", "battery")


def current():
    path = Path("/etc/puresteel/profile")
    try:
        value = path.read_text().strip()
        return value if value in PROFILES else "balanced"
    except OSError:
        return "balanced"


def status():
    return run(["/usr/local/sbin/puresteel-profile", "status"], timeout=20)


def apply(name):
    if name not in PROFILES:
        return 2, "Invalid Puresteel profile"
    return privileged("profile-apply", name)
