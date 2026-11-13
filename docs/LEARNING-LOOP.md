# The learning loop

A CV is only as good as the evidence behind it, and nobody writes all their evidence down up front. The toolkit therefore grows the candidate's career file a little every time a job is discussed. Every skill that reads a job description follows this loop.

## The loop

1. **Match.** Compare the job's must-haves with the experience files. Find the strongest specific evidence for each one, including older roles.
2. **Tell them what's strong.** In two to four bullets, say what in their background fits this job best and why, citing the role and the accomplishment.
3. **Name what's thin.** Say which important requirements have no evidence, only adjacent evidence, or evidence without scope or numbers.
4. **Ask two or three targeted questions.** Pick the gaps that would most change the outcome for this job. Make them concrete and easy to answer:
   - "The role asks for building a team from scratch. In your time at Org B, did you hire the team? Roughly how many people?"
   - "You led the pricing change at Org A. Do you remember the effect on revenue or conversion, even roughly, and over what period?"
   - "Have you worked with a board or investors directly? In which role?"

   Also ask once: "Is there anything else from your experience that's relevant here and that I might not know about?"
5. **Record what they confirm.** Write each answer into the right `experience/` file in the right section, in their words where possible, with a provenance line (format below). Update the depth in `experience/INDEX.md` when the role now meets the next level's definition there. Remove answered items from `open-questions.md`, and add new gaps you noticed but didn't ask about.
6. **Use it.** Only now draft or score using the new evidence.

## Provenance lines

Every experience file ends with a provenance log. Every skill writes the same format, one line per source event, starting with the date:

```
- YYYY-MM-DD | <source> | <status> | <what it covers>
```

- **source:** `CV import (sources/<file>)`, `LinkedIn import (sources/<file>)`, `career interview`, `screening <role-id>` (for a quick verdict on an unregistered job, `screening <Employer>, <Role title>`), or `prepare <role-id>`.
- **status:** `unconfirmed` (imported, not yet checked with the candidate), `confirmed by candidate`, or `corrected by candidate`.
- **what it covers:** a few words, e.g. `team size and budget`, `pricing accomplishment`.

Example: `- 2030-01-15 | screening northwind-vp-product-r123 | confirmed by candidate | hired the team of 12`.

`python3 -m toolkit lint` checks that every experience file has at least one dated line.

## Rules

- **Two or three questions per job, not twenty.** The loop should feel like a good recruiter's conversation, not a form.
- **Unconfirmed is not evidence.** Your guesses, typical figures for similar roles, or "probably" answers stay out of the CV. If they don't know a number, record a qualitative outcome instead.
- **Keep "I" and "we" separate.** Ask what they personally owned whenever an outcome was a team effort.
- **Respect confidentiality.** Ask whether a number or client name can be used publicly, and record the answer under "Approved public wording".
- **Never overwrite a confirmed fact.** If new information conflicts with it, keep both, flag the conflict, and ask.
- **Imported facts can be corrected.** A fact marked `unconfirmed` (from a CV or LinkedIn import) is replaced when the candidate corrects it. Keep the old wording in the provenance line (`corrected by candidate | was: "daily deploys"`) so the change is visible, and check whether `master-cv.md` repeats the old claim; if it does, propose the fix.
- **Don't ask twice.** If a gap was already asked about for this job (for example during screening), don't ask again while preparing; use the answer, or the recorded "don't know".
- **If they skip the questions, carry on.** Note the gaps in `open-questions.md` and work with what is confirmed.
