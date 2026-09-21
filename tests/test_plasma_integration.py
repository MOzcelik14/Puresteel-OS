"""Protect Plasma migration from legacy desktop repair regressions."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def src(path):
    return (ROOT / path).read_text(encoding="utf-8")

class PlasmaIntegrationTests(unittest.TestCase):
    def test_recovery_and_helper_use_sddm(self):
        for path in (
            "config/includes.chroot/usr/local/sbin/puresteel-recovery",
            "config/includes.chroot/usr/local/bin/puresteel-repair",
            "packages/puresteel-center/rootfs/usr/lib/puresteel-center/puresteel-helper",
        ):
            value = src(path)
            self.assertNotIn("repair-lightdm", value)
            self.assertNotIn("lightdm_repair", value)
            self.assertIn("sddm", value.lower())
        self.assertIn("enable --force sddm.service", src("config/includes.chroot/usr/local/sbin/puresteel-recovery"))
    def test_plasma_accessibility_uses_kde_config(self):
        value = src("config/includes.chroot/usr/local/bin/puresteel-accessibility")
        self.assertNotIn("org.cinnamon", value)
        self.assertIn("kwriteconfig6", value)
        self.assertIn("plasma-apply-colorscheme", value)
    def test_center_konsole_and_wifi_diagnostic(self):
        value = src("packages/puresteel-center/rootfs/usr/share/puresteel-center/puresteel_center/pages/puresteel.py")
        self.assertNotIn("gnome-terminal", value)
        self.assertIn('["konsole", "--hold", "-e", "/bin/sh", "-lc", command]', value)
        self.assertIn('self.launch_terminal("puresteel-wifi")', value)
    def test_dolphin_admin_protocol_is_packaged(self):
        self.assertIn('["dolphin", uri]', src("config/includes.chroot/usr/local/bin/puresteel-open-admin"))
        self.assertIn("\nkio-admin\n", src("config/package-lists/puresteel-core.list.chroot"))
if __name__ == "__main__":
    unittest.main()
