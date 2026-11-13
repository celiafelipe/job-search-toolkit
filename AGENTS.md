# Agent guide

This repository is a toolkit of agent skills (`skills/*/SKILL.md`) plus a small local Python CLI (`toolkit/`). The same `skills/` folder serves Claude (`.claude-plugin/`) and Codex (`.codex-plugin/`). Do not fork the skills per host.

## When you are helping someone with their job search

- Start with `skills/job-starter/SKILL.md` if the person has no workspace yet. Otherwise use `skills/job-search/SKILL.md`, which routes to the right stage.
- The person may not be technical. You run the commands, read and write the files, and explain in plain language. Never ask them to run Python, edit JSON or compute hashes.
- The toolkit root is the folder that contains `toolkit/` and `skills/`. Run CLI commands from there: `python3 -m toolkit --workspace "<workspace>" <command>`.
- The candidate's data lives in their private workspace (default `~/Documents/Job Search`), never in this repository.
- Never invent experience, numbers or answers. Ask, then record what the person confirms, with a date, in the right experience file. That is the learning loop in `docs/LEARNING-LOOP.md`.
- Nothing is sent to an employer without the person's explicit permission for that exact action (`docs/APPLY.md`).

## When you are changing this repository

- Run `python3 -m unittest discover -s tests` and `python3 tools/privacy_check.py` before proposing a commit.
- Keep all examples fictional and use reserved domains (`example.org`, `*.example`). No real names, employers or personal paths.
- Skill files stay host-neutral Markdown with `name` and `description` frontmatter.
