# Job Search Toolkit

A set of agent skills for finding roles, screening them against your criteria, preparing a truthful CV, independently reviewing the exact package, and tracking a verified submission. It keeps your candidate data in a separate private workspace. No account, inbox integration, schedule, or automatic submission authority comes with it.

## Quick start

1. Clone or download this repository. From the checkout, run the commands below. Use Python 3.10+ on a system with POSIX file locking. For PDF builds, install Chrome or Chromium and Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`). The workflow was tested on macOS; other platforms and employer sites are untested. Set `JOBKIT_CHROME` to the browser executable if discovery fails.

   ```sh
   python3 -m toolkit doctor
   python3 -m toolkit init
   ```

2. Fill the starter files in `~/.job-search-workspace`, or ask your assistant to follow [job-search-onboard](skills/job-search-onboard/SKILL.md). To choose a different private location, set `JOBKIT_WORKSPACE` or pass `--workspace /path/to/private-workspace` **before** the subcommand. The workspace cannot be inside a Git checkout. Keep the master CV and confirmed candidate evidence as source files; role drafts live in separate folders.
3. In an agent client with local file access, point the assistant to [job-search](skills/job-search/SKILL.md) and give it the private workspace path, the stage you want and either a job link or sourcing scope. For skill discovery, register the skill folders using your client’s method without replacing an existing same-name skill; keep the relative links to the checkout intact. You can also use any stage by pointing directly to its `SKILL.md`. This project does not install skills or modify your client settings.
4. See [which files each stage needs](docs/WORKFLOW.md#start-here). Try: “Screen these links against my rubric. For the strongest fit, inspect the application and prepare a local package. Do not enter data or submit.”

| Stage | Skill |
| --- | --- |
| Setup | [job-search-onboard](skills/job-search-onboard/SKILL.md) |
| Coordinate the pipeline | [job-search](skills/job-search/SKILL.md) |
| Find and register roles | [job-discover](skills/job-discover/SKILL.md) |
| Screen a role | [job-screen](skills/job-screen/SKILL.md) |
| Prepare documents and answers | [job-prepare](skills/job-prepare/SKILL.md) |
| Review in a separate fresh context | [job-review](skills/job-review/SKILL.md) |
| Inspect and, if authorized, apply | [job-apply](skills/job-apply/SKILL.md) |
| Verify and recover | [job-track](skills/job-track/SKILL.md) |

## Try the fictional workflow

```sh
demo_dir=$(mktemp -d)
python3 examples/demo.py "$demo_dir/private"
python3 -m toolkit --workspace "$demo_dir/private" tracker
```

The demo registers a fictional role, builds and checks a PDF, records a simulated submit attempt, resolves an ambiguous outcome and reads the tracker back. It never opens an employer site. Its reviewer IDs, approval, and receipt are synthetic; simulation records cannot enable live application actions. See [the contracts](docs/WORKFLOW.md) and [execution guide](docs/APPLY.md) for a real handoff. After an explicit opt-in, a capable assistant can use a bounded policy to apply to newly found eligible roles. The policy limits destinations, criteria, and time; it installs no scheduler.

## Capabilities and limits

The Python tools handle local state and checks. The agent or user reads sources and operates the employer form through an available, authorized browser. The toolkit does not search sites by itself, log into accounts, press Submit, verify the truth of a pasted receipt, or prove that a reviewer worked independently. If tooling is missing, keep work local and mark the affected step pending. Do not substitute self-review or treat a local test as a real application.

The document builder uses a fresh local headless browser profile and a plain single-column template. It checks recovery in two Poppler text views and renders every page for independent visual review. It does not use your signed-in profile or emulate a vendor’s ATS. Its constrained Markdown format and PDF-only scope are intentional; a DOCX-only or unsupported form needs user handoff. If a restricted agent sandbox prevents headless Chrome from launching, run the same command from a suitable local terminal or use your tool’s approved launch permission. Do not bypass browser sandboxing.

## Privacy and verification

Private profile files, CVs, answers, review records, portal evidence, tracker and browser artifacts stay outside the repository. Keep only the minimal evidence needed; avoid storing tokens, credentials or unrelated applicant data. Don’t send private data to search engines, resume checkers or unknown form destinations. Your agent host may have its own processing and retention terms.

Run `python3 -m unittest discover -s tests`. The PDF integration test requires the PDF tools and a working browser launch. Run `python3 tools/privacy_check.py` before sharing changes. The checker is a guardrail: independently review the tree and Git commit identities/history before publication.
