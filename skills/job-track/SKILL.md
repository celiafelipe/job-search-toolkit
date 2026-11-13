---
name: job-track
description: Verify and record an application submission, reconcile uncertain attempts and prevent duplicates, or import a verified candidate-submitted application.
---

The toolkit root is two levels above this skill's folder (it contains `toolkit/`); run CLI commands from there with `--workspace "<workspace>"` (default `~/Documents/Job Search`). You run every command and write every file; explain outcomes to the candidate in plain language and never ask them to run Python or edit JSON.

Read [ledger and recovery](../../docs/APPLY.md). Use the canonical role and its registered aliases. The ledger is the source of truth; a new tracker export is a view of the same state.

For a pending attempt, match evidence to the role, observed destination, timestamp and attempt ID. A visible portal confirmation/history entry or user-verified matching receipt can establish submission. A click, spinner or absence of a receipt does not establish either outcome. Save minimal evidence and run `resolve`, then read back `tracker`. If evidence is ambiguous, retain `uncertain`. Only authoritative evidence that the specific submission did not occur permits reopening; never retry blindly or repair a tracker issue by resubmitting.

For a candidate-submitted application with no toolkit attempt, use `record-existing` with a matching verified receipt. Do not invent an attempt or infer success from draft files. On an orphaned lock, verify that the owner ended; use `recover-lock` to mark its interrupted attempts uncertain and inspect them before continuing. Record later user-supplied lifecycle events separately in the role folder with their evidence; they do not change the original submission proof.

Report the verified state, evidence, what is uncertain, and next owner/action. Do not send messages or create unrelated follow-up tasks.
