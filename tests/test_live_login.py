"""Static regression tests for the Live ISO login path.

These do not replace boot-testing the finished ISO in QEMU.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


class LiveLoginTests(unittest.TestCase):
    def test_live_only_service_precedes_sddm(self):
        unit = source("config/includes.chroot/etc/systemd/system/puresteel-live-session.service")
        self.assertIn("ConditionKernelCommandLine=boot=live", unit)
        self.assertIn("Wants=live-config.service", unit)
        self.assertIn("After=live-config.service", unit)
        self.assertIn("Before=display-manager.service sddm.service", unit)
        self.assertIn("WantedBy=graphical.target", unit)
        self.assertIn("ExecStart=/bin/sh /usr/local/libexec/puresteel-live-session", unit)
        build_hook = source("config/hooks/live/0360-puresteel-plasma.hook.chroot")
        self.assertIn("systemctl enable puresteel-live-session.service", build_hook)

    def test_recovery_and_plasma_wayland_autologin(self):
        script = source("config/includes.chroot/usr/local/libexec/puresteel-live-session")
        self.assertIn('if ! id "$LIVE_USER"', script)
        self.assertIn("useradd --create-home --user-group", script)
        self.assertIn("/usr/share/wayland-sessions/plasma.desktop", script)
        self.assertIn("Session=$session", script)
        self.assertIn("Relogin=false", script)
        self.assertIn("90-puresteel-live.conf", script)
        self.assertIn("user-setup", source("config/package-lists/live.list.chroot"))

    def test_no_live_autologin_or_default_password_in_installed_image(self):
        live_script = source("config/includes.chroot/usr/local/libexec/puresteel-live-session")
        self.assertLess(live_script.index("boot=live"), live_script.index("useradd"))
        self.assertNotIn("chpasswd", live_script)
        self.assertNotIn("passwd -d", live_script)
        default_sddm = source("config/includes.chroot/etc/sddm.conf.d/10-puresteel.conf")
        self.assertIn("User=\nSession=\n", default_sddm)


if __name__ == "__main__":
    unittest.main()
