---
name: job-review
description: Independently review a prepared job application for evidence quality, exact answers, PDF rendering and ATS text recoverability before it can be transmitted.
---

The toolkit root is two levels above this skill's folder (it contains `toolkit/`); run CLI commands from there with `--workspace "<workspace>"` (default `~/Documents/Job Search`). You run every command and write every file; explain outcomes to the candidate in plain language and never ask them to run Python or edit JSON.

Start in a fresh context distinct from the preparer. First read only: the job posting (`roles/<role-id>/job-description.*` or the registered snapshot), the form inspection if one exists, `profile.md` and the `experience/` files. Do not open `screen.json`, the evidence map, the draft or the preparer's notes yet. Save your own ranked assessment and retrieval trail before opening the draft. If no independent worker/context can actually be arranged, mark review pending. Do not manufacture run IDs or self-review.

Check that the strongest specific match is visible and any omissions are deliberate; verify claims against the experience files and their provenance log rather than the preparer's wording. Apply the anti-patterns and checklist in [the CV craft guide](../job-prepare/references/cv-craft.md). Check role, employer, dates, ownership, quantities, terminology, disclosure constraints and evidence for each exact answer. Look for unsupported claims, unexplained gaps, wrong job/company, and mismatch with actual required fields or letter limits.

For every PDF built by the toolkit, inspect the exact build receipt, both text views and every page image. Recover key contact, chronology and role-to-achievement relationships without using the source to mentally fill in missing context. Compare to the source, then inspect margins, layout, line wraps, clipping and breaks. If the build reported recovery warnings, resolve each one with concrete observations, or request revision. Review the build named in `roles/<role-id>/notes.md` (the one the upload copy came from); if several exist and none is named, ask. A local text pass does not establish what the employer’s parser sees.

**The candidate's own CV** (`"source": "candidate"` in the package, or `CV choice: own` in `profile.md`): the design is theirs, so do not review its visuals and add no `visual` entry for it. Still check the facts on it against the experience files, open its saved `review-cv` report (it must be for this exact file), and note the readability findings in your review notes as advice for the candidate. Those findings never fail a review on their own; unsupported claims, wrong employer or dates, and answers without evidence still do. Every form answer is reviewed exactly as for any other package.

**CV-only review (the common case: the candidate sends the CV themselves, with no inspected form or package):** write `roles/<role-id>/review/review-notes.md` with your findings and an outcome of `ready`, `revise` or `needs_fact`, and tell the candidate in plain words. Do not create `review.json`; that belongs to the full package workflow below.

**Full package review:** write findings and a `pass`, `revise`, or `needs_fact` outcome. A pass binds exact package, visual evidence and concrete findings per [the contract](../../docs/WORKFLOW.md). Recheck changes before signing a new revision. The CLI tests consistency and bytes; the execution owner must verify actual reviewer/session provenance and review quality. Do not upload, edit the package, change policy or update the tracker.
