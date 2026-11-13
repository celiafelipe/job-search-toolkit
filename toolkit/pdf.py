"""Canonical local Markdown-to-PDF build and extraction evidence."""
from html import escape
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unicodedata

from .core import atomic, checked, inside, read, record, require

CSS = """
@page { size: A4; margin: 16mm 18mm; }
body { color: #182634; font: 11pt/1.37 Arial, "Liberation Sans", Helvetica, "DejaVu Sans", sans-serif; overflow-wrap: anywhere; }
h1, h2, h3 { margin: .65em 0 .22em; break-after: avoid; }
h1 { font-size: 24pt; margin-top: 0; }
h2 { font-size: 14pt; border-bottom: 1px solid #aab9c1; color: #203b4a; }
h3 { font-size: 11.5pt; }
strong { font-weight: 700; color: #0f1c27; }
p, ul { margin: .2em 0 .54em; orphans: 3; widows: 3; }
p { break-inside: avoid; }
ul { padding-left: 1.25em; }
li { margin: .12em 0; break-inside: avoid; }
"""


def tools():
    browser = os.environ.get("JOBKIT_CHROME")
    if not browser:
        browser = next((p for n in ("chrome-headless-shell", "google-chrome", "google-chrome-stable",
                                    "chromium", "chromium-browser")
                        if (p := shutil.which(n))), None)
    if not browser:
        candidate = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        browser = str(candidate) if candidate.is_file() else None
    if browser:
        browser = shutil.which(browser)
    return {"browser": browser, **{name: shutil.which(name)
            for name in ("pdfinfo", "pdftotext", "pdftoppm")}}


def install_hints(runtime):
    """Plain-language fixes an agent can offer (with the user's permission) for missing tools."""
    hints = []
    if not runtime["browser"]:
        hints.append("Install a browser for PDF export: macOS, Google Chrome (google.com/chrome); "
                     "Debian/Ubuntu 'sudo apt-get install chromium'; Fedora 'sudo dnf install chromium'. "
                     "On servers, containers or WSL, the lighter headless build is more reliable: "
                     "'npx @puppeteer/browsers install chrome-headless-shell@stable', then set JOBKIT_CHROME "
                     "to the chrome-headless-shell file it reports.")
    if not all(runtime[name] for name in ("pdfinfo", "pdftotext", "pdftoppm")):
        hints.append("Install Poppler: macOS 'brew install poppler'; Debian/Ubuntu "
                     "'sudo apt-get install poppler-utils'; Fedora 'sudo dnf install poppler-utils'.")
    return hints


def run(command, timeout=90):
    name = Path(command[0]).name
    try:
        result = subprocess.run(command, check=False, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ValueError(
            f"{name} did not finish within {timeout}s. On Linux this usually means the full browser "
            "cannot start headless here (common in containers or without a desktop session). Fix: install "
            "Chrome's headless build ('npx @puppeteer/browsers install chrome-headless-shell@stable') and set "
            "JOBKIT_CHROME to it, or run from a normal desktop session.") from None
    if result.returncode != 0:
        detail = [line for line in result.stderr.decode("utf-8", errors="replace").splitlines() if line.strip()]
        raise ValueError(f"{name} failed (exit {result.returncode})"
                         + (": " + " | ".join(detail[-3:]) if detail else ""))
    return result.stdout.decode("utf-8", errors="replace")


def chrome(browser, profile, pdf, page):
    """Headless print with networking blocked: the page is local and needs nothing from the internet."""
    command = [browser, "--headless", "--no-first-run", "--no-default-browser-check",
               "--disable-background-networking", "--disable-component-update", "--disable-sync",
               "--disable-default-apps", "--no-pings", "--disable-domain-reliability",
               "--host-resolver-rules=MAP * ~NOTFOUND", "--disable-gpu", "--disable-dev-shm-usage",
               "--no-pdf-header-footer", f"--user-data-dir={profile}", f"--print-to-pdf={pdf}"]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        # Chrome refuses to start as root with its sandbox (containers). The page is our own escaped HTML.
        command.append("--no-sandbox")
    return command + [page]


_EXPORT_CHECK = None


def export_check():
    """Cached result of one real test export ("ok" or the reason it failed)."""
    global _EXPORT_CHECK
    if _EXPORT_CHECK is None:
        _EXPORT_CHECK = probe(tools())
    return _EXPORT_CHECK


def probe(runtime, timeout=45):
    """Actually print a tiny page, so doctor reports whether PDF export works, not just whether tools exist."""
    if not all(runtime.values()):
        return "PDF tools missing"
    with tempfile.TemporaryDirectory(prefix="jobkit-probe-") as temp:
        temp = Path(temp)
        page, pdf = temp / "probe.html", temp / "probe.pdf"
        page.write_text("<!doctype html><meta charset=utf-8><p>jobkit probe</p>", encoding="utf-8")
        try:
            run(chrome(runtime["browser"], temp / "profile", pdf, page.as_uri()), timeout=timeout)
            require(pdf.is_file(), "Browser did not create a PDF")
            require("jobkit probe" in run([runtime["pdftotext"], str(pdf), "-"]), "PDF text not readable")
        except (ValueError, OSError) as exc:
            return str(exc)
    return "ok"


BULLET = re.compile(r"^(?:[-*]\s+|[\u2022\u25aa\u25cf]\s*)")
UNSUPPORTED = (
    (re.compile(r"^#{4,}"), "headings deeper than ### are not supported"),
    (re.compile(r"^\d+[.)]\s"), "numbered lists are not supported; use '- ' bullets"),
    (re.compile(r"^(>|\|)"), "quotes and tables are not supported"),
    (re.compile(r"^(```|!\[|<)"), "code blocks, images and HTML are not supported"),
    (re.compile(r"^(-{3,}|\*{3,}|_{3,})$"), "horizontal rules are not supported"),
)


def check_inline(value, number):
    require(value.count("**") % 2 == 0, f"Line {number}: close every **bold** span: {value[:70]}")
    rest = plain(value)
    require("](" not in rest, f"Line {number}: links are not supported; write the URL as plain text: {value[:70]}")
    require(not re.search(r"__|`|\*", rest),
            f"Line {number}: only **bold** is supported inline (no italics or code): {value[:70]}")


def parse(markdown):
    """Constrained syntax: headings 1-3, paragraphs, bullet lists (- * or •) and **bold**.

    Errors name the source line so a person or agent can fix it directly."""
    blocks, paragraph, bullets = [], [], []

    def flush(kind):
        if kind == "p" and paragraph:
            blocks.append(("p", [" ".join(paragraph)]))
            paragraph.clear()
        if kind == "ul" and bullets:
            blocks.append(("ul", list(bullets)))
            bullets.clear()

    for number, raw in enumerate([*markdown.splitlines(), ""], 1):
        line = raw.strip()
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        for pattern, reason in UNSUPPORTED:
            require(heading or not pattern.match(line), f"Line {number}: {reason}: {line[:70]}")
        bullet = None if heading or re.match(r"^\*\*", line) else BULLET.match(line)
        if not line or heading:
            flush("p")
            flush("ul")
            if heading:
                check_inline(heading[2], number)
                blocks.append((f"h{len(heading[1])}", [heading[2]]))
        elif bullet:
            flush("p")
            item = line[bullet.end():].strip()
            require(item, f"Line {number}: empty bullet")
            check_inline(item, number)
            bullets.append(item)
        else:
            flush("ul")
            check_inline(line, number)
            paragraph.append(line)
    require(blocks, "Source is empty")
    return blocks


def plain(value):
    """Text as it reads in the PDF: bold markers removed."""
    return value.replace("**", "")


def inline(value):
    """Escape text and render balanced **bold** spans."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escape(value))


PAPER = {"a4": "A4", "letter": "letter"}


def html(blocks, paper="a4"):
    chunks = []
    for tag, values in blocks:
        body = "".join(f"<li>{inline(v)}</li>" for v in values) if tag == "ul" else inline(values[0])
        chunks.append(f"<{tag}>{body}</{tag}>")
    title = next((plain(values[0]) for tag, values in blocks if tag == "h1"), "Document")
    return ('<!doctype html><meta charset="utf-8"><title>' + escape(title) + '</title><style>' + CSS.replace("size: A4", "size: " + PAPER[paper])
            + '</style>' + '\n'.join(chunks))


def normalized(value):
    value = unicodedata.normalize("NFKC", value).replace("\u00ad", "").casefold()
    # Text extractors may drop or keep a hyphen where the PDF wrapped a line ("on-call" -> "oncall"
    # or "on- call"), so compare hyphenated words without their hyphens.
    value = re.sub(r"\s*[-\u2010\u2011\u2012\u2013]\s*", "", value)
    return " ".join(value.split())


def analyze(blocks, extracted):
    passages = [normalized(plain(p)) for _, values in blocks for p in values]
    errors, warnings = [], []
    for mode, contents in extracted.items():
        contents = normalized(contents)
        cursor = 0
        out_of_order = []
        for index, passage in enumerate(passages, 1):
            pos = contents.find(passage, cursor)
            if pos < 0:
                if passage not in contents:
                    errors.append(f"{mode}:missing:{index}")
                else:
                    out_of_order.append(index)
            else:
                cursor = pos + len(passage)
        for index in out_of_order:
            warnings.append(f"{mode}:order:{index}")
    return errors, warnings


def extract(pdf, runtime):
    return {mode: run([runtime["pdftotext"], *flag, "-enc", "UTF-8", str(pdf), "-"])
            for mode, flag in (("reading", []), ("layout", ["-layout"]))}


def page_count(pdf, runtime):
    match = re.search(r"(?m)^Pages:\s*(\d+)", run([runtime["pdfinfo"], str(pdf)]))
    require(match and int(match[1]) > 0, "Could not establish PDF page count")
    return int(match[1])


def check_source(root, source):
    """Validate a CV or letter against the supported Markdown subset without building a PDF."""
    blocks = parse(inside(root, source).read_text(encoding="utf-8"))
    return {"format": "ok", "headings": [plain(v[0]) for t, v in blocks if t in ("h1", "h2", "h3")],
            "blocks": len(blocks)}


def build(root, source, output, kind, paper="a4"):
    source = inside(root, source)
    output = inside(root, output, file=False)
    require(not output.exists() and output.parent.is_dir(), "Use a new build directory with an existing parent")
    runtime = tools()
    require(all(runtime.values()), "PDF tools unavailable; run doctor")
    source_before = record(source)
    blocks = parse(source.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=".pdf-") as temp:
        stage = Path(temp)
        target = stage / "build"
        target.mkdir(mode=0o700)
        source_html = target / "document.html"
        source_html.write_text(html(blocks, paper), encoding="utf-8")
        pdf = target / "document.pdf"
        run(chrome(runtime["browser"], stage / "browser", pdf, source_html.as_uri()))
        require(pdf.is_file(), "Browser did not create PDF")
        extracted = extract(pdf, runtime)
        errors, warnings = analyze(blocks, extracted)
        if errors:
            texts = [plain(v) for _, values in blocks for v in values]
            missing = sorted({int(code.rsplit(":", 1)[1]) for code in errors})
            raise ValueError("Some text could not be read back from the PDF; reword or simplify these passages: "
                             + "; ".join(f"#{i} \"{texts[i - 1][:70]}\"" for i in missing))
        for mode, contents in extracted.items():
            (target / f"{mode}.txt").write_text(contents, encoding="utf-8")
        pages = page_count(pdf, runtime)
        run([runtime["pdftoppm"], "-r", "120", "-png", str(pdf), str(target / "page")])
        images = sorted(target.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
        require(len(images) == pages, "Incomplete page rendering")
        require(record(source) == source_before, "Source changed during build")
        files = {f.name: {"path": str(output / f.name), "sha256": record(f)["sha256"]}
                 for f in target.iterdir() if f.is_file()}
        receipt = {"schema": 1, "kind": kind, "source": source_before,
                   "builder_sha256": record(Path(__file__))["sha256"],
                   "pages": [p.name for p in images], "files": files,
                   "recovery_warnings": warnings, "word_count": sum(len(v.split())
                        for _, values in blocks for v in values)}
        atomic(target / "build.json", receipt)
        require(not output.exists(), "Build destination was created by another process")
        target.rename(output)
    return {"build": str(output / "build.json"), "pages": pages, "recovery_warnings": warnings}


def verify(root, build_path, attachment, kind):
    receipt = read(build_path)
    require(receipt["schema"] == 1 and receipt["kind"] == kind, "Wrong PDF build type")
    require(receipt["builder_sha256"] == record(Path(__file__))["sha256"],
            "PDF builder changed: rebuild and review")
    source = checked(root, receipt["source"])
    files = {name: checked(root, item) for name, item in receipt["files"].items()}
    require(files["document.html"].read_text(encoding="utf-8") ==
            html(parse(source.read_text(encoding="utf-8"))), "Build HTML differs from current source")
    require(record(attachment)["sha256"] == receipt["files"]["document.pdf"]["sha256"],
            "Outgoing PDF differs from checked build")
    runtime = tools()
    require(runtime["pdfinfo"] and runtime["pdftotext"], "Missing PDF verification tools")
    fresh = extract(attachment, runtime)
    require(all((files[f"{key}.txt"].read_text(encoding="utf-8") == value)
                for key, value in fresh.items()), "PDF extraction differs from recorded views")
    errors, warnings = analyze(parse(source.read_text(encoding="utf-8")), fresh)
    require(not errors and warnings == receipt["recovery_warnings"], "PDF recovery evidence changed")
    pages = receipt["pages"]
    require(page_count(attachment, runtime) == len(set(pages)) == len(pages)
            and all(re.fullmatch(r"page-\d+\.png", name) and name in files for name in pages),
            "Missing or invalid page renders")
    return receipt
