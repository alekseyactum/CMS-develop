# ERP Reference Data And Runtime Read Models

This document fixes the first-release requirements for ERP-imported reference data and runtime/read-model
payloads in the clean CMS backend.

The term "runtime data" is allowed in product discussion, but the implementation should keep two clear
layers:

- `reference-data`: ERP-imported source objects stored in the CMS database;
- `runtime-resolvers`: backend logic that builds public read-model payloads from CMS database state.

The public frontend must not call ERP and must not decide whether ERP objects are eligible for rendering.

## Source Boundary

ERP is the source of truth for object identity and public eligibility.

CMS is the source of truth for CMS-owned public enrichment:

- localized public names and labels;
- localized descriptions or display text where required;
- media selected or managed inside CMS;
- CMS-owned sort order;
- generated read-only lawyer slugs;
- validation, preview, publish, snapshots, and diagnostics.

ERP-owned source fields are read-only from the CMS admin perspective. CMS must not edit source fields,
delete ERP-imported objects, or manually change the ERP-owned public eligibility flag.

The only ERP visibility field used by CMS public logic is:

```text
show_on_site
```

Services also have two ERP-owned classification flags:

```text
service_cond
legal_cond
```

`service_cond` means the service may appear in the public services list/tree.
`legal_cond` means the service may appear in the future legal classifier tree.
These flags are independent:

- search/seizure may be a criminal-law service but not a legal classifier item;
- drug lawyer may be a legal classifier item but not a sellable service;
- alimony lawyer may be both.

Other ERP fields such as `active` and `send_to_site` remain ERP-internal unless a later explicit
integration decision changes this rule.

## Upsert Direction And Access

ERP pushes normal changes to CMS one object at a time.

The first release uses three synchronization modes:

- event upsert: ERP notifies `data-inside-migrator` about concrete changed objects;
- event delete: ERP notifies `data-inside-migrator` that a concrete qualification relation was removed;
- scheduled reconciliation: Google Scheduler calls `data-inside-migrator` regularly, and the migrator
  decides which internal maintenance task is due.

Event upsert remains the primary path for normal reference objects. Scheduled reconciliation is required
for qualification/link tables because they can disappear from ERP without a reliable single-row "delete"
event, but it is a safety net, not a replacement for delete events.

ERP -> CMS reference-data endpoints must be private service-to-service endpoints:

- only ERP backend calls them;
- access is IAM/service-account based between Cloud Run services;
- shared API keys and IP allowlists are not the primary security mechanism;
- CMS admin does not imitate ERP source updates in production.

The current implemented integration shape is:

```http
POST /internal/migrations/cms.reference-data/run
```

ERP backend sends only the sync intent:

```json
{
  "mode": "upsert",
  "objectType": "practice",
  "externalIds": [15, 18, 21]
}
```

For deleted qualification relations, ERP sends:

```json
{
  "mode": "delete",
  "objectType": "lawyerQualification",
  "externalIds": [1001]
}
```

or:

```json
{
  "mode": "delete",
  "objectType": "regionQualification",
  "externalIds": [2001]
}
```

`delete` is supported only for qualification relation objects. Normal dictionaries are not deleted from
CMS by event; ERP must send a normal `upsert` with `show_on_site=false` when a normal object should no
longer be public.

Then `data-inside-migrator` reads the ERP source database, normalizes the payload and calls protected
`cms-back` internal endpoints:

```text
/api/internal/erp/reference/practices/upsert
/api/internal/erp/reference/services/upsert
/api/internal/erp/reference/problems/upsert
/api/internal/erp/reference/regions/upsert
/api/internal/erp/reference/offices/upsert
/api/internal/erp/reference/lawyers/upsert
/api/internal/erp/reference/reviews/upsert
/api/internal/erp/reference/lawyer-qualifications/upsert
/api/internal/erp/reference/region-qualifications/upsert
/api/internal/erp/reference/lawyer-qualifications/deactivate
/api/internal/erp/reference/region-qualifications/deactivate
/api/internal/erp/reference/lawyer-qualifications/full-sync
/api/internal/erp/reference/region-qualifications/full-sync
```

ERP must not call `cms-back` directly for this flow.

The migrator response is considered successful only when the result body has `status="ok"`.
If at least one requested object was not migrated, the migrator must return a non-2xx HTTP status with
the full result payload. ERP callers must check both HTTP status and the returned per-item statuses.

This prevents false-positive cases where ERP receives an HTTP 200 even though an object such as an office
was skipped or failed during CMS import.

The scheduled entrypoint is separate from ERP event upserts:

```http
POST /internal/scheduled/run
```

Initial scheduler behavior:

- Google Scheduler may call this endpoint every 5 minutes;
- the migrator checks current `Europe/Kiev` time;
- the first scheduled task runs only inside the 02:00-02:04 Kyiv window;
- all other calls are ignored with `status="ignored"`;
- manual/operator calls may use `force=true` for the same task.

Initial scheduled task:

```text
cms-reference-qualifications-full-sync
```

This task reads complete ERP snapshots for lawyer and region qualifications, sends them to `cms-back`
full-sync endpoints, and deactivates CMS qualification rows that are no longer present in the ERP snapshot.
It does not delete rows.

Develop runtime state:

- Cloud Scheduler job: `data-inside-migrator-develop-scheduled-run-5m`;
- schedule: `*/5 * * * *`, `Europe/Kiev`;
- target: `POST /internal/scheduled/run` on `data-inside-migrator-develop`;
- OIDC service account: `data-migrator-dev-scheduler@composite-ally-360719.iam.gserviceaccount.com`;
- request body: `{"task":"cms-reference-qualifications-full-sync"}`;
- the job currently points to develop and must be switched/recreated for release only after the release
  migrator and release CMS backend are ready.

## Storage Rules

Each ERP-imported object has:

- an internal CMS id;
- `external_id` from ERP;
- `source`, initially `actumdata`;
- normalized source fields from the approved contract;
- CMS-owned fields where needed.

Do not use ERP ids as primary CMS ids.

The source uniqueness rule is:

```text
source + external_id
```

inside each typed reference table.

For normal reference objects, if ERP stops sending an object, CMS does not auto-delete it and does not
auto-disable it. The last known `show_on_site` value remains authoritative until ERP sends a new value.

Qualification rows are the exception because they are relation facts, not dictionaries. Full-sync
reconciliation and explicit ERP delete events may mark a qualification row as inactive:

```text
is_active = false
removed_from_source_at = full sync timestamp
```

The historical row remains in CMS for diagnostics and audit-like visibility.

The first release stores only the current normalized source state. It does not store raw payloads and does
not keep a full source-change history inside CMS. ERP remains the source history for ERP-owned fields.

## Translation Skeletons

ERP and `data-inside-migrator` do not create CMS-owned localized fields.

For every translatable reference object, `cms-back` must guarantee that admin list and detail responses contain
translation rows for all supported locales:

```text
uk
ru
en
```

This guarantee is enforced from two sides:

- on first insert of a translatable ERP object, CMS creates missing translation skeleton rows;
- on admin list/detail read, CMS checks the translation rows again and creates any missing locale rows before
  returning the object to the CMS frontend.

The operation is idempotent. Existing translation rows are never overwritten by ERP upsert, skeleton
creation, or admin detail read.

Initial skeleton values:

- for `uk`, CMS may copy safe source text such as `source_name`, `source_shortname`, `source_address`, or
  original review text into the matching localized field;
- for `ru` and `en`, localized CMS-owned fields start empty;
- editors then fill or correct localized fields through the CMS admin translation API.

Qualification tables do not have translation skeletons.

## Validation Boundary

`show_on_site=true` means the object may be used on the public site.

It does not guarantee that a section or page using the object can be published.

CMS validation remains responsible for checking whether the concrete section/page has all required public
data for its locale, schema, and payload contract.

Example:

```text
lawyer.show_on_site = true
lawyer public_name for en is missing
lawyers_page en requires public_name
```

Result:

```text
the lawyer object is not disabled by CMS
the section/page publish fails validation
```

Validation happens for the concrete section/page where the object is used, not globally for every object
in the database.

Draft preview may expose incomplete data with diagnostics. Publish preview and publish must use strict
publish validation.

## CMS Admin Reference API

CMS frontend works with reference data through admin endpoints, not through ERP upsert endpoints:

```text
GET   /api/admin/reference/meta
GET   /api/admin/reference/{resource}
GET   /api/admin/reference/{resource}/{id}
PATCH /api/admin/reference/{resource}/{id}
PUT   /api/admin/reference/{resource}/{id}/translations/{locale}
```

`GET /api/admin/reference/meta` is the backend-owned contract for the CMS frontend. It returns supported
resources, locales, list filters, editable CMS fields, required fields, localized fields, and whether the
resource has `show_on_site` and CMS editor audit tracking.

The CMS frontend should not hardcode the editable/required/reference field shape when the backend can
provide it from the same configuration used by validation and persistence.

Supported resources:

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

The response must preserve ownership separation:

- `sourceFields`: ERP-owned read-only source fields;
- `cmsFields`: CMS-owned fields such as media ids, sort order, and read-only generated lawyer `slug`;
- `relationFields`: external and resolved relation ids;
- `translations`: CMS-owned localized fields for `uk`, `ru`, `en`;
- `relations`: readable linked objects for single-object relations such as lawyer region/office;
- `children`: readable dependent object lists for parent dictionaries;
- `diagnostics`: current validation hints for the CMS frontend.
- `updatedBy` / `updatedAt`: the last non-translation CMS base-field edit for normal reference resources;
- `translationsMeta`: per-locale translation audit plus latest translation editor/date.

`children` is intentionally separate from `relations`.

`relations` answers "which single object is this record linked to?".
Example: a lawyer has one resolved region and one resolved office.

`children` answers "which dependent records belong under this object?".
The first supported dependency lists are:

```text
practices.children.services
services.children.problems
```

The dependency lists must include enough read-only source/CMS/translation data for the CMS frontend to
display practice -> services and service -> problems trees without additional requests for every child.

PATCH can edit only CMS-owned fields for that resource. Translation PUT can edit only the localized fields
defined for that resource. Qualification resources are read-only in CMS because relation and score values
remain ERP-owned.

Normal dictionary resources must track the last CMS editor separately from ERP/source sync metadata.
The implementation should use a CMS-specific audit field such as `cms_updated_by`, not the generic
source/update marker that may be touched by `data-inside-migrator`.

Admin API `updatedAt` / `updatedBy` for normal dictionaries reflects only non-translation CMS-owned base
field edits. Translation edits are reported separately in `translationsMeta`.

## Source Slugs And Redirects

ERP provides source slugs for practices, services, problems, and regions. CMS stores them as read-only
source data in `source_slug`.

For these dictionaries there is no separate CMS-owned `public_slug`. The public route slug is the ERP
source slug, shared across all locales. If a visible routable object has no source slug, diagnostics must
return a critical error.

Lawyers are the exception: ERP does not provide lawyer slugs. CMS generates one stable read-only `slug`
when the lawyer record is first created in the CMS database. That slug is not editable and must not be
regenerated when the lawyer name changes.

Example:

```text
lawyer.slug = ivan-ivanov
/advokaty/ivan-ivanov
/ru/advokaty/ivan-ivanov
/en/advokaty/ivan-ivanov
```

If an ERP source slug changes or a generated lawyer slug ever changes through a controlled maintenance
operation, CMS must create redirects from old public URLs to the new public URLs for all affected locale
routes. Normal editor UI must not edit these slugs.

## Snapshot And Stale Policy

Published page snapshots store:

- the complete public payload needed by the frontend;
- dependency refs for ERP/CMS reference objects that were actually used in the payload.

Runtime/read-model data is therefore resolved by backend before snapshot activation. The frontend still
receives a complete public payload.

When ERP updates a reference object, CMS:

- updates the typed reference table;
- finds pages whose current published snapshot explicitly references that object;
- marks those pages stale / needs republish;
- does not automatically replace the current published snapshot.

Republish after ERP/source changes is manual in the first release.

Future dependency-index logic may detect pages that could be affected by resolver filters even when the
object was not present in the current snapshot, but the first release uses explicit snapshot dependency
refs only.

## Table Shape Direction

Use typed tables, not one universal JSON table.

Reference tables use the `cms_ref_` prefix:

```text
cms_ref_practices
cms_ref_services
cms_ref_problems
cms_ref_regions
cms_ref_offices
cms_ref_lawyers
cms_ref_reviews
cms_ref_lawyer_qualifications
cms_ref_region_qualifications
```

Translations are also typed:

```text
cms_ref_practice_translations
cms_ref_service_translations
cms_ref_problem_translations
cms_ref_region_translations
cms_ref_office_translations
cms_ref_lawyer_translations
cms_ref_review_translations
```

Qualification tables do not have translations.

Typed tables are preferred because they keep SQL readable, allow normal constraints, and avoid hiding
different object shapes in a universal JSON column.

If an upsert references a related object that has not been imported yet, CMS accepts the upsert and keeps
the external relation unresolved until the related object exists. Public validation must block payloads
that require a resolved relation.

## Object Contracts

### Practices

ERP/source fields:

```text
external_id
name
shortname
slug
color
show_on_site
```

CMS-owned base fields:

```text
sort_order
```

Translations:

```text
locale
public_name
menu_title
```

### Services

ERP/source fields:

```text
external_id
practice_external_id
name
shortname
slug
color
show_on_site
service_cond
legal_cond
```

CMS-owned base fields:

```text
sort_order
```

Translations:

```text
locale
public_name
menu_title
```

`service_cond` and `legal_cond` are not editable in CMS. They are read-only ERP source flags. Runtime
resolvers must use them when building normal service pages/lists and the future legal classifier.

Recommended ERP DB rollout defaults:

```sql
ALTER TABLE `actumdata`.`services`
  ADD COLUMN `service_cond` TINYINT(1) NOT NULL DEFAULT 1 AFTER `show_on_site`,
  ADD COLUMN `legal_cond` TINYINT(1) NOT NULL DEFAULT 0 AFTER `service_cond`;
```

After adding the fields, ERP must explicitly mark exceptions:

- `service_cond = 1`, `legal_cond = 0`: service only;
- `service_cond = 0`, `legal_cond = 1`: legal classifier only;
- `service_cond = 1`, `legal_cond = 1`: both;
- `service_cond = 0`, `legal_cond = 0`: neither public service list nor legal classifier.

### Problems

ERP/source fields:

```text
external_id
practice_external_id
service_external_id
name
shortname
slug
color
show_on_site
```

CMS must validate that the referenced service belongs to the referenced practice when both references are
resolved.

CMS-owned base fields:

```text
sort_order
```

Translations:

```text
locale
public_name
menu_title
```

### Regions

ERP/source fields:

```text
external_id
name
shortname
slug
color
show_on_site
```

CMS-owned base fields:

```text
sort_order
```

Translations:

```text
locale
public_name
menu_title
prepositional_name
```

`prepositional_name` stores the localized regional name in prepositional form. It is CMS-owned and must be
edited per locale.

### Offices

ERP/source fields:

```text
external_id
region_external_id
name
address
map_url
google_place_id
show_on_site
```

CMS-owned base fields:

```text
sort_order
```

Translations:

```text
locale
address
```

Offices do not have public slugs in the first release.

### Lawyers

ERP/source fields:

```text
external_id
name
region_external_id
office_external_id
license
show_on_site
```

Each lawyer has one primary region in the first release.

CMS-owned base fields:

```text
slug
photo
sort_order
```

`slug` is generated by CMS backend on first insert, is returned as read-only API data, and is not
regenerated on later lawyer name changes.

Translations:

```text
locale
public_name
description
```

### Reviews

ERP/source fields:

```text
external_id
author_name
text
photo_url
author_url
rating
is_real
office_external_id
practice_external_id
service_external_id
lawyer_external_id
published_at
show_on_site
```

`show_on_site` maps from ERP review visibility.

Reviews do not have CMS-owned `sort_order` in the first release. Review ordering is resolver/policy
logic, not manual ordering.

Translations:

```text
locale
display_text
```

The original ERP review text remains unchanged. `display_text` is the CMS-owned localized public version.

### Lawyer Qualifications

Lawyer qualifications are not dictionaries. They are ranking signals.

ERP/source fields:

```text
external_id
lawyer_external_id
practice_external_id
service_external_id
score
```

There is no `show_on_site` for a qualification row. Public use depends on:

- `is_active = true`;
- required related objects being present/resolved;
- related objects being eligible for the public site;
- the score policy.

Score policy:

```text
score = null -> do not use
score <= 1 -> do not use
score > 1 -> may be used for selection/ranking
```

### Region Qualifications

Region qualifications are also ranking/availability signals, not dictionaries.

They do not include a lawyer, service, problem, or score in the first release. They are facts that a
region has a competency for a practice.

ERP/source fields:

```text
external_id
region_external_id
practice_external_id
is_active
removed_from_source_at
```

There is no `show_on_site` for a region qualification row. Public use depends on `is_active = true` and
on the referenced region/practice being present, resolved, and public-eligible.

## First Implementation Order

The backend should implement this layer in phases:

1. Create the complete typed database model for all reference-data objects in the first release scope.
2. Add private ERP upsert APIs per object type.
3. Add CMS-owned editing and validation for translations, media, sort order, and generated lawyer slugs.
4. Add runtime resolvers and connect them to page schemas.

The full table foundation should be designed up front, but runtime use can be connected page type by page
type.

## Media Records

CMS media is stored as metadata records in the CMS database. File bytes are not stored in MySQL.

The first backend implementation creates `cms_media_assets` and admin endpoints:

```text
GET    /api/admin/media/meta
GET    /api/admin/media
GET    /api/admin/media/{id}
POST   /api/admin/media/upload
POST   /api/admin/media
POST   /api/admin/media/{id}/complete-upload
PUT    /api/admin/media/{id}/translations/{locale}
DELETE /api/admin/media/{id}
```

The normal admin upload path is `POST /api/admin/media/upload`. The CMS frontend sends multipart form data
to `cms-back`; `cms-back` validates the request, creates the metadata record, generates the object key,
uploads the bytes to Cloud Storage with its service account, and marks the record `uploaded`.

The lower-level `POST /api/admin/media` and `POST /api/admin/media/{id}/complete-upload` endpoints remain
available for internal/advanced flows that need to reserve a record before upload. They still must use the
backend-created record and must not bypass `cms-back` ownership of media identity and metadata.

The bucket may remain private. Public rendering must use the stable serving path or a later media-serving
layer, not a raw public Cloud Storage URL.

Environment isolation is done with separate buckets, not with `develop/` and `release/` folders inside one
bucket. Develop uses `MEDIA_BUCKET=site-media-develop`; future release must use its own bucket such as
`site-media-release`. Object keys stay neutral:

```text
media/{usageType}/{year}/{month}/{mediaId}/{filename}
```

Media records include:

- stable `media_id`;
- usage type;
- lifecycle state;
- upload state;
- storage provider and bucket;
- backend-generated object key;
- stable serving path;
- original filename;
- MIME type;
- size in bytes;
- checksum and object generation when available;
- dimensions when available;
- CMS editor audit fields.

Localized media metadata is stored separately in `cms_media_asset_translations`:

- `media_id`;
- `locale`;
- `alt_text`;
- `title_text`;
- last translation editor and timestamp.

Initial usage types:

```text
lawyer_photo
article_cover
og_image
license_document
generic
```

Public image usage types require `alt_text` and `title_text`. Size and MIME limits are owned by the backend
and exposed through `GET /api/admin/media/meta`. Public image usage types require these fields for every
supported locale.

Reference-data integration:

- lawyer `cmsFields.photoMediaId` must reference an active uploaded `lawyer_photo` media record;
- the backend rejects missing, deleted, pending-upload, or wrong-usage media ids;
- media deletion is soft;
- deletion is blocked when a record is referenced by a lawyer photo or by a published page snapshot.

The first release does not introduce a universal `cms_media_usages` table. Media ownership remains in the
field that references the media asset, for example lawyer `photo_media_id` or a section payload field.
Deletion/readiness checks must inspect the implemented owner fields and published snapshots. A separate
usage index can be added later only if real cross-object media reporting needs it.

This gives the CMS frontend a stable media identifier before the richer media-library UI is implemented.
