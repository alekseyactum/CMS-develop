# Editorial Content Gap Audit - 2026-08-23

Normative product contract:

- [`editorial-content-specification-2026-08-23.md`](editorial-content-specification-2026-08-23.md)

Delivery order:

- [`editorial-content-implementation-plan-2026-08-23.md`](editorial-content-implementation-plan-2026-08-23.md)

## 1. Audit Scope

This audit compares the finalized editorial-content specification with repository state on the following
`origin/develop` revisions:

| Repository | Revision |
|---|---|
| `cms-back` | `ac51e050a209185beb69ce9d78f07d00a7506e73` |
| `cms-front` | `1d95afb057d083a9e587ce347bcaa5706b44e50a` |
| `site-front` | `e27c12b8e8995968a27845f70834f6b6bc4ed301` |

The audit is repository-based. It does not assert that every deployed Cloud Run service currently runs the
same revision. The dirty primary `cms-front` checkout was not used as evidence and was not modified.

## 2. Executive Conclusion

The existing implementation is a useful foundation, but the finalized editorial-content product is not
functionally complete.

The six page types, routes, basic section schemas, projections, collection resolver, JSON-LD builder, admin
navigation group, and public route shells already exist. However, several of those parts implement the older
June contract. The most important gaps are not visual polish: they are contract, validation, lifecycle,
privacy, and renderer gaps.

The current state can be summarized as follows:

| Surface | State | Conclusion |
|---|---|---|
| Page type and route registration | Foundation ready | All six types and their route families exist |
| Backend authoring contract | Partial and outdated | Cannot represent the finalized author, media, builder, and relation models |
| Backend lifecycle and projections | Partial | Publish/rollback projection hooks exist; collection refresh and late-V1 archive behavior do not |
| Backend validation | Partial and outdated | Basic checks exist; the closed block registry and finalized conditional rules do not |
| Backend JSON-LD | Partial | Main graph types exist; authorship and paginated collection semantics differ from the specification |
| CMS interface | Skeleton | List/workbench entry exists, but only Cases have a practical creation/translation flow |
| Public site | Route shell only | Routes resolve through the generic pipeline, but editorial detail and collection renderers are absent |

Therefore the correct implementation strategy remains contract convergence first, followed by one complete
Blog vertical slice. Building all three CMS interfaces before correcting the shared backend contract would
create rework.

## 3. Existing Foundation To Preserve

### Backend

- `blog_page`, `media_page`, `case_page`, `blog_collection_page`, `media_collection_page`, and
  `case_collection_page` are registered in `src/page-schemas/page-schema-registry.ts`.
- Editorial public route shapes and localized route families exist.
- The section registry includes `publication_meta`, `content_builder`, and `case_summary`.
- Published editorial projection tables and extraction/rebuild services exist under
  `src/editorial-projections/`.
- Page publish and rollback already trigger editorial projection rebuilding.
- A runtime collection resolver reads published projection data.
- The admin editorial facade supports listing and creation at a basic level.
- `src/structured-data/editorial-graph.builder.ts` already contains the main editorial JSON-LD graph
  families.
- Public sitemap handling recognizes editorial routes.
- The ordinary page/section/draft/snapshot lifecycle remains suitable as the source of truth.

### CMS frontend

- The backend-driven navigation can open Blog, Media, and Cases.
- `app/[locale]/admin/publications/[kind]/page.js` and the editorial publication list components exist.
- Rows expose status, update, workbench editor, preview, and publication actions.
- Generic section editing and the existing service-tree reference UI can be reused where their contracts
  match the finalized model.

### Public site

- Localized collection and detail route files exist for all three kinds.
- The routes use the shared server-side public page resolver.
- The common JSON-LD script output mechanism can render a graph supplied by the backend.
- Existing media and generic public-section infrastructure can be reused by dedicated editorial renderers.

## 4. Backend Contract Gaps

### 4.1 `publication_meta`

Current implementation:

- common fields include title, excerpt, cover media ID, optional publication date, featured state, and one
  primary practice/service/problem reference;
- Blog and Media use the old single-author discriminator (`authorType`) and one lawyer or CMS-user author;
- Case supports a primary lawyer plus coauthor references;
- additional service-tree relations use an older primary-plus-additions representation.

Required changes:

- add required cover alt text whenever a cover is present;
- enforce the public publication date according to the finalized lifecycle rules;
- replace the single Blog/Media author discriminator with an ordered list of zero to five lawyer authors;
- keep Actum as the public fallback when no Blog/Media lawyer author is selected;
- support the optional reviewer independently of authors;
- keep one primary Case lawyer and limit the total Case lawyer list to five;
- implement the explicit Media representation modes and require `mediaPublishedAt` for external references;
- normalize service-tree relations into an unlimited ordered relation set with at most one primary relation;
- prevent internal CMS-user identity objects from entering the public editorial contract.

Compatibility must be deliberate. Existing section JSON must remain readable during rollout, but newly saved
drafts must use the finalized shape. An old-shape reader is preferable to silently rewriting published data.

### 4.2 `content_builder`

Current implementation stores an optional list and validates only that each row is an object with a nonempty
`blockType`.

Missing behavior:

- stable `blockId` values;
- the closed V1 registry: heading, paragraph, list, quote, image, table, and callout;
- typed field validation for every block kind;
- H2/H3/H4 validation and `includeInToc`;
- `tocEnabled` at section level;
- deterministic heading anchors;
- image alt validation;
- safe table structure validation;
- per-kind empty-content warnings;
- rejection of unknown block types.

This is a blocking shared-contract gap. The generic list-of-JSON implementation is not an acceptable public
or CMS contract for the finalized editor.

### 4.3 Detail-page section structure

The detail schemas do not yet include:

- the optional fixed `editorial_cta` section;
- the agreed runtime related-service hierarchy section;
- all finalized ordering rules shared by preview, published snapshots, and public rendering.

The section order must be owned by the page schema, not reconstructed independently by the public frontend.

### 4.4 Localization

The generic page infrastructure supports locales, but the dedicated editorial facade currently exposes a
translation workflow only for Cases. It also copies `publishedAt` while creating a translation, contrary to
the finalized independent-localization date semantics.

Required changes:

- provide one locale-family workflow for Blog, Media, and Cases;
- require an existing published Ukrainian page before publishing Russian or English;
- copy only the fields allowed by the specification;
- do not copy locale-specific title, slug, excerpt, body, SEO, cover alt, or publication date as live shared
  values;
- return stable locale-switch links for existing translations.

### 4.5 Admin list facade

The backend list supports kind, locale, status, text query, limit, and offset. It lacks the full agreed sort
and diagnostic/stale filtering contract. The API should own deterministic ordering and pagination metadata;
the CMS must not sort only the current client-side page.

### 4.6 Collection projections and automatic refresh

Projection rebuilding on detail publish and rollback already exists. The remaining gaps are:

- no automatic technical refresh/republication of affected collection snapshots was found;
- the runtime resolver loads up to 200 items instead of serving 12-item pages;
- it does not return `page`, `pageSize`, `totalItems`, and `totalPages`;
- it does not reject out-of-range pages with 404;
- cards do not use the finalized nested cover contract with alt text;
- Case cards lack the finalized result label;
- contributor summaries do not implement the ordered author rules;
- internal CMS-user author summaries can currently reach the public collection payload.

Collection refresh must be a technical consequence of a detail lifecycle event. It must not create a new
editorial version or require an editor to republish the collection manually.

### 4.7 Archive and unpublish

Generic page status infrastructure contains an archived state, but the agreed editorial unpublish/archive,
restore, public 404/410 behavior, projection removal, collection refresh, and sitemap effects are not exposed
as a complete editorial lifecycle. This remains the intentionally late V1 phase.

## 5. Validation Gaps

The current validator already provides useful basic checks for publication metadata, relations, duplicate
references, Case summary content, and some warnings. It does not yet enforce the finalized error/warning
boundary.

Blocking gaps:

- closed and typed content block registry;
- stable and unique block IDs;
- author count and ordering rules;
- Media mode-specific required fields, including external publication date;
- cover alt when cover exists;
- one-primary service-tree constraint across all selected chains;
- locale publication gate consistently across all three kinds;
- public privacy constraints.

Warning gaps:

- zero service-tree relations;
- no meaningful content blocks;
- kind-specific recommended fields and content diagnostics;
- optional TOC quality warnings without turning absence of body content into a blocking error.

The user decision that an empty content builder is a warning, not a blocking error, must be preserved.
External-reference Media with no local builder content must not receive that warning.

## 6. JSON-LD Gaps

The existing builder is a strong starting point. It already models BlogPosting, Article, external-reference
WebPage, Case-related Thing, collection ItemList, Actum fallback, and service-tree `about` relations.

Required corrections:

- emit all selected Blog/Media lawyer authors as one ordered `author` array;
- emit the primary and coauthor Case lawyers in the agreed ordered `author` array rather than placing
  coauthors only in `contributor`;
- keep reviewer independent from authorship;
- derive the graph only from the normalized published projection/public contract;
- emit the current collection page's 12 items with global positions;
- make every pagination page self-canonical;
- keep pagination URLs out of sitemap XML;
- never expose internal CMS-user identity as a public Person unless a separate public-author product model is
  introduced later.

## 7. CMS Frontend Gaps

The current editorial screen is an administrative skeleton, not the finalized editor.

High-priority gaps:

- creation UI is effectively limited to Cases;
- translation creation and locale controls are effectively limited to Cases;
- a utility hardcodes `case_page` for the workbench route;
- the list always requests a fixed first page and lacks the agreed search, filters, sorts, and 50-item
  pagination UI;
- no specialized typed content-block builder exists;
- no drag/reorder/add/delete block workflow exists for the closed V1 registry;
- no TOC controls or heading inclusion controls exist;
- no finalized author/reviewer picker exists;
- no explicit Media mode editor exists;
- no finalized multiple service-tree chain selector exists;
- no collection header/settings editor entry exists;
- no dedicated detail route and three-column editorial workspace matching the agreed CMS interaction model
  exists.

Generic section-editor JSON controls can remain as diagnostics/fallback tooling, but they must not be the
primary authoring experience for `content_builder`.

## 8. Public Site Gaps

All route files exist, but the route presence currently overstates implementation readiness. The public site
does not contain dedicated renderers for:

- publication metadata and contributor presentation;
- Media representation modes and source attribution;
- Case summary;
- typed content blocks;
- generated table of contents;
- fixed editorial CTA;
- related service-tree hierarchy;
- editorial collection header;
- editorial collection cards;
- 12-item SSR pagination.

The generic public route pipeline can fetch and expose page payloads, and the generic JSON-LD output works.
However, without the dedicated section renderers these routes are only transport shells.

The editorial route files also do not yet provide the complete dynamic Next metadata/canonical behavior
required by the specification.

## 9. Priority Order

### P0 - Shared contract and public safety

1. Finalize backend types for publication metadata, authors, reviewer, Media modes, service-tree relations,
   cover alt, and the typed block registry.
2. Add compatibility readers for existing old-shape drafts/snapshots without emitting internal CMS-user data
   publicly.
3. Implement the finalized validation boundary and tests.
4. Normalize projection extraction and the public DTO.
5. Correct JSON-LD authorship and privacy behavior.

### P1 - Complete Blog vertical slice

1. Backend Blog creation, localization, authoring, preview, publish, and projection behavior.
2. CMS Blog list/create/locale controls and typed block editor.
3. Public Blog detail renderer and metadata.
4. Blog collection header, runtime cards, pagination, and automatic refresh.
5. End-to-end preview/publish/rollback checks.

### P2 - Media extension

Add local Actum article and external-reference modes, source attribution, conditional validation, CMS controls,
public rendering, and JSON-LD.

### P3 - Case extension

Add Case lawyer ordering, optional ERP relation, Case summary, CMS controls, public rendering, and Case JSON-LD.

### P4 - Cross-kind collection hardening

Complete automatic technical refresh, pagination edge cases, canonical rules, sitemap behavior, and card
contract consistency across all three kinds.

### P5 - Archive/unpublish

Implement the agreed late-V1 lifecycle only after all three publication kinds pass normal publish and
rollback acceptance.

## 10. Recommended Next Implementation Slice

The next safe slice is Phase 1 common backend convergence, not a frontend page.

Deliver together:

1. finalized TypeScript DTOs and normalized public contract;
2. finalized page-schema fields;
3. compatibility parsing for old author and relation shapes;
4. the closed typed block registry with validation;
5. author/reviewer and service-tree validation;
6. projection extractor updates;
7. JSON-LD author/privacy corrections;
8. focused unit and integration tests;
9. updated API examples for both frontend teams.

Exit criteria for that slice:

- one backend contract can represent every finalized Blog, Media, and Case field;
- no public endpoint exposes internal CMS-user author identity;
- invalid block kinds and invalid per-kind fields are rejected;
- empty content remains a warning under the agreed rules;
- old published data remains readable;
- no CMS or public frontend is forced to depend on the superseded June shape.

Only after this contract is stable should the Blog CMS and public renderers be implemented as the first full
vertical slice.
