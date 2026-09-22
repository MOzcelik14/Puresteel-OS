"""Read-only health of installed Puresteel rolling APT packages.

Uses the locally cached APT index; it does not claim live archive verification.
The privileged Safe Update action handles apt-get update and Timeshift.
"""
import os
import platform
import re
from pathlib import Path

from .common import run

APT_SOURCE = Path("/etc/apt/sources.list.d/puresteel.sources")
APT_KEY = Path("/usr/share/keyrings/puresteel-archive-keyring.asc")
CHANNEL = Path("/etc/puresteel/channel")


def release_status(source=APT_SOURCE, key=APT_KEY, channel=CHANNEL):
    code, installed = run(["dpkg-query", "-W", "-f=${Version}", "puresteel-center"], timeout=12)
    installed = installed.strip() if code == 0 else ""
    code, output = run(["apt-cache", "policy", "puresteel-center"], timeout=12,
                       env={**os.environ, "LC_ALL": "C"})
    match = re.search(r"^\s*Candidate:\s*(\S+)", output, flags=re.M) if code == 0 else None
    candidate = match.group(1) if match and match.group(1) != "(none)" else ""
    pending = False
    if installed and candidate and candidate != installed:
        rc, _ = run(["dpkg", "--compare-versions", candidate, "gt", installed], timeout=10)
        pending = rc == 0
    try:
        configured = "mozcelik14.github.io/Puresteel-OS/apt" in source.read_text()
    except OSError:
        configured = False
    try:
        channel_name = channel.read_text().strip() or "stable"
    except OSError:
        channel_name = "stable"
    return {
        "installed": installed,
        "candidate": candidate,
        "pending": pending,
        "source_ok": configured,
        "key_ok": key.is_file(),
        "channel": channel_name,
        "kernel": platform.release(),
    }
