import json
import re
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENTER_DIR = ROOT / "packages/puresteel-center/rootfs/usr/share/puresteel-center"
if str(CENTER_DIR) not in sys.path:
    sys.path.insert(0, str(CENTER_DIR))

from puresteel_center.services import report_service  # noqa: E402


def _parse_po_msgids(path):
    text = path.read_text(encoding="utf-8")
    return re.findall(r'^msgid "(.+)"$', text, flags=re.MULTILINE)


class DoctorAndReportsTests(unittest.TestCase):
    def test_puresteel_doctor_json_contract(self):
        doctor = ROOT / "config/includes.chroot/usr/local/bin/puresteel-doctor"
        proc = subprocess.run(
            [sys.executable, str(doctor), "--json"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("os", data)
        self.assertIn("kernel", data)
        self.assertIsInstance(data["failed_units"], list)
        self.assertEqual(data["failed_unit_count"], len(data["failed_units"]))
        self.assertIsInstance(data["tools"], dict)
        for key in ("flatpak", "timeshift", "fwupdmgr", "mokutil", "nvidia-smi", "smartctl"):
            self.assertIsInstance(data["tools"].get(key), bool)

    def test_create_support_bundle_creates_valid_tar_gz(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle = Path(tmpdir) / "puresteel-support-bundle.tar.gz"
            out = report_service.create_support_bundle(bundle)
            self.assertEqual(Path(out), bundle)
            self.assertTrue(bundle.is_file())
            with tarfile.open(bundle, "r:gz") as archive:
                names = set(archive.getnames())
            self.assertEqual(
                names,
                {
                    "puresteel-support-bundle/system-report.txt",
                    "puresteel-support-bundle/puresteel-doctor.txt",
                    "puresteel-support-bundle/puresteel-hw-report.txt",
                    "puresteel-support-bundle/journal-errors.txt",
                },
            )

    def test_po_catalogs_stay_in_sync(self):
        pot_ids = _parse_po_msgids(ROOT / "po/puresteel.pot")
        tr_ids = _parse_po_msgids(ROOT / "po/tr.po")
        self.assertGreaterEqual(len(pot_ids), 10)
        self.assertEqual(pot_ids, tr_ids)


if __name__ == "__main__":
    unittest.main()
