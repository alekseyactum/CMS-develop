# CMS Front Page Authoring Task

This document is the first implementation task for CMS frontend page authoring screens.

The backend contract is available in Swagger/OpenAPI. Use OpenAPI examples as the primary source for
request/response shapes, especially for authoring state, preview, publish, and rollback.

## Endpoints

```text
GET  /api/admin/page-schemas
GET  /api/admin/page-schemas/{pageType}
GET  /api/admin/page-workbench/tree
GET  /api/admin/page-workbench/page-types/{pageType}
GET  /api/admin/page-workbench/pages/{pageId}/row
POST /api/admin/page-workbench/pages/bootstrap
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

The frontend should use this endpoint to build page creation forms and section editors. Do not hardcode
the available page types, slots, route params, or field lists in the frontend.

## Page Workbench

Use:

```text
GET /api/admin/page-workbench/tree?locale=uk
GET /api/admin/page-workbench/page-types/{pageType}?locale=uk
GET /api/admin/page-workbench/pages/{pageId}/row
POST /api/admin/page-workbench/pages/bootstrap
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
- generated collections that are visible in the tree but not fully matrix-managed yet: `lawyer_page`;
- `variantMode`: `single`, `regional`, or `generated_collection`;
- `createdCount` and high-level summary counters for badges.

`GET /page-types/{pageType}` returns:

- `columns`: fixed section/runtime slots from the backend page schema;
- `rows`: concrete page variants for the selected locale;
- row-level `actions`: whether the UI can open, bootstrap, preview, publish, rollback, or view the
  current snapshot for the page;
- row-level `diagnostics`: publish blockers and warnings for the whole page;
- `cells`: one summary cell per section/runtime slot;
- `summary`: counters for the whole opened matrix.

`GET /pages/{pageId}/row` returns one fresh matrix row for an already created page. Use it after section
editor actions such as save draft, validate, publish independent section, rollback, enable, or disable.
The response gives backend-computed cell statuses, diagnostics, and actions, so the frontend can replace
the row in the opened matrix without recalculating publish or visibility rules locally.

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

For this first slice, `contacts_page` and `lawyers_page` are supported as single-row matrices. Regional
and generated matrices will be expanded later without changing the general contract shape.

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
- `section`: binding/current authoring state: ids, ownership, publish mode, visibility, composition,
  draft/published version refs;
- `content.draft`: full current draft content for this section, if a draft exists;
- `content.published`: full current published content for this section, if a published version exists;
- `diagnostics.draftValidation`: latest recorded publish validation state for the draft, if available;
- `diagnostics.errors` and `diagnostics.warnings`;
- `actions`: backend-computed flags for the UI.

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
  problem, and later regional variants.
- Dependency-aware runtime/read-model slots: practice pages should expose services, service pages should
  expose problems, and generated pages should be driven by CMS reference data rather than frontend guesses.
- Richer page bootstrap for generated pages: creating/opening a page from a reference object such as a
  practice, service, problem, or lawyer.
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
