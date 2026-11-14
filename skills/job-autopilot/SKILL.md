---
name: job-autopilot
description: Sets up and runs a daily unattended job-search run (discover, screen, short digest) on the candidate's own computer, using a schedule in their agent host. Use when someone says "run my job search every morning", "set up autopilot", "check for jobs daily", "pause my job-search autopilot", or when a scheduled task asks for "the job-search daily run".
---

# Job autopilot

Two modes. **Set up** is a conversation with the candidate. **Daily run** is what the schedule triggers, with nobody watching. The policy lives in workspace files, so the scheduled prompt stays one stable line:

> Run the job-search daily run for the workspace at "~/Documents/Job Search".

The toolkit root is two levels above this skill's folder. The core rules in [job-search](../job-search/SKILL.md#core-rules) apply in both modes. If the prompt asks for "the job-search daily run", go straight to [Daily run](#daily-run).

## Set up

### 1. Check it's ready

Autopilot repeats something that already works; it does not replace setting it up. Before offering a schedule, check:

- The workspace exists and `lint` passes.
- `discovery/sources.md` exists, and the candidate agreed `rubric.md`.
- There has been one attended discovery run on those sources ([job-discover](../job-discover/SKILL.md)) in which every source worked, at least once, including every browser source (a source that hit a login page doesn't count), and the candidate looked at the inbox. That run is the rehearsal. If there hasn't been one, do it now, together, before going further.

If something is missing, say what, and fix it with them first.

### 2. Agree what it does

Ask in plain words, one or two questions at a time:

1. **Sources.** Should it check every source in `discovery/sources.md` each day, or only some of them on some days? Sources themselves (accounts, searches, new boards) are changed in `discovery/sources.md` through [job-discover](../job-discover/SKILL.md), not here.
2. **When.** Which days and roughly what time? The computer has to be awake, the agent app open, and the browser signed in at that time.
3. **What it may do.** The default is: find, screen and write a short summary. It never applies, messages anyone or changes anything on a job board.
   - Setup never turns on automatic applications, even if a scoped grant already exists in `policy.json` ([the application guide](../../docs/APPLY.md)). Adding `apply` is a later decision the candidate makes after reviewing at least one digest, so the check run in step 5 can never send an application.
4. **The summary.** How many roles at most, and whether a quiet day should be one line.

### 3. Write `autopilot.md`

Copy [the template](references/autopilot-template.md) into the workspace as `autopilot.md`, fill it from their answers, and show them the result in plain words. Refer to sources by their names in `discovery/sources.md`; don't copy their details. (`lint` doesn't check this file, so read it back once.)

### 4. Create the schedule in their host

Creating a schedule is a lasting change, so ask first and show exactly what will be created: the one-line prompt, the days and time, and which app runs it. Then follow [host scheduling](references/host-scheduling.md). Never use a cloud schedule: it can't see their workspace or their signed-in browser.

### 5. Check it

If the host can trigger the task once now, do that and read the digest together. Otherwise, check the first scheduled digest with them the next time they're in. Tell them:

- Where the inbox is (`discovery/inbox.md`) and that the daily summary appears in the host's task history.
- To pause, they can say "pause my job-search autopilot" (you set `Status: paused` in `autopilot.md`) or turn the task off in the host. To change timing or what runs daily, you update `autopilot.md` and, for timing, the host schedule. To change sources, you update `discovery/sources.md` with them; the next daily run picks it up.

## Daily run

Nobody is watching. Ask no questions. Anything that needs the candidate becomes an exception in the digest.

1. **Read the plan.** Read `autopilot.md`. If it is missing or says `Status: paused`, stop and reply with one line saying so.
2. **Recover first.** Run `doctor` and `tracker`. An uncertain application is never retried: list it as an exception. Read `discovery/state.json` for retries from earlier runs.
3. **Take the workspace lease.** Choose a run ID such as `autopilot-2030-01-15T0700` and run `lock <run ID>`. If another owner holds the lease, stop: report "a previous run still holds the lease" as an exception, with its run ID and start time from `tracker`, so the next attended session can recover it ([job-search](../job-search/SKILL.md#on-every-session)). Never clear it yourself; clearing needs evidence ([one execution owner](../../docs/APPLY.md#one-execution-owner)).
4. **Discover and screen.** Follow [job-discover](../job-discover/SKILL.md), which reads `discovery/sources.md`, limited to the sources `autopilot.md` says to check today. A login page, CAPTCHA or access block ends that source for today; it is an exception, not a reason to stop the run.
5. **Apply, only if allowed.** Skip this step unless `autopilot.md` lists `apply` under allowed actions **and** `policy.json` holds a scoped grant that is unexpired and valid for its selection mode, as [the application guide](../../docs/APPLY.md) describes (for `eligible_roles`, it must still match the current `rubric.md` and `search-preferences.md`). Then follow the full pipeline in [job-search](../job-search/SKILL.md#full-pipeline-when-asked) and [the application guide](../../docs/APPLY.md), within the per-run cap. Preparation and review must each run in a fresh separate context; if the host can't provide that, stop after preparation and list the role as awaiting review. Any sensitive question, new fact or mismatch holds that role as an exception.
6. **Release the lease** with `unlock <run ID>`, even when sources failed.
7. **Digest.** Reply with a short summary, which the host keeps in the task's history:
   - First line: coverage (**complete**, **partial** or **failed**), the number of new roles, and the inbox path ([run report](../job-discover/references/state-and-inbox.md#run-report)).
   - Saved roles and the top roles worth a look, each with a link, score and one-line reason, within the cap in `autopilot.md`.
   - Applications sent (only under a grant), with their recorded outcome.
   - **Needs you:** logins, CAPTCHAs, uncertain applications, conflicts to review, and proposed changes to sources or criteria.

   A quiet, fully covered day is one line.

Never change `autopilot.md`, `discovery/sources.md`, `search-preferences.md`, `rubric.md`, `policy.json` or the schedule during a daily run. Propose changes in the digest.
