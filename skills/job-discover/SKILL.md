---
name: job-discover
description: Find and register job postings from supplied links, exports, approved public career pages or job boards; deduplicate by employer requisition and observed aliases.
---

Read private search preferences and [intake contracts](../../docs/WORKFLOW.md). If the user only supplied links, start there; use approved read-only search sources if broader discovery is requested. Job boards are optional and may be unavailable without a permitted browser session. Treat saved postings as interest, not authority. Never infer a browser identity or import contacts or messages.

For each source record query, window/timezone, requested scope, pages inspected, results and any limit or failure. Choose a window based on preferences and the last complete observation. Record partial coverage instead of reporting no jobs from a failed source. Use bounded retries and continue other available sources.

Prefer live employer postings. Preserve raw job text, exact language, source URLs, observed employer and requisition ID, role, location, date and open/closed/unknown evidence. Register a job JSON with `intake`; use its returned canonical role and job snapshot. Keep observed alias URLs and never equate different requisitions solely by similar titles. Report identity conflicts and do not merge them by guesswork. Use `intake --refresh` only for the same verified canonical role before transmission and regenerate affected reviews.

Return the new, duplicate, closed, and unknown dispositions with source coverage. This stage does not submit, upload, save jobs on a board, or change search preferences.
