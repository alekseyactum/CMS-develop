# Section Model Foundation

This document fixes the first release-oriented model for CMS page sections.

It is a foundation brief for the future `cms-back/src/sections` module. It should guide code and tests
before page authoring persistence, preview assembly, publish flow, and database tables are implemented.

## Purpose

Sections are first-class authoring units, but public rendering remains snapshot-first.

Section schemas decide whether a section publishes independently or together with its page. The public
frontend must still receive a complete published page snapshot with resolved payload, not live authoring
tables.

This model exists to avoid two bad outcomes:

- a page-only model where one small content edit forces editors to republish the whole page manually;
- a live-section model where the frontend assembles a public page from whichever section versions are
  currently latest.

## Non-Goals

This brief does not define the full section list for every page type.

Out of scope for this foundation step:

- real database tables;
- full price catalog implementation;
- all page schemas;
- all section field schemas;
- CMS UI behavior;
- route registry persistence;
- public frontend rendering.

Concrete page structures should be defined later per page type, for example `services_root`,
`practice_page`, `service_page`, `article_page`, and `contacts_page`.

## Core Terms

`SectionDefinition`

The reusable schema/policy description for a section type. It defines what the section is allowed to do,
not the content of one concrete section.

`SectionInstance`

A concrete section attached to a page, owned globally inside CMS, or backed by an external source. It has
a stable section identity used by authoring, snapshots, diagnostics, and rollback.

`SectionVersion`

A versioned content record for one section instance. Draft and published versions are separate historical
states.

`SectionVersionRef`

A reference to one exact section version.

`PageSnapshotSectionRef`

The minimal section reference stored inside a page snapshot. It should identify which concrete published
section version contributed to the resolved public output, but it should not carry full composition rules.

## Ownership

The first release model must support three ownership scopes.

`page_owned`

The section belongs to one page. Most editorial sections start here.

`global_owned`

The section exists as a standalone CMS-owned global section and may be inherited or referenced by many
pages. Examples include footer, header/navigation, and shared price sections when prices are managed
inside CMS.

`external_source_backed`

The section is backed by a source outside normal CMS section ownership. Future examples include ERP,
service catalog, or an external price source. The first release should leave a clear boundary for this,
but it does not need to implement full external integration.

Ownership does not decide override or append by itself. Footer and price may both be `global_owned`, but
footer can be inherit-only while price can allow override or append according to section schema.

## Versions And Audit

Every section operation must record actor and timestamp.

Required operation metadata:

- created by and at;
- updated by and at;
- published by and at;
- archived, disabled, or rolled back by and at when those operations exist.

Draft and published section versions must be distinguishable. A section version can be valid authoring
history even when it does not activate a new public page snapshot.

## Page Schema Ownership

Canonical page structure belongs to Nest backend page schemas, not to editable database configuration.

The database stores concrete section instances, section versions, page-section bindings, resolved
published snapshots, and content. It should not be the canonical source for which required sections make
up a page type.

Each page type schema should define:

- required and optional section slots;
- section order for required slots;
- whether a section slot is visual content or metadata;
- allowed ownership scopes;
- publish mode;
- dependent draft policy;
- publish propagation policy;
- composition policy;
- visibility/disable policy;
- validation rules;
- allowed dynamic body section types where applicable.

Concrete section lists should be specified before implementing each page type. The general model should
not attempt to define every page type section list up front.

## Initial Page Schema Registry

The first page schema registry slice is code-defined in `cms-back`, not stored in database tables.

Initial fixed page schemas:

- `lawyers_page`: `/lawyers`;
- `lawyer_page`: `/lawyers/:lawyerSlug`;
- `contacts_page`: `/contacts`.

All three page types are localized for `uk`, `ru`, and `en`, but they are not regional in this first
iteration. Ukrainian routes have no locale prefix; `ru` and `en` use locale prefixes through the routing
module.

Shared required slots for all three schemas:

- `site_header`: global-owned, independent, inherit-only, fixed at the start of the page;
- `seo`: page-owned metadata section, published with the page;
- `site_footer`: global-owned, independent, inherit-only, fixed at the end of the page.

Page-specific content/runtime slots:

- `lawyers_page` has `lawyers_header`, `lawyers_filter`, and `lawyers_listing`;
- `lawyer_page` has `lawyer_profile`;
- `contacts_page` has `contacts_header` and `contacts_map`.

`lawyers_filter`, `lawyers_listing`, `lawyer_profile`, and `contacts_map` are runtime/reference slots.
They are part of the page schema, but their data comes from CMS public read models or directories, not
from normal editable `section_versions`. A page snapshot should store the slot/source reference and the
backend should resolve the allowed public read model data while building the public payload.

For this first iteration, these three page schemas have fixed structure. Editors cannot add arbitrary
dynamic body sections to them. Dynamic editor-managed body sections remain reserved for blog-like pages
such as articles, cases, and media/publications pages.

## Composite CMS And Runtime Sections

Not every block that uses runtime/read-model data should be modeled as a pure runtime section.

Many public blocks have two parts:

- CMS-authored fields, such as title, intro text, labels, display settings, and editor-owned copy;
- backend-resolved read-model data, such as lawyers, offices, reviews, practices, services, or regions.

The first-release model should represent these as composite sections when they appear as one visible block
on the page. A composite section has one page-schema slot and one frontend payload contract, but the
backend understands that its payload is assembled from both CMS-owned content and resolved reference data.

Use a pure runtime/reference slot only when the block has no meaningful CMS-authored content.

The public frontend still receives a complete resolved payload. It must not call ERP, read authoring
tables, or decide which reference objects are eligible.

Published snapshots for composite/runtime sections should include dependency refs for reference objects
that were actually used in the payload. These refs are diagnostics and stale-detection metadata; frontend
rendering should depend on the resolved public payload itself.

## First Public Payload Assembly

The first public payload assembler is a pure function over prepared inputs:

```text
page schema + published section payloads + runtime/read-model payloads -> public page payload
```

It does not fetch from the database, does not read draft state, does not decide whether a page can be
published, and does not resolve runtime directories by itself.

The assembler validates that required schema slots are present before a public payload is produced.
Section-backed slots must be passed with exact published section version refs. Runtime/reference slots
must be passed as resolved public read-model payloads.

The resulting public payload separates:

- top-level `seo` metadata;
- ordered visual `sections`;
- source diagnostics for section-version versus runtime/read-model content.

This keeps the frontend contract simple: Next.js receives one complete public payload and does not need
to understand draft tables, authoring composition, or publish-readiness rules.

## First Persistence Tables

The first database layer stores factual authoring and published state only. It must not move canonical
page schemas or section schemas into editable database configuration.

Initial persistence tables:

- `cms_pages`: page variants by page type, locale, optional region, route path, and public path;
- `cms_sections`: stable section identities, locale, ownership scope, kind, owner page, and optional
  external source key;
- `cms_section_versions`: draft/published/archived section content versions with actor/date metadata;
- `cms_section_current_versions`: explicit current published and latest draft pointers for all sections;
- `cms_section_validation_runs`: archive of section version validation attempts;
- `cms_section_version_validation_state`: current validation state per section version and check type;
- `cms_page_section_bindings`: current authoring connection between a page slot and source/local section
  state, composition, visibility, draft status, and layout;
- `cms_page_section_binding_dependencies`: upstream section draft dependencies used for stale diagnostics;
- `cms_page_snapshots`: durable resolved public page payloads;
- `cms_page_snapshot_section_refs`: exact section versions that contributed to a page snapshot;
- `cms_page_current_snapshots`: explicit current public snapshot pointer per page.

This structure supports the first release rule: schemas live in Nest code; content, versions, bindings,
dependencies, and snapshots live in the database.

## First Persistence Service

The first repository/service layer over these tables is `SectionsPersistenceService`.

It owns database reads and writes for:

- creating page records;
- creating section identities;
- creating section versions with transaction-safe next version numbers;
- setting and reading current section version pointers;
- writing section validation runs and current validation state;
- creating or updating page-section bindings;
- replacing binding dependency rows;
- reading page-section bindings for preview/publish flows;
- creating page snapshots and snapshot section refs in one transaction;
- setting and reading the current page snapshot pointer.

This service must stay below publish/business rules. It does not decide whether a page is publishable,
whether append is allowed, how content is resolved, or which slots a page type requires. Those decisions
remain in section/page schema rules and publish services. The persistence service only writes and reads
factual state.

## Composition Strategies

The model must support these composition strategies:

- `inherit`: use parent/source/base value;
- `override`: replace parent/source/base value;
- `append`: keep parent/source/base value and add child/regional/page-specific value.

Strategies may apply at section level or field level.

The model supports both whole-section composition and field-level composition. Whole-section override
makes the page section self-contained. Field-level composition allows one section to inherit some fields,
override other fields, and append to allowed list-like fields.

For the first release, composition allowance is defined by section/page schema. Do not add a separate
instance-level lock policy unless a later requirement proves it is needed. If footer must never be
overridden, its schema should make it inherit-only.

Append must be explicit. A field cannot be appended only because it happens to be an array or rich-text
field. The section schema must allow append for that field.

Append is allowed only for list fields and rich-text block arrays in the first release. Plain strings,
numbers, prices, and arbitrary objects should use inherit or override, not append.

Composition settings are stored in current authoring page-section binding state. They are not stored in
the public snapshot as full composition rules, and they are not owned by the global section version
itself.

No separate composition-history model is required for the first release. General actor/date operation
audit remains required.

## Global And Price Sections

Global sections must be separated by behavior, not by a new ownership scope. `global_owned` covers both
shared fixed sections and shared editable/base sections, while section schema defines how dependent pages
react to draft and published changes.

Global sections are localized as separate section records. Do not store all languages inside one large
multilingual `content_json`.

Example:

```text
site_footer uk -> one global section
site_footer ru -> one global section
site_footer en -> one global section
```

The `cms_sections` table must therefore store an explicit `locale`. For `page_owned` sections, this locale
matches the owner page locale. For `global_owned` sections, locale belongs directly to the section itself.

Shared fixed global sections, such as footer and main navigation/menu, should normally use:

- `global_owned`;
- `independent` publish mode;
- inherit-only composition;
- no page-local section versions;
- no page-level draft stale review for ordinary global draft changes;
- affected page snapshot rebuild after a new global version is published.

All pages for the same locale may reference the same published footer/menu section version in their
snapshots. When footer or menu is published, public pages should move to the new version through affected
snapshot rebuilds, not by creating separate footer/menu versions per page and not by reading live global
tables at render time.

Saving a draft of a shared fixed global section must not change public pages, current page snapshots, or
page authoring state. Footer/menu draft changes must not mark dependent pages `draft_stale`; affected
pages can be calculated for diagnostics or preview, but ordinary page editors should not see thousands of
pages as dirty just because global navigation has an unpublished draft.

Publishing shared fixed global sections uses a patch-based snapshot rebuild, not full recomposition from
authoring state:

```text
current public page snapshot + new footer/menu payload/ref -> new public page snapshot
```

The rebuild must preserve all other section refs and payloads from the current public snapshot. Draft
versions of page-owned sections must not be read or included. Runtime/read-model sections should not make
footer/menu patch rebuild fail because the page is not rebuilt from scratch.

Footer/menu rebuild policy is best-effort:

- the new footer/menu version may become the current published section version after section validation
  passes;
- affected pages that rebuild successfully switch to new page snapshots;
- affected pages that fail for technical reasons go to diagnostics/retry;
- one failed page must not block already valid rebuilt pages.

Expected footer/menu patch rebuild failures are technical or state-integrity failures, for example:

- missing current page snapshot;
- missing expected footer/menu ref in current snapshot;
- missing published section version payload;
- database/transaction error;
- concurrent rebuild or publish conflict;
- timeout.

Footer/menu rollback is implemented as a new draft/publish flow, not by moving the current pointer back to
an old published version. If the current footer is `v3` and the editor chooses to roll back to old `v1`,
the system creates a new draft `v4` with content copied from `v1`. If `v4` passes current validation, it
is published and affected snapshots rebuild normally. If it fails validation, `v4` remains the latest
draft with validation diagnostics so an editor can fix it.

To support this audit trail, section versions should record their source where applicable, for example:

```text
source_section_version_id
change_reason: manual_edit | rollback
```

Price sections must support a shared source for base service prices, but unlike footer/menu they may
require composition instead of a simple payload replacement when inherited or appended content is used.

The intended model:

- a base service price is maintained once in a global CMS section or future external source;
- non-regional service pages inherit or reference that price section/source by default;
- pages may override only fields allowed by schema;
- pages may append contextual notes where allowed;
- regional variants may inherit, override allowed fields, or append allowed regional context.

Regional price sections must not inherit directly from the global price source when a base
non-regional page exists for the same practice/service. The intended chain is:

```text
global price source/section
  -> base non-regional page price section
      -> regional page price section
```

This applies to both price values and CMS-authored price text/notes. The base non-regional page is the
parent content layer for regional variants, while the global price source remains the upper shared source
for base pages.

Regional price resolution uses the current published base page price result as its parent input, never an
unpublished base draft.

If the base non-regional price section uses inherit/append/field-level inherited fields from the global
price source, the base page can be affected by global price publication according to the global price
rebuild policy. Regional pages then become dependent on the resulting base page price section, not on the
global price source directly.

If the base page publishes a changed price section, dependent regional pages that inherit or append from
it must be marked as having unapplied parent published changes. They must not be automatically published.
Editors should update them through the explicit regional republish flow.

Regional whole-section override makes the regional price section self-contained for that slot. In that
case, later base price changes do not change the regional price block automatically and should not mark it
stale for inherited price content.

Regional append adds regional content on top of the resolved published base price result. Field-level
composition follows the same rule: inherited fields come from the base page price result, appended fields
append to the base page value, and overridden fields keep the regional value.

If a page or region uses whole-section override, it is treated as self-contained for that section and
global section updates do not automatically change it. With field-level composition, rebuild behavior is
field-aware:

- inherited fields may update from the new global/base version;
- appended fields may rebuild from the new global/base value plus the local append value according to
  policy;
- overridden fields keep the local value.

Footer and menu are global section examples with a different policy from price: they should normally be
inherit-only, not overridable by pages, and published as one shared version that triggers affected snapshot
rebuilds.

Global price sections use automatic affected snapshot rebuild for dependent pages that still depend on
the global source.

When a global price section is published:

- enabled page bindings using whole-section `inherit` must rebuild the price block from the new published
  global price;
- enabled page bindings using whole-section `append` must rebuild the price block from the new published
  global price plus the current published local append content;
- field-level composition must rebuild when at least one field uses `inherit` or `append`;
- whole-section `override` is self-contained and must not be changed by the global price publish;
- disabled optional price bindings must not be changed.

The rebuild is not a full page republish from draft authoring state. It must preserve the current public
snapshot and replace only the resolved price block plus the relevant price section refs. Draft versions of
other page sections must not be read or included.

Unlike footer/menu, price rebuild may require content recomposition and validation:

```text
new global published price + current published local append/override delta -> resolved price payload
```

If a dependent page's recomposed price payload fails validation, the global price version may still remain
published, valid affected pages may still switch to new snapshots, and the failed page should go to
diagnostics/retry or manual repair. This is still a best-effort affected snapshot rebuild, but with
price-specific recomposition rather than footer/menu-style direct replacement.

Saving a new global price draft does not change public snapshots. It may mark dependent enabled bindings
as stale for authoring diagnostics when they use `inherit`, `append`, or field-level inherited/appended
fields. Whole-section overrides and disabled optional bindings are not stale because they do not depend on
the global price payload.

The first release should not implement the full price catalog or ERP integration.

## Current Section Versions

The current section version pointer model applies to all sections, not only global sections.

`cms_section_versions` stores the version archive. Draft and published versions live in the same table and
are distinguished by lifecycle state:

```text
lifecycle_state: draft | published | archived
```

`cms_section_current_versions` stores the current pointers:

```text
section_id
current_published_version_id
latest_draft_version_id
published_activated_by
published_activated_at
draft_updated_by
draft_updated_at
```

This table answers “what is current for this section?” It does not replace snapshot refs.

`cms_page_snapshot_section_refs` answers a different question: “which exact section version contributed
to this historical page snapshot?”

Page rollback changes the current page snapshot pointer only. It must not mutate current section pointers.

## Section Validation State

Invalid save draft attempts do not need to be persisted in the first release. If draft save validation
fails, normal section version tables remain unchanged and the UI can show the immediate validation error.

Publish validation is different because the draft already exists and the editor needs durable diagnostics
for the failed publish attempt.

Section publish validation should be stored in two places:

`cms_section_validation_runs`

Archive of validation attempts:

```text
validation_run_id
section_version_id
check_type: publish_validation
status: passed | passed_with_warnings | failed
issues_json
checked_by
checked_at
request_id
```

`cms_section_version_validation_state`

Current validation state for one section version and check type:

```text
section_version_id
check_type
status
latest_validation_run_id
critical_count
warning_count
error_count
checked_at
```

The UI should read current validation state for the editor-facing status and may read validation runs for
history.

Validation issues must carry severity:

```text
severity: critical | warning
```

Critical issues block publish or publish-preview for the affected section/page. Warnings do not block
draft save or publication, but they must be returned to the UI and included in readiness diagnostics where
they matter.

Warnings are expected to be mostly field/object-specific, for example recommended text length, optional
metadata quality, weak media metadata, or non-critical content quality concerns.

Even if a draft passed validation when it was saved, publish must validate the draft again. Schema rules,
media references, required fields, or related constraints may have changed between save and publish.

If publish validation fails:

- the draft remains a draft;
- no new published version is created;
- current published section pointer does not change;
- affected page snapshot rebuild does not start;
- validation run and validation state record the current reasons.

If publish validation passes:

- validation run and state record success;
- a published section version is created from the draft content;
- `cms_section_current_versions.current_published_version_id` is updated;
- affected page snapshot rebuild starts according to section policy.

## Page-Owned Parent Inheritance

Publishing a page-owned parent section must not automatically publish inherited child or regional pages.

Example:

```text
base service page section published
regional page inherits/appends that section
```

The base page publish updates only the base page snapshot and the base page-owned section versions that
publish with that page. Inherited child or regional pages remain on their current public snapshots until a
separate explicit action updates them.

Dependent child/regional bindings should still record that a newer parent published version is available
when they use `inherit`, `append`, or field-level inherited/appended fields. Whole-section overrides and
disabled optional bindings are not affected.

The first release should expose this as an explicit CMS action, for example:

```text
Republish regional pages
```

This action is controlled and visible to the editor/operator. It should:

- show affected regional pages before execution;
- skip whole-section overrides and disabled optional bindings;
- use current published parent section versions;
- use current published local append/override deltas where needed;
- not read unrelated draft sections from regional pages;
- create new page snapshots for selected affected pages;
- switch current snapshots only for successful pages;
- write diagnostics/retry state for failed pages.

This keeps page-owned inheritance predictable. Normal parent page publish does not hide a cascade of
regional public updates, while editors still have an explicit batch operation when they want to apply the
new parent content to regional pages.

Useful authoring status concepts for this flow:

```text
has_local_draft_changes
has_unapplied_parent_published_changes
last_regional_republish_status
```

## No Persisted Overlay Versions

The first release must not introduce persisted overlay section versions.

Inheritance, override, and append are authoring/publish-time rules. On publish, backend resolves the
final section content and writes the resolved output into the page snapshot payload.

This avoids a first-release model like:

```text
base section version + overlay version(s) -> separate persisted resolved section version
```

Instead, use:

```text
authoring binding composition + section versions -> resolved page snapshot payload
```

Snapshot diagnostics may keep minimal section/version refs where useful, but frontend rendering must not
depend on inheritance lineage.

## Content Resolution Rules

The first implementation layer resolves content as a pure deterministic operation:

```text
section schema + composition state + source/base content + local content -> resolved section content
```

Resolution must support:

- whole-section `inherit`, `override`, and `append`;
- field-level `inherit`, `override`, and `append` inside object sections;
- schema validation before applying a strategy;
- append only for list-like and rich-text block array content;
- clear errors when required source/local content is missing or when append receives non-array content.

Field-level resolution uses the section-level strategy as the default for fields that do not have an
explicit field strategy. For example, a section can inherit all base fields by default, override `title`,
and append `items`.

Resolution must clone returned JSON values and must not mutate source/base or local authoring data. It is
not persistence by itself; persistence will later store section versions, bindings, and final resolved
page snapshot payloads.

## Draft Dependency And Staleness

Inherited and append-based authoring can create draft dependencies between parent/source/base sections and
child or regional page bindings. Whether upstream draft changes mark dependents stale is section-schema
policy, not ownership alone.

Two first-release policies are required:

- `mark_stale`: upstream draft changes mark dependent inherit/append bindings as `draft_stale` until the
  page or regional authoring state is reviewed;
- `none`: upstream draft changes do not create page-level stale review, used for shared fixed globals such
  as footer/menu where pages always inherit one shared published section.

If a parent/source/base draft changes:

- CMS must not automatically persist new child draft section versions;
- CMS must not automatically persist new child page draft versions;
- dependent child bindings and pages must be marked `draft_stale` or an equivalent authoring status when
  the section schema uses the `mark_stale` policy;
- public current page snapshots must remain unchanged.

Draft dependency metadata should record which upstream draft version a dependent binding/page was last
reviewed or composed against.

Implementation note: `cms-back` now treats both saving a new upstream draft and creating a rollback draft
as upstream draft changes. The lifecycle flow finds dependent page-section bindings registered with the
`mark_stale` dependency policy, applies field-aware inherit/append staleness rules, updates their
`draft_stale` status and dependency refs, and returns the affected bindings to the admin API. It does not
materialize child draft versions and it does not change published page snapshots.

Independent section publication is also wired to an affected snapshot planning step. When a section is
published with `publishPropagationPolicy = rebuild_affected_snapshots`, `cms-back` finds direct and
source-dependent page bindings, applies the same direct/inherit/append impact rules, and returns affected
pages/bindings with recommended action `rebuild_snapshot`.

The implementation now also attempts the rebuild workflow for affected pages. For each affected page it
loads the current public snapshot, patches the changed section payload/ref, creates a new page snapshot,
switches `cms_page_current_snapshots`, and records the applied published section version on the binding or
source dependency. Existing page-owned drafts are not read or changed. Rebuild is partial-success: a page
without a current snapshot, broken payload state, or another technical failure is returned as
`skipped`/`failed` diagnostics while other valid pages can still move to rebuilt snapshots.

Draft preview must resolve from the latest upstream draft versions plus the child/regional override and
append state. The composed draft result may be recalculated on demand or in background authoring flows,
but it must not become a second persisted source of truth that competes with the child/local authoring
state.

If a child page uses whole-section override, that section is self-contained for draft dependency purposes
and upstream draft changes must not mark it stale for inherited content. Field-level composition may use
field-aware stale behavior where only inherited/appended fields depend on the upstream draft.

Editor diagnostics and publish-readiness checks must expose upstream draft changes clearly. A dependent page
with unresolved upstream draft changes must be revalidated through preview/review before it is treated as
ready for publish.

## Layout Policy

Page snapshots must preserve section order and layout placement.

The model must distinguish:

- fixed sections;
- editor-movable sections;
- layout slots or zones.

Some sections can be reordered. Some cannot be moved outside their slot. Some cannot be moved at all.

Layout policy belongs to the page/section schema layer, not to frontend rendering guesses.

Required section order is defined by backend page schema and is not editor-reorderable by default.

## Blog-Like Dynamic Body Pages

Blog-like pages need a constrained flexible layout.

The first blog-like group includes:

- `article_page`;
- `case_page`;
- media/publications page.

Expected shape:

- fixed start sections;
- editor-managed body zone;
- fixed end sections.

Editors may add and reorder allowed content sections inside the body zone. They must not insert sections
before fixed start sections or after fixed end sections in the first release.

Dynamic body sections are governed by page body-zone validation. The schema should define allowed dynamic
section types and minimum/required body content rules, for example at least one meaningful content block.

Editor-inserted dynamic sections are movable only inside the editable body zone.

## Metadata Sections

SEO is a first-class section for authoring, versioning, validation, publish, snapshot, and rollback.

SEO should not be treated as a visual body block. The backend schema can distinguish section kind, for
example content versus metadata, while the frontend decides how to process `seo` in the final payload.

## Section Publish Activation

Section publish mode is defined by schema:

- `independent`: section can publish its own new published section version;
- `with_page`: draft changes are published together with page publish.

Even an independent section publish does not change the public site directly. Public activation always
happens through a new complete page snapshot:

- changed `with_page` sections are validated during page publish and prepared for publication;
- new published versions for changed `with_page` sections and the new current page snapshot must be
  committed atomically;
- independent sections used by publish-resolution must already have a published version;
- unchanged sections stay pinned to the versions selected by publish-resolution;
- layout refs are preserved unless the operation explicitly changes allowed layout state;
- page-level validation runs before the new page snapshot becomes current.

If a `with_page` page publish fails section validation or page-level validation, the failed attempt must
not persist new published versions for the affected `with_page` sections and must not activate a new
public current page snapshot.

Independent section publication remains a separate flow. It may create a new published section version
before affected page snapshots rebuild. If a later affected-page rebuild fails, the independent section
version remains published in authoring history, but invalid page snapshots must not be activated.

Required independent sections must have a published version before any page depending on them can be
published. Enabled optional independent sections must also resolve to a published version. Missing
published versions are publish/readiness errors.

Page publish prepares changed `with_page` draft sections for publication while building the new page
snapshot. Enabled optional `with_page` sections must pass section validation; backend must not silently
disable invalid enabled sections.
Failed page publish attempts should be retained as diagnostics or audit history, not as partial published
state for `with_page` sections.

## Preview And Publish Resolution

CMS supports editor preview modes and one strict publish mode.

`published-preview`

Resolves from currently published section versions. It is used to review the state that can be safely
published from already-published dependencies.

`draft-preview`

Resolves from latest draft section versions where available, including draft independent sections. It is
used for authoring review.

`publish-preview`

Runs the strict publish-resolution checks without activating a snapshot. It should show the editor what
would be published and return the same critical blockers/warnings that the real publish path would use.

`publish-resolution`

The real page publish path:

- changed `with_page` sections are validated and prepared for conversion from draft to published versions;
- independent sections are resolved only from current published versions;
- required and enabled optional sections are validated;
- resolved public payload is built;
- if validation succeeds, changed `with_page` sections are committed as new published versions and a new
  page snapshot is created and activated as current in one atomic operation.

Publish must not accidentally include draft independent sections.

Draft preview may return an incomplete payload together with diagnostics so editors can work with
unfinished content. Publish preview and publish are strict: critical issues block activation, while
warnings remain visible but non-blocking.

## Global Section Rebuild Policy

Publishing a `global_owned` section creates a new global section version. Public pages move to that
version only through affected page snapshot rebuilds.

Global section activation is policy-driven:

- global section publish itself is immediate as authoring history;
- public page activation happens through affected page snapshot rebuild;
- rebuild may be automatic, manually approved, or scheduled/batched depending on section policy;
- large affected sets must be processed in batches with diagnostics;
- failed page rebuilds must not block already valid rebuilt pages unless policy requires all-or-nothing.

Shared fixed global sections such as footer/menu should default to affected snapshot rebuild without
page-by-page manual draft review. Shared price-like sections may still require draft-stale review before
affected page snapshots are considered ready, because local override/append content can depend on changed
base values.

All-or-nothing behavior is also policy-driven. The default should be partial success with diagnostics,
while high-risk sections may require all-or-nothing or manual approval.

Affected pages are determined primarily from current published state/bindings and checked against page
schema for readiness diagnostics.

## Visibility And Deletion

Section lifecycle and page binding visibility are separate concepts.

Section lifecycle:

- draft;
- published;
- archived.

Page binding visibility:

- enabled;
- disabled.

Disabled means the section binding is not active for that page. Disabled bindings are excluded from
published page snapshots: they do not appear in public payload or section refs.

Whether a section can be disabled is defined by schema through `canDisable`. Required sections normally
use `canDisable=false`, while optional sections may be disabled when schema allows it.

Physical deletion is allowed only for draft-only sections that never reached published history or page
snapshot history. Published/history sections must be archived or removed from the current draft/binding,
not physically deleted.

## Rollback

Published snapshot rollback restores public output only:

```text
current public snapshot -> selected historical snapshot
```

It must not mutate current draft, page-section bindings, composition settings, or authoring state.

Authoring rollback is a separate feature and can be implemented later. The first release must support
public rollback through historical published snapshots.

## Initial Code Scope

The first `src/sections` slice should stay pure and testable.

Recommended files:

```text
src/sections/index.ts
src/sections/section.types.ts
src/sections/section-schema-policy.ts
src/sections/section-snapshot-rules.ts
src/sections/section-snapshot-rules.spec.ts
```

The first code slice should not use the database.

Initial code status as of 2026-05-10, before the 2026-05-11 requirement refinement:

- `cms-back/src/sections` is implemented as a pure TypeScript module with no Nest, database, or Cloud
  runtime dependency;
- section schema policy validates section-level and field-level `inherit`, `override`, and `append`
  composition rules;
- parent/source lock policy rejects forbidden section and field operations explicitly in the initial code,
  but the refined first-release requirement moves this decision into schema policy;
- page snapshot rules can pin a newly published section version into an existing snapshot while keeping
  unchanged section refs stable;
- rollback restores exact historical section refs in the initial code, while the refined requirement
  treats public snapshot rollback as resolved-output rollback;
- layout policy distinguishes fixed zones from editor-managed body zones;
- unit tests cover the first section policy and snapshot behavior.

Requirements update as of 2026-05-11:

- section ownership is refined to `page_owned`, `global_owned`, and `external_source_backed`;
- persisted overlay section versions are removed from first-release scope;
- published snapshots should prioritize resolved public payload plus minimal section/version refs, not
  full composition lineage;
- page structures are code-defined in Nest page schemas;
- preview and publish resolution are separate modes;
- schema decides section publish mode, disable rules, layout behavior, and composition policy.

The existing `cms-back/src/sections` foundation already covers the pure rules for composition,
staleness, snapshot refs and layout. The lifecycle/persistence layer now also wires upstream draft
propagation for `saveDraft` and section rollback drafts, plus affected snapshot planning for independent
section publish. Automatic affected snapshot rebuild is now implemented for affected current public
snapshots and returns per-page rebuild diagnostics.

Recommended tests:

- validate allowed section and field composition strategies;
- reject append where schema does not allow append;
- reject override where schema does not allow override;
- mark dependent bindings/pages stale on upstream draft change without materializing child draft versions;
- resolve draft preview from latest upstream draft plus local override/append state;
- apply one section publication to a previous snapshot ref set while preserving unchanged refs;
- reject duplicate section ids inside a snapshot ref set;
- preserve section order where the operation does not change layout;
- reject moving fixed sections;
- allow body-zone insertion for article/case-style page layouts;
- verify publish-resolution does not include draft independent sections;
- preserve public current snapshot when only upstream draft state changes;
- verify disabled bindings are excluded from published snapshot output;
- restore historical public snapshot output on rollback.

## Later Persistence Implications

Future database tables should be designed after the pure model and tests exist.

Likely future areas:

- section definitions or schema registry;
- section instances;
- section versions;
- page-section binding state;
- draft dependency and staleness metadata;
- published page snapshots with resolved payloads and minimal refs;
- global section references;
- external source boundaries;
- page layout slots/zones;
- audit metadata for section operations.

These tables should not be created before the section model proves its core rules in code.
