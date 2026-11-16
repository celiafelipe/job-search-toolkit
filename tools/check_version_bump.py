"""Fail if user-facing files changed since a base ref without a version bump.

Usage: python3 tools/check_version_bump.py [base-ref]   (default: origin/main)

Installed copies of the plugin only update when the version in plugin.json
changes, so every change that reaches users needs a new version.
"""
import json
import subprocess
import sys

SHIPPED = ("skills/", "toolkit/", "templates/", "assets/", ".claude-plugin/",
           ".codex-plugin/", ".agents/")
MANIFEST = ".claude-plugin/plugin.json"


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True,
                          text=True).stdout


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    merge_base = git("merge-base", base, "HEAD").strip()
    changed = [p for p in git("diff", "--name-only", merge_base).splitlines()
               if p.startswith(SHIPPED)]
    if not changed:
        print("No user-facing files changed; no version bump needed.")
        return 0
    old = json.loads(git("show", f"{merge_base}:{MANIFEST}"))["version"]
    with open(MANIFEST, encoding="utf-8") as f:
        new = json.load(f)["version"]
    if old == new:
        print(f"User-facing files changed but the version is still {old}:")
        for p in changed[:10]:
            print(f"  {p}")
        print("Raise version in .claude-plugin/plugin.json and "
              ".codex-plugin/plugin.json, and add it to CHANGELOG.md.")
        return 1
    print(f"Version bumped {old} -> {new}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
