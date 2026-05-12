# Release Contour Requirements

This document captures step-by-step requirements for the production-oriented CMS contour. Decisions are
added through the question/answer process before they become implementation work.

## Decision Index

- Decision 1: first production-oriented runtime mode.
- Decision 2: access boundary before indexing.
- Decision 3: target page set for the first production release.
- Decision 4: locales and regional variants.
- Decision 5: regional inheritance and append strategy.
- Decision 6: public URL structure for locales and regions.
- Decision 7: region slug policy.
- Decision 8: SEO validation policy.
- Decision 9: published state strategy.
- Decision 10: locale publication readiness.
- Decision 11: ERP and directory data boundary.
- Decision 12: admin roles and publication workflow.
- Decision 13: media and file storage.
- Decision 14: frontend rendering boundary and section specification.
- Decision 15: redirect map intake sources.
- Decision 16: deployment and runtime diagnostics.
- Decision 17: environment contours.
- Decision 18: admin and preview authentication.
- Decision 19: database migrations and seed data.
- Decision 20: backend and frontend contracts.
- Decision 21: release-critical testing.
- Decision 22: observability and CMS readiness diagnostics.
- Decision 23: page removal and archive policy.
- Decision 24: generated lists and related entities.
- Decision 25: initial content strategy.
- Decision 26: page type specification format.
- Decision 27: indexing go-live process.
- Decision 28: frontend cache and revalidation.
- Decision 29: admin UI scope and backend API boundary.
- Decision 30: backend release-ready definition.
- Decision 31: backup, rollback, and recovery policy.
- Decision 32: initial backend implementation order.

## Decision 1: First Production-Oriented Runtime Mode

The first production-oriented CMS runtime must be release-ready, but closed to indexing until a separate
explicit indexing decision is made.

This means the implementation should be built as real release software, not as a throwaway demo:

- stable Next.js public frontend, Next.js CMS frontend, and NestJS backend service boundaries;
- real public routing behavior;
- production-grade SEO metadata generation;
- sitemap and robots support;
- canonical and hreflang support;
- publish, rollback, route registry, and route alias diagnostics;
- release readiness diagnostics;
- environment-driven indexing policy;
- safe rollback path for application and content changes.

However, the runtime must not become search-indexable by accident.

Until the indexing decision is explicitly made, the release contour should enforce:

- `noindex, nofollow` policy for public pages;
- robots policy that blocks indexing;
- sitemap behavior that does not invite indexing of the not-yet-approved public surface;
- operator-visible diagnostics showing whether indexing is enabled or disabled;
- access only for explicitly allowed IPs before public go-live;
- a hard separation between "release-ready" and "approved for indexing".

## Domain Direction

The current live production site is on `actum.com.ua`.

The future primary domain is expected to be `actum.ua`.

During development and release preparation, `actum.ua` may be used as the future primary URL, but it must
remain closed to indexing until a separate go-live decision changes that policy.

The future migration direction is:

- `actum.ua` becomes the primary domain;
- old public URLs from `actum.com.ua` redirect to the corresponding new URLs on `actum.ua`;
- redirects must be planned through an explicit URL mapping and route alias/redirect policy, not as an
  ad hoc server rewrite;
- the switch from closed release contour to indexed public site must be a controlled release action.

## Legacy Redirect Map

The production-oriented release must include the old redirect and URL map from the current live site.

Before `actum.ua` becomes the indexed primary domain, the project must collect and review the current
public URL surface of `actum.com.ua`, including:

- currently indexed public URLs;
- existing redirect rules;
- old URLs that already redirect today;
- URLs visible in sitemap, navigation, canonical links, and hreflang links;
- high-value legacy URLs from analytics or search-console data when available.

The collected mapping must become an explicit migration artifact for the new CMS routing model.

Each legacy URL should resolve to one of these outcomes:

- a direct redirect to the corresponding new `actum.ua` route;
- a deliberate redirect to the nearest relevant replacement page;
- a documented "no equivalent" decision, handled through the chosen not-found or gone policy.

Redirects should be implemented through the CMS route alias/redirect policy or another documented routing
layer that can be tested and inspected. They should not exist only as undocumented load balancer or web
server rules.

The release acceptance checks must verify:

- no redirect loops;
- no unnecessary redirect chains;
- expected redirect status codes for old public URLs;
- canonical URLs point to the new primary domain after indexing is enabled;
- hreflang alternates use the new route set;
- removed URLs have an intentional handling policy.

## Decision 2: Access Boundary Before Indexing

Before the public go-live decision, the `actum.ua` release contour must be closed by access policy, not
only by SEO policy.

The selected baseline is:

- public frontend routes stay `noindex, nofollow`;
- access to the release-preparation public frontend is allowed only from explicitly approved IPs;
- admin and preview surfaces are strictly closed and require authentication, authorization, and the same
  or stricter network access boundary;
- admin and preview URLs must never rely on `noindex` as their primary protection;
- indexing can only be enabled after a separate go-live decision changes both the SEO policy and the
  access policy.

IP allowlist rules should be treated as runtime/infrastructure configuration and documented with the
release environment. If reviewers or contractors cannot use stable IPs, the exception must be explicitly
approved and implemented through a stronger identity-based access option rather than opening the release
contour publicly.

Any real change to load balancer rules, ingress, identity-aware access, DNS, Cloud Run, IAM, or related
runtime configuration remains governed by `gcp-infra-playbook`.

## Frontend Entry Point And Load Balancing

The deployment design should allow a dedicated frontend entry point for the new CMS public surface.

A separate frontend load balancer may be used for this release contour, but creating or changing actual
GCP load balancers, Cloud Run services, DNS, certificates, IAM, or deployment triggers is not part of this
documentation decision.

Any real infrastructure decision for load balancing, DNS, Cloud Run, Cloud Build, Cloud SQL, Cloud
Storage, Secret Manager, or IAM is governed by `gcp-infra-playbook` and requires the appropriate
confirmation and preflight before cloud state is read or changed.

## Decision 3: Target Page Set For The First Production Release

The first production release should target the full validated page set from `notstrapitest`, plus the
important public pages that were not implemented in the prototype.

This is the target release scope, not the first implementation slice. Implementation must still proceed
page type by page type, with each type passing preview, publish, runtime, SEO, redirect, and diagnostics
checks before the next larger surface is treated as ready.

Validated page types from `notstrapitest`:

- `services_root`;
- `practice_page`;
- `service_page`;
- `problem_page`;
- `lawyers_root`;
- `lawyer_page`;
- `articles_root`;
- `article_page`;
- `cases_root`;
- `case_page`.

Additional page types required for the production release:

- home page;
- about page;
- career page;
- advocate license page;
- contacts page.

The additional pages should not force the system into a universal visual page-builder model. They should
be implemented as explicit CMS page types with readable authoring fields, predictable templates, and the
same publishing discipline as the rest of the site.

Each production-release page type must define:

- authoring fields;
- route rules;
- locale behavior;
- SEO metadata requirements;
- preview payload shape;
- published snapshot contract;
- public frontend rendering requirements;
- redirect or alias behavior when relevant;
- release readiness checks.

The static or institutional pages may have a simpler domain model than service, lawyer, article, or case
pages. That simplicity should be preserved instead of forcing them through catalog or regional inheritance
logic that they do not need.

## Decision 4: Locales And Regional Variants

The production release must support three locales:

- `uk`;
- `ru`;
- `en`.

Ukrainian is the primary locale and must not use a public URL prefix.

Unless a later routing decision changes this, the expected public locale prefixes are:

- `uk`: no prefix;
- `ru`: `/ru`;
- `en`: `/en`.

There must be no silent public fallback between locales. If a page is requested in a locale that is not
published, the runtime should return an intentional not-found, redirect, or unavailable result according
to the page type's routing policy. It must not quietly render another language.

Publishing must validate mandatory locale fields for the selected locale. Missing required locale content
is a publish blocker, not a frontend rendering problem.

Regional variants must follow the proven `notstrapitest` scope.

Regionality applies to the services tree:

- `services_root`;
- `practice_page`;
- `service_page`;
- `problem_page`.

Lawyers, articles, cases, and institutional pages are locale-only in the first production release unless a
later explicit decision changes their model.

Because regional pages increase the content matrix, regional support must be designed with strict
safeguards:

- every regional page variant has a stable base page relationship;
- regional content should use inheritance, explicit overrides, and controlled append rules rather than full
  copied pages by default;
- a regional variant should only be published when it passes page-type-specific quality checks;
- empty or low-value regional pages must not be published only because a region exists;
- canonical, hreflang, breadcrumbs, generated lists, and redirects must be region-aware;
- route uniqueness must account for locale, region, page type, and slug;
- preview must show the composed regional result, including inherited base content and regional
  overrides;
- release readiness must expose missing or invalid regional variants before go-live.

The implementation should preserve the working `notstrapitest` regional boundary instead of expanding
regionality to every page type by default.

## Decision 5: Regional Inheritance And Append Strategy

Regional pages in the services tree must be modeled as a base page plus a regional composition layer.

The regional page must not be a full independent copy of the base page by default. Instead, each regional
page type should be composed from:

- base page content;
- regional overrides;
- regional append content;
- region-specific directory or runtime data when the page type needs it.

The supported regional content strategies are:

- inherit: use the base page content as-is;
- override: replace the base page field or section with regional content;
- append: keep the inherited base content and add regional content to it.

Append is a first-class production requirement, but it must be explicitly controlled.

The ability to append content should be defined by the page and section schema. Some sections may allow
regional append, while other sections must remain inherit-only or override-only. The editor UI should not
offer append for sections where append would create duplicate, misleading, or structurally invalid public
content.

Each section type must declare its allowed regional strategies, for example:

- inherit only;
- inherit or override;
- inherit or append;
- inherit, override, or append.

Append rules must be deterministic:

- appended regional content is stored on the regional variant, not inside the base page;
- preview must show the final composed result and identify inherited, overridden, and appended content;
- publish must persist the final composed snapshot together with enough source metadata for diagnostics;
- rollback must preserve the selected regional strategies;
- release readiness checks must report invalid append usage;
- append must not bypass locale, SEO, quality, or route validation.

Draft dependency handling must also be explicit:

- changing a base/parent/source draft must not automatically create persisted child draft copies;
- dependent regional variants and inherited pages must be marked stale for authoring/review until
  revalidated;
- draft preview must recompose the result from the latest upstream drafts plus local override/append
  content;
- public snapshots must remain unchanged until normal publish or rebuild activates a new valid snapshot.

Append should be used to add meaningful regional context, not to create accidental duplicate pages. If a
regional page only repeats the base content without useful regional content, it should remain inherited or
unpublished according to that page type's quality policy.

## Decision 6: Public URL Structure For Locales And Regions

The production release must use a stable URL structure where the optional locale prefix comes before the
optional region slug, followed by the page path.

The selected structure is:

`/{locale?}/{region?}/{page-path}`

Ukrainian remains the primary locale and has no locale prefix.

Examples:

- `uk`, base page: `/services/family-law`;
- `uk`, regional page: `/kyiv/services/family-law`;
- `ru`, base page: `/ru/services/family-law`;
- `ru`, regional page: `/ru/kyiv/services/family-law`;
- `en`, base page: `/en/services/family-law`;
- `en`, regional page: `/en/kyiv/services/family-law`.

This route shape applies to regional services-tree pages.

The route builder, published route registry, redirect map, canonical URLs, hreflang alternates,
breadcrumbs, sitemap generation, and release readiness checks must all use the same route structure for
regional services-tree pages.

The region slug policy is still a separate decision. The system must explicitly decide whether region
slugs are shared across locales or localized per locale before implementation.

The CMS must reject ambiguous routes where a locale prefix, region slug, static root path, or page slug
could be interpreted in more than one way.

## Decision 7: Region Slug Policy

Region canonical slugs must be shared across locales.

The canonical region slug is a stable technical URL identifier, for example:

- `/kyiv/...`;
- `/ru/kyiv/...`;
- `/en/kyiv/...`.

Localized region names belong to content, tokens, and display metadata, not to the canonical region slug.
For example, the same `kyiv` slug may render with Ukrainian, Russian, or English display text depending
on locale and token case.

The CMS should still support region route aliases for legacy or alternative spellings.

Allowed use cases for region aliases:

- old URLs from `actum.com.ua`;
- historical spellings;
- localized or transliterated region variants that already exist in the live URL surface;
- temporary migration redirects.

Region aliases must not create a second canonical URL for the same regional page. They must resolve to
the canonical route through the redirect or alias policy.

The route registry and release checks must enforce:

- one canonical region slug per region;
- no duplicate canonical slugs;
- no alias conflicts with locale prefixes, static roots, page slugs, or other region slugs;
- no redirect loops between region aliases and canonical routes;
- canonical, hreflang, sitemap, and breadcrumbs use canonical region slugs.

## Decision 8: SEO Validation Policy

The production release must use a balanced SEO validation policy.

Critical SEO and routing problems must block publishing. Quality, completeness, and optimization issues
should produce warnings unless they make the published page technically invalid or misleading.

Every publishable page variant should have SEO data for its locale and regional context when relevant:

- `title`;
- `h1`;
- `meta_description`;
- canonical URL;
- robots policy;
- hreflang alternates;
- breadcrumbs;
- Open Graph metadata;
- structured data / JSON-LD when the page type supports it;
- sitemap inclusion policy.

Publish blockers:

- missing `title`;
- missing `h1`;
- missing or invalid canonical route;
- unknown locale;
- unknown region for a regional page;
- route conflict in the published route registry;
- broken hreflang that points to a non-existing published page variant;
- unknown token in SEO text or route-critical content;
- robots or indexing policy conflicts with the selected release mode;
- invalid structured data when the page type requires structured data for publication.

Warnings:

- missing `meta_description`;
- missing page-specific Open Graph image when a valid fallback exists;
- title or description length outside recommended ranges;
- regional page is too similar to the base page;
- regional page has little unique regional content;
- page will not be included in sitemap because of the selected policy;
- optional structured data is incomplete;
- non-critical social metadata is incomplete.

The closed release contour must still generate and validate SEO metadata, canonical URLs, hreflang, and
sitemap policy even while indexing is disabled. `noindex` is a release-mode setting, not an excuse to skip
SEO validation.

## Decision 9: Published State Strategy

The first production release should use a snapshot-first published state model, extended with explicit
dependency tracking and stale rebuild diagnostics.

The project should not introduce a full published graph layer as a separate required architecture for the
first release.

The proven `notstrapitest` approach remains the baseline:

- publish creates a durable current snapshot for the page variant;
- public frontend reads only published/current state, not draft authoring tables;
- snapshots contain enough payload for deterministic public rendering;
- route registry stores the current published routes and aliases;
- dependency tracking identifies which pages became stale after relevant source changes;
- stale rebuild queue and release readiness diagnostics show what should be republished or rebuilt.

For the current scope, this is more rational than adding a separate full published graph layer. The main
complexity drivers that would justify that layer are intentionally limited:

- regional inheritance is scoped to the services tree;
- lawyers, articles, cases, and institutional pages are locale-only;
- dependency tracking has already been proven in the prototype without a full graph architecture.

The implementation should still preserve useful source metadata inside snapshots and publish records:

- base page identifier and version;
- regional override identifier and version when relevant;
- regional append strategy when relevant;
- source section identifiers where diagnostics need them;
- published route and canonical route;
- locale and region;
- publish job and author metadata.

A fuller published graph may be reconsidered later only if concrete release requirements prove that
snapshot-first plus dependency tracking is insufficient.

### Section-Level Authoring And Publication

Sections are independent authoring units.

Each page section must have its own draft and published versions. Every section operation must record the
actor and timestamp, including at minimum:

- create author and date;
- update author and date;
- publish author and date;
- archive, disable, or rollback author and date when those operations exist.

Section publication does not use one universal flow. Section publish mode is schema-defined:

- `independent` sections can publish their own new published section versions;
- `with_page` sections receive new published versions only as part of successful page publish.

The public frontend must not assemble pages from live section tables or from "latest published section"
lookups. The public frontend receives only a complete published page snapshot/public payload.

Independent section publication must therefore activate public content by creating a new complete page
snapshot:

- the changed section points to the newly published section version;
- unchanged sections remain pinned to the exact section versions from the previous page snapshot;
- page-level metadata, route, SEO, breadcrumbs, quality state, and render payload remain part of the
  complete page snapshot;
- page-level validation still runs before the new snapshot becomes current.

For `with_page` sections, successful page publish must commit the new section published versions and the
new current page snapshot atomically. If section validation or critical page-level validation fails, the
attempt must not persist new `with_page` published section versions and must not activate a new public
current page snapshot.

For `independent` section publication, the published section version may remain in authoring history even
when a later affected-page rebuild fails, but the invalid rebuilt page snapshot must not become current.

Page snapshots must reference the exact section versions used to render them. Rollback of a page must
restore the page to a historical set of section versions, not rebuild the page from whatever section
versions are latest at rollback time.

Regional inheritance, override, and append behavior must work at section level where the section schema
allows it. Section schemas must declare whether a section supports inherit, override, append, or a subset
of those strategies for regional variants.

Section composition must also support field-level policies. A section may inherit as a whole, but append or
override may need to apply only to selected fields inside that section. For example, a section may inherit
its title, override an introduction, and append additional regional items to a list field. The section
schema must therefore declare field composition policies where whole-section policy is not precise enough.

Some sections may be global-owned or external-source-backed rather than purely page-owned. The first known
case is a price section: base service prices should come from one shared source so core service prices can
be changed in one place. Pages that show that price section may inherit the shared source, override
allowed presentation fields, or append contextual notes where the section schema allows it. The first
release does not need to implement the full price catalog before the section model exists, but the section
model must not make global-owned or external-source-backed sections impossible.

For the first release, inherit/override/append protection is schema-defined. A protected global section
such as footer should be modeled as inherit-only in schema rather than through a separate parent/source
lock policy. A regional or child section may only append or override fields explicitly allowed by the
section/page schema.

Section layout must distinguish movable and fixed sections. Some sections can be reordered by editors,
while others are fixed by page type or layout slot. The page snapshot must preserve the section order and
layout slot used for rendering.

Article pages and case pages need an insertion-zone model. They may have fixed starting sections and fixed
ending sections, while allowing editors to add and reorder content sections only inside the body zone
between those fixed boundaries. The model should support this shape without making all page types use the
same flexible section layout.

## Decision 10: Locale Publication Readiness

All supported locales must be handled through the same publication readiness rule.

The system supports `uk`, `ru`, and `en`, but support for a locale does not mean that every page must be
published in that locale immediately.

A page variant is publishable only when that exact locale/page variant passes required content, routing,
SEO, and quality checks.

If a locale version has critical missing content, it must not be published.

This applies to every supported locale:

- `uk`;
- `ru`;
- `en`.

There must be no special rule that allows incomplete English pages, incomplete Russian pages, or
incomplete Ukrainian pages to appear publicly.

Unpublished locale variants:

- must not be returned by public route lookup;
- must not be included in sitemap;
- must not appear as hreflang alternates;
- must not be silently replaced with another locale;
- must be visible in release readiness diagnostics as missing, incomplete, or intentionally not published.

The first release can therefore support all three locales technically while publishing each locale/page
variant only when it is actually ready.

## Decision 11: ERP And Directory Data Boundary

The first production release should use a hybrid directory-data model.

Critical directories may be created and maintained in CMS for the first release, but the data model must
already include explicit boundaries for future ERP integration.

The CMS model must support:

- stable internal IDs;
- optional external ERP IDs;
- source ownership metadata;
- clear separation between ERP-owned fields and CMS-owned fields;
- diagnostics for records that are missing expected external IDs;
- future idempotent import from ERP without rewriting the page model.

ERP-owned fields should be treated as read-only from the CMS perspective once ERP integration is active.

CMS-owned fields may include:

- public slugs;
- page-owned route metadata;
- SEO fields;
- authoring sections;
- page visibility and publish state;
- CMS-specific ordering or editorial display settings;
- regional override and append content where the page type supports it.

For the first release, the project must not implement ERP write-back unless a later explicit decision
approves it. Writing CMS edits back into ERP is a separate, higher-risk integration and should not be
introduced as an accidental side effect of directory management.

If ERP is unavailable after integration is introduced, the public site must continue to render from the
last valid published state. ERP availability must not be required for ordinary public page rendering.

## Decision 12: Admin Roles And Publication Workflow

The first production release must include role-based access and a lightweight publication workflow.

Required roles:

- `admin`;
- `editor`;
- `viewer`.

Required baseline permissions:

- `viewer` may inspect published state, diagnostics, and permitted admin screens without changing content;
- `editor` may create and edit draft content, run preview, and move content to review when allowed;
- `admin` may manage users, permissions, publication, rollback, release readiness, and critical settings.

Publishing must not be available to every content editor by default.

The required workflow is:

- `draft`;
- `ready_for_review`;
- `published`;
- `archived` when a page type supports removal from the public surface.

The first release does not require a full enterprise approval chain with separate author, legal reviewer,
marketing reviewer, scheduled approval, and multi-step sign-off. That can be added later if the real
editorial process proves it is needed.

The admin UI must make publication state visible:

- current draft status;
- last published snapshot;
- who changed the page;
- who published the page;
- publish blockers;
- warnings;
- stale/rebuild status;
- rollback availability.

Publish and rollback actions must be audited.

The release readiness cockpit must include workflow problems, for example:

- pages stuck in draft;
- pages ready for review but not published;
- locale variants with critical missing content;
- regional services-tree variants with invalid override or append state;
- pages with publish blockers;
- stale published snapshots.

## Decision 13: Media And File Storage

The first production release must include a real media and file model.

Files must not be stored directly in the database. The database stores metadata and references only.

Physical file storage must use Cloud Storage or a compatible object storage service.

The CMS must have media records for uploaded or referenced files.

Required media metadata should include:

- stable media identifier;
- storage bucket or provider identifier;
- storage object key;
- public URL or public URL derivation data;
- MIME type;
- file size;
- checksum or equivalent integrity marker when available;
- original filename;
- media usage type;
- alt text when the asset is used as a public content image;
- title when the asset is used as a public content image and the page type requires it;
- upload author and timestamps;
- replacement/deprecation status when relevant.

Supported media usage types should include at least:

- `lawyer_photo`;
- `article_cover`;
- `og_image`;
- `license_document`;
- other page-type-specific public content assets as the templates require.

The system must enforce MIME type and file size restrictions. These restrictions should be configurable by
usage type where needed.

Public media URLs must be stable enough for published content, SEO metadata, Open Graph previews, and
cached frontend rendering.

Media deletion must be safe:

- a file used by a current published snapshot must not be physically deleted;
- a file referenced by historical snapshots should be retained or intentionally archived according to the
  retention policy;
- the admin UI should show where a media record is used before allowing deletion;
- replacing an asset should create a new controlled state rather than silently mutating historical
  published content.

The first release does not require a large, polished media-library UI. A minimal administrative interface
is acceptable if the data model, validation, usage tracking, and safe deletion rules are correct.

## Decision 14: Frontend Rendering Boundary And Section Specification

The public frontend must render pages from published public contracts.

The frontend must not know about draft or authoring tables and must not decide what is publishable.

Required frontend boundary:

- public rendering uses a published snapshot or public payload;
- frontend does not read authoring endpoints for public routes;
- frontend does not reconstruct publish rules;
- frontend does not decide route, locale, region, SEO, or quality validity;
- preview uses the same rendering layer where practical, but receives a preview payload from protected
  backend endpoints;
- runtime sections may use backend-provided public read models only when explicitly allowed by the section
  contract.

Runtime sections are allowed, but only through controlled public contracts.

For runtime sections:

- backend owns the public read model;
- the read model must not expose draft state;
- the section must define cache, fallback, and failure behavior;
- if runtime data is unavailable, the frontend must follow the section policy instead of improvising;
- runtime sections must be included in readiness and diagnostics where they affect release quality.

The final section structure from `notstrapitest` is not automatically frozen into the production release.
Before implementing each page type, the project must define a page/section specification.

Each page type specification must describe:

- page purpose;
- route rules;
- locale behavior;
- regional behavior when relevant;
- authoring fields;
- section list and section order rules;
- which sections are required, optional, repeatable, generated, or runtime;
- section-level inherit, override, and append rules where regional variants exist;
- field list for each section;
- field validation rules;
- SEO fields and blockers/warnings;
- preview payload shape;
- published snapshot/public payload shape;
- runtime read models where needed;
- fallback and error behavior;
- readiness checks.

This means page and section structure should be refined during implementation, but every refinement must
be made explicit before that page type is considered release-ready.

## Decision 15: Redirect Map Intake Sources

The redirect map must be collected from multiple sources, not from a single crawl only.

Required redirect-map intake sources:

- crawl of the current public site;
- current sitemap;
- robots, canonical, and hreflang URLs;
- existing redirect rules when available;
- Search Console or analytics export when available;
- manually added known legacy URLs.

The collected URLs must be normalized into a reviewable table with at least:

- `old_url`;
- `new_route`;
- `status`;
- `reason`.

## Decision 16: Deployment And Runtime Diagnostics

The first production release should keep the deployment model close to the proven `notstrapitest` path.

The baseline deployment flow is:

`GitHub trigger -> Cloud Build -> Cloud Run`

The project should not add separate deployment orchestration, Cloud Tasks, Scheduler, or a dedicated worker
service only because the system has a CMS publish/rebuild process.

For the first release:

- application code changes are deployed through git-based Cloud Build triggers;
- Cloud Run is the runtime target for the public frontend, CMS frontend, and backend services;
- build, deploy, revision, and runtime diagnostics live primarily in Google Cloud tools;
- manual Cloud Run changes are not the normal deployment path;
- any actual Cloud Build trigger, Cloud Run service, load balancer, DNS, IAM, or secret change is governed
  by `gcp-infra-playbook`.

This decision is about infrastructure and deployment. It does not remove CMS-level publication
diagnostics. The CMS should still show content readiness, publish blockers, route problems, stale snapshot
state, and redirect-map issues where those are product concerns rather than Cloud Run deployment concerns.

The first release does not require a separate Cloud Run worker or Cloud Tasks-based rebuild pipeline.
Those may be reconsidered later only if the proven `notstrapitest`-style approach becomes insufficient in
real operation.

## Decision 17: Environment Contours

The target cloud environment model for CMS is:

- `develop`;
- `release`.

The project starts with the `develop` contour only.

The `release` contour will be introduced later, after the implementation and runtime requirements are
ready enough to justify production-oriented resources.

Expected contour roles:

- `develop`: implementation, integration checks, internal validation, and non-release testing;
- `release`: production-oriented preparation, future `actum.ua` release candidate, closed by noindex and
  IP allowlist until a separate go-live decision.

The absence of a `release` contour at the start must not weaken the code or architecture quality. Code
should still be written as release-grade where the module is in scope.

Creating or changing real `release` resources is not part of this decision. Any future Cloud Run, Cloud
Build, DNS, load balancer, Cloud SQL, Cloud Storage, Secret Manager, IAM, or environment-variable work for
`release` must follow `gcp-infra-playbook` and require the appropriate confirmation before cloud state is
read or changed.

## Decision 18: Admin And Preview Authentication

The first production release must use DB-backed users with secure session-based authentication for admin
and preview surfaces.

The selected baseline is:

- users are stored in the CMS database;
- passwords are stored only as secure password hashes;
- roles and permissions are stored in the database;
- admin and preview surfaces require login;
- frontend must not store access tokens in `localStorage`;
- browser authentication should use secure `httpOnly` cookies or an equivalent server-controlled session
  flow;
- sessions should support expiration and rotation;
- login, logout, failed login, and permission-sensitive actions should be auditable.

Bootstrap admin creation must be safe:

- no real passwords in git;
- no hard-coded bootstrap credentials;
- bootstrap password or bootstrap creation secret must come from approved secret/runtime configuration;
- bootstrap flow should be disabled or idempotent after initial setup.

Two-factor authentication and external SSO/IAP may be considered later, but they are not required for the
first production release unless access-risk assessment changes.

## Decision 19: Database Migrations And Seed Data

The first production release must use explicit SQL migrations and a strict migration runner.

The selected baseline is:

- TypeORM `synchronize` is disabled in every shared or cloud environment;
- database schema changes are made through explicit SQL migrations stored in the repository;
- the migration runner records applied migrations in the database;
- migrations must not auto-run during Cloud Run service startup;
- cloud migrations must run manually or through an explicitly confirmed migration step;
- migration filenames must be unique;
- migration ordering must be monotonic and unambiguous;
- the migration runner must fail on duplicate sequence numbers, duplicate filenames, or ordering
  ambiguity;
- migration execution must be idempotent at the runner level;
- dangerous migrations must have an explicit rollback or recovery plan documented before execution.

Automatic down migrations are not required for every migration, but release-impacting schema changes must
have a practical rollback path. That rollback path may be restore-from-backup, forward-fix migration, or
another documented recovery procedure depending on the change.

Seed data must be separated by purpose:

- reference seed: stable required dictionaries or baseline records needed by the application;
- demo/dev seed: local or develop-only sample data for testing and implementation;
- bootstrap/admin seed: safe initial admin creation controlled through approved secret/runtime
  configuration.

Seed rules:

- no real secrets in seed files;
- no real passwords in git;
- no production credentials in markdown or SQL;
- demo/dev seed must not be required for release runtime;
- reference seed must be safe to apply repeatedly or guarded by stable keys.

## Decision 20: Backend And Frontend Contracts

The first production release must use versioned, typed contracts between the NestJS backend and the
Next.js frontend.

The selected baseline is:

- public payloads include `schemaVersion`;
- preview payloads include `schemaVersion`;
- page payloads are typed per page type;
- section payloads are typed per section type;
- `cms-back` publishes the API contract as OpenAPI;
- `site-front` and `cms-front` use generated typed clients for backend APIs where practical;
- backend and frontend must not exchange arbitrary unvalidated JSON for publishable pages;
- DTO or schema validation is required at contract boundaries;
- public API and admin/private API are separated;
- changes to published/public payload shape are treated as contract changes;
- incompatible contract changes must update OpenAPI, payload schemas, and generated clients in the same
  feature cycle where practical.

The frontend should handle unsupported or invalid payload versions intentionally rather than rendering
broken pages.

Preview and published payloads may share structure where practical, but they do not have to be identical.
Preview payloads may include draft-only diagnostics, source markers, blockers, warnings, and editor-facing
metadata that must never appear in the public payload.

Public payloads must contain only data safe for public rendering.

## Decision 21: Release-Critical Testing

The first production release must include focused tests for release-critical behavior.

The project does not require a vanity coverage percentage. Tests should protect the behavior that would
make the CMS unsafe, unstable, or difficult to release if broken.

Required test categories:

- unit tests for pure domain logic;
- integration tests for database and publish flows;
- contract tests for backend/frontend payload schemas;
- smoke tests for critical user and public-runtime paths.

Unit test candidates:

- route builder;
- locale and region parsing;
- token resolver;
- section composition;
- inherit, override, and append strategy selection;
- SEO validation;
- redirect decision logic;
- permission checks where they are pure enough to isolate.

Integration test candidates:

- migration runner success path;
- migration runner duplicate and ordering failures;
- database module connection and health behavior;
- publish flow;
- snapshot creation;
- current snapshot selection;
- route registry writes;
- route aliases and redirect resolution;
- rollback behavior;
- media usage blocking deletion of published assets.

Contract tests must verify that backend public and preview payloads match the schemas expected by the
frontend, including `schemaVersion`, page type, section types, SEO fields, route fields, and runtime
section contracts.

Smoke tests should cover at least:

- admin login;
- preview;
- publish;
- public route lookup;
- public page rendering from published payload;
- rollback;
- redirect map validation for representative old URLs.

Large brittle tests from `notstrapitest` should not be copied as the desired pattern. The clean CMS should
prefer smaller tests with clear fixtures, explicit contracts, and focused assertions.

## Decision 22: Observability And CMS Readiness Diagnostics

The first production release must combine Google Cloud diagnostics with CMS-level release readiness
diagnostics.

Google Cloud remains the primary place for infrastructure and runtime diagnostics:

- build status;
- deploy status;
- Cloud Run revisions;
- runtime logs;
- infrastructure errors;
- service-level runtime configuration.

The CMS must provide product-facing readiness diagnostics that are visible to operators and editors.

The release readiness cockpit should include at least:

- publish blockers;
- warnings;
- incomplete locale variants;
- invalid regional services-tree variants;
- stale snapshots;
- route conflicts;
- broken aliases and redirects;
- redirect-map coverage issues;
- missing media;
- missing required alt/title metadata;
- sitemap exclusion reasons;
- robots and indexing mode;
- pages stuck in draft;
- pages ready for review but not published;
- failed or incomplete directory/ERP-sync records when integration exists;
- runtime section health when a section depends on a public read model.

CMS diagnostics should help answer product questions that Cloud Run logs cannot answer, for example:

- why a page cannot be published;
- why a page is not in sitemap;
- why hreflang is missing;
- why a redirect target is unresolved;
- why a snapshot is stale;
- which media asset blocks deletion.

The first release does not require a full custom metrics, tracing, and alerting stack beyond what is
provided or configured in Google Cloud. That can be expanded later if real operational needs justify it.

## Decision 23: Page Removal And Archive Policy

Published pages must not be physically deleted through ordinary editorial actions.

The normal way to remove a page from the public surface is soft archive or unpublish with explicit route
handling.

When a published page is removed from the public surface, the CMS must require an intentional route
outcome:

- redirect to a replacement page;
- `410 Gone`;
- `404 Not Found`;
- another documented outcome approved for the page type.

Historical snapshots should be retained for audit, rollback, and debugging according to the retention
policy.

Archive or unpublish must update or affect:

- current published state;
- route registry;
- route aliases and redirect policy;
- sitemap inclusion;
- hreflang alternates;
- canonical references;
- generated lists where the page appears;
- release readiness diagnostics.

Physical deletion is allowed only as an administrative maintenance operation with strict checks, for
example:

- the page has no current published snapshot;
- the page is not referenced by active redirects or aliases;
- the page is not used by generated lists or other published payloads;
- retention policy allows deletion;
- an audit record is created.

The first release should prefer safe archive behavior over hard deletion.

## Decision 24: Generated Lists And Related Entities

Generated sections and related-entity lists must be backend-owned.

The frontend should render generated sections from published payloads or explicitly allowed public read
models. It must not reconstruct CMS visibility, publish, locale, region, or ordering rules on its own.

Generated lists for public pages must use published/current state and approved public read models only.
They must not read draft or authoring state.

Generated section examples include:

- practice lists;
- service lists;
- problem lists;
- lawyer lists;
- office lists;
- article author blocks;
- case lawyer blocks;
- other page-type-specific related-entity sections.

Generated list rules:

- unpublished entities must not appear on public pages;
- entities excluded by visibility policy must not appear;
- locale readiness must be respected;
- regional services-tree visibility must be respected where relevant;
- ordering must be deterministic;
- randomization, if used for fairness, must be performed at publish or controlled read-model generation
  time and stored or made reproducible according to the section policy;
- section payloads must include enough metadata for diagnostics when an expected item is missing.

Runtime read models are allowed for generated sections such as lawyers or offices, but only through the
controlled public-contract approach described in the frontend rendering boundary.

## Decision 25: Initial Content Strategy

Production content migration is not decided yet.

The final strategy for moving or creating production content will be made later, after the relevant CMS
code, page types, and section contracts are implemented well enough to evaluate real content needs.

The project must not blindly copy the `notstrapitest` database or treat prototype content as production
seed data.

Until the production content strategy is decided, the implementation may define only the minimal
reference/test content needed to validate code behavior.

Minimal reference/test content may include:

- supported locales: `uk`, `ru`, `en`;
- at least one canonical region such as `kyiv`;
- the required static roots for the validated route shape;
- one practice;
- one service under that practice;
- one problem under that service;
- one lawyer;
- one office;
- one article;
- one case;
- one media record for an image usage type;
- one legacy redirect example.

This minimal content must exist only to test migrations, route building, preview, publish, snapshots,
generated lists, SEO validation, media references, and redirect behavior.

Demo/test content must not be treated as final production content and must not be required by the future
release runtime.

## Decision 26: Page Type Specification Format

Each production page type must have its own markdown specification before implementation.

The project should not keep all page-type rules only in code and should not hide page structure decisions
inside DTOs without product documentation.

One page type should have one focused spec. This keeps discussion, review, implementation, and later
changes manageable.

Each page type specification must include at least:

- page purpose;
- route pattern;
- locale behavior;
- regional behavior;
- source of data;
- authoring fields;
- section list;
- fields for every section;
- required, optional, repeatable, generated, and runtime section markers;
- inherit, override, and append rules where regional variants exist;
- SEO blockers and warnings;
- preview payload shape;
- public payload shape;
- generated or runtime read models when needed;
- readiness checks;
- test expectations.

The page type spec must be written before that page type is treated as ready for implementation. The spec
may evolve during implementation, but material changes must be reflected in markdown together with code.

## Decision 27: Indexing Go-Live Process

Switching from the closed release-preparation mode to the indexed public site must be a controlled
go-live process.

The project must not treat indexing go-live as only a single environment-variable flip.

The selected baseline is:

- go-live requires an explicit confirmation;
- go-live uses a documented checklist;
- the technical indexing switch is a controlled configuration change;
- access policy changes are reviewed together with SEO/indexing changes;
- rollback plan is known before indexing is enabled.

Before indexing is enabled, the project must verify at least:

- release contour is deployed and checked;
- public access policy is intentionally changed from closed/IP-allowlisted mode;
- robots policy changes from blocking to public according to the go-live decision;
- `X-Robots-Tag` noindex policy is removed where appropriate;
- sitemap returns the intended published URLs;
- canonical URLs point to `actum.ua`;
- hreflang alternates are correct and only include published locale variants;
- legacy redirect map is applied and representative old URLs are tested;
- no redirect loops or unnecessary redirect chains exist;
- release readiness cockpit has no go-live blockers;
- critical media, OG, structured data, and SEO checks pass;
- analytics and Search Console readiness are reviewed when available;
- application and content rollback paths are known.

The indexing flag or runtime setting may be the technical mechanism for enabling indexing, but it is not
the complete release process.

## Decision 28: Frontend Cache And Revalidation

The first production release must support explicit frontend cache revalidation after backend publish and
rollback actions.

The selected baseline is Next.js cache/revalidation by affected routes or tags.

The backend publish and rollback flows must be able to expose which public surfaces were affected by a
content change, for example:

- the page route itself;
- locale variants;
- regional services-tree variants when relevant;
- generated lists that include the page;
- breadcrumbs or parent pages affected by child route changes;
- sitemap;
- route aliases or redirects affected by the change.

The frontend may cache published payloads or rendered pages, but cache behavior must not break the CMS
truth boundary:

- frontend must never fall back to draft or authoring state for public routes;
- stale cache must be diagnosable;
- failed revalidation should create a visible warning or operational signal;
- rollback must trigger the same kind of affected-route revalidation as publish;
- sitemap, robots, route registry, and redirect behavior must have explicit cache policies.

The exact Next.js implementation details may be decided during frontend implementation, but the backend
must provide enough affected-route or affected-tag information for predictable revalidation.

## Decision 29: Admin UI Scope And Backend API Boundary

The detailed admin UI screen scope will be decided later during frontend implementation.

The current project focus is the backend CMS capability and the contracts that the frontend admin shell can
use.

The backend must implement the controllers, APIs, validation, permissions, and diagnostics needed for the
production CMS workflows, even if the exact frontend screen layout is specified later.

Backend administrative capabilities should cover the release-required functions already defined in this
document, including:

- authentication and sessions;
- users, roles, and permissions;
- page authoring APIs;
- preview APIs;
- publish APIs;
- rollback APIs;
- snapshot history APIs;
- route registry and alias APIs;
- redirect-map APIs;
- release readiness diagnostics APIs;
- media record APIs;
- directory/reference record APIs;
- migration/health diagnostics where appropriate.

The frontend admin UI must be implemented as a separate frontend concern and should consume these backend
contracts rather than forcing backend logic into UI-specific shapes.

This decision intentionally avoids committing to a final screen list, layout, or UX workflow before the
backend contracts and page type specifications are ready.

## Decision 30: Backend Release-Ready Definition

The backend is release-ready only when it satisfies the defined CMS contracts and release-critical
behavior. A successful deploy to `develop` is not enough by itself.

Backend release-ready criteria:

- approved page type specifications exist for the implemented page types;
- implemented page types have APIs, DTOs, schema validation, and permission checks;
- preview works for implemented page types;
- publish works for implemented page types;
- rollback works for implemented page types;
- snapshot creation and current snapshot selection work;
- public payload contracts are versioned and validated;
- public API and admin/private API are separated;
- route registry works;
- route aliases and redirect map behavior work;
- SEO validation works with blockers and warnings;
- locale publication readiness works;
- regional services-tree inheritance, override, and append work;
- generated lists use published/current state and approved public read models;
- auth, sessions, RBAC, and audit requirements are implemented;
- media metadata and usage tracking work;
- safe media deletion rules are enforced;
- database migrations and seed rules are enforced;
- release readiness diagnostics expose content, route, SEO, media, locale, regional, and stale-state
  problems;
- affected routes or tags are available for frontend revalidation;
- release-critical unit, integration, contract, and smoke tests pass;
- public runtime does not depend on draft/authoring tables;
- public runtime does not require ERP availability for ordinary page rendering.

The backend may be considered ready per implemented slice before every future page type exists, but that
slice must meet the same release-ready quality bar for its scope.

## Decision 31: Backup, Rollback, And Recovery Policy

The production-oriented CMS must use layered recovery. CMS snapshot rollback is necessary but not enough
by itself.

Recovery layers:

- application code rollback;
- published content rollback;
- database backup and restore;
- media/file retention and restore;
- migration recovery;
- indexing go-live rollback.

Expected recovery model:

- application code rollback uses Cloud Run revisions and the git-based deployment path;
- published content rollback uses CMS snapshot rollback;
- database recovery uses Cloud SQL backup/export policy when cloud release resources exist;
- media recovery uses Cloud Storage or compatible object-storage retention/versioning policy;
- dangerous migrations require a documented recovery plan before execution;
- indexing go-live requires a documented rollback plan before indexing is enabled.

The first `develop` contour may use lighter recovery practices, but future `release` resources must not be
introduced without an explicit backup and recovery policy.

The first release does not require a full disaster-recovery program with formal RPO/RTO, standby
environment, and scheduled restore drills unless a later risk decision requires it. Those can be added
after the release contour and operational needs are clearer.

## Decision 32: Initial Backend Implementation Order

The first implementation phase should follow a backend-first order.

The project should not start with the full authoring system, full frontend admin UI, or every page type at
once.

The initial implementation order is:

1. Project skeleton: NestJS app, config validation, and health endpoint.
2. Database module and strict SQL migration runner.
3. Auth, secure sessions, RBAC, and bootstrap admin flow.
4. Core dictionaries and reference data: locales, regions, page types, and media metadata basics.
5. Route builder, route registry, and aliases.
6. Page type specification template.
7. First vertical page slice: `services_root` or `practice_page`.
8. Preview, publish, snapshot, and rollback for the first slice.
9. SEO validation and locale readiness for the first slice.
10. Regional inherit, override, and append for the services tree.
11. Generated lists.
12. Readiness diagnostics.
13. Redirect map intake and validation.
14. Backend/frontend contracts and affected-route or affected-tag revalidation support.

This order is a starting plan, not a permanent constraint. It may be adjusted when a concrete page type
spec or implementation risk proves a better sequence, but changes to the order should be documented.

The first implementation slices must stay small enough to be verified end to end. A slice is preferable to
a broad partial implementation when it proves config, database, auth, routing, preview, publish, snapshot,
rollback, and diagnostics for a real page type.
