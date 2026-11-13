import sys
import tempfile
from pathlib import Path
import unittest

from toolkit import core, pdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import privacy_check  # noqa: E402


class PrivacyCheck(unittest.TestCase):
    def test_detects_secrets_and_personal_paths(self):
        # Built at runtime so the samples never appear literally in the release tree.
        user, sep = "someone", "\\"
        for sample in ("ghp_" + "a" * 36, "github_pat_" + "b" * 30, "AKIA" + "C" * 16,
                       sep.join(["C:", "Users", user, "cv.pdf"]),
                       "/".join(["", "Users", user, "cv.pdf"]), "/".join(["", "home", user, "cv.pdf"])):
            self.assertTrue(privacy_check.SENSITIVE.search(sample), sample)

    def test_ignores_ordinary_text(self):
        self.assertIsNone(privacy_check.SENSITIVE.search("Run python3 -m toolkit doctor in /usr/bin"))


class Markdown(unittest.TestCase):
    def test_bold_renders_and_recovers_as_plain_text(self):
        blocks = pdf.parse("# Name\n\n- **Grew revenue 40%** across three markets\n")
        self.assertIn("<strong>Grew revenue 40%</strong>", pdf.html(blocks))
        errors, _ = pdf.analyze(blocks, {"reading": "Name\nGrew revenue 40% across three markets"})
        self.assertEqual(errors, [])

    def test_rejects_unbalanced_bold_and_other_markup(self):
        for source in ("- **open bold", "Text with *italic*", "A [link](https://x.example)", "`code`"):
            with self.assertRaises(ValueError, msg=source):
                pdf.parse(source)

    def test_master_cv_template_is_buildable_markdown(self):
        template = Path(__file__).resolve().parents[1] / "templates" / "master-cv.md"
        self.assertTrue(pdf.parse(template.read_text(encoding="utf-8")))


class Workspace(unittest.TestCase):
    def test_init_creates_experience_sources_and_roles(self):
        with tempfile.TemporaryDirectory() as temp:
            root = core.workspace(Path(temp) / "My Job Search", initialized=False)
            core.init(root, demo=False)
            for name in ("experience/INDEX.md", "experience/_role-template.md", "career-story.md",
                         "open-questions.md", "profile.md", "master-cv.md", "ledger.json"):
                self.assertTrue((root / name).is_file(), name)
            self.assertTrue((root / "sources").is_dir())
            self.assertTrue((root / "roles").is_dir())
            config = core.read(root / "config.json")
            for key, value in config.items():
                self.assertTrue((root / value).exists(), f"{key} -> {value}")

    def test_default_workspace_is_visible(self):
        self.assertFalse(Path(core.DEFAULT_WORKSPACE).name.startswith("."))


if __name__ == "__main__":
    unittest.main()
