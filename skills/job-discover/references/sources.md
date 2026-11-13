# Source recipes

How to read each kind of source. The candidate's sources, accounts and search list are in `discovery/sources.md` ([template](sources-template.md)); every run, attended or scheduled, uses that file. Use only sources listed there, in this order: saved jobs first, then alert emails, then live searches, then other boards and career pages. Saved jobs show what the candidate already wants; alerts are cheap; live searches are slow and fragile.

Every source uses the window and checkpoint rules in [state and inbox](state-and-inbox.md).

## Before any browser source

- Use the browser the candidate approved and check that it is signed in to the account they named (as recorded in `discovery/sources.md`, never guess). If it is not, stop that source and report it. Do not switch to another profile or account.
- Read pages one at a time. No parallel tabs crawling the same site and no retries against a challenge.
- A login page, CAPTCHA, verification step or access block ends that source for this run. Never enter credentials or solve a challenge. Record "blocked" and carry on with the next source.
- Read only. Never save, unsave, hide, apply, message, or change filters, lists or alert settings on the site, unless the candidate approved one specific filter change in `discovery/sources.md` (for example "always set the date filter to the last 7 days").

## Saved jobs on a job board

1. Open the board's saved-jobs list through its visible menus. Go through every page; note it if you could not reach them all.
2. Remember saved job IDs in the state. Saved jobs are not limited by posting date. The first run is a baseline: it does not mean those saves are new.
3. For each newly saved job:
   - Already in the inbox or tracker: add a **Saved by you** tag to the existing entry and mention it once as a new interest signal. Do not create a second entry or re-score unchanged evidence.
   - Already applied: leave it as applied.
   - Previously skipped: list it under **Saved: conflicts to review**, with the earlier reason and the criterion it conflicts with. Never discard the save silently and never override the skip yourself.
4. A saved job with a gap or conflict still appears in the digest: link, why it could be worth pursuing, the gap, and the decision needed. Mention it once and keep it visible in the inbox. Raise it again only if something material changes.
5. A save is interest, never permission to apply and never a reason to change the score.

## Job alert emails

1. Use the mail tools the host provides. Search for the alert sender recorded in `discovery/sources.md`. Include read and unread mail; leave out notification noise from the same service that is not a job alert.
2. Go through every page of results for the window.
3. From each email, take employer, title, location, the posting link and the snippet. Include clearly relevant "similar roles" the email lists.
4. Strip tracking parameters from saved links. Never store email bodies, cookies or tracking tokens.
5. Never mark, label, move, archive or delete mail.

## Live searches on a job board

1. Build the search list from `search-preferences.md`: each target title, each location, as separate searches. Write the list in `discovery/sources.md` so every run uses the same one.
2. Enter through the board's own search box. Do not trust that a hand-built URL sets the location or date filter. After every search or filter change, check that the visible keyword, location, date filter and result list are what you meant before reading results.
3. Use the smallest date filter that covers the window. If the board has none small enough, use the next one up and check the visible posting dates. A posting with no visible date is "date unverified", not new.
4. Read results until relevance clearly drops, then stop that search.
5. Record each search as `done`, `stopped at relevance cutoff`, `failed` or `not attempted`. One failed search makes live search coverage partial for this run.

## Other boards and career pages

- Treat a board's "matches" or "recommended" page as that page's coverage, not the whole board's. Note the board's own filters if they differ from the candidate's preferences, but don't change them.
- If a page advertises more results than you could reach, make one more attempt, then record partial coverage.
- A role missing from a board is not proof that it closed. Check the employer's page.
- For employer career pages the candidate approved, check the listing against the posting date window and record what you looked at.

## Trying a new source

Adding a source changes what every later run does, including scheduled ones, so it needs the candidate's decision. When they want to try one, run it as a bounded trial and write the plan in `discovery/sources.md`:

- **Baseline first.** The first full read of the source is a baseline. Backlog found then is useful but does not count as the source's extra yield.
- **Fixed length.** Compare over a set number of fully covered runs of the existing sources (10 is a good default). Partial runs don't count.
- **Measure.** Roles worth pursuing that no other source found, roles it found at least a day earlier, extra minutes per run, and how often it worked. A failed or blocked check counts as a failure, not as a skipped day.
- **Stop and ask.** When the trial ends, stop collecting from that source, summarize the numbers in the digest, and recommend keep, adjust or drop. The candidate decides.
