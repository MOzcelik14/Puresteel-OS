"""No-root regression tests for critical update and rollback behavior."""
import importlib.machinery
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "packages/puresteel-center/rootfs/usr/lib/puresteel-center/puresteel-helper"
loader = importlib.machinery.SourceFileLoader("puresteel_test_helper", str(HELPER))
spec = importlib.util.spec_from_loader(loader.name, loader)
helper = importlib.util.module_from_spec(spec)
loader.exec_module(helper)


class SnapshotSafetyTests(unittest.TestCase):
    def test_failed_snapshot_blocks_all_apt_commands(self):
        with patch.object(helper.os, "geteuid", return_value=0), \
             patch.object(helper, "snapshot", return_value=9), \
             patch.object(helper, "run") as apt, \
             patch.object(sys, "argv", ["puresteel-helper", "safe-upgrade"]):
            self.assertEqual(helper.main(), 9)
            apt.assert_not_called()

    def test_snapshot_marker_contains_real_snapshot_id(self):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            timeshift = directory / "timeshift"
            timeshift.touch()
            config = directory / "timeshift.json"
            config.write_text(json.dumps({"backup_device_uuid": "test-uuid"}))
            marker = directory / "last-update-snapshot"
            before = {"2026-09-18_10-00-00"}
            after = before | {"2026-09-19_12-00-00"}
            with patch.object(helper, "TIMESHIFT_BIN", timeshift), \
                 patch.object(helper, "timeshift_configured", return_value=True), \
                 patch.object(helper, "snapshot_names", side_effect=[before, after]), \
                 patch.object(helper, "TIMESHIFT_CONFIGS", (config,)), \
                 patch.object(helper, "LAST_UPDATE", marker), \
                 patch.object(helper, "run", return_value=0):
                self.assertEqual(helper.snapshot("Before Puresteel system update", mark_last_update=True), 0)
                data = json.loads(marker.read_text())
                self.assertEqual(data["snapshot"], "2026-09-19_12-00-00")
                self.assertEqual(data["backup_device_uuid"], "test-uuid")

    def test_uncertain_snapshot_id_blocks_marking(self):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            timeshift = directory / "timeshift"
            timeshift.touch()
            marker = directory / "last-update-snapshot"
            with patch.object(helper, "TIMESHIFT_BIN", timeshift), \
                 patch.object(helper, "timeshift_configured", return_value=True), \
                 patch.object(helper, "snapshot_names", side_effect=[set(), set()]), \
                 patch.object(helper, "LAST_UPDATE", marker), \
                 patch.object(helper, "run", return_value=0):
                self.assertEqual(helper.snapshot("test", mark_last_update=True), 1)
                self.assertFalse(marker.exists())

    def test_unavailable_timeshift_is_not_a_success(self):
        with tempfile.TemporaryDirectory() as root:
            with patch.object(helper, "TIMESHIFT_BIN", Path(root) / "missing"):
                self.assertEqual(helper.snapshot("test"), 1)


if __name__ == "__main__":
    unittest.main()
