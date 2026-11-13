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
  }
}
```

- One entry per source, named as in `discovery/sources.md`. Use canonical IDs (`<site>:<job id>`, or the employer and requisition number) so the same role found twice is counted once.
- Record `first_seen` per ID and per source. That is how you can later tell whether an alert arrived after a live search had already found the role. If older history is missing, say first-discovery is unknown rather than guessing.

## Window and checkpoints

- **Window start:** the source's `last_success` minus one day of overlap. If there is none (first run), use the last 14 days. If the candidate missed runs (a weekend, a holiday), the window simply grows to cover the gap. Report the actual window you used.
- **Advance a checkpoint only when every planned check for that source succeeded and its results are saved in the inbox.** Write checkpoints after the inbox, never before.
- **Never advance a failed or partial source.** Keep its old checkpoint so the next run covers the gap. Do not advance any checkpoint during a test or a rehearsal that stopped early.
- Keep retryable failures (a posting that would not load) in `retry` so deduplication does not hide them forever.
- A retry of the same run must be safe: it must not add a role to the inbox twice.

## Dedupe and screen

1. Collect lightweight IDs and links from all sources first.
2. Remove duplicates across sources, the inbox and the tracker: first by canonical posting or requisition, then by employer, title and location. Different requisition numbers can be different roles; if you can't tell, report it rather than merging.
3. Merge source tags when two sources found the same role.
4. Keep earlier outcomes: applied stays applied, skipped stays skipped unless there is new evidence or the candidate asks.
5. Only then fetch the employer's job description, once per distinct role per run. Reuse an earlier assessment unless the role, the evidence or the criteria changed. An employer page showing the role closed beats a board listing.
6. Screen with [job-screen](../../job-screen/SKILL.md) against `rubric.md`. No job description means a provisional assessment, never an invented fit.
7. Register roles that are worth a closer look (pursue or hold) with `intake`. Roles that fail a hard gate stay as one line in the inbox.

## Inbox

Add one dated block to the top of `discovery/inbox.md`. Never rewrite older blocks.

```markdown
## 2030-01-15 run

Coverage: saved jobs complete; alerts complete (2030-01-14 to 2030-01-15); live searches partial (6 of 8, board asked for a login); career pages complete.

### Saved by you
- [VP Product, Fictional Employer](https://jobs.example/role/123): score 78, pursue. Strong match on scope; salary not published.

### Worth a look
1. [Head of Product, Example Labs](https://careers.example/jobs/42): score 74, pursue. Marketplace experience fits; hybrid days unknown.
2. [Director of Product, Sample Co](https://jobs.example/role/77): provisional, description would not load. Will retry.

### Saved: conflicts to review
- [Chief Product Officer, Placeholder Inc](https://jobs.example/role/88): skipped on 2030-01-10 (relocation). You saved it today. Decision needed: keep skipped or review?

### Skipped
- Product Lead, Demo Ltd: below the level you want.

Duplicates: 5 already known. Failed: 2 live searches (login). To retry: 1 posting.
```

Every role gets a clickable link, a score or "provisional", a one-line reason and what is still unknown. Skips get one line each so they can be audited.

## Run report

Always say which of these it was. Never report "nothing found" when a check did not run.

- **Nothing new:** every source ran and there were no new roles. One line.
- **Partial coverage:** some checks ran; name the ones that didn't and why.
- **Check failed:** a source could not run at all.

## Learning log

Read `discovery/log.md` before a run. After saving the inbox, add one short entry: run ID, coverage per source, time per source where you can measure it, IDs seen per source, overlap between sources, already-known duplicates, genuinely new roles, new saved-interest signals, roles worth pursuing, and failures. No email bodies, cookies or tracking tokens.

Write a learning only when evidence supports it: observation, proposed change, expected benefit, status, and how a later run will check it. No made-up daily lesson. Record the candidate's explicit feedback with its date and scope; don't infer preferences from a single save, a silence or a rejection.

You may make small, reversible execution improvements on your own (reuse an assessment that hasn't changed, fix how a link is cleaned). Log them and check next time that they helped. Never change sources, schedule, thresholds, location or salary criteria, or permissions on your own: propose the change in the digest and let the candidate decide.

After about 10 fully covered runs, compare sources: which ones found roles worth pursuing that no other source found, which found them earlier, and what each costs in time. Recommend keeping, narrowing or dropping a source only from those numbers. Partial runs are not evidence that a source is weak.
