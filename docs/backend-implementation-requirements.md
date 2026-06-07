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
  local content;
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
- layout-level global data such as header/footer/contact settings, where public frontend reads a separate
  layout payload instead of receiving those blocks inside every page snapshot;
- first layout/global contracts: `site_header`, `site_footer_practices`, `site_footer`, and
  `site_contact_settings`, as refined in `docs/site-layout-and-header-requirements.md` and
  `docs/site-footer-section-workbench.md`;
- layout revalidation for header/footer/contact settings, preserving page snapshots and page-owned drafts;
- best-effort layout rebuild/revalidation diagnostics for failed layout refreshes, not all-or-nothing
  page publication blocking;
- footer/menu rollback through a new draft copied from the old published version, followed by current
  publish validation, not by moving the current published pointer back to the old version;
- automatic affected snapshot rebuild for global price publish when pages use enabled inherit, append, or
  field-level inherited/appended price composition;
- price publish rebuild must preserve the current page snapshot and recompute only the price block from
  the new global published price plus current published local append/override deltas;
- global price editor requirements are fixed in `docs/global-price-section-workbench.md`: the persisted
  editable content is `{ items }`, the read-only localized section header comes from backend code registry,
  save returns `saved: true | false` with diagnostics, history exposes computed version roles/actions, and
  publish response is the source of affected snapshot rebuild results;
- `latest_draft` preview may use latest draft layers, but `published` preview and public snapshot creation
  must use only current published source/local versions;
- whole-section price overrides and disabled optional price bindings must not be changed by global price
  publish;
- page-owned parent section publish must not automatically publish inherited child/regional pages;
- inherited child/regional pages should expose unapplied parent published changes and be updated through
  an explicit CMS action such as `Republish regional pages`;
- schema-defined inherit/override/append restrictions, so source-backed page sections can remain
  inherit-only where needed without a separate first-release parent/source lock policy;
- dependent draft policy, so price-like inherited/appended sections can require `draft_stale` review while
  layout globals such as header/footer do not require page-by-page draft stale review;
- dependency metadata or equivalent diagnostics that show when inherited drafts require revalidation;
- layout placement policy, distinguishing fixed sections from editor-movable sections;
- layout slots or zones, including article/case pages where editor-added sections are allowed only between
  fixed starting and fixed ending sections.

The first concrete page schema registry must be code-defined in Nest, not editable database configuration.
Initial page types include `practice_collection_page`, `practice_page`, `service_page`, `problem_page`,
`lawyers_page`, `lawyer_page`, and `contacts_page`. Service-tree page types are localized and regional;
lawyers and contacts are localized but not regional in the first iteration. Page schemas contain
page-owned content sections, required page-owned SEO, and explicit runtime/reference slots where needed.
Header, footer, footer practices, and contact settings are layout-level data read through the layout
payload and must not be copied into every page schema or page snapshot.

This preserves editor flexibility without breaking snapshot-first public rendering, rollback, cache
revalidation, route diagnostics, SEO validation, or release readiness.

When backend changes the current published page snapshot pointer, the publish/rebuild/rollback workflow
must also initiate public frontend revalidation for the affected Next.js routes or tags. If an HTML CDN is
introduced later, the same snapshot activation event must initiate CDN purge/revalidation for the affected
HTML cache entries. Failed revalidation must be recorded as an operational signal; it must not be hidden
as a successful publish-side effect.

## Admin Navigation Contract

The backend should expose one lightweight admin navigation endpoint for the CMS sidebar:

```text
GET /api/admin/navigation?locale=uk
GET /api/admin/navigation?locale=uk&includeIndicators=true
```

This endpoint is a navigation and prioritization contract. It must not replace page workbench, section
editor, global section, reference data, publication, or user-management APIs.

The response must include `generatedAt`, an ISO timestamp of when the navigation tree and indicators were
assembled. Frontend should use this as freshness metadata for the sidebar/statistical addon; it is not a
cache key and not a domain version.

Required top-level groups:

- `practices`: a clickable root group for the public services/practice collection page. The group itself
  opens `practice_collection_page`; its `items` contain only the full non-regional practice -> service ->
  problem tree. Practice/service/problem child nodes open the matching generated page workbench. The
  collection page must not be duplicated as a first child item of its own group. Regional variants are not
  expanded in the sidebar and belong to the selected workbench screen.
- `lawyer_pages`: generated public lawyer profile pages for visible lawyers. This is not the lawyers
  reference-data editor; it opens the page/workbench area for individual lawyer public pages.
- `publications`: publication collections such as articles, cases, and media mentions.
- `global_sections`: the shared layout/global area. It contains versioned global sections
  `site_header`, `site_footer_practices`, `site_footer`, `global_price`, plus the non-versioned
  `site_contact_settings` settings item.
- `reference_data`: ERP/CMS dictionaries. The service/practice/problem dictionaries are exposed in the
  sidebar as one `service_hierarchy` item, not as separate top-level `practices`, `services`, and
  `problems` items. Other regular dictionary items are lawyers, regions, offices, and reviews.
  Competencies stay internal/read-model data and are not a regular standalone editor item.
- `single_pages`: home, about, career, lawyer license, and contacts.
- `users`: CMS users list, filtered by future access permissions. Roles/permissions are not shown as a
  separate item until that workflow is implemented.

Every menu item should contain a typed `target` that tells the frontend what to open. The frontend should
not infer target behavior from titles or hardcoded sidebar lists.

The endpoint should return only nodes that can be opened by the current frontend/backend implementation.
Do not return disabled "planned" nodes in the runtime menu. Future target groups may remain documented but
should appear in the API only when they have a real opening target.

`indicators` should be controlled by `includeIndicators=true`. Without this flag, the backend may return
only the navigation tree. The first backend slice does not need server-side menu filters; the frontend may
filter locally from the aggregate indicators if needed.

The menu should support a compact statistical addon through aggregate `indicators`. For the `practices`
page tree, indicators must be split into semantic scopes:

- `own`: the base non-regional page of this node. For the `practices` group itself this is the public
  services/practice collection page; for a practice/service/problem item this is the matching Ukraine-wide
  generated page.
- `regional`: regional inheritors of the same page node only.
- `children`: child practice/service/problem descendants below this node, including their regional
  inheritors where relevant. If the node has no child page nodes, this scope must be `null`.

For menu purposes, draft changes and stale inherited dependencies can be combined into an editor-facing
`attention` aggregate, but the underlying domain model must keep them separate because they have different
publish/review workflows. The navigation API must not expose a separate `requiresReview` axis for the
sidebar; `attention.own.stale` is calculated as `draftChanges OR staleDependencies`.
Publication coverage should be exposed as lightweight published/total counters where meaningful.

Practice/service/problem publication coverage must be split into:

- `own`: whether the base non-regional page itself is published;
- `regional`: published/total regional variants of the same node only;
- `children`: published/total child service/problem pages below this node, including their regional
  variants where relevant, or `null` when the node has no child page nodes.

The object tree itself remains non-regional: practice -> service -> problem. Regional pages are shown
inside the selected workbench screen, not as separate sidebar nodes. The menu may display regional and
children scopes separately or combine them visually in brackets, but the API must keep them separate.

Regional totals must count only expected regional pages. A regional page is expected only when the region is
visible and the node is applicable for that region through the region competence model. Disabled regions and
non-applicable region/node pairs must not increase `regional.totalCount` and must not be treated as missing
pages. Children totals must likewise count only visible/applicable ERP objects and expected regional
inheritors.

The navigation API should avoid derived fields that the current CMS menu does not use. For the `practices`
tree it should not return `status`, `availability`, `notCreatedCount`, or `notPublishedCount`. The frontend
can derive row color/priority from errors, warnings, and attention values. `requiredPermission` stays useful
for debugging and permission-aware UI, even though the backend filters groups by permissions.

Global section indicators must expose only real publish impact. For `global_price`, affected pages are
pages whose current public snapshot would change because they inherit or append from the global source.
Fully overridden or disabled price sections should not be counted. For layout-level globals such as
`site_header`, `site_footer_practices`, and `site_footer`, page snapshot impact should be empty/zero
because public pages read them through the layout payload, not through page snapshot refs.
The first implementation returns this as `publishImpact.affectedPages.count` and
`publishImpact.affectedBindings.count`; it is a menu summary, not a detailed rebuild plan.

Reference-data menu indicators should stay simple: dictionary-level validation errors/warnings and
visible/total record counts. Do not add a separate reference-data `attention` wrapper in the first slice.
For `service_hierarchy`, indicators use `own` and `children` scopes:

- root `service_hierarchy`: `own` means practices; `children` means services and problems;
- practice node: `own` means this practice; `children` means its services and their problems;
- service node: `own` means this service; `children` means its problems.

Reference-data hierarchy indicators do not use `regional`, because this is an ERP/CMS dictionary tree, not a
page regional-inheritance tree.
Single pages should expose own diagnostics, own attention, and own publication state, with regional
coverage only if the page type becomes regional. Lawyer pages should use generated-page indicators driven
by visible lawyer records, without service-tree descendants. Users should expose active/total counts in the
first slice.

Current implementation coverage:

- `practices` returns the clickable services collection group and the full practice/service/problem tree
  with page indicators. This is the source for the CMS service hierarchy in the sidebar;
- `lawyer_pages` returns generated lawyer profile page coverage based on visible lawyers;
- `single_pages` returns indicators for currently implemented standalone page types;
- `global_sections` returns draft/published status for versioned global sections, layout/settings
  diagnostics for `site_contact_settings`, and lightweight publish impact only where the item can affect
  page snapshots;
- `reference_data` returns aggregate diagnostics plus visible/total counts. It includes one full
  `service_hierarchy` tree down to service nodes; problem nodes are not shown in the sidebar and are loaded
  in the central screen after selecting a service;
- `users` returns active/total counts.

The navigation response should return the complete practice/service/problem tree in the first release slice
because current expected volumes are small enough and a full tree keeps the UI simple. The response must
remain summary-only: no full section content, no full validation history, no snapshot history, and no
authoring payloads.

Navigation indicators are dynamic and may become stale while an editor works. Frontend must refresh
`/api/admin/navigation?locale=<locale>&includeIndicators=true` after successful actions that can change
page, section, publication, reference-data, media, global-section, settings, or user indicators. A rare
background refresh, for example every 60-120 seconds while the CMS tab is active, is acceptable. The
frontend must not call the indicator endpoint on every render, hover, or field keystroke. Realtime
push/SSE/WebSocket updates are intentionally out of the first slice. When refreshing, the frontend should
preserve expanded menu keys, selected node, and scroll position.

In the `practices` group, the group itself is the `practice_collection_page` root. The complete
practice/service/problem tree is returned directly in `group.items`. The collection page and practice nodes
must not be rendered as separate sibling roots, and the collection page must not appear inside its own
children collection.

Generated practice/service/problem menu nodes should open a source-scoped page workbench matrix through a
safe `GET` endpoint:

```text
GET /api/admin/page-workbench/page-types/<pageType>?locale=<locale>&sourceId=<cms-source-id>
```

The response shape is the normal `PageWorkbenchMatrixResponse`, but `rows` are limited to the selected
base non-regional page and its expected regional variants. This endpoint must not create authoring state by
itself. Creating a missing generated page remains an explicit editor action through the generated-source
bootstrap/open endpoints.

The central workbench screen opened from the service tree must be driven by this matrix response, not by
reference-data list endpoints. Reference-data APIs remain the editor for ERP/CMS dictionary objects; the
page workbench owns page rows, section/runtime cells, diagnostics, actions, and exact workbench endpoints.
Generated `open` / `open-editor` endpoints are explicit quick-edit actions, not the default sidebar click.

`PageWorkbenchMatrixResponse` must include a top-level `scope` object. For normal page-type screens:
`scope.kind = "page_type"` and `scope.source = null`. For source-scoped practice/service/problem screens:
`scope.kind = "generated_source"` and `scope.source` contains the selected source registry record
(`id`, `resource`, `title`, `sourceSlug`, route fields, parent refs, diagnostics). Frontend screens must
use this object as the selected sidebar context instead of inferring the selected entity from the first row.

Workbench matrix rows and cells must expose backend-owned action endpoints in addition to boolean action
flags. The frontend uses `actions` to decide what control can be shown and `endpoints` to know what URL to
call. UI components must not manually assemble workbench URLs from `pageId`, `slotKey`, `sourceId`, or
`regionId`.

Row endpoint contract:

- `row.endpoints.refresh`: `GET /api/admin/page-workbench/pages/{pageId}/row`, only for created pages;
- `row.endpoints.bootstrap`: page creation endpoint for not-created rows; generated regional rows include
  a default `body.regionId`;
- `row.endpoints.preview`: page preview endpoint when `actions.canPreview`;
- `row.endpoints.publish`: page publish endpoint when `actions.canPublish`;
- `row.endpoints.rollback`: page rollback endpoint when `actions.canRollback`;
- `row.endpoints.snapshots`: snapshot history endpoint for created pages;
- `row.endpoints.currentSnapshot`: current snapshot detail endpoint when a current snapshot exists.

Cell endpoint contract:

- `cell.endpoints.editor`: section editor read endpoint when the section can be opened;
- `cell.endpoints.history`: section history endpoint when history is available;
- `cell.endpoints.updateState`: section enable/disable endpoint when visibility can change;
- `cell.endpoints.saveDraft`: section draft save endpoint when draft saving is allowed;
- `cell.endpoints.validateDraft`: section draft validation endpoint when a draft exists;
- `cell.endpoints.publishDraft`: independent section publish endpoint when allowed;
- `cell.endpoints.rollback`: section rollback endpoint when history is available.

Unavailable actions must have `null` endpoints, not guessed or disabled-looking URLs. Runtime cells may stay
without editor endpoints until a separate runtime detail API is introduced.

Reference-data list/detail endpoints remain dictionary endpoints, not the source of the CMS sidebar. They
may still expose nested lightweight relation summaries for convenience. For example, a practice can return
`children.services[]`, and those service summaries can return `children.problems[]`. This helps dictionary
screens show dependencies, but navigation should still be built from `/api/admin/navigation`.

Reference list endpoints such as `/api/admin/reference/practices`, `/api/admin/reference/services`, and
`/api/admin/reference/problems` are flat dictionary management APIs. They must not be used as the source
for the CMS sidebar hierarchy. Use them only after opening the `reference_data` group or after selecting a
`service_hierarchy` context. The hierarchy click endpoints are:

```text
GET /api/admin/reference/practices
GET /api/admin/reference/services?parentPracticeId=<cms-practice-id>
GET /api/admin/reference/problems?parentServiceId=<cms-service-id>
```

`parentPracticeId` and `parentServiceId` use CMS record IDs, not ERP external IDs. `externalId` remains in
the `source` object for display and debugging.

The `service_hierarchy` sidebar tree must be returned eagerly in the first slice: all practices and their
services are returned in one navigation response. Problems are intentionally not rendered as sidebar nodes.
Objects with `show_on_site = false` are still shown in the dictionary hierarchy; `flags.showOnSite` tells
the frontend how to style them. `records.visibleCount` counts `show_on_site = true`, while
`records.totalCount` counts all records. If a disabled parent has enabled children, keep the children
visible and report a warning rather than an error.

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

- `practice_collection_page` (clean CMS replacement for prototype `services_root`);
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

Implementation note, 2026-05-26: `PageLifecycleService` contract tests now cover inherited price
composition across latest-draft preview, published preview, page publish snapshot refs, and regional
base-page -> regional-page price source chains. Published preview intentionally ignores newer draft layers;
only latest-draft preview may use them.

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

Implementation note, 2026-05-22/30: `cms-back` now registers the first generated service-tree page
schemas: `practice_collection_page`, `practice_page`, `service_page`, and `problem_page`.
`practice_collection_page` is the public services/root collection page. It uses the canonical base path
`services`, has no `practiceId`, and can be regional. Practice/service/problem canonical base paths are
built from ERP-owned source slugs as `services/{practiceSlug}`,
`services/{practiceSlug}/{serviceSlug}`, and `services/{practiceSlug}/{serviceSlug}/{problemSlug}`. The
page workbench matrix can now return generated rows for the services collection, visible practices,
services, and problems from the CMS reference-data tables. Each row includes a `sourceRecord` with
reference ids, route params, computed `pagePath`/`publicPath`, parent refs, and source diagnostics. If a
generated row has a valid path and no critical source diagnostics, the frontend may call the workbench
generated bootstrap endpoint so the backend can reread the source and build the route. Regional variants
are now handled by the workbench matrix through row-level `region`/`regionSlug` and optional bootstrap
`regionId`. Richer generated `lawyer_page` rows remain follow-up work.

Implementation note, 2026-05-22: generated service-tree schemas now expose a first realistic section
scaffold for CMS UI work. Runtime/read-model slots can be paired with editable page-owned block sections
through `compositeGroupKey`, for example `practice_services_block` with `practice_services` and
`service_problems_block` with `service_problems`. The frontend may display those paired slots as one visual
block while the backend keeps CMS-authored draft content and runtime reference-data payloads separate.
Optional page-owned FAQ and consultation CTA sections are present for practice, service, and problem pages.
Price sections are modeled as source-backed page-owned sections: base generated pages inherit from
`global_price`, while regional generated pages inherit from the matching base page price section.

Implementation note, 2026-06-04: service-tree page schemas were aligned with the first site designs.
`breadcrumbs` are not CMS authoring sections and must not appear as editable page slots; they are generated
runtime/public payload metadata from route/page context. `practice_collection_page` keeps only an editable
`practice_collection_intro` hero slot and a runtime `practice_collection` list; it does not include the
standard service-hierarchy lead form in the first design slice. `practice_page` now has the following
backend scaffold:

- `seo`;
- `practice_intro` hero, including optional `ctaLabel` and `ctaTarget`;
- `practice_services_block` + runtime `practice_services`;
- optional page-owned content slots `practice_intro_text`, `practice_actions`, `practice_team_cta`,
  and `practice_optional_text`;
- runtime placeholders `practice_cases` and `practice_reviews`;
- inherited `price`;
- optional `practice_faq`;
- `practice_lawyers_block` + runtime `practice_lawyers`;
- optional page-owned `lead_questionnaire`;
- runtime `lead_capture`.

`lead_capture` is a fixed backend/runtime contract for the service hierarchy pages, not a global section
and not an editable page-owned section. It gives the frontend a stable form component context. The optional
`lead_questionnaire` stores page-specific questions and can be inherited/overridden/appended regionally as
a normal page-owned section. The same `lead_questionnaire` + `lead_capture` tail is available on
`practice_page`, `service_page`, and `problem_page`; detailed service/problem content structure remains a
separate design pass.

Approved direction, 2026-06-05: `problem_page` structure is approved conceptually from the current page
design, but must not be expanded in backend code until the exact implementation slice for service/problem
pages starts. Header/footer and breadcrumbs stay outside the editable page schema. Breadcrumbs and the
small route/context navigation under the hero are derived from route/reference data, not from editable
page sections.

`problem_page` should be modeled as a fixed service-hierarchy page with these logical areas:

- `seo`: page-owned metadata section.
- `problem_intro`: required page-owned hero section with title, short lead/subtitle, optional CTA label,
  and optional CTA target. Visual background and layout are frontend concerns.
- `problem_context_navigation`: runtime/read-model area derived from the page route and parent
  practice/service/problem references. It is read-only for the editor and is not stored as page content.
- `problem_guidance`: page-owned structured content section for the main unique problem narrative. It
  contains an ordered list of internal blocks, for example `advice_cards` and `accent_text`. This avoids
  hard-coding three or more design-specific advice slots before we know whether future problem pages need
  the same count and order. If the editor later needs independent versioning per guidance block, this can
  be split into several page-owned sections.
- `problem_team_cta`: optional page-owned CTA/support section. If a lawyer card is shown, the card data
  should be resolved from the lawyers read model, while the section stores only CMS text/settings.
- `problem_cases`: runtime/read-model list of cases for the current problem/service/practice context.
- `problem_reviews`: runtime/read-model list of reviews for the current problem/service/practice context.
- `price`: inherited `global_price` page-owned section using the already defined inherit/append/override
  price model.
- `problem_faq`: optional page-owned FAQ section.
- `problem_lawyers_block` + `problem_lawyers`: editable block title/lead paired with runtime lawyer list.
- optional `lead_questionnaire`: page-specific questionnaire before/in the lead form.
- runtime `lead_capture`: standard service-hierarchy lead form contract.

Implementation sequencing decision, 2026-06-05: do not implement the full `problem_page` structure as the
next code slice. The next page-authoring slice should concentrate on `practice_collection_page` and
`practice_page` first, because they are smaller, already represented in current schemas, and cover the
core editor-matrix mechanics: generated base/regional rows, section cells, runtime cells, inherited price,
optional sections, open/save/validate/preview/publish, and navigation indicator refresh. After that slice
is stable, `service_page` and then `problem_page` should be implemented from the approved structures.

Implementation note, 2026-05-22: `cms-back` now contains the first page runtime resolver layer. During
preview and publish, page lifecycle asks `PageRuntimeResolverService` to fill missing runtime payloads for
service-tree pages. The first supported slots are `practice_collection`, `practice_services`,
`practice_lawyers`, `practice_cases`, `practice_reviews`, `service_problems`, `service_lawyers`,
`problem_lawyers`, and `lead_capture`. The resolver reads CMS reference-data tables, uses source slugs from
the page path, filters visible/public records, applies lawyer qualification score rules (`score > 1`), and
builds route-ready list items where real reference data is already available. For
`practice_collection_page`, base rows list all visible practices and regional rows list visible practices
that have an active region qualification for the selected visible region. `practice_cases` and
`practice_reviews` currently return empty route-aware list payloads until cases/reviews read models are
implemented. Provided runtime payloads are still respected and are not resolved twice, which preserves
backward compatibility with manual preview/publish requests. Missing visible sources or unroutable visible
child items now fail as `PAGE_RUNTIME_RESOLUTION_FAILED` before an invalid public snapshot is created.

Implementation note, 2026-05-23: `cms-back` now exposes the first direct global sections workbench API:
`GET /api/admin/global-sections`,
`GET /api/admin/global-sections/{sectionKey}/locale-diagnostics`,
`GET /api/admin/global-sections/{sectionKey}/editor`,
`GET /api/admin/global-sections/{sectionKey}/public-content`,
`POST /api/admin/global-sections/{sectionKey}/draft`,
`POST /api/admin/global-sections/{sectionKey}/validate`,
`POST /api/admin/global-sections/{sectionKey}/publish`,
`GET /api/admin/global-sections/{sectionKey}/history`, and
`POST /api/admin/global-sections/{sectionKey}/rollback`. The first keys are `site_header`,
`site_footer_practices` (read-only diagnostics/runtime payload), `site_footer`, and `global_price`.
Global sections are locale-specific, reuse the existing
`SectionLifecycleService`. `site_header`, `site_footer_practices`, and `site_footer` are layout-level
globals and publish with propagation `none`: they update the current global section version but do not
rebuild page snapshots. `global_price` is available as the first shared price source for generated
practice/service/problem pages and publishes with affected page snapshot rebuild. Its detailed editor/API
contract is defined in `docs/global-price-section-workbench.md`.

Implementation note, 2026-05-27: global-section editor DTOs expose `schema.fields`, and global-section
publish responses document the lifecycle publish result instead of an opaque `unknown`: affected pages,
affected bindings, and rebuilt snapshot statuses are part of the frontend contract.

Implementation note, 2026-06-04: global-section screens can read all-locale diagnostics through
`GET /api/admin/global-sections/{sectionKey}/locale-diagnostics` and the current published/public payload
through `GET /api/admin/global-sections/{sectionKey}/public-content?locale=...`. The editor endpoint
remains the source for draft editing; `public-content` is for comparing/debugging what the public layout
would use from the current published global section.

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

Implementation note, 2026-05-23/30: generated service-tree workbench matrices now include regional
variants. `GET /api/admin/page-workbench/page-types/{practice_collection_page|practice_page|service_page|problem_page}`
returns the base row plus regional rows for visible regions with valid `sourceSlug`. Regional rows keep the
same `sourceRecord` and add row-level `region`/`regionSlug`. The generated bootstrap endpoint accepts
optional `regionId`; backend rereads the region, builds the canonical regional route, and passes
`regionSlug` into page authoring. The service-tree endpoint remains non-regional so the left hierarchy
stays collection -> practice -> service -> problem without multiplying every node by regions.

Implementation note, 2026-06-04: generated service-tree workbench matrices now use the same expected-region
boundary as the navigation indicators. Regional rows are emitted only for applicable visible regions:
practice pages require an active region qualification for that practice; service/problem pages use the
parent practice qualification; the regional practice collection uses regions with at least one active
visible practice qualification. Non-applicable region/source pairs are not returned and must not be treated
as missing regional pages.

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
