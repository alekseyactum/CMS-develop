# Editorial Content Backend Execution Plan - 2026-06-19

This document turns the editorial content roadmap into concrete backend implementation slices for
`cms-back`.

Related documents:

- [`editorial-content-architecture-2026-06-19.md`](editorial-content-architecture-2026-06-19.md)
- [`editorial-content-backend-roadmap-2026-06-19.md`](editorial-content-backend-roadmap-2026-06-19.md)

## Goal

Implement the new editorial contour in a way that:

- reuses the current page/section/snapshot model;
- stays understandable for frontend;
- supports future collection pages and filters;
- avoids building a parallel publication subsystem.

## Working Rule

Implementation should happen in small backend slices.

Each slice should end in one of two states:

- ready to merge because the contract is stable enough;
- stopped intentionally because a product decision is still missing.

Do not start several slices in parallel if they touch the same page-schema or publish pipeline boundary.

## Implementation Status - 2026-06-20

Implemented in `cms-back`:

- `blog_page`, `media_page`, and `case_page` are registered page types.
- `blog_collection_page`, `media_collection_page`, and `case_collection_page` are registered collection
  page types.
- `publication_meta`, `case_summary`, and `content_builder` are normal page-owned sections.
- `cms_editorial_publications` and `cms_editorial_publication_contributors` exist as published
  projection tables.
- Publishing or rolling back `blog_page`, `media_page`, or `case_page` rebuilds the published projection
  from the resulting page snapshot.
- Collection pages resolve `editorial_collection_items` from the published projection.
- Backend now exposes a first admin facade for publication lists and creation:
  - `GET /api/admin/editorial/publications?kind=blog|media|case&locale=uk`
  - `GET /api/admin/editorial/publications/slug-check?kind=blog|media|case&locale=uk&title=...`
  - `GET /api/admin/editorial/publications/{pageId}`
  - `POST /api/admin/editorial/publications`

The facade does not replace the section editor. It creates/fetches normal pages and returns links into the
existing authoring/workbench endpoints for `publication_meta`, `case_summary`, and `content_builder`.

## Recommended Slice Order

1. naming normalization and page-type registration
2. shared section schemas
3. detail page workbench/editor flow
4. author/reference selectors
5. published projection tables and rebuild logic
6. collection page schemas and runtime resolvers
7. preview/public payload verification
8. frontend handoff

## Slice 1 - Naming And Page Types

### Objective

Normalize old `article_*` naming and register the new editorial page types in backend code.

### Changes

- use `blog_page` as the preferred new detail page type;
- use `blog_collection_page` as the preferred new collection type;
- keep `case_page`;
- add `media_page` and `media_collection_page`;
- keep legacy `article_page` mentions only where older docs still describe prototype history.

### Backend touchpoints

- page-type enum/unions
- route/page-type registries
- admin navigation metadata where page types are enumerated
- any DTO unions that currently assume only existing page families

### Acceptance criteria

- backend compiles with the new page-type names in shared contracts;
- there is one preferred naming scheme for the new contour;
- no new feature code still depends on `article_page` as the primary new name.

### Stop if

- route naming becomes a product decision instead of a technical normalization;
- frontend already hard-coded a competing name that we intentionally want to keep.

## Slice 2 - Shared Section Schemas

### Objective

Add the reusable editorial section schemas before wiring full page workbench behavior.

### Changes

Implement section schemas for:

- `publication_meta`
- `case_summary`
- `content_builder`

### Backend touchpoints

- section schema registry
- section field definitions
- validators
- editor DTO builders
- preview/public serialization helpers where required

### Required validation

#### publication_meta

- common required fields
- cover media validation
- relation-chain validation for practice/service/problem
- shared validation for unlimited `additionalServiceTreeRefs[]` on blog, media, and case pages
- backend-generated identity/order handling for additional lines and duplicate detection
- type-specific contributor rules
- required explicit media `representationMode` and its conditional source URL rules
- backend-owned `contentModifiedAt` based on the normalized visible-content digest
- type-specific author/co-author rules for case

#### case_summary

- required `lead`
- required `situation`
- warning-only validation for weaker optional completion

#### content_builder

- block registry
- per-block validation entrypoint
- explicit reject path for unsupported block types

### Acceptance criteria

- `/validate` can return meaningful errors/warnings for these sections;
- section editors can be described through backend DTOs without frontend guessing;
- block content is typed enough for preview/public rendering to trust it.

### Stop if

- block-library scope starts expanding without a real public template need;
- the team tries to encode visual page layout decisions inside the generic builder too early.

## Slice 3 - Detail Page Schemas And Workbench Flow

### Objective

Make `blog_page`, `media_page`, and `case_page` real workbench-driven page types.

### Changes

Register page schemas:

- `blog_page`: `seo -> publication_meta -> content_builder`
- `media_page`: `seo -> publication_meta -> content_builder`
- `case_page`: `seo -> publication_meta -> case_summary -> content_builder`

### Backend touchpoints

- page schema registry
- generated/open-editor flows if needed
- page workbench matrix row building
- section editor wrappers
- page preview readiness
- page publish readiness

### Expected behavior

- editors work through normal page workbench endpoints;
- no separate custom CRUD flow is introduced for blog/media/case bodies;
- page preview and publish operate through the existing page lifecycle model.

### Acceptance criteria

- each new page type can be opened in page workbench;
- required sections can be created, validated, drafted, previewed, and published;
- `case_page` works with both `case_summary` only and `case_summary + content_builder`.

### Stop if

- collection page requirements begin to leak into detail page authoring;
- the team starts inventing a separate "publication editor" outside page workbench.

## Slice 4 - Author And Reference Selectors

### Objective

Expose enough lookup data for frontend forms to edit contributor and relation fields safely.

### Changes

Provide lightweight selector/read-model support for:

- lawyers
- CMS users
- practices
- services
- problems

### Backend touchpoints

- existing reference-data endpoints where reusable
- small dedicated selector endpoints only if existing endpoints are too heavy
- lookup validation helpers shared with `publication_meta`

### Important rule

Do not make frontend load giant reference datasets if a smaller selector contract is enough.

### Acceptance criteria

- frontend can populate author/reviewer/co-author and relation selectors;
- backend can validate saved refs against the same source of truth;
- selector contracts are stable and intentionally small.

### Stop if

- selector endpoints start becoming full duplicate admin list screens;
- internal CMS account data starts leaking into public author/byline payloads. CMS-user attribution is
  workflow-only; public fallback authorship is the Actum organization.

## Slice 5 - Published Projection

### Objective

Create the published projection used by collection pages and future related-content runtime blocks.

### Changes

Add database structures:

- `cms_editorial_publications`
- `cms_editorial_publication_contributors`

### Backend touchpoints

- SQL migration
- repository/query layer
- projection rebuild service
- publish/rollback hooks for editorial page types

### Projection rules

- build from the current published snapshot only;
- never treat draft state as collection truth;
- upsert one current row per published locale/page variant;
- replace contributor rows deterministically on rebuild.

### Recommended implementation detail

Keep projection extraction isolated in a small module, for example:

- `EditorialProjectionExtractor`
- `EditorialProjectionRepository`
- `EditorialProjectionRebuilder`

Do not hide the logic inside a giant publish service branch.

### Acceptance criteria

- publishing `blog_page`, `media_page`, or `case_page` creates or updates projection rows;
- rollback restores projection state to the rolled-back snapshot output;
- projection queries can return stable cards without parsing content-builder blocks.

### Stop if

- the team starts storing draft-only data in the projection;
- the projection begins to diverge from snapshot truth.

## Slice 6 - Collection Page Schemas And Runtime Resolvers

### Objective

Implement minimal but stable collection pages for blog/media/case.

### Changes

Register collection page schemas:

- `blog_collection_page`
- `media_collection_page`
- `case_collection_page`

Recommended first shape:

- `seo`
- `editorial_collection_intro`
- `editorial_collection_items`

### Backend touchpoints

- page schema registry
- intro section schema
- runtime resolver for `editorial_collection_items`
- page preview/public payload assembly

### Resolver behavior

Read from `cms_editorial_publications` and filter by:

- `publication_kind`
- locale

Initial ordering:

- `published_at desc`

Future-compatible filters may be added later for:

- practice
- service
- problem
- featured flag

### Acceptance criteria

- collection pages can preview and publish through the normal page flow;
- runtime list output is deterministic and built from projection data;
- frontend can render collection cards from one stable runtime payload.

### Stop if

- detailed visual treatment of collections is still changing too fast;
- collection cards need data not yet present in projection.

## Slice 7 - Preview And Public Contract Verification

### Objective

Prove that preview/public payloads for editorial pages are stable enough for frontend implementation.

### Changes

Add contract-focused tests and manual verification examples for:

- `blog_page`
- `media_page`
- `case_page`
- collection page runtime lists

### Backend touchpoints

- preview payload assembler
- published snapshot assembler
- runtime list serialization
- tests around required fields and shape stability

### Acceptance criteria

- preview payload and published payload differ only where expected;
- content-builder blocks serialize predictably;
- collection cards do not depend on unpublished draft content;
- rollback restores the public contract shape correctly.

### Stop if

- frontend template requirements reveal missing public payload fields;
- too many assumptions are still implicit in test fixtures.

## Slice 8 - Frontend Handoff

### Objective

Give frontend one clean contract for detail-page authoring and one clean contract for collection pages.

### Changes

Document:

- which page types exist;
- which sections are editable vs runtime;
- which selectors are needed;
- how preview works;
- which fields are warnings vs errors;
- how collection cards are resolved.

### Acceptance criteria

- frontend does not need to reverse-engineer payloads from backend code;
- there is one agreed source document for editorial page integration.

## Tests Per Slice

### Unit / pure-module tests

Needed early for:

- `publication_meta` validation
- relation-chain validation
- contributor validation
- content-builder block validation
- projection extraction from published snapshot data

### Integration tests

Needed for:

- section draft/validate/publish flow
- projection rebuild on publish
- projection rebuild on rollback
- collection runtime resolver queries

### Manual smoke scenarios

Minimum scenarios:

1. publish a `blog_page` with internal CMS-user attribution and verify public corporate Actum authorship
2. publish `media_page` in `actum_article` mode with empty `sourceUrl` and verify warning-only behavior
3. reject `media_page` in `external_reference` mode with empty `sourceUrl`
4. publish both media modes and verify distinct graph ownership
5. publish blog/media/case pages with several valid additional service-tree lines
6. publish a `case_page` with only `case_summary`
7. publish a richer `case_page` with `content_builder`
8. technically republish unchanged content and verify `contentModifiedAt` is preserved
9. rollback changed content and verify projection plus `contentModifiedAt` behavior
10. preview a collection page and confirm only published items are listed

## Suggested Merge Strategy

Prefer several backend PR-sized steps, not one giant feature branch:

1. docs + naming normalization
2. shared section schemas
3. detail page schemas
4. projection migration + rebuild logic
5. collection pages
6. frontend handoff docs

This keeps rollback and review manageable.

## Practical Recommendation

If we want the safest path, the first real code slice in `cms-back` should be:

- naming normalization
- `publication_meta`
- `case_summary`
- `content_builder`
- detail page schemas

That gives us authoring value early without yet committing to the collection projection and runtime list
layer.
