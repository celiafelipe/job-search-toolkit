"""Styled CV templates: the same constrained Markdown, laid out as semantic HTML plus a theme stylesheet.

A template only restyles. Every word of the source appears once, in source order, so the PDF text
read-back check still applies. The structure added here (header, sections, roles, education items,
skill and language items) is derived from headings and `|` / comma separators the source already has."""
from html import escape
from pathlib import Path
import re

THEMES = ("editorial", "gutter", "banner")
DEFAULT_THEME = "editorial"
ACCENTS = {"navy": "#1f3a5f", "teal": "#0e5f63", "burgundy": "#7a2e3b", "forest": "#2e5339",
           "plum": "#5b3f86", "graphite": "#2b2b2b"}
DEFAULT_ACCENT = "navy"
STYLES = Path(__file__).with_name("themes")
MAX_SKILLS = 5
LETTER_CSS = """
.letter { font-size: 10.6pt; line-height: 1.55; }
.letter p { margin: 0 0 3.2mm; }
.letter ul { margin: 0 0 3.2mm 5mm; list-style: disc; }
.theme-gutter .letter { margin-left: 46mm; padding-top: 4mm; }
.theme-banner .letter { padding: 6mm 16mm 0; }
.theme-editorial .letter { padding-top: 6mm; }
"""

SECTION_KINDS = (
    ("languages", re.compile(r"^languages?$", re.I)),
    ("skills", re.compile(r"skill|expertise|competenc", re.I)),
    ("summary", re.compile(r"summary|profile|about", re.I)),
    ("achievements", re.compile(r"achievement|highlight", re.I)),
    ("experience", re.compile(r"experience|employment|career", re.I)),
    ("education", re.compile(r"education|qualification|degree", re.I)),
)
DATES = re.compile(r"\d")
LANGUAGE = re.compile(r"^(?P<lang>[^(:–-]+?)\s*(?:\((?P<a>[^)]+)\)|[:–-]\s*(?P<b>.+))$")


def accent_colour(value):
    """A named accent or a #rrggbb colour."""
    value = (value or DEFAULT_ACCENT).strip().lower()
    colour = ACCENTS.get(value, value)
    if not re.fullmatch(r"#[0-9a-f]{6}", colour):
        raise ValueError(f"Unknown accent '{value}': use one of {', '.join(ACCENTS)} or a colour like #1f3a5f")
    return colour


def section_kind(title):
    return next((kind for kind, pattern in SECTION_KINDS if pattern.search(title)), "other")


def items(values):
    """Skill or language items from a bullet list, or from comma- or semicolon-separated paragraphs."""
    found = []
    for value in values:
        found.extend(part.strip() for part in re.split(r"\s*[,;·]\s*", value) if part.strip())
    return found


def render(blocks, inline, plain, theme, accent, paper, kind="cv"):
    require_theme(theme)
    out, i = [], 0
    title = next((plain(values[0]) for tag, values in blocks if tag == "h1"), "Document")

    # Header: the name, then any paragraphs before the first section. The last one is the contact line.
    header = []
    while i < len(blocks) and blocks[i][0] != "h2":
        # A letter's header is only the name and the contact line under it; the rest is the letter.
        if kind == "letter" and len(header) == 2:
            break
        header.append(blocks[i])
        i += 1
    if header:
        out.append("<header>")
        last = max((n for n, (tag, _) in enumerate(header) if tag == "p"), default=None)
        for n, (tag, values) in enumerate(header):
            if tag == "h1":
                out.append(f"<h1>{inline(values[0])}</h1>")
            elif tag == "p":
                cls = "contact" if n == last else "headline"
                if cls == "contact":
                    parts = [inline(part) for part in re.split(r"\s+\|\s+", values[0])]
                    body = '<span class="sep"> · </span>'.join(f'<span class="item">{p}</span>' for p in parts)
                else:
                    body = inline(values[0])
                out.append(f'<p class="{cls}">{body}</p>')
            else:
                out.append(block(tag, values, inline))
        out.append("</header>")

    if kind == "letter":
        out.append('<div class="letter">' + "".join(block(t, v, inline) for t, v in blocks[i:]) + "</div>")
        i = len(blocks)
    sections = []
    while i < len(blocks):
        heading = blocks[i][1][0]
        i += 1
        body = []
        while i < len(blocks) and blocks[i][0] != "h2":
            body.append(blocks[i])
            i += 1
        kind = section_kind(plain(heading))
        sections.append((kind, f'<section class="sec sec-{kind}"><h2>{inline(heading)}</h2>'
                               + section_body(kind, body, inline) + "</section>"))

    # One column only: side-by-side sections get interleaved by text extraction and by ATS parsers.
    out.extend(html for _, html in sections)

    css = (STYLES / "base.css").read_text(encoding="utf-8") + (STYLES / f"{theme}.css").read_text(encoding="utf-8")
    css = css.replace("size: A4", "size: " + paper)
    if kind == "letter":
        css += LETTER_CSS
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><title>' + escape(title) + "</title><style>"
            + f":root {{ --accent: {accent}; }}\n" + css + "</style>"
            + f'<body class="theme-{theme}"><article class="cv">' + "\n".join(out) + "</article></body></html>")


def require_theme(theme):
    if theme not in THEMES:
        raise ValueError(f"Unknown CV template '{theme}': use one of {', '.join(THEMES)} or classic")


def block(tag, values, inline, cls=None):
    attr = f' class="{cls}"' if cls else ""
    if tag == "ul":
        return f"<ul{attr}>" + "".join(f"<li>{inline(v)}</li>" for v in values) + "</ul>"
    return f"<{tag}{attr}>{inline(values[0])}</{tag}>"


def role_heading(value, inline):
    parts = re.split(r"\s+\|\s+", value)
    if len(parts) < 2:
        return f'<h3><span class="title">{inline(value)}</span></h3>'
    dates = parts.pop() if len(parts) >= 3 or DATES.search(parts[-1]) else None
    html = f'<span class="title">{inline(parts[0])}</span>'
    if len(parts) > 1:
        html += f'<span class="sep"> | </span><span class="org">{inline(" | ".join(parts[1:]))}</span>'
    if dates:
        # Dates stay inline: right-aligned dates read back as a separate column in plain-text extraction.
        html += f'<span class="sep"> | </span><span class="dates">{inline(dates)}</span>'
    return f"<h3>{html}</h3>"


def section_body(kind, body, inline):
    if kind in ("skills", "languages") and body and all(tag in ("p", "ul") for tag, _ in body):
        values = items(v for _, vals in body for v in vals)
        if kind == "skills":
            # Real spaces between items: text extraction then sees separate words, not separate columns.
            return '<ul class="tags">' + " ".join(f"<li>{inline(v)}</li>" for v in values) + "</ul>"
        rows = []
        for value in values:
            match = LANGUAGE.match(value)
            if match:
                level = match["a"] or match["b"]
                rows.append(f'<li><span class="lang">{inline(match["lang"])}</span> '
                            f'<span class="lvl">{inline(level)}</span></li>')
            else:
                rows.append(f'<li><span class="lang">{inline(value)}</span></li>')
        return '<ul class="langs">' + " ".join(rows) + "</ul>"
    if kind == "education" and all(tag in ("p", "ul") for tag, _ in body):
        entries = []
        for tag, values in body:
            for value in values:
                parts = re.split(r"\s+\|\s+", value)
                names = ("school", "degree")
                html = "".join(f'<span class="{names[n]}">{inline(p)}</span>' for n, p in enumerate(parts[:2]))
                if len(parts) > 2:
                    html += '<span class="meta">' + inline(" · ".join(parts[2:])) + "</span>"
                entries.append(f'<div class="edu-item">{html}</div>')
        return "".join(entries)

    out, role = [], None
    for tag, values in body:
        if tag == "h3":
            if role is not None:
                out.append("</div>")
            out.append('<div class="role">' + role_heading(values[0], inline))
            role = "heading"
        elif role == "heading" and tag == "p":
            out.append(block(tag, values, inline, "context"))
            role = "open"
        else:
            out.append(block(tag, values, inline))
            if role:
                role = "open"
    if role is not None:
        out.append("</div>")
    return "".join(out)


def skill_count(markdown):
    """Number of items in a Skills section, or None when there is none (used for a craft warning)."""
    for heading, body in re.findall(r"(?ims)^##\s+([^\n]*)\n(.*?)(?=^##\s|\Z)", markdown):
        if section_kind(heading) == "skills":
            lines = [re.sub(r"^\s*(?:[-*]\s+|•\s*)", "", line) for line in body.splitlines() if line.strip()]
            return len(items(lines)), bool(re.search(r"language", heading, re.I))
    return None
