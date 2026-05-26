# Backend Implementation Requirements

This document records implementation requirements for the clean `CMS` backend, based on the reviewed
`notstrapitest` refactoring assessments for page authoring and page preview.

## Decision

The `notstrapitest` refactoring assessments are accepted as diagnostic input, not as a direct work order
to refactor the prototype.

The clean `CMS` project should carry forward the proven behavior and edge cases, but it should not port
the large `PageAuthoringService` and `PagePreviewService` as-is. The new backend should be designed with
the right boundaries from the start.

## Source Assessment

The reviewed assessments identified two prototype pressure points:

- `PageAuthoringService`: one large service owns authoring, context loading, response building,
  relations, impact analysis, persistence, optional module fallbacks, and all page-type branching.
- `PagePreviewService`: one large service owns all page preview flows, blueprint loading, generated
  content composition, route attachment, slug maps, listing-card projection, token resolution, and
  quality evaluation.

The diagnosis is accepted:

- both services are too broad;
- nullable universal context objects obscure which data is required for each page type;
- page-type branching is too concentrated;
- several pure rules and data projections should be isolated and tested;
- a large mechanical refactor risks losing business logic if it is done without contract tests.

## Primary Rule

Do not make the new `CMS` backend a cleaned-up copy of the prototype services.

Port behavior through explicit contracts, tests, and small domain modules. Use the prototype code as a
reference for proven scenarios and edge cases, not as the target structure.

## Backend Boundaries

The NestJS backend should separate these responsibilities:

- authoring state and editor-facing draft operations;
- preview payload assembly and quality-policy evaluation;
- publishing decisions, snapshot creation, rollback, and current snapshot selection;
- public snapshot API consumed by the Next.js frontend;
- route building, route registry, aliases, and diagnostics;
- regional inheritance and token resolution;
- catalog and ERP-owned read-only integration boundaries;
- operator readiness and release diagnostics.

No single service should own all page types, all persistence, all response DTO construction, and all
publishing or preview behavior at once.

## Typed Page Contexts

The backend should use explicit typed contexts per page type instead of one universal nullable context.

Required direction:

- use `pageType` or `templateCode` as a discriminator;
- represent contexts as discriminated TypeScript unions;
- make page-specific entities non-null in their own context;
- keep shared fields in a base context;
- avoid passing bags with many optional fields such as `practiceId?`, `serviceId?`, `problemId?`,
  `lawyerId?`, `caseId?`, and `articleId?` unless the caller truly supports all variants.

Example direction:

```typescript
type BasePageContext = {
  locale: LocaleContext;
  region: RegionContext | null;
  blueprint: PageBlueprintContext;
};

type PracticePageContext = BasePageContext & {
  pageType: 'practice_page';
  practice: PracticeContext;
};

type ServicePageContext = BasePageContext & {
  pageType: 'service_page';
  practice: PracticeContext;
  service: ServiceContext;
};

type CmsPageContext = PracticePageContext | ServicePageContext;
```

## Use Cases And Domain Services

Prefer small use-case handlers and domain services over one large service.

Good candidates for isolated modules:

- route building;
- route parsing;
- route lookup and alias diagnostics;
- section extraction and ordering rules;
- base/override JSON merge rules;
- regional token resolution;
- meta state construction;
- listing-card projection;
- slug map loading;
- authoring impact analysis;
- authoring relations;
- preview response assembly;
- snapshot payload assembly;
- quality-policy evaluation.

Use page-type-specific handlers for behavior that is genuinely page-specific. Use shared domain services
for behavior that repeats across page types.

Strategy-style dispatch is allowed, but it is not a goal by itself. Avoid building a hidden abstract
pipeline that becomes a new monolith through inheritance. Composition should be preferred when it keeps
the flow easier to read and test.

## Snapshot And Preview Contracts

The versioned snapshot and preview payloads are the main contracts between backend and frontend.

The backend should define and test these contracts before UI code depends on them. At minimum, the
contracts should account for:

- `schemaVersion`;
- `pageType`;
- `locale`;
- `region`;
- `route`;
- `canonicalRoute`;
- `seo`;
- `breadcrumbs`;
- `sections`;
- `generated`;
- `structuredData`;
- `quality`;
- `publishedAt` for published snapshots;
- source identifiers for diagnostics.

Use runtime validation for external-facing contracts where practical, for example with Zod schemas or an
equivalent explicit validator.

The first public payload assembler is a pure backend contract layer. It receives an already selected page
schema, exact published section-version payloads, and resolved runtime/read-model payloads, then returns
the complete public object intended for the Next.js frontend. It must not read draft authoring tables,
decide publishability, or fetch runtime directories by itself.

Runtime/read-model payloads are resolved from CMS database reference-data tables, not from live frontend
calls to ERP. The implementation should keep `reference-data` storage separate from `runtime-resolvers`
that project those records into public page payloads.

The first assembled payload shape includes:

- `schemaVersion`;
- `pageType`;
- `locale`;
- `route` and `canonicalRoute`;
- `seo`;
- `breadcrumbs`;
- ordered visual `sections`;
- `publishedAt`;
- source diagnostics that distinguish section-version content from runtime/read-model content;
- dependency refs for ERP/CMS reference objects that were actually used in runtime/read-model payloads.

Metadata sections such as `seo` are exposed through top-level metadata, not rendered as body sections.
Visual sections are ordered by backend page schema layout.

When a visible block combines CMS-authored content with runtime/read-model data, model it as one composite
section/slot in the page schema instead of two unrelated sibling sections. The backend assembles the
single public payload; the frontend renders the resolved contract.

## Section Authoring And Publication Units

The clean backend must model sections as independent authoring units, not only as anonymous JSON inside a
page draft.

Required direction:

- each section has its own draft and published versions;
- each section operation records actor and timestamp;
- section publish mode is schema-defined: `independent` or `with_page`;
- independent section publication creates a new published section version;
- changed `with_page` draft sections are published only as part of successful page publish;
- section publication must not make the public frontend assemble a page from live section tables;
- public runtime still reads a complete published page snapshot/public payload;
- successful page publish commits new `with_page` published section versions and the new page snapshot
  atomically;
- independent section publication creates a new page snapshot where only the changed section points to the
  new section version and unchanged sections stay pinned to their previous section versions;
- page-level validation runs before a new page snapshot becomes current;
- if critical page-level validation fails during `with_page` page publish, the attempt must not persist
  new `with_page` published section versions or activate a new public current snapshot;
- if critical page-level validation fails after an independent section publish triggers affected page
  snapshot rebuild, the already published independent section version remains in authoring history but the
  invalid rebuilt page snapshot must not become current;
- page rollback restores the exact historical set of section versions referenced by the selected snapshot;
- regional inherit, override, and append behavior is section-level or field-level where the section schema
  allows it;
- draft dependency tracking and stale-state diagnostics must cover inherited/regional authoring;
- upstream draft changes must not automatically persist derived child draft versions or child page draft
  copies;
- preview must recompose inherited draft results from the latest upstream drafts plus local child
  override/append state.

Section schemas must also support:

- field-level composition policy, so selected fields can inherit, override, or append independently where
  needed;
- deterministic content resolution, so schema plus composition plus source/local content produces the
  resolved JSON section content that will later be stored in the page snapshot payload;
- first persistence tables for pages, sections, section versions, page-section bindings, binding
  dependencies, page snapshots, snapshot section refs, and current snapshot pointers;
- explicit section locale, so global footer/menu sections are separate per locale instead of one
  multilingual JSON blob;
- current section version pointers for all sections, covering current published and latest draft versions;
- section validation diagnostics split into validation run history and current validation state;
- validation issue severity split into `critical` and `warning`, where critical issues block publish and
  warnings remain visible but non-blocking;
- a repository/service layer over those tables that handles SQL reads/writes and transaction boundaries
  without absorbing publish decisions, page-schema rules, or content resolution logic;
- global-owned and external-source-backed sections, including the price-section use case where base
  service prices come from one shared source and pages inherit, override allowed fields, or append allowed
  notes;
- price-section inheritance chain where regional service-tree pages inherit price values and price text
  from the current published base non-regional page price result, while base pages inherit from the shared
  global price source;
- first implemented price inheritance layer: generated `practice_page`, `service_page`, and `problem_page`
  schemas expose a page-owned `price` slot with `sourcePolicy = price_inheritance`; base non-regional
  pages bind that local price section to the locale `global_price` source, and regional generated pages
  bind their local price section to the base page's local price section;
- page publish/preview must resolve `source + local` price composition before assembling the public
  payload, and page snapshots must record both source and local section refs when both contributed to the
  resolved price block;
- shared fixed global sections such as footer/menu, where all pages inherit one published global section
  version and a publish event triggers affected page snapshot rebuilds instead of page-local section
  versions;
- patch-based affected snapshot rebuild for shared fixed footer/menu sections, preserving other current
  published section payloads and refs without reading page drafts or runtime read models;
- best-effort footer/menu rebuild with diagnostics/retry for failed pages, not all-or-nothing blocking;
- footer/menu rollback through a new draft copied from the old published version, followed by current
  publish validation, not by moving the current published pointer back to the old version;
- automatic affected snapshot rebuild for global price publish when pages use enabled inherit, append, or
  field-level inherited/appended price composition;
- price publish rebuild must preserve the current page snapshot and recompute only the price block from
  the new global published price plus current published local append/override deltas;
- whole-section price overrides and disabled optional price bindings must not be changed by global price
  publish;
- page-owned parent section publish must not automatically publish inherited child/regional pages;
- inherited child/regional pages should expose unapplied parent published changes and be updated through
  an explicit CMS action such as `Republish regional pages`;
- schema-defined inherit/override/append restrictions, so protected sections such as footer can remain
  inherit-only without a separate first-release parent/source lock policy;
- dependent draft policy, so price-like inherited/appended sections can require `draft_stale` review while
  footer/menu-like shared globals do not require page-by-page draft stale review;
- dependency metadata or equivalent diagnostics that show when inherited drafts require revalidation;
- layout placement policy, distinguishing fixed sections from editor-movable sections;
- layout slots or zones, including article/case pages where editor-added sections are allowed only between
  fixed starting and fixed ending sections.

The first concrete page schema registry must be code-defined in Nest, not editable database configuration.
Initial page types are `lawyers_page`, `lawyer_page`, and `contacts_page`. They are localized but not
regional in the first iteration, use required global-owned header/footer slots, required page-owned SEO,
and runtime/reference slots for lawyers listing/filter, lawyer profile, and contacts map data.

This preserves editor flexibility without breaking snapshot-first public rendering, rollback, cache
revalidation, route diagnostics, SEO validation, or release readiness.

When backend changes the current published page snapshot pointer, the publish/rebuild/rollback workflow
must also initiate public frontend revalidation for the affected Next.js routes or tags. If an HTML CDN is
introduced later, the same snapshot activation event must initiate CDN purge/revalidation for the affected
HTML cache entries. Failed revalidation must be recorded as an operational signal; it must not be hidden
as a successful publish-side effect.

## Porting Rules From notstrapitest

When taking behavior from `notstrapitest`:

- first identify the product behavior being preserved;
- write or port tests for that behavior before rewriting it;
- map prototype edge cases to the new module that owns them;
- move pure logic before moving persistence or transaction logic;
- keep transaction order unchanged until tests prove the new implementation;
- document behavior that is intentionally not carried forward.

The following prototype behaviors are especially important to preserve:

- page-owned public slugs;
- base and regional inheritance;
- regional token resolution and unresolved-token quality reporting;
- generated listing visibility and ordering;
- listing-card overrides from child pages;
- missing child page slug handling;
- route registry and alias diagnostics;
- preview quality evaluation;
- publish to durable snapshots;
- rollback by creating a new current snapshot from historical payload.

## Testing Requirements

Before implementing or porting a backend slice, create tests for the behavior being preserved.

Required test types:

- unit tests for pure rules such as JSON merge, section extraction, ordering, token resolution, and route
  building;
- contract tests for preview and published snapshot payload shapes;
- tests for independent section publication creating a complete page snapshot with pinned section
  versions;
- tests proving that failed page-level validation prevents public snapshot activation after a section
  publish;
- rollback tests proving that historical page snapshots restore their exact section version set;
- integration tests for authoring get/save on the MVP page types;
- integration tests for preview of the MVP page types;
- publish and rollback tests around current snapshot behavior;
- route registry and unresolved alias diagnostic tests.

For code ported from `notstrapitest`, tests should prove behavior rather than line-by-line similarity.
Golden fixtures are acceptable where they make the public contract safer.

## What Not To Carry Forward Literally

Do not use these prototype traits as targets:

- one `PageAuthoringService` that owns all page types and all authoring responsibilities;
- one `PagePreviewService` that owns all page types and all preview responsibilities;
- universal nullable contexts for every page type;
- optional dependencies scattered through business logic;
- line-count reduction as the primary success metric;
- wrapper services that only proxy another service without adding a stable contract, batching,
  projection, caching, or boundary clarity;
- frontend logic that reconstructs publish rules or reads draft authoring state.

## Initial Backend MVP

The first clean backend implementation should stay narrow:

- `services_root`;
- `practice_page`;
- `uk` and `ru`;
- base and regional page variants;
- authoring get/save for those page types;
- preview payload generation;
- quality-policy evaluation;
- publish to current snapshot;
- public snapshot lookup by route;
- basic route diagnostics.

Additional page types should be added after the first clean loop is working end to end with tests:

`authoring -> preview -> publish -> current snapshot -> Next.js public render`

Implementation note, 2026-05-17: `cms-back` now contains the first public snapshot lookup endpoint,
`GET /api/public/pages/by-route?route=/contacts`. It reads only `cms_page_current_snapshots` and
`cms_page_snapshots` by the normalized public route and returns public snapshot metadata plus the stored
public payload for Next.js rendering. It intentionally does not read draft section versions or authoring
tables.

Implementation note, 2026-05-18: `cms-back` now contains the first admin page-authoring slice:
`POST /api/admin/pages/bootstrap`, `GET /api/admin/pages/{pageId}/authoring`, and
`POST /api/admin/pages/{pageId}/sections/{slotKey}/draft`. The backend can create a page from the registered
page schema, connect page-owned sections and shared global sections, expose current authoring state, and save
drafts for page-owned sections. Runtime slots remain read-model slots and are not persisted as page-section
bindings.

Implementation note, 2026-05-21: `cms-back` now contains the first admin page workbench slice:
`GET /api/admin/page-workbench/tree` and `GET /api/admin/page-workbench/page-types/{pageType}`. This layer is
an editor-facing aggregator above page schemas, pages catalog, and page authoring state. It returns the left
tree and matrix-ready section/runtime cell summaries for `contacts_page` and `lawyers_page` without exposing
section content. `lawyer_page` is visible as a generated collection node and will get full generated matrix
support later.

Implementation note, 2026-05-21: `cms-back` now contains the first section editor read slice:
`GET /api/admin/pages/{pageId}/sections/{slotKey}/editor`. This endpoint opens one CMS section from the
workbench matrix and returns draft/published content, schema metadata, diagnostics, and backend-computed
action flags. The workbench matrix remains summary-only; full section content belongs to the section editor
payload.

Implementation note, 2026-05-26: the section editor read payload now exposes source-backed content layers
for inherited sections such as page `price`: `content.source`, `content.local`, and `content.resolved`.
The resolved layer is computed by the backend from section schema, binding composition, source versions,
and local versions. This keeps the CMS frontend from reimplementing inherit/override/append merging logic
and gives editors a direct view of inherited, local, and final section content.

Implementation note, 2026-05-21: `cms-back` now contains page-scoped section editor action endpoints:
`POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/draft`,
`POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/validate`, and
`POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/publish`. The CMS frontend can now operate by
`pageId + slotKey`; backend decides whether the slot is page-owned or independent/global, applies the
registered Nest page schema, and returns the reloaded editor payload. Independent/global editor payloads now
resolve `latest_draft_version_id` and `current_published_version_id` from `cms_section_current_versions`, so
shared sections edited outside a page binding still appear correctly in the page editor.

Implementation note, 2026-05-21: `cms-back` now contains page-scoped section history and rollback endpoints:
`GET /api/admin/pages/{pageId}/sections/{slotKey}/editor/history` and
`POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/rollback`. History returns draft/published/archive
section versions with audit metadata and current-version markers. Section rollback does not move the
published pointer backwards; it creates a new draft copied from the selected published section version. For
page-owned sections the page binding is pointed to that new rollback draft. For independent/global sections
the section latest-draft pointer is updated while published pages stay unchanged until a later publish or
affected snapshot rebuild.

Implementation note, 2026-05-22: `cms-back` workbench matrix rows now expose page-level `actions` and
`diagnostics`. The CMS frontend can show page buttons for open/bootstrap/preview/publish/rollback/current
snapshot from backend-computed flags and can display backend-computed publish blockers such as stale
sections, validation failures, empty required sections, or required independent sections that must be
published before page publish.

Implementation note, 2026-05-22: `cms-back` section editor now exposes backend-computed visibility actions
and `PATCH /api/admin/pages/{pageId}/sections/{slotKey}/editor/state`. The endpoint changes only the
page-section binding visibility (`enabled`/`disabled`), returns the reloaded editor payload, and does not
create section drafts or rewrite published section versions. Disabling is allowed only when the registered
page schema permits it for that slot.

Implementation note, 2026-05-22: `cms-back` page workbench now exposes
`GET /api/admin/page-workbench/pages/{pageId}/row` as a lightweight row refresh endpoint. After a section
editor action, CMS frontend can request this row and replace the matrix row with backend-computed statuses,
diagnostics, and action flags. Workbench cell actions now distinguish `canEnable` and `canDisable` for
section visibility controls.

Implementation note, 2026-05-22: `cms-back` page workbench now exposes page-level action endpoints:
`POST /api/admin/page-workbench/pages/{pageId}/preview`,
`POST /api/admin/page-workbench/pages/{pageId}/publish`, and
`POST /api/admin/page-workbench/pages/{pageId}/rollback`. These endpoints are thin UI-facing wrappers over
the existing page lifecycle service; they do not create a second publish path. Each successful action
returns the lifecycle result plus a fresh workbench row payload, so the CMS frontend can update the matrix
row after preview/publish/rollback without locally reconstructing publish rules.

Implementation note, 2026-05-22: `cms-back` page workbench now exposes page snapshot history for rollback
screens: `GET /api/admin/page-workbench/pages/{pageId}/snapshots` and
`GET /api/admin/page-workbench/pages/{pageId}/snapshots/{snapshotId}`. The list endpoint returns historical
snapshots, current-marker metadata, audit timestamps, and exact section version refs. The detail endpoint
returns the same metadata plus the stored public payload. The CMS frontend should use these endpoints to
show historical published states and pass the selected `snapshotId` as `sourceSnapshotId` to the existing
rollback action. Historical snapshots remain immutable; rollback creates a new current snapshot.

Implementation note, 2026-05-22: `cms-back` page workbench now exposes
`POST /api/admin/page-workbench/pages/bootstrap`. This endpoint wraps the existing page authoring bootstrap
workflow and returns the bootstrap result plus a fresh workbench row. It exists so the CMS frontend can
create a page directly from a not-created matrix row and immediately replace that row with backend-computed
state, without calling the lower-level authoring endpoint and then manually refreshing the matrix.

Implementation note, 2026-05-22: `cms-back` page workbench now exposes section editor wrappers:
`GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor`,
`PATCH /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/state`,
`POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/draft`,
`POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/validate`,
`POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/publish`,
`GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/history`, and
`POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/rollback`. These endpoints are
thin UI-facing wrappers over the existing page authoring section editor service. Each response returns the
operation result plus a fresh workbench row, so the CMS frontend can update both the opened section editor
and the matrix row after save, validate, publish, rollback, enable, or disable without reconstructing
backend rules or making a separate row-refresh request.

Implementation note, 2026-05-22: `cms-back` now registers the first generated service-tree page schemas:
`practice_page`, `service_page`, and `problem_page`. Their canonical base paths are built from ERP-owned
source slugs as `services/{practiceSlug}`, `services/{practiceSlug}/{serviceSlug}`, and
`services/{practiceSlug}/{serviceSlug}/{problemSlug}`. The page workbench matrix can now return generated
rows for visible practices, services, and problems from the CMS reference-data tables. Each row includes a
`sourceRecord` with reference ids, route params, computed `pagePath`/`publicPath`, parent refs, and source
diagnostics. If a generated row has a valid path and no critical source diagnostics, the frontend may call
the workbench generated bootstrap endpoint so the backend can reread the source and build the route.
Regional variants are now handled by the workbench matrix through row-level `region`/`regionSlug` and
optional bootstrap `regionId`. Richer section sets and generated `lawyer_page` rows remain follow-up work.

Implementation note, 2026-05-22: generated service-tree schemas now expose a first realistic section
scaffold for CMS UI work. Runtime/read-model slots can be paired with editable page-owned block sections
through `compositeGroupKey`, for example `practice_services_block` with `practice_services` and
`service_problems_block` with `service_problems`. The frontend may display those paired slots as one visual
block while the backend keeps CMS-authored draft content and runtime reference-data payloads separate.
Optional page-owned FAQ and consultation CTA sections are present for practice, service, and problem pages.
Price sections remain a separate follow-up because their global/base/regional inheritance behavior must be
implemented as a dedicated source-backed workflow, not as a simple page-owned block.

Implementation note, 2026-05-22: `cms-back` now contains the first page runtime resolver layer. During
preview and publish, page lifecycle asks `PageRuntimeResolverService` to fill missing runtime payloads for
service-tree pages. The first supported slots are `practice_services`, `practice_lawyers`,
`service_problems`, `service_lawyers`, and `problem_lawyers`. The resolver reads CMS reference-data tables,
uses source slugs from the page path, filters visible/public records, applies lawyer qualification score
rules (`score > 1`), and builds route-ready list items. Provided runtime payloads are still respected and
are not resolved twice, which preserves backward compatibility with manual preview/publish requests. Missing
visible sources or unroutable visible child items now fail as `PAGE_RUNTIME_RESOLUTION_FAILED` before an
invalid public snapshot is created.

Implementation note, 2026-05-23: `cms-back` now exposes the first direct global sections workbench API:
`GET /api/admin/global-sections`, `GET /api/admin/global-sections/{sectionKey}/editor`,
`POST /api/admin/global-sections/{sectionKey}/draft`,
`POST /api/admin/global-sections/{sectionKey}/validate`,
`POST /api/admin/global-sections/{sectionKey}/publish`,
`GET /api/admin/global-sections/{sectionKey}/history`, and
`POST /api/admin/global-sections/{sectionKey}/rollback`. The editable keys are `site_header`,
`site_footer`, and `global_price`. Global sections are locale-specific, reuse the existing
`SectionLifecycleService`, and publish with `rebuild_affected_snapshots` so affected page snapshots can be
refreshed without touching unrelated page-owned drafts. `global_price` is now available as the first shared
price block for generated practice/service/problem pages; the deeper base-page -> regional price
inheritance workflow remains a separate implementation step.

Implementation note, 2026-05-23: `cms-back` now exposes the first real generated service-tree workbench
API: `GET /api/admin/page-workbench/service-tree` and
`POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/bootstrap`. The service-tree
endpoint returns nested practice -> service -> problem nodes from CMS reference data, with existing page
state, diagnostics, and safe `canBootstrap`/`canOpen` actions. The generated bootstrap endpoint rereads the
selected source object and lets backend compute/validate the page route before creating or opening the CMS
page. This removes the need for the CMS frontend to assemble generated page paths by hand for
practice/service/problem pages.

Implementation note, 2026-05-23: generated practice/service/problem bootstrap now also creates backend-owned
minimal draft content for required page-owned sections when the CMS frontend sends an empty body. The first
defaults cover SEO title/description, intro title, and paired runtime block headings. Explicit
`initialSectionContents` from the frontend are shallow-merged over these defaults, so the UI can override a
field without taking responsibility for the whole generated payload. Optional page-owned FAQ/consultation
CTA slots are created as disabled bindings when no initial content is supplied, preventing empty optional
sections from blocking preview/publish until an editor deliberately enables and fills them.

Implementation note, 2026-05-23: generated practice/service/problem workbench matrices now include regional
variants. `GET /api/admin/page-workbench/page-types/{practice_page|service_page|problem_page}` returns the
base row plus regional rows for visible regions with valid `sourceSlug`. Regional rows keep the same
`sourceRecord` and add row-level `region`/`regionSlug`. The generated bootstrap endpoint accepts optional
`regionId`; backend rereads the region, builds the canonical regional route, and passes `regionSlug` into
page authoring. The service-tree endpoint remains non-regional so the left hierarchy stays practice ->
service -> problem without multiplying every node by regions.

Implementation note, 2026-05-24: workbench matrix rows now expose row-level `pagePath` and `publicPath`.
For existing pages these fields mirror the stored page route; for not-created generated rows they expose
the backend-computed route that will be used after bootstrap, including regional prefixes. Matrix summary
`errors` and `warnings` now count row-level page diagnostics, not only section cell diagnostics, so
not-created or source-blocked rows are reflected in the top-level counters shown to editors.

## Review Gate

Any change that ports prototype behavior into `CMS` should answer these questions:

- Which product behavior from `notstrapitest` is being preserved?
- Which tests prove that behavior?
- Which module owns the behavior in the new backend?
- Is the frontend reading a stable backend contract rather than draft internals?
- Does the change keep authoring, preview, publishing, and public runtime boundaries clear?
