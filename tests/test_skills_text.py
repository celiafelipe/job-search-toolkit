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


class ScreenRecordTests(unittest.TestCase):
    def test_registered_roles_always_save_the_current_screen(self):
        text = read("skills/job-screen/SKILL.md")
        section = text[text.index("## Record"):]
        self.assertIn("already registered, always save", section)
        # The offer to save applies only to roles that aren't registered yet.
        self.assertLess(section.index("isn't registered yet"), section.index("offer once"))


if __name__ == "__main__":
    unittest.main()
