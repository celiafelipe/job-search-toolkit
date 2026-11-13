---
name: job-search
description: Entry point and coordinator for the job search toolkit. Use for any job-search request when it's unclear which stage applies, such as "help with my job search", "find me jobs", "what should I apply to", "where are my applications" or "continue my job search". Routes to setup, career interview, discovery, screening, CV tailoring, review, application or tracking.
---

# Job search

The toolkit root is two levels above this skill's folder (it contains `toolkit/`). The candidate's workspace is `~/Documents/Job Search` unless they said otherwise. The candidate may not be technical: you run the commands, read and write the files, and explain in plain language.

## Route the request

| Situation | Go to |
| --- | --- |
| No workspace yet, or "get started" | [job-starter](../job-starter/SKILL.md) |
| Wants to strengthen their profile, or the experience files are thin | [career-interview](../career-interview/SKILL.md) |
| Wants new roles found or a list of links checked | [job-discover](../job-discover/SKILL.md) |
| Shares a job and asks if it fits | [job-screen](../job-screen/SKILL.md) |
| Wants a tailored CV, cover letter or answers | [job-prepare](../job-prepare/SKILL.md) |
| A package needs checking before sending | [job-review](../job-review/SKILL.md), in a fresh separate context |
| Wants the toolkit to fill in or submit a form | [job-apply](../job-apply/SKILL.md), only with explicit permission |
| Applied already, or asks about status | [job-track](../job-track/SKILL.md) |

A request for one stage ends at that stage unless they ask for more.

## On every session

- Check that the workspace exists (`python3 -m toolkit --workspace "<path>" doctor` reports `workspace_exists`).
- Read the tracker (`python3 -m toolkit --workspace "<path>" tracker`). Before anything new, reconcile any uncertain application: never retry it.
- Glance at `open-questions.md`. If a gap matters for today's work, ask about it as part of the [learning loop](../../docs/LEARNING-LOOP.md).

## Full pipeline (when asked)

1. Discover and screen. Rank eligible roles by objective score, and note roles the candidate prioritized separately.
2. For the chosen roles, inspect the application form read-only ([job-apply](../job-apply/SKILL.md)), then prepare the package in a fresh context and review it in a different fresh context.
3. By default, stop at a ready-to-send package for the candidate. Submission requires their explicit permission and the checks in [the application guide](../../docs/APPLY.md).
4. Record outcomes with [job-track](../job-track/SKILL.md).

## Report back

Report what was found, what was screened (with the verdict and a one-line reason for each), what is prepared and where the files are, anything sent (only with permission), and what's next. Keep it short. Do not infer timing, authorization or browser identity from examples.
