# Autopilot

How the scheduled daily run behaves. Which sources exist and how to read them is in `discovery/sources.md`; this file only says when to run, which of those sources to check, and what the run may do.

Status: active
Set up: 2030-01-15, after the rehearsal run of 2030-01-14
Schedule: weekdays around 07:00, in the host's scheduled tasks (local, not cloud)

## Sources to check each run

All sources in `discovery/sources.md`, unless listed otherwise here. (Example: "Skip `career-pages` on weekdays; check them on Mondays only.")

## Allowed actions

- discover
- screen
- digest

Add `apply` only if `policy.json` holds a scoped grant (see `docs/APPLY.md` in the toolkit). Maximum applications per run: 0.

## Digest

- At most 5 roles worth a look, saved roles first.
- A quiet, fully covered day is one line.

## Personal additions

Anything specific to this candidate's daily run that the generic skills don't cover. The daily run follows it as long as it stays within the allowed actions above.
