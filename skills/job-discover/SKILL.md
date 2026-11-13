---
name: job-discover
description: Find and register job postings from links the candidate shares, job alerts or exports, or approved public career pages and job boards. Removes duplicates by employer and requisition number. Use when someone says "find roles that match my criteria", "look for jobs at X", or shares a batch of job links.
---

# Job discover

The toolkit root is two levels above this skill's folder. The workspace defaults to `~/Documents/Job Search`. You run every command and write every file; explain results in plain language and never ask the candidate to run Python or edit JSON.

## Before searching

- Read `search-preferences.md` and [the intake contract](../../docs/WORKFLOW.md#1-intake-and-screening).
- If they shared links, start with those. Search more widely only if they ask, and only on sources they approved.
- Job boards that need a login may not be reachable. Never log in for them, import their contacts or messages, or guess which account to use. Hand over to them instead.
- A job they saved on a board shows interest. It is not permission to apply.

## For each source

Keep a short note of what you searched: the query, the date range, the pages you looked at, what you found, and anything that failed or was cut short. If a source fails, say so and carry on with the others. "No jobs found" is only true when the search actually ran. Try a failed source again once or twice, not endlessly.

Pick the date range from their preferences and the last time you searched.

## For each posting

1. Prefer the employer's own career page over a job board copy.
2. Save the full job text as written, with the link, employer, requisition number if there is one, role title, location, date posted, and whether it is still open (open, closed or unknown).
3. Choose the `role_id` first, name the folder `roles/<role_id>/` after it, write `job.json` there, then register it with `intake`. Use the role ID and snapshot that `intake` returns.
4. **Duplicates:** the same employer and requisition number is the same job, even from a different link (keep the extra link as an alias). Two postings with a similar title but different requisition numbers are different jobs. If you can't tell, report it rather than merging.
5. If a registered posting changes before an application is sent, refresh it with `intake --refresh` for that same role, and redo any review that depended on it.

## Report back

Give a short list: new roles, duplicates of ones already registered, closed postings, and unclear ones, plus which sources you covered and any that failed. Offer to screen the most promising ones ([job-screen](../job-screen/SKILL.md)).

This stage never applies, uploads, saves jobs on a board, or changes their search preferences.
