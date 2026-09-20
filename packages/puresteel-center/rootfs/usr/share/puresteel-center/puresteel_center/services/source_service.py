"""Flatpak scope-aware source management; system remotes are read-only here."""
import re
from urllib.parse import urlsplit
from pathlib import Path
from .common import command_exists, run

REMOTE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")


def apt_sources():
    files = []
    paths = [Path("/etc/apt/sources.list")]
    directory = Path("/etc/apt/sources.list.d")
    if directory.exists():
        paths += sorted(list(directory.glob("*.list")) + list(directory.glob("*.sources")))
    for path in paths:
        if path.exists():
            try:
                files.append((str(path), path.read_text(encoding="utf-8", errors="replace").strip()))
            except OSError:
                pass
    return files


def flatpak_remotes():
    if not command_exists("flatpak"):
        return [], "Flatpak is not installed"
    rows, errors = [], []
    for scope in ("user", "system"):
        code, output = run(["flatpak", "remotes", "--" + scope,
                            "--columns=name,url"], timeout=25)
        if code:
            errors.append(scope + ": " + output[-400:])
            continue
        for line in output.splitlines():
            parts = line.split("\t", 1)
            if parts[0].strip():
                rows.append((parts[0].strip(),
                             parts[1].strip() if len(parts) == 2 else "", scope))
    return rows, "\n".join(errors)


def add_flatpak_remote(name, url):
    if not REMOTE_NAME.fullmatch(name):
        return 2, "Remote name must contain only letters, digits, dot, hyphen or underscore."
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        return 2, "Enter a complete HTTPS Flatpak repository URL."
    return run(["flatpak", "remote-add", "--user", "--if-not-exists",
                name, url], timeout=60)


def remove_flatpak_remote(name, scope):
    if scope != "user":
        return 2, "System remotes are managed by the distribution. This page only removes user remotes."
    if not REMOTE_NAME.fullmatch(name):
        return 2, "Invalid Flatpak remote name."
    return run(["flatpak", "remote-delete", "--user", name], timeout=60)
