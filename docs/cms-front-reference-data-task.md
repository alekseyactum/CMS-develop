# CMS Front Reference Data Task

This document is the implementation task for the CMS frontend developer for the first admin reference-data
screens.

The goal is to give editors a simple interface for ERP-imported site dictionaries while preserving the
ownership boundary:

- ERP owns source identity, source slugs for practices/services/problems/regions, relations, ranking
  signals, and `show_on_site`;
- CMS owns CMS media references, sort order, localized public labels, descriptions, generated read-only
  lawyer slugs, and diagnostics display;
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
Backend may return qualification sync-state fields such as `isActive` and `removedFromSourceAt`.
Show them as read-only status data when present; do not expose them as editable controls.

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
- main CMS-owned fields such as `sortOrder`, `photoMediaId`, or read-only lawyer `slug` when present;
- relation hints from `relationFields`;
- readable relation objects from `relations` when present;
- readable child lists from `children` when present;
- diagnostics summary with warning/error count;
- last non-translation CMS editor when the backend returns `updatedBy`;
- link/button to open the object detail.

Do not allow editing directly inside the first list version unless it is trivial and uses the same PATCH
rules as the detail screen.

### Reference Detail

When the editor opens one object, call:

```text
GET /api/admin/reference/{resource}/{id}
```

List and detail reads are important because backend guarantees missing translation skeleton rows there.
The frontend should use backend responses as the source for the edit form and diagnostics.

The detail screen should have clear groups:

- ERP source fields: read-only;
- relation fields: read-only, but visible for diagnostics;
- readable relation objects: read-only helper data for display/select labels;
- readable child lists: read-only helper data for dependency displays;
- CMS base fields: editable only when meta marks them editable;
- translations: one tab or segment per locale;
- diagnostics: visible near the top and near affected fields where practical.
- last non-translation CMS editor/date: show `updatedBy` / `updatedAt` for normal dictionary resources
  when present.
- translation audit: show `translationsMeta.latestUpdatedAt`, `translationsMeta.latestUpdatedBy`, and
  per-locale `translationsMeta.locales[locale]` where useful.

Do not expose source fields, relation fields, `showOnSite`, qualification scores, or qualification
sync-state fields as editable controls.

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

For dependency displays, backend returns `children`.

Practices can include their services:

```json
{
  "children": {
    "services": [
      {
        "resource": "services",
        "id": "9b1598ad-889a-4f82-9392-cf2bc757fb24",
        "externalId": "15",
        "displayTitle": "Legal consultation",
        "sourceFields": {
          "showOnSite": true,
          "serviceCond": true,
          "legalCond": false
        },
        "cmsFields": {
          "sortOrder": 10
        },
        "translations": {
          "uk": {
            "publicName": "Юридична консультація",
            "menuTitle": "Консультація"
          }
        }
      }
    ]
  }
}
```

Services can include their problems:

```json
{
  "children": {
    "problems": [
      {
        "resource": "problems",
        "id": "7aebafaf-13ce-4038-b14a-fc5b4dbf0ba3",
        "externalId": "31",
        "displayTitle": "Court dispute"
      }
    ]
  }
}
```

These child lists are read-only in this API. They are for showing the hierarchy and dependencies in the
CMS frontend. Editing a child object still happens through its own resource detail endpoint.

## Save Rules

### CMS Base Fields

For fields from `cmsFields` where `editable=true`, save with:

```http
PATCH /api/admin/reference/{resource}/{id}
```

Request body:

```json
{
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

### Navigation Title Fields

For practice, service, problem, and region dictionaries, the editor-facing title fields have different
jobs:

- `sourceFields.sourceName` and `sourceFields.sourceShortname` are ERP/source-owned read-only fallbacks.
- `translations.{locale}.publicName` is the normal public/content name.
- `translations.{locale}.menuTitle` is the short navigation label used by backend-generated breadcrumbs,
  menus, hierarchy labels, and compact link lists.

The backend display priority for navigation contexts is:

```text
menuTitle ?? publicName ?? sourceName
```

When translation skeletons are created, `menuTitle` is prefilled from `sourceShortname` and then
`sourceName`; `publicName` is prefilled from `sourceName`. Editors can change both through the translation
editor. Missing or overlong title values are warnings, not blocking errors.

## Diagnostics UI

Every record can include `diagnostics`.

Display diagnostics in editor language as simple messages. At minimum, preserve backend `message` if no
localized UI copy exists yet.

Severity behavior:

- `error`: the object cannot be safely used by publish/runtime logic until fixed or until the consuming
  page/section decides not to use it;
- `warning`: the object is incomplete or needs editor attention, but the backend may still allow saving.

Examples:

- missing source slug for visible routable source dictionaries;
- missing generated lawyer slug;
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
- source slugs for practices/services/problems/regions and generated lawyer `slug`;
- qualification scores, relations, `isActive`, and `removedFromSourceAt`.

Editable in CMS only when meta says so:

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

## Media Record Contract

The backend now exposes the first media-record API for CMS-owned media metadata:

```text
GET    /api/admin/media/meta
GET    /api/admin/media
GET    /api/admin/media/{id}
GET    /api/admin/media/{id}/file
POST   /api/admin/media/upload
POST   /api/admin/media
POST   /api/admin/media/{id}/complete-upload
PUT    /api/admin/media/{id}/translations/{locale}
DELETE /api/admin/media/{id}
```

This API manages CMS media records and file upload through `cms-back`. The bucket may stay private. The
frontend must not upload directly to Cloud Storage, invent storage object keys, or treat the returned media
URL as a direct Cloud Storage public URL.

The primary first upload flow is:

1. frontend sends multipart form data to `POST /api/admin/media/upload`;
2. backend validates usage type, MIME, size, and required localized media text;
3. backend creates the media record, generates the object key, uploads bytes to the configured bucket, and
   marks the record `uploaded`;
4. frontend receives the ready `AdminMediaAsset`;
5. only `uploaded` media can be used where public rendering requires an actual file.

The lower-level `POST /api/admin/media` plus `POST /api/admin/media/{id}/complete-upload` endpoints still
exist as an internal/advanced path, but normal CMS frontend upload should use `POST /api/admin/media/upload`.

The protected admin preview/download endpoint is:

```http
GET /api/admin/media/{id}/file
```

It streams file bytes only for an active uploaded media record. It is for CMS admin preview and media
picker use, not for public site rendering. Because `cms-back` is not a browser-public service in the
develop contour, `cms-front` should proxy this endpoint through its own authenticated server-side route
when an `<img>`/preview URL is needed in the browser.

`GET /api/admin/media/meta` returns usage policies:

- supported `usageType` values;
- supported `ownerResource` values;
- allowed MIME types;
- maximum file size;
- whether localized `altText` and `titleText` are required;
- supported upload states;
- serving path pattern.

Initial usage types:

```text
lawyer_photo
article_cover
og_image
license_document
generic
```

For public image usages such as `lawyer_photo`, `article_cover`, and `og_image`, the backend requires
`altText` and `titleText` for every supported locale.

`usageType` describes the file policy and purpose: MIME types, size, and required localized metadata.
It must not be expanded just to say which concrete object owns the file. Object ownership is passed
separately as `ownerResource` plus `ownerId`. Initial owner resources are:

```text
lawyers
pages
```

Use `ownerResource=lawyers` for lawyer photos. Use `ownerResource=pages` for page-owned media such as
blog/media/case covers, including case pages, when the page id is known.

Upload a file through the backend:

```http
POST /api/admin/media/upload
Content-Type: multipart/form-data
```

Form fields:

- `file`: binary file;
- `usageType`: one of the backend usage types;
- `ownerResource`: optional, one of the backend owner resources;
- `ownerId`: optional, required together with `ownerResource`;
- `translations`: JSON string with localized media metadata;
- `width`: optional positive integer;
- `height`: optional positive integer.

Example `translations` value:

```json
{
  "uk": { "altText": "Ivan Ivanov lawyer portrait UK", "titleText": "Ivan Ivanov UK" },
  "ru": { "altText": "Ivan Ivanov lawyer portrait RU", "titleText": "Ivan Ivanov RU" },
  "en": { "altText": "Ivan Ivanov lawyer portrait", "titleText": "Ivan Ivanov" }
}
```

Create a pending media record without uploading bytes:

```http
POST /api/admin/media
```

```json
{
  "usageType": "lawyer_photo",
  "ownerResource": "lawyers",
  "ownerId": "7f94fc5e-80b5-401e-9100-5d6f0f95ce04",
  "originalFilename": "ivan-ivanov.webp",
  "mimeType": "image/webp",
  "sizeBytes": 112000,
  "translations": {
    "uk": { "altText": "Ivan Ivanov lawyer portrait UK", "titleText": "Ivan Ivanov UK" },
    "ru": { "altText": "Ivan Ivanov lawyer portrait RU", "titleText": "Ivan Ivanov RU" },
    "en": { "altText": "Ivan Ivanov lawyer portrait", "titleText": "Ivan Ivanov" }
  }
}
```

The backend owns and returns:

- `id`;
- `ownerResource` and `ownerId` when an owner context was supplied;
- configured `bucket`;
- backend-generated `objectKey`;
- stable `servingPath`, for example `/media/{mediaId}/original.webp`;
- `lifecycleState`;
- `uploadState`;
- localized `translations`;
- `translationsMeta`;
- audit fields.

The `objectKey` is environment-neutral inside the selected bucket, for example:

```text
media/lawyer_photo/2026/05/{mediaId}/original.webp
```

Develop/release separation is done by `MEDIA_BUCKET`, not by adding `develop/` or `release/` prefixes to
the object key.

Complete a lower-level upload after the object exists in storage:

```http
POST /api/admin/media/{id}/complete-upload
```

```json
{
  "objectGeneration": "1700000000000000",
  "checksum": "optional-checksum",
  "width": 1200,
  "height": 1600
}
```

Editable media metadata is localized and saved one locale at a time:

```http
PUT /api/admin/media/{id}/translations/{locale}
```

```json
{
  "altText": "Updated localized alt",
  "titleText": "Updated localized title"
}
```

Use `cmsFields.photoMediaId` on lawyers to connect a lawyer to a media record. The backend validates that
`photoMediaId` points to an active uploaded media record with `usageType="lawyer_photo"`. If the media
record has an owner, it must be `ownerResource="lawyers"` with the same lawyer id; older ownerless
`lawyer_photo` assets remain accepted for compatibility.

### Lawyer Photo Picker Flow

For the first lawyer photo picker, use this practical flow:

1. Open existing photo choices:

```http
GET /api/admin/media?usageType=lawyer_photo&uploadState=uploaded&limit=50&offset=0
```

For a concrete lawyer editor, prefer the owner-scoped picker:

```http
GET /api/admin/media?usageType=lawyer_photo&ownerResource=lawyers&ownerId={lawyerId}&uploadState=uploaded&limit=50&offset=0
```

2. Show each choice using media metadata and an admin preview URL proxied by `cms-front`:

```text
cms-front browser route -> cms-front server handler -> GET /api/admin/media/{id}/file -> image bytes
```

3. Upload a new lawyer photo with:

```http
POST /api/admin/media/upload
Content-Type: multipart/form-data
```

Required fields for `usageType=lawyer_photo`:

- `file`;
- `usageType=lawyer_photo`;
- `ownerResource=lawyers`;
- `ownerId={lawyerId}`;
- `translations` JSON string with `altText` and `titleText` for `uk`, `ru`, and `en`.

4. After upload succeeds, attach the media record to the lawyer:

```http
PATCH /api/admin/reference/lawyers/{lawyerId}
```

```json
{
  "photoMediaId": "5d6f0f95-80b5-401e-9100-7f94fc5e04ce"
}
```

5. Re-read the lawyer detail:

```http
GET /api/admin/reference/lawyers/{lawyerId}
```

The detail response should now return `cmsFields.photoMediaId`. If the selected media is missing, deleted,
not uploaded, or not `usageType="lawyer_photo"`, backend rejects the PATCH. The frontend should show the
backend validation message and keep the editor's current form state.

Deletion is soft and guarded. `DELETE /api/admin/media/{id}` is rejected if the record is already referenced
by a lawyer photo or by a published page snapshot.

There is intentionally no separate `cms_media_usages` API in the current implementation. Media ownership is
stored on the media asset itself as a lightweight picker context, while actual public usage is still decided
by the owning object or section field. Deletion checks the implemented hard references plus published
snapshot payloads.

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
- media picker can list uploaded lawyer photos, upload a new `lawyer_photo`, preview it through the
  protected admin file endpoint/proxy, and save `photoMediaId` to a lawyer;
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
