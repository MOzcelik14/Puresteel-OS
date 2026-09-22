"""Puresteel ISO builder UI guards; only execute non-mutating preview/help."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "bootstrap.sh"


def call(*args, env=None):
    return subprocess.run(
        ["/bin/bash", str(BUILDER), *args],
        capture_output=True, text=True, check=False, timeout=12,
        env=env,
    )


class BuilderInterfaceTests(unittest.TestCase):
    def test_help_explains_iso_not_host_install(self):
        result = call("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("BUILDS a live ISO", result.stdout)
        self.assertIn("--preview", result.stdout)

    def test_preview_does_not_write_or_use_sudo_git_apt(self):
        with tempfile.TemporaryDirectory() as root:
            output = Path(root) / "no-output"
            clone = Path(root) / "no-clone"
            env = dict(os.environ, PATH="/nonexistent", NO_COLOR="1",
                       PURESTEEL_OUTPUT_DIR=str(output),
                       PURESTEEL_WORKDIR=str(clone))
            result = call("--preview", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("P U R E S T E E L", result.stdout)
            self.assertIn("01/05", result.stdout)
            self.assertIn("05/05", result.stdout)
            self.assertIn("Nothing was installed or generated", result.stdout)
            self.assertNotIn("\x1b[", result.stdout)
            self.assertFalse(output.exists())
            self.assertFalse(clone.exists())

    def test_menu_preview_no_writes_and_no_tty(self):
        with tempfile.TemporaryDirectory() as root:
            output = Path(root) / "no-menu-output"
            clone = Path(root) / "no-menu-clone"
            env = dict(os.environ, PATH="/nonexistent", NO_COLOR="1",
                       PURESTEEL_OUTPUT_DIR=str(output),
                       PURESTEEL_WORKDIR=str(clone))
            result = call("--preview-menu", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PURESTEEL MENU", result.stdout)
            self.assertIn("Build settings", result.stdout)
            self.assertIn("Preview only", result.stdout)
            self.assertFalse(output.exists())
            self.assertFalse(clone.exists())

    def test_no_terminal_fails_closed(self):
        result = call()
        self.assertEqual(result.returncode, 2)
        self.assertIn("--build", result.stderr)
        self.assertIn("--preview-menu", result.stderr)

    def test_help_mentions_menu_and_unattended_build(self):
        result = call("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Interactive menu", result.stdout)
        self.assertIn("--build", result.stdout)
        self.assertIn("--text-menu", result.stdout)

    @unittest.skipUnless(__import__("shutil").which("script"), "util-linux script unavailable")
    def test_text_menu_can_exit_without_building(self):
        import shlex
        with tempfile.TemporaryDirectory() as root:
            output = Path(root) / "output"
            clone = Path(root) / "clone"
            env = dict(os.environ, TERM="dumb", NO_COLOR="1",
                       PURESTEEL_OUTPUT_DIR=str(output),
                       PURESTEEL_WORKDIR=str(clone))
            cmd = "/bin/bash " + shlex.quote(str(BUILDER)) + " --text-menu"
            result = subprocess.run(
                ["script", "-q", "-e", "-c", cmd, "/dev/null"],
                input="0\n", text=True, capture_output=True,
                timeout=12, check=False, env=env,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PURESTEEL MENU", result.stdout)
            self.assertIn("Menu closed", result.stdout)
            self.assertFalse(output.exists())
            self.assertFalse(clone.exists())

    def test_unsafe_build_directory_rejected_before_sudo_or_output(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            output = base / "output"
            # A former implementation recursively removed WORKDIR; reject a
            # parent of HOME before any log or build operation.
            env = dict(os.environ, HOME=str(base / "home"),
                       PURESTEEL_OUTPUT_DIR=str(output),
                       PURESTEEL_WORKDIR=str(base),
                       NO_COLOR="1")
            result = call("--build", env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be a directory under", result.stderr)
            self.assertFalse(output.exists())

    def test_repeat_build_never_recursively_deletes_selected_directory(self):
        source = BUILDER.read_text(encoding="utf-8")
        self.assertNotIn('rm -rf -- "$WORKDIR"', source)
        self.assertIn('mktemp -d "$WORKDIR/run.XXXXXXXX"', source)
        self.assertIn('run_logged git clone --depth=1 --branch "$REF" "$REPO" "$SOURCE_DIR"', source)

    def test_ref_validation_accepts_main_and_common_git_refs_without_sudo(self):
        # Runs real --build preflight, not --preview, without any apt/sudo/git
        # commands available. A passing ref must reach the missing apt-get
        # check; no directories are written or dependencies installed.
        import shutil
        realpath = shutil.which("realpath")
        self.assertIsNotNone(realpath)
        with tempfile.TemporaryDirectory() as root:
            parent = Path(root)
            fakebin = parent / "bin"
            fakebin.mkdir()
            (fakebin / "realpath").symlink_to(realpath)
            output = parent / "output"
            home = parent / "home"
            env = dict(os.environ, PATH=str(fakebin), HOME=str(home),
                       PURESTEEL_OUTPUT_DIR=str(output), NO_COLOR="1")
            for ref in ("main", "feat/terminal-ui", "v1.4.0-1"):
                with self.subTest(ref=ref):
                    result = call("--build", env=dict(env, PURESTEEL_REF=ref))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("Invalid PURESTEEL_REF", result.stderr)
                    self.assertIn("Required command missing: apt-get", result.stderr)
                    self.assertFalse(output.exists())

    def test_ref_validation_reports_hidden_bad_characters_without_sudo(self):
        import shutil
        realpath = shutil.which("realpath")
        self.assertIsNotNone(realpath)
        with tempfile.TemporaryDirectory() as root:
            parent = Path(root)
            fakebin = parent / "bin"
            fakebin.mkdir()
            (fakebin / "realpath").symlink_to(realpath)
            env = dict(os.environ, PATH=str(fakebin), HOME=str(parent / "home"),
                       PURESTEEL_OUTPUT_DIR=str(parent / "output"), NO_COLOR="1",
                       PURESTEEL_REF="main\\r")
            result = call("--build", env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid PURESTEEL_REF", result.stderr)
            self.assertIn("main", result.stderr)
            self.assertFalse((parent / "output").exists())

    def test_verbose_preview_and_invalid_flag(self):
        result = call("--verbose", "--preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        invalid = call("--unknown")
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("Unknown option", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
