import json
import tempfile
from pathlib import Path
import unittest

from toolkit import core, cvtheme, lint, pdf

CV = """# Avery Example

Product Leader | Platforms and marketplaces

Lisbon, Portugal | avery@example.org | example.org/avery

## Executive summary

Product leader with ten years building marketplaces.

## Key achievements

- **Grew revenue 40% in two years** across three markets.

## Experience

### Head of Product | Orchard Co | Jan 2020 – Present

Grocery marketplace, 200 people.

- **Raised conversion 12%** with a rebuilt checkout.
- Hired and coached four product managers.

### Product Manager | Ledgerline | 2015 – 2019

- Launched the partner API.

## Skills

Product strategy, Marketplaces, Pricing, Org design, Discovery

## Education

University of Example | MSc Economics | 2014 | Lisbon, Portugal

Example College | BSc Mathematics | 2012 | Porto, Portugal

## Languages

Portuguese (native), English (fluent), French: basic
"""


class Rendering(unittest.TestCase):
    def render(self, template):
        return pdf.html(pdf.parse(CV), "a4", template, "teal")

    def test_every_template_adds_structure_without_changing_words(self):
        for template in cvtheme.THEMES:
            page = self.render(template)
            self.assertIn(f'class="theme-{template}"', page)
            self.assertIn("--accent: #0e5f63", page)
            self.assertIn('<p class="headline">', page)
            self.assertIn('<p class="contact">', page)
            self.assertEqual(page.count('<div class="role">'), 2)
            self.assertIn('<span class="dates">Jan 2020 – Present</span>', page)
            self.assertEqual(page.count('<div class="edu-item">'), 2)
            tags = page[page.index('class="tags"'):]
            self.assertEqual(tags[:tags.index("</ul>")].count("<li>"), 5)
            self.assertIn('<span class="lang">French</span> <span class="lvl">basic</span>', page)
            self.assertNotIn("duo", page)

    def test_classic_keeps_the_original_page(self):
        self.assertEqual(pdf.html(pdf.parse(CV)), pdf.html(pdf.parse(CV), "a4", "classic", "plum"))
        self.assertNotIn("<section", pdf.html(pdf.parse(CV)))

    def test_letter_keeps_its_paragraphs_out_of_the_header(self):
        letter = "# Avery Example\n\nLisbon | avery@example.org\n\nDear team,\n\nA short letter.\n"
        page = pdf.html(pdf.parse(letter), "a4", "banner", None, "letter")
        header = page[page.index("<header>"):page.index("</header>")]
        self.assertIn("avery@example.org", header)
        self.assertNotIn("Dear team", header)
        self.assertIn('<div class="letter"><p>Dear team,</p>', page)

    def test_accent_names_and_colours(self):
        self.assertEqual(cvtheme.accent_colour("Forest"), "#2e5339")
        self.assertEqual(cvtheme.accent_colour("#AABBCC"), "#aabbcc")
        self.assertEqual(cvtheme.accent_colour(None), cvtheme.ACCENTS[cvtheme.DEFAULT_ACCENT])
        with self.assertRaises(ValueError):
            cvtheme.accent_colour("red; background: url(x)")
        with self.assertRaises(ValueError):
            pdf.html(pdf.parse(CV), "a4", "fancy")

    def test_read_back_ignores_letter_spacing_and_separators(self):
        blocks = pdf.parse("## Education\n\nUniversity of Example | MSc Economics | 2014\n\n"
                           "## Languages\n\nEnglish (native), French (fluent)\n")
        extracted = "E D U C AT I O N\nUniversity of Example\nMSc Economics\n2014\nLANGUAGES\nEnglish native French fluent"
        self.assertEqual(pdf.analyze(blocks, {"reading": extracted}), ([], []))
        self.assertEqual(pdf.analyze(blocks, {"reading": "EDUCATION LANGUAGES"})[0][0], "reading:missing:2")


class SkillsLimit(unittest.TestCase):
    def test_more_than_five_skills_warns(self):
        warnings = lint.cv_warnings("# A\n\nx\n\n## Skills\n\na, b, c, d, e, f\n")
        self.assertTrue(any("6 skills" in w for w in warnings))
        self.assertFalse(lint.cv_warnings("# A\n\nx\n\n## Skills\n\n- a\n- b\n- c\n- d\n- e\n"))

    def test_combined_skills_and_languages_section_warns(self):
        warnings = lint.cv_warnings("# A\n\nx\n\n## Skills and languages\n\na, English\n")
        self.assertTrue(any("own '## Languages' section" in w for w in warnings))


@unittest.skipUnless(pdf.export_check() == "ok", "PDF export unavailable: " + str(pdf.export_check()))
class RealBuilds(unittest.TestCase):
    def test_each_template_builds_reads_back_and_verifies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "ws"
            core.init(root, demo=True)
            (root / "cv.md").write_text(CV, encoding="utf-8")
            for template in cvtheme.THEMES:
                result = pdf.build(root, "cv.md", f"build-{template}", "cv", template=template, accent="plum")
                self.assertEqual(result["template"], template)
                receipt = pdf.verify(root, Path(result["build"]), root / f"build-{template}" / "document.pdf", "cv")
                self.assertEqual((receipt["template"], receipt["accent"]), (template, "#5b3f86"))

    def test_workspace_config_sets_the_default_look(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "ws"
            core.init(root, demo=True)
            self.assertEqual(pdf.style(root), ("editorial", "#1f3a5f"))
            (root / "cv-style.json").write_text(json.dumps({"template": "banner", "accent": "teal"}),
                                                encoding="utf-8")
            self.assertEqual(pdf.style(root), ("banner", "#0e5f63"))
            self.assertEqual(pdf.style(root, "gutter", "#123456"), ("gutter", "#123456"))


if __name__ == "__main__":
    unittest.main()
