"""Puresteel GPU Driver Manager no-root regressions: never touch real APT."""
import importlib.machinery
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = ROOT / "packages/puresteel-center/rootfs/usr/share/puresteel-center"
sys.path.insert(0, str(PYTHON_ROOT))

from puresteel_center.services import driver_service as service  # noqa: E402

HELPER = ROOT / "packages/puresteel-center/rootfs/usr/lib/puresteel-center/puresteel-helper"
loader = importlib.machinery.SourceFileLoader("puresteel_drivers_test_helper", str(HELPER))
spec = importlib.util.spec_from_loader(loader.name, loader)
helper = importlib.util.module_from_spec(spec)
loader.exec_module(helper)


class GpuParserTests(unittest.TestCase):
    def test_gpu_parser_handles_pci_domain_and_detects_active_kernel_driver(self):
        sample = (
            "0000:00:02.0 VGA compatible controller [0300]: Intel Corporation [8086:46a3]\n"
            "\tKernel driver in use: i915\n"
            "\tKernel modules: i915\n"
            "0000:01:00.0 3D controller [0302]: NVIDIA Corporation GA107M [10de:25a5]\n"
            "\tKernel driver in use: nvidia\n"
            "\tKernel modules: nouveau, nvidia_drm, nvidia\n"
        )
        gpus = service.parse_gpu_blocks(sample)
        self.assertEqual(len(gpus), 2)
        self.assertEqual([gpu["vendor"] for gpu in gpus], ["Intel", "NVIDIA"])
        self.assertEqual(gpus[1]["driver"], "nvidia")

    def test_no_nvidia_hardware_does_not_offer_nvidia_packages(self):
        with patch.object(service, "run") as commands:
            self.assertEqual(service.driver_choices([{"vendor": "Intel"}]), [])
            commands.assert_not_called()

    def test_driver_choices_require_actual_apt_candidate(self):
        with patch.object(service, "command_exists", return_value=False), \
             patch.object(service, "package_status", return_value={"installed": "", "candidate": ""}):
            self.assertEqual(service.driver_choices([{"vendor": "NVIDIA"}]), [])

    def test_apt_simulation_rejects_removing_packages(self):
        with patch.object(service, "package_status", side_effect=lambda name: {
                "installed": "1.0" if name.startswith("linux-headers-") else "",
                "candidate": "1.0",
             }), patch.object(service, "run", side_effect=[
                 (0, "6.12.0-amd64"), (0, "Remv xserver-xorg-core [1]\nInst nvidia-driver (1.0)"),
             ]):
            code, output = service.simulate_install("nvidia-driver")
        self.assertEqual(code, 4)
        self.assertIn("refuses", output)

    def test_unavailable_driver_is_never_installed(self):
        with patch.object(service, "package_status", return_value={
            "installed": "", "candidate": "",
        }), patch.object(service, "run") as commands:
            code, _ = service.simulate_install("nvidia-tesla-999-driver")
            commands.assert_not_called()
        self.assertEqual(code, 3)

    def test_driver_name_rejects_shell_metacharacters(self):
        code, _ = service.simulate_install("nvidia-driver;rm -rf /")
        self.assertEqual(code, 2)


class PrivilegedDriverSafetyTests(unittest.TestCase):
    def test_root_helper_rechecks_gpu_and_refuses_unknown_driver(self):
        with patch.object(helper, "gpu_present", return_value=True), \
             patch.object(helper, "run") as install:
            self.assertEqual(helper.driver_transaction("install", "nvidia-driver;bad"), 2)
            install.assert_not_called()

    def test_root_helper_refuses_package_removals(self):
        with patch.object(helper, "gpu_present", return_value=True), \
             patch.object(helper, "installed_package", return_value=True), \
             patch.object(helper, "apt_candidate", return_value="1.0"), \
             patch.object(helper, "capture", return_value=(0, "Remv xserver-xorg-core [1]")), \
             patch.object(helper, "run") as install:
            self.assertEqual(helper.driver_transaction("install", "nvidia-driver"), 4)
            install.assert_not_called()

    def test_root_helper_blocks_missing_kernel_headers(self):
        with patch.object(helper, "gpu_present", return_value=True), \
             patch.object(helper, "installed_package", return_value=False), \
             patch.object(helper, "run") as install:
            self.assertEqual(helper.driver_transaction("install", "nvidia-driver"), 5)
            install.assert_not_called()

    def test_root_helper_refuses_vendor_without_hardware(self):
        with patch.object(helper, "gpu_present", return_value=False), \
             patch.object(helper, "run") as install:
            self.assertEqual(helper.driver_transaction("repair", "nvidia"), 2)
            install.assert_not_called()


if __name__ == "__main__":
    unittest.main()
