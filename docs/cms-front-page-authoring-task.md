# CMS Front Page Authoring Task

This document is the first implementation task for CMS frontend page authoring screens.

The backend contract is available in Swagger/OpenAPI. Use OpenAPI examples as the primary source for
request/response shapes, especially for authoring state, preview, publish, and rollback.

## Endpoints

```text
GET  /api/admin/page-schemas
GET  /api/admin/page-schemas/{pageType}
GET  /api/admin/navigation
GET  /api/admin/page-workbench/tree
GET  /api/admin/page-workbench/service-tree
GET  /api/admin/page-workbench/page-types/{pageType}
GET  /api/admin/page-workbench/pages/{pageId}/row
POST /api/admin/page-workbench/pages/bootstrap
POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/bootstrap
GET  /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor
PATCH /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/state
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/draft
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/validate
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/publish
GET  /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/history
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/rollback
GET  /api/admin/page-workbench/pages/{pageId}/snapshots
GET  /api/admin/page-workbench/pages/{pageId}/snapshots/{snapshotId}
POST /api/admin/page-workbench/pages/{pageId}/preview
POST /api/admin/page-workbench/pages/{pageId}/publish
POST /api/admin/page-workbench/pages/{pageId}/rollback
GET  /api/admin/pages
POST /api/admin/pages/bootstrap
GET  /api/admin/pages/{pageId}/authoring
GET  /api/admin/pages/{pageId}/sections/{slotKey}/editor
PATCH /api/admin/pages/{pageId}/sections/{slotKey}/editor/state
POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/draft
POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/validate
POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/publish
GET  /api/admin/pages/{pageId}/sections/{slotKey}/editor/history
POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/rollback
POST /api/admin/pages/{pageId}/sections/{slotKey}/draft
POST /api/admin/pages/{pageId}/preview
POST /api/admin/pages/{pageId}/publish
POST /api/admin/pages/{pageId}/rollback
```

All write operations may send `x-cms-actor` until real CMS auth/session audit is wired.
Navigation and other user-aware endpoints should send one of the current identity headers:
`x-cms-user-id`, `x-cms-user-email`, or temporary develop-only `x-cms-actor`.

## Admin Navigation

Use:

```text
GET /api/admin/navigation?locale=uk
```

This endpoint is the source for the left CMS menu. Do not build the whole sidebar by hardcoding separate
frontend lists. Backend groups navigation by domain and filters system/admin entries by the current user's
permissions.

The response contains `groups`:

- `pages`: page authoring navigation. It contains the service tree area (`practice_page`, `service_page`,
  `problem_page`), fixed pages (`contacts_page`, `lawyers_page`), and lawyer pages.
- `global_sections`: shared sections such as menu/header, footer, and the global price source. All three
  are backed by `/api/admin/global-sections`. The global price editor manages the upper shared source;
  concrete generated pages expose their own page `price` slot when the page is opened in the workbench.
- `reference_data`: editable CMS reference resources from ERP-owned source objects: practices, services,
  problems, lawyers, regions, offices, reviews. Competencies are intentionally not exposed as a separate
  regular editor menu item.
- `access_management`: users and roles/permissions. Backend returns this group only for users with
  `users.read` permission, which currently means admin-level access.

Each item can include:

- `route`: frontend route to open;
- `endpoint`: backend endpoint that should be used to load the main data for that menu item;
- `children`: nested entries, for example the service tree page collections;
- `availability`: `available` or `planned`.

Important: `GET /api/admin/page-workbench/tree` remains the page-type workbench tree, not the whole CMS
sidebar. For the actual practice/service/problem hierarchy use
`GET /api/admin/page-workbench/service-tree?locale=uk`. Use `/api/admin/navigation` for the sidebar entry
points, then use page-workbench/reference/users endpoints for the selected area.

## Global Sections

Use:

```text
GET  /api/admin/global-sections?locale=uk
GET  /api/admin/global-sections/{sectionKey}/editor?locale=uk
POST /api/admin/global-sections/{sectionKey}/draft?locale=uk
POST /api/admin/global-sections/{sectionKey}/validate?locale=uk
POST /api/admin/global-sections/{sectionKey}/publish?locale=uk
GET  /api/admin/global-sections/{sectionKey}/history?locale=uk&limit=50&offset=0
POST /api/admin/global-sections/{sectionKey}/rollback?locale=uk
```

Supported editable section keys now:

- `site_header`;
- `site_footer`;
- `global_price`.

`site_header` is the shared header/menu source. Its current minimal content contract is an object with
required `menu: []`. Extra header fields can be added later without changing the global-section lifecycle.

`site_footer` is the shared footer source. Its current minimal content contract is an object with required
`columns: []` and optional `copyright`.

`global_price` uses the same draft/validate/publish/history/rollback endpoints. Its first content contract
is an object with required `items: []` and optional `title`, `lead`, and `notes`.

The editor response includes `schema.fields`. Use it as the current backend contract for required fields
and simple field shapes. The frontend should not hardcode a separate validation contract for these global
sections.

Generated `practice_page`, `service_page`, and `problem_page` schemas also expose an optional page
`price` slot. This slot is not edited through the global section screen. It is a page-owned section with
`sourcePolicy: "price_inheritance"`:

- base non-regional generated pages source their page `price` from the locale-specific `global_price`;
- regional generated pages source their page `price` from the matching base non-regional page price
  section;
- the page `price` may inherit the source, override allowed fields, or append allowed list/rich-text
  fields;
- public snapshots store the resolved price payload and keep separate source/local section refs for
  diagnostics and rollback.

This means the global price screen edits the shared source, while the page section editor edits the local
page/regional layer. Header/footer remain direct shared globals and do not create page-local section
versions.

Price preview modes are intentionally separate:

- `latest_draft` preview composes the latest available source draft/published version with the latest
  available local draft/published version;
- `published` preview composes only the current published source and local versions, even if newer drafts
  already exist.

The public snapshot/publish path uses the same backend composition rule as `published` preview: the
snapshot stores only the resolved price payload, while section refs keep the exact source/local versions
that produced it.

Global sections are locale-specific. Opening the editor for `site_footer?locale=uk` reads or creates the
Ukrainian global footer section record. Russian and English versions are separate section records and
separate version histories.

Save draft:

```json
{
  "content": {
    "columns": []
  }
}
```

Validate and publish may omit `sectionVersionId`; backend then uses the latest draft:

```json
{}
```

Publishing `site_header`, `site_footer`, or `global_price` uses `rebuild_affected_snapshots`: backend
creates the new published section version and plans/rebuilds affected page snapshots without touching
unrelated page-owned draft sections.

The publish response contains:

- `publish.publishedVersionId`: the new published section version;
- `publish.affectedPages`: pages that depend on this global section;
- `publish.affectedBindings`: exact page-section bindings affected by the new section version;
- `publish.rebuiltSnapshots`: rebuild result per affected page, with `status = rebuilt | skipped | failed`;
- `editor`: fresh global-section editor state after publish.

For the UI this means: show publish success from `publishedVersionId`, then show rebuild impact from
`rebuiltSnapshots`. `failed` or `skipped` rebuilds are page/snapshot follow-up work, not a missing section
publication.

For `global_price`, affected rebuilds apply to pages that directly depend on the global source, normally
the base non-regional generated pages. Regional pages depend on the base page price layer and should be
reviewed/republished through the regional page workflow when that layer changes.

All mutation responses return a fresh `editor` object. Use it to replace the current editor state after
save, validate, publish, or rollback.

## Basic Flow

1. Load page schemas/meta.
2. Load the page workbench tree.
3. Open a page type workbench matrix.
4. Bootstrap or open a concrete page from the selected row.
5. Render `authoring.page`, editable `authoring.sections`, and read-only `authoring.runtimeSlots`.
6. Open a concrete section through the workbench section editor endpoint.
7. Save/validate/publish that section through the workbench section action endpoints.
8. Build preview through the workbench page action endpoint.
9. Publish a page through the workbench page action endpoint.
10. Rollback through the workbench page action endpoint when needed.

The frontend must not reconstruct publish rules. Backend decides what can be saved, previewed, published,
or rolled back.

## Page Schemas

Use:

```text
GET /api/admin/page-schemas
GET /api/admin/page-schemas/{pageType}
```

This is the UI metadata source for page authoring. It returns:

- registered `pageTypes`;
- supported `locales`;
- route template and route params;
- whether regional routes are supported;
- whether the body allows editor-added sections;
- fixed section slots;
- runtime slots;
- section fields and required/optional state;
- section ownership/publish/composition rules needed to decide which controls to show.
- optional `sourcePolicy` for special source resolution. Currently only `price_inheritance` exists.

The frontend should use this endpoint to build page creation forms and section editors. Do not hardcode
the available page types, slots, route params, or field lists in the frontend.

## Page Workbench

Use:

```text
GET /api/admin/page-workbench/tree?locale=uk
GET /api/admin/page-workbench/service-tree?locale=uk
GET /api/admin/page-workbench/page-types/{pageType}?locale=uk
GET /api/admin/page-workbench/pages/{pageId}/row
POST /api/admin/page-workbench/pages/bootstrap
POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/bootstrap?locale=uk
GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor
PATCH /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/state
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/draft
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/validate
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/publish
GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/history
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/rollback
GET /api/admin/page-workbench/pages/{pageId}/snapshots?limit=50&offset=0
GET /api/admin/page-workbench/pages/{pageId}/snapshots/{snapshotId}
POST /api/admin/page-workbench/pages/{pageId}/preview
POST /api/admin/page-workbench/pages/{pageId}/publish
POST /api/admin/page-workbench/pages/{pageId}/rollback
```

This is the source for the main page workbench screen: left tree plus section matrix. It is intentionally
summary-only and must not replace the section editor.

`GET /tree` returns page groups and page-type nodes:

- fixed page types already supported by the workbench: `contacts_page`, `lawyers_page`;
- generated collections: `practice_page`, `service_page`, `problem_page`, and `lawyer_page`;
- `practice_page`, `service_page`, and `problem_page` already return generated matrix rows from CMS
  reference data; `lawyer_page` is still visible as a generated collection but not fully matrix-managed yet;
- `variantMode`: `single`, `regional`, or `generated_collection`;
- `createdCount` and high-level summary counters for badges.

`GET /service-tree` returns the real service-tree hierarchy for the left page workbench area:

```text
GET /api/admin/page-workbench/service-tree?locale=uk
```

The response is nested:

- practice node;
- child service nodes;
- child problem nodes.

Each node contains:

- `sourceRecord`: the CMS reference object that drives the generated page;
- `page`: existing CMS page state, or `null` when the page is not created yet;
- `diagnostics`: source/page blockers and warnings;
- `actions.canOpen`: open the page workbench/editor when `page` exists;
- `actions.canBootstrap`: create the CMS page from this source object when backend says it is safe.

Use this endpoint for the tree-like left UI where practices contain services and services contain
problems. This tree intentionally does not expand regional variants. Use `GET /page-types/{pageType}` when
the user opens a matrix/table for one page type and needs base/regional page rows.

`GET /page-types/{pageType}` returns:

- `columns`: fixed section/runtime slots from the backend page schema;
- `columns[].compositeGroupKey`: optional key telling the UI that several columns belong to one visual
  block, for example editable CMS block settings plus a runtime list from reference data;
- `rows`: concrete page variants for the selected locale;
- `rows[].pagePath` and `rows[].publicPath`: backend-computed route fields for the row. For existing
  pages they mirror `row.page.pagePath` / `row.page.publicPath`; for not-created generated rows they show
  the route that will be used after bootstrap. They may be `null` only when the row is not route-ready;
- for generated service-tree rows, `sourceRecord`: the source practice/service/problem record that drives
  the row and route;
- for generated regional rows, `region` and `regionSlug`: the CMS region source used to build the
  regional route;
- row-level `actions`: whether the UI can open, bootstrap, preview, publish, rollback, or view the
  current snapshot for the page;
- row-level `diagnostics`: publish blockers and warnings for the whole page;
- `cells`: one summary cell per section/runtime slot;
- `summary`: counters for the whole opened matrix. `summary.errors` and `summary.warnings` are row-level
  counters, so page diagnostics such as `PAGE_NOT_CREATED` are included, not only section cell diagnostics.

`GET /pages/{pageId}/row` returns one fresh matrix row for an already created page. Use it after section
editor actions such as save draft, validate, publish independent section, rollback, enable, or disable.
The response gives backend-computed cell statuses, diagnostics, and actions, so the frontend can replace
the row in the opened matrix without recalculating publish or visibility rules locally.

For generated service-tree page types, call the same matrix endpoint:

```text
GET /api/admin/page-workbench/page-types/practice_page?locale=uk
GET /api/admin/page-workbench/page-types/service_page?locale=uk
GET /api/admin/page-workbench/page-types/problem_page?locale=uk
```

Each generated row is tied to one visible reference object from the CMS database:

- `practice_page`: one visible practice;
- `service_page`: one visible service with `serviceCond=true` and a resolved visible practice;
- `problem_page`: one visible problem with resolved visible practice and service.

For `practice_page`, `service_page`, and `problem_page`, the matrix now returns both:

- base non-regional rows, for example `/services/family-law`;
- regional rows for visible regions with a valid `sourceSlug`, for example `/kyiv/services/family-law`.

Regional rows still use the same `sourceRecord` as the base page. The region is a separate row field:

```json
{
  "kind": "regional",
  "title": "Kyiv / Family law",
  "pagePath": "services/family-law",
  "publicPath": "/kyiv/services/family-law",
  "regionSlug": "kyiv",
  "region": {
    "resource": "regions",
    "id": "region-1",
    "externalId": "74",
    "title": "Kyiv",
    "locale": "uk",
    "sourceSlug": "kyiv",
    "showOnSite": true,
    "diagnostics": []
  }
}
```

Rows contain `sourceRecord`:

```json
{
  "pageType": "practice_page",
  "resource": "practices",
  "id": "practice-1",
  "externalId": "10",
  "title": "Family law",
  "locale": "uk",
  "sourceSlug": "family-law",
  "showOnSite": true,
  "routeParams": {
    "practiceSlug": "family-law"
  },
  "pagePath": "services/family-law",
  "publicPath": "/services/family-law",
  "parentRefs": {},
  "diagnostics": []
}
```

If the generated page is not created yet, `row.page = null` and `actions.canBootstrap = true` when
`row.pagePath` and `row.publicPath` are available and there are no critical route/source diagnostics.
Use row-level route fields for UI display. `sourceRecord.pagePath` / `sourceRecord.publicPath` still
describe the base source route; regional rows may have a different `row.publicPath`. Prefer backend-owned
generated bootstrap:

```text
POST /api/admin/page-workbench/generated-sources/practice_page/{sourceRecord.id}/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/service_page/{sourceRecord.id}/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/problem_page/{sourceRecord.id}/bootstrap?locale=uk
```

Request body may be empty. For practice/service/problem generated pages, backend creates minimal valid
draft content for required page-owned sections:

- `seo`: `title` and `description` from the source object title;
- intro section: `title` from the source object title;
- paired runtime block headings, for example `service_problems_block` / `service_lawyers_block`;
- optional FAQ/consultation CTA sections are created as bindings but disabled until the editor enables and
  fills them.

The request body may still contain overrides for initial section content. Object-shaped section content is
shallow-merged over backend defaults:

```json
{
  "initialSectionContents": {
    "seo": {
      "title": "Custom SEO title"
    }
  }
}
```

To create/open a regional generated page, call the same endpoint and pass the returned `row.region.id` as
`regionId`:

```json
{
  "regionId": "region-1"
}
```

Backend rereads the source object, and when `regionId` is present also rereads the region source. It
verifies slugs/parent links/route, creates or opens the page with the same `pagePath` and the selected
`regionSlug`, and returns `{ bootstrap, workbench }`. This should be the default frontend path for creating
generated practice/service/problem pages, because the frontend does not have to trust its own assembled URL
and does not have to invent the first draft payload.

The older generic bootstrap still exists for fixed pages or advanced flows:

```json
{
  "pageType": "practice_page",
  "locale": "uk",
  "pagePath": "services/family-law",
  "regionSlug": null
}
```

If a source slug or required parent relation is missing, backend returns a generated row with critical
diagnostics such as `PAGE_SOURCE_SLUG_MISSING`, `PAGE_SOURCE_PARENT_UNRESOLVED`,
`PAGE_SOURCE_PARENT_NOT_VISIBLE`, or `PAGE_SOURCE_ROUTE_INVALID`; in that case `canBootstrap=false`.
The frontend should show these diagnostics and route the editor to fix the underlying reference record.

`POST /pages/bootstrap` creates or opens a page authoring instance from the selected workbench row and
returns `{ bootstrap, workbench }`. The request body is the same as `POST /api/admin/pages/bootstrap`:

```json
{
  "pageType": "contacts_page",
  "locale": "uk",
  "pagePath": "contacts",
  "regionSlug": null,
  "initialSectionContents": {
    "seo": {
      "title": "Contacts"
    }
  }
}
```

Use this endpoint for `actions.canBootstrap`. After success, replace the not-created row with
`response.workbench.row`. The frontend should not build routes or section bindings itself; backend resolves
the page schema, route, shared sections, initial section versions, and row state. If a page already exists
for the same public route, the endpoint returns `bootstrap.created = false` plus the existing page row.

The workbench section editor endpoints wrap the same editor logic as
`/api/admin/pages/{pageId}/sections/{slotKey}/editor...`, but always return a fresh workbench row:

- `GET /pages/{pageId}/sections/{slotKey}/editor`: returns `{ editor, workbench }`;
- `PATCH /pages/{pageId}/sections/{slotKey}/editor/state`: returns `{ updateState, workbench }`;
- `POST /pages/{pageId}/sections/{slotKey}/editor/draft`: returns `{ saveDraft, workbench }`;
- `POST /pages/{pageId}/sections/{slotKey}/editor/validate`: returns `{ validation, workbench }`;
- `POST /pages/{pageId}/sections/{slotKey}/editor/publish`: returns `{ publish, workbench }`;
- `GET /pages/{pageId}/sections/{slotKey}/editor/history`: returns `{ history, workbench }`;
- `POST /pages/{pageId}/sections/{slotKey}/editor/rollback`: returns `{ rollback, workbench }`.

Use these workbench endpoints for the main page editor UI. The nested operation object contains the same
payload as the lower-level authoring endpoint, and `response.workbench.row` is the row that should replace
the current matrix row after the action. This removes the need for the frontend to manually call
`GET /pages/{pageId}/row` after every save, validation, publish, rollback, enable, or disable action.

The workbench page action endpoints wrap the same lifecycle logic as `POST /api/admin/pages/{pageId}/...`,
but they also return `workbench`, a fresh row-refresh payload for the affected page:

- `POST /pages/{pageId}/preview`: returns `{ preview, workbench }`;
- `POST /pages/{pageId}/publish`: returns `{ publish, workbench }`;
- `POST /pages/{pageId}/rollback`: returns `{ rollback, workbench }`.

Use these endpoints for page buttons on the matrix screen. The request bodies are the same as the existing
page lifecycle endpoints. After a successful action, replace the row with `response.workbench.row` and keep
using backend-provided `actions`/`diagnostics`.

For generated service-tree pages, the backend now resolves missing runtime/read-model payloads during
preview and publish. The frontend does not need to manually send payloads for these slots:

- `practice_services`;
- `practice_lawyers`;
- `service_problems`;
- `service_lawyers`;
- `problem_lawyers`.

The resolver reads CMS reference tables, uses the page route context (`services/{practiceSlug}`,
`services/{practiceSlug}/{serviceSlug}`, etc.), and returns list payloads with route-ready items. If the
frontend sends a `runtimePayloads` entry for one of these slots, backend keeps the provided payload and does
not resolve that same slot again. This is mainly useful for tests or transitional UI experiments; normal CMS
frontend code should let backend resolve service-tree runtime slots.

Runtime resolution can block preview/publish with `PAGE_RUNTIME_RESOLUTION_FAILED` when the page route no
longer matches visible reference data or a visible child item has no required source slug. Show this as a
backend validation error and route the editor to fix the underlying reference object.

Snapshot history endpoints support the rollback UI:

- `GET /pages/{pageId}/snapshots`: returns historical page snapshots, newest first;
- `GET /pages/{pageId}/snapshots/{snapshotId}`: returns one snapshot with its public payload.

Use the list endpoint to open the page history panel. Each item contains:

- `snapshotId`, `snapshotNo`, `status`;
- `createdBy` / `createdAt`: who created this snapshot and when;
- `activatedBy` / `activatedAt`: who made it current and when, only for the current snapshot;
- `isCurrent`: whether this snapshot is currently served publicly;
- `sectionRefs`: exact section versions used by that snapshot.

Use the detail endpoint when the editor clicks "view" on a historical snapshot. It returns the same metadata
plus `publicPayload`, so the UI can preview exactly what rollback would restore. To rollback, send the chosen
`snapshotId` as `sourceSnapshotId` to `POST /pages/{pageId}/rollback`. Rollback creates a new current snapshot;
it does not mutate the historical snapshot.

For this first slice, `contacts_page` and `lawyers_page` are supported as single-row matrices. Generated
service-tree matrices are available for base and regional practice, service, and problem pages.

Generated service-tree schemas now pair editable CMS block sections with runtime/read-model slots through
`compositeGroupKey`, so the UI can render them as one block:

- `practice_services_block` + `practice_services` use `practice_services`;
- `practice_lawyers_block` + `practice_lawyers` use `practice_lawyers`;
- `service_problems_block` + `service_problems` use `service_problems`;
- `service_lawyers_block` + `service_lawyers` use `service_lawyers`;
- `problem_lawyers_block` + `problem_lawyers` use `problem_lawyers`.

The `*_block` section stores CMS-authored title/lead/settings for the block. The runtime slot stores the
read-only list contract. Optional page-owned `*_faq` and `*_consultation_cta` sections are also present
and may be enabled/disabled through backend-provided actions. Price sections are modeled as source-backed
page-owned sections: base generated pages inherit from `global_price`, while regional generated pages
inherit from the matching base page price section.

Section cells contain only metadata and status:

- ids: `bindingId`, `sectionId`, `sourceSectionId`, `localSectionId`;
- state: `visibility`, `draftStatus`, `draftVersion`, `publishedVersion`;
- ownership/publish info: `ownershipScope`, `publishMode`, `composition`;
- `diagnostics`: errors, warnings, missing published version, stale state;
- `actions`: what the UI may show (`canOpen`, `canEdit`, `canSaveDraft`, `canPublish`, etc.).
- `actions.canEnable` / `actions.canDisable`: show section visibility controls computed by the backend.

Section cells do not contain section content. When the editor opens one cell, load the full edit state
through `GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor`.

Runtime cells represent read-model data, not editable CMS drafts. They expose `source` metadata and should
be shown as read-only blocks in the matrix.

Use row-level `actions` for page buttons:

- `actions.canBootstrap`: show create/bootstrap page action when the row is not created yet;
- `actions.canOpen`: open page authoring state;
- `actions.canPreview`: allow preview build for the current draft/published mix;
- `actions.canPublish`: allow page publish;
- `actions.canRollback`: allow rollback flow only when the page already has a current snapshot;
- `actions.canViewCurrentSnapshot`: show current public snapshot details.

Use row-level `diagnostics.blockingReasons` for page banners/tooltips. The frontend should display the
messages and codes, but should not recreate the rules. Important codes:

- `PAGE_NOT_CREATED`;
- `PAGE_SECTION_DRAFT_STALE`;
- `PAGE_SECTION_VALIDATION_FAILED`;
- `PAGE_REQUIRED_SECTION_EMPTY`;
- `PAGE_REQUIRED_INDEPENDENT_SECTION_NOT_PUBLISHED`;
- `PAGE_NO_CURRENT_SNAPSHOT`.

## Pages Catalog

Use:

```text
GET /api/admin/pages
```

Optional query params:

- `pageType`;
- `locale`;
- `status`;
- `q`;
- `limit`;
- `offset`.

This endpoint is the source for the CMS screen "Pages". It returns one row per page with:

- page identity and route: `pageId`, `pageType`, `locale`, `regionSlug`, `pagePath`, `publicPath`;
- raw page `status`;
- derived `publishState`: `not_published`, `published`, `draft_changed`, `requires_review`;
- current published snapshot summary, if it exists;
- section summary: total bindings, draft bindings, stale bindings, missing published bindings;
- `createdAt` and `updatedAt`.

Use `publishState` for badges in the page list. Use `sectionSummary.staleBindings > 0` to show that the
page requires review before publish. The catalog does not replace `GET /api/admin/pages/{pageId}/authoring`;
it only helps the frontend choose which page to open.

## Authoring State

`GET /api/admin/pages/{pageId}/authoring` returns:

- `page`: page identity, locale, route, public path, and status;
- `sections`: CMS section slots;
- `runtimeSlots`: read-only runtime/read-model slots.

For each item in `sections`, pay attention to:

- `slotKey`: stable key used in save/preview/publish workflows;
- `fields`: editable field contract for the UI;
- `layout`: where the section belongs;
- `ownershipScope`: `page_owned`, `global_owned`, etc.;
- `publishMode`: `with_page` or `independent`;
- `visibility`: enabled/disabled state;
- `draftStatus`: `fresh` or `draft_stale`;
- `composition`: inherit/override/append rules;
- `draftVersion` and `publishedVersion`.

Only page-owned, editable slots should expose draft editing controls. Shared/global/runtime slots should be
displayed as part of the page state, but not edited through the page-owned draft endpoint.

## Section Editor

Use:

```text
GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor
```

This endpoint opens one CMS section from the workbench matrix. It is the main payload for the section edit
screen. The response shape is:

```json
{
  "editor": {},
  "workbench": {
    "row": {}
  }
}
```

Use `response.editor` to render the section editor and `response.workbench.row` to refresh the matrix row
behind the opened editor.

`response.editor` contains:

- `page`: page identity and route;
- `slot`: schema-driven section metadata: fields, layout, content shape, allowed composition strategies;
  inherited/source-backed sections also include `slot.fieldPolicies`, so the UI knows which fields may
  inherit, override, or append;
- `section`: binding/current authoring state: ids, ownership, publish mode, visibility, composition,
  draft/published version refs;
- `content.draft`: full current draft content for this section, if a draft exists;
- `content.published`: full current published content for this section, if a published version exists;
- `content.source`: for inherited/source-backed sections, the current source draft/published versions;
- `content.local`: for inherited/source-backed sections, the page/regional local draft/published versions;
- `content.resolved.draft`: backend-composed draft preview content from source + local, when it can be
  resolved;
- `content.resolved.published`: backend-composed published content from source + local, when it can be
  resolved;
- `diagnostics.draftValidation`: latest recorded publish validation state for the draft, if available;
- `diagnostics.errors` and `diagnostics.warnings`;
- `actions`: backend-computed flags for the UI.

For normal non-inherited sections, `content.source`, `content.local`, and `content.resolved.*` may be
`null`; use the existing `content.draft` / `content.published` fields. For page price sections, prefer
showing the three-layer view:

- source: inherited parent content;
- local: what this page/region changes;
- resolved: what preview/publish will render.

The frontend should not merge source and local content itself. Use `content.resolved.*` for the preview of
the final section result, and use `section.composition` plus `slot.fieldPolicies` only to render controls.
For inherited price sections, `content.resolved.draft` is the editor's latest-draft preview and
`content.resolved.published` is the currently published result. Do not show draft-resolved content as if it
were already public.

Important boundaries:

- Workbench matrix cells are summary-only.
- Section editor is the place where full section content appears.
- Runtime slots must not call this endpoint; they are read-model blocks and should stay read-only in this
  slice.
- `actions.canSavePageDraft` means the backend can save this slot as a page-owned draft.
- `actions.canSaveIndependentDraft` means the backend can save this slot as an independent/global section
  draft.
- `actions.canEnableSection` and `actions.canDisableSection` mean the backend allows changing only the
  page binding visibility for this slot.
- The frontend should use the page-scoped editor action endpoints below for both cases. The frontend does
  not need to decide which low-level section lifecycle endpoint is correct.

## Section Editor Actions

Use these endpoints from the section edit screen:

```text
PATCH /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/state
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/draft
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/validate
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/publish
GET  /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/history
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/rollback
```

State request body:

```json
{
  "visibility": "disabled"
}
```

Use this endpoint for section enable/disable switches in the page editor. It updates only the page-section
binding visibility. It does not create a new section draft and does not change published section versions.
The backend rejects disabling fixed/required slots where the page schema does not allow it. The response
returns `previousVisibility`, the new `visibility`, and a reloaded `editor` payload.
In the workbench wrapper, read it as `response.updateState.editor` and then replace the matrix row with
`response.workbench.row`.

Draft request body:

```json
{
  "content": {
    "title": "Contacts"
  }
}
```

The backend decides whether this is a `with_page` page-owned section or an `independent` global section.
The response returns operation metadata plus a reloaded `editor` payload. Use `response.editor` as the new
current section state in the UI on the lower-level endpoint. In the workbench wrapper, use
`response.saveDraft.editor` and then replace the matrix row with `response.workbench.row`.

Validate request body:

```json
{
  "sectionVersionId": "optional-draft-version-id",
  "recordDiagnostics": true
}
```

If `sectionVersionId` is omitted, the backend validates the current draft visible in the editor payload.
The response returns `ok`, `errors`, `validationRunId`, and a reloaded `editor` payload.
In the workbench wrapper, use `response.validation.editor` and `response.workbench.row`.

Publish request body:

```json
{
  "sectionVersionId": "optional-draft-version-id"
}
```

This endpoint is only for independent sections such as shared/global sections. Page-owned sections are
published with the page through `POST /api/admin/pages/{pageId}/publish`.
In the workbench wrapper, use `response.publish.editor` and `response.workbench.row`.

History:

```text
GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/history?limit=50&offset=0
```

The response returns version rows for the section currently opened through the page editor:

- draft, published and archived versions;
- version content for preview/review;
- `createdBy`, `createdAt`, `publishedBy`, `publishedAt`;
- `isCurrentDraft` and `isCurrentPublished`;
- `canRollback`, which is true only for published versions.

Rollback:

```text
POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/rollback
```

For the workbench UI use:

```text
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/rollback
```

Request body:

```json
{
  "sourcePublishedVersionId": "section-contacts-header-published-v1"
}
```

Rollback does not move the published pointer backwards. It creates a new draft copied from the selected
published version and returns a reloaded `editor` payload. For page-owned sections the backend also points
the page binding to the new rollback draft. For independent/global sections the backend updates the section
latest draft pointer, and pages keep their published state until a later publish/rebuild.
In the workbench wrapper, use `response.rollback.editor` and `response.workbench.row`.

The older `POST /api/admin/pages/{pageId}/sections/{slotKey}/draft` endpoint still exists for the first
page-owned slice, but new CMS page editor UI should prefer the `/editor/draft` endpoint.

The lower-level `/api/admin/pages/.../editor...` endpoints still exist and keep the same operation payloads.
For the main CMS page workbench, prefer the `/api/admin/page-workbench/...` wrappers because they remove
one extra refresh request after every action.

## Preview

Use:

```text
POST /api/admin/pages/{pageId}/preview
```

The response payload is the protected preview payload for the preview frontend. Preview may include latest
draft state and runtime payloads supplied by the backend/admin flow. The public frontend must not use this
endpoint.

## Publish

Use:

```text
POST /api/admin/pages/{pageId}/publish
```

The response contains:

- `snapshotId`;
- `snapshotNo`;
- `publicPath`;
- `withPageSectionCommits`;
- final public `payload`.

After publish, the public frontend should read the current published snapshot/public endpoint. It should
not read authoring state.

## Rollback

Use:

```text
POST /api/admin/pages/{pageId}/rollback
```

Rollback creates a new current snapshot from a historical source snapshot. It does not mean the frontend
should manually assemble old page state.

## Planned Backend Follow-Ups For CMS Front

The current page workbench slice is intentionally limited to the first usable page-editor flow. The backend
team plans to add the following pieces next, so the frontend should keep screens modular and avoid hardcoding
temporary assumptions:

- Practice/service/problem hierarchy: generated workbench rows and page schemas for practice, service,
  and problem are present for base and regional variants. The backend service-tree endpoint stays
  non-regional for the left hierarchy; the opened matrix is where regional page rows appear.
- Dependency-aware runtime/read-model slots: practice pages should expose services, service pages should
  expose problems, and generated pages should be driven by CMS reference data rather than frontend guesses.
- Richer page bootstrap for generated lawyer pages remains future work. Practice, service, and problem
  pages should already be created through `POST /api/admin/page-workbench/generated-sources/.../bootstrap`;
  this endpoint now also supplies minimal required section drafts when the frontend sends an empty body.
- Section action coverage for future movable/blog-like sections: add/remove/reorder will come later and
  should be a backend-owned action layer, not a frontend-only mutation.
- Warning diagnostics: currently critical validation is the main blocker; field-level warnings will become
  part of section/page diagnostics without blocking every save.
- Typed client generation: OpenAPI should remain the source for DTOs; frontend should prefer generated
  clients when that pipeline is connected.

## UI Notes

- Show `draft_stale` clearly: the page/section requires review before publish.
- Keep preview and published/current state visually distinct.
- Do not allow editing runtime slots directly from the page section draft form.
- Do not infer publishability only from visible fields. Backend publish validation is the final authority.
