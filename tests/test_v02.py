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


class BetaFindings(unittest.TestCase):
    """Regressions for issues found by the first fresh-machine beta run."""

    def test_hyphen_wrapped_at_line_end_is_recovered(self):
        blocks = pdf.parse("- Introduced the on-call model and PCI-DSS controls\n")
        for extracted in ("Introduced the on-\ncall model and PCI-\nDSS controls",
                          "Introduced the oncall model and PCIDSS controls",
                          "Introduced the on-call model and PCI-DSS controls"):
            errors, _ = pdf.analyze(blocks, {"reading": extracted})
            self.assertEqual(errors, [], extracted)

    def test_errors_name_the_line(self):
        cases = {"# Name\n\n1. First": "Line 3", "# Name\nText with [link](x)": "Line 2",
                 "# Name\n\n- *italic*": "Line 3", "# Name\n- **open": "Line 2",
                 "#### Too deep": "Line 1"}
        for source, expected in cases.items():
            with self.assertRaisesRegex(ValueError, expected, msg=source):
                pdf.parse(source)

    def test_pasted_bullet_styles_become_lists(self):
        blocks = pdf.parse("# Name\n\u2022 Led platform\n* Hired 9 managers\n- **Cut cost 38%**\n")
        self.assertEqual(blocks[1], ("ul", ["Led platform", "Hired 9 managers", "**Cut cost 38%**"]))

    def test_bold_paragraph_is_not_a_bullet(self):
        self.assertEqual(pdf.parse("**Strong opening** line")[0][0], "p")

    def test_pdf_title_comes_from_name(self):
        self.assertIn("<title>Jordan Example</title>", pdf.html(pdf.parse("# Jordan Example\n\nText")))

    def test_second_init_explains_instead_of_errno(self):
        with tempfile.TemporaryDirectory() as temp:
            root = core.workspace(Path(temp) / "ws", initialized=False)
            core.init(root, demo=False)
            with self.assertRaisesRegex(ValueError, "already exists"):
                core.init(root, demo=False)

    def test_timeout_message_suggests_fix(self):
        with self.assertRaisesRegex(ValueError, "JOBKIT_CHROME"):
            pdf.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.5)

    def test_failure_message_keeps_tool_error(self):
        with self.assertRaisesRegex(ValueError, "boom"):
            pdf.run([sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"])

    @unittest.skipUnless(pdf.export_check() == "ok", "PDF export unavailable here: " + pdf.export_check())
    def test_real_build_with_many_hyphenated_words(self):
        words = ("on-call", "PCI-DSS", "cross-functional", "go-to-market", "end-to-end", "data-driven",
                 "B2B-SaaS", "follow-the-sun", "zero-downtime", "self-service")
        bullets = "\n".join(f"- {' '.join(words[i:] + words[:i])} programme number {i} for the team"
                             for i in range(len(words)))
        with tempfile.TemporaryDirectory() as temp:
            root = core.workspace(Path(temp) / "ws", initialized=False)
            core.init(root, demo=False)
            (root / "cv.md").write_text("# Hyphen Test\n\n## Experience\n\n" + bullets + "\n", encoding="utf-8")
            result = pdf.build(root, "cv.md", "build", "cv")
            self.assertGreaterEqual(result["pages"], 1)


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


class ThirdReport(unittest.TestCase):
    def test_init_makes_everything_private_and_parent_visible(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Docs" / "Job Search"
            core.init(root, demo=True)
            self.assertEqual((root.parent.stat().st_mode & 0o777), 0o755)
            for path in [root, *root.rglob("*")]:
                self.assertEqual(path.stat().st_mode & 0o077, 0, path)

    def test_check_cv_reports_format_without_pdf(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "ws"
            core.init(root, demo=True)
            (root / "cv.md").write_text("# Sam Doe\n\n## Experience\n\n- **Grew** revenue\n", encoding="utf-8")
            result = pdf.check_source(root, "cv.md")
            self.assertEqual(result["headings"], ["Sam Doe", "Experience"])
            (root / "bad.md").write_text("# Sam\n\n| a | b |\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                pdf.check_source(root, "bad.md")

    def test_letter_paper(self):
        blocks = pdf.parse("# Sam Doe\n")
        self.assertIn("size: letter", pdf.html(blocks, "letter"))
        self.assertIn("size: A4", pdf.html(blocks))
