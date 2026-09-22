"""Signed rolling APT publishing guards (no private key required)."""
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


class RollingAptTests(unittest.TestCase):
    def test_rolling_version_is_valid_and_newer_than_base(self):
        version = subprocess.check_output(
            ["bash", "scripts/rolling-apt-version.sh"], cwd=ROOT, text=True
        ).strip()
        base = source("packages/puresteel-center/VERSION").strip()
        self.assertRegex(version, r"^\d[^\s]*\+git\d{14}\.[0-9a-f]{12}-1$")
        subprocess.run(["dpkg", "--compare-versions", version, "gt", base], check=True)

    def test_all_package_builders_use_same_rolling_override(self):
        for filename in ("scripts/build-center-package.sh",
                         "scripts/build-meta-packages.sh",
                         "scripts/build-component-packages.sh"):
            self.assertIn("PURESTEEL_PACKAGE_VERSION", source(filename))
        release = source("scripts/release-center.sh")
        self.assertIn('export PURESTEEL_PACKAGE_VERSION="$VERSION"', release)
        self.assertIn('verify-apt-repository.py --require-version "$VERSION"', release)
        self.assertIn('PUBLISHED_FPR', release)
        self.assertIn('"$FPR" != "$PUBLISHED_FPR"', release)

    def test_publisher_does_not_run_from_unvalidated_pull_requests(self):
        workflow = source(".github/workflows/publish-apt.yml")
        for guard in ("workflow_run.conclusion == 'success'",
                      "workflow_run.event == 'push'",
                      "workflow_run.head_branch == 'main'",
                      "workflow_run.head_repository.full_name == github.repository",
                      "PURESTEEL_APT_SIGNING_KEY_B64",
                      "PURESTEEL_APT_SIGNING_PASSPHRASE",
                      "PURESTEEL_APT_PUBLISH_TOKEN",
                      "git rev-parse origin/main",
                      "git add docs/apt"):
            self.assertIn(guard, workflow)
        self.assertIn("'docs/apt/**'", source(".github/workflows/validate.yml"))
        self.assertNotIn("PRIVATE KEY-----", workflow)


if __name__ == "__main__":
    unittest.main()
