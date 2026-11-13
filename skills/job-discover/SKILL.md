---
name: job-discover
description: Find and register job postings from links the candidate shares, saved jobs and job alert emails, live searches on approved job boards, or approved career pages. Remembers what each source already covered, removes duplicates across sources, and writes a ranked inbox. Use when someone says "find roles that match my criteria", "check my job alerts", "look for jobs at X", "refresh my job inbox", or shares a batch of job links.
---

# Job discover

The toolkit root is two levels above this skill's folder. The workspace defaults to `~/Documents/Job Search`. You run every command and write every file; explain results in plain language and never ask the candidate to run Python or edit JSON.

## Before searching

- Read `search-preferences.md`, `rubric.md` and [the intake contract](../../docs/WORKFLOW.md#1-intake-and-screening).
- Read `discovery/sources.md`. If it doesn't exist and they want more than the links they shared, write it with them first from [the template](references/sources-template.md): which kinds of source they approved in `search-preferences.md`, which browser account, which alert sender, and the live searches built from their target titles and locations. Change it later only when they agree.
- Read `discovery/state.json`, `discovery/inbox.md`, `discovery/log.md` and the tracker if they exist ([state and inbox](references/state-and-inbox.md)).
- If they shared links, start with those. Search more widely only if they ask, and only on sources they approved.
- Job boards that need a login may not be reachable. Never log in for them, import their contacts or messages, or guess which account to use. Hand over to them instead.
- A job they saved on a board shows interest. It is not permission to apply.

## Run the sources

Go through the sources in `discovery/sources.md` in order: saved jobs, alert emails, live searches, then other boards and career pages. [Source recipes](references/sources.md) explains how to read each one safely.

For each source, work out its date window from its last successful check ([state and inbox](references/state-and-inbox.md#window-and-checkpoints)) and keep a short note of what you searched: the query, the actual window, the pages you looked at, what you found, and anything that failed or was cut short. If a source fails, say so and carry on with the others. "No jobs found" is only true when the search actually ran. Try a failed source again once, not endlessly.

## For each posting

1. Remove duplicates across sources, the inbox and the tracker before fetching full descriptions ([dedupe and screen](references/state-and-inbox.md#dedupe-and-screen)).
2. Prefer the employer's own career page over a job board copy.
3. Save the full job text as written, with the link, employer, requisition number if there is one, role title, location, date posted, and whether it is still open (open, closed or unknown).
4. For roles worth a closer look, choose the `role_id` first, name the folder `roles/<role_id>/` after it, write `job.json` there, then register it with `intake`. Use the role ID and snapshot that `intake` returns.
5. **Duplicates:** the same employer and requisition number is the same job, even from a different link (keep the extra link as an alias). Two postings with a similar title but different requisition numbers are different jobs. If you can't tell, report it rather than merging.
6. If a registered posting changes before an application is sent, refresh it with `intake --refresh` for that same role, and redo any review that depended on it.

## Save and report

1. Add a dated block to the top of `discovery/inbox.md`: coverage and actual windows, saved roles first, then ranked roles with clickable links, conflicts to review, one-line skips, duplicates and failures ([inbox format](references/state-and-inbox.md#inbox)).
2. Only then advance the checkpoints of sources that fully succeeded. Never advance a failed or partial one.
3. Add one entry to `discovery/log.md` ([learning log](references/state-and-inbox.md#learning-log)).
4. Tell the candidate in a few lines whether it was **nothing new**, **partial coverage** or **check failed**, what's worth a look, and where the inbox is. Offer to screen the most promising ones in depth ([job-screen](../job-screen/SKILL.md)).

## Offer autopilot after a good first run

If this was the candidate's first discovery run on their own approved sources, every planned source ran (or failed for a clear, reported reason), and they found the inbox useful, offer once: "I can run this for you every morning and leave a short summary. Want to set that up?" On yes, go to [job-autopilot](../job-autopilot/SKILL.md); this run counts as its rehearsal. Don't offer again if they decline.

This stage never applies, uploads, saves jobs on a board, or changes their search preferences.
