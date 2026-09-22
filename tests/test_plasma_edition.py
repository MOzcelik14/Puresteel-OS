"""Static release guard for minimal Puresteel Plasma defaults.

These tests do NOT replace booting the ISO in QEMU.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class PlasmaEditionTests(unittest.TestCase):
    def test_core_selects_plasma_not_cinnamon(self):
        core = source("config/package-lists/puresteel-core.list.chroot").splitlines()
        active = set(line.strip() for line in core if line.strip() and not line.lstrip().startswith("#"))
        self.assertTrue({"plasma-desktop", "sddm", "plasma-nm", "libpam-kwallet5", "kwin-x11",
                         "plasma-workspace", "kwin-wayland", "xdg-desktop-portal-kde"}.issubset(active))
        self.assertTrue({"cinnamon", "cinnamon-core", "lightdm", "slick-greeter",
                         "kde-full", "kde-standard", "plasma-discover", "nemo"}.isdisjoint(active))

    def test_defaults_are_light_and_puresteel_branded(self):
        self.assertIn("ColorScheme=BreezeLight",
                      source("config/includes.chroot/etc/skel/.config/kdeglobals"))
        self.assertIn("Current=breeze",
                      source("config/includes.chroot/etc/sddm.conf.d/10-puresteel.conf"))
        greeter = source("config/includes.chroot/usr/share/sddm/themes/breeze/theme.conf.user")
        self.assertIn("showlogo=shown", greeter)
        self.assertIn("puresteel-light.png", greeter)
        self.assertIn("puresteel-installer.png", greeter)
        init = source("config/includes.chroot/usr/local/bin/puresteel-desktop-init")
        self.assertIn("plasma-defaults-applied", init)
        self.assertIn("first-run-complete", init)

    def test_full_iso_bundles_gaming_creator_developer_and_heroic(self):
        gaming = source("config/package-lists/puresteel-gaming.list.chroot")
        creator = source("config/package-lists/puresteel-creator.list.chroot")
        developer = source("config/package-lists/puresteel-developer.list.chroot")
        multiarch = source("config/hooks/live/0015-puresteel-multiarch.hook.chroot")
        flatpak = source("config/hooks/live/0200-puresteel-flatpak.hook.chroot")
        for name in ("wine", "wine64", "winetricks", "gamemode", "mangohud"):
            self.assertIn(name + "\n", gaming)
        for name in ("kdenlive", "audacity", "ffmpeg"):
            self.assertIn(name + "\n", creator)
        for name in ("build-essential", "cmake", "python3-venv", "gdb"):
            self.assertIn(name + "\n", developer)
        for name in ("steam-installer", "steam-libs-i386", "wine32:i386",
                     "nvidia-driver-libs:i386", "mesa-vulkan-drivers:i386"):
            self.assertIn(name, multiarch)
        self.assertIn("dpkg --add-architecture i386", multiarch)
        self.assertIn("com.heroicgameslauncher.hgl", flatpak)
        self.assertIn("flatpak install --system", flatpak)

    def test_wifi_is_not_forced_into_plaintext(self):
        script = source("config/includes.chroot/usr/local/bin/puresteel-wifi")
        self.assertNotIn("--show-secrets", script)
        self.assertNotIn("wifi-sec.psk ", script)
        self.assertIn("libpam-kwallet5", script)
        self.assertIn("password", source("docs/KDE-WIFI.md"))


if __name__ == "__main__":
    unittest.main()
