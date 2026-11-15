# Host scheduling

The workspace and the signed-in browser are on the candidate's computer, so the schedule must run there too. Menus change between versions: if what you see differs from these steps, follow the host's current interface and say what you did.

The prompt is always the same single line, with the real workspace path:

> Run the job-search daily run for the workspace at "~/Documents/Job Search".

## What works

| Host | Works? | Notes |
| --- | --- | --- |
| Codex app Automations | Yes | Runs locally on the project. The app must be open and the computer awake. |
| Claude desktop app scheduled tasks (Cowork or the Code tab) | Yes | Runs locally. You can create it when the candidate asks. Reaches the browser through the browser extension connection. |
| Cloud schedules (for example Claude Code's cloud routines) | No | Runs on a remote machine: no access to the workspace or the signed-in browser. |
| A loop or timer inside an open chat | Only while that chat stays open | Fine for a test, not for a daily schedule. |
| Operating-system timers running the agent headless | Not recommended | Technical to set up and has no signed-in browser. |

## Codex app

1. Make sure the toolkit plugin is installed and the workspace folder is reachable from the project the automation will run in.
2. Create an automation for that project with the one-line prompt, the agreed days and time, and local execution.
3. Check that the automation is allowed to use the browser connection the rehearsal used.
4. Run it once now if the app offers that, and read the result together.

## Claude desktop app

1. Make sure the toolkit plugin is installed and the browser extension is connected to the browser account used in the rehearsal.
2. Create a scheduled task with the one-line prompt, the agreed days and time, and a working folder that can reach both the toolkit and the workspace. If your tools can create scheduled tasks, do it after the candidate says yes; otherwise walk them through the app's scheduled tasks screen.
3. Run it once now if the app offers that, and read the result together.

## Before you finish

Tell the candidate, in plain words:

- The computer must be on and awake, the agent app open, and the browser signed in at the scheduled time. If it isn't, that day's run is skipped or partial, and the next run covers the gap.
- Being signed in once does not guarantee staying signed in. A run that hits a login page reports it and carries on with other sources.
- How to pause it, change it, or remove it.
