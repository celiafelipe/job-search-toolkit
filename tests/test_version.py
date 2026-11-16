"""The plugin version must match across hosts and appear in the changelog."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent


def version_of(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))["version"]


class VersionTests(unittest.TestCase):
    def test_claude_and_codex_versions_match(self):
        self.assertEqual(
            version_of(".claude-plugin/plugin.json"),
            version_of(".codex-plugin/plugin.json"),
        )

    def test_changelog_lists_current_version(self):
        version = version_of(".claude-plugin/plugin.json")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## {version} ", changelog)


if __name__ == "__main__":
    unittest.main()
