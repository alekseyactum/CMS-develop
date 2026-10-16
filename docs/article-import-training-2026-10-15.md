# Article import training — 2026-10-15

Historical record: the training sections below describe the state observed on 2026-10-15,
not the current release state. Both training articles were deleted on 2026-10-16; the user's
own article was preserved. See [release cleanup](#release-cleanup-2026-10-16) for the verified
outcome. The historical draft links no longer resolve. Subsequent import decisions are
recorded in the agreed [article import specification](article-import-specification-2026-10-16.md).

Evidence paths under `outputs/` identify local files relative to the repository root.
These captures, scripts and recovery backups are not included in Git; they are not
repository download links. This report records their findings and the cleanup receipt.

## Status and scope

Two Ukrainian articles from the existing Actum site were imported as **unpublished drafts** in
the release CMS. Their `seo`, `publication_meta`, and `content_builder` sections are saved.
Six source images were uploaded to the new media registry and referenced by their new CMS IDs.
Neither article has a published snapshot. The prepared redirects are disabled.

Data persistence checks passed. **Visual acceptance is incomplete:** both real site previews
render the article text, but all six body image blocks are missing from the rendered page.
This is a backend/frontend media resolution defect, not evidence that the uploads or saved
article content are missing. The drafts are not declared ready for publication.

The training covers content conversion and draft import. It does not include a runtime code
deployment, article publication, redirect activation, article translation, or legal revision
of the source text.

## Imported drafts

| Article | CMS draft | Page ID | Original publication date | Body blocks | Uploaded media |
| --- | --- | --- | --- | --- | --- |
| 1 — Непокора або відмова від виконання наказу командира в військовий час | [Open in release CMS](https://cms-front-release-2ubpwinuqq-lm.a.run.app/uk/admin/publications/blog/292070c1-e94c-4023-950e-645426d331f4) | `292070c1-e94c-4023-950e-645426d331f4` | `2023-01-30` | 57 | 1 |
| 2 — Відшкодування шкоди за незаконне кримінальне переслідування: як отримати компенсацію від держави | [Open in release CMS](https://cms-front-release-2ubpwinuqq-lm.a.run.app/uk/admin/publications/blog/d483b545-24f5-4411-ac6e-b09693679efb) | `d483b545-24f5-4411-ac6e-b09693679efb` | `2026-10-13` | 80 | 5 |

The dates come from the existing site's editorial listing cards. In particular, article 1's
Strapi `publishedAt` is `2023-12-18T15:14:13.002Z`; that later storage timestamp was not used
as the original editorial publication date.

Article 1 has no evidenced source lawyer author, so `lawyerAuthorRefs` and legal reviewer remain
empty. Article 2 is associated with the matching existing record **Мунтяну Юліан Іванович**,
CMS ID `e393082b-49f7-4998-b831-e75753e6fb12`, as lawyer author and legal reviewer. The source
copyrighter association is retained in the source capture, not imported as a public lawyer author.

A subsequent fresh author read (`outputs/article-import-training-2026-10-15/article-2-facade-author-check.json`)
confirms both references are still present. The fresh
article 2 assembled preview (`outputs/article-import-training-2026-10-15/article-2-preview-author-check.json`)
contains the UUID references but no resolved `authors` or `legalReviewer` objects. The site
mapper expects those objects with `fullName`; the resulting missing credit display is another
public payload integration defect, not an omitted author assignment. It needs the same
preview/publication parity as the media fix.

The final routes, after a separate publication decision, are:

- `/blog/nepokora-abo-vidmova-vid-vykonannia-nakazu-komandyra-v-viiskovyi-chas`
- `/blog/kompensaciya-vid-derzhavy-za-nezakonne-kryminalne-peresliduvannya`

These route names do not imply that the pages are currently public.

## Sources and conversion decisions

- [Article 1 on the existing site](https://www.actum.com.ua/blog-3-1/nepokora-abo-vidmova-vid-vykonannia-nakazu-komandyra-v-viiskovyi-chas)
  was read through the public Strapi `topic-blog` endpoint. Its body is legacy rich-text HTML.
- [Article 2 on the existing site](https://www.actum.com.ua/blog-3-1/kompensaciya-vid-derzhavy-za-nezakonne-kryminalne-peresliduvannya)
  was read through the public Strapi `blogs-v2` endpoint. Its body is an ordered `elementsZone`
  with typed blocks, so block types and table structure were taken from source data.

Original article titles, complete introductions, body text, heading order, supported inline
emphasis, HTTP links, tables, quotes, and editorial images were preserved. The collection
excerpts use the existing source-card descriptions. The complete introductions remain as the
first body paragraphs. This distinction matters because the current release blog detail does
not automatically display `publication_meta.excerpt` or `coverMediaId`; those fields serve
the collection cards. Each article image is therefore also represented once in its body.

Article 1 contains 47 paragraphs, 9 H2 headings, and 1 image. Its 56 blank spacer paragraphs
were removed. One nonempty HTML line break was represented as a paragraph boundary. Old font,
color, alignment, and spacing styles follow the new site's design.

Article 2 contains 44 paragraphs, 20 headings (5 H2 and 15 H3), 3 lists, 4 quotes, 1 important
callout, 5 images, and 3 tables. The source block labelled `Важливо` is an important callout
with unchanged text. The seven FAQ questions remain H3 headings followed by their answer
paragraphs. Seven empty separators were removed. All table headings and cells remain in
their original logical rows and columns. The legal-disclaimer graphic is editorial content
and remains included among the five images.

Hash tags, advertising banners, the generic Actum hero banner, and related-article recommendations
were excluded from the target. This does not remove ordinary article paragraphs that mention
Actum or link to its services. Article 2 has no promotional block components in `elementsZone`.

## Verification completed

Persistence verification (`outputs/article-import-training-2026-10-15/persistence-verification.json`)
reports **PASS, 108 checks, no discrepancies**. It compares the six saved section responses
with fresh reads of both drafts, their section editors, and redirects. Both pages are
`draft` / `not_published`, with `currentSnapshot: null`. Fresh content matches the final
payloads and save requests. Both page diagnostics report zero errors.

Article 1's completeness report (`outputs/article-import-training-2026-10-15/article-1-completeness.json`)
confirms identical normalized body text and identical normalized introduction-plus-body text
(15,814 characters). Article 2's prepared payload records 123 independently enumerated source
text fields, 124 target mappings including the metadata/body introduction copy, and a complete
mapping of all 86 source blocks. All its mapped source text checks passed. The later excerpt
adjustment uses the shorter existing card text while leaving the full body introduction intact.

Both site previews explicitly identify themselves as **PREVIEW — неопублікована чернетка**.
The visual verification record (`outputs/article-import-training-2026-10-15/visual-verification.json`)
captures the incomplete result. Article 1 was checked on desktop at width 1007. Text, tables,
quote variants, and the important callout render. Article 2's desktop table presentation
was checked. For article 2 at a mobile viewport width of 390, the document width was 375 and the table
containers were 343 wide with 560-wide scrollable content and `overflow: auto`; no page-wide
horizontal overflow was observed. Article 1 has not received a mobile visual check. These
checks do not constitute complete visual acceptance while the images are missing.

## Publication blockers and remaining decisions

1. **Body image resolution:** all six body image blocks contain persisted media UUIDs but
   produce no `<img>` element in real site previews. The backend-to-site payload currently
   does not supply the media object/URL expected by the site's image mapping. Fix the media
   resolution contract in both draft preview and exact publication assembly so each editorial
   image reference resolves to an allowed serving address with its metadata; update the site
   mapper to consume that public image field. Then repeat both previews on desktop and mobile. Keep the canonical
   article content as media IDs; substituting legacy external image URLs is not the accepted
   fix. No code fix was deployed as part of this import.
2. **Internal links:** legacy Actum URLs remain in the saved text where no published new
   destination could be verified. The frontend rewrites legacy Actum URLs to the current
   origin, so preserving the old absolute URL does not guarantee navigation back to the old
   site. Resolve the article/service link mappings or prepare their redirects before
   publication. See route inspection findings (`outputs/article-import-training-2026-10-15/route-inspection-findings.json`).
   At inspection time, the military and criminal practice pages were missing; the relevant
   disobedience and unauthorized-absence targets were blocked by missing source slugs.
3. **Telephone links in article 1:** four source `tel:` anchors retain their exact visible
   text and marks as ordinary text because the current editorial inline-link contract only
   supports HTTP(S) and site-relative URLs. The numbers are not clickable. The original
   anchors are recorded in `unsupportedLinks` in the article 1 payload.
4. **Service relations and authorship:** `serviceTreeRefs` remains empty for both drafts.
   Article 1 also needs an editorial decision if a named lawyer author or reviewer is desired;
   no name was inferred. Article 2's long title is retained verbatim despite a length warning.
   The contract already supports one primary practice/service/problem chain and additional
   chains. A taxonomy reference does not require an existing public landing page. The follow-up
   read-only active UK site tree (`outputs/article-import-training-2026-10-15/taxonomy-active-service-tree-uk.json`)
   contains 19 practices, 130 services, and 574 problems. It excludes hidden ERP records and
   reflects the website's active hierarchy. No new taxonomy assignments were saved during
   this follow-up verification.
5. **Final visual acceptance and publication:** repeat the full content and navigation review
   after fixing image resolution. The source legal wording and figures were migrated without
   a substantive legal accuracy review.

## Redirect state

Both old `/blog-3-1/...` paths have prepared redirects to their corresponding new
`/blog/...` routes. The redirect records are `prepared`, `enabled: false`,
with `active: null` and the corresponding draft in `pending.targetPageId`.
The requests used the old production source URLs and planned `actum.ua` destinations.
The registry normalizes the displayed URLs to the current release origin
(`https://site-front-release-2ubpwinuqq-lm.a.run.app`) and stores the target page identity.
No redirect was configured on the currently operating old website or its domain infrastructure.
They must remain disabled until the destination article is published and its route is verified.

- Article 1 redirect ID: `471c15ab-5092-4c47-8875-6e966e03b114`.
- Article 2 redirect ID: `785c1459-3fa4-40d7-b40f-d466069eb6b7`.

## Evidence and repeatable local checks

The training output directory (`outputs/article-import-training-2026-10-15/`) contains the
public source JSON and metadata, prepared and final payloads, source images, upload receipts,
draft save requests/responses, fresh reads, and verification results. No credential values
are reproduced in this report. Generate a fresh preview through the CMS instead of reusing
or publishing a preview access URL.

- Source captures: article 1 (`outputs/article-import-training-2026-10-15/article-1-source.json`),
  article 2 (`outputs/article-import-training-2026-10-15/article-2-source.json`).
- Source dates and SEO: article 1 metadata (`outputs/article-import-training-2026-10-15/article-1-metadata.json`),
  article 2 metadata (`outputs/article-import-training-2026-10-15/article-2-metadata.json`).
- Final payloads: article 1 (`outputs/article-import-training-2026-10-15/article-1-final.json`),
  article 2 (`outputs/article-import-training-2026-10-15/article-2-final.json`).
- Conversion scripts: article 1 (`outputs/article-import-training-2026-10-15/prepare-article-1.py`),
  article 2 (`outputs/article-import-training-2026-10-15/prepare-article-2.py`).
- Final card excerpt selection: use-source-card-excerpts.py (`outputs/article-import-training-2026-10-15/use-source-card-excerpts.py`).
- Upload mapping: media-plan.json (`outputs/article-import-training-2026-10-15/media-plan.json`).
- Persistence checker: verify-persistence.py (`outputs/article-import-training-2026-10-15/verify-persistence.py`).

`prepare-article-2.py --check` reads the prepared article 2 payload without regenerating it.
`verify-persistence.py` compares the captured final requests and fresh CMS responses locally.
Neither check publishes a page. Do not rerun the create/upload/write scripts as a verification
step: those scripts perform mutations and can create additional records.

For manual review, open each CMS draft, inspect its content builder, request a fresh site preview,
and compare the complete introduction, all headings, final paragraphs, three tables, quotes,
callout, and images against the source. Check every internal link and the mobile table scroll.
Publication and redirect activation remain separate subsequent actions.

## Release cleanup 2026-10-16

The user explicitly requested deletion of the two training imports. This section records
the later cleanup; the preceding sections describe the historical training result.
Fresh release reads found article 1 unpublished, while article 2 had acquired published
snapshot `38dc79a6-80e1-4a5b-a691-b25df3c53f20` on 2026-10-15 at 10:51:56 UTC.

At 2026-10-16 03:22:17 UTC (06:22 Kyiv), one transaction deleted exactly these pages
and their owned content/history:

- `292070c1-e94c-4023-950e-645426d331f4` — the disobedience article.
- `d483b545-24f5-4411-ac6e-b09693679efb` — the compensation article.

The deletion included 8 owned sections, 15 section versions, 8 bindings, 6 current-version
pointers, 6 authoring request rows, the single published snapshot and current head,
3 snapshot-section references, 1 editorial projection and 2 contributor relations.
Both prepared legacy redirects were canceled by clearing their pending targets; their
disabled registry rows remain available for a subsequent real import. All six uploaded
media assets and translations were preserved. No 410 reservation was created.

The deployed CMS has no normal delete/unpublish writer for this operation. A reviewed,
one-off maintenance script ran through the existing `cms-back-release-migrate` job with
per-execution overrides. No saved job, deployment, schema, IAM or secret was changed,
and no migrations were run. This was a narrow exception for the explicitly requested
training cleanup: each target's redirect guard was removed atomically with its owning
page, with FK enforcement enabled throughout. Other guards and redirect registry rows
were preserved. It is not a reusable editorial retirement workflow.

The playbook preflight and independent script review passed. Full-row backup and deletion
were restricted by exact page, snapshot and version identities. The transaction repeated
dependency checks under locks and required the complete backup hash to match before DML.
External FK/JSON consumers, unexpected operational history, database triggers or
nontransactional tables would have blocked execution; none were found.

- Backup execution: `cms-back-release-migrate-2llkn`.
- Committed deletion execution: `cms-back-release-migrate-dqrx8`.
- Script SHA256: `a30a9cc150eeb3ede49068f1a9eaf086f5516945face43a2a63f05ea23dedd40`.
- Backup SHA256: `33b80117e9d41bab9febebc790afeb8caebbfb09979aa7e0f1200b4803b4257c`.
- Local recovery data: `outputs/article-import-cleanup-2026-10-16/backup-before.json`.
  The full rows were exported encrypted, decrypted locally and hash-verified before
  deletion. Credentials and the temporary private key were not persisted. Restoration
  would require a separately reviewed transaction using this backup, not rerunning cleanup.
- Execution result and API evidence:
  cleanup outputs (`outputs/article-import-cleanup-2026-10-16/`).

Post-cleanup admin and public route API reads returned 404 for both deleted pages.
The UK blog list contains exactly the user's retained page
`9ac3539e-1fc6-4614-9f6b-339b3d6016fd`, titled
«Що робити якщо підставили з наркотиками: правовий алгоритм захисту та доведення
провокації за ст. 307 ККУ». Its complete editorial facade is byte-equivalent after
canonicalization to the pre-cleanup capture (SHA256
`9034ac656796cca5fdb75df6d80a7ae738c6c8bdb8220a5185b600cfb446a882`).
Both redirect rows were re-read with `enabled: false`, `active: null`, `pending: null`.
For manual verification, refresh the release CMS blog list: only the retained article
should remain. The earlier draft links in this historical report no longer resolve.
