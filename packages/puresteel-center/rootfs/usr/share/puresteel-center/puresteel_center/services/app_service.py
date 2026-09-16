import re
from .common import command_exists, privileged, run

def apt_search(query):
    if not command_exists("apt-cache") or len(query.strip()) < 2:
        return []
    code, out = run(["apt-cache","search",query], timeout=25)
    if code != 0:
        return []
    rows=[]
    for line in out.splitlines()[:80]:
        if " - " in line:
            name, desc = line.split(" - ", 1)
            rows.append(("APT", name.strip(), desc.strip()))
    return rows

def flatpak_search(query):
    if not command_exists("flatpak") or len(query.strip()) < 2:
        return []
    code, out = run(["flatpak","search","--columns=application,description",query], timeout=35)
    if code != 0:
        return []
    rows=[]
    for line in out.splitlines()[:80]:
        parts=line.split("\t")
        appid=parts[0].strip() if parts else ""
        desc=parts[1].strip() if len(parts)>1 else ""
        if appid:
            rows.append(("Flatpak", appid, desc))
    return rows

def apt_installed(name):
    code, _ = run(["dpkg-query","-W","-f=${Status}",name], timeout=8)
    return code == 0

def flatpak_installed(appid):
    code, _ = run(["flatpak","info",appid], timeout=8)
    return code == 0

def install(source, name):
    if source == "APT":
        return privileged("apt-install", name)
    return run(["flatpak","install","-y","flathub",name], timeout=3600)

def remove(source, name):
    if source == "APT":
        return privileged("apt-remove", name)
    return run(["flatpak","uninstall","-y",name], timeout=3600)
