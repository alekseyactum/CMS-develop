# Editorial Content Backend Roadmap - 2026-06-19

This document turns the agreed editorial content architecture into a practical backend implementation path.

Related architecture contract:

- [`editorial-content-architecture-2026-06-19.md`](editorial-content-architecture-2026-06-19.md)
- [`editorial-content-backend-execution-plan-2026-06-19.md`](editorial-content-backend-execution-plan-2026-06-19.md)

## Purpose

We need to implement blog, media, and case pages in a way that:

- fits the current CMS snapshot/section model;
- supports structured collection pages and future filters;
- does not create three unrelated subsystems;
- does not create a second hidden CMS beside the page workbench.

## Naming Normalization

For the new implementation contour:

- use `blog_page` instead of legacy `article_page`;
- use `blog_collection_page` instead of legacy `articles_root`;
- keep `case_page`;
- introduce `media_page` and `media_collection_page`.

Legacy mentions in older docs are historical references, not the preferred new naming.

## Main Engineering Decision

The important implementation decision is this:

- page content still lives in normal section versions and page snapshots;
- collection/filter/search support comes from a projection/index layer;
- we do not create separate "master content tables" for the body of blog/media/case pages.

That means:

- no `cms_blog_articles` body table;
- no `cms_cases` body table as the main source of public render;
- no duplicated publish lifecycle outside the existing page/snapshot model.

This matters because a separate parallel content storage model would duplicate:

- draft logic;
- publish logic;
- rollback logic;
- preview contracts;
- audit expectations.

That would be a real overcomplication at this stage.

## Recommended Persistence Model

### 1. Source of truth

The source of truth for page content remains:

- page schema;
- section bindings;
- section versions;
- page snapshots.

`publication_meta`, `case_summary`, and `content_builder` should be ordinary page-owned sections.

### 2. Published projection

Add a small published-only projection layer for collection/runtime use.

Recommended tables:

- `cms_editorial_publications`
- `cms_editorial_publication_contributors`

This is intentionally a projection, not a second editorial source of truth.

### Table: cms_editorial_publications

Recommended role:

- one row per published locale/page variant of `blog_page`, `media_page`, or `case_page`.

Recommended fields:

- `publication_id`
- `page_id`
- `snapshot_id`
- `page_type`
- `publication_kind` (`blog`, `media`, `case`)
- `locale`
- `public_path`
- `title`
- `excerpt`
- `cover_media_id`
- `published_at`
- `content_modified_at` nullable, backend-owned
- `is_featured`
- `practice_id`
- `service_id`
- `problem_id`
- `source_name` nullable, for media
- `source_url` nullable, for media
- `representation_mode` nullable only for legacy/unclassified drafts; required for new publication
- `media_published_at` nullable, for media
- `erp_case_external_id` nullable, for case
- `primary_lawyer_author_id` nullable
- `legal_reviewer_lawyer_id` nullable
- `cms_user_author_id` nullable
- `sort_published_at`
- `created_at`
- `updated_at`

Important notes:

- the row should represent the currently published snapshot only;
- when a page is republished or rolled back, this row is rebuilt from the resulting published snapshot;
- draft-only state should not require a second projection in the first slice.
- `cms_user_author_id` remains internal workflow attribution and must not become a public person/byline;
  public author fallback is the global Actum organization.
- `content_modified_at` advances only when the normalized visible-content digest changes; technical
  projection/snapshot rebuilds preserve it.

### Table: cms_editorial_publication_service_tree_refs

Use one normalized row for every primary and additional service-tree line needed by collection and related
content queries.

Recommended fields:

- `relation_id`
- `publication_id`
- `relation_kind` (`primary`, `additional`)
- `sort_order` (primary is always first; additional order follows saved order)
- `practice_id`
- `service_id` nullable
- `problem_id` nullable

The projection has no product-level item-count limit. Rebuild validates hierarchy membership, rejects
duplicate additional lines, and preserves deterministic order. Authoring remains owned by the published
`publication_meta` snapshot; this table is a rebuildable read projection, not a second source of truth.

### Table: cms_editorial_publication_contributors

Recommended role:

- contributor rows only where one publication can have several lawyers, mainly case co-authors.

Recommended fields:

- `contributor_id`
- `publication_id`
- `role` (`primary_author`, `co_author`, `legal_reviewer`)
- `lawyer_id`
- `sort_order`

Why not keep all contributor data in one JSON field:

- SQL joins and filters stay simpler;
- public card/list queries remain explicit;
- future author pages or "more by this lawyer" slices become easier.

At the same time, this is still a small projection table, not a full second content domain.

## Recommended Page Schemas

### blog_page

Recommended first schema order:

1. `seo`
2. `publication_meta`
3. `content_builder`

### media_page

Recommended first schema order:

1. `seo`
2. `publication_meta`
3. `content_builder`

### case_page

Recommended first schema order:

1. `seo`
2. `publication_meta`
3. `case_summary`
4. `content_builder`

This gives us:

- a fast path for cases;
- a consistent authoring shape across all publication pages;
- room for long-form expansion later.

## Recommended Collection Page Schemas

The visual structure of collection pages is still not fully fixed. So the backend should start with a
minimal stable schema that does not block future design.

Recommended first slice:

### blog_collection_page

1. `seo`
2. `editorial_collection_intro`
3. `editorial_collection_items`

### media_collection_page

1. `seo`
2. `editorial_collection_intro`
3. `editorial_collection_items`

### case_collection_page

1. `seo`
2. `editorial_collection_intro`
3. `editorial_collection_items`

Where:

- `editorial_collection_intro` is a small page-owned section;
- `editorial_collection_items` is a runtime list filtered by publication kind.

This is a deliberate compromise:

- enough structure to implement collection pages now;
- not so much product locking that future design changes become painful.

## Section Schema Work

### publication_meta

Needs:

- shared schema definition;
- page-type-specific validation branches for blog/media/case;
- reference checks against practice/service/problem;
- media ownership/usage checks for `coverMediaId`;
- contributor reference checks.

### case_summary

Needs:

- fixed field contract;
- fixed internal labels;
- strong required validation only for `lead` and `situation`;
- warnings for weak optional completion.

### content_builder

Needs:

- explicit block registry;
- per-block validation;
- stable preview/public serialization.

Important recommendation:

- do not start with too many block types;
- ship the contract and a small useful block set first.

## Projection Build Rules

The projection must be rebuilt from published snapshots, not from draft content.

Recommended rebuild triggers:

- page publish for `blog_page`, `media_page`, `case_page`
- page rollback for those page types
- page unpublish/archive later, if that lifecycle is added

Recommended behavior:

1. resolve published snapshot;
2. extract `publication_meta`;
3. extract `case_summary` where relevant if some public list fields ever need it;
4. upsert `cms_editorial_publications`;
5. replace contributor rows in `cms_editorial_publication_contributors`.

This keeps the projection deterministic and rebuildable.

## Public Collection Runtime Layer

Collection pages should read from the projection layer, not by parsing large bodies from section JSON.

Recommended first collection resolver capabilities:

- filter by `publication_kind`
- filter by `locale`
- order by `published_at desc`
- optional future filters by:
  - `practice_id`
  - `service_id`
  - `problem_id`
  - `is_featured`

Initial list cards should rely on structured metadata, not on ad hoc content-builder inspection.

## Admin API Direction

### What should stay the same

Do not create a separate admin CRUD subsystem for blog/media/case content bodies.

Authoring should stay inside the normal page workbench flow:

- page matrix/open editor
- page section editor
- validate
- draft save
- preview
- publish
- rollback

### What new APIs are actually needed

Minimal new backend surfaces:

1. page schemas and workbench support for:
   - `blog_page`
   - `media_page`
   - `case_page`
   - collection page types
2. section schema/validation support for:
   - `publication_meta`
   - `case_summary`
   - `content_builder`
3. collection runtime resolver support from `cms_editorial_publications`
4. lightweight selector support where frontend needs it:
   - lawyers selector
   - CMS users selector
   - existing practice/service/problem references

### What should not be added yet

Avoid adding:

- a custom publication workflow service with its own drafts;
- separate preview endpoints unrelated to page workbench;
- separate content-body CRUD endpoints.

## Frontend Impact

This backend shape gives frontend two understandable layers:

### 1. Detail page authoring

For `blog_page`, `media_page`, `case_page`:

- edit page as normal through page workbench;
- `publication_meta` is the structured admin form;
- `case_summary` exists only for case;
- `content_builder` is the dynamic body editor.

### 2. Collection/runtime pages

For `blog_collection_page`, `media_collection_page`, `case_collection_page`:

- edit intro/SEO in normal CMS form;
- read list items from runtime payload backed by the publication projection.

So frontend does not need to guess where collection cards come from.

## Recommended Delivery Order

### Phase 1 - schema and naming

- normalize naming in backend contracts to `blog_page`;
- register new page types;
- define section schemas.

### Phase 2 - page authoring

- enable page workbench/editor for `blog_page`, `media_page`, `case_page`;
- add validation rules.

### Phase 3 - published projection

- add `cms_editorial_publications`;
- add `cms_editorial_publication_contributors`;
- rebuild projection on publish/rollback.

### Phase 4 - collection pages

- add collection page schemas;
- add runtime resolvers from the projection.

### Phase 5 - frontend implementation

- page editors;
- collection page editors;
- public preview/render integration.

## Risks To Avoid

### Risk 1: over-universal builder too early

If `content_builder` starts with too many block types, we will spend more time on editor mechanics than on
delivering useful publication pages.

### Risk 2: content hidden only in body blocks

If title/authors/relations/source metadata are hidden inside free-form body content, collections and
filters become fragile very quickly.

### Risk 3: second publication CMS inside the CMS

If we create separate draft/publish storage for blog/media/case bodies, we will duplicate the hardest parts
of the system with very little product benefit.

## Practical Conclusion

The moderate implementation path is:

- keep the existing page/snapshot model as the only editorial source of truth;
- add a small published projection for collection/runtime use;
- implement three detail page types and three collection page types on top of that;
- keep `case_page` special only where it genuinely needs to be special: `case_summary`.

This is the most balanced way to get the feature set without building a second CMS inside the first one.
