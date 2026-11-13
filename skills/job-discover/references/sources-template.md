# Discovery sources

How discovery finds jobs for this candidate. Every discovery run reads this file, whether the candidate asked in chat or a schedule started it. Write it with the candidate during the first discovery run, and update it only when they agree a change.

Last agreed: 2030-01-14

## Sources, in order

Use the same names as `discovery/state.json`. Remove the lines that don't apply.

- `board-saved`: saved jobs on the job board the candidate uses
- `board-alerts`: job alert emails
- `board-live`: live searches, listed below
- `career-pages`: employer career pages, listed below

## Browser and accounts

- Browser: the candidate's own browser, through the host's browser connection
- Account or profile to use: (the one the candidate named; stop if a different one is signed in)
- Alert email sender: (as the candidate named it)

## Live searches

One search per title and location. Date filter: the smallest one that covers the window.

| Title | Location |
| --- | --- |
| VP Product | Remote, Europe |
| Head of Product | Example City |

## Career pages

- [Fictional Employer careers](https://careers.example/jobs)

## Approved filter changes

None. (Example of an approved change: "On the matches page, always select Last 7 days.")

## Source trials

None running. (When the candidate wants to try a new source, write its plan here: baseline date, number of comparison runs, and what will be measured.)

## Personal additions

Anything specific to how this candidate's sources should be read that the generic recipes don't cover.
