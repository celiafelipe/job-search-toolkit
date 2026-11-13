"""Run with python3 -m toolkit from the toolkit checkout."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from . import core, pdf, quality


def parser():
    p = argparse.ArgumentParser(description="Local job-search package checks and application ledger; no network actions.")
    p.add_argument("--workspace", default=os.environ.get("JOBKIT_WORKSPACE") or core.default_workspace(),
                   help="Private folder outside Git; also JOBKIT_WORKSPACE")
    commands = p.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check runtime and PDF dependencies")
    init = commands.add_parser("init", help="Create a new private workspace and starter files")
    init.add_argument("--demo", action="store_true", help="Use reserved .example destinations only")
    intake = commands.add_parser("intake", help="Register job JSON or merge a known alias")
    intake.add_argument("job")
    intake.add_argument("--refresh", action="store_true", help="Store an updated job snapshot before transmission")
    commands.add_parser("tracker", help="Read the canonical application ledger")
    for name in ("lock", "unlock"):
        commands.add_parser(name, help="Acquire or release this workspace's browser lease").add_argument("owner")
    recover = commands.add_parser("recover-lock", help="Mark interrupted attempts uncertain and clear verified orphan")
    recover.add_argument("owner")
    recover.add_argument("evidence")
    build = commands.add_parser("build-pdf", help="Export and check a CV or required letter PDF")
    build.add_argument("source")
    build.add_argument("output")
    build.add_argument("--kind", choices=("cv", "letter"), required=True)
    check = commands.add_parser("check", help="Recompute the independent review gate")
    check.add_argument("package")
    check.add_argument("review")
    check.add_argument("--final", action="store_true")
    for name in ("authorize-transmission", "begin-submit"):
        cmd = commands.add_parser(name, help="Write the local action checkpoint; no external action")
        cmd.add_argument("package")
        cmd.add_argument("review")
        cmd.add_argument("--approval")
        cmd.add_argument("--owner", required=True)
        cmd.add_argument("--simulate", action="store_true")
    resolve = commands.add_parser("resolve", help="Record verified evidence or keep attempt uncertain")
    resolve.add_argument("role_id")
    resolve.add_argument("attempt_id")
    resolve.add_argument("outcome", choices=("submitted_verified", "no_submission", "uncertain"))
    resolve.add_argument("evidence")
    resolve.add_argument("--owner", required=True)
    existing = commands.add_parser("record-existing", help="Track a verified user/portal application made outside this toolkit")
    existing.add_argument("role_id")
    existing.add_argument("evidence")
    existing.add_argument("--owner", required=True)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    c = args.command
    os.umask(0o077)
    try:
        root = core.workspace(args.workspace, initialized=c not in ("init", "doctor"))
        if c == "doctor":
            runtime = pdf.tools()
            check = pdf.probe(runtime)
            hints = pdf.install_hints(runtime)
            if all(runtime.values()) and check != "ok":
                hints.append("The PDF tools are installed but a test export failed: " + check)
                hints.append("Most reliable fix on Linux, containers and WSL: 'npx @puppeteer/browsers install "
                             "chrome-headless-shell@stable', then set JOBKIT_CHROME to the chrome-headless-shell "
                             "path it prints, and run doctor again.")
            result = {"python": sys.version.split()[0], "workspace": str(root),
                      "pdf_dependencies": {name: bool(path) for name, path in runtime.items()},
                      "pdf_export_test": check,
                      "pdf_ready": check == "ok",
                      "workspace_exists": (root / "ledger.json").is_file(),
                      "fix": hints,
                      "scope": "No browser session, site access, or authenticated tool was checked."}
        elif c == "init":
            result = core.init(root, args.demo)
        elif c == "intake":
            result = core.intake(root, args.job, args.refresh)
        elif c == "tracker":
            result = core.read(root / "ledger.json")
        elif c in ("lock", "unlock"):
            result = core.lock(root, args.owner, release=c == "unlock")
        elif c == "recover-lock":
            result = core.recover_lock(root, args.owner, args.evidence)
        elif c == "build-pdf":
            result = pdf.build(root, args.source, args.output, args.kind)
        elif c == "check":
            package = quality.gate(root, args.package, args.review, final=args.final)
            result = {"review_gate": "pass", "role_id": package["role_id"],
                      "final_form_coverage_checked": args.final, "action_authorized": False}
        elif c in ("authorize-transmission", "begin-submit"):
            result = core.authorize_action(root, args.package, args.review, args.approval,
                                           args.owner, "submit" if c == "begin-submit" else "transmit",
                                           args.simulate)
        elif c == "record-existing":
            result = core.existing_submission(root, args.role_id, args.evidence, args.owner)
        else:
            result = core.resolve(root, args.role_id, args.attempt_id, args.outcome,
                                  args.evidence, args.owner)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if c != "doctor" or result["pdf_ready"] else 1
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.TimeoutExpired) as exc:
        print(f"Stopped: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
