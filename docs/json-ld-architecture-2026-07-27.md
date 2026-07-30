# JSON-LD Architecture Decisions - 2026-07-27

## Status

This document records the decisions accepted during the JSON-LD requirements review. It is intentionally
incremental: accepted decisions are normative for the first implementation slice, while unresolved items
stay explicitly open.

JSON-LD is not yet implemented as a complete CMS/public-site contract.

## Decision 1: Graph ownership

- `cms-back` owns JSON-LD semantics, node composition, relationships, and `@id` rules.
- `site-front` receives an already assembled graph and only serializes it safely into
  `<script type="application/ld+json">`.
- `site-front` must not independently reconstruct or amend the semantic graph.
- `cms-front` may eventually show read-only preview and diagnostics, but it is not the graph owner.

## Decision 2: Relationship to page SEO

- JSON-LD is a computed part of the resolved top-level page `seo` payload.
- It belongs to the SEO surface for preview, validation, diagnostics, and publication.
- It is not a free-form authoring field and must not be exposed as an editable JSON textarea.
- The graph may use the complete resolved page model: SEO metadata, route, locale, breadcrumbs,
  page-owned content, runtime relationships, and global organization/location data.

Illustrative public shape:

```json
{
  "seo": {
    "title": "...",
    "description": "...",
    "canonicalUrl": "https://actum.com.ua/...",
    "ogImage": {},
    "structuredData": {
      "@context": "https://schema.org",
      "@graph": []
    }
  }
}
```

The final property names remain an implementation-contract detail to confirm before coding.

## Decision 3: Snapshot-first generation

- Preview JSON-LD is generated from the same resolved preview payload shown to the editor.
- Published JSON-LD is generated from the same resolved public payload used to create the page snapshot.
- The published graph is stored inside the immutable page snapshot.
- `site-front` renders the stored graph and does not rebuild it from live data on every request.
- Page rollback restores the corresponding historical JSON-LD together with the historical snapshot.
- Dependency changes do not silently mutate an already published graph.

## Decision 4: Page identity, locale, and region

- Every published locale/region URL is a separate `WebPage`.
- Every page variant has its own absolute production canonical URL and URL-based `WebPage @id`.
- Canonical URLs are self-referential.
- Ukrainian, Russian, and English pages do not share one `WebPage @id`.
- A regional page must not canonicalize to the base Ukraine page.
- Localized variants are related through the site's `hreflang` contract, not through a shared canonical.
- Develop/release hostnames must never appear in production graph identifiers.

Page-owned identifiers use the page canonical as their base:

```text
{canonicalUrl}#webpage
{canonicalUrl}#breadcrumb
{canonicalUrl}#faq
```

## Decision 5: A lawyer entity versus localized profile pages

- One real lawyer is one `Person` node.
- Localized lawyer pages are separate `ProfilePage`/`WebPage` nodes.
- Every localized profile points to the same `Person` through `mainEntity`.
- Localized names, descriptions, and credentials do not create separate people.
- The lawyer keeps one internal CMS UUID in `identifier`.
- For the current contract, the public `Person @id` is based on the lawyer's primary canonical profile URL
  plus a type fragment such as `#person`.

Illustrative relationship:

```json
[
  {
    "@type": "ProfilePage",
    "@id": "https://actum.com.ua/ru/advokaty/example#webpage",
    "inLanguage": "ru",
    "mainEntity": {
      "@id": "https://actum.com.ua/advokaty/example#person"
    }
  },
  {
    "@type": "Person",
    "@id": "https://actum.com.ua/advokaty/example#person",
    "identifier": "stable-cms-uuid",
    "name": "..."
  }
]
```

The same entity-versus-localized-page principle is expected to apply to other page-backed business
entities, but their exact Schema.org types and primary URLs remain separate decisions.

## Decision 6: Primary URL For A Page-Backed Entity

- The primary URL for a page-backed business entity is the canonical URL of its base, Ukrainian,
  non-regional page.
- The public entity `@id` uses that primary URL plus the appropriate type fragment.
- Russian, English, and regional pages remain separate `WebPage` nodes.
- Every localized/regional page relates its `mainEntity` to the entity identifier based on the base
  Ukrainian non-regional URL.
- Entity identity must not depend on which localized or regional variant happened to be published first.

Illustrative identifiers:

```text
Lawyer:   https://actum.com.ua/advokaty/example#person
Practice: https://actum.com.ua/services/example#entity
Service:  https://actum.com.ua/services/example/example-service#entity
Problem:  https://actum.com.ua/services/example/example-service/example-problem#entity
```

The placeholder `#entity` fragments for practice/service/problem are not final. Their exact fragments
depend on the Schema.org type decisions still to be made.

## Explicit V1 Scope Boundary: Slugs Are Immutable

For the first JSON-LD implementation, a page-backed entity slug is treated as immutable.

The following work is explicitly out of scope:

- a CMS UI for editing a slug;
- an ordinary admin API for changing a slug;
- old-slug alias management;
- automatic permanent redirect creation after a slug change;
- automatic `@id`, canonical, sitemap, breadcrumb, or `hreflang` migration after a slug change;
- dependency discovery and bulk snapshot rebuilding caused by a slug change;
- operational tooling for an exceptional slug re-key.

The architecture acknowledges that an exceptional future slug change would change the canonical URL and
the URL-based public entity `@id`, and would require redirects plus dependent snapshot rebuilds. That
future mechanism is not part of the current task and must not be implemented implicitly.

Current implementation assumption:

> A slug does not change after the entity receives its public canonical route and JSON-LD identity.

## Decision 7: Primary Ukrainian Publication Gate

- The base Ukrainian non-regional page is the publication prerequisite for every localized or regional
  variant of the same page-backed entity.
- Russian, English, and regional drafts may be created and edited before the primary Ukrainian page is
  published.
- Preview and publication of those variants are blocked until the primary Ukrainian page has a current
  published snapshot.
- The backend must expose an explicit blocking diagnostic such as
  `PRIMARY_UA_PAGE_NOT_PUBLISHED`; clients must not infer this state from missing URLs or failed payload
  assembly.
- Publishing the primary Ukrainian page removes this prerequisite failure, subject to the variant's own
  validation and publication readiness.
- This gate guarantees that the entity has a production canonical primary URL and stable public `@id`
  before another page variant refers to it.

## Open Decisions

The next unresolved block is the exact organization, regional `LegalService`, and physical-office graph.
The current discussion has identified, but has not yet made normative, the following questions:

- whether a regional `practice_collection_page` is the canonical entity page for the regional
  `LegalService`;
- the stable `@id` contract shared by that regional provider and all regional child pages;
- whether the primary regional office owns additional offices through `department`, or whether the
  offices are sibling local businesses under the global organization;
- whether `practice_collection_page` must gain a visible, runtime-only `local_offices` section so that its
  structured data is supported by visible page content;
- Schema.org type selection for practices, services, and problems, including how `Service` and
  `OfferCatalog` divide responsibilities;
- how pricing `Offer.itemOffered` references actual services instead of a provider organization.

Later decisions must cover non-page-backed entity identifiers, per-page node sets, reviews and ratings,
FAQ/cases/breadcrumbs, validation severity, and rollout.

Search-intent landing pages are specified separately in
`docs/intent-page-family-requirements-2026-07-30.md`. That document now defines the accepted family,
variant-binding, navigation, workbench, lifecycle, and entity-identity principles. Exact intent graph
templates still depend on the unresolved general organization/provider and service-type decisions in this
document and must not be implemented by inference.
