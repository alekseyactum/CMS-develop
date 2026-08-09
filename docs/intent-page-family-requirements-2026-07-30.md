# Search Intent Page Families - Product And Backend Requirements - 2026-07-30

## Status

This document records the requirements accepted during the search-intent page discussion.

The CMS navigation and source-scoped workbench contract was revised on 2026-08-09. The revised contract
supersedes the earlier lazy virtual-group and one-family-at-a-time workbench design.

The product requirements review is complete. This is a normative product and backend contract, not an
implementation-status report. The intent JSON-LD templates now use the accepted organization, regional
provider, shared `Service`, and `Offer` rules in `docs/json-ld-architecture-2026-07-27.md` together with the
payload and page-matrix contract in `docs/json-ld-implementation-requirements-2026-08-03.md`.

Search-intent pages must use the existing CMS page lifecycle. They are not a second page engine and must not
be implemented as an independent SEO landing-page subsystem.

All intent families use one generic CMS page type:

```text
intent_page
```

The source binding, not a separate page type, identifies whether the family originated from a practice
collection, practice, service, or problem.

## Goal

The service hierarchy is primarily organized for hierarchical user navigation:

```text
practice collection -> practice -> service -> problem
```

Important search intents do not always fit naturally into that hierarchy. Examples include:

- lawyer in Kyiv;
- attorney in Kyiv;
- legal services in Kyiv;
- online lawyer consultation;
- lawyer consultation.

Trying to optimize one hierarchy page equally for several materially different intents produces unclear
titles, weak content focus, and search cannibalization. The CMS therefore needs controlled alternative
intent pages derived from existing service-hierarchy pages.

The feature must support focused pages without producing disconnected, automatically published, low-value
doorway pages.

## Eligible Source Pages

An intent family may be created from the base Ukrainian, non-regional variant of:

- `practice_collection_page`;
- `practice_page`;
- `service_page`;
- `problem_page`.

An intent page cannot be the source of another intent family.

One source line may own more than one intent family. For example, one service may have separate families for
"lawyer consultation" and "online lawyer consultation".

The create action is available only when:

- the current page is the base Ukrainian non-regional source;
- its page type is eligible;
- the source authoring aggregate exists and is not archived;
- the current page is not itself an intent page.

The base Ukrainian page is the creation root, not the only page related to the intent family.

## Core Domain Model

### `IntentPageFamily`

`IntentPageFamily` identifies one search intent across locales and regions.

Conceptually it contains:

```json
{
  "id": "intent-family-id",
  "sourceRootPageId": "base-ua-non-regional-source-page-id",
  "slug": "advokat-po-alimentam",
  "internalTitle": "Адвокат по аліментах",
  "status": "active"
}
```

`sourceRootPageId` is immutable. It identifies the service-hierarchy line from which the intent was
created and prevents the same family from being independently recreated from a regional or translated
source variant.

The family uses the same route slug across locales. Locale prefixes and public paths follow the ordinary
site route contract; intent pages do not introduce an independent localized-slug subsystem.

The family remains a domain object rather than being identical to a page record. In the CMS, however, its
visual anchor is the national intent page:

- the national intent is the family header/primary row for the selected locale;
- regional intent pages are displayed as that national page's variants;
- the base Ukrainian national intent is the stable creation and identity root;
- family-level counters aggregate the national and all regional/localized variants;
- if the national page authoring state is damaged or missing, the family remains visible under its
  `internalTitle` and exposes repair diagnostics instead of disappearing.

The exact storage table and field names remain an implementation detail.

### Concrete variant binding

Family-level provenance is insufficient for navigation and publication.

Every concrete intent page must also be bound to the matching concrete source page:

```json
{
  "familyId": "intent-family-id",
  "intentPageId": "intent-page-kyiv-uk",
  "sourceVariantPageId": "source-page-kyiv-uk",
  "locale": "uk",
  "regionId": "kyiv"
}
```

The matching rule is:

```text
intent locale == source locale
intent region == source region
intent hierarchy lineage == family source lineage
```

Examples:

```text
Ukraine / UK intent <-> Ukraine / UK source
Kyiv / UK intent    <-> Kyiv / UK source
Kyiv / RU intent    <-> Kyiv / RU source
Kharkiv / EN intent <-> Kharkiv / EN source
```

The backend creates and maintains this binding. An editor must not manually select an arbitrary source
variant.

Recommended invariants:

- one intent page belongs to exactly one intent family;
- one intent page points to exactly one matching source variant;
- one family has at most one intent variant for each `(locale, region)` pair;
- a source variant may be linked to several different intent families;
- a regional intent must not silently fall back to the national source;
- a translated intent must not silently fall back to another locale.

The relation must be queryable in both directions:

```text
source variant -> matching intent variants
intent variant -> matching source variant
```

## Creation And Reconciliation

Creation uses the normal CMS plan-and-execute workflow.

Suggested API surface:

```text
POST /api/admin/page-workbench/pages/:sourcePageId/intent-families/plan
POST /api/admin/page-workbench/pages/:sourcePageId/intent-families

POST /api/admin/intent-page-families/:familyId/reconcile-regions/plan
POST /api/admin/intent-page-families/:familyId/reconcile-regions
```

Eligible source rows should advertise their actual endpoints through the workbench contract. The frontend
must not construct endpoint paths from page type assumptions.

Planning must use the existing CMS operation vocabulary where applicable:

```text
will_create
will_repair
already_exists
blocked
```

Execution must be idempotent. Retrying an operation must not create a second family or duplicate variants.

Initial creation input must include at least:

```json
{
  "slug": "advokat-po-alimentam",
  "internalTitle": "Адвокат по аліментах",
  "introTitle": "Адвокат по аліментах",
  "regionalIntroTitleTemplate": "Адвокат по аліментах {regionPrepositional}"
}
```

The backend builds the full route from the source route and validates route conflicts. The slug is immutable
in the first version.

Illustrative routes:

```text
/services/advokat
/kyiv/services/advokat

/services/family/alimony/advokat-po-alimentam
/kyiv/services/family/alimony/advokat-po-alimentam
```

Intent pages are created as drafts. Creation and reconciliation never publish them automatically.

## Locale And Route Behavior

Intent pages use the same localization model as other generated site pages:

- supported locales are `uk`, `ru`, and `en`;
- every locale/region combination is a separate CMS page, authoring state, validation state, and snapshot;
- the workbench exposes the normal locale tabs and all-locale diagnostics;
- Ukrainian public paths have no locale prefix;
- Russian and English public paths use the existing `/ru` and `/en` prefixes;
- locale switching uses backend-provided exact page URLs;
- no locale falls back to another locale's editable content or published snapshot;
- the primary Ukrainian publication gate remains in force.

The family slug follows the same immutability and route-building rules as existing generated page slugs.
Creating, opening, repairing, and diagnosing a localized intent variant must reuse the normal page
workbench/bootstrap behavior rather than a separate "intent translation" workflow.

## Initial Page Structure

Intent pages use ordinary CMS sections, validation, preview, snapshots, rollback, and repair.

The initial structure is:

1. SEO;
2. intent intro;
3. global achievements;
4. intent introductory text;
5. FAQ content with related intent/source navigation;
6. the existing lead block/form composition;
7. `regional_links` regional alternatives on the national variant;
8. `local_offices` physical offices on regional variants.

The implementation should reuse established section contracts where their semantics are already correct.
It must not duplicate lead-form or achievement schemas only because the page type is new.

Page-owned editable content is independent for every intent page:

- the national intent and every regional intent are separate drafts;
- changing the national intent does not rewrite regional drafts or snapshots;
- changing one regional intent does not rewrite another region;
- creation may initialize titles and empty/minimal section drafts from deterministic templates, but this
  is one-time initialization rather than live content inheritance.

Standard shared/typical sections keep their existing CMS source policies. For example, global achievements,
lead-form content, and other genuinely shared sections continue to use the same inheritance/override
behavior as they do on current generated page types. This shared-section behavior does not turn
page-owned intent copy into inherited content.

The following future sections should be possible without changing the family model:

- related services;
- lawyers;
- cases;
- reviews.

Their inclusion in the first implementation is not yet required.

## System Relationships And Visible Links

The source/intent relation is domain data. Editable FAQ content is not its source of truth.

The CMS exposes a runtime/read-only navigation model adjacent to the FAQ content.

On a source page:

```json
{
  "kind": "intent_navigation",
  "direction": "to_intents",
  "items": [
    {
      "familyId": "intent-family-id",
      "pageId": "matching-published-intent-page-id",
      "title": "Адвокат по аліментах у Києві",
      "href": "/kyiv/services/family/alimony/advokat-po-alimentam"
    }
  ]
}
```

On an intent page:

```json
{
  "kind": "intent_navigation",
  "direction": "to_source",
  "source": {
    "pageId": "matching-published-source-page-id",
    "title": "Аліменти",
    "href": "/kyiv/services/family/alimony"
  }
}
```

Public link resolution is always locale- and region-exact:

- national source -> national intent in the same locale;
- regional source -> regional intent in the same locale and region;
- regional intent -> regional source in the same locale and region.

Only published targets enter a public snapshot. Draft targets remain visible in CMS diagnostics but do not
produce broken public links.

If one source variant has several published intent pages, all of them must remain available through its
system navigation. Editorial control is limited to presentation:

- `sortOrder` controls their order;
- `featured` marks one or more links for more prominent presentation;
- the localized intent H1 is the default anchor label;
- an optional localized `navigationTitle` may provide a shorter label;
- neither `featured` nor ordering may remove the last crawlable link to a published intent.

The public frontend may render this navigation in or immediately after the FAQ visual block. Disabling the
editable FAQ section must not disable the system relationship navigation; otherwise important pages can
become orphaned.

Contextual typed links inside individual FAQ answers are not part of V1. The first implementation contains
only the mandatory runtime navigation block.

A future version may add structured references such as:

```json
{
  "question": "Коли потрібен адвокат?",
  "answer": "...",
  "links": [
    {
      "targetKind": "intent_family",
      "targetId": "intent-family-id",
      "label": "Адвокат по аліментах"
    }
  ]
}
```

If introduced later, typed references will be resolved by the backend to the published target for the
current locale and region. Raw editor-managed URLs must not become the system relationship mechanism.

## Publication And Snapshot Dependencies

The existing snapshot-first rule applies:

- preview is assembled from the resolved preview payload;
- publication stores all resolved navigation and structured data in an immutable snapshot;
- published snapshots do not mutate when a related page is later published or unpublished.

Publication prerequisites:

- the base Ukrainian non-regional source must have a current published snapshot;
- an intent variant requires its exact matching source variant to be published;
- non-primary intent variants remain subject to the normal primary Ukrainian publication gate;
- a regional intent requires the national intent of the same locale to have a current published snapshot;
- missing or ambiguous variant binding blocks preview/publication with an explicit diagnostic.

The family publication order is therefore:

```text
UK national intent -> UK regional intents
RU national intent -> RU regional intents
EN national intent -> EN regional intents
```

The base Ukrainian national intent remains the primary family publication prerequisite across locales.

Publishing or unpublishing an intent changes the set of reverse links expected on its source page. The
backend must mark the matching source variant stale with a diagnostic such as:

```text
INTENT_LINKS_CHANGED
```

The source page remains published with its previous immutable snapshot and is republished explicitly to
update its reverse links. Publishing the intent must not silently republish or rewrite the source.

Publishing or unpublishing a regional intent also changes the regional-alternatives list expected in the
matching national intent page for that locale. The backend therefore marks that national intent page stale
as well. It is republished separately.

Consequently, a regional intent publication may produce two explicit stale dependencies:

```text
matching regional source variant -> INTENT_LINKS_CHANGED
matching national intent variant -> INTENT_REGIONAL_LINKS_CHANGED
```

`stale` does not mean unpublished. It means that the currently served snapshot remains valid but does not
yet contain the newly expected runtime links.

Unpublishing a national intent while published regional or localized dependants still require it must not
silently break them. The backend must either block the isolated operation or return an explicit impact plan
that includes the dependant unpublish operations.

## New Regions And Changed Applicability

Intent regional variants participate in the normal service-hierarchy region lifecycle.

Reconciliation is triggered when:

- a region is created;
- a region becomes visible on the site;
- the corresponding source hierarchy becomes applicable in the region;
- a previously disabled or archived applicable region is restored.

A regional intent draft is created only when a matching regional source variant exists and the source
line is applicable to that region. The source may still be unpublished: this does not prevent intent
authoring preparation, but it continues to block intent publication.

Intent-family creation and reconciliation must not bootstrap a missing regional source page as a side
effect. When the source page is missing:

- the expected intent row remains visible as blocked;
- diagnostics identify the missing exact source variant;
- no orphan intent page is created;
- after the source page is created through the normal service-hierarchy workflow, reconciliation creates
  the missing intent draft.

Reconciliation must:

- be idempotent;
- create missing drafts;
- repair incomplete bindings or authoring aggregates through the normal repair workflow;
- never overwrite existing editor content;
- never publish automatically;
- report blocked variants instead of silently omitting them.

If a region or source line later becomes inapplicable, published intent pages are not silently deleted.
They receive an explicit diagnostic and an unpublish/archive plan.

## CMS Navigation And Workbench

Intent pages must not be mixed with ordinary practice/service/problem children. They are alternative landing
pages, not another hierarchy level.

Intent pages do not create separate nodes or virtual intent groups in the hierarchical CMS menu. They are
displayed inside the ordinary source-scoped matrix of the practice collection, practice, service, or problem
whose search alternatives they represent.

The ordinary source rows remain Ukraine and the applicable regions. Each source row can be expanded to show
the concrete intent variants for the same locale and geographic scope. In the collapsed state the source row
shows the backend-calculated aggregate state of those variants. In the expanded state each existing intent
variant is rendered as an ordinary page row with its own section cells, actions, diagnostics, and endpoints.

`child` is only a presentation and diagnostic-roll-up concept here. An intent page is not:

- a child in the service hierarchy;
- a content-inheritance child of the source page;
- part of the source page's own publish readiness;
- a reason to block source publication merely because the intent draft itself is invalid.

### Source-scoped read model

One source-scoped matrix request must return the complete ordinary matrix and its complete intent workbench
read model. The frontend must not fetch and merge one response per family. The initial contract deliberately
returns full ordinary `PageWorkbenchRow` values for all existing intent variants; a summary-only or lazy-row
mode is not part of the accepted first implementation. Backend implementation must nevertheless resolve the
rows in batches and must not implement the contract as an unbounded sequence of heavyweight per-row matrix
queries.

Illustrative response shape:

```json
{
  "rows": ["ordinary source rows"],
  "intentWorkbench": {
    "columns": ["intent page columns"],
    "summary": {
      "families": 2,
      "expectedVariants": 10,
      "existingVariants": 8,
      "publishedVariants": 3,
      "staleVariants": 1,
      "blockedVariants": 2,
      "errors": 4,
      "warnings": 5
    },
    "localeDiagnostics": [],
    "regions": [
      {
        "scope": { "kind": "national" },
        "title": "Україна",
        "summary": {
          "families": 2,
          "expectedVariants": 2,
          "existingVariants": 2,
          "publishedVariants": 2,
          "errors": 1,
          "warnings": 2
        },
        "items": []
      },
      {
        "scope": { "kind": "region", "regionId": "kyiv-id" },
        "regionSlug": "kyiv",
        "title": "Київ",
        "summary": {
          "families": 2,
          "expectedVariants": 2,
          "existingVariants": 1,
          "publishedVariants": 1,
          "errors": 1,
          "warnings": 0
        },
        "items": []
      }
    ]
  }
}
```

National scope must be represented explicitly as `{ "kind": "national" }`. It must not be inferred only
from a nullable region id. Regional scope must be represented as `{ "kind": "region", "regionId": "..." }`.
Titles and slugs are presentation and routing data, not relationship identity.

Every `items[]` entry must include at least:

- a stable item key;
- `familyId` and the family display/presentation data;
- the exact source-variant binding;
- the provisioning operation and expected/missing/repair state;
- a full ordinary `PageWorkbenchRow`, or `null` when the expected variant does not yet exist;
- page diagnostics and the non-blocking intent roll-up;
- standard backend-provided page and section endpoints;
- family-level endpoints for reconcile and presentation.

All intent variants continue to reuse the ordinary page workbench lifecycle: editor, draft, validation,
preview, publish, history, rollback, and locale switching. Family-level creation, region reconciliation,
ordering, `featured`, localized short navigation titles, and future archive/restore remain family actions and
must not be reimplemented as page actions. Each intent row therefore retains its `familyId` and an explicit
action for opening or configuring that family.

### Diagnostics and roll-up

The backend owns all diagnostic aggregation. The frontend only renders the returned counters and must not
sum family responses, infer missing variants, calculate publishability, build endpoint paths, or reconstruct
family relationships from URLs.

The diagnostic contract must distinguish:

```json
{
  "diagnostics": {
    "own": { "errors": 0, "warnings": 1 },
    "linked": { "errors": 0, "warnings": 0 },
    "intents": { "errors": 2, "warnings": 3 },
    "rollup": { "errors": 2, "warnings": 4 }
  }
}
```

- `own` describes the concrete page itself and participates in that page's action readiness;
- `linked` describes ordinary linked runtime/page data under the existing page-workbench rules;
- `intents` describes related intent variants and is an attention/read-model scope, not a source publish gate;
- `rollup` is the backend-calculated display total for the source row and higher navigation indicators.

An invalid intent page is counted in the matching Ukraine/region summary, family summary, locale indicator,
source page `intents` indicator, hierarchical ancestor roll-ups, the Practices group, and the open matrix
summary. The same leaf diagnostic must be counted exactly once in every aggregate. Implementations must use
stable diagnostic identity or an equivalent canonical leaf-state aggregation strategy rather than adding
already aggregated parent totals together.

`INTENT_LINKS_CHANGED` is the explicit exception to non-own intent diagnostics. It describes the source page
itself: the source page's current immutable snapshot contains an outdated set of intent links. It is therefore
an `own` stale/attention reason on the source page, even though its metadata identifies the related family.
It does not mean that the source page is unpublished and does not silently republish it.

### Regional publication counter

The compact counter shown for Ukraine or a region is:

```text
published existing intent pages / all existing intent pages
```

For example, `2/2` means that two concrete intent pages currently exist for that Ukraine/region row and both
are published. Expected but not yet created variants are not included in this denominator. They remain visible
separately through `expectedVariants`, `existingVariants`, `missing/blocked` state, and diagnostic indicators,
so a successful publication ratio cannot hide incomplete provisioning.

### Refresh after mutation

Saving, publishing, rolling back, reconciling, or otherwise changing an intent variant can change the row,
region summary, family summary, locale summary, source indicator, ancestor roll-ups, and menu indicators.
After every such mutation the frontend must either reload the complete source-scoped read model or call a
backend refresh endpoint that returns the changed row together with every affected aggregate. Refreshing only
the visible intent row is insufficient.

### Matrix publication scope

The existing geographic or hierarchy scope and the intent inclusion scope are independent dimensions. Bulk
publish requests and their mandatory backend plans must therefore include an explicit `contentScope`:

```text
source_only
intents_only
source_and_intents
```

`source_only` is the safe default. Collapsed intent rows must never be published implicitly by an ordinary
matrix publication action. The backend publish plan must list every concrete page and its outcome before the
operation is executed.

### Menu indicators

The hierarchical menu structure remains unchanged, but its indicator contract changes. Intent pages create no
menu nodes; their diagnostic state is included in a separate intent roll-up of the matching source page and
its ancestors. This roll-up must preserve the distinction between source-own, regional, hierarchy-child, and
intent diagnostics and must not double-count a diagnostic that is already represented in a lower aggregate.

In addition to contextual navigation, CMS needs a global `Intent pages` audit view with filters for:

- source page type;
- source hierarchy;
- family;
- locale;
- region;
- draft/published/stale/blocked state;
- missing regional variants;
- reconciliation and repair failures.

This global view is especially important after a new region creates drafts in many families.

## Archive Lifecycle

Archive is a reversible administrative state, not physical deletion.

An archived intent family:

- is hidden from the normal active navigation;
- remains available through an `Archived` filter;
- preserves page ids, routes, versions, snapshots, audit history, and source bindings;
- cannot create, repair, or publish variants until restored;
- keeps its slug/routes reserved.

Archiving must use an explicit impact plan. If the family still has published variants, the plan includes
their unpublication and the resulting stale source/national snapshots. Nothing is unpublished silently.

The first version does not physically delete intent families.

Unpublishing or archiving a source page must discover its published intent dependants. The isolated source
operation is blocked until an explicit plan accounts for them. Making a region inapplicable follows the
same principle: variants receive diagnostics and an explicit unpublish/archive plan rather than automatic
deletion.

## Public Navigation And Indexing Boundaries

Intent pages are not automatically inserted into the primary public service hierarchy menu.

When published, they must:

- have crawlable links to and from the matching source variant;
- enter the appropriate sitemap;
- have their own canonical URL;
- use ordinary locale-alternate rules;
- have breadcrumbs that preserve the complete matching source hierarchy and append the intent as the
  final leaf;
- remain excluded from public output while they are drafts.

Illustrative national breadcrumb:

```text
Home -> Services -> Family law -> Alimony -> Alimony lawyer
```

Illustrative regional breadcrumb:

```text
Home -> Kyiv -> Services -> Family law -> Alimony -> Alimony lawyer in Kyiv
```

V1 public discovery is limited to:

- automatic source-to-intent and intent-to-source links;
- national-intent-to-regional-intent links;
- breadcrumbs;
- sitemap entries;
- ordinary locale alternatives.

Intent pages are not added to the primary public menu and V1 does not introduce a separate public intent
catalog or index page. The global intent-family list is an administrative CMS audit view only.

The feature must not equate automatic draft creation with search readiness. Regional variants are published
independently only after their content is useful for that intent and region.

## JSON-LD Intent Entity Principle

The initial accepted principle is that a search phrase does not create a new business entity.

- an intent page does not create a new `Service @id` merely because it uses a different query or title;
- the national intent `WebPage` describes the same page-backed source entity from a different search angle;
- the relationship uses the final source entity type and stable `@id` selected by the general JSON-LD
  architecture;
- national and regional intent `WebPage.mainEntity` values reference that same source `Service` entity;
- a regional intent describes geography and provider by the same rules as its matching ordinary regional
  source variant: `Service.provider` references the regional `LegalService`, and `Service.areaServed`
  identifies the region;
- the existence of a regional intent page does not itself create an `Offer`;
- intent-page `Offer` nodes follow the common price-to-service binding contract. They are emitted only from
  a real visible offer such as a published price row, with `itemOffered` referencing the actual `Service`
  and `seller` referencing the applicable global or regional provider;
- a search phrase, page title, or regional URL must never be interpreted as an offer by itself.

These rules are normative and use the general service, provider, and offer model defined in
`docs/json-ld-architecture-2026-07-27.md`.

## Validation Scope For V1

Intent pages use the same section, page, locale, preview, and publication validation model as other
generated page types.

V1 does not add an intent-specific word-count, similarity, regional-uniqueness, or manual SEO-review gate.
Independent drafts and independent publication remain the editorial control.

Domain invariants are still mandatory validation, not optional SEO heuristics. Publication remains blocked
when, for example:

- the exact source binding is missing or ambiguous;
- the matching source variant is not published;
- the primary Ukrainian publication prerequisite is not met;
- the route conflicts with another page;
- ordinary required sections are invalid.

More advanced intent-content quality diagnostics may be added later without changing the family model.

## Required Diagnostics

The backend must expose stable machine-readable diagnostics for at least:

```text
INTENT_SOURCE_NOT_ELIGIBLE
INTENT_ON_INTENT_NOT_ALLOWED
INTENT_FAMILY_ALREADY_EXISTS
INTENT_ROUTE_CONFLICT
INTENT_SOURCE_VARIANT_MISSING
INTENT_SOURCE_VARIANT_NOT_PUBLISHED
INTENT_VARIANT_BINDING_MISSING
INTENT_VARIANT_BINDING_AMBIGUOUS
INTENT_PRIMARY_UA_NOT_PUBLISHED
INTENT_NATIONAL_VARIANT_NOT_PUBLISHED
INTENT_LINKS_CHANGED
INTENT_REGION_NOT_APPLICABLE
INTENT_RECONCILIATION_REQUIRED
```

Clients must not infer these states from missing URLs, empty arrays, or generic HTTP errors.

## Explicit Non-Goals For The First Version

- creating intent pages from other intent pages;
- automatic publication;
- automatic rewriting of published snapshots;
- manual selection of arbitrary source variants;
- silent national or cross-locale link fallback;
- slug editing, redirect management, and public identity re-keying;
- a separate intent-only page editor or publication engine;
- automatically placing every intent page in the primary public navigation tree;
- editor-managed source/intent URLs or typed per-FAQ-answer links in V1.

## Runtime Slot Keys

Intent pages use two semantically separate runtime/read-only slots:

### `regional_links`

- page type: `intent_page`;
- scope: national variants only;
- meaning: published regional variants of the same intent family in the current locale;
- source: backend-resolved family variant bindings and current published snapshots;
- empty public result: hide the section;
- CMS behavior: keep expected/missing/blocked variants visible through diagnostics.

### `local_offices`

- page type: `intent_page`;
- scope: regional variants only;
- meaning: real physical offices applicable to the current region;
- source: the same office/reference-data resolver contract used by other regional hierarchy pages;
- empty public result: hide the section, subject to the ordinary page diagnostics contract;
- not editable in the page section editor.

The legacy `regional_offices` key on existing page types is not renamed as part of this task. New
`intent_page` behavior must not use that misleading key.
