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
body { color: #182634; font: 11pt/1.37 Arial, sans-serif; overflow-wrap: anywhere; }
h1, h2, h3 { margin: .65em 0 .22em; break-after: avoid; }
h1 { font-size: 24pt; margin-top: 0; }
h2 { font-size: 14pt; border-bottom: 1px solid #aab9c1; color: #203b4a; }
h3 { font-size: 11.5pt; }
p, ul { margin: .2em 0 .54em; orphans: 2; widows: 2; }
ul { padding-left: 1.25em; }
li { margin: .12em 0; break-inside: avoid; }
"""


def tools():
    browser = os.environ.get("JOBKIT_CHROME")
    if not browser:
        browser = next((p for n in ("google-chrome", "chromium", "chromium-browser")
                        if (p := shutil.which(n))), None)
    if not browser:
        candidate = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        browser = str(candidate) if candidate.is_file() else None
    if browser:
        browser = shutil.which(browser)
    return {"browser": browser, **{name: shutil.which(name)
            for name in ("pdfinfo", "pdftotext", "pdftoppm")}}


def run(command):
    result = subprocess.run(command, check=False, capture_output=True, timeout=90)
    require(result.returncode == 0, f"{Path(command[0]).name} failed (exit {result.returncode})")
    return result.stdout.decode("utf-8", errors="replace")


def parse(markdown):
    """Constrained syntax: headings 1–3, paragraphs, and contiguous dash lists."""
    blocks, paragraph, bullets = [], [], []
    for line in [*markdown.splitlines(), ""]:
        line = line.strip()
        match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if not line or match or line.startswith("- "):
            if paragraph:
                blocks.append(("p", [" ".join(paragraph)]))
                paragraph.clear()
            if not line.startswith("- ") and bullets:
                blocks.append(("ul", list(bullets)))
                bullets.clear()
            if match:
                blocks.append((f"h{len(match[1])}", [match[2]]))
            if line.startswith("- "):
                bullets.append(line[2:])
        else:
            if bullets:
                blocks.append(("ul", list(bullets)))
                bullets.clear()
            require(not re.match(r"^(#|[>|*]|\d+\.\s|```|!\[|---|<)", line),
                    "Unsupported Markdown; use headings, paragraphs and dash lists")
            paragraph.append(line)
    require(blocks, "Source is empty")
    require(all(not re.search(r"\*\*|__|`|\]\(", v) for _, values in blocks for v in values),
            "Use literal text rather than inline Markdown or links")
    return blocks


def html(blocks):
    chunks = []
    for tag, values in blocks:
        body = "".join(f"<li>{escape(v)}</li>" for v in values) if tag == "ul" else escape(values[0])
        chunks.append(f"<{tag}>{body}</{tag}>")
    return '<!doctype html><meta charset="utf-8"><style>' + CSS + '</style>' + '\n'.join(chunks)


def normalized(value):
    value = unicodedata.normalize("NFKC", value).replace("\u00ad", "").casefold()
    return " ".join(value.split())


def analyze(blocks, extracted):
    passages = [normalized(p) for _, values in blocks for p in values]
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


def build(root, source, output, kind):
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
        source_html.write_text(html(blocks), encoding="utf-8")
        pdf = target / "document.pdf"
        run([runtime["browser"], "--headless", "--no-first-run",
             "--no-default-browser-check", "--disable-background-networking",
             "--no-pdf-header-footer", f"--user-data-dir={stage / 'browser'}",
             f"--print-to-pdf={pdf}", source_html.as_uri()])
        require(pdf.is_file(), "Browser did not create PDF")
        extracted = extract(pdf, runtime)
        errors, warnings = analyze(blocks, extracted)
        require(not errors, "PDF content not recovered: " + ", ".join(errors))
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
