# Current CMS Handoff - 2026-06-09

This document is the short source of truth for continuing the CMS work in a new Codex thread without
loading the full previous chat history.

## How To Continue In A New Chat

Start the new chat with this message:

```text
Продолжаем проект Actum CMS. Прочитай:
- G:\работа\Actum\develop\CMS\AGENTS.md
- G:\работа\Actum\develop\CMS\docs\current-cms-handoff-2026-06-09.md

Работаем дальше только с develop, release не трогаем. Перед GCP-проверками читать gcp-infra-playbook и
делать preflight. Ближайшая цель: довести page workbench/matrix для practice_collection_page и
practice_page до рабочего сценария редактора.
```

## Repositories And Branches

Main local repositories:

- `G:\работа\Actum\develop\CMS` - documentation/specification repository.
- `G:\работа\Actum\develop\cms-back` - NestJS backend repository.
- `G:\работа\Actum\develop\gcp-infra-playbook` - mandatory GCP/runtime playbook.

Current branch rule:

- work only in `develop`;
- do not push or merge `release`;
- `release` will be handled separately later by promoting the develop state.

Latest known pushed state:

- `cms-back/develop`: commit `5d83d26` (`Add page workbench row metadata`).
- `CMS/develop`: commit `f71d2d3` (`Document page workbench matrix updates`).

Latest verified backend deploy after push:

- GCP project: `composite-ally-360719`.
- Region: `europe-central2`.
- Cloud Run service: `cms-back-develop`.
- Cloud Build trigger: `cms-back-develop`.
- Build id: `457832bd-5967-4446-83e5-ecf97fffd0b4`.
- Cloud Run revision: `cms-back-develop-00136-rdx`.
- `/api/health`: `200`.
- `/api/ready`: `200`, database `ok`.
- Fresh `ERROR` logs for that revision: none at the time of verification.

## Operational Rules

Follow `AGENTS.md` in `CMS`.

Important project-specific rules:

- Do not store secrets, tokens, private keys, passwords, or live credential values in code, docs, logs, or chat.
- Before reading or changing GCP state, read the relevant `gcp-infra-playbook` context and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\gcloud-preflight.ps1
```

- After pushing `cms-back/develop`, verify:
  - Cloud Build `cms-back-develop`;
  - Cloud Run latest created/ready revision;
  - `/api/health`;
  - `/api/ready`;
  - fresh error logs for the new revision.
- Push `CMS` docs and `cms-back` code separately with clear commits.
- Use the backend repo patterns already in place. Do not introduce large abstractions unless they solve a
  real current problem.

## Product Architecture Decisions

The CMS is split into two services:

- frontend: Next.js;
- backend: NestJS.

The public site frontend must not read draft/authoring tables directly. It should render from published
snapshots/public payloads.

Preview uses the same rendering idea, but receives preview payloads from protected backend endpoints.

Header, footer, breadcrumbs, and route/context navigation are not editable page sections. They are outside
the page authoring schema:

- header/footer are site layout/global section concerns;
- breadcrumbs are generated from route/reference context;
- public page content is built from page snapshot + allowed runtime read models.

## Core Data Model

### Pages And Sections

Pages are composed from section slots registered in backend code. Section/page structure is not free-form
in the database for normal pages. The backend schema registry defines which slots exist and how they behave.

Section types:

- page-owned sections;
- global sections;
- inherited child sections;
- runtime/read-model slots;
- not-created section slots in the workbench matrix.

Important: do not infer UI semantics only from `composition.strategy`.

For the frontend, the authoritative field is:

```json
"relationship": {
  "role": "self_owned | child | global_source | runtime | not_created",
  "inheritanceStrategy": "none | inherit | override | append",
  "isInherited": true,
  "sourceSectionId": "...",
  "localSectionId": "..."
}
```

Use `cell.relationship` to label a cell as parent/child/self/runtime/not-created. For example, a page-owned
SEO section may have `composition.strategy = "override"` internally, but if `relationship.role` is
`self_owned` and `isInherited = false`, it is not a child section.

### Draft, Publish, Snapshots

Sections have draft/published versions. A page snapshot points to concrete section versions.

Public frontend receives a complete published page snapshot. It must not assemble a page from live draft or
authoring tables.

Rollback must restore a specific set of section versions, not "latest published sections".

Independent global section publication should rebuild affected page snapshots only where appropriate and
without touching unrelated page-owned drafts.

### Locales

Public locales:

- `uk` - default, no public URL prefix;
- `ru`;
- `en`.

Global section workbench is locale-aware. Global section status is interpreted in the current locale. Where
the UI needs all locale diagnostics, backend should return all three locales in the relevant editor
response, so the frontend does not need three separate calls for the same screen.

### Regional Pages

Regional pages inherit from base/Ukraine pages only where the page type supports regional routes.

Regional content model:

- inherit;
- override;
- append.

Append/override availability is constrained by section schema and policy. Not every section should be
overridable or appendable.

For price:

- base generated pages inherit from `global_price`;
- regional generated pages inherit from the matching base page price section;
- regional price behavior can be inherit/override/append, depending on section policy.

## Reference Data And Runtime Data

ERP sends data into the CMS database through `data-inside-migrator`.

The CMS owns:

- local display fields;
- localizations;
- media metadata/selection;
- diagnostics;
- routing/public payload use.

ERP owns:

- external identity;
- `show_on_site`;
- ERP source names;
- source slugs for practices/services/problems/regions;
- service flags such as `service_cond` and `legal_cond`;
- competencies/qualifications.

Reference objects:

- practices;
- services;
- problems;
- regions;
- offices;
- lawyers;
- reviews;
- lawyer competencies;
- region competencies.

Current important reference-data decisions:

- no editable `publicSlug` in CMS;
- practices/services/problems/regions use ERP-owned source slug;
- lawyers do not have ERP slug; CMS generates a stable read-only lawyer slug once on create and does not
  regenerate it on name changes;
- offices, reviews, and competencies do not have route slugs;
- `lastSyncedAt` was removed from normal reference objects and kept only where synchronization state is
  actually meaningful for competencies;
- `updatedAt`/`updatedBy` exposed to CMS frontend represent the latest CMS edit across the object and its
  localizations;
- `translationsMeta` contains latest translation edit metadata and per-locale metadata:

```json
"translationsMeta": {
  "latestUpdatedAt": "...",
  "latestUpdatedBy": "...",
  "locales": {
    "uk": { "updatedAt": "...", "updatedBy": "..." }
  }
}
```

Reference-data localization rows should be created both:

- when a new object arrives;
- as a safety check when the object detail endpoint is opened.

This prevents the frontend from receiving an object without required locale rows.

## Media Model

Files are not stored in the database.

The database stores media metadata. Physical files live in Cloud Storage or compatible object storage.

Media rules:

- stable public URLs are required;
- bucket itself can stay private;
- media metadata records exist in CMS;
- images in public content require `alt`/`title` where appropriate;
- mime and size restrictions are validated;
- files cannot be removed if used by a published snapshot;
- lawyer photo is integrated into reference-data editing through media picker/upload.

## Global Sections And Site Layout

Global section API exists for editor/history/validate/draft/publish-related work.

Important global sections:

- `global_price`;
- `site_header`;
- `site_footer`;
- `site_footer_practices`.

Header and footer are outside page schema. Page workbench rows should not show header/footer as page cells.

### global_price

Global price section is editable through global section workbench.

Key product decisions:

- default readonly texts such as common title/accent/description can be defined by backend/system and shown
  read-only in the editor;
- editable core is price items;
- price validation examples:
  - title length less than 4 or more than 46 is warning/invalid depending policy, 100+ is error;
  - price cannot exceed `100000`;
  - description target length 50-200, 400+ is alert/error by policy;
- endpoint `/validate` supports checking unsaved payload, not only a saved `sectionVersionId`.

### site_footer_practices

This is a separate global layout section for the practices list shown in footer.

Current direction:

- title "ПРАКТИКИ" / localized title is system-defined/read-only;
- list is runtime/read-only from visible practice reference data;
- order is by practice name unless later changed;
- frontend can preview layout from admin layout endpoints.

### site_footer

This is the lower footer/site links section.

Editable:

- social URLs for a predefined fixed set of social networks;
- visibility/order behavior is constrained by predefined keys;
- legal PDF document references, such as offer and privacy policy;
- working hours if kept in footer content.

Not editable or currently frontend/system-owned:

- phone is currently not modeled as versioned CMS backend data to avoid overloading snapshots/cache;
- navigation labels/links are mostly system/page-route derived;
- copyright may be generated/system-owned.

Legal PDFs:

- store file in object storage/media system;
- CMS stores media id/reference;
- missing required legal document is warning;
- validate max size and PDF mime type.

### site_header

Header/menu is a global layout concern, not a page section.

Current direction:

- main navigation is mostly route/reference-data driven;
- services mega menu uses visible practices and visible services with `service_cond = true`;
- if a referenced public page is missing/unpublished, do not show it in public layout and produce admin
  warnings;
- phone/display schedule are not currently forced into a versioned global settings snapshot.

## Admin Navigation

The CMS left menu is a navigation and attention dashboard, not just a list.

Main groups:

- practices/services tree;
- lawyer pages;
- single/static pages;
- global sections;
- ERP/reference data;
- users.

The practices group is both:

- a clickable page item for `practice_collection_page`;
- a parent group containing the non-regional service hierarchy: practice -> service -> problem.

Reference-data group should not show flat huge lists of services/problems. Its service hierarchy should be
represented as a nested item inside reference data. The central screen changes depending on which navigation
node is clicked:

- click "Практики" in reference data: show all practices;
- click a concrete practice under reference data: show services for that practice;
- click a concrete service: show problems for that service;
- individual problem items are not opened directly from the nav as object-detail pages; they are edited
  from the central list screen.

Indicator semantics were corrected in the requirements:

- `own` means the base/Ukraine page represented by the current item;
- regional descendants are separate from hierarchy children;
- hierarchy child totals should not include the item itself;
- published ratios for regional descendants should count only enabled/eligible regions with the relevant
  competency;
- stale/attention is a combined editor signal for "has drafts or stale dependencies".

If frontend needs fast refresh after edits, navigation should be refetched after save/publish/validate
actions. Longer-term, we can add event/polling helpers, but no heavy realtime mechanism is required now.

## Page Workbench API

The central page editor matrix is based on:

```http
GET /api/admin/page-workbench/page-types/{pageType}?locale=uk
GET /api/admin/page-workbench/page-types/{pageType}?locale=uk&sourceId={sourceId}
```

Important page types:

- `practice_collection_page`;
- `practice_page`;
- `service_page`;
- `problem_page`;
- `lawyer_page` later.

The matrix returns:

- collection/source metadata;
- rows: Ukraine/base row and regional rows;
- cells: page section/runtime slots;
- row/cell diagnostics;
- available endpoints/actions.

Recent backend additions:

- `cells` include version audit metadata:
  - `createdAt`;
  - `createdBy`;
  - `publishedAt`;
  - `publishedBy`.
- rows include:
  - `sourceTitle`;
  - `regionTitle`;
  - `displayTitle`.
- rows include `endpoints.history`:

```http
GET /api/admin/page-workbench/pages/{pageId}/history?limit=50&offset=0
```

- matrix includes bulk endpoints:

```json
"endpoints": {
  "bulkPublishPlan": {
    "method": "POST",
    "path": "/api/admin/page-workbench/bulk-publish/plan"
  },
  "bulkPublish": {
    "method": "POST",
    "path": "/api/admin/page-workbench/bulk-publish"
  }
}
```

Use `bulkPublishPlan` before `bulkPublish`.

Important frontend interpretation rules:

- row diagnostics and cell diagnostics are different;
- `PAGE_NO_CURRENT_SNAPSHOT` can be a row-level warning even when section cells look fine;
- if `row.publish` is `null`, inspect `row.readiness.publish.reasons`;
- preview/rollback/snapshots can exist even when publishing is temporarily unavailable;
- use `cell.relationship`, not raw `composition`, to show parent/child/self/runtime labels.

## Current Page Structures

### practice_collection_page

This is the public services/practices collection page, URL base `services`. In the CMS editor it should be
presented as "Практики"; the public route remains `/services`.

It supports regional routes.

Current backend slots:

1. `seo`
   - base page-owned metadata section;
   - regional variants inherit from the base by default and may only diverge through an explicit override;
   - fields: `title`, `description`, optional `canonicalPath`, optional `ogImage`.

2. `practice_collection_intro`
   - base page-owned content section;
   - regional variants inherit from the base by default and may only diverge through an explicit override;
   - fields:
     - `title` required;
     - `lead` optional rich text;
     - `ctaLabel` optional;
     - `ctaTarget` optional.

3. `practice_collection`
   - runtime/read-model slot;
   - field: `items` required list;
   - base/Ukraine row: visible practices with nested visible service-list services;
   - regional row: visible practices with active region qualification, with nested visible services that
     belong to those region-qualified practices;
   - nested services use `show_on_site=true` and `service_cond=true`;
   - practice and service ordering uses CMS `sort_order`, then localized/source name, then stable id;
   - practice/service entries with missing or unpublished linked generated pages remain visible in the
     admin runtime payload with diagnostics/warnings.

Regional page behavior:

- expected regional rows are visible regions that have at least one active visible practice qualification;
- regional canonical route is self-canonical, for example `/kyiv/services`;
- empty or low-value required runtime collections should block publish rather than creating a regional
  public page only because the region exists.

Not part of this page schema:

- header;
- footer;
- breadcrumbs;
- standard lead form;
- footer practices.

This page is the best first small page-workbench slice because it has only one editable content section
plus one runtime list.

### practice_page

This is a page for a specific practice, URL base `services/{practiceSlug}`.

It supports regional routes.

Current backend slots:

1. `seo`
   - page-owned metadata.

2. `practice_intro`
   - required page-owned hero/intro section;
   - fields:
     - `title` required;
     - `lead` optional rich text;
     - `ctaLabel` optional;
     - `ctaTarget` optional.

3. `practice_services_block`
   - page-owned editable block text for the services area;
   - composite group: `practice_services`;
   - fields:
     - `title` required;
     - `lead` optional rich text.

4. `practice_services`
   - runtime/read-model list paired with `practice_services_block`;
   - composite group: `practice_services`;
   - source key: `practice_services`;
   - route param: `practiceSlug`;
   - fields: `items` required list.

5. `practice_intro_text`
   - optional page-owned text section;
   - can be disabled;
   - fields: `title` required, `lead` optional.

6. `practice_actions`
   - optional page-owned structured/list section;
   - can be disabled;
   - fields: `title` required, `lead` optional, `items` optional list.

7. `practice_team_cta`
   - optional page-owned CTA section;
   - can be disabled;
   - fields: `title` required, `lead` optional, `buttonLabel` optional, `buttonTarget` optional.

8. `practice_cases`
   - runtime/read-model list;
   - currently route-aware and may return empty until cases read model is implemented.

9. `practice_reviews`
   - runtime/read-model list;
   - currently route-aware and may return empty until reviews read model is implemented.

10. `practice_optional_text`
    - optional page-owned text section;
    - can be disabled;
    - fields: `title` required, `lead` optional.

11. `price`
    - inherited global price section;
    - base generated pages inherit from `global_price`;
    - regional pages inherit from the matching base page price section.

12. `practice_faq`
    - optional page-owned FAQ;
    - can be disabled;
    - field: `items` optional list.

13. `practice_lawyers_block`
    - page-owned editable text for lawyer list area;
    - composite group: `practice_lawyers`;
    - fields: `title` required, `lead` optional.

14. `practice_lawyers`
    - runtime/read-model lawyer list paired with `practice_lawyers_block`;
    - source key: `lawyers_directory`;
    - route param: `practiceSlug`;
    - filters: `practice`;
    - fields: `items` required list.

15. `lead_questionnaire`
    - optional page-owned questionnaire section;
    - can be disabled;
    - fields:
      - `title` optional;
      - `description` optional rich text;
      - `questions` required list.

16. `lead_capture`
    - runtime standard lead form contract;
    - not a global section;
    - not an editable page-owned section;
    - frontend renders the common form component from this runtime context.

For the first working implementation, do not try to perfect all 16 slots. The practical route is:

1. verify `practice_intro`;
2. verify `practice_services_block` + `practice_services`;
3. verify `price`;
4. verify `practice_faq`;
5. verify `practice_lawyers_block` + `practice_lawyers`;
6. verify `lead_capture`;
7. then refine optional content slots.

2026-06-09 product-structure checkpoint for `practice_page`:

- Regional inheritance rule: for future regional service-hierarchy pages, regional page-owned sections
  should inherit from the matching base page by default and diverge only through an explicit override.
  `seo` and `practice_intro` for `practice_page` should follow this rule. Base changes should mark
  inherited regional pages stale/requires-review.
- Canonicals are backend-owned and self-canonical for both base and regional routes.
- `seo`: `title` and `description` start from the source practice name and remain editable. Empty required
  fields are errors; SEO length/quality and `ogImage` media policy issues are warnings. `ogImage` is
  optional and may use a frontend/site fallback.
- `practice_intro`: required, fixed, not disableable, inherited regionally. Default `title` comes from the
  practice name; default `lead` is empty. Hero CTA stays as the primary lead-flow action. `ctaLabel` and
  `ctaTarget` must be a valid pair; UI should use controlled target choices, not free external URLs.
- A new global/shared recognition section is required after the hero on the home page and all
  service-hierarchy pages except `practice_collection_page`. It is one global source, not page-owned,
  not overrideable, not appendable, not disableable, and not movable. Proposed content: required
  `items[]` with `sourceName`, optional `sourceLogo`, and required `achievementText`. Fewer than 3 items
  is a warning; empty `achievementText` is an error; missing both `sourceName` and `sourceLogo` is an
  error; media issues are warning when text fallback exists.
- `practice_services_block` + `practice_services`: required, fixed, not disableable. The editable block is
  inherited regionally and defaults to a localized services heading, preferably "Services {practice}" when
  a suitable grammatical form exists, otherwise "Services". Runtime source is current practice services
  where `show_on_site=true` and `service_cond=true`; regional runtime must filter by regional competence.
  Empty runtime list blocks publish. Missing/unpublished linked service pages are admin warnings; public
  items should render disabled/non-link rather than active broken links. Ordering remains `sort_order`,
  then display/source name, then stable id.
- Add a separate optional composite section for "Може зацікавити", not part of `practice_services`.
  Proposed names: `practice_related_legal_block` + `practice_related_legal`. Runtime source is current
  practice rows with `show_on_site=true`, `legal_cond=true`, and `service_cond=false`; regional runtime is
  filtered by regional competence. Items use the same service-route shape as service pages. Missing or
  unpublished linked pages are warnings and render public items disabled/non-link. The section can be
  disabled, is fixed, inherited regionally, and empty enabled runtime is a warning rather than a publish
  blocker.
- Text sections: the old single `practice_intro_text` concept should become three independent fixed
  optional slots with the same schema: optional `title`, optional rich-text `lead`, but enabled sections
  must contain at least one of them. Proposed slots/variants:
  `practice_intro_text` (`accent_panel`) after related legal, `practice_reviews_text` (`proof_band`) after
  reviews, and `practice_price_text` (`price_note`) after price. All can be enabled independently,
  inherit regionally, can override, do not append, and are not movable.
- `practice_actions`: confirmed as the "lawyer actions" section. It is optional/can-disable but enabled by
  default, inherited regionally, overrideable, not appendable, not movable, and uses one fixed visual
  style. Fields: required `title`, optional `lead`, required `items[]`. Item fields: required `title` and
  optional `description`. Enabled empty section is an error; item count target is 2-8.
- Discussion stopped before finalizing `practice_team_cta`, cases, reviews, price, FAQ, lawyers,
  lead_questionnaire, and lead_capture.

### service_page And problem_page

Do not expand these deeply before `practice_collection_page` and `practice_page` are stable.

`problem_page` product structure was conceptually approved, but full backend expansion should be a later
slice. Important approved concepts:

- header/footer/breadcrumbs/context nav are outside editable page schema;
- `problem_intro` is hero/content start;
- long unique advisory body should be one structured `problem_guidance` section with ordered internal
  blocks, not many prematurely fixed backend slots;
- `problem_team_cta`, `problem_faq`, `problem_lawyers_block`, optional `lead_questionnaire`, and inherited
  `price` are editable/page-owned areas;
- `problem_cases`, `problem_reviews`, `problem_lawyers`, and `lead_capture` are runtime/read-model areas.

## Current Immediate Goal

The next concrete milestone is not another global polish pass. It is:

```text
Make the page workbench/matrix flow genuinely usable for practice_collection_page and practice_page.
```

Work through the editor scenario:

1. Open from admin navigation.
2. Receive page matrix rows:
   - base/Ukraine;
   - eligible regional rows.
3. If a generated page is missing, use bootstrap/open-editor endpoints to create/open it.
4. Open a default editable section.
5. Save draft.
6. Validate draft/section/page.
7. Preview page.
8. Publish when backend readiness allows.
9. Confirm row/cell data updates correctly:
   - diagnostics;
   - relationship;
   - publishedAt/publishedBy;
   - history endpoint;
   - navigation indicators.

Recommended order:

1. `practice_collection_page` first because it is small.
2. `practice_page` second because it exercises:
   - editable sections;
   - runtime lists;
   - inherited price;
   - optional sections;
   - lead form runtime slot.
3. After that, adapt the same mechanics to `service_page`.
4. Only after that, implement the approved final `problem_page` structure.

## Useful Current APIs

Admin navigation:

```http
GET /api/admin/navigation?locale=uk&includeIndicators=true
```

Page matrix:

```http
GET /api/admin/page-workbench/page-types/practice_collection_page?locale=uk
GET /api/admin/page-workbench/page-types/practice_page?locale=uk
GET /api/admin/page-workbench/page-types/practice_page?locale=uk&sourceId={practiceId}
```

Generated page bootstrap/open examples:

```http
POST /api/admin/page-workbench/generated-sources/practice_collection_page/practice_collection/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/practice_page/{sourceRecord.id}/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/practice_page/{sourceRecord.id}/open-editor?locale=uk
```

Page row:

```http
GET /api/admin/page-workbench/pages/{pageId}/row
GET /api/admin/page-workbench/pages/{pageId}/history?limit=50&offset=0
POST /api/admin/page-workbench/pages/{pageId}/preview
POST /api/admin/page-workbench/pages/{pageId}/publish
POST /api/admin/page-workbench/pages/{pageId}/rollback
GET /api/admin/page-workbench/pages/{pageId}/snapshots
GET /api/admin/page-workbench/pages/{pageId}/snapshots/{snapshotId}
```

Global sections:

```http
GET /api/admin/global-sections
GET /api/admin/global-sections/{sectionKey}/editor?locale=uk
GET /api/admin/global-sections/{sectionKey}/history?locale=uk
POST /api/admin/global-sections/{sectionKey}/validate
POST /api/admin/global-sections/{sectionKey}/draft
POST /api/admin/global-sections/{sectionKey}/rollback
POST /api/admin/global-sections/{sectionKey}/draft-from-version
```

Reference data:

```http
GET /api/admin/reference/practices
GET /api/admin/reference/services
GET /api/admin/reference/problems
GET /api/admin/reference/regions
GET /api/admin/reference/offices
GET /api/admin/reference/lawyers
GET /api/admin/reference/reviews
GET /api/admin/reference/{type}/{id}
PATCH /api/admin/reference/{type}/{id}
```

For the admin navigation menu, do not use flat `/reference/problems` as the source for service hierarchy.
Use the navigation tree/workbench hierarchy returned by backend.

## 2026-06-09 Practice Collection Workbench Update

`practice_collection_page` matrix rows now carry admin diagnostics for the generated runtime tree:

- `PAGE_RUNTIME_REQUIRED_LIST_EMPTY` is critical when the base/regional collection would have no practices;
- `PAGE_LINKED_PAGE_NOT_CREATED` warns when a visible linked practice/service has no generated page yet;
- `PAGE_LINKED_PAGE_NOT_PUBLISHED` warns when the generated page exists but has no current published
  snapshot.

Linked-page warnings include `sourceType`, `sourceId`, and `publicPath`, stay visible in admin payloads, and
do not by themselves block publish. Empty `practice_collection.items` is also guarded in
`PageLifecycleService.publishPage`, so direct publish calls cannot create an invalid collection snapshot.

## 2026-06-09 Frontend Feedback Response

Three frontend-reported gaps were addressed in `cms-back`:

1. `GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor` now returns
   `workbench.row` with the same generated source-aware row shape as
   `GET /api/admin/page-workbench/page-types/{pageType}` and
   `GET /api/admin/page-workbench/pages/{pageId}/row`. For generated regional rows, frontend can rely on
   consistent `rowKey`, `kind`, `sourceTitle`, `regionTitle`, `displayTitle`, `sourceRecord`, `region`,
   `regionSlug`, `pagePath`, and `publicPath`.
2. Page-scoped section editor history now includes `changeOrigin`, matching global section history:
   `ME` for manual edits, `RB#<sourceVersionNo>` / `RB#<sourceVersionNo>_<repeatNo>` for rollbacks, and
   `FV` for draft-from-version/copy rows.
3. Legacy regional `practice_collection_page` `seo` and `practice_collection_intro` bindings are repaired
   when authoring state is read if they were created before the base-inheritance dependency existed. The
   backend reconnects them to the base page-owned section and marks them `draft_stale` when the base has an
   unreviewed draft. Freshly bootstrapped regional rows already create these dependencies.

Frontend note to send: remove any workaround that treats section-editor `workbench.row` as a plain catalog
row; consume the same row shape everywhere. Use `history.items[].changeOrigin` for version-origin badges.
If an old regional row does not look stale immediately after a base edit, refresh/open that regional
authoring row once so the lazy repair path can attach the missing dependency.

## Known Frontend Developer Notes Already Given

Recent notes to CMS frontend developer:

- use `cell.relationship` for self/child/global/runtime/not-created;
- use row `history` endpoint for row history screen;
- use version audit fields in cells for published date/user;
- row-level warnings may exist without cell errors;
- `row.publish = null` means backend does not currently allow publication; inspect readiness reasons;
- header/footer were removed from page schema and are external layout/global parts;
- schedule/settings object was simplified/removed where it caused unnecessary versioning;
- global section `/validate` can validate unsaved payload, not only saved sectionVersionId;
- global section editor response should carry diagnostics needed by the current screen, including all
  locale diagnostics where the design shows all locales.

## Open Questions / Risks

Keep these visible in the next thread:

- Exact field-level final content for all `practice_page` optional sections is not fully designed yet.
- `service_page` and `problem_page` should not be over-expanded until practice pages are stable.
- Cases and reviews runtime lists are placeholders/read-model contracts until their real data model is
  completed.
- Public site frontend integration and cache/revalidation are later-stage work.
- User/roles and admin permission gating are not the current focus, but the admin navigation already
  anticipates users/roles.
- The CMS should stay understandable for editors; do not expose raw internal complexity where a simple
  status/reason is enough.

## Next Suggested Action In New Chat

Ask Codex to do this:

```text
Начинаем с practice_collection_page. Проверь код схемы, matrix response и editor endpoints. Пройди сценарий:
navigation -> page matrix -> generated/base/regional rows -> open/create page -> open practice_collection_intro
section -> save draft -> validate -> preview -> publish/readiness. Если чего-то не хватает в API или docs,
внеси точечные правки.
```

Current correction: `practice_collection_page` workbench diagnostics and publish guard were advanced on
2026-06-09. Next, repeat the same editor/readiness flow for `practice_page`; after that, move to
`service_page`.
