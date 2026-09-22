"""GitHub Pages must render Puresteel Markdown in the styled documentation view."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GUIDES = {
    "INSTALL", "BUILD", "PURESTEEL_CENTER", "UPDATES", "ROLLING",
    "HARDWARE", "KDE-WIFI", "PLATFORM", "QA", "TROUBLESHOOTING",
}


class DocumentationSiteTests(unittest.TestCase):
    def test_site_links_point_to_styled_guides(self):
        page = (DOCS / "index.html").read_text(encoding="utf-8")
        self.assertNotRegex(page, r'href="[^"]+\.md(?:#[^"]*)?"')
        targets = set(re.findall(r'href="guide\.html\?doc=([A-Z_-]+)"', page))
        self.assertTrue(GUIDES.issubset(targets), GUIDES - targets)

    def test_all_guide_documents_exist(self):
        for name in GUIDES:
            self.assertTrue((DOCS / (name + ".md")).is_file(), name)

    def test_all_guides_have_substantive_turkish_versions(self):
        for name in GUIDES:
            english = (DOCS / (name + ".md")).read_text(encoding="utf-8")
            turkish_path = DOCS / "tr" / (name + ".md")
            self.assertTrue(turkish_path.is_file(), name)
            turkish = turkish_path.read_text(encoding="utf-8")
            self.assertGreater(len(turkish), 900, name)
            self.assertIn("# ", turkish, name)
            self.assertNotEqual(turkish, english, name)
            self.assertEqual(turkish.count("```"), english.count("```"), name)

    def test_language_switch_loads_matching_localized_markdown(self):
        viewer = (DOCS / "guide.html").read_text(encoding="utf-8")
        script = (DOCS / "assets/guide.js").read_text(encoding="utf-8")
        self.assertIn('data-guide-lang="tr"', viewer)
        self.assertIn('data-guide-lang="en"', viewer)
        self.assertIn('localStorage.setItem("puresteel-lang", choice)', script)
        self.assertIn('fetch((tr ? "tr/" : "") + current + ".md"', script)
        self.assertIn('github + "docs/" + (tr ? "tr/" : "")', script)
        self.assertIn('"&lang=" + lang', script)

    def test_renderer_is_local_and_sanitizes_markdown(self):
        viewer = (DOCS / "guide.html").read_text(encoding="utf-8")
        script = (DOCS / "assets/guide.js").read_text(encoding="utf-8")
        for library in ("vendor/showdown.min.js", "vendor/purify.min.js"):
            self.assertIn(library, viewer)
            self.assertTrue((DOCS / "assets" / library).is_file())
        for required in ("known.has(requested)", "DOMPurify.sanitize",
                         'fetch((tr ? "tr/" : "") + current + ".md"', "guide.html?doc=",
                         "localLink(originalHref)", "navigator.clipboard.writeText"):
            self.assertIn(required, script)
        self.assertIn(".docnav a[hidden]{display:none}", viewer)
        self.assertTrue((DOCS / ".nojekyll").is_file())

    def test_actions_checks_renderer_syntax(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertIn("node --check docs/assets/guide.js", workflow)


if __name__ == "__main__":
    unittest.main()
