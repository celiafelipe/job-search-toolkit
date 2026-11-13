"""Preflight the release tree. This is not a replacement for human review."""
import argparse
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TOP = {"README.md", "LICENSE", ".gitignore", "AGENTS.md", "CLAUDE.md", "CHANGELOG.md"}
FOLDERS = {"toolkit", "skills", "templates", "docs", "tests", "examples", "tools",
           ".claude-plugin", ".codex-plugin"}
TEXT_EXTENSIONS = {".py", ".md", ".json"}
EMAIL = re.compile(r"[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})", re.I)
URL = re.compile(r"https?://[^\s'\"><)`]+")
SENSITIVE = re.compile(
    r"(?:/Users/[A-Z0-9._-]+/|/home/[A-Z0-9._-]+/|[A-Z]:\\Users\\[A-Z0-9._-]+|"
    r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b|"
    r"-----BEGIN [A-Z ]*PRIVATE " r"KEY-----)", re.I)


def safe_domain(host):
    # schemas.openxmlformats.org is the fixed Word XML namespace, not a link anyone visits.
    return (host.lower() in {"example.org", "example.net", "example.com", "schemas.openxmlformats.org"}
            or host.lower().endswith(".example"))


def scan():
    if (ROOT / ".git").exists():
        result = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                                cwd=ROOT, check=True, capture_output=True)
        paths = [ROOT / name for name in set(result.stdout.decode().split("\0")) if name]
    else:
        paths = [p for p in ROOT.rglob("*") if "__pycache__" not in p.parts and (p.is_file() or p.is_symlink())]
    failures = []
    for p in sorted(paths):
        rel = p.relative_to(ROOT)
        if p.is_symlink() or not p.is_file():
            failures.append(f"{rel}: not an ordinary release file")
            continue
        if str(rel) not in TOP and not (len(rel.parts) >= 2 and rel.parts[0] in FOLDERS
                                        and rel.suffix in TEXT_EXTENSIONS):
            failures.append(f"{rel}: outside release file allowlist")
            continue
        try:
            contents = p.read_text(encoding="utf-8")
        except UnicodeError:
            failures.append(f"{rel}: binary file")
            continue
        if SENSITIVE.search(contents):
            failures.append(f"{rel}: possible personal path or secret")
        if any(not safe_domain(domain) for domain in EMAIL.findall(contents)):
            failures.append(f"{rel}: email outside a reserved example domain")
        if any((host := urlsplit(link.rstrip(".,")).hostname) and not safe_domain(host)
               for link in URL.findall(contents)):
            failures.append(f"{rel}: URL outside a reserved example domain")
    return len(paths), failures


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    count, failures = scan()
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Release preflight passed for {count} files. Review Git history and content independently.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
