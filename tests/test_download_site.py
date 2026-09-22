"""Site download links and publication-status separation guards."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DownloadSiteTests(unittest.TestCase):
    def test_public_download_and_fallback_have_exact_paths(self):
        html = (ROOT / "docs/index.html").read_text()
        for name in ("Puresteel-Latest.iso", "Puresteel-Latest.iso.sha256",
                     "Puresteel-Latest.json"):
            self.assertIn("r2.dev/" + name, html)
        self.assertIn("id=\"download\"", html)
        self.assertIn("sha256sum -c Puresteel-Latest.iso.sha256", html)
        self.assertIn("GitHub artifact / build history", html)

    def test_ci_status_is_not_assumed_to_be_r2_publication(self):
        html = (ROOT / "docs/index.html").read_text()
        self.assertIn("publishedRelease", html)
        self.assertIn("latestBuild", html)
        self.assertIn("GitHub CI status is shown separately from R2 publication.", html)
        self.assertIn("data-i18n=\"navDownload\"", html)
        self.assertIn("navDownload:'İndir'", html)
        self.assertIn("navDownload:'Download'", html)

    def test_manifest_includes_size_and_checksum(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text()
        self.assertIn('"bytes": Path("live-image-amd64.hybrid.iso").stat().st_size', workflow)
        self.assertIn('"sha256": Path("Puresteel-Latest.iso.sha256")', workflow)


if __name__ == "__main__":
    unittest.main()
