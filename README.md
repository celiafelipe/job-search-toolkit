# Job Search Toolkit

**An AI job-search partner for senior leaders.** It learns your career once, in depth, then helps you screen roles, tailor a truthful CV for each one and keep track of every application. It works with Claude and Codex.

> Beta (v0.2). Built from a real executive job search, now being tested with a small group. Feedback is very welcome.

## Why it's different

Most AI CV tools rewrite your CV from a job ad. The result sounds generic and is often not quite true. This toolkit works the other way round:

1. **It builds a private career file first.** Starting from your CV or LinkedIn PDF, it creates one file per role. A guided career interview, modelled on the chronological "WHO" interview used in many executive hiring processes, then captures the context, numbers, stories and lessons that never fit on a CV.
2. **It learns with every job you discuss.** When you share a role, it tells you what in your background is strongest for it, and asks two or three questions about the gaps that matter. Your answers are saved, so every application makes the next one better.
3. **It never invents anything.** Every line on a tailored CV traces back to something you confirmed. You should be able to read it five minutes before an interview and recognize every word.
4. **It never applies without you.** By default it prepares everything and you send it. Automatic applications are an explicit opt-in with strict limits.

It is tuned for executive and senior roles (executive summary, key achievements, scope and business outcomes, two-page CVs), but it works at any level: you choose your career track during setup.

## Get started (about 20 minutes)

You don't need to be technical. Your AI assistant does the setup.

**With Claude Code** (in the terminal or the Code tab of the Claude desktop app):

```
/plugin marketplace add celiafelipe/job-search-toolkit
/plugin install job-search-toolkit@job-search-toolkit
```

Then say: **"Set up my job search."**

**With any other agent that can read files and run commands** (Codex, or Claude without plugins), say:

> Download the job search toolkit from github.com/celiafelipe/job-search-toolkit to my home folder, read its AGENTS.md, and set up my job search.

The assistant will:

1. Check your computer, and offer to install the one or two free tools it needs to make PDFs.
2. Create a private folder at `Documents/Job Search` that you can open in Finder or Files.
3. Ask for your CV or your LinkedIn profile as a PDF. (On LinkedIn: your profile → **Resources** → **Save to PDF**.) If you have old interview prep, performance reviews or a bio, drop them into the `sources` folder too.
4. Build your career files, then ask five short questions about what you're looking for.
5. Show you what's already strong and what's thin, and suggest the next step.

## What you can ask for

| Say something like | What happens |
| --- | --- |
| "Set up my job search" | First-time setup ([job-starter](skills/job-starter/SKILL.md)) |
| "Interview me about my career" / "Let's do my most recent role" | A 20-minute guided interview, one role at a time ([career-interview](skills/career-interview/SKILL.md)) |
| "Is this a good fit?" plus a job link or text | Verdict, what's strong, what's thin, two or three questions ([job-screen](skills/job-screen/SKILL.md)) |
| "Tailor my CV for this role" | A tailored CV and a checked PDF, with a summary of changes and interview talking points ([job-prepare](skills/job-prepare/SKILL.md)) |
| "I'd rather keep my own CV design" | Feedback on whether application systems can read your PDF and how strong the content is; you make any changes in your own tool, and it's never edited for you |
| "Find roles that match my criteria" | Searches the sources you approved and registers new postings ([job-discover](skills/job-discover/SKILL.md)) |
| "Check for new jobs every morning" | After a first search together, a daily run on your computer that leaves a short summary ([job-autopilot](skills/job-autopilot/SKILL.md)) |
| "Check this application before I send it" | An independent review in a fresh context ([job-review](skills/job-review/SKILL.md)) |
| "I applied to X" / "Where are my applications?" | Records and tracks applications and prevents duplicates ([job-track](skills/job-track/SKILL.md)) |
| "Apply for me" | Only after you explicitly grant permission for that exact action ([job-apply](skills/job-apply/SKILL.md), [rules](docs/APPLY.md)) |

## Your private folder

```
Documents/Job Search/
  profile.md              who you are, your career track, what to keep private
  master-cv.md            your master CV (never edited when tailoring)
  my-cv/                  or, if you prefer, your own designed CV PDF (never changed)
  career-story.md         the narrative that connects your roles
  experience/             one file per role: context, achievements, stories, lessons
  open-questions.md       gaps the assistant will ask about over time
  search-preferences.md   what you're looking for
  rubric.md               how roles are scored (your criteria, your weights)
  sources/                drop your CV, LinkedIn PDF and other material here
  roles/                  one folder per job: screening, tailored CV, PDF
  answer-policy.md        answers you approved for reuse on application forms
  config.json, policy.json, ledger.json, job-snapshots/
                          the assistant's bookkeeping: settings, application permissions
                          and history. You don't need to open these.
```

Everything stays on your computer. Your assistant's provider processes what you discuss with it under its own terms. The toolkit never sends your data to job boards, CV checkers or employers unless you ask.

## Requirements and limits

- **macOS or Linux.** Windows is not supported yet (WSL may work).
- Python 3.9 or newer (the one built into macOS works), plus Google Chrome or Chromium and Poppler for PDF export. The setup checks these and offers to install anything missing.
- The toolkit doesn't log in to job sites, solve CAPTCHAs or bypass any site's rules. When a site needs a login, it hands over to you.
- PDF export runs Chrome headless with a fresh profile and networking blocked, so your CV never leaves your computer during the build. In Linux containers running as root, Chrome's sandbox is disabled for this local page only. If `doctor` reports that the test export fails, it prints the fix (often installing Chrome's lightweight headless build).
- The PDF uses a clean single-column layout designed to be read correctly by applicant tracking systems. No tool can guarantee how a specific employer's system parses it.

## For developers

The skills are plain Markdown (`skills/*/SKILL.md`). One folder serves both Claude (`.claude-plugin/`) and Codex (`.codex-plugin/`). A small Python CLI (`python3 -m toolkit`) handles the local workspace, PDF build and checks, and an application ledger that prevents duplicate or unauthorized submissions. See [the technical contracts](docs/WORKFLOW.md), [the application rules](docs/APPLY.md) and [the learning loop](docs/LEARNING-LOOP.md).

```sh
python3 -m unittest discover -s tests   # tests (the PDF test needs Chrome and Poppler)
python3 examples/demo.py "$(mktemp -d)/private"   # fictional offline walkthrough
python3 tools/privacy_check.py          # run before every commit: no personal data in the repo
```

Contributions are welcome. Keep every example fictional and use reserved domains such as `example.org`. MIT licensed.
