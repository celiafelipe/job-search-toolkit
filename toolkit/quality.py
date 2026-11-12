"""Bind a reviewed package to its exact files, answers and observed form."""
from .core import checked, inside, instant, read, record, require, text, url
from . import pdf

FIELDS = ("prompt", "value", "source")


def verified_package(root, package):
    plan = read(package)
    require(plan["schema"] == 1, "Unsupported package version")
    for key in ("role_id", "preparer_id"):
        text(plan[key], key)
    text(plan["preparation_session"], "fresh preparation context evidence")
    job = read(checked(root, plan["job"]))
    require(job["role_id"] == plan["role_id"], "Package job record belongs to another role")
    screen = read(checked(root, plan["screen"]))
    require(screen["role_id"] == plan["role_id"] and screen["verdict"] in ("pursue", "hold", "skip"),
            "Screening does not match role or decision contract")
    ledger = read(root / "ledger.json")
    require(ledger["roles"].get(plan["role_id"], {}).get("job") == plan["job"],
            "Package must use the current registered intake snapshot")
    checked(root, plan["job_description"])
    checked(root, plan["evidence_map"])
    inspection = read(checked(root, plan["inspection"]))
    require(plan["role_id"] == inspection["role_id"], "Inspection belongs to another role")
    destination = url(plan["destination_url"])
    require(plan["destination_url"] == destination == inspection["destination_url"],
            "Use exact observed HTTPS destination")
    instant(inspection["observed_at"])
    text(inspection["platform"], "ATS or unknown")
    text(inspection["platform_evidence"], "observed platform evidence or why unknown")
    require(inspection["coverage"] in ("observed_only", "complete"), "Invalid inspection coverage")
    require(isinstance(inspection["required_fields"], list)
            and all(isinstance(f, str) and f.strip() for f in inspection["required_fields"]),
            "required_fields must list the exact visible prompts")
    answers = read(checked(root, plan["answers"]))
    require(answers["role_id"] == plan["role_id"] and isinstance(answers["fields"], list),
            "Answers belong to another role or fields are malformed")
    seen = set()
    for field in answers["fields"]:
        for key in FIELDS:
            require(key in field, f"Answer missing {key}")
        prompt = text(field["prompt"], "exact field prompt")
        text(field["source"], f"evidence for {prompt}")
        require(prompt not in seen, "Duplicate answer prompt")
        require(type(field["value"]) in (str, int, bool, list), f"Unsupported answer for {prompt}")
        if isinstance(field["value"], list):
            require(all(isinstance(v, str) and v.strip() for v in field["value"]),
                    f"Invalid choices for {prompt}")
        seen.add(prompt)
    require(set(inspection["required_fields"]) <=
            {f["prompt"] for f in answers["fields"]
             if (f["value"].strip() if isinstance(f["value"], str) else f["value"] != [])},
            "A required observed field is missing or blank")
    limits = inspection["attachments"]
    require(set(limits) <= {"cv", "letter"}, "Only CV and required cover letter PDFs are supported")
    letter_mode = inspection["letter_mode"]
    require(letter_mode in ("none", "pdf_required", "text_required"), "Invalid cover letter requirement")
    require(("letter" in limits) == (letter_mode == "pdf_required"),
            "Letter PDFs are supported only when required by the form")
    letters = [field for field in answers["fields"] if field.get("kind") == "letter"]
    require(len(letters) == (letter_mode == "text_required"), "Unexpected or missing letter text")
    if letter_mode == "text_required":
        require(letters[0]["prompt"] == inspection["letter_prompt"] and
                isinstance(letters[0]["value"], str) and letters[0]["value"].strip(),
                "Letter text must match the required prompt")
        max_chars = inspection.get("letter_max_chars")
        if max_chars is not None:
            require(type(max_chars) is int and 0 < len(letters[0]["value"]) <= max_chars,
                    "Letter exceeds observed character limit")
    builds = {}
    for attachment in plan["attachments"]:
        kind = attachment["kind"]
        require(kind in limits and kind not in builds, "Unexpected or duplicate attachment")
        path = checked(root, attachment["file"])
        require(path.suffix.lower() == ".pdf", "Only reviewed PDFs are supported")
        allowed = limits[kind].get("extensions")
        if allowed is not None:
            require(isinstance(allowed, list) and ".pdf" in allowed, "Employer does not accept PDF")
        max_bytes = limits[kind].get("max_bytes")
        if max_bytes is not None:
            require(type(max_bytes) is int and 0 < path.stat().st_size <= max_bytes,
                    "PDF exceeds observed upload size limit")
        text(limits[kind]["slot"], "observed attachment field label")
        receipt = pdf.verify(root, checked(root, attachment["build"]), path, kind)
        builds[kind] = receipt
    require({kind for kind in limits if limits[kind]["required"]} <= set(builds),
            "Required attachment is missing")
    if letter_mode == "pdf_required":
        require("letter" in builds, "Required letter PDF is missing")
    return plan, builds, inspection


def gate(root, package_file, review_file, final=False):
    package = inside(root, package_file)
    review = read(inside(root, review_file))
    require(review["schema"] == 1 and review["package"] == record(package),
            "Review must match exact package bytes")
    require(review["status"] == "pass" and review["unresolved_findings"] == [],
            "Independent review has not passed")
    plan, builds, inspection = verified_package(root, package)
    require(review["role_id"] == plan["role_id"], "Review belongs to another role")
    require(text(review["reviewer_id"], "actual reviewer identity") != plan["preparer_id"],
            "Preparation and review identities must differ")
    text(review["review_session"], "fresh reviewer context evidence")
    require(review["independent_before_draft"] is True, "Reviewer must retrieve evidence before opening draft")
    require(review["review_session"] != plan["preparation_session"],
            "Review must use a different fresh session")
    checked(root, review["independent_evidence"])
    require(review["independent_evidence"]["sha256"] != plan["evidence_map"]["sha256"],
            "Independent assessment cannot be the preparer's evidence map")
    checked(root, review["review_notes"])
    visual = review["visual"]
    require(set(visual) == set(builds), "Visual review must cover every PDF")
    for kind, receipt in builds.items():
        item = visual[kind]
        require(item["pdf_sha256"] == receipt["files"]["document.pdf"]["sha256"]
                and item["pages"] == [receipt["files"][p] for p in receipt["pages"]],
                "Visual review does not match exact PDF and every rendered page")
        text(item["findings"], "concrete visual and recovery observations")
        warnings = item["warning_resolutions"]
        require(set(warnings) == set(receipt["recovery_warnings"]), "Unresolved PDF recovery warning")
        for reason in warnings.values():
            text(reason, "specific recovery warning resolution")
    if final:
        require(inspection["coverage"] == "complete", "Finish inspecting conditional fields before submission")
    return plan
