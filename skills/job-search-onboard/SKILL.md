---
name: job-search-onboard
description: Set up a private candidate workspace for the reusable job-search toolkit and collect the minimum profile, career evidence, preferences, and policies for its stages.
---

Read [setup and privacy](../../README.md) and the [workspace contract](../../docs/WORKFLOW.md). From the toolkit checkout, run `python3 -m toolkit doctor` and `python3 -m toolkit init` with an optional `--workspace` before the subcommand. Use an untracked directory outside Git; do not put candidate data in the checkout, starter templates, or examples. Record an existing workspace path instead of reinitializing it.

Use the starter files to collect only what the requested stages need:
- Profile and candidate-approved master CV. Keep the source unchanged while tailoring.
- Detailed career evidence by role/project, including claim provenance, scope, dates, outcomes, supported metrics and disclosure limits. A master CV is not a substitute.
- Search preferences, source access and rubric. Confirm hard requirements, weights, score interpretation and what missing information means.
- Exact confirmed answers with scope and refresh conditions, including availability, eligibility, compensation and consent only if supplied.
- Path configuration. Default action policy is preparation-only. A switch to application authority requires explicit current user consent and bounded scope; explain exactly which data or actions it would permit. No schedule is installed.

Show what is ready and which stages are blocked. Do not guess unset preferences or import a prior candidate's files or policy. Validate with the offline demo if wanted.
