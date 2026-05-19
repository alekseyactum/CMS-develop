# CMS Front Reference Data Task

This document is the implementation task for the CMS frontend developer for the first admin reference-data
screens.

The goal is to give editors a simple interface for ERP-imported site dictionaries while preserving the
ownership boundary:

- ERP owns source identity, relations, ranking signals, and `show_on_site`;
- CMS owns public slugs, CMS media references, sort order, localized public labels, descriptions, and
  diagnostics display;
- the backend owns the field contract, validation rules, and admin API shape.

The frontend must not call internal ERP upsert endpoints and must not duplicate backend field rules.

## Existing Backend Contract

Use these admin endpoints:

```text
GET   /api/admin/reference/meta
GET   /api/admin/reference/{resource}
GET   /api/admin/reference/{resource}/{id}
PATCH /api/admin/reference/{resource}/{id}
PUT   /api/admin/reference/{resource}/{id}/translations/{locale}
```

The same contract is also described in the backend Swagger/OpenAPI metadata. For reference-data screens,
prefer the OpenAPI response examples for `meta`, `lawyers`, `regions`, and `services` over copying examples
from chat messages.

The frontend should first call:

```text
GET /api/admin/reference/meta
```

This endpoint returns:

- supported locales;
- supported resources;
- list filters;
- ERP-owned source fields;
- CMS-owned editable fields;
- relation fields;
- localized fields;
- required fields;
- whether a resource has `showOnSite`;
- whether a resource is editable/translatable;
- whether a resource tracks the last CMS editor.

The frontend may keep human-friendly UI labels locally, but the resource/field editability and required
state must come from backend meta.

## Supported Resources

The first release scope includes:

```text
practices
services
problems
regions
offices
lawyers
reviews
lawyer-qualifications
region-qualifications
```

Qualification resources are read-only in CMS. They are ranking signals, not normal dictionaries.

## Required Screens

### Reference Resource List

Create a list screen for each resource.

The list screen should call:

```text
GET /api/admin/reference/{resource}?q=&showOnSite=&limit=&offset=
```

Use filters only when they are useful for the selected resource:

- text search by `q`;
- `showOnSite` filter only for resources where meta says `hasShowOnSite=true`;
- pagination by `limit` and `offset`.

Each row should show:

- object title from the best available source/localized field;
- `externalId`;
- `showOnSite` if present;
- main CMS-owned fields such as `publicSlug`, `sortOrder`, or `photoMediaId` when present;
- relation hints from `relationFields`;
- readable relation objects from `relations` when present;
- diagnostics summary with warning/error count;
- last CMS editor when the backend returns `cmsUpdatedBy`;
- link/button to open the object detail.

Do not allow editing directly inside the first list version unless it is trivial and uses the same PATCH
rules as the detail screen.

### Reference Detail

When the editor opens one object, call:

```text
GET /api/admin/reference/{resource}/{id}
```

This detail read is important because backend guarantees missing translation skeleton rows here. The
frontend should use the detail response as the source for the edit form.

The detail screen should have clear groups:

- ERP source fields: read-only;
- relation fields: read-only, but visible for diagnostics;
- readable relation objects: read-only helper data for display/select labels;
- CMS base fields: editable only when meta marks them editable;
- translations: one tab or segment per locale;
- diagnostics: visible near the top and near affected fields where practical.
- last CMS editor/date: show `cmsUpdatedBy` / `cmsUpdatedAt` for normal dictionary resources when present.

Do not expose source fields, relation fields, `showOnSite`, or qualification scores as editable controls.

For `lawyers`, backend keeps raw relation IDs in `relationFields` and additionally returns readable linked
objects in `relations`:

```json
{
  "relationFields": {
    "regionExternalId": "74",
    "officeExternalId": "30",
    "regionId": "8d860f99-8e92-4a9b-a82b-20f06bc6ff9b",
    "officeId": "7f0a1760-2335-447f-9644-f4f970e0bd0a"
  },
  "relations": {
    "region": {
      "resource": "regions",
      "id": "8d860f99-8e92-4a9b-a82b-20f06bc6ff9b",
      "externalId": "74",
      "displayTitle": "Київ",
      "translations": {
        "uk": {
          "publicName": "Київ",
          "menuTitle": "Київ",
          "prepositionalName": "Києві"
        }
      }
    },
    "office": {
      "resource": "offices",
      "id": "7f0a1760-2335-447f-9644-f4f970e0bd0a",
      "externalId": "30",
      "displayTitle": "Київ, вул. Хрещатик",
      "translations": {
        "uk": {
          "address": "Київ, вул. Хрещатик"
        }
      }
    }
  }
}
```

Use `relations.region` and `relations.office` to show human-readable region/office labels without extra
requests. Keep `relationFields` as the technical IDs/diagnostic source.

## Save Rules

### CMS Base Fields

For fields from `cmsFields` where `editable=true`, save with:

```http
PATCH /api/admin/reference/{resource}/{id}
```

Request body:

```json
{
  "publicSlug": "family-law",
  "sortOrder": 10
}
```

Send only fields that changed. The backend will reject read-only or unsupported fields.

### Localized Fields

For translation fields, save one locale at a time:

```http
PUT /api/admin/reference/{resource}/{id}/translations/{locale}
```

Request body example:

```json
{
  "publicName": "Family law",
  "menuTitle": "Family"
}
```

Send only fields that belong to that resource translation contract. The backend will reject unsupported
localized fields.

## Diagnostics UI

Every record can include `diagnostics`.

Display diagnostics in editor language as simple messages. At minimum, preserve backend `message` if no
localized UI copy exists yet.

Severity behavior:

- `error`: the object cannot be safely used by publish/runtime logic until fixed or until the consuming
  page/section decides not to use it;
- `warning`: the object is incomplete or needs editor attention, but the backend may still allow saving.

Examples:

- missing public slug;
- missing localized public name;
- unresolved relation;
- missing localized address.

The frontend must not decide publishability globally from diagnostics. It should display diagnostics and
let page/section publish validation make the final decision.

## Field Ownership Rules

Read-only in CMS:

- `sourceFields`;
- `relationFields`;
- `externalId`;
- `source`;
- `showOnSite`;
- qualification scores and relations.

Editable in CMS only when meta says so:

- public slugs;
- media references such as lawyer photo id;
- sort order;
- localized public names, menu titles, descriptions, addresses, review display text.
- region `prepositionalName`, edited separately per locale.

`showOnSite` comes from ERP. CMS frontend can display it and filter by it, but must not edit it.

## UX Requirements For First Iteration

Keep the first implementation practical:

- resource navigation by supported resources;
- list with search/filter/pagination;
- detail page with source/CMS/translations/diagnostics groups;
- save CMS base fields;
- save translations per locale;
- disabled/read-only controls for non-editable data;
- visible loading, empty, not-found, validation error, and save-error states;
- no editor-authored writes when the editor only opens detail, except the backend's idempotent translation
  skeleton creation.

The first version does not need advanced bulk editing, drag sorting, import screens, or full media picker
integration. For media fields, a plain id field or temporary selector is acceptable until the media module
is implemented.

## Acceptance Criteria

The task is ready when:

- frontend uses `GET /api/admin/reference/meta` before building reference-data screens;
- all supported resources are reachable from the UI;
- `lawyer-qualifications` and `region-qualifications` are displayed read-only;
- editable fields are derived from backend meta;
- source/relation/visibility fields cannot be edited;
- detail read creates and displays missing `uk`, `ru`, `en` translation skeletons;
- PATCH updates CMS base fields;
- PUT updates localized fields for each locale;
- normal dictionary detail/list views show the last CMS editor when returned by backend;
- region translations expose `prepositionalName` for each locale;
- diagnostics are visible and grouped by severity;
- the UI handles backend validation errors without losing the editor's current form state.

## Non-Goals

Do not implement in this frontend task:

- ERP upsert flows;
- direct database access;
- public site read models;
- page publish logic;
- global publishability decisions for reference objects;
- changing `showOnSite` from CMS;
- writing CMS edits back to ERP.
