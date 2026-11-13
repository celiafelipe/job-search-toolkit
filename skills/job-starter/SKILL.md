---
name: job-starter
description: First-time setup for the job search toolkit. Use when someone says "set up my job search", "get started", "start my job search", shares their CV or LinkedIn profile for the first time, or has no job-search workspace yet. Checks and installs what is needed, creates a private folder, imports their CV or LinkedIn PDF into structured career files, asks a few questions about what they are looking for, and shows what to do next. Designed for non-technical people; the agent does all the technical work.
---

# Job starter

Get a new person from zero to a useful setup in about 20 minutes, without asking them to touch a terminal or fill templates by hand. Speak plainly. Do one step at a time and say what you are doing.

## 0. Welcome and promises

Introduce the toolkit in two or three sentences, and make these promises:

- Their information stays in a private folder on their computer.
- You never invent experience, numbers or answers. You ask, and you only use what they confirm.
- Nothing is sent to any employer without their explicit permission for that specific application.

Tell them the setup gets them started quickly, and that their career file improves every time you discuss a job together. They do not need to write everything down up front.

## 1. Check the computer (you do this, silently if all is well)

The toolkit root is the folder containing `toolkit/` and `skills/`, two levels above this skill's folder. Run commands from there:

```sh
python3 -m toolkit doctor
```

- If `python3` is missing or older than 3.10, explain and help install it (macOS: `xcode-select --install` or python.org; Linux: the package manager).
- If `pdf_ready` is false, show the `fix` hints from `doctor` in plain words and offer to run the install command for them. Ask permission before installing anything.
- Windows is not supported yet; suggest WSL or a Mac or Linux machine.
- PDF tools are only needed for the final CV PDF. Setup can continue without them.

## 2. Create their private folder

Suggest the default `~/Documents/Job Search`, a visible folder they can open in Finder or Files. If they want another place, use `--workspace "<path>"` (it must not be inside a Git repository). If `doctor` says the workspace already exists, do not re-initialize it: switch to [job-search](../job-search/SKILL.md).

```sh
python3 -m toolkit --workspace "<path>" init
```

Tell them that if they keep the folder somewhere else, they should say so at the start of future conversations, or store it in their agent's memory.

## 3. Collect what they already have

Ask for whatever is easiest, in this order of preference. Any one of these is enough to start:

1. **Their CV** (PDF, Word or text). Ask them to drop it into the `sources/` folder or attach it.
2. **Their LinkedIn profile as a PDF.** On LinkedIn: open your profile → **Resources** (or **More**) → **Save to PDF**. Do not try to log in to LinkedIn or scrape it. A public profile link is fine to read if your tools can open it, but the PDF is more reliable.
3. **Anything richer they already have:** past performance reviews, promotion cases, interview preparation notes (for example WHO or Topgrading prep), a bio or portfolio. Put them in `sources/` too.

Read every source fully. If a file cannot be read, say so rather than guessing at its contents.

## 4. Build their career files

From the sources, create:

- **`experience/YYYY-organization.md`**, one per role, from `experience/_role-template.md`. Fill only what the sources state. Note the source in each file's provenance log, e.g. `from CV (sources/cv.pdf), not yet confirmed`.
- **`experience/INDEX.md`**: one row per role with a depth rating. Most roles start as `thin`.
- **`master-cv.md`** in the supported format (headings, paragraphs, dash lists, `**bold**`), following [the CV craft guide](../job-prepare/references/cv-craft.md). Transcribe faithfully: this is their master copy, not a tailored version. Never edit their original file in `sources/`.
- **`profile.md`**: name, contact details, languages, and the career track (`executive`, `senior` or `standard`), inferred from titles and scope and then confirmed with them.
- **`career-story.md`**: a short draft of their positioning and career arc, clearly marked as a draft for them to react to.

Then show a short summary: the roles found, the dates, and anything that looked inconsistent (overlapping dates, missing years, titles that differ between the CV and LinkedIn). Ask them to confirm or correct it. Record their corrections.

## 5. Five questions about what they want

Ask one or two at a time, conversationally. Do not present the template.

1. What roles and level are you aiming for? Is anything a stretch or a pivot?
2. Where can you work: location, remote, hybrid, travel?
3. What would make you say no straight away (your deal-breakers)?
4. What kind of company excites you (stage, size, industry, mission)?
5. Do you want to set a compensation floor? (Optional. Keep it private and never put it in an application without asking.)

Write `search-preferences.md`. Draft `rubric.md` with weights totalling 100 and pursue/hold/skip thresholds, show it to them in plain words ("I'd score a role mostly on X and Y; a role in Z would be a hard no"), and adjust it until they agree. The rubric is theirs, not yours.

## 6. Show what's strong and what's thin

Give a short health check:

- Two or three things that already stand out in their background.
- Which roles are `thin` and why that matters, e.g. "your most recent role has no numbers yet, and that's the one recruiters read first".
- Add the most valuable gaps to `open-questions.md`. Do not ask them all now.

## 7. Offer the next step

Offer two paths and let them choose:

- **Career interview (recommended, about 20 minutes per role):** start with their most recent role. See [career-interview](../career-interview/SKILL.md). This is the fastest way to a strong CV.
- **Jump into a real job:** paste a job ad or link, and you will screen it ([job-screen](../job-screen/SKILL.md)). You will tell them what's strong for that role and ask about the gaps that matter, so their career file grows with every job ([learning loop](../../docs/LEARNING-LOOP.md)).

## Rules

- Never ask them to run commands or edit JSON. If an action needs their computer password (for example installing software), explain why and let them run that one step.
- Do not import another candidate's files or policies. The default application policy is preparation only; changing it is a separate, explicit decision covered in [the application guide](../../docs/APPLY.md).
- Do not put any of their data inside the toolkit folder or a Git repository.
