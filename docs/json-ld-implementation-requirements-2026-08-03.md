# JSON-LD Implementation Requirements - 2026-08-03

## Status And Authority

This document converts the accepted product and graph decisions in
`docs/json-ld-architecture-2026-07-27.md` into an implementation contract for `cms-back`, `site-front`,
admin preview/diagnostics, migrations, and tests.

The architecture decision document remains normative for entity meaning and identity. This document is
normative for payload shape, page templates, dependency tracking, validation behavior, and implementation
readiness. Search-intent and editorial details also require:

- `docs/intent-page-family-requirements-2026-07-30.md`;
- `docs/editorial-content-architecture-2026-06-19.md`;
- `docs/lawyer-page-structure-2026-06-18.md`.

No public frontend or admin frontend may independently reconstruct graph semantics.

## Implementation State

As of 2026-08-03, the first `cms-back` implementation is prepared but deliberately not activated:

- graph builders, snapshot persistence, blocking diagnostics, dependency tracking, repair inventory, and
  controlled backfill endpoints are implemented on the backend feature branch;
- database migrations are authored but have not been executed against shared environments;
- `CMS_JSON_LD_ENABLED_PAGE_TYPES` remains empty, so no page type generates or blocks publication on the
  new contract yet;
- no backfill, repair republish, Cloud Run deployment, or GCP configuration change has been performed;
- `site-front` safe script serialization and optional `cms-front` read-only diagnostics remain separate
  follow-up work and are not implemented by the backend change.

Activation therefore still requires migration review/execution, a dry-run inventory, explicit page-type
allowlisting in the accepted dependency order, frontend serialization, and release QA. Prepared code must
not be interpreted as an active production contract.

## Public And Preview Payload Contract

The resolved SEO payload uses one exact property:

```json
{
  "seo": {
    "title": "...",
    "description": "...",
    "canonicalUrl": "https://www.actum.com.ua/...",
    "structuredData": {
      "@context": "https://schema.org",
      "@graph": []
    }
  }
}
```

Rules:

- `seo.structuredData` is a pure JSON-LD object, not a JSON string and not an additional wrapper.
- Existing page-payload `schemaVersion` remains the transport contract version; no custom version field is
  inserted into Schema.org data.
- The backend stores `structuredDataBuilderVersion` as internal snapshot/publication metadata outside
  `seo.structuredData`. It identifies the deterministic builder contract used for the snapshot and is the
  only supported input for version-targeted stale detection and backfill selection; consumers must not
  inspect the graph to infer its version.
- `structuredDataBuilderVersion` is a positive integer starting at `1`. It increments when a deployed
  change can alter graph bytes, blocking validation, or captured dependency roles for already-published
  input; a code-only refactor with identical output and dependencies does not increment it.
- `@context` is exactly `https://schema.org` and appears once at the graph root.
- `@graph` is always an array with deterministic node ordering.
- Preview assembles this property from the resolved preview payload.
- Publication stores the exact property inside the immutable public page snapshot.
- Public reads return the stored snapshot value and never rebuild it from live reference data.
- A supported page type with a blocking graph error still returns the resolvable partial graph in preview.
- A public snapshot created before JSON-LD rollout may temporarily omit `structuredData`; `site-front` must
  treat absence as no script rather than an error.

Admin preview/readiness responses additionally expose diagnostics outside `seo.structuredData`:

```json
{
  "diagnostics": {
    "structuredData": [
      {
        "code": "JSON_LD_MAIN_ENTITY_UNRESOLVED",
        "severity": "error",
        "path": "@graph[1].mainEntity",
        "nodeId": "https://www.actum.com.ua/...#webpage",
        "sourceKind": "service",
        "sourceId": "cms-uuid",
        "message": "Required main entity cannot be resolved."
      }
    ]
  }
}
```

`message` is display text only. `code` and `severity` are the client contract.

## Common Graph Contract

Every supported public page graph follows these rules:

- all public `@id`, `url`, canonical, image, and profile URLs are absolute production URLs;
- develop, release, Cloud Run, admin, and localhost origins are forbidden in a publishable graph;
- every page has one page node at `{canonicalUrl}#webpage` using the most specific applicable `WebPage`
  subtype;
- every non-home page node references the global `WebSite` through `isPartOf` by `@id` only;
- every page-owned creative-work node uses the page canonical plus a stable fragment;
- every non-home public page with visible breadcrumbs has one page-owned `BreadcrumbList` at
  `{canonicalUrl}#breadcrumb`;
- the home page does not emit a synthetic one-item breadcrumb;
- breadcrumb positions are one-based, contiguous, route-resolved, and match visible navigation;
- only published and publicly resolvable targets enter lists, catalogs, breadcrumbs, alternates, and
  relationships;
- node arrays and property arrays are deterministically ordered, and repeated references are deduplicated
  by `@id`;
- a node builder registers every `@id` with its real entity kind; reuse for a conflicting kind is a
  publication-blocking error;
- disabled or non-visible sections contribute no structured-data nodes or stale dependencies;
- backend builders use typed source identifiers and relations, never localized labels or route parsing, to
  determine graph identity.

Required deterministic root order:

1. current page node;
2. current main entity or page-owned creative work;
3. page-owned breadcrumb and FAQ nodes;
4. offers/catalog/list nodes in visible order;
5. visible reviews, cases, lawyers, credentials, offices, and other enrichment nodes by stable source id;
6. partial referenced-entity enrichments explicitly owned by the current page.

Object property order is not semantically meaningful, but serializers and golden tests must keep one stable
order to make snapshots and diffs reviewable.

## Page-Type Node Matrix

| CMS page type | Page node | Required main entity and owned nodes | Conditional nodes |
|---|---|---|---|
| `home_page` primary Ukrainian | `WebPage` | full global `WebSite`; full global Actum `Organization`; page `mainEntity` references the organization | visible home lists only when explicitly typed; no breadcrumb and no synthetic search action |
| `home_page` Russian/English | `WebPage` | `mainEntity` references the global Actum organization and `isPartOf` references the global WebSite by `@id` | localized page properties only; it does not clone the complete global nodes |
| `about_page` | `AboutPage` | `mainEntity` references global Actum organization by `@id` | only visible sourced supporting entities |
| `career_page` | `WebPage` | no invented business entity; `about` references Actum | future `JobPosting` nodes only from an explicit published vacancy model |
| `lawyer_license_page` | `WebPage` | `about` references Actum; no organization certification is inferred from the page title | organization `Certification` only from explicit verified organization-license data |
| `contacts_page` | `ContactPage` | `mainEntity` references global Actum; partial same-id organization enrichment owns visible `contactPoint` and published regional-provider refs | stable office/provider refs; complete office nodes remain owned by regional collection pages |
| `practice_collection_page` national | `CollectionPage` | `mainEntity` is the national `OfferCatalog` of published practices; provider is global Actum | visible published catalog offers |
| `practice_collection_page` regional | `CollectionPage` | `mainEntity` is the complete regional `LegalService`; regional practice catalog; priority and department office graph | visible reviews/ratings if the page template supports them |
| `practice_page` | `WebPage` | stable practice `Service` | child-service catalog, prices/offers, FAQ, reviews, cases and other visible resolved enrichments |
| `service_page` | `WebPage` | stable service `Service` | child-problem catalog, prices/offers, FAQ, reviews, cases and other visible resolved enrichments |
| `problem_page` | `WebPage` | stable problem `Service` | prices/offers, FAQ, reviews, cases and other visible resolved enrichments; no empty child catalog |
| `intent_page` | `WebPage` | same source `Service @id` as the exact bound source variant | common price offers, FAQ and visible runtime enrichments; no offer caused only by intent/region/title |
| `lawyers_page` | `CollectionPage` | `mainEntity` is a page-owned `ItemList`; every item references a visible published lawyer `Person @id` and localized profile URL | partial item name/image may mirror the visible card; it does not own full lawyer profiles |
| `lawyer_page` | `ProfilePage` | localized complete-enough shared `Person` description | certification, education credentials, expertise, visible cases, publications and reviews |
| `blog_page` | `WebPage` | page-owned `BlogPosting` at `{canonicalUrl}#article` | reviewer, image, FAQ if supported, primary/additional service `about`, translation relation |
| `media_page` / `actum_article` | `WebPage` | page-owned `Article` at `{canonicalUrl}#article` | external work through `about`, reviewer, services, dates and image |
| `media_page` / `external_reference` | `WebPage` | external `CreativeWork` identified by required source URL | local `WebPage.about` service refs; no local Article and no invented external author |
| `case_page` | `WebPage` | page-owned `Article` at `{canonicalUrl}#article`; shared real-matter `Thing` | lawyers, services, reviews, translation relation, image and dates |
| `blog_collection_page` | `CollectionPage` | page-owned `ItemList` of published blog works | visible filters do not create entities |
| `media_collection_page` | `CollectionPage` | page-owned `ItemList` of published media target works/pages | mode-specific target ids |
| `case_collection_page` | `CollectionPage` | page-owned `ItemList` of published case-study articles | no draft entries |

`services_root` and `article_page` remain legacy routing compatibility types in the current backend type
union, but they are not current authoring schema types. The JSON-LD builder does not silently map or infer
their semantics. Rollout inventory must either migrate each surviving record to
`practice_collection_page`/`blog_page` with an explicit canonical identity decision or document it as an
immutable legacy snapshot outside the first rollout. Attempting to create a new JSON-LD publication for
either legacy type is blocked as unsupported.

All collection `ItemList` nodes use `{canonicalUrl}#item-list`; every `ListItem` has a contiguous `position`
and references the real target `@id` and public URL. Pagination, if introduced, produces a list for the
visible page only and must not claim hidden results.

Collection targets are exact:

- blog cards target the localized page-owned `BlogPosting @id`;
- case cards target the localized page-owned case-study `Article @id`;
- `actum_article` media cards target the localized page-owned `Article @id`;
- `external_reference` media cards target the localized Actum `WebPage @id`, because that is the real
  navigable collection item; the external work remains that page's `mainEntity`;
- lawyer cards target the shared `Person @id`, while `ListItem.url` uses the current locale's published
  lawyer-profile URL.

No collection entry may switch its target identity according to whichever optional node happens to be
available. `mainEntity` is required only where the matrix explicitly names it; `career_page` and
`lawyer_license_page` therefore remain valid without an invented `mainEntity`.

## Shared Node Templates

### Web page

Every page node includes, when resolved and visible:

```json
{
  "@type": "WebPage",
  "@id": "{canonicalUrl}#webpage",
  "url": "{canonicalUrl}",
  "name": "{visiblePageTitle}",
  "description": "{seoDescription}",
  "inLanguage": "{locale}",
  "isPartOf": { "@id": "{productionOrigin}/#website" },
  "publisher": { "@id": "{productionOrigin}/#organization" },
  "breadcrumb": { "@id": "{canonicalUrl}#breadcrumb" }
}
```

The most specific subtype replaces `WebPage`. `mainEntity`, `about`, `reviewedBy`, and `hasPart` are added
only by page-type rules. A missing optional image or description is a warning; missing canonical, name,
language, or required main entity is blocking.

### WebSite

The home graph owns:

```text
{productionOrigin}/#website
```

It includes production URL, visible site name, supported alternate name when sourced, publisher reference,
and supported languages. V1 does not emit `SearchAction` because no explicit public site-search contract is
defined. A future real public search feature may add it through a separate decision.

### Service and offers

Practice, service, problem, and intent pages use `#service` for the stable source entity fragment. Parent
catalog, `category`, provider, geography, prices, and offer rules follow Decisions 9-15 and 22 of the
architecture document.

An offer always has a stable page-owned or source-row-based identifier. Price-row offers use the stable
price item id, never array position or price text. Numeric values are JSON numbers normalized to the source
currency precision; display prefixes such as `from` are represented through the accepted
`PriceSpecification` mode rather than embedded into numeric values. The accepted V1 modes are `exact`,
`from`, `up_to`, `range`, and `negotiable`; `up_to` emits `maxPrice` and preserves existing upper-bound
price semantics.

### Reviews and aggregate ratings

A publishable full review node requires:

- `isReal=true` and `showOnSite=true`;
- a supported numeric source rating within the configured scale;
- a non-empty visible localized review text;
- a non-empty source-backed author name;
- a resolvable primary reviewed `Service`.

The review author is an inline `Person` with source-backed public name. No stable `Person @id` is invented
for a customer. Source `authorUrl` or photo may be emitted only when public, valid, and allowed by the
review contract; they never become proof of identity by inference.

`AggregateRating` for a `Service` counts only publishable reviews whose primary `itemReviewed` is that
service. A review attached through an additional topical chain can be visible on another service page but
does not contribute its rating to that other service. The aggregate uses the complete eligible set, not
only the current carousel slice, and the exact value/count must be visible on the page. Current scale is
validated as 1-5 and emits `bestRating: 5` and `worstRating: 1`.

### Images

Public content images use crawlable production URLs and may be emitted as `ImageObject` when width, height,
caption/title, and localized alt metadata are resolved. A missing optional image omits the property with a
warning; placeholders and admin/protected URLs are forbidden. The organization logo is owned by the home
organization graph and referenced elsewhere only when required by a supported consumer contract.

## Structured-Data Builder Boundary

`cms-back` implements one orchestration boundary with typed page builders, for example:

```text
StructuredDataService
  -> CommonPageGraphBuilder
  -> OrganizationGraphBuilder
  -> ServiceGraphBuilder
  -> LawyerGraphBuilder
  -> EditorialGraphBuilder
  -> ReviewGraphBuilder
  -> GraphIdentityRegistry
  -> StructuredDataValidator
```

The names are illustrative, but these constraints are mandatory:

- no single universal nullable context for all page types;
- each page builder receives the same resolved snapshot input used for public rendering;
- node builders are pure/deterministic for the same resolved input and production-origin configuration;
- the identity registry owns conflict detection and deduplication;
- graph generation performs no live network request and does not call external validators at runtime;
- source resolution happens before graph assembly and returns typed resolved/unresolved results;
- graph diagnostics preserve source kind/id and JSON path;
- a page snapshot stores both resolved content and the finished graph atomically.

## Stale Dependency Contract

The general rule is byte-impact based:

> A published page is marked stale only when a dependency change would change its resolved visible snapshot
> or stored JSON-LD. A page that contains only an unchanged stable `@id` reference is not stale merely
> because non-identity fields of the referenced entity changed elsewhere.

Dependency records must include source kind, source id, affected page id, dependency role, and the source
revision/digest captured by the current snapshot. Stale detection must not scan labels or parse stored JSON.

| Changed source/event | Pages marked stale | Pages not marked stale solely for this change |
|---|---|---|
| global organization identity/logo/legal data | home; contacts only if its partial visible enrichment changes | ordinary pages with bare organization `@id` refs |
| global contact point | home when visible there; contacts | service/editorial pages with publisher/provider id only |
| region priority-office selection | regional `practice_collection_page`; pages whose visible office list changes | regional service children that contain only regional-provider id |
| regional provider or office publish/unpublish | owning regional collection; contacts when its visible regional/office list changes; affected visible office consumers | regional service children that retain only the same regional-provider id |
| office address/geo/phone/hours | owning regional collection; contacts if it visibly repeats the changed contact value | lawyer profile containing only office `@id`; regional child service pages |
| lawyer office assignment | affected localized lawyer profiles and any visible runtime cards that expose office | unrelated service pages with no visible lawyer-office data |
| lawyer public name/profile/photo/license/education | affected locale profiles; visible lists/cards using changed fields | pages that carry only the lawyer `Person @id` |
| lawyer qualifications | lawyer profiles whose `knowsAbout`/visible practice list changes; visible qualified-lawyer runtime consumers | pages not consuming the lawyer qualification |
| service parent binding/route identity | the service page, descendants' breadcrumbs/category, old/new parent catalogs, exact bound intents and visible consumers | unrelated hierarchy branches |
| child service publish/unpublish | immediate parent catalog page and visible collections | descendants or siblings whose snapshot bytes do not change |
| price row | pages whose resolved visible price/offer includes the row | pages with no resolved price dependency |
| review text/author/rating/visibility/primary service | every page rendering that review; primary service pages whose aggregate changes; lawyer/case visible review consumers | services linked only through additional topical chains for aggregate purposes, unless their visible review list changes |
| review additional chain | affected related-service visible lists and review `about` graphs | primary service aggregate when primary itemReviewed/rating is unchanged |
| case publication/content/relations | case page; visible case collections, lawyer profiles, and service runtime lists that change | pages with only unchanged case ids and no visible case data |
| blog/media publication/content/relations | detail page and visible collections/lawyer/service consumers | unrelated pages |
| editorial translation publish/unpublish | that translation's collections and hreflang consumers | Ukrainian original solely for inverse `workTranslation`, which is not emitted |
| intent variant publish/unpublish | exact matching source navigation; national intent regional-links snapshot as specified by the intent requirements | unrelated source variants/locales/regions |
| JSON-LD builder/schema version change | pages of explicitly affected enabled page types selected by migration plan | page types not enabled or unaffected by the version change |

Stale behavior:

- dependency changes never mutate an immutable current snapshot;
- stale status is advisory for the already-live snapshot unless a separate safety rule requires unpublish;
- preview resolves current source data and shows the candidate updated graph;
- normal publication clears stale markers covered by the new snapshot;
- no dependency change automatically republishes a page during ordinary operation;
- rollback restores the historical graph and historical dependency captures, then recalculates current
  stale diagnostics against present source state;
- disabled optional sections register no dependency and cannot make their page stale.

## Required Diagnostic Codes

Blocking errors:

```text
JSON_LD_CANONICAL_MISSING
JSON_LD_CANONICAL_NOT_PRODUCTION
JSON_LD_PAGE_ID_INVALID
JSON_LD_PAGE_TYPE_UNSUPPORTED
JSON_LD_MAIN_ENTITY_UNRESOLVED
PRIMARY_UA_PAGE_NOT_PUBLISHED
JSON_LD_REGIONAL_PROVIDER_UNRESOLVED
JSON_LD_OFFER_SERVICE_UNRESOLVED
JSON_LD_ID_CONFLICT
JSON_LD_SERIALIZATION_FAILED
JSON_LD_REQUIRED_CONTRACT_INVALID
JSON_LD_MEDIA_MODE_REQUIRED
JSON_LD_EXTERNAL_SOURCE_URL_REQUIRED
JSON_LD_EDUCATION_ID_INVALID
```

Advisory warnings:

```text
JSON_LD_OPTIONAL_RELATION_UNRESOLVED
JSON_LD_OPTIONAL_IMAGE_MISSING
JSON_LD_LAWYER_WORK_LOCATION_MISSING
JSON_LD_LAWYER_QUALIFICATION_OMITTED
JSON_LD_REVIEW_OMITTED
JSON_LD_AGGREGATE_RATING_UNAVAILABLE
JSON_LD_OPTIONAL_CATALOG_ITEM_OMITTED
JSON_LD_OPTIONAL_EXTERNAL_SOURCE_MISSING
JSON_LD_RICH_RESULT_NOT_ELIGIBLE
JSON_LD_STALE_DEPENDENCY
```

Codes are stable API values. New codes may be added, but existing meanings/severities must not change
silently. Admin clients render backend severity and message and do not reimplement eligibility logic.

## `site-front` Serialization Contract

`site-front` performs only safe serialization:

1. read stored `payload.seo.structuredData`;
2. if absent, render no JSON-LD script;
3. serialize exactly once with JSON serialization;
4. escape `<`, `>`, and `&` as Unicode escapes and escape U+2028/U+2029, or use the framework's equivalent
   safe script-data serializer;
5. render one `<script type="application/ld+json">` for the stored graph;
6. attach the configured CSP nonce when the site CSP requires one.

It must not add nodes, repair URLs, replace origins, calculate ratings, infer locale/region, or merge another
frontend-owned graph. HTML and graph data must come from the same snapshot.

## Tests And Acceptance Gates

Required unit tests:

- identifier builders for every entity kind and environment-origin rejection;
- snapshot `structuredDataBuilderVersion` persistence and version-targeted stale selection;
- identity conflict registry and same-id deduplication;
- deterministic ordering;
- every page-type builder in national/regional and UA/RU/EN variants where applicable;
- price modes and explicit service binding;
- primary/additional service endpoints;
- review primary itemReviewed versus topical about relations;
- media representation modes;
- lawyer license/education/work/expertise relations;
- validation severity and partial-preview behavior;
- visible-content digest and `contentModifiedAt` behavior.

Required integration tests:

- authoring/preview -> validation -> publish -> stored snapshot -> public read;
- failed publish writes neither current snapshot nor prepared `with_page` section versions;
- rollback restores the exact historical graph;
- technical republish preserves `contentModifiedAt`;
- stale dependency changes mark only affected pages;
- primary-UA gate blocks dependent locale/region publication;
- intent binding and regional provider resolution;
- review/aggregate changes and collection/list membership;
- media mode migration/readiness;
- education-id locale consistency;
- public graph never contains admin, localhost, develop, release, or Cloud Run hostnames.

Required frontend contract tests:

- stored graph is emitted byte-equivalently after JSON parse/serialize normalization;
- no script when property is absent;
- hostile text containing `</script>` cannot break out of the JSON-LD script;
- no duplicate graph produced by layout and page components;
- CSP nonce behavior where enabled.

Required fixtures/golden snapshots cover at least every row of the page-type matrix, plus disabled optional
sections, incomplete optional data, blocking identity failure, rollback, and stale preview.

External Schema.org/Google validation may run in CI or release QA against fixtures, but production preview
and publish cannot depend on a network validator. Search-engine rich-result eligibility is advisory and
does not replace the backend truth/identity contract.

## Data Migration Prerequisites

Before lawyer-page JSON-LD is enabled:

- generate immutable `educationItemId` values for Ukrainian education facts;
- explicitly align translations to those ids;
- require manual resolution where locale arrays are ambiguous rather than matching localized text;
- preserve empty education lists as valid.

Before media-page JSON-LD is enabled:

- add required `representationMode` to the authoring/API contract;
- do not infer values for existing pages;
- require explicit classification before a new JSON-LD snapshot is published.

Before any page-type rollout is enabled:

- inventory surviving `services_root` and `article_page` records and their current public snapshots;
- explicitly migrate or exempt every such record; no page may be retyped or redirected by inference.

Additional service-tree arrays default to an empty list for blog/media records that predate the feature.
Existing editorial publications receive an empty `contentModifiedAt`; migration timestamps must not be
presented as visible content modifications. Existing published snapshots remain immutable throughout all
migrations.

## Accepted Rollout Decisions

The semantic, implementation, and rollout contracts are complete. The following operational choices were
accepted by the owner on 2026-08-03.

### R1. Initial snapshot backfill

After a dry-run inventory, run a controlled backend system republish for current pages
that pass the new contract. It creates new immutable snapshots, preserves visible content and
`contentModifiedAt`, records a system actor/reason, and never publishes pages that fail diagnostics. Failed
pages remain on their previous snapshot and enter a repair queue.

The dry-run endpoint accepts explicitly requested supported page types in inspection mode even while those
types are absent from the runtime rollout allowlist. Inspection mode must not activate preview, publish, or
public snapshot generation. The mutating backfill endpoint remains restricted to page types already enabled
in the runtime allowlist. This preserves the required order: inventory first, activation second, controlled
republish third.

Requiring a human to open and publish every existing page was rejected as the default rollout mechanism.
Human repair and publication remain required for records that fail the dry run or blocking validation.

### R2. Public activation scope

Enable generation, blocking validation, backfill, and `site-front` rendering by page type in dependency
order rather than with one global switch:

1. home/global organization and contacts;
2. national Ukrainian service collection and hierarchy;
3. regional collections/providers/offices and regional hierarchy;
4. lawyers and lawyer collection;
5. editorial details and collections;
6. intent pages;
7. remaining locales after their primary Ukrainian prerequisites pass.

Each type advances through shadow preview, stored snapshot, release rendering/QA, then production rendering.
One all-or-nothing activation was rejected because it increases launch coupling and rollback scope.
