"""Daily release audit guards for the ISO builder, gaming and release source."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class DailyReleaseAudit(unittest.TestCase):
    def test_windows_wsl_command_has_balanced_bash_quoting(self):
        source = read("windows-build.ps1")
        cmd = next(line for line in source.splitlines()
                   if "& wsl.exe -d $Distro -- bash -lc " in line)
        self.assertTrue(cmd.rstrip().endswith('"'), "WSL shell command must end its double quote")
        self.assertIn("--build", cmd)
        self.assertIn("PURESTEEL_OUTPUT_DIR=", cmd)

    def test_ci_parses_windows_script_and_triggers_only_live_branches(self):
        workflow = read(".github/workflows/validate.yml")
        self.assertIn("windows-powershell-syntax:", workflow)
        self.assertIn("Parser]::ParseFile", workflow)
        self.assertIn("branches: [ main ]", workflow)
        self.assertNotIn("branches: [ main, puresteel-platform-tools", workflow)

    def test_i386_enabled_on_iso_and_gaming_pack_installs_32bit_libraries(self):
        hook = read("config/hooks/live/0015-puresteel-multiarch.hook.chroot")
        self.assertIn("dpkg --add-architecture i386", hook)
        helper = read("packages/puresteel-center/rootfs/usr/lib/puresteel-center/puresteel-helper")
        for name in ("steam-libs-i386", "libvulkan1:i386", "mesa-vulkan-drivers:i386", "libgl1-mesa-dri:i386"):
            self.assertIn('"' + name + '"', helper)
        self.assertIn('"install", "--no-remove", "-y", *pack["apt"]', helper)
        self.assertIn('grep -Fxq i386', read("scripts/smoke-iso.sh"))

    def test_tracked_python_caches_are_removed(self):
        for path in (ROOT / "packages").rglob("*.pyc"):
            self.fail("Tracked package cache left in source tree: " + str(path))
        self.assertIn("__pycache__/", read(".gitignore"))
        self.assertIn("*.pyc", read(".gitignore"))


if __name__ == "__main__":
    unittest.main()
