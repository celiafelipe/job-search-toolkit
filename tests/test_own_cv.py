"""Bring your own CV: advisory feedback on the candidate's PDF, and the package rule that accepts it."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from examples.demo import OWN_CV, fixture, simple_pdf
from toolkit import __main__ as cli, core, owncv, pdf, quality

POPPLER = bool(pdf.find_tool("pdftotext"))

SINGLE = """Rowan Example
Exhibit coordinator | rowan@example.org | +44 20 7946 0000

Experience

Visitor Programs Assistant, Paper Harbor Museum                     2021 to 2024
- Redesigned exhibit wayfinding and tested signage with 40 visitors.
- Trained 12 volunteers on a handover checklist.
"""

SIDEBAR = "\n".join(f"{left:<37}{right}" for left, right in [
    ("Contact", "Rowan Example"),
    ("Lisbon", "Professional Experience"),
    ("Skills", "Head of Programs, Orchard Co, 2020 to 2024"),
    ("Research", "Redesigned exhibit wayfinding across three galleries"),
    ("Signage", "Trained volunteers on a handover checklist every season"),
    ("Training", "Grew weekend visits after the signage was replaced"),
    ("Languages", "Ran monthly accessibility walk-throughs with local groups"),
    ("English", "Wrote plain language labels for the new collection"),
    ("", "Led the volunteer rota for the summer opening hours"),
])


def ids(findings):
    return {item["id"] for item in findings}


class Readability(unittest.TestCase):
    def test_clean_single_column_has_no_serious_findings(self):
        found = ids(owncv.readability(SINGLE * 3, SINGLE * 3, 1, 0))
        self.assertFalse(found & {"columns", "contact_missing", "no_text", "rating_symbols", "icon_glyphs"})

    def test_sidebar_layout_is_flagged_as_columns(self):
        self.assertIn("columns", ids(owncv.readability(SIDEBAR + " word" * 60, SIDEBAR, 1, 0)))

    def test_image_only_and_missing_contact(self):
        self.assertEqual(ids(owncv.readability("  \f", "", 1, 2)), {"no_text"})
        text = "Rowan Example\nExperience\n" + "word " * 80
        self.assertIn("contact_missing", ids(owncv.readability(text, text, 1, 0)))

    def test_icons_ratings_spacing_and_images(self):
        text = SINGLE + "\ue0b0 \ue0b1 \ue0b2\nFrench \u25cf\u25cf\u25cf\u25cb\u25cb\nE X P E R I E N C E\n" + "w " * 60
        found = owncv.readability(text, text, 1, 6)
        self.assertTrue({"icon_glyphs", "rating_symbols", "spaced_letters", "images"} <= ids(found))
        self.assertEqual(found, sorted(found, key=lambda f: ["high", "medium", "low"].index(f["severity"])))


class Content(unittest.TestCase):
    def test_reuses_cv_rules_and_flags_duties_numbers_and_unbacked_figures(self):
        text = ("Rowan Example\n" + "x" * 120 + "\nI am passionate.\n"
                + "".join(f"- Responsible for task {name}\n" for name in "abcde") + "- Grew visits by 25%\n")
        warnings = " ".join(owncv.content(text, "Grew visits by 18% in 2023."))
        for expected in ("first person", "passionate", "duties rather than results", "have a number", "25%"):
            self.assertIn(expected, warnings)
        self.assertNotIn("will wrap", warnings)  # a finished PDF has no Markdown header line to keep short
        self.assertNotIn("not in the experience files", " ".join(owncv.content(text, "")))


class Lint(unittest.TestCase):
    def test_own_cv_choice_replaces_master_cv_checks(self):
        from toolkit import lint
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "ws"
            core.init(root, demo=True)
            self.assertTrue(any("placeholder" in w for w in lint.run(root)["warnings"]))
            profile = root / "profile.md"
            profile.write_text(profile.read_text(encoding="utf-8").replace(
                "- CV choice:", "- CV choice: own (my-cv/Rowan-Example-CV.pdf)\n- Old CV choice line:"),
                encoding="utf-8")
            warnings = " ".join(lint.run(root)["warnings"])
            self.assertNotIn("placeholder", warnings)
            self.assertIn("my-cv/ has no PDF", warnings)
            (root / "my-cv").mkdir()
            simple_pdf(root / "my-cv" / "cv.pdf", OWN_CV)
            self.assertIn("no saved review-cv report", " ".join(lint.run(root)["warnings"]))
            core.atomic(root / "my-cv" / "readability.json",
                        {"kind": "candidate_cv_check", "cv": core.record(root / "my-cv" / "cv.pdf")})
            self.assertEqual(lint.run(root), {"lint": "ok", "errors": [], "warnings": []})


class SuppliedCvGate(unittest.TestCase):
    """The package contract, written by hand so it runs without Poppler."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root, self.folder, self.package, self.review, _ = fixture(
            Path(self.temp.name) / "private", with_cv=False)
        mine = self.root / "my-cv"
        mine.mkdir()
        self.cv = mine / "Rowan-Example-CV.pdf"
        simple_pdf(self.cv, OWN_CV)
        self.report = mine / "readability.json"
        core.atomic(self.report, {"schema": 1, "kind": "candidate_cv_check", "cv": core.record(self.cv),
                                  "readability": [{"id": "phone_missing", "severity": "low", "message": "x"}],
                                  "content": [], "advisory": "Suggestions only."})
        inspection = self.folder / "inspection.json"
        self.change(inspection, attachments={"cv": {"required": True, "slot": "CV", "extensions": [".pdf"]}})
        self.change(self.package, inspection=core.record(inspection))
        self.attach({"kind": "cv", "source": "candidate", "file": core.record(self.cv),
                     "readability": core.record(self.report)})

    def change(self, file, **updates):
        doc = core.read(file)
        doc.update(updates)
        core.atomic(file, doc)

    def attach(self, *attachments, visual=None):
        self.change(self.package, attachments=list(attachments))
        self.change(self.review, package=core.record(self.package), visual=visual or {})

    def gate(self):
        return quality.gate(self.root, self.package, self.review, final=True)

    def test_supplied_cv_passes_without_visual_review_despite_findings(self):
        self.assertEqual(self.gate()["attachments"][0]["source"], "candidate")

    def test_visual_entry_for_supplied_cv_is_rejected(self):
        attachment = core.read(self.package)["attachments"][0]
        self.attach(attachment, visual={"cv": {"pdf_sha256": attachment["file"]["sha256"]}})
        with self.assertRaisesRegex(ValueError, "Visual review must cover every PDF built here"):
            self.gate()

    def test_readability_check_must_match_exact_bytes(self):
        simple_pdf(self.cv, OWN_CV + ["One more line"])
        attachment = {"kind": "cv", "source": "candidate", "file": core.record(self.cv),
                      "readability": core.record(self.report)}
        self.attach(attachment)
        with self.assertRaisesRegex(ValueError, "run review-cv again"):
            self.gate()
        self.attach({**attachment, "readability": None})
        with self.assertRaises((TypeError, ValueError)):
            self.gate()

    def test_only_cv_and_no_build_receipt(self):
        attachment = core.read(self.package)["attachments"][0]
        self.attach({**attachment, "build": attachment["readability"]})
        with self.assertRaisesRegex(ValueError, "no build receipt"):
            self.gate()
        self.attach({**attachment, "source": "upload"})
        with self.assertRaisesRegex(ValueError, "generated or candidate"):
            self.gate()

    def test_generated_cv_still_needs_a_build_receipt(self):
        self.attach({"kind": "cv", "file": core.record(self.cv)})
        with self.assertRaisesRegex(ValueError, "needs its build receipt"):
            self.gate()


@unittest.skipUnless(POPPLER, "Poppler (pdftotext) is not installed here")
class ReviewCvCommand(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def test_demo_package_with_own_cv_passes_check(self):
        root, _, package, review, _ = fixture(Path(self.temp.name) / "private", with_cv=False, own_cv=True)
        plan = quality.gate(root, package, review, final=True)
        self.assertEqual(core.read(review)["visual"], {})
        self.assertEqual(plan["attachments"][0]["source"], "candidate")

    def test_command_is_advisory_and_never_changes_the_file(self):
        root = Path(self.temp.name).resolve() / "ws"
        core.init(root, demo=True)
        simple_pdf(root / "sources" / "mine.pdf", ["Rowan Example", "I am passionate about museums."])
        before = core.record(root / "sources" / "mine.pdf")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["--workspace", str(root), "review-cv", "sources/mine.pdf",
                             "--save", "my-cv/readability.json"])
        self.assertEqual(code, 0)
        result = json.loads(out.getvalue())
        self.assertEqual(core.record(root / "sources" / "mine.pdf"), before)
        self.assertEqual(result["cv"], before)
        self.assertTrue({"contact_missing", "little_text"} <= ids(result["readability"]))
        self.assertIn("first person", " ".join(result["content"]))
        self.assertEqual(core.read(root / "my-cv" / "readability.json")["cv"], before)

    def test_non_pdf_is_refused_politely(self):
        root = Path(self.temp.name).resolve() / "ws"
        core.init(root, demo=True)
        (root / "sources" / "cv.docx").write_bytes(b"PK")
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(cli.main(["--workspace", str(root), "review-cv", "sources/cv.docx"]), 2)
        self.assertIn("export one", err.getvalue())


@unittest.skipUnless(pdf.export_check() == "ok", "PDF export unavailable here: " + pdf.export_check())
class GeneratedCvStillNeedsVisual(unittest.TestCase):
    def test_generated_pdf_without_visual_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, package, review, _ = fixture(Path(temp) / "private", with_cv=True)
            doc = core.read(review)
            doc["visual"] = {}
            core.atomic(review, doc)
            with self.assertRaisesRegex(ValueError, "Visual review must cover"):
                quality.gate(root, package, review, final=True)


if __name__ == "__main__":
    unittest.main()
