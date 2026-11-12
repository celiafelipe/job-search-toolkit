# Local contracts

The toolkit root is the checkout containing `toolkit/` and `skills/`. Run `python3 -m toolkit` there. The private workspace is the root chosen during onboarding, outside any Git checkout. Agent skills use `config.json` as a file pointer map; the CLI uses the selected workspace and its fixed `ledger.json` and `policy.json`. A manifest path can be absolute or relative to the workspace; all paths must resolve inside it. Path/hash references use the object below, with absolute resolved paths recommended. Changing workspaces or moving a package needs a new review.

```json
{"path": "/private/workspace/roles/role-1/answers.json", "sha256": "<SHA-256 of exact file bytes>"}
```

Use `shasum -a 256 FILE`, or `core.record(Path(...))` from this checkout, to get the digest. Create a new revision rather than editing reviewed artifacts. Preserve private sources when needed for recovery. Do not transfer role records or reviews between candidates.

## Start here

| Task | Minimum inputs |
| --- | --- |
| Discover | Supplied links or approved sources and `search-preferences.md` |
| Screen | Job posting, `search-preferences.md`, `rubric.md` and relevant candidate evidence |
| Prepare | Registered posting, screening, form inspection, `profile.md`, `master-cv.md`, detailed career evidence, and confirmed answers for actual questions |
| Review | Raw posting, form inspection, approved sources, then exact prepared package |
| Apply | Passing independent review, complete live recheck, action authority and a browser that supports the required interaction |
| Track | Registered role and matching, verified receipt or an unresolved attempt to reconcile |

Start the CV from [the supported Markdown template](../templates/master-cv.md). For an existing CV in another format, extract or transcribe into that template and check it against the original; leave the original intact.

## 1. Intake and screening

Create a per-role folder beneath the private `roles/` and a raw job description. Keep source/time/language and source coverage alongside it. Register job metadata with `intake roles/.../job.json`; use the returned canonical ID and immutable `job` reference from this command or `tracker` in later manifests.

```json
{
  "role_id": "employer-key-123",
  "company": "Fictional Employer",
  "title": "Role title",
  "posting_url": "https://jobs.example/role/123",
  "requisition_id": "123",
  "identity_evidence": "The employer posting shows requisition 123.",
  "observed_at": "2030-01-01T09:00:00+00:00",
  "aliases": []
}
```

Use an empty requisition ID if none is evidenced. Check employer URL, listing status and identity before selecting. Conflicting identities need manual reconciliation. Intake adds observed aliases; re-run with `--refresh` and the canonical ID to store an updated pre-transmission snapshot without replacing attempts or deleting history. When the raw description changes, refresh intake and screening and review the new materials. Track posting details that the ledger does not need in the role folder.

Screening JSON: `role_id`, `score` (0–100, or null for a provisional assessment), `verdict` (`pursue`, `hold`, `skip`), `hard_gaps` and `unknowns` (lists), and `rationale` with criteria, role evidence, candidate evidence and any explicit user override. An override does not change the objective score. If the user has authorized scoped application to newly found eligible roles, also bind the exact authorized `rubric` and `search_preferences` using path/hash references in the screening JSON.

## 2. Inspection and preparation

Store `inspection.json` with canonical `role_id`, exact HTTPS `destination_url`, timestamp `observed_at`, `platform` (name or `unknown`), `platform_evidence` (visible branding/form/host or what was inconclusive), `coverage` (`observed_only` or `complete`), `required_fields` (list of exact prompts), `letter_mode` (`none`, `pdf_required`, `text_required`), and `attachments` (map of `cv` or required `letter` to `required` boolean, exact `slot` label, optional `extensions` list such as `[".pdf"]`, and optional `max_bytes`). For a letter textbox also record `letter_prompt` and, if visible, `letter_max_chars`. Keep full observed prompts, optional/conditional fields, locale, limit wording and evidence separately when needed. Never guess a platform or document limit; a host/brand does not reveal the actual parser or employer configuration.

Save `answers.json` with `role_id` and `fields`, a list of `{"prompt": "Exact prompt", "value": "Exact proposed value", "source": "Confirmed scoped evidence"}` objects. Supported values are strings, integers, booleans and lists of selected labels. Add `"kind": "letter"` to a required letter textbox answer. Record exact sent values, including consent decisions. Check employer constraints not represented by the CLI, such as allowed choices, input validation, disclosure scopes and non-letter length limits.

Build only PDFs the form accepts. Use UTF-8 plain Markdown: headings with one to three hash signs, plain paragraphs separated by blank lines, and dash lists. Use literal URLs and plain text; no HTML, tables, images or inline markup. Put role, employer and dates together on a subheading; natural page breaks, no fixed page count. Start a fresh output directory:

```sh
python3 -m toolkit build-pdf roles/role-1/cv.md roles/role-1/cv-build --kind cv
```

The output contains the exact PDF, generated HTML, two recoverability views, every-page PNGs and `build.json`. Never handwrite the build receipt. Both text modes must recover each source passage; check order warnings, repeated text, chronology and attribution manually. An identical upload-named PDF may reuse the build if the new path and hash are included in the reviewed package.

Prepare `package.json` with:

- `schema: 1`, `role_id`, `destination_url`, `preparer_id`, `preparation_session` (actual fresh run/context identifier).
- Path/hash references `job` (registered immutable intake snapshot), `job_description`, `screen`, `inspection`, `answers`, `evidence_map`.
- `attachments`: list of `{"kind":"cv","file":{...},"build":{...}}` with exact outgoing file and build receipt path/hash references. Use `[]` if no documents are needed.

## 3. Independent review

Use a separate fresh context. First write a ranked independent evidence assessment from the posting and canonical career material. Then review the actual exact application package and write findings. Create `review.json` with:

- `schema: 1`, `role_id`, `status` (`pass`, `revise`, or `needs_fact`), `package` path/hash, `reviewer_id`, `review_session`, `independent_before_draft` (true only if actually performed), `unresolved_findings` (must be empty to pass).
- Path/hash references `independent_evidence` and `review_notes`.
- `visual`: map for each outgoing PDF kind to `pdf_sha256`, `pages` (ordered path/hash refs for every image from the build), `findings` (specific visual and recovery observations), and `warning_resolutions` (map of every warning ID to a specific decision grounded in the views). Use `{}` if no PDFs.

Run `check PACKAGE REVIEW`; `--final` also checks that inspection coverage is complete. This test checks manifest consistency and current bytes. It does not prove genuine independence, auth provenance, successful upload, or receipt truth. A human or execution agent must check actual worker identities/contexts and artifacts. Use separate roles even for base CV reuse; if a separate fresh context is unavailable, stop at review pending.

[The fictional fixture](../examples/demo.py) gives complete valid JSON examples for each contract. For authority, upload checks, receipt schemas and recovery, see [execution](APPLY.md).
