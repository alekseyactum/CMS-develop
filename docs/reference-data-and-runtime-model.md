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

- public slugs;
- localized public names and labels;
- localized descriptions or display text where required;
- media selected or managed inside CMS;
- CMS-owned sort order;
- validation, preview, publish, snapshots, and diagnostics.

ERP-owned source fields are read-only from the CMS admin perspective. CMS must not edit source fields,
delete ERP-imported objects, or manually change the ERP-owned public eligibility flag.

The only ERP visibility field used by CMS public logic is:

```text
show_on_site
```

Other ERP fields such as `active` and `send_to_site` remain ERP-internal unless a later explicit
integration decision changes this rule.

## Upsert Direction And Access

ERP pushes changes to CMS one object at a time.

The first release does not require full batch sync as the primary integration path.

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
```

ERP must not call `cms-back` directly for this flow.

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

If ERP stops sending an object, CMS does not auto-delete it and does not auto-disable it. The last known
`show_on_site` value remains authoritative until ERP sends a new value.

The first release stores only the current normalized source state. It does not store raw payloads and does
not keep a full source-change history inside CMS. ERP remains the source history for ERP-owned fields.

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
GET   /api/admin/reference/{resource}
GET   /api/admin/reference/{resource}/{id}
PATCH /api/admin/reference/{resource}/{id}
PUT   /api/admin/reference/{resource}/{id}/translations/{locale}
```

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
- `cmsFields`: CMS-owned editable fields such as public slugs, media ids and sort order;
- `relationFields`: external and resolved relation ids;
- `translations`: CMS-owned localized fields for `uk`, `ru`, `en`;
- `diagnostics`: current validation hints for the CMS frontend.

PATCH can edit only CMS-owned fields for that resource. Translation PUT can edit only the localized fields
defined for that resource. Qualification resources are read-only in CMS because relation and score values
remain ERP-owned.

## Public Slugs And Redirects

ERP may provide source slugs for practices, services, problems, and regions. CMS stores them as source
data only.

Public slugs are CMS-owned and are not automatically changed when ERP changes a source slug or name.

Public slug rules:

- `public_slug` is shared across locales;
- one object has one canonical public slug;
- uniqueness is checked within the object type;
- translations localize display text, not the slug.

Example:

```text
lawyer.public_slug = ivan-ivanov
/advokaty/ivan-ivanov
/ru/advokaty/ivan-ivanov
/en/advokaty/ivan-ivanov
```

When CMS changes a public slug/public route, CMS must create redirects from old public URLs to the new
public URLs for all affected locale routes.

ERP source slug changes must not create public redirects by themselves because they must not change the
public URL.

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
public_slug
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
```

CMS-owned base fields:

```text
public_slug
sort_order
```

Translations:

```text
locale
public_name
menu_title
```

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
public_slug
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
public_slug
sort_order
```

Translations:

```text
locale
public_name
menu_title
```

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

Offices do not require public slugs in the first release.

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
public_slug
photo
sort_order
```

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

There is no `show_on_site` for a qualification row. Public use depends on the related objects and the
score policy.

Score policy:

```text
score = null -> do not use
score <= 1 -> do not use
score > 1 -> may be used for selection/ranking
```

### Region Qualifications

Region qualifications are also ranking/availability signals, not dictionaries.

They do not include a lawyer and they do not include problems in the first release.

ERP/source fields:

```text
external_id
region_external_id
practice_external_id nullable
service_external_id nullable
score
```

Supported levels:

```text
region + practice + score
region + service + score
```

Score policy:

```text
score = null -> do not use
score <= 1 -> do not use
score > 1 -> may be used for selection/ranking
```

## First Implementation Order

The backend should implement this layer in phases:

1. Create the complete typed database model for all reference-data objects in the first release scope.
2. Add private ERP upsert APIs per object type.
3. Add CMS-owned editing and validation for translations, slugs, media, and sort order.
4. Add runtime resolvers and connect them to page schemas.

The full table foundation should be designed up front, but runtime use can be connected page type by page
type.
