# CV craft

How to write and tailor a CV that is truthful, readable by applicant tracking systems (ATS), and persuasive to a human. Read the candidate's career track in `profile.md` first.

## The golden rule

The candidate should be able to read the tailored CV five minutes before an interview and say: "Yes, this is all true, and I remember these details." Tailoring means choosing, ordering and phrasing evidence. It never means adding things that aren't in the experience files.

## Structure

1. **Name and header line:** a headline, location and contact details.
2. **Executive summary** (executive and senior tracks), or a short profile: three or four lines.
3. **Key achievements** (executive track; optional for senior): three to five bolded, quantified results across their career.
4. **Experience:** most recent first. For each role: a heading `Role | Organization | Start – End`, one line of context (what the organization is, and the scope: team, budget, products, markets), then the bullets.
5. **Education, skills and languages.**

Supported format: `#` to `###` headings, plain paragraphs, `- ` lists and `**bold**`. Nothing else: no tables, links, italics or images. This keeps the PDF readable by ATS parsers.

## By career track

| | Executive | Senior | Standard |
| --- | --- | --- | --- |
| Length | 2 pages (up to 3 for long careers) | 2 pages | 1–2 pages |
| Opening | Executive summary plus key achievements | Summary, optional key achievements | Short profile |
| Bullets per recent role | 4–6 | 4–6 | 3–5 |
| Emphasis | Strategy, scale, business outcomes, transformation, leadership of leaders, board and investor exposure | Ownership, team leadership, cross-functional delivery, measurable impact | Skills, delivery, results, growth |
| Older roles (10+ years ago) | One line of context, 0–2 bullets, or grouped under "Earlier career" | Same | Keep if relevant |

## Key achievements

Three to five results that together show range: pick from different roles and different strengths (for example growth, scale, people, transformation). Phrase each as a career-level headline, not a copy of a role bullet: if an achievement also appears under its role, the role bullet gives the how and the detail, and the key achievement gives the one-line result. No two lines on the page should read almost the same.

## Writing bullets

- **Lead with the outcome**, then how, then scope: "**Grew net revenue 35% in 18 months** by repositioning pricing for three customer segments; led a team of 12."
- Use the employer's vocabulary only where it accurately describes the work.
- Numbers need a baseline, a period and a source in the experience file. If there is no confirmed number, write a qualitative outcome instead. Never estimate.
- Keep "I" and "we" honest. Use "led", "owned" and "built" only when the experience file says so.
- One idea per bullet, and one or two lines at most.
- Bold sparingly: the result in each key bullet, never whole sentences.

## Voice and details

- **One voice throughout.** No "I", "me" or "my" anywhere, including the summary: "Builds engineering organizations that…" or a verbless phrase, not "I build teams…".
- **Keep the header line short** so it fits on one line: location, email, phone and one profile link. Drop anything else, or put the link on a second line on purpose.
- **Skills line by level.** For executive and senior candidates, list leadership and domain areas the bullets evidence (for example "Platform strategy, M&A integration, P&L ownership"). Leave detailed tools and languages out unless the role asks for them.

## Headline and location

- Match the headline to the **level of the target role**. Never claim more than the candidate holds; a broader framing is fine if the experience supports it. For example, someone who has been a Chief X Officer can present as "X Executive" or "X Leader" for a VP or Head-of role. Someone who has never held a C-level title must not present as one.
- On a targeted application, show one base location plus a relocation or remote signal relevant to the job. Never imply they live somewhere they don't.

## Tailoring a CV for a role

1. Start from a copy of `master-cv.md` in the role folder. Never edit the master or anything in `sources/`.
2. Pick the three to five strongest matches for the job's must-haves, including from older roles, using the experience files rather than only the master CV.
3. Reorder bullets so the strongest matches come first in each role, and the best overall match shows up in the summary or key achievements.
4. Adjust the context line of a role to surface the relevant scope (industry, stage, team size), if the experience file supports it.
5. Swap in a better-matching accomplishment from the experience files if one exists and is confirmed.

**Limit the changes.** Tailoring a role CV typically changes no more than 15–20% of the master's content, and the summary keeps most of the candidate's own wording. A CV that reads like a different person is a red flag in interviews.

**Structural upgrades belong in the master, not the role CV.** If the master is missing something its career track needs (for example an executive summary or key achievements section), or is still at import quality, do not add it per role. Propose an update to `master-cv.md` first (see "Keeping the master current" below), get approval, then tailor from the improved master.

## Keeping the master current

The master CV improves as the experience files grow. After a career interview, or when the learning loop adds a strong new proof point, propose specific changes to `master-cv.md`: what to add, replace or reorder, and why. Apply them only after the candidate approves. Before changing it, copy the current version to `sources/master-cv-YYYY-MM-DD.md` so nothing is lost. Never edit the candidate's original files in `sources/`.

## Anti-patterns (instant discard signals)

- **A summary that echoes the job description.** Screeners spot JD-parroting immediately. Keep the candidate's voice; you may adjust one phrase or add one natural sentence that connects to the company.
- **Self-labelling adjectives** ("data-driven", "visionary", "results-oriented"). Let the bullets prove it.
- **Em dashes and other AI writing tells**: "spearheaded", "leveraged synergies", "in today's fast-paced world". Use commas, colons or parentheses instead of em dashes.
- **Keyword stuffing** or a long skills list of things that aren't evidenced elsewhere.
- **Invented or rounded-up metrics.**

## Special cases

- **Vague job description:** keep the changes minimal and tailor to the industry, stage and level only.
- **The master CV already matches well:** say so, and offer three to five small tweaks or the master as-is.
- **A must-have isn't evidenced:** run the [learning loop](../../../docs/LEARNING-LOOP.md) and ask about it. If it's still not there, options are adjacent experience framed honestly, addressing it in a cover letter, or skipping the role. Never fill the gap.
- **The master CV is weak or missing sections its track needs:** improve the master first (career interview, then a master update), rather than polishing a weak base per role.

## Before handing off

- [ ] Every claim traces to an experience file or a dated candidate confirmation.
- [ ] No metric was changed, rounded up or invented.
- [ ] The candidate would recognize every line.
- [ ] The strongest match for the job is visible in the first third of page one.
- [ ] The length fits the track, and there are no em dashes or self-labels.
- [ ] A short change summary lists what changed and why, plus two or three interview talking points.
