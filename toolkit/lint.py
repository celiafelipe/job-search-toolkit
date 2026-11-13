"""Consistency checks for the files the agent writes by hand in a workspace."""
import json
import re

from . import pdf

DATE_LINE = re.compile(r"^\s*-?\s*`?\d{4}-\d{2}-\d{2}")
SCREEN_KEYS = {"role_id", "score", "verdict", "hard_gaps", "unknowns", "rationale"}
RATIONALE_KEYS = {"criteria", "role_evidence", "candidate_evidence", "user_override"}
DEPTHS = {"thin", "ok", "rich"}
FIRST_PERSON = re.compile(r"\b(I|me|my)\b")


def table(text):
    """Header and data rows of the first Markdown table, as lists of stripped cells."""
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in text.splitlines() if line.strip().startswith("|")]
    if not rows:
        return [], []
    return [cell.casefold() for cell in rows[0]], [row for row in rows[2:] if any(row)]


def table_rows(text):
    return table(text)[1]


def section(text, heading):
    match = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return match.group(1) if match else ""


def run(root):
    errors, warnings = [], []

    rubric = root / "rubric.md"
    if rubric.is_file():
        weights = []
        header, rows = table(rubric.read_text(encoding="utf-8"))
        column = header.index("weight") if "weight" in header else None
        for row in rows if column is not None else []:
            if len(row) > column and row[column]:
                try:
                    weights.append(float(row[column].rstrip("%")))
                except ValueError:
                    errors.append(f"rubric.md: weight '{row[column]}' for '{row[0]}' is not a number")
        if weights and sum(weights) != 100:
            errors.append(f"rubric.md: weights total {sum(weights):g}, not 100")

    experience = root / "experience"
    files = sorted(p.name for p in experience.glob("*.md") if p.name not in ("INDEX.md", "_role-template.md"))
    index = experience / "INDEX.md"
    listed = []
    if index.is_file():
        for row in table_rows(index.read_text(encoding="utf-8")):
            if not row[0]:
                continue
            listed.append(row[0].strip("`"))
            if len(row) >= 5 and row[4] and row[4] not in DEPTHS:
                errors.append(f"experience/INDEX.md: depth '{row[4]}' for {row[0]} must be thin, ok or rich")
            if len(row) >= 6 and row[5] and not re.match(r"^(not started|in progress|done \d{4}-\d{2}-\d{2})",
                                                         row[5]):
                warnings.append(f"experience/INDEX.md: career interview '{row[5]}' for {row[0]} is not "
                                "'not started', 'in progress (resume at: ...)' or 'done YYYY-MM-DD'")
    for name in files:
        if name not in listed:
            errors.append(f"experience/{name} has no row in experience/INDEX.md")
        log = section((experience / name).read_text(encoding="utf-8"), "Provenance log")
        if not any(DATE_LINE.match(line) for line in log.splitlines()):
            errors.append(f"experience/{name}: the provenance log has no dated line")
    for name in listed:
        if name not in files:
            errors.append(f"experience/INDEX.md lists {name}, but the file does not exist")

    master = root / "master-cv.md"
    if master.is_file():
        text = master.read_text(encoding="utf-8")
        try:
            pdf.parse(text)
        except ValueError as exc:
            errors.append(f"master-cv.md: {exc}")
        if "—" in text:
            warnings.append("master-cv.md: contains em dashes; use commas, colons or parentheses")
        if FIRST_PERSON.search(text):
            warnings.append("master-cv.md: uses first person (I, me, my); keep one voice without it")

    for screen in sorted((root / "roles").glob("*/screen.json")):
        name = f"roles/{screen.parent.name}/screen.json"
        try:
            data = json.loads(screen.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{name}: not valid JSON ({exc})")
            continue
        missing = SCREEN_KEYS - set(data)
        if missing:
            errors.append(f"{name}: missing {', '.join(sorted(missing))}")
        if data.get("verdict") not in (None, "pursue", "hold", "skip"):
            errors.append(f"{name}: verdict must be pursue, hold or skip")
        if data.get("role_id") not in (None, screen.parent.name):
            errors.append(f"{name}: role_id '{data.get('role_id')}' does not match its folder")
        rationale = data.get("rationale")
        if rationale is not None and (not isinstance(rationale, dict) or RATIONALE_KEYS - set(rationale)):
            errors.append(f"{name}: rationale must be an object with {', '.join(sorted(RATIONALE_KEYS))}")

    return {"lint": "ok" if not errors else "problems found", "errors": errors, "warnings": warnings}
