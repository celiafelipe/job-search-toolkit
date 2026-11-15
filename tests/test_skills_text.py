"""Skill text must tell the candidate that review and submission exist."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


class DiscoverabilityTests(unittest.TestCase):
    def test_starter_mentions_review_and_apply(self):
        text = read("skills/job-starter/SKILL.md")
        self.assertIn("job-apply", text)
        self.assertIn("job-review", text)
        self.assertIn("Application handling", text)

    def test_prepare_hand_off_offers_both(self):
        text = read("skills/job-prepare/SKILL.md")
        section = text[text.index("## Hand off"):]
        self.assertIn("job-review", section)
        self.assertIn("job-apply", section)

    def test_profile_template_has_application_handling(self):
        self.assertIn("Application handling", read("templates/profile.md"))


if __name__ == "__main__":
    unittest.main()
