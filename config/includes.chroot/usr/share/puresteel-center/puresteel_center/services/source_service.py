\
from pathlib import Path
from .common import command_exists, run

def apt_sources():
    files=[]
    paths=[Path("/etc/apt/sources.list")]
    d=Path("/etc/apt/sources.list.d")
    if d.exists():
        paths += sorted(list(d.glob("*.list")) + list(d.glob("*.sources")))
    for p in paths:
        if p.exists():
            try:
                files.append((str(p), p.read_text(encoding="utf-8", errors="replace").strip()))
            except OSError:
                pass
    return files

def flatpak_remotes():
    if not command_exists("flatpak"):
        return []
    code, out = run(["flatpak","remotes","--columns=name,url"], timeout=20)
    if code != 0:
        return []
    rows=[]
    for line in out.splitlines():
        parts=line.split("\t")
        if parts and parts[0].strip():
            rows.append((parts[0].strip(), parts[1].strip() if len(parts)>1 else ""))
    return rows

def add_flatpak_remote(name, url):
    return run(["flatpak","remote-add","--user","--if-not-exists",name,url], timeout=30)

def remove_flatpak_remote(name):
    return run(["flatpak","remote-delete","--user",name], timeout=30)
