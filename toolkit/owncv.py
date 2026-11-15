"""Advisory feedback on a CV the candidate designed themselves (Word, Canva, Pages...).

Reads the PDF the way a simple applicant tracking system (ATS) would, with local Poppler tools,
and reports what may get lost. Never changes the candidate's file and never blocks anything.
"""
import re
import subprocess

from . import lint, pdf
from .core import atomic, inside, now, read, record, require

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"(?<!\w)\+?\d[\d ()./-]{7,}\d(?!\w)")
RUN = re.compile(r"\S+(?: \S+)*")
YEAR = re.compile(r"\b(?:19|20)\d\d\b")
ICON_GLYPH = re.compile("[\ue000-\uf8ff]")
RATING = re.compile("(?:[\u25cf\u25cb\u25c9\u25ef\u2605\u2606\u25a0\u25a1\u25aa\u25ab\u25c6\u25c7\u2b24] ?){3,}")
SPACED = re.compile(r"(?<!\w)(?:[A-Za-z] ){4,}[A-Za-z](?!\w)")
EXPERIENCE_HEADING = re.compile(r"(?im)^\s*(?:professional |work |relevant |career )?"
                                r"(?:experience|employment|work history|career history|career)\b")
BULLET = re.compile("^\\s*(?:[-*\u2022\u25aa\u25cf\u2013\u25e6\u2023\u2043]|\\d+[.)])\\s+(.*\\S)")
VAGUE = re.compile(r"^(?:responsible for|worked on|helped|involved in|duties included|assisted|"
                   r"participated in|in charge of)\b", re.I)
METRIC = re.compile(r"(?:[$\u20ac\u00a3]\s?\d[\d.,]*\s?(?:k|m|bn|million|billion)?\b"
                    r"|\b\d[\d.,]*\s?(?:%|percent\b|x\b|k\b|m\b|bn\b|million\b|billion\b))", re.I)


def finding(key, severity, message):
    return {"id": key, "severity": severity, "message": message}


def column_lines(layout):
    """Lines whose text starts at the same point well inside the page: a second column or sidebar.

    Single-column CVs start text at the left margin; right-aligned dates are short and are skipped."""
    lines = [line.expandtabs() for line in layout.replace("\f", "\n").splitlines() if line.strip()]
    starts = []
    for line in lines:
        for run in RUN.finditer(line):
            words = run.group(0).split()
            if run.start() >= 15 and len(words) >= 3 and not (YEAR.search(run.group(0)) and len(words) <= 6):
                starts.append(run.start())
                break
    # The most lines whose inner text starts within a few characters of each other.
    best = max((sum(1 for other in starts if start <= other < start + 8) for start in starts), default=0)
    return best if best >= 6 and best >= 0.2 * len(lines) else 0


def readability(reading, layout, pages, images):
    """Machine-readability findings from the two text views; most serious first."""
    found = []
    words = len(reading.split())
    if words == 0:
        return [finding("no_text", "high",
                        "No text could be read at all. The PDF is probably a scan or a picture, so an "
                        "applicant tracking system sees an empty CV. Export it again from the original "
                        "design tool as a text PDF (not 'print to image' or a photo).")]
    if words < 50 * pages:
        found.append(finding("little_text", "high",
                             f"Only {words} words could be read on {pages} page(s). Parts of the CV are "
                             "probably images or outlined text that a tracking system cannot read."))
    garbled = reading.count("\ufffd") + reading.count("(cid:")
    if garbled >= 5:
        found.append(finding("garbled_text", "high",
                             f"{garbled} characters come out as junk when the text is copied out. The fonts "
                             "were embedded without a text map; re-export with a standard font."))
    emails = list(EMAIL.finditer(reading))
    if not emails:
        found.append(finding("contact_missing", "high",
                             "No email address appears in the readable text. If it sits in a header, footer, "
                             "image or icon, a tracking system may not see it. Put it as plain text near "
                             "the top."))
    elif emails[0].start() > len(reading) * 0.3:
        found.append(finding("contact_late", "low",
                             "The email address is read far down the text, not near the top. Tracking "
                             "systems usually look for contact details first."))
    if not PHONE.search(reading):
        found.append(finding("phone_missing", "low",
                             "No phone number found in the readable text. Fine if you leave it out on purpose."))
    columns = column_lines(layout)
    if columns:
        found.append(finding("columns", "medium",
                             f"The layout has text side by side in columns (about {columns} lines). Some "
                             "tracking systems read straight across the page and mix the columns together. "
                             "A single column is safest; if you keep a sidebar, keep only short extras there "
                             "(skills, languages), never your experience."))
    if not EXPERIENCE_HEADING.search(reading):
        found.append(finding("no_experience_heading", "medium",
                             "No heading such as 'Experience' or 'Work history' was found. Tracking systems "
                             "use standard headings to find each section; avoid creative names or headings "
                             "drawn as images."))
    icons = len(ICON_GLYPH.findall(reading))
    if icons >= 3:
        found.append(finding("icon_glyphs", "medium",
                             f"{icons} symbols from an icon font (often phone, email or location icons) read "
                             "as junk characters. Harmless only if the real details are plain text beside "
                             "them."))
    if RATING.search(reading):
        found.append(finding("rating_symbols", "medium",
                             "Skill levels shown as dots, stars or bars read as meaningless symbols. Write "
                             "the level in words ('fluent', 'advanced') or leave it out."))
    if SPACED.search(reading):
        found.append(finding("spaced_letters", "low",
                             "Letter-spaced text such as 'E X P E R I E N C E' reads as separate letters, so "
                             "the heading may not be recognised. Use normal spacing."))
    if images:
        found.append(finding("images", "medium" if images >= 5 else "low",
                             f"The PDF contains {images} image(s). Anything inside an image (a photo, logos, "
                             "skill bars, a name or contact line drawn as graphics) is invisible to a "
                             "tracking system, and some employers prefer no photo."))
    if pages > 3:
        found.append(finding("long", "low", f"{pages} pages. Most CVs work best at two, three for executives."))
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(found, key=lambda item: order[item["severity"]])


def content(reading, experience_text, name="CV"):
    """Advisory content warnings: the shared CV rules plus checks that suit a finished design."""
    warnings = lint.cv_warnings(reading, name, markdown=False)
    bullets = [m[1] for m in map(BULLET.match, reading.splitlines()) if m]
    if len(bullets) >= 5:
        numbered = sum(1 for b in bullets if re.search(r"\d", b))
        if numbered < 0.3 * len(bullets):
            warnings.append(f"{name}: only {numbered} of {len(bullets)} bullets have a number (size, money, "
                            "time, percentage); results with numbers are easier to believe")
        vague = [b for b in bullets if VAGUE.match(b)]
        if vague:
            warnings.append(f"{name}: {len(vague)} bullet(s) describe duties rather than results, such as "
                            f"\"{vague[0][:60]}\"; start with what changed because of you")
    if experience_text.strip():
        known = re.sub(r"\s", "", experience_text).casefold()
        unbacked = sorted({m.group(0).strip() for m in METRIC.finditer(reading)
                           if re.sub(r"\s", "", m.group(0)).casefold() not in known})
        if unbacked:
            warnings.append(f"{name}: these figures are not in the experience files yet, so they can't be "
                            f"checked or reused: {', '.join(unbacked[:10])}; confirm each one with the candidate")
    return warnings


def experience_text(root):
    folder = root / "experience"
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted(folder.glob("*.md"))
                     if p.name not in ("INDEX.md", "_role-template.md"))


def count_images(path):
    tool = pdf.find_tool("pdfimages")
    if not tool:
        return None
    listing = pdf.run([tool, "-list", str(path)])
    return max(0, len([line for line in listing.splitlines() if line.strip()]) - 2)


def review(root, source, save=None):
    """Read the candidate's own PDF like an ATS would. Advisory: returns findings, never edits the file."""
    path = inside(root, source)
    require(path.suffix.lower() == ".pdf" and path.read_bytes()[:5] == b"%PDF-",
            "Bring-your-own CV feedback needs the PDF the candidate would upload; ask them to export one")
    tool = pdf.find_tool("pdftotext")
    require(tool, "Reading a PDF needs Poppler; run doctor for the install command")
    before = record(path)
    try:
        views = pdf.extract(path, {"pdftotext": tool})
    except ValueError as exc:
        raise ValueError(f"Could not read text from this PDF ({exc}). It may be password-protected; "
                         "ask for an unprotected export") from None
    pages = max(1, views["reading"].rstrip("\f").count("\f") + 1)
    try:
        images = count_images(path)
    except (ValueError, OSError, subprocess.SubprocessError):
        images = None
    require(record(path) == before, "The CV changed while it was being read; try again")
    report = {
        "schema": 1, "kind": "candidate_cv_check", "cv": before, "checked_at": now(),
        "pages": pages, "words": len(views["reading"].split()), "images": images,
        "readability": readability(views["reading"], views["layout"], pages, images or 0),
        "content": content(views["reading"], experience_text(root), path.name),
        "advisory": "Suggestions only. The candidate's file was not changed; they decide what to edit in "
                    "their own design tool.",
    }
    if save:
        target = inside(root, save, file=False)
        require(target.suffix == ".json" and target != path, "Save the report as a separate .json file")
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic(target, report)
        report["saved"] = str(target)
    return report


def verify(root, report_path, attachment):
    """Bind a candidate-supplied PDF to a readability check of exactly those bytes. Findings stay advisory."""
    report = read(report_path)
    require(report.get("schema") == 1 and report.get("kind") == "candidate_cv_check",
            "Candidate CV needs a saved review-cv report")
    require(report["cv"]["sha256"] == record(attachment)["sha256"],
            "The readability check is for a different version of the candidate's CV; run review-cv again")
    require(attachment.read_bytes()[:5] == b"%PDF-", "Candidate CV is not a PDF")
    return report
