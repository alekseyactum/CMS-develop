# Editorial Content Architecture - 2026-06-19

This document fixes the target backend/content architecture for the editorial publication domain:

- blog articles;
- media mentions / "we in media";
- cases.

The goal is to avoid two extremes:

- three separate unrelated subsystems;
- one shapeless universal page type with weak validation and unclear editorial rules.

The chosen direction is one shared editorial content contour with several content kinds and page types.

## Naming Note

Older documents and prototype references may still use:

- `article_page`
- `articles_root`

For the new CMS contour, use:

- `blog_page`
- `blog_collection_page`

This is only a naming normalization. It does not imply a different product role from the earlier
"article/blog publication" idea.

## Scope

This document defines:

- the shared data model;
- the common section model;
- which parts are common and which are type-specific;
- the minimum validation rules;
- what should be implemented first.

This document does not yet define the final visual structure of collection pages in detail. It fixes the
data and authoring model first.

## Core Decision

Blog, media, and case pages should use one common editorial architecture:

- common metadata/index layer;
- common body-builder model;
- type-specific validation and fields where needed.

They should remain different public page types:

- `blog_page`
- `media_page`
- `case_page`

And they should have separate collection page types:

- `blog_collection_page`
- `media_collection_page`
- `case_collection_page`

There is no requirement yet for one public collection that mixes all content kinds together. The data model
may allow it later, but it should not be part of the first implementation slice.

## Shared Principles

### One page, one snapshot

Each publication page remains a normal CMS page with draft/published lifecycle and snapshots.

This means:

- preview is built from a protected preview payload;
- public site renders published page snapshots;
- publish/rollback rules stay aligned with the rest of the CMS.

### Separate metadata from body

The publication must have a structured metadata/index layer that is not buried inside a free-form rich-text
body.

This is needed for:

- collection cards and list pages;
- author badges;
- legal reviewer badges;
- practice/service/problem relations;
- filters and future search;
- stable sort/publish behavior.

### Cases need a fast path

`case_page` should support both:

- a minimal structured publication path for fast editorial work;
- a richer expanded page when needed.

So a case is not forced to become a fully custom editorial composition every time.

### Case localization model

Localized versions of one case are separate `case_page` records joined by `cms_pages.locale_group_id`.
This keeps every locale independently editable, previewable, publishable, and rollbackable while preserving
the fact that all variants describe the same case.

Creating a translation copies only shared structural data:

- practice, service, and problem relations;
- primary and co-author relations;
- cover media and featured state;
- ERP case id and additional service-tree relations.

Localized content is never inherited from another language. `seo`, `publication_meta.title`,
`publication_meta.excerpt`, `case_summary`, and `content_builder` belong to the target locale. A newly
created variant starts with the requested title/excerpt and empty `case_summary`/`content_builder` drafts.
It cannot be published until the normal page validation rules are satisfied.

The unique `(locale_group_id, locale)` database constraint allows at most one page per language in a group.
Existing editorial pages are assigned individual groups during migration; they are not merged heuristically.
Only explicitly created translations join an existing group.

Public page reads calculate `localeAlternates` from the currently published variants in the same group.
Unpublished drafts are not exposed as language alternatives.

## Shared Page-Owned Sections

All three publication page types should use the common page-owned section:

- `publication_meta`

All three publication page types should also support a dynamic ordered body zone through:

- `content_builder`

Additionally, `case_page` should always include:

- `case_summary`

## Section: publication_meta

`publication_meta` is the shared structured metadata section for `blog_page`, `media_page`, and
`case_page`.

### Common fields

- `title` - required
- `excerpt` - required plain text
- `coverMediaId` - optional, but missing value is a warning
- `publishedAt` - auto-filled on first publish, then editable in CMS
- `isFeatured` - optional, default `false`
- `practiceRef` - optional
- `serviceRef` - optional
- `problemRef` - optional

### Relation chain rules

Allowed relation combinations:

- nothing selected;
- only `practiceRef`;
- `practiceRef + serviceRef`;
- `practiceRef + serviceRef + problemRef`.

Rules:

- if `serviceRef` is selected, it must belong to `practiceRef`;
- if `problemRef` is selected, it must belong to `serviceRef` and `practiceRef`;
- conflicting chain is an error.

### Contributor model

#### blog

- optional author;
- author may be:
  - `lawyer`
  - `cms_user`
- optional `legalReviewerLawyerRef`

#### media

- optional author;
- author may be:
  - `lawyer`
  - `cms_user`

#### case

- required `primaryLawyerAuthorRef`
- optional `coAuthorLawyerRefs[]`

### Type-specific fields

#### blog

No extra required type-specific metadata fields for now.

#### media

- `sourceName` - required
- `sourceUrl` - optional, missing value is a warning
- `mediaPublishedAt` - optional

#### case

- `erpCaseExternalId` - optional

## Section: case_summary

`case_summary` exists only on `case_page`.

It is required and gives the fast editorial publication format even when the page does not yet need a large
custom body.

### Fields

- `lead` - required plain text
- `situation` - required rich text
- `actions` - optional rich text
- `result` - optional rich text
- `courtName` - optional plain text
- `caseNumber` - optional plain text
- `resultLabel` - optional plain text
- `timelineNote` - optional plain text
- `confidentialityNote` - optional plain text

Important:

- `erpCaseExternalId` stays in `publication_meta`, not in `case_summary`;
- section labels/headings inside `case_summary` are fixed by schema and not editor-renamable.

### Validation

Errors:

- empty `lead`
- empty `situation`

Warnings:

- empty `actions`
- empty `result`
- overlong optional fields
- editorial quality issues such as unusually long labels/text blocks

## Section: content_builder

`content_builder` is the shared dynamic body zone for `blog_page`, `media_page`, and `case_page`.

It should be modeled as an ordered list of blocks with a stable typed contract, for example:

```json
{
  "items": [
    {
      "blockType": "rich_text",
      "variant": "default",
      "content": {}
    }
  ]
}
```

The exact list of allowed block types can be expanded later, but the initial model should stay explicit and
typed. Do not use one free-form JSON field with no schema discipline.

Recommended first block families:

- `rich_text`
- `quote`
- `image`
- `gallery`
- `cta`
- `related_links`

The important point at this stage is not the final list of blocks, but the contract shape:

- ordered list;
- typed `blockType`;
- optional `variant`;
- typed `content` per block type.

## Validation Rules

### publication_meta

Common errors:

- empty `title`
- empty `excerpt`
- invalid `coverMediaId`
- conflicting practice/service/problem chain

Common warnings:

- missing `coverMediaId`
- unusually long `title`
- unusually long `excerpt`

### blog-specific

Errors:

- author type selected but matching author reference missing
- both lawyer and CMS-user author refs filled at the same time

Warnings:

- no author
- no legal reviewer
- bad author or reviewer reference

### media-specific

Errors:

- empty `sourceName`
- author type selected but matching author reference missing
- both lawyer and CMS-user author refs filled at the same time

Warnings:

- no author
- empty `sourceUrl`
- empty `mediaPublishedAt`
- bad author reference

### case-specific

Errors:

- empty `primaryLawyerAuthorRef`
- primary author not found
- bad co-author reference
- duplicate co-authors
- co-author duplicates primary author

Warnings:

- empty `erpCaseExternalId`

## Additional Service-Tree Tags

Cases and reviews can belong to more than one service-tree line.

The primary practice/service/problem line remains the main relation. For cases it is stored in
`publication_meta`; for reviews it comes from the normal review reference-data fields. This primary line
can be filled by ERP/import flows.

Additional lines are CMS-owned editorial tags:

```json
{
  "additionalServiceTreeRefs": [
    {
      "practiceRef": "practice-cms-id",
      "serviceRef": "service-cms-id",
      "problemRef": "problem-cms-id"
    }
  ]
}
```

Rules:

- `practiceRef` is required for each additional line;
- `serviceRef` is optional;
- `problemRef` is optional, but requires `serviceRef`;
- duplicates are invalid;
- a line that duplicates the primary relation is a warning, because it is redundant;
- these tags are not overwritten by ERP upsert/resync.

Runtime lists should match both primary and additional lines:

- service-hierarchy case lists match cases by primary relation or by an additional tag;
- service-hierarchy review lists match reviews by primary relation or by an additional tag;
- primary matches sort before additional matches;
- for problem review lists, an exact additional problem match sorts before the older service-level fallback.

## Collection Behavior

Required public collection page types:

- `blog_collection_page`
- `media_collection_page`
- `case_collection_page`

At this stage, their detailed visual section sets remain future work. What is fixed now:

- collection pages must read from the shared editorial metadata/index layer, not from ad hoc body parsing;
- collections should filter by publication kind;
- relations to practice/service/problem should be available for future filtering or related-content lists;
- there is no requirement yet for a unified all-content public collection.

## Why This Direction

This model is intentionally in the middle:

- common enough to avoid building three isolated mini-CMS products;
- structured enough to avoid an untyped universal page monster;
- flexible enough to support richer long-form pages later;
- simple enough to publish a case quickly with only `publication_meta + case_summary`.

It also fits the current CMS principles:

- page snapshots remain authoritative;
- preview/publish lifecycle stays consistent with other page types;
- frontend receives explicit typed contracts instead of guessing from raw body markup.

## Recommended Implementation Order

1. Add backend schemas for:
   - `blog_page`
   - `media_page`
   - `case_page`
   - `blog_collection_page`
   - `media_collection_page`
   - `case_collection_page`
2. Add section schemas:
   - `publication_meta`
   - `case_summary`
   - `content_builder`
3. Add validation for shared and type-specific rules.
4. Add the shared metadata/index read layer for collection pages.
5. Add first collection page runtime resolvers.
6. Add CMS frontend support for the new page types and section editors.

## Explicit Non-Goals For The First Slice

The first implementation slice should not try to solve everything at once.

Out of scope for the first pass:

- one public collection mixing all content kinds together;
- a large universal block library for every possible editorial scenario;
- overcomplicated authoring workflows for cases;
- replacing the current snapshot-based CMS model with a special publication subsystem.
