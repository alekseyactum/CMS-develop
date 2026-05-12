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
- global-owned and external-source-backed sections, including the price-section use case where base
  service prices come from one shared source and pages inherit, override allowed fields, or append allowed
  notes;
- shared fixed global sections such as footer/menu, where all pages inherit one published global section
  version and a publish event triggers affected page snapshot rebuilds instead of page-local section
  versions;
- schema-defined inherit/override/append restrictions, so protected sections such as footer can remain
  inherit-only without a separate first-release parent/source lock policy;
- dependent draft policy, so price-like inherited/appended sections can require `draft_stale` review while
  footer/menu-like shared globals do not require page-by-page draft stale review;
- dependency metadata or equivalent diagnostics that show when inherited drafts require revalidation;
- layout placement policy, distinguishing fixed sections from editor-movable sections;
- layout slots or zones, including article/case pages where editor-added sections are allowed only between
  fixed starting and fixed ending sections.

This preserves editor flexibility without breaking snapshot-first public rendering, rollback, cache
revalidation, route diagnostics, SEO validation, or release readiness.

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

## Review Gate

Any change that ports prototype behavior into `CMS` should answer these questions:

- Which product behavior from `notstrapitest` is being preserved?
- Which tests prove that behavior?
- Which module owns the behavior in the new backend?
- Is the frontend reading a stable backend contract rather than draft internals?
- Does the change keep authoring, preview, publishing, and public runtime boundaries clear?
