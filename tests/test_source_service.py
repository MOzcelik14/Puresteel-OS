"""Puresteel Flatpak source regression tests: no root/system deletion."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages/puresteel-center/rootfs/usr/share/puresteel-center"))
from puresteel_center.services import source_service as sources  # noqa: E402


class RemoteScopeTests(unittest.TestCase):
    def test_user_and_system_remotes_are_separate(self):
        with patch.object(sources, "command_exists", return_value=True), \
             patch.object(sources, "run", side_effect=[
                 (0, "custom\thttps://example.org/custom.flatpakrepo"),
                 (0, "flathub\thttps://dl.flathub.org/repo/"),
             ]) as command:
            rows, errors = sources.flatpak_remotes()
        self.assertEqual(errors, "")
        self.assertEqual(rows[0][2], "user")
        self.assertEqual(rows[1][2], "system")
        self.assertIn("--user", command.call_args_list[0].args[0])
        self.assertIn("--system", command.call_args_list[1].args[0])

    def test_system_remote_cannot_be_removed_through_user_page(self):
        with patch.object(sources, "run") as command:
            status, message = sources.remove_flatpak_remote("flathub", "system")
        self.assertNotEqual(status, 0)
        self.assertIn("System remotes", message)
        command.assert_not_called()

    def test_remote_rejects_invalid_name_or_non_https_url(self):
        with patch.object(sources, "run") as command:
            self.assertNotEqual(sources.add_flatpak_remote("bad;rm", "https://example.org")[0], 0)
            self.assertNotEqual(sources.add_flatpak_remote("valid", "http://example.org")[0], 0)
            command.assert_not_called()

    def test_valid_remote_stays_user_scoped(self):
        with patch.object(sources, "run", return_value=(0, "done")) as command:
            self.assertEqual(sources.add_flatpak_remote(
                "personal", "https://example.org/repo.flatpakrepo"), (0, "done"))
        self.assertEqual(command.call_args.args[0][:3],
                         ["flatpak", "remote-add", "--user"])


if __name__ == "__main__":
    unittest.main()
