# Job Search Toolkit

**An AI job-search partner for senior leaders.** It learns your career once, in depth, then helps you find and screen roles, tailor a truthful CV for each one and keep track of every application. It works with Claude and Codex.

Created by [Celia Felipe](https://www.linkedin.com/in/celiafelipe) · MIT licensed · Beta (v0.2)

[Install](#install) · [How it works](#how-it-works) · [Skills](#skills) · [Autopilot](#autopilot-a-daily-job-search-run) · [Privacy](#your-private-folder) · [For developers](#for-developers)

> Built from a real executive job search and now being tested with a small group. Feedback is very welcome: [open an issue](https://github.com/celiafelipe/job-search-toolkit/issues).

## Why it's different

Most AI CV tools rewrite your CV from a job ad. The result sounds generic and is often not quite true. This toolkit works the other way round:

1. **It builds a private career file first.** Starting from your CV or LinkedIn PDF, it creates one file per role. A guided career interview, modelled on the chronological "WHO" interview used in many executive hiring processes, then captures the context, numbers, stories and lessons that never fit on a CV.
2. **It learns with every job you discuss.** When you share a role, it tells you what in your background is strongest for it, and asks two or three questions about the gaps that matter. Your answers are saved, so every application makes the next one better.
3. **It never invents anything.** Every line on a tailored CV traces back to something you confirmed. You should be able to read it five minutes before an interview and recognize every word.
4. **It never applies without you.** By default it prepares everything and you send it. Automatic applications are an explicit opt-in with strict limits.

It is tuned for executive and senior roles (executive summary, key achievements, scope and business outcomes, two-page CVs), but it works at any level: you choose your career track during setup.

## Install

You don't need to be technical. Install the plugin, then say **"Set up my job search."** Your assistant does the rest (about 20 minutes).

### Claude desktop app (Cowork or the Code tab)

1. Open the plugins screen and choose to add a marketplace.
2. Enter `celiafelipe/job-search-toolkit`.
3. Install **job-search-toolkit** from that marketplace, then start a new conversation.

### Claude Code (terminal)

```bash
claude plugin marketplace add celiafelipe/job-search-toolkit
claude plugin install job-search-toolkit@job-search-toolkit
```

Or, inside a Claude Code session: `/plugin marketplace add celiafelipe/job-search-toolkit`, then `/plugin install job-search-toolkit@job-search-toolkit`.

### Codex (app or CLI)

```bash
codex plugin marketplace add celiafelipe/job-search-toolkit
```

Then open the Plugins Directory in the Codex app (or `/plugins` in the CLI), choose the **Job Search Toolkit** marketplace and install it.

### Any other agent

Any assistant that can read files and run commands works. Say:

> Download the job search toolkit from github.com/celiafelipe/job-search-toolkit to my home folder, read its AGENTS.md, and set up my job search.

### What setup does

1. Checks your computer and offers to install the one or two free tools it needs to make PDFs.
2. Creates a private folder at `Documents/Job Search` that you can open in Finder or Files.
3. Asks for your CV or your LinkedIn profile as a PDF. (On LinkedIn: your profile → **Resources** → **Save to PDF**.) Old interview prep, performance reviews or a bio can go in the `sources` folder too.
4. Builds your career files, then asks five short questions about what you're looking for.
5. Shows you what's already strong and what's thin, and suggests the next step.

### Staying up to date

The toolkit is improving quickly. See [what's new](CHANGELOG.md) in each version.

- **Get updates automatically (recommended):** your app won't update the plugin on its own unless you switch this on. In Claude Code, run `/plugin`, open **Marketplaces**, choose **job-search-toolkit** and turn on auto-update. New versions then arrive the next time you start Claude.
- **Update by hand:** refresh the marketplace in your app, or run `claude plugin marketplace update job-search-toolkit` (Claude Code) or `codex plugin marketplace upgrade job-search-toolkit` (Codex). Then start a new conversation.

Not sure which version you have? Ask your assistant: "Which version of the job search toolkit am I using?"

## How it works

You talk to one assistant in plain language; it picks the right skill for each step. Your career file sits in the middle: every skill reads from it, and every job you screen adds to it.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/how-it-works-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/how-it-works-light.png">
    <img src="assets/how-it-works-light.png" width="760" alt="How Job Search Toolkit works. You ask in plain language and job-search, the front door, opens the right skill. Everything happens in a private folder on your computer. Once, at the start: 1 job-starter sets up and creates your career file; 2 career-interview deepens it. For each job: 3 job-discover finds roles; 4 job-screen gives a pursue, hold or skip verdict, reads your career file and adds your answers to it; 5 job-prepare reads your career file to write a tailored, truthful CV; 6 job-review checks it independently; 7 you send it yourself, or job-apply sends it only with your explicit permission; 8 job-track records every application. Optional job-autopilot repeats discovery and screening every day and never applies or contacts anyone.">
  </picture>
</p>

## Skills

| Skill | What it does | Say something like |
| --- | --- | --- |
| [job-search](skills/job-search/SKILL.md) | Entry point. Works out where you are and routes to the right step. | "Help with my job search" / "Continue my job search" |
| [job-starter](skills/job-starter/SKILL.md) | First-time setup: checks your computer, creates your private folder, imports your CV or LinkedIn PDF, asks what you're looking for, and shows your CV in each of the three templates so you can pick a look and colour. | "Set up my job search" / "Show me the CV templates" |
| [career-interview](skills/career-interview/SKILL.md) | A 20-minute guided interview, one role at a time, that captures the stories and numbers behind your CV. | "Interview me about my career" / "Let's do my most recent role" |
| [job-discover](skills/job-discover/SKILL.md) | Finds postings from links you share, saved jobs, job alert emails, approved job boards and career pages. Removes duplicates and writes a ranked inbox. | "Find roles that match my criteria" / "Check my job alerts" |
| [job-screen](skills/job-screen/SKILL.md) | Pursue, hold or skip verdict against your own criteria, what's strong, what's thin, and two or three questions to fill the gaps. | "Is this a good fit?" plus a link or text |
| [job-prepare](skills/job-prepare/SKILL.md) | A tailored, truthful CV and a checked PDF in the template you chose (editorial, gutter or banner), with a summary of changes and interview talking points. Cover letter or form answers only if the application needs them. If you keep your own CV design, it gives feedback instead and never edits your file. | "Tailor my CV for this role" / "Use the banner template in teal" / "I'd rather keep my own CV design" |
| [job-review](skills/job-review/SKILL.md) | An independent review in a fresh context: evidence, exact answers, PDF rendering and whether application systems can read it. | "Check this application before I send it" |
| [job-apply](skills/job-apply/SKILL.md) | Fills and submits an application form, only for the exact actions you've authorized ([rules](docs/APPLY.md)). | "Apply for me" |
| [job-track](skills/job-track/SKILL.md) | Records applications, prevents duplicates and shows where everything stands. | "I applied to X" / "Where are my applications?" |
| [job-autopilot](skills/job-autopilot/SKILL.md) | Sets up and runs a daily unattended search on your computer. | "Check for new jobs every morning" / "Pause my autopilot" |

## Autopilot: a daily job-search run

Once discovery works well with you watching, the assistant can repeat it on a schedule: every morning it checks your sources, screens what's new against your criteria and leaves a short digest. A quiet day is one line.

**How to set it up**

1. Do one discovery run together first (*"Find roles that match my criteria"*). Every source has to work once, including job sites you're signed in to. This is the rehearsal.
2. Say *"Check for new jobs every morning."* The assistant asks which sources to check, which days and time, and how long the summary should be, and writes it all into `autopilot.md` in your folder.
3. It creates a **scheduled task** in your app (after you say yes), with one fixed prompt:
   > Run the job-search daily run for the workspace at "~/Documents/Job Search".
4. It runs the task once with you and you read the first digest together.

**Where it can run**

| App | Works? |
| --- | --- |
| Claude desktop app scheduled tasks (Cowork or the Code tab) | Yes, runs on your computer |
| Codex app Automations | Yes, runs on your computer |
| Cloud schedules (for example Claude Code cloud routines) | No: they can't see your private folder or your signed-in browser |

**What it will and won't do**

- It finds, screens and summarizes. It never applies, messages anyone or changes anything on a job board, unless you later grant a separate, limited permission to apply.
- Your computer must be on and awake, the app open, and your browser signed in at the scheduled time. A missed day is covered by the next run.
- Logins, CAPTCHAs and anything else that needs you go under **Needs you** in the digest.
- To stop, say *"Pause my job-search autopilot"* or turn the task off in your app.

Details: [host scheduling](skills/job-autopilot/references/host-scheduling.md).

## Your private folder

```
Documents/Job Search/
  profile.md              who you are, your career track, what to keep private
  master-cv.md            your master CV (never edited when tailoring)
  cv-style.json           the CV template and accent colour you picked
  my-cv/                  or, if you prefer, your own designed CV PDF (never changed)
  career-story.md         the narrative that connects your roles
  experience/             one file per role: context, achievements, stories, lessons
  open-questions.md       gaps the assistant will ask about over time
  search-preferences.md   what you're looking for
  rubric.md               how roles are scored (your criteria, your weights)
  sources/                drop your CV, LinkedIn PDF and other material here
  discovery/              where to look for jobs, and the ranked inbox of new roles
  autopilot.md            your daily run settings, if you use autopilot
  roles/                  one folder per job: screening, tailored CV, PDF
  answer-policy.md        answers you approved for reuse on application forms
  config.json, policy.json, ledger.json, job-snapshots/
                          the assistant's bookkeeping: settings, application permissions
                          and history. You don't need to open these.
```

Everything stays on your computer. Your assistant's provider processes what you discuss with it under its own terms. The toolkit never sends your data to job boards, CV checkers or employers unless you ask.

## Requirements and limits

- **macOS or Linux.** Windows is not supported yet (WSL may work).
- Python 3.9 or newer (the one built into macOS works), plus Google Chrome or Chromium and Poppler for PDF export. Setup checks these and offers to install anything missing.
- The toolkit doesn't log in to job sites, solve CAPTCHAs or bypass any site's rules. When a site needs a login, it hands over to you.
- PDF export runs Chrome headless with a fresh profile and networking blocked, so your CV never leaves your computer during the build. In Linux containers running as root, Chrome's sandbox is disabled for this local page only. If `doctor` reports that the test export fails, it prints the fix (often installing Chrome's lightweight headless build).
- The PDF comes in three templates (editorial, gutter and banner) with six accent colours or your own. All three keep a single-column layout, inline dates and plain-text skills so applicant tracking systems read them in the right order, and every build checks that the PDF text reads back in order. No tool can guarantee how a specific employer's system parses it.

## For developers

The skills are plain Markdown (`skills/*/SKILL.md`). One folder serves both Claude (`.claude-plugin/`) and Codex (`.codex-plugin/`, listed through `.agents/plugins/marketplace.json`). A small Python CLI (`python3 -m toolkit`) handles the local workspace, PDF build and checks, and an application ledger that prevents duplicate or unauthorized submissions. See [the technical contracts](docs/WORKFLOW.md), [the application rules](docs/APPLY.md) and [the learning loop](docs/LEARNING-LOOP.md).

```sh
python3 -m unittest discover -s tests   # tests (the PDF test needs Chrome and Poppler)
python3 examples/demo.py "$(mktemp -d)/private"   # fictional offline walkthrough
python3 tools/privacy_check.py          # run before every commit: no personal data in the repo
python3 tools/check_version_bump.py     # user-facing changes need a new version
```

**Releasing an update.** Installed copies only update when the version number changes. For every release, raise `version` in both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` (0.3.1 for fixes, 0.4.0 for new features) and add a matching section to [CHANGELOG.md](CHANGELOG.md). `tests/test_version.py` checks that the two match and are in the changelog, and `tools/check_version_bump.py` (also run on every pull request) fails if user-facing files changed without a new version.

Contributions are welcome. Keep every example fictional and use reserved domains such as `example.org`.

## License

MIT. Created by [Celia Felipe](https://www.linkedin.com/in/celiafelipe).
