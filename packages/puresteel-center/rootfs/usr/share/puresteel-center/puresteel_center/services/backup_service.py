import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

from .common import run

def create_backup(destination, selections):
    home = Path.home()
    dest = Path(destination).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive = dest / f"puresteel-backup-{stamp}.tar.gz"

    include=[]
    mapping={
        "documents": home/"Documents",
        "pictures": home/"Pictures",
        "music": home/"Music",
        "config": home/".config",
    }
    for key, path in mapping.items():
        if selections.get(key) and path.exists():
            include.append(path)

    with tempfile.TemporaryDirectory(prefix="puresteel-backup-") as tmp:
        tmp_path=Path(tmp)
        if selections.get("packages"):
            _, apt = run(["sh","-c","apt-mark showmanual 2>/dev/null || true"], timeout=30)
            _, flat = run(["sh","-c","flatpak list --app --columns=application 2>/dev/null || true"], timeout=30)
            (tmp_path/"apt-packages.txt").write_text(apt+"\n", encoding="utf-8")
            (tmp_path/"flatpak-apps.txt").write_text(flat+"\n", encoding="utf-8")
            include += [tmp_path/"apt-packages.txt", tmp_path/"flatpak-apps.txt"]

        try:
            with tarfile.open(archive, "w:gz") as tar:
                for path in include:
                    arc = f"home/{path.name}" if path.is_relative_to(home) else f"system/{path.name}"
                    excluded = None
                    try:
                        excluded = f"{arc}/{archive.resolve().relative_to(path.resolve())}"
                    except ValueError:
                        pass
                    # Destination may be inside Documents/.config. Never archive the
                    # archive-in-progress recursively.
                    def exclude_output(member):
                        return None if excluded and (
                            member.name == excluded or member.name.startswith(excluded + "/")
                        ) else member
                    tar.add(path, arcname=arc, recursive=True, filter=exclude_output)
        except Exception:
            archive.unlink(missing_ok=True)
            raise

    return str(archive)
