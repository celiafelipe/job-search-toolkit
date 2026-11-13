---
name: job-prepare
description: Tailor a truthful, role-specific CV (and a cover letter or form answers only if the application requires them) from the candidate's confirmed career evidence, then build a checked PDF. Use when someone says "tailor my CV for this job", "prepare my application" or "write a cover letter for this role", or after a pursue verdict from job-screen.
---

# Job prepare

The toolkit root is two levels above this skill's folder. The workspace defaults to `~/Documents/Job Search`. You run every command and handle every file; the candidate only reads, answers and approves.

Read [the CV craft guide](references/cv-craft.md) before writing. It is the standard for structure, tone by career track, bullets, headlines and anti-patterns.

## Inputs

- The job posting and the screening (run [job-screen](../job-screen/SKILL.md) first if there isn't one).
- `profile.md` (career track, contact details, what to keep private), `master-cv.md`, `career-story.md`, and the experience files.
- If a real application form will be used: its observed questions and attachment rules. Without them, prepare a provisional draft and mark form constraints as unknown.

For an application that will go through the full reviewed workflow, work in a fresh context separate from the reviewer, per [the package contract](../../docs/WORKFLOW.md).

## Steps

1. **Map the evidence.** List the job's must-haves. For each, find the strongest supported evidence across all roles, including older ones, and rate it direct, adjacent, unsupported or candidate-suggested. Save this as `roles/<role-id>/evidence-map.md`.
2. **Close the important gaps first.** If a must-have only has thin evidence, run [the learning loop](../../docs/LEARNING-LOOP.md) before writing: share what's strong, ask two or three questions, and record what they confirm. Don't write around a gap you could ask about.
3. **Tailor the CV.** Copy `master-cv.md` to `roles/<role-id>/cv.md` and apply the tailoring steps and limits in the CV craft guide. Keep their voice, and never edit the master or `sources/`.
4. **Show the changes.** Give a short summary of what changed and why, the strongest three matches, and two or three interview talking points. Ask for their reaction, and revise until they're happy. They must recognize every line.
5. **Cover letter, only if required:** three short paragraphs with two or three specific, evidenced connections to the employer's needs. No generic motivation, and no repeating the CV. Match the required format and length.
6. **Form answers:** record each exact prompt, the proposed value and its source, in `answers.json`. Leave unsupported optional fields empty, and raise unanswered required fields with the candidate rather than guessing. Use `answer-policy.md` for previously confirmed answers within their exact scope.
7. **Build the PDF:**

   ```sh
   python3 -m toolkit --workspace "<workspace>" build-pdf roles/<role-id>/cv.md roles/<role-id>/cv-build --kind cv
   ```

   Use a new output folder for each build. Open `page-*.png` yourself and check the layout, page breaks and that nothing is clipped. Tell the candidate where the PDF is (`cv-build/document.pdf`). If the PDF tools are missing, run `doctor` and offer the fix.

## Hand off

For an actual submission, hand the package to an independent reviewer ([job-review](../job-review/SKILL.md)) in a separate fresh context. If the candidate will submit it themselves, they can use the PDF directly. Remind them the toolkit can record the application once they've sent it ([job-track](../job-track/SKILL.md)).

Stay offline in this stage: no form entry, uploads or applications, and no policy or tracker changes.
