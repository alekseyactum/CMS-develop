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
GET  /api/admin/pages
POST /api/admin/pages/bootstrap
GET  /api/admin/pages/{pageId}/authoring
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
6. Save drafts only through `POST /sections/{slotKey}/draft`.
7. Build preview through `POST /preview`.
8. Publish through `POST /publish`.
9. Rollback through `POST /rollback` when needed.

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
- `cells`: one summary cell per section/runtime slot;
- `summary`: counters for the whole opened matrix.

For this first slice, `contacts_page` and `lawyers_page` are supported as single-row matrices. Regional
and generated matrices will be expanded later without changing the general contract shape.

Section cells contain only metadata and status:

- ids: `bindingId`, `sectionId`, `sourceSectionId`, `localSectionId`;
- state: `visibility`, `draftStatus`, `draftVersion`, `publishedVersion`;
- ownership/publish info: `ownershipScope`, `publishMode`, `composition`;
- `diagnostics`: errors, warnings, missing published version, stale state;
- `actions`: what the UI may show (`canOpen`, `canEdit`, `canSaveDraft`, `canPublish`, etc.).

Section cells do not contain section content. When the editor opens one cell, load the full edit state
through `GET /api/admin/pages/{pageId}/authoring` or the future dedicated section editor endpoint.

Runtime cells represent read-model data, not editable CMS drafts. They expose `source` metadata and should
be shown as read-only blocks in the matrix.

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

## Save Draft

Use:

```text
POST /api/admin/pages/{pageId}/sections/{slotKey}/draft
```

Request body:

```json
{
  "content": {
    "title": "Contacts"
  }
}
```

The backend returns the updated section state. Use that returned section as the current UI state for that
slot.

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

## UI Notes

- Show `draft_stale` clearly: the page/section requires review before publish.
- Keep preview and published/current state visually distinct.
- Do not allow editing runtime slots directly from the page section draft form.
- Do not infer publishability only from visible fields. Backend publish validation is the final authority.
