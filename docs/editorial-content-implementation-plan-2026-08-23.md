# Editorial Content Implementation Plan - 2026-08-23

## Implementation status - 2026-08-23

The first backend convergence slice is implemented on `codex/editorial-content-v1`: finalized metadata,
legacy read compatibility, public privacy normalization, the closed typed block registry, common
Blog/Media/Case locale-family creation, projection fields for cover alt and primary service relation, and
ordered JSON-LD authors. The work remains unmerged and does not include legacy-content migration, public
collection pagination/refresh, the CMS typed editor, or site renderers.

The common backend foundation now also preserves the existing public editorial date when a legacy snapshot
without editor-owned `publishedAt` is republished for technical reasons. Such a republish does not create a
false material change or advance `contentModifiedAt`.

Normative product contract:

- [`editorial-content-specification-2026-08-23.md`](editorial-content-specification-2026-08-23.md)

Baseline gap audit:

- [`editorial-content-gap-audit-2026-08-23.md`](editorial-content-gap-audit-2026-08-23.md)

The June 2026 documents describe the original backend foundation. This plan is the current delivery order
for converging the existing implementation with the finalized product contract.

## Working Rules

- Preserve the existing page/section/snapshot lifecycle as the only source of truth.
- Treat projection tables as rebuildable published read models, never as draft/body ownership.
- Complete one vertical slice before expanding the shared mechanism to all kinds.
- Update backend contracts and documentation together.
- Do not include legacy-content migration in these slices.
- Do not modify or publish `cms-front` code as part of backend work unless separately authorized.

## Phase 0 - Baseline And Contract Gap Audit

Verify the current deployed and repository state before implementation:

- six page types and their schemas;
- section registries and current validators;
- projection tables and publish/rollback hooks;
- editorial admin facade;
- CMS navigation/list/editor implementation;
- site-front detail and collection renderers;
- JSON-LD output and public route handling.

Produce a gap checklist against the normative specification. Existing scaffolding is not proof of complete
functional behavior.

The repository baseline and prioritized findings are recorded in
[`editorial-content-gap-audit-2026-08-23.md`](editorial-content-gap-audit-2026-08-23.md).

Exit criteria:

- every required change is assigned to backend, CMS frontend, or site frontend;
- no implementation slice relies on an outdated June contract.

## Phase 1 - Common Backend Foundation

Complete or correct:

- `publication_meta` common fields and kind-specific branches;
- ordered author/reviewer relations with the five-author limit;
- normalized unlimited service-tree chains with one primary relation;
- the closed V1 block registry and typed per-block validation;
- stable block IDs and heading anchors;
- TOC configuration and diagnostics;
- optional fixed `editorial_cta`;
- agreed blocking-error and warning boundary;
- locale-family creation/copy rules;
- public date semantics;
- public route, canonical, and exact locale-switch contracts.

Database work must be additive and migration-safe. Existing published snapshots must not be silently
rewritten by a schema migration.

Required tests:

- pure validators for every block type;
- contributor limits/order/duplicates;
- service-tree membership, primary relation, and duplicates;
- media-mode conditional validation;
- locale creation and Ukrainian-first publication gate;
- stable anchors and deterministic serialization;
- material-change date behavior.

Exit criteria:

- backend DTOs fully describe the editor without frontend rule inference;
- preview and publish share the same validation semantics;
- existing publication projections can be rebuilt deterministically.

## Phase 2 - Blog Vertical Slice

Backend:

- finalize `blog_page` schema;
- implement corporate Actum author fallback and optional reviewer;
- implement Blog TOC rules;
- build Blog projection/card output;
- build Blog JSON-LD.

CMS frontend handoff:

- Blog list with agreed search/filter/sort/pagination;
- dedicated publication editor;
- author/reviewer and service-tree selectors;
- typed block editor;
- validation, preview, history, and publication actions.

Site frontend handoff:

- render public intro, TOC, V1 blocks, CTA, and runtime relations;
- render BlogPosting JSON-LD returned by backend;
- render Blog card and placeholder cover.

Exit criteria:

- one Ukrainian Blog page can be created, saved, validated, previewed, published, rendered, revised, and
  rolled back;
- one translation can be created and independently published after Ukrainian;
- public and preview results match except for expected lifecycle metadata.

## Phase 3 - Media Extension

Implement both explicit modes:

- `actum_article`;
- `external_reference`.

Required behavior:

- mode is never inferred;
- conditional field validation is backend-owned;
- external original authorship is not assigned to Actum;
- external-reference TOC is forced off;
- original source link is the primary public action;
- empty external-reference builder is valid without warning;
- card attribution and JSON-LD differ correctly by mode.

Exit criteria:

- both modes pass full create-to-publish and rollback smoke tests;
- frontend renders each mode without branching on accidental field presence.

## Phase 4 - Case Extension

Complete:

- required primary lawyer and up to four co-authors;
- optional ERP case relation;
- typed `case_summary`;
- optional body/TOC/CTA;
- case card attribution and result label;
- Article plus stable case-matter Thing JSON-LD.

Exit criteria:

- a minimal case with `case_summary` and an empty builder publishes with warnings only where specified;
- a long-form case uses the same builder as Blog and Media;
- lawyer order and case structured data remain stable after rollback.

## Phase 5 - Collections And Automatic Refresh

For each kind:

- finalize `seo + collection_header + editorial_listing`;
- return the agreed card contract;
- implement featured-first deterministic ordering;
- implement 12-item server pagination;
- return pagination metadata and current-page ItemList JSON-LD;
- implement independent collection preview/publication;
- implement technical refresh after detail publish/rollback/archive;
- preserve old live collection and expose stale/error state when refresh fails.

CMS list screens keep their separate 50-item administrative pagination.

Exit criteria:

- drafts and unpublished locale variants never enter public collections;
- featured cards appear only on the first public page and are not duplicated;
- out-of-range pages return 404;
- technical refresh does not alter collection SEO/header or public material dates;
- unpublished collections are never auto-published.

## Phase 6 - Archive And Unpublish

Deliver as a separately reviewable slice:

- permission model;
- archive/unpublish and restore lifecycle;
- public pointer and projection removal;
- automatic collection refresh;
- 410 behavior;
- audit/history preservation;
- hard delete only for eligible never-published drafts.

This phase does not block the initial Blog vertical slice.

## Phase 7 - Hardening And Acceptance

Contract verification:

- OpenAPI/DTO examples for all editable and runtime sections;
- preview versus published payload fixtures;
- JSON-LD fixtures for Blog, both Media modes, Case, and collections;
- exact route and locale-alternate fixtures.

Integration tests:

- publish and rollback projection rebuild;
- automatic collection refresh and failure recovery;
- stale diagnostics;
- pagination and deterministic ordering;
- invalid reference and media rejection;
- authorization and audit events.

Manual end-to-end matrix:

- Ukrainian, Russian, and English lifecycle;
- empty and rich builders;
- all V1 block types;
- warning-only publication;
- blocking validation;
- missing-cover placeholder;
- corporate author fallback;
- selected reviewer;
- multiple service-tree chains;
- both media modes;
- minimal and long-form cases;
- page 1/page 2 collection navigation without JavaScript.

## Explicit Follow-Up Specifications

Do not absorb these into the implementation opportunistically:

- legacy content migration and redirects;
- public tags, filters, and search;
- new builder block families;
- slug-change workflow;
- mixed editorial collection;
- additional recommendation algorithms.
