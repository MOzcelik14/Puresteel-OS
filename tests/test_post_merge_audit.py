"""Post-merge release consistency guards; no ISO or privileged commands required."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


class PostMergeAuditTests(unittest.TestCase):
    def test_plasma_iso_builders_have_matching_name(self):
        name = "Puresteel-Plasma-amd64.iso"
        for path in ("bootstrap.sh", "windows-build.ps1", "docs/BUILD.md"):
            self.assertIn(name, source(path))
            self.assertNotIn("Puresteel-Cinnamon-amd64.iso", source(path))

    def test_legacy_nemo_actions_are_not_bundled(self):
        self.assertFalse((ROOT / "config/includes.chroot/usr/share/nemo/actions").exists())
        self.assertNotIn("nemo_action", source("scripts/build-component-packages.sh"))

    def test_recovery_and_hardware_report_describe_plasma(self):
        self.assertIn("SDDM repair", source("config/includes.chroot/usr/share/doc/puresteel/RECOVERY.md"))
        report = source("config/includes.chroot/usr/local/bin/puresteel-hw-report")
        self.assertIn('"desktop": "KDE Plasma 6 (Wayland or X11)"', report)
        self.assertNotIn('"desktop": "Cinnamon/X11"', report)


    def test_public_website_describes_current_plasma_edition(self):
        html = source("docs/index.html")
        for outdated in ("Cinnamon", "LightDM", "Slick Greeter", "Nemo"):
            self.assertNotIn(outdated, html)
        self.assertIn("Current main · Plasma 6", html)
        self.assertIn("Güncel main · Plasma 6", html)
        self.assertIn("Wayland + X11", html)

    def test_rolling_iso_website_has_matching_public_downloads(self):
        html = source("docs/index.html")
        url = "https://pub-6bd67d084cc74faa8573569db4b21336.r2.dev"
        self.assertIn(url + "/Puresteel-Latest.iso\"", html)
        self.assertIn(url + "/Puresteel-Latest.iso.sha256\"", html)
        self.assertIn("downloadIso:'Güncel ISO indir'", html)
        self.assertIn("downloadIso:'Download latest ISO'", html)
        self.assertIn("r2.dev", source("docs/ROLLING.md"))

    def test_iso_build_does_not_claim_to_publish_signed_apt(self):
        for path in ("build.sh", ".github/workflows/validate.yml"):
            self.assertNotIn("release-center.sh", source(path))
        self.assertIn("private key", source("docs/UPDATES.md"))


if __name__ == "__main__":
    unittest.main()
