# JSON-LD Architecture Decisions - 2026-07-27

## Status

This document records the decisions accepted during the JSON-LD requirements review. Decisions 1-31 are
normative for the first implementation. The exact implementation contract is completed in
`docs/json-ld-implementation-requirements-2026-08-03.md`, including the accepted backfill and staged-rollout
strategy.

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

The exact property is `seo.structuredData`; it contains the pure JSON-LD object. Diagnostics remain outside
that object as defined in `docs/json-ld-implementation-requirements-2026-08-03.md`.

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

The same entity-versus-localized-page principle applies to the service and editorial entities defined by
the later decisions in this document.

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
Practice: https://actum.com.ua/services/example#service
Service:  https://actum.com.ua/services/example/example-service#service
Problem:  https://actum.com.ua/services/example/example-service/example-problem#service
```

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

## Decision 8: Regional LegalService And Office Graph

- Every region is represented by one stable regional `LegalService`.
- The regional `practice_collection_page` is the authoritative page for the complete regional
  `LegalService` graph.
- The regional `LegalService` uses the configured priority office as the source of its primary address,
  telephone, map, coordinates, opening hours, and other location-specific properties.
- The region has one explicit `primaryOfficeId` setting shared by all regional pages.
- If the configured priority office cannot be used, resolution falls back deterministically to the first
  visible office by `sortOrder`, then by stable office identifier.
- The regional `LegalService` keeps its own stable regional `@id` and points to the priority physical
  office through `location`.
- Every physical office, including the priority office, is a separate `LegalService` and keeps its own
  stable locale-neutral `@id`; changing the priority office must not change or exchange physical-office
  identities.
- A physical-office `LegalService` is used directly as both the branch organization and physical place.
  The graph must not create an additional parallel `Place` node for the same office.
- The regional `LegalService.parentOrganization` points to the single global Actum organization.
- Only non-priority offices appear in the regional `LegalService.department` collection.
- Every physical office, including the priority office, points back to the regional `LegalService` through
  `parentOrganization`. Priority status changes only whether an office is referenced through the regional
  provider's `location` or `department`; it does not change the office's parent or identity.
- Physical-office nodes own their office-specific address, geo coordinates, telephone, opening hours, and
  stable branch code. The regional provider may expose the selected priority-office values according to
  the resolution rule above, but the office node remains their authoritative physical source.
- Regional practice, service, problem, and intent pages refer to the regional provider only by its stable
  `@id`. They do not repeat a new full regional organization node.
- The regional practice collection exposes the corresponding visible runtime-only `local_offices` section,
  so the complete structured office graph is supported by visible page content.

## Decision 9: Practice, Service, And Problem Entity Types

- Practice, service, and problem business entities all use the Schema.org `Service` type.
- Their difference is expressed by the CMS hierarchy and graph relationships, not by inventing different
  entity types for each hierarchy level.
- A parent `Service` may expose published child services through `hasOfferCatalog`.
- The catalog is an `OfferCatalog`; every catalog entry is an `Offer`.
- `Offer.itemOffered` points to the stable `@id` of the actual child `Service`.
- `OfferCatalog` is a supporting list structure and is not the main business entity of the page.
- Only existing published children may be included in a published catalog.

Provider and geography follow the page variant:

- on a base Ukraine page, `Service.provider` points to the global Actum organization and `areaServed`
  identifies Ukraine;
- on a regional page, `Service.provider` points to the corresponding regional `LegalService` and
  `areaServed` identifies that region;
- all locale and region variants continue to use the one stable `Service @id` derived from the primary
  Ukrainian non-regional page;
- a regional child page references the regional `LegalService @id`; the full provider node remains owned
  by the regional practice collection.

## Decision 10: Pricing Offers Must Bind To Real Services

- Every enabled price-section row produces a separate `Offer`.
- `Offer.itemOffered` always points to a real existing `Service @id`; it must never point to an
  `Organization` or `LegalService`.
- On a page whose current business entity is a `Service`, a price row targets the current `Service` by
  default.
- An editor may explicitly bind a price row to an appropriate child `Service` when the row prices that
  child instead.
- On a page whose current business entity is a `LegalService`, including a regional practice collection,
  there is no default current `Service`; every enabled price row therefore requires an explicit service
  binding.
- The backend must not infer a service relationship from a price-row name or other mutable display text.
- `Offer.seller` points to the same provider selected for the page: the global Actum organization on a
  base Ukraine page or the regional `LegalService` on a regional page.
- Price text, currency, exact price, and starting-price semantics are represented through the
  `Offer`/`PriceSpecification` contract.

## Decision 11: Explicit Price Modes

- Every structured price row has an explicit `priceMode`; the backend must not infer price semantics from
  display text, punctuation, prefixes, or translated words.
- Supported V1 modes are:
  - `exact`: emit `PriceSpecification.price`;
  - `from`: emit `PriceSpecification.minPrice`;
  - `range`: emit both `PriceSpecification.minPrice` and `PriceSpecification.maxPrice`;
  - `negotiable`: do not emit a numeric price; preserve the visible localized explanation through the
    offer description.
- `priceCurrency` is required for `exact`, `from`, and `range` and uses an ISO 4217 currency code.
- `exact` requires one numeric price.
- `from` requires one numeric minimum.
- `range` requires numeric minimum and maximum values, and the maximum must not be lower than the
  minimum.
- `negotiable` must not publish a fabricated zero, minimum, maximum, or currency.
- Localized display labels such as `від`, `от`, and `from` are presentation values and do not determine
  the machine-readable mode.

## Decision 12: Regional And Office Identifier Templates

- The production origin is supplied by backend configuration; JSON-LD builders must not hardcode a
  develop, release, preview, or production hostname.
- The global Actum organization identifier is:

  ```text
  {productionOrigin}/#organization
  ```

- The global website identifier is:

  ```text
  {productionOrigin}/#website
  ```

- The regional `LegalService @id` is based on the canonical Ukrainian regional
  `practice_collection_page` URL:

  ```text
  {canonicalUkRegionalServicesUrl}#legal-service
  ```

  Example:

  ```text
  https://actum.com.ua/kyiv/services#legal-service
  ```

- Russian and English regional pages reference the same Ukrainian-derived regional `LegalService @id`.
- A physical office without its own canonical public page uses the stable locale-neutral identifier:

  ```text
  {productionOrigin}/#office-{officeUuid}
  ```

- An office identifier does not depend on locale, region, `primaryOfficeId`, `sortOrder`, or current
  department membership.
- Moving an office between regions or changing regional office priority must not change the physical
  office `@id`.
- The underlying region and office UUIDs may also be emitted through `identifier`; `@id` remains the
  public graph identity.

## Decision 13: Practice Collection Page Main Entities

- The base Ukrainian and localized non-regional `/services` page is a `CollectionPage` whose
  `mainEntity` is the published practice `OfferCatalog`.
- The base collection graph references the global Actum organization as `publisher` and as the provider
  of catalogued services. It does not create a page-local duplicate organization.
- A regional `/{region}/services` page is a `CollectionPage` whose `mainEntity` is the corresponding
  regional `LegalService`.
- The regional `LegalService.hasOfferCatalog` points to the published regional practice catalog.
- The regional collection page is also the authoritative graph owner for the selected priority office,
  `location`, non-priority `department` offices, and their reciprocal organization relationships.
- Locale-specific collection pages keep their own `CollectionPage`/`WebPage @id`, canonical URL, language,
  and breadcrumb nodes while referring to shared business-entity identifiers.

## Decision 14: Service-Hierarchy Page Graphs

- Every `practice_page`, `service_page`, and `problem_page` variant has its own `WebPage` node and uses
  its current business `Service` as `mainEntity`.
- A practice `Service.hasOfferCatalog` exposes the published service children of that practice.
- A service `Service.hasOfferCatalog` exposes the published problem children of that service.
- A leaf problem `Service` does not emit an empty catalog.
- Catalog membership is assembled from the published service hierarchy and never inferred from editable
  names or route text.
- Every page variant has its own page-owned `BreadcrumbList` generated from the resolved public route and
  hierarchy.
- Provider and geography use the accepted base-versus-regional rules.
- Locale and regional page variants retain distinct `WebPage @id` values while referring to the stable
  primary-Ukrainian `Service @id`.

## Decision 15: Reverse Service-Hierarchy Relationship

- The authoritative parent-to-child business relationship remains:

  ```text
  Service.hasOfferCatalog -> OfferCatalog -> Offer.itemOffered -> child Service
  ```

- A child `Service.category` points to the stable `@id` of its immediate parent `Service`.
- `category` contains only the immediate parent, not the complete ancestor chain.
- The complete user-facing page hierarchy remains represented by `BreadcrumbList`.
- The child page does not repeat a partial copy of the parent's `OfferCatalog`; this avoids duplicate
  ownership and unnecessary stale dependencies.
- `isPartOf` is not used between services because it is a CreativeWork relationship.
- `isRelatedTo` is not used for hierarchy because it does not express parent/child direction. It remains
  available only for genuinely non-hierarchical related-service relationships if such a feature is
  specified later.

## Decision 16: Reviews, Ratings, Lawyers, And Cases

- CMS reviews are real source-backed reviews with one real rating per review.
- Every structured review uses a stable locale-neutral identifier:

  ```text
  {productionOrigin}/#review-{reviewUuid}
  ```

- Reusing the same published review on several pages does not create several reviews; every occurrence
  keeps the same `Review @id`, source text, author, date, and rating.
- `Review.reviewRating` is emitted from the stored source rating. The backend must not invent a default or
  assume a five-star score.
- The reviewed legal `Service` is the primary `Review.itemReviewed`.
- Lawyers who participated in providing the reviewed service are linked through `Review.about` to their
  stable `Person @id` values.
- The related case, when one exists and is publishable as a graph entity, is also linked through
  `Review.about`. Absence of a case is valid and does not create a placeholder node.
- A lawyer `Person` may point back to visible related reviews through `subjectOf`; it must not treat the
  service rating as a rating of the person.
- A lawyer `ProfilePage` may include the full nodes for reviews visibly rendered on that page. Those nodes
  still use their global review identifiers and continue to review the same `Service`.
- `AggregateRating` may be emitted for a `Service` only when it is calculated from the complete defined set
  of eligible published ratings and the aggregate is represented in visible page content.
- V1 does not attach `AggregateRating` to `Person` because Schema.org does not define that property for
  `Person`.
- Authentic reviews published on Actum's own site remain self-serving for Google rich-result eligibility.
  JSON-LD must not promise or model around review stars that Google does not support for this scenario.

## Decision 17: Real Cases And Localized Case Publications

- A real client matter and a public `case_page` publication about that matter are separate graph entities.
- The real matter uses a stable locale-neutral generic `Thing` because Schema.org has no suitable
  `LegalCase` type and the CMS cases are not uniformly events, organizations, or court documents.
- The real matter identifier is:

  ```text
  {productionOrigin}/#case-{localeGroupId}
  ```

- The matter uses the ERP case identifier when available and otherwise its stable CMS locale-group
  identifier through `identifier`.
- Every localized `case_page` has its own `WebPage` and `Article` nodes derived from that locale's canonical
  URL. The `Article` uses `genre: "Case study"`.
- Every localized case `Article.about` points to the shared real-matter `Thing` and to the explicitly linked
  primary/additional legal `Service` entities.
- The primary lawyer is `Article.author`; co-author lawyers are `Article.contributor` values; all use stable
  `Person @id` references.
- `Article.publisher` points to the global Actum organization.
- Published Russian and English case articles use `translationOfWork` to reference the published primary
  Ukrainian case article while retaining independent localized page/article identifiers and content.
- The real-matter `Thing.subjectOf` may point to its published localized case articles and linked published
  reviews.
- A linked `Review` continues to review the legal `Service` through `itemReviewed`; its `about` collection
  may additionally point to the real-matter `Thing` and participating lawyer `Person` nodes.
- Absence of a linked case on a review is valid and never creates a placeholder case entity.

## Decision 18: FAQ As A Page Fragment

- A service-hierarchy or intent page remains a `WebPage` whose `mainEntity` is its business `Service`.
- The complete page is not additionally typed as `FAQPage` merely because it contains an FAQ section.
- An enabled, non-empty, visibly rendered FAQ section produces a subordinate `FAQPage` node with the
  page-owned identifier:

  ```text
  {canonicalUrl}#faq
  ```

- The main `WebPage.hasPart` references the FAQ fragment, and the `FAQPage.isPartOf` points back to the
  main `WebPage`.
- `FAQPage.about` references the current `Service`.
- Every FAQ item produces one `Question` with a stable identifier based on the item's UUID rather than
  its array position:

  ```text
  {canonicalUrl}#question-{faqItemUuid}
  ```

- `FAQPage.mainEntity` lists the published `Question` nodes. Every question contains one
  `acceptedAnswer` of type `Answer` assembled from the resolved published content.
- Disabled, empty, hidden, or unresolved FAQ sections do not produce `FAQPage`, `Question`, or `Answer`
  nodes.
- The answer serializer preserves only the explicitly allowed safe content contract; it must not expose
  unsafe editor HTML in JSON-LD.
- Google removed the FAQ rich-result feature in 2026. This graph is retained for truthful Schema.org
  semantics and other consumers, not as a promise of a Google FAQ snippet.

## Decision 19: Global Organization Ownership And Contact Enrichment

- Actum is one global `Organization` identified by the locale-neutral identifier defined in Decision 12:

  ```text
  {productionOrigin}/#organization
  ```

- Repeating that exact `@id` does not create another organization. Consumers must merge descriptions
  carrying the same identifier.
- The primary Ukrainian home page is the authoritative owner of the complete global `Organization` node
  and the complete global `WebSite` node.
- Other pages must not clone the complete organization description. They normally reference the global
  organization only by `@id` from properties such as `publisher`, `provider`, and `parentOrganization`.
- The localized contacts page is a deliberate exception for contextual enrichment:
  - its page node is a `ContactPage`;
  - `ContactPage.mainEntity` references the global Actum organization;
  - its graph may repeat the same global `Organization @id` with only the contact-related properties that
    are visibly represented and resolved on that contacts page;
  - those properties may include `contactPoint` values and `subOrganization` references to published
    regional `LegalService` entities.
- Contact-page enrichment is a partial description of the existing organization, not a second authoritative
  copy. Identity, name, logo, legal identity, and other organization-wide fields remain owned by the home
  page graph.
- Full regional `LegalService` and office nodes remain owned by their regional collection pages. The
  contacts page links to those entities by their stable `@id` values and does not clone their complete
  descriptions.
- Disabled, unpublished, or unresolved contact points and regional providers must not be emitted as
  placeholder references.

## Decision 20: Lawyer Employment And Work Location

- A lawyer `Person.worksFor` references the single global Actum `Organization`.
- A lawyer's current physical office is represented separately through `Person.workLocation`, referencing
  the stable `@id` of that physical-office `LegalService`.
- The regional aggregate `LegalService` is a regional service provider, not a separate employer. A lawyer
  does not receive an additional `worksFor` relationship to it.
- Moving a lawyer between offices changes `workLocation` only. It does not change the lawyer's `Person
  @id`, global employment relationship, or localized profile-page identities.
- `memberOf` is not used to express employment, regional assignment, or office location. It may be added
  in the future only for a separately sourced and verified membership in a professional organization or
  membership program.
- If a current physical office cannot be resolved, the graph omits `workLocation` and reports a diagnostic;
  it must not substitute the regional aggregate provider as a synthetic office.

## Decision 21: Lawyer Qualifications As Expertise

- Active lawyer qualifications that satisfy the existing public eligibility rule (`score > 1`) are exposed
  through `Person.knowsAbout`.
- Every `knowsAbout` value references the stable `@id` of an existing published `Service` entity. This may
  be a practice-, service-, or problem-level entity because all three levels use the `Service` type under
  Decision 9.
- The internal qualification score is a CMS/ERP selection rule and must not be emitted in public JSON-LD.
- A qualified entity is eligible for the graph only after its primary Ukrainian non-regional page is
  published and its stable public identifier can be resolved.
- An unpublished, inactive, or unresolved qualification is omitted and produces a diagnostic. The graph
  must not replace an unresolved service reference with a text label.
- Lawyer expertise does not make the lawyer the page's service provider or seller. `Person.makesOffer`
  is not generated from qualifications; services remain provided by the global Actum organization or the
  corresponding regional `LegalService`.

## Decision 22: Intent Pages Reuse The Common Service And Offer Model

- An intent page is a different search and content angle on an existing source `Service`; it does not
  create a new business entity or `Service @id`.
- National and regional intent `WebPage.mainEntity` values reference the same source `Service` as their
  matching ordinary source variants.
- A regional intent applies the common regional semantics: `Service.provider` references the regional
  `LegalService`, and `Service.areaServed` identifies the matching region.
- A search phrase, title, intent family, or regional URL does not by itself create an `Offer`.
- Intent-page offers are generated only from the same real visible offer sources used on ordinary service
  pages, including explicitly service-bound published price rows under Decisions 10 and 11.
- An intent-page `Offer.itemOffered` references the actual source `Service`, and `Offer.seller` references
  the applicable global organization or regional `LegalService`.
- The detailed intent-family lifecycle and exact source-variant binding remain governed by
  `docs/intent-page-family-requirements-2026-07-30.md`.

## Decision 23: Publication-Blocking Versus Advisory Diagnostics

- JSON-LD validation uses at least two severities: publication-blocking errors and advisory warnings.
- Preview remains available when blocking errors exist. It returns the resolvable partial graph together
  with stable machine-readable diagnostics; only publication is blocked.
- Publication is blocked when the graph would be technically invalid, materially false, or unable to
  preserve its required identity and primary business relationships. Blocking conditions include:
  - missing or invalid production canonical URL or required `WebPage @id`;
  - unresolved required `mainEntity`;
  - a violated primary-Ukrainian entity identity or publication prerequisite;
  - a regional page whose required regional provider cannot be resolved;
  - an `Offer` whose required real `Service` binding cannot be resolved;
  - conflicting use of one `@id` for different real entities;
  - graph serialization failure or violation of the backend's required Schema.org contract.
- An optional enrichment failure does not block publication. The affected optional node or property is
  omitted, and a warning is returned. Advisory conditions include:
  - an unresolved individual lawyer qualification;
  - a missing lawyer `workLocation`;
  - absent reviews, aggregate rating, cases, FAQ, prices, or other optional content;
  - an unresolved optional child-service catalog entry;
  - a missing recommended but non-required Schema.org property;
  - failure to qualify for a search-engine-specific rich result while the Schema.org graph remains
    truthful and valid.
- Omission is permitted only for genuinely optional enrichment. The backend must not downgrade a required
  identity or business-relation error to a warning merely to allow publication.
- Diagnostic codes, affected node/property paths, severity, and human-readable explanations belong to
  the backend contract; clients must not infer severity from message text.

## Decision 24: Localized Lawyer Profile Graphs

- The primary Ukrainian lawyer page remains the authoritative identity root for the shared `Person @id`.
- Every localized lawyer page emits its own `ProfilePage`/`WebPage` node and a sufficiently described
  `Person` node with that same shared identifier. A non-primary profile must not use only a bare `@id`
  reference as its `mainEntity`.
- The localized profile graph includes the current page's visibly rendered localized values, including the
  lawyer's public name, professional description, localized role label, and image when available.
- The localized profile graph also repeats the same locale-neutral facts and references when resolved,
  including internal public identifier, lawyer credential, `worksFor`, `workLocation`, and `knowsAbout`.
- Values from other locales are not loaded into the current page graph. The current `ProfilePage.inLanguage`
  identifies the page language, while the shared `Person @id` establishes that localized names and
  descriptions refer to the same real lawyer.
- Different localized spelling or transliteration of a lawyer's name must not create another `Person`.
- The current locale's required public name must be resolved before publication. Missing optional profile
  enrichment follows the diagnostic severity rules in Decision 23.

## Decision 25: Lawyer License As Certification

- A lawyer's professional license/certificate is modeled as a separate stable `Certification` node and is
  linked from the lawyer through `Person.hasCertification`.
- The certification uses a page-backed locale-neutral identifier based on the primary Ukrainian lawyer
  profile URL:

  ```text
  {primaryUkLawyerCanonicalUrl}#lawyer-license
  ```

- `Certification.certificationIdentification` contains the real lawyer certificate/license number.
- `Certification.about` references the shared lawyer `Person @id`.
- The certification's visible name is localized to the current profile page while retaining the same
  certification `@id` across locales.
- `issuedBy`, `datePublished`, `certificationStatus`, and a public verification `url` are emitted only when
  the corresponding data is explicitly sourced and verified. The backend must not infer an issuer,
  issuance date, status, or registry URL from the certificate number.
- The generic CreativeWork `license` property must not be used for the right to practise law; that property
  describes usage/licensing terms for content rather than a person's professional authorization.
- `EducationalOccupationalCredential`/`hasCredential` is not used for this specific lawyer-license record
  in V1 because `Certification` expresses the authoritative professional attestation more precisely.

## Decision 26: Lawyer Education And Degree Identity

- Every `educationItems` record is an editor-confirmed completed education fact. A populated `degree`
  represents a degree or qualification actually awarded to the lawyer.
- Every education fact receives a backend-generated immutable `educationItemId` shared by all locale
  translations. Array position and localized content must never be used as identity inputs.
- The primary Ukrainian lawyer profile owns the common education-item set and ordering. Other locales
  translate the fields of the same items and cannot independently create, remove, or re-key them.
- The current localized `institution` value produces a `Person.alumniOf` entry represented as an inline
  `EducationalOrganization`. No global institution `@id` is invented without authoritative institution
  reference data.
- A populated `degree` additionally produces an `EducationalOccupationalCredential` linked through
  `Person.hasCredential` with the stable identifier:

  ```text
  {primaryUkLawyerCanonicalUrl}#education-{educationItemId}
  ```

- The credential's `name` and optional specialization are localized from the current profile. Its
  `credentialCategory` is `degree`.
- An education item without `degree` may still produce `alumniOf` but does not produce a credential node.
- `periodLabel` and free-form notes remain visible profile content and are not converted into structured
  dates or credential assertions.
- Missing, duplicate, unknown, or locale-mismatched education-item identifiers are validation errors. The
  backend must not derive an identifier from an institution name, degree, translated text, or list index.

## Decision 27: Public Authorship Versus Internal CMS Users

- Internal CMS users are editors/operators, not public author entities. A CMS user must never be converted
  automatically into a public `Person` node.
- Internal CMS-user identifiers, names, email addresses, permissions, roles, and other account fields must
  not be exposed in public page payloads or JSON-LD.
- When a blog or media publication has a selected public lawyer author, `Article.author` references that
  lawyer's stable `Person @id`.
- When no lawyer author is selected, including when an internal CMS user is recorded for workflow
  attribution, `Article.author` references the global Actum `Organization`.
- `Article.publisher` always references the global Actum organization, regardless of whether the public
  author is a lawyer or Actum itself.
- An internal CMS-user attribution must not create a personal public byline. Public UI and JSON-LD must
  agree on corporate authorship in this case.
- The existing no-author diagnostic may remain an editorial-quality warning meaning that no named lawyer
  author was selected; it does not remove the corporate Actum author from the public graph.
- Public non-lawyer author profiles and identities are outside V1. They require a separate explicitly
  public data model and opt-in rather than reuse of authentication accounts.
- A resolved and visibly rendered `legalReviewerLawyerRef` is emitted as `WebPage.reviewedBy`, referencing
  the lawyer's stable public `Person @id`.
- A legal reviewer is not added to `Article.author`, `Article.contributor`, or `CreativeWork.editor` merely
  because they checked legal accuracy or completeness.
- An unresolved or non-visible legal reviewer is omitted with an advisory diagnostic under Decision 23.

## Decision 28: Explicit Media-Page Representation Modes

- Every `media_page` has an explicit required `representationMode` with exactly two V1 values:
  `actum_article` and `external_reference`.
- The backend must not infer the mode from `sourceUrl`, body length, populated sections, or other content.
- In `actum_article` mode:
  - the local `WebPage.mainEntity` references a page-owned `Article` identified as
    `{canonicalUrl}#article`;
  - the local article uses the authorship and publisher rules in Decision 27;
  - when an external `sourceUrl` is present, an external `CreativeWork` uses that absolute URL as its
    `@id` and is referenced from the local article through `about`;
  - `isBasedOn` is not inferred merely because the local article discusses the external work;
  - missing `sourceUrl` is an advisory warning and no anonymous external work is invented.
- In `external_reference` mode:
  - no page-owned local `Article` entity is created;
  - `WebPage.mainEntity` is the external `CreativeWork` whose `@id` and `url` are the required absolute
    `sourceUrl`;
  - the external work's publisher is an inline `Organization` named from `sourceName`; Actum must not be
    asserted as publisher or author of the external work;
  - the local `WebPage.publisher` continues to reference the global Actum organization;
  - a selected lawyer or internal CMS user must not be asserted as author of the external work.
- V1 uses the generic `CreativeWork` type for an external media item. A more specific external type may be
  introduced later only through an explicit sourced content-type field, not URL or title heuristics.
- Missing or invalid `sourceUrl` blocks publication in `external_reference` mode. It remains a warning in
  `actum_article` mode.
- Existing published snapshots are preserved. Existing drafts may remain temporarily unclassified, but
  their next publication is blocked until an editor explicitly selects a representation mode; migration
  must not guess it.

## Decision 29: Multiple Editorial Service-Tree Relations

- `blog_page`, `media_page`, `case_page`, and review records support the common CMS-owned
  `additionalServiceTreeRefs[]` contract in addition to their primary practice/service/problem line.
- There is no product-level limit on the number of additional lines. General API request-size and abuse
  protections may still apply and are not a semantic relationship limit.
- Every line is validated as a hierarchy: practice is required; service is optional but must belong to the
  practice; problem is optional but requires and must belong to the selected service.
- JSON-LD uses only the most specific selected entity from each line:
  - practice when the line ends at practice;
  - service when the line ends at service;
  - problem when the line ends at problem.
- The endpoint of the primary line and every valid additional line are resolved to their stable published
  `Service @id`, deduplicated by identifier, and emitted in deterministic order with the primary endpoint
  first and additional endpoints following saved order.
- For `BlogPosting`, local media `Article`, and case-study `Article`, all resolved endpoints are emitted
  through `Article.about`.
- For an external-reference media page, the local `WebPage.about` carries the resolved service endpoints;
  the external `CreativeWork` must not be made about Actum services without source evidence.
- For `Review`, the primary endpoint remains the sole `itemReviewed`. The primary and additional service
  endpoints may also be listed in `Review.about` together with the already accepted case and lawyer
  relations. Adding a topical chain does not create another rating value or another reviewed-item identity.
- Duplicate additional lines are invalid. A line duplicating the primary relation is redundant and produces
  a warning; graph-level deduplication still guarantees one reference per `Service @id`.
- An unresolved or unpublished optional additional endpoint is omitted with an advisory diagnostic. The
  backend must not replace it with a label or synthesize a `Service` identity.

## Decision 30: Editorial Publication And Modification Dates

- Editorial `publication_meta.publishedAt` is the visible first-publication/byline date and maps to
  `Article.datePublished`.
- A separate backend-owned read-only `contentModifiedAt` records the latest material change to an already
  published public article and maps to `Article.dateModified`.
- First publication leaves `contentModifiedAt` absent; the graph may omit `dateModified` rather than copy
  a technical snapshot timestamp or force it equal to `datePublished`.
- The backend updates `contentModifiedAt` only when a normalized digest of user-visible editorial content
  differs from the current published snapshot. The digest includes visible metadata, article body, images,
  public author/reviewer attribution, primary and additional topical relations, and type-specific case or
  media data.
- The digest excludes generated JSON-LD, dependency-only enrichment, snapshot/version identifiers,
  diagnostics, publication bookkeeping, and system timestamps.
- A technical republish or stale-dependency refresh with no visible-content change preserves
  `contentModifiedAt`.
- A rollback that changes the live visible content sets `contentModifiedAt` to the successful rollback
  publication time. A rollback to an identical visible digest preserves it.
- Changing the visible editorial `publishedAt` value after first publication is a material change and
  advances `contentModifiedAt`.
- Whenever `dateModified` is emitted in JSON-LD, the same `contentModifiedAt` value must be present in the
  public snapshot and visibly rendered on the page. Editors cannot set it manually.
- All emitted dates use ISO 8601 timestamps with an explicit timezone.

## Decision 31: Locale-Owned Editorial Dates

- Every localized editorial page is a separate `Article`/`BlogPosting` creative work and owns its own
  `publishedAt` and `contentModifiedAt` values.
- `Article.datePublished` and `Article.dateModified` are resolved from the current locale variant only.
  They are not inherited or synchronized from the primary Ukrainian publication.
- Creating a translation does not copy either publication date. An editor may explicitly choose the same
  visible `publishedAt` value in several locales, but the backend must not impose it.
- Publishing, materially editing, technically republishing, or rolling back one locale follows Decision 30
  independently and must not change any other locale's dates.
- A Russian or English creative work may reference the primary Ukrainian creative work through
  `translationOfWork` when that primary work is published. This relationship, rather than a shared date,
  expresses that the pages are translations of one work family.
- For every published Russian or English editorial translation, `translationOfWork` is required and points
  to the primary Ukrainian creative-work `@id`.
- The primary Ukrainian graph does not emit the inverse `workTranslation` list. Schema.org defines the
  properties as inverses, while published `hreflang` alternates provide reciprocal page discovery; a newly
  published or withdrawn translation therefore does not make the Ukrainian snapshot stale solely to update
  JSON-LD.
- On media pages, external `mediaPublishedAt` belongs only to the external `CreativeWork`. It must not be
  used as the local Actum `Article.datePublished` or local `WebPage` publication date.

## Implementation Status

The regional provider/office model, service hierarchy, price-to-service binding, reviews, cases, FAQ, and
global organization ownership, including lawyer employment and work-location semantics, are now
normative. Lawyer qualification-to-expertise mapping and intent-page service/offer semantics are also
normative. Validation severity, its effect on preview/publication, and localized lawyer-profile graph
ownership are now normative. Lawyer-license certification and education/degree identity semantics are now
normative. Public authorship and the non-public status of CMS user accounts are now normative.
Media-page representation modes and their distinct graph ownership are now normative.
Multiple service-tree relations and their `about` endpoint semantics are now normative.
Editorial `datePublished`/`dateModified` semantics are now normative.
Locale ownership of editorial dates is now normative.

The implementation matrix, exact payload/diagnostic contract, stale dependency rules, migrations, test
gates, controlled system backfill, and page-type staged rollout are defined in
`docs/json-ld-implementation-requirements-2026-08-03.md`. No product or rollout decisions remain open for
the first implementation.

Search-intent landing pages are specified separately in
`docs/intent-page-family-requirements-2026-07-30.md`. That document now defines the accepted family,
variant-binding, navigation, workbench, lifecycle, entity identity, and common `Service`/`Offer` graph
rules. Implementation must use that document together with the normative identifiers and provider rules
defined here.
