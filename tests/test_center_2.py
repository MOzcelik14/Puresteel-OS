"""Center 2.0 rolling-release status parsing without PySide or root."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "packages/puresteel-center/rootfs/usr/share/puresteel-center/puresteel_center/services/release_service.py"


class RollingCenterTests(unittest.TestCase):
    def test_release_panel_displays_installed_cached_candidate_without_secrets(self):
        source = (ROOT / "packages/puresteel-center/rootfs/usr/share/puresteel-center/puresteel_center/pages/home.py").read_text()
        self.assertIn("ReleaseWorker", source)
        self.assertIn("ROLLING RELEASE STATUS", source)
        self.assertIn("refresh_release", source)
        self.assertNotIn("GPG_PASSPHRASE", source)

    def test_package_version_is_built_into_center_payload(self):
        build = (ROOT / "scripts/build-center-package.sh").read_text()
        self.assertIn('"$STAGE/usr/share/puresteel-center/PACKAGE_VERSION"', build)
        window = (ROOT / "packages/puresteel-center/rootfs/usr/share/puresteel-center/puresteel_center/main_window.py").read_text()
        self.assertIn("PACKAGE_VERSION", window)

    def test_signed_repo_visibility_does_not_auto_apply_updates(self):
        update = (ROOT / "packages/puresteel-center/rootfs/usr/share/puresteel-center/puresteel_center/pages/updates.py").read_text()
        self.assertIn('item[0].startswith("puresteel-")', update)
        self.assertIn("safe=True", update)
        source = SERVICE.read_text()
        self.assertIn("apt-cache", source)
        self.assertIn("dpkg-query", source)
        self.assertNotIn("apt-get install", source)


if __name__ == "__main__":
    unittest.main()
