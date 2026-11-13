"""Fictional, offline walkthrough. Never accesses an employer or sends data."""
import argparse
import datetime as dt
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolkit import core, pdf, quality  # noqa: E402

ROLE = "orchard-lantern-57"
DESTINATION = "https://careers.orchard-lantern.example/roles/57"


def fixture(root, with_cv=True, inspect_pages=None):
    root = core.workspace(root, initialized=False)
    core.init(root, demo=True)
    folder = root / "roles" / ROLE
    folder.mkdir()

    def write(name, content):
        path = folder / name
        path.write_text(content, encoding="utf-8")
        return core.record(path)

    def data(name, value):
        path = folder / name
        core.atomic(path, value)
        return core.record(path)

    raw = write("job-description.txt",
                "Orchard Lantern seeks an exhibit coordinator to improve visitor signage and volunteer handovers.\n")
    job = data("job.json", {"role_id": ROLE, "title": "Exhibit Coordinator", "company": "Orchard Lantern",
                            "posting_url": "https://jobs.example/exhibits/57", "requisition_id": "57",
                            "identity_evidence": "Fictional posting and employer form display requisition 57.",
                            "observed_at": core.now(), "aliases": [DESTINATION]})
    registered = core.intake(root, job["path"])
    screen = data("screen.json", {"role_id": ROLE, "score": 88, "verdict": "pursue",
                                  "hard_gaps": [], "unknowns": [],
                                  "rationale": "Direct evidence of accessible exhibit signage and handover training."})
    inspection = data("inspection.json", {
        "role_id": ROLE, "destination_url": DESTINATION, "observed_at": core.now(),
        "platform": "unknown", "platform_evidence": "Fictional employer form has no vendor label.",
        "coverage": "complete", "required_fields": ["Name", "Available for weekend shifts?"],
        "letter_mode": "none",
        "attachments": {"cv": {"required": True, "slot": "CV", "extensions": [".pdf"],
                                "max_bytes": 2_000_000}} if with_cv else {}
    })
    answers = data("answers.json", {"role_id": ROLE, "fields": [
        {"prompt": "Name", "value": "Rowan Example", "source": "Fictional profile"},
        {"prompt": "Available for weekend shifts?", "value": True,
         "source": "Fictional confirmation for this requisition"}
    ]})
    write("career-evidence.md", """# Fictional career evidence
- EX-A: Rowan redesigned wayfinding at Paper Harbor Museum, responsible for sign wording and visitor testing.
- EX-B: Rowan trained volunteers to use a handover checklist; no verified numerical outcome.
""")
    mapping = write("evidence-map.md",
                    "1. Direct: sign design and visitor testing (EX-A).\n2. Direct: volunteer handovers (EX-B).\n")
    independent = write("independent-evidence.md",
                        "EX-A best matches the signage requirement; EX-B supports handovers but no outcome metric.\n")
    notes = write("review.md", "Fictional walkthrough attestation only; no live application review.\n")
    attachments, visual = [], {}
    if with_cv:
        cv = write("cv.md", """# Rowan Example

Exhibit coordinator | rowan@example.org

## Experience

### Visitor Programs Assistant | Paper Harbor Museum | 2021 to 2024

- Redesigned exhibit wayfinding and tested signage with visitors.
- Trained volunteers on a handover checklist.

## Skills

Visitor research, plain language signage and volunteer training.
""")
        build = pdf.build(root, cv["path"], folder / "cv-build", "cv")
        built = core.read(build["build"])
        attachments.append({"kind": "cv", "file": built["files"]["document.pdf"],
                            "build": core.record(build["build"])})
        visual["cv"] = {
            "pdf_sha256": built["files"]["document.pdf"]["sha256"],
            "pages": [built["files"][p] for p in built["pages"]],
            "findings": "Synthetic demo attestation; not a real independent review.",
            "warning_resolutions": {w: "Fictional fixture: inspect the two saved extraction views."
                                    for w in built["recovery_warnings"]}}
        if inspect_pages:
            inspect_pages(built)
    package = data("package.json", {
        "schema": 1, "role_id": ROLE, "job": registered["job"], "job_description": raw,
        "screen": screen, "inspection": inspection, "destination_url": DESTINATION,
        "preparer_id": "fictional-preparer", "preparation_session": "fictional-prep-run",
        "answers": answers, "evidence_map": mapping, "attachments": attachments
    })
    review = data("review.json", {
        "schema": 1, "role_id": ROLE, "status": "pass", "package": package,
        "reviewer_id": "fictional-reviewer", "review_session": "fictional-review-run",
        "independent_before_draft": True, "unresolved_findings": [],
        "independent_evidence": independent, "review_notes": notes, "visual": visual
    })
    end = (core.instant(core.now()) + dt.timedelta(hours=1)).isoformat()
    grant = data("approval.json", {
        "role_id": ROLE, "destination_url": DESTINATION, "review_sha256": review["sha256"],
        "actions": ["transmit", "submit"], "authorized_by": "fictional candidate", "simulation": True,
        "authorized_at": core.now(), "expires_at": end,
        "evidence": "Synthetic approval for the offline demonstration only."
    })
    return root, folder, package["path"], review["path"], grant["path"]


def enable_demo(root):
    core.atomic(root / "policy.json", {"mode": "ask-per-package", "actions": ["transmit", "submit"]})


def demo_receipt(folder, attempt_id, kind, observation):
    path = folder / f"{kind}.json"
    core.atomic(path, {"role_id": ROLE, "attempt_id": attempt_id, "observed_at": core.now(),
                       "destination_url": DESTINATION, "kind": kind, "observation": observation,
                       "simulation": True})
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", help="New workspace outside Git")
    args = parser.parse_args()
    os.umask(0o077)
    root, folder, package, review, approval = fixture(args.workspace)
    quality.gate(root, package, review, final=True)
    print("Review checks passed (synthetic reviewers).")
    enable_demo(root)
    owner = "offline-demo"
    core.lock(root, owner)
    try:
        core.authorize_action(root, package, review, approval, owner, "transmit", True)
        attempt = core.authorize_action(root, package, review, approval, owner, "submit", True)
        print("Attempt persisted. Simulating an ambiguous response; nothing transmitted.")
        proof = demo_receipt(folder, attempt["id"], "ambiguous", "Fictional timeout after hypothetical click.")
        core.resolve(root, ROLE, attempt["id"], "uncertain", proof, owner)
        proof = demo_receipt(folder, attempt["id"], "portal_history",
                             "Fictional application history lists requisition 57 as received (demo receipt 57).")
        result = core.resolve(root, ROLE, attempt["id"], "submitted_verified", proof, owner)
        print("Fictional tracker readback:", result["state"])
        assert core.read(root / "ledger.json")["roles"][ROLE]["state"] == "submitted_verified"
    finally:
        core.lock(root, owner, release=True)


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"Demo stopped: {exc}\nRun 'python3 -m toolkit doctor' and follow its 'fix' hints.", file=sys.stderr)
        sys.exit(1)
