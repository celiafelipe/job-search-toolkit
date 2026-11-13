---
name: job-screen
description: Quickly assess whether a job is worth applying to, against the candidate's own criteria and career evidence. Gives a pursue, hold or skip verdict with traceable reasons, says what is strong and what is thin in their background for this role, and asks two or three questions to fill the gaps. Use whenever someone shares a job description, a job link or a recruiter brief, or asks "is this a good fit", "should I apply", "screen this job" or "quick scan".
---

# Job screen

The toolkit root is two levels above this skill's folder (it contains `toolkit/`). The candidate's private workspace is `~/Documents/Job Search` unless they told you otherwise. You run any commands; never ask the candidate to.

## Inputs

Read the job posting (full text; if they gave a link, read it), `search-preferences.md`, `rubric.md`, `profile.md`, `experience/INDEX.md` and the relevant experience files. If the workspace doesn't exist, start [job-starter](../job-starter/SKILL.md) first. For a posting that isn't registered yet, register it as described in [job-discover](../job-discover/SKILL.md) when they want to track it. A quick verdict doesn't require registration.

If the rubric is missing, give a provisional qualitative view and offer to set up criteria. Don't present a numeric score.

## Assess

- Separate the actual duties and hard eligibility (location, work authorization, language, required qualifications) from nice-to-haves.
- Check level and scope against their track and preferences: team size, reporting line, company stage, remit.
- Distinguish a genuine incompatibility from missing information.
- Rate the evidence for each must-have as direct, adjacent, unsupported or unknown, citing experience files. Don't reward title overlap alone.
- Check the hard gates first. Then score each criterion with the scale in `rubric.md` (Full, Most, Half, Little, None) and add up. Apply the candidate's weights and thresholds consistently. If they want to pursue a role anyway, note the override and keep the objective score.

## Respond (short and scannable)

1. **Verdict:** pursue / hold / skip, with the score and a one-line reason.
2. **What's strong for this role:** two to four specific matches from their experience.
3. **What's thin or missing:** the important gaps, and whether each is a dealbreaker or just unproven.
4. **Two or three questions** that would most strengthen this application, following [the learning loop](../../docs/LEARNING-LOOP.md), plus once: "Anything else relevant I might not know about?"
5. **Next step:** for pursue, offer to tailor the CV ([job-prepare](../job-prepare/SKILL.md)).

When they answer, record the confirmed facts in the experience files as the learning loop describes, then update the assessment if it changes.

## Record

If the role is registered, save `roles/<role-id>/screen.json` following [the contract](../../docs/WORKFLOW.md#1-intake-and-screening): `role_id`, `score`, `verdict`, `hard_gaps`, `unknowns`, `rationale` (an object; its keys are defined in the contract). Reassess when the posting, rubric or their answers change. Screening never authorizes an application.
