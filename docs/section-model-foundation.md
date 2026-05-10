# Section Model Foundation

This document fixes the first release-oriented model for CMS page sections.

It is a foundation brief for the future `cms-back/src/sections` module. It should guide code and tests
before page authoring persistence, preview assembly, publish flow, and database tables are implemented.

## Purpose

Sections are independent authoring units, but public rendering remains snapshot-first.

Editors should be able to edit and publish individual sections. The public frontend must still receive a
complete published page snapshot that pins every rendered section to an exact section version.

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

A concrete section attached to a page or supplied through a shared/source-backed model. It has a stable
section identity used by authoring, snapshots, diagnostics, and rollback.

`SectionVersion`

A versioned content record for one section instance. Draft and published versions are separate historical
states.

`SectionVersionRef`

A reference to one exact section version.

`PageSnapshotSectionRef`

The section reference stored inside a page snapshot. It must include the section identity, section type,
version reference, and layout position used by that snapshot.

## Ownership

The first release model must support at least two ownership modes.

`page_owned`

The section belongs to one page. Most editorial sections start here.

`source_backed`

The section is backed by a shared source owned outside the page section itself. The first known case is a
price section where base service prices should be changed in one place and reused across service pages.

The section model must not require the full price catalog to exist immediately, but it must leave a clean
place for source-backed references and source lock policy.

## Versions And Audit

Every section operation must record actor and timestamp.

Required operation metadata:

- created by and at;
- updated by and at;
- published by and at;
- archived, disabled, or rolled back by and at when those operations exist.

Draft and published section versions must be distinguishable. A section version can be valid authoring
history even when it does not activate a new public page snapshot.

## Composition Strategies

The model must support these composition strategies:

- `inherit`: use parent/source/base value;
- `override`: replace parent/source/base value;
- `append`: keep parent/source/base value and add child/regional/page-specific value.

Strategies may apply at section level or field level.

Whole-section strategy is not always precise enough. A section may inherit its title, override an intro
field, and append items to a list field. Therefore `SectionDefinition` must allow field-level composition
policy where needed.

Append must be explicit. A field cannot be appended only because it happens to be an array or rich-text
field. The section schema must allow append for that field.

## Source-Backed Price Sections

Price sections must support one shared source for base service prices.

The intended model:

- a base service price is maintained once in a shared source;
- non-regional service pages inherit or reference that price section/source by default;
- pages may override only fields allowed by schema and source lock policy;
- pages may append contextual notes where allowed;
- regional variants may inherit, override allowed fields, or append allowed regional context.

The first section foundation code should model this as policy and references only. It should not implement
the full price catalog.

## Lock Policy

Parent or source sections may protect themselves from override.

Locks may apply at:

- section level;
- field level.

A child or regional section must not override a locked parent/source field. It may only override or append
fields allowed by both the section schema and the parent/source lock policy.

Lock policy should produce explicit validation errors. It should not silently ignore forbidden child
content.

## Layout Policy

Page snapshots must preserve section order and layout placement.

The model must distinguish:

- fixed sections;
- editor-movable sections;
- layout slots or zones.

Some sections can be reordered. Some cannot be moved outside their slot. Some cannot be moved at all.

Layout policy belongs to the page/section schema layer, not to frontend rendering guesses.

## Article And Case Insertion Zones

Article pages and case pages need a constrained flexible layout.

Expected shape:

- fixed start sections;
- editor-managed body zone;
- fixed end sections.

Editors may add and reorder allowed content sections inside the body zone. They must not insert sections
before fixed start sections or after fixed end sections unless a later page schema explicitly allows it.

The model should support article/case insertion zones without forcing every page type into the same
flexible layout.

## Section Publish Activation

All sections can be published independently from the editor's point of view.

A section publish operation creates a new section version. Public activation still happens through a new
complete page snapshot:

- the changed section points to the new section version;
- unchanged sections stay pinned to the exact versions from the previous current page snapshot;
- layout refs are preserved unless the operation explicitly changes allowed layout state;
- page-level validation runs before the new page snapshot becomes current.

If page-level validation fails, the new section version remains available in authoring history, but a new
public current page snapshot must not be activated.

## Rollback

Rollback must restore the exact historical section version set referenced by a previous page snapshot.

Rollback must not rebuild a page from latest section versions.

For example, if a historical snapshot referenced:

```text
hero -> v1
faq -> v4
price -> v2
```

rollback must restore those exact references, not:

```text
hero -> latest
faq -> latest
price -> latest
```

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

Recommended tests:

- validate allowed section and field composition strategies;
- reject append where schema does not allow append;
- reject override against section-level or field-level lock policy;
- apply one section publication to a previous snapshot ref set while preserving unchanged refs;
- reject duplicate section ids inside a snapshot ref set;
- preserve section order where the operation does not change layout;
- reject moving fixed sections;
- allow body-zone insertion for article/case-style page layouts;
- restore historical section refs on rollback.

## Later Persistence Implications

Future database tables should be designed after the pure model and tests exist.

Likely future areas:

- section definitions or schema registry;
- section instances;
- section versions;
- page snapshot section refs;
- source-backed section references;
- source/parent lock metadata;
- page layout slots/zones;
- audit metadata for section operations.

These tables should not be created before the section model proves its core rules in code.
