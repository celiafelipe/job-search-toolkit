# State, inbox and learning log

Discovery keeps four files in the workspace, under `discovery/`. Create them on the first run. The candidate agrees `sources.md`; the agent writes the others; the candidate reads the inbox.

| File | What it holds |
| --- | --- |
| `discovery/sources.md` | Which sources to check, the browser account, alert sender, live searches and trials ([template](sources-template.md)) |
| `discovery/state.json` | Per-source checkpoints, seen IDs and things to retry |
| `discovery/inbox.md` | The ranked list of found roles, newest run on top |
| `discovery/log.md` | One short entry per run: coverage, yield, failures, learnings |

## State

```json
{
  "schema": 1,
  "sources": {
    "board-saved": {
      "last_success": "2030-01-14T07:02:00+00:00",
      "last_attempt": "2030-01-15T07:01:00+00:00",
      "last_outcome": "blocked",
      "seen": {"board:123": {"first_seen": "2030-01-10T07:03:00+00:00"}},
      "retry": [{"id": "board:456", "reason": "posting page did not load"}]
    }
  },
  "backlog": [{"id": "board:789", "posted": "2030-01-12", "passed_triage": "2030-01-15T07:20:00+00:00"}]
}
```

- One entry per source, named as in `discovery/sources.md`. Use canonical IDs (`<site>:<job id>`, or the employer and requisition number) so the same role found twice is counted once. When a listing shows no ID (some search result cards only show it once opened), use a fallback key `<site>-search:<employer>|<title>|<location>`, and switch to the real ID if you open the card later.
- `backlog` holds roles that passed triage but weren't fully screened yet because of the per-run cap ([dedupe and screen](#dedupe-and-screen)).
- Record `first_seen` per ID and per source. That is how you can later tell whether an alert arrived after a live search had already found the role. If older history is missing, say first-discovery is unknown rather than guessing.

## Window and checkpoints

- **Window start:** the source's `last_success` minus one day of overlap. If there is none (first run), use the search window in `search-preferences.md`, or the last 7 days if it doesn't set one. Saved jobs have no window. If the candidate missed runs (a weekend, a holiday), the window simply grows to cover the gap. Report the actual window you used.
- **Advance a checkpoint only when every planned check for that source succeeded and its results are saved in the inbox.** Write checkpoints after the inbox, never before.
- **Never advance a failed or partial source.** Keep its old checkpoint so the next run covers the gap. Do not advance any checkpoint during a test or a rehearsal that stopped early.
- Keep retryable failures (a posting that would not load) in `retry` so deduplication does not hide them forever.
- A retry of the same run must be safe: it must not add a role to the inbox twice.
- If `state.json` exists but can't be read, never overwrite or rebuild it. Report coverage as **failed** with "state file unreadable" under what needs the candidate, and stop.

## Dedupe and screen

1. Collect lightweight IDs and links from all sources first.
2. Remove duplicates across sources, the inbox and the tracker: first by canonical posting or requisition, then by employer, title and location. Different requisition numbers can be different roles; if you can't tell, report it rather than merging.
3. Merge source tags when two sources found the same role.
4. Keep earlier outcomes: applied stays applied, skipped stays skipped unless there is new evidence or the candidate asks. If the board marks a role "Applied" but the tracker has no record, never treat it as new: list it under **Possibly already applied** and ask once. When the candidate confirms, record it with `record-existing`.
5. **Triage** every remaining listing from what the listing itself shows: title, level, location and workplace type, and any hard gate in `rubric.md` that the listing can answer. Fail means one skip with its reason; no description fetch. Unclear means it passes.
6. **Order** the roles that passed: saved jobs first, then newest posting first (the last day, then the last week, then older).
7. **Screen in depth up to 10 roles per run**, in that order. For each, fetch the employer's job description once, save it as `roles/<role_id>/job-description.txt`, and screen it with [job-screen](../../job-screen/SKILL.md) against `rubric.md` (its result goes in `roles/<role_id>/screen.json`). Reuse an earlier assessment unless the role, the evidence or the criteria changed. An employer page showing the role closed beats a board listing. No job description means a provisional assessment, never an invented fit.
8. Put the roles past the cap in the state's `backlog`, still in that order, and list them in the inbox as "waiting for a closer look". Later runs screen new saved jobs first, then the newest of new roles and backlog together, up to the same cap. Drop a backlog role once its posting closes.
9. Register roles worth a closer look (pursue or hold) with `intake`.

## Inbox

Add one dated block to the top of `discovery/inbox.md`. Never rewrite older blocks.

```markdown
## 2030-01-15 run

Coverage: saved jobs complete; alerts complete (2030-01-14 to 2030-01-15); live searches partial (6 of 8, board asked for a login); career pages complete.

### Saved by you
- [VP Product, Fictional Employer](https://jobs.example/role/123): score 78, pursue. Strong match on scope; salary not published.

### Possibly already applied
- [Head of Product, Sample Studio](https://jobs.example/role/55): the board shows "Applied", but it isn't in your tracker. Did you apply? If so, I'll add it.

### Worth a look
1. [Head of Product, Example Labs](https://careers.example/jobs/42): score 74, pursue. Marketplace experience fits; hybrid days unknown.
2. [VP Product, Demo Group](https://jobs.example/role/61) (3 location listings: Example City, Sample Town, remote): score 70, hold. Scope fits; level unclear.
3. [Director of Product, Sample Co](https://jobs.example/role/77): provisional, description would not load. Will retry.

### Waiting for a closer look
12 roles passed the first check but are past today's limit of 10. Next run starts with the newest. Full list in `discovery/state.json`.

### Saved: conflicts to review
- [Chief Product Officer, Placeholder Inc](https://jobs.example/role/88): skipped on 2030-01-10 (relocation). You saved it today. Decision needed: keep skipped or review?

### Skipped
- Below the level you want: 14
- Outside your locations: 9
- Not a product role: 6

Duplicates: 5 already known. Failed: 2 live searches (login). To retry: 1 posting.
```

Every role gets a clickable link, a score or "provisional", a one-line reason and what is still unknown.

- **Skips** are grouped by reason with a count. The role-by-role list (title, employer, link, reason) goes in that run's `discovery/log.md` entry so it can be audited.
- **The same role in several locations** (same employer and title, no requisition numbers that tell them apart) is one line with "N location listings". Keep every ID in `seen`, and never merge them in the tracker: each listing that gets registered keeps its own role.

## Run report

Report two things separately: how complete the coverage was, and how many new roles were found. Never report "nothing found" when a check did not run.

- **Complete:** every planned check ran.
- **Partial:** at least one check ran and at least one didn't; name the ones that didn't and why.
- **Failed:** no check ran, or the run stopped before saving (for example, an unreadable state file).

Then the count: "3 new roles" or "nothing new". A complete run with nothing new is one line.

## Learning log

Read `discovery/log.md` before a run. After saving the inbox, add one short entry: run ID, coverage per source, time per source where you can measure it, IDs seen per source, overlap between sources, already-known duplicates, genuinely new roles, new saved-interest signals, roles worth pursuing, the skipped roles with their reasons, and failures. No email bodies, cookies or tracking tokens.

Write a learning only when evidence supports it: observation, proposed change, expected benefit, status, and how a later run will check it. No made-up daily lesson. Record the candidate's explicit feedback with its date and scope; don't infer preferences from a single save, a silence or a rejection.

You may make small, reversible execution improvements on your own (reuse an assessment that hasn't changed, fix how a link is cleaned). Log them and check next time that they helped. Never change sources, schedule, thresholds, location or salary criteria, or permissions on your own: propose the change in the digest and let the candidate decide.

After about 10 fully covered runs, compare sources: which ones found roles worth pursuing that no other source found, which found them earlier, and what each costs in time. Recommend keeping, narrowing or dropping a source only from those numbers. Partial runs are not evidence that a source is weak.
