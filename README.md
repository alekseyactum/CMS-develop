# CMS

Clean implementation context repository for the Actum content platform.

This repository starts from the validated lessons of `notstrapitest`, but it is not a blind copy of that
prototype. `notstrapitest` was used as a working polygon for checking the CMS model without Strapi. `CMS`
is the place where the finished implementation should be specified deliberately, with production-oriented
project structure, documentation, and runtime discipline.

`CMS-develop` is the umbrella/context repository. The deploy-bearing service code is expected to live in
the canonical service repositories:

- `re-actum/site-front`;
- `re-actum/cms-front`;
- `re-actum/cms-back`.

## Website specifications

Use this index to find website requirements and their implementation contracts. Edit requirements in the
linked source documents, not here. The [project docs](docs/) contain the shared specifications and
historical records; service-specific acceptance criteria and API contracts stay in their service
repositories.

### Shared product and CMS requirements

- Site shell: [layout, header and contacts](docs/site-layout-and-header-requirements.md),
  [footer and legal documents](docs/site-footer-section-workbench.md),
  [global price section](docs/global-price-section-workbench.md),
  [lead questionnaire](docs/lead-questionnaire-contract-2026-07-16.md).
- Standalone pages: [Home](docs/home-page-structure-2026-08-05.md),
  [About](docs/about-page-structure-2026-10-06.md),
  [Career](docs/career-page-backend-requirements-2026-09-17.md),
  [License / partnership requirements](docs/license-page-backend-requirements-2026-09-27.md) and
  [page contract](docs/license-page-backend-contract-2026-09-27.md), including
  [the accent heading amendment](docs/license-hero-accent-title-rollout-2026-09-30.md#scope-and-source).
- Service hierarchy: [practices](docs/practice-page-structure-2026-06-13.md),
  [services](docs/service-page-structure-2026-06-16.md),
  [problems](docs/problem-page-structure-2026-06-15.md),
  [hierarchy amendments](docs/service-hierarchy-page-amendments-2026-06-28.md),
  [optional problem pages](docs/problem-optional-pages-2026-09-17.md),
  [intent page families](docs/intent-page-family-requirements-2026-07-30.md).
- Lawyers, offices and reviews: [lawyer profile pages](docs/lawyer-page-structure-2026-06-18.md),
  [exact lawyer qualification selection](docs/lawyer-exact-qualification-selection-2026-10-24.md),
  [reference data and public read models](docs/reference-data-and-runtime-model.md).
- Blog, media and cases: [editorial content requirements](docs/editorial-content-specification-2026-08-23.md),
  [editorial architecture](docs/editorial-content-architecture-2026-06-19.md),
  [CMS publication search and filters](docs/cms-publication-search-and-filter-specification-2026-10-19.md),
  [article import](docs/article-import-specification-2026-10-16.md),
  [media import](docs/media-import-specification-2026-11-06.md).
- Routing, SEO and locales: [redirects](docs/redirects-specification-2026-09-13.md),
  [JSON-LD architecture](docs/json-ld-architecture-2026-07-27.md) and
  [implementation requirements](docs/json-ld-implementation-requirements-2026-08-03.md),
  [Ukrainian-source translation](docs/cms-uk-source-translation-specification-2026-11-03.md).
- CMS authoring and publishing: [backend requirements](docs/backend-implementation-requirements.md),
  [section model](docs/section-model-foundation.md),
  [section authoring and versioning](docs/section-authoring-versioning-contract-2026-10-04.md),
  [roles and scoped publication](docs/cms-roles-and-scoped-publication-specification-2026-10-18.md),
  [stale-page refresh](docs/stale-page-refresh-contract-2026-10-12.md),
  [runtime and global section indicators](docs/runtime-global-section-indicators-2026-09-18.md).
- CMS-front tasks: [page and section authoring](docs/cms-front-page-authoring-task.md),
  [reference data](docs/cms-front-reference-data-task.md), [users](docs/cms-front-users-task.md),
  [source diagnostics and bulk page bootstrap](docs/source-diagnostics-and-bulk-bootstrap-task.md).

### Site-front specifications and acceptance criteria

- Forms: [global forms and integration testing](https://github.com/re-actum/site-front/blob/develop/specs/FEAT-global-site-forms.md),
  [working form delivery](https://github.com/re-actum/site-front/blob/develop/specs/FEAT-site-form-delivery.md)
  ([AC-7 and other acceptance criteria](https://github.com/re-actum/site-front/blob/develop/specs/FEAT-site-form-delivery.md#acceptance-criteria)).
- Directory: [lawyer filters](https://github.com/re-actum/site-front/blob/develop/specs/FEAT-lawyers-directory-filters.md) (draft).
- Rendering and UI: [schema-based page builders](https://github.com/re-actum/site-front/blob/develop/specs/FEAT-page-builder-sets.md),
  [removing MUI/Emotion](https://github.com/re-actum/site-front/blob/develop/specs/FEAT-remove-mui.md),
  [design tokens](https://github.com/re-actum/site-front/blob/develop/docs/design-tokens.md),
  [typography](https://github.com/re-actum/site-front/blob/develop/docs/type-scale.md).
- Public routing and content: [redirect handling](https://github.com/re-actum/site-front/blob/develop/docs/redirect-routing.md),
  [optional problem links](https://github.com/re-actum/site-front/blob/develop/docs/problem-links.md),
  [editorial video](https://github.com/re-actum/site-front/blob/develop/docs/editorial-video.md),
  [editorial data constraints](https://github.com/re-actum/site-front/blob/develop/docs/editorial-backend-gaps.md).
- [Full site-front specs directory](https://github.com/re-actum/site-front/tree/develop/specs) ·
  [technical documentation](https://github.com/re-actum/site-front/tree/develop/docs).

### CMS-back website and integration contracts

- Forms: [global forms and snapshot bindings](https://github.com/re-actum/cms-back/blob/develop/docs/global-site-forms-implementation.md),
  [integration-test API](https://github.com/re-actum/cms-back/blob/develop/docs/site-form-integration-api.md),
  [working delivery and ERP transport](https://github.com/re-actum/cms-back/blob/develop/docs/site-form-delivery-2026-11-05.md),
  [legacy career application API](https://github.com/re-actum/cms-back/blob/develop/docs/career-applications.md).
- Pages and shared UI: [Home](https://github.com/re-actum/cms-back/blob/develop/docs/home-page-backend-implementation.md),
  [About](https://github.com/re-actum/cms-back/blob/develop/docs/about-page-backend.md) and
  [single heading](https://github.com/re-actum/cms-back/blob/develop/docs/about-single-heading-transition.md),
  [Career](https://github.com/re-actum/cms-back/blob/develop/docs/career-backend.md),
  [License / partnership](https://github.com/re-actum/cms-back/blob/develop/docs/license-page-backend-contract-2026-09-27.md),
  [intent pages](https://github.com/re-actum/cms-back/blob/develop/docs/intent-pages-backend-implementation-plan.md),
  [optional problem pages](https://github.com/re-actum/cms-back/blob/develop/docs/problem-optional-pages.md),
  [sitemap](https://github.com/re-actum/cms-back/blob/develop/docs/sitemap-page-backend.md),
  [contact map coordinates](https://github.com/re-actum/cms-back/blob/develop/docs/contacts-map-coordinates.md),
  [public footer PDF links](https://github.com/re-actum/cms-back/blob/develop/docs/public-footer-legal-links.md).
- Lawyers and reviews: [public lawyer profile data](https://github.com/re-actum/cms-back/blob/develop/docs/lawyer-page-runtime-backend.md),
  [directory ranking and order editor](https://github.com/re-actum/cms-back/blob/develop/docs/tasks/lawyers-directory-ranking-and-order-editor-20261105.md),
  [partnership flag](https://github.com/re-actum/cms-back/blob/develop/docs/lawyer-license-partnership.md),
  [review office links](https://github.com/re-actum/cms-back/blob/develop/docs/review-office-links-2026-11-05.md),
  [review reconciliation API](https://github.com/re-actum/cms-back/blob/develop/docs/review-reconciliation-api-2026-10-23.md).
- Editorial: [public presentation](https://github.com/re-actum/cms-back/blob/develop/docs/editorial-public-presentation.md),
  [FAQ and recommendations](https://github.com/re-actum/cms-back/blob/develop/docs/blog-faq-recommendations.md),
  [video block](https://github.com/re-actum/cms-back/blob/develop/docs/editorial-video-block.md),
  [admin list and search](https://github.com/re-actum/cms-back/blob/develop/docs/editorial-admin-list-facade.md),
  [filter options](https://github.com/re-actum/cms-back/blob/develop/docs/editorial-filter-options-api-2026-10-27.md),
  [author names and photos](https://github.com/re-actum/cms-back/blob/develop/docs/editorial-author-display-frontend-task-2026-10-28.md),
  [ERP case articles integration](https://github.com/re-actum/cms-back/blob/develop/docs/deal-articles-client-handoff-2026-10-30.md)
  and [CMS workflow](https://github.com/re-actum/cms-back/blob/develop/docs/deal-articles-admin-workflow-2026-11-04.md).
- Routing, SEO and media: [locale alternates](https://github.com/re-actum/cms-back/blob/develop/docs/public-page-locale-alternates.md),
  [lawyer canonical URLs](https://github.com/re-actum/cms-back/blob/develop/docs/lawyer-auto-canonical.md),
  [lawyer SEO image](https://github.com/re-actum/cms-back/blob/develop/docs/lawyer-seo-image.md),
  [redirects API](https://github.com/re-actum/cms-back/blob/develop/docs/redirects-backend-contract-2026-09-13.md),
  [structured data readiness](https://github.com/re-actum/cms-back/blob/develop/docs/structured-data-publish-readiness.md),
  [public media delivery](https://github.com/re-actum/cms-back/blob/develop/docs/durable-media-serving.md),
  [signed preview](https://github.com/re-actum/cms-back/blob/develop/docs/signed-site-preview.md).
- Authoring and publication: [safe section saves](https://github.com/re-actum/cms-back/blob/develop/docs/section-authoring-safe-save.md),
  [content readiness](https://github.com/re-actum/cms-back/blob/develop/docs/section-content-readiness.md),
  [publication API](https://github.com/re-actum/cms-back/blob/develop/docs/publication-http-contract.md),
  [scoped SEO and content](https://github.com/re-actum/cms-back/blob/develop/docs/scoped-seo-publication-api-2026-10-18.md),
  [unified diagnostics and repair](https://github.com/re-actum/cms-back/blob/develop/docs/unified-diagnostics-and-publication-repair-2026-10-24.md),
  [page refresh API](https://github.com/re-actum/cms-back/blob/develop/docs/stale-refresh-http-contract.md),
  [refresh pause and resume](https://github.com/re-actum/cms-back/blob/develop/docs/page-refresh-pause-frontend-task-2026-10-27.md).
- Translation: [Ukrainian-source workflow](https://github.com/re-actum/cms-back/blob/develop/docs/uk-source-translations.md),
  [Cloud Translation EU](https://github.com/re-actum/cms-back/blob/develop/docs/cloud-translation-eu.md),
  [frontend and migrator integration tasks](https://github.com/re-actum/cms-back/blob/develop/docs/autotranslation-integration-tasks-2026-11-04.md).
- [Full CMS-back technical documentation](https://github.com/re-actum/cms-back/tree/develop/docs).

### Cross-repository specifications and amendments

- [AC-7 correction: delivery without a trusted client key](https://github.com/re-actum/site-front/blob/d7769cf8542e1e24a9e3c236fa807df8b122bc40/specs/FEAT-site-form-delivery.md#acceptance-criteria)
  ([docs-only commit](https://github.com/re-actum/site-front/commit/d7769cf8542e1e24a9e3c236fa807df8b122bc40);
  not yet merged into `site-front/develop`).
- Forms (site, CMS and ERP): [global forms integration requirements](https://github.com/re-actum/erp_backend/blob/tz/docs/tasks/site-cms-global-forms-integration-spec-20261102.md),
  [frontend integration task](https://github.com/re-actum/erp_backend/blob/tz/docs/tasks/site-cms-global-forms-frontend-task-20261102.md)
  and [working delivery requirements](https://github.com/re-actum/erp_backend/blob/tz/docs/tasks/site-cms-form-delivery-spec-20261104.md).
- Case articles (ERP and CMS): [publication requirements and the ERP deal number](https://github.com/re-actum/erp_backend/blob/tz/docs/tasks/deal-article-publication-spec-20261013.md),
  [ERP backend task](https://github.com/re-actum/erp_backend/blob/tz/docs/tasks/backend-erp-deal-article-20261013.md),
  [migrator task](https://github.com/re-actum/erp_backend/blob/tz/docs/tasks/migrator-deal-article-20261013.md)
  and [ERP design task](https://github.com/re-actum/erp_backend/blob/tz/docs/tasks/design-erp-deal-article-20261013.md).
- Amendments to shared UI and authoring:
  [About menu disclosure](https://github.com/re-actum/cms-back/blob/4e5b681f5cc19d944360cf9db9e9e88ce3cf6c42/docs/about-header-dropdown-contract-2026-11-05.md),
  [independent price text overrides](https://github.com/re-actum/cms-back/blob/01b6512b1d8dee17036d6480803d90bfddfc31d1/docs/price-text-overrides-rollout-2026-11-05.md#scope)
  and [locale navigation in the CMS workbench](https://github.com/alekseyactum/CMS-develop/commit/b415a0917f3983ec1047a5359f30847504c3af76).

## Goal

Build an Actum-controlled CMS for legal-site content where editors can manage structured pages, preview
the final result, publish stable snapshots, inspect live routing, and roll back safely.

The target CMS should support:

- page-owned authoring instead of forcing public content into catalog entities;
- base and regional page variants where regional inheritance is intentional;
- preview before publish;
- snapshot-first public rendering through a Next.js frontend;
- published route registry and route alias diagnostics;
- operator-facing release readiness checks;
- safe integration boundaries for ERP-owned read-only data;
- no secrets, tokens, passwords, or private keys in git.

## Service Shape

The clean implementation is expected to be split into three application services:

- a Next.js `site-front` service for public site rendering;
- a Next.js `cms-front` service for the admin/editorial shell;
- a NestJS backend for authoring state, permissions, preview assembly, publish, snapshots, routes,
  rollback, diagnostics, and integrations.

The backend owns the CMS truth and the versioned published snapshot contract. The frontends render public,
admin, and preview surfaces from backend contracts and must not become a second source of publish logic.

See [`docs/service-split-decision.md`](docs/service-split-decision.md).
See [`docs/cloud-develop-architecture.md`](docs/cloud-develop-architecture.md) for the agreed develop
Cloud Run, Cloud SQL, Secret Manager, IAM, media, and deployment architecture.

## Backend Implementation Direction

The backend should not inherit the large prototype services as its target structure. The clean
implementation should port proven behavior from `notstrapitest` through typed page contexts, versioned
preview/snapshot contracts, focused domain services, and tests around the preserved edge cases.

See [`docs/backend-implementation-requirements.md`](docs/backend-implementation-requirements.md).
See [`docs/cms-roles-and-scoped-publication-specification-2026-10-18.md`](docs/cms-roles-and-scoped-publication-specification-2026-10-18.md)
for the role matrix and scoped publication specification pending written approval: Ukrainian role
labels, separate page/publication/SEO/global editors, admin-only ERP and refresh commands, filtered
journal reads, exact SEO approval before first publication, and content/SEO publication isolation.
This is documentation only; existing users, application permissions and environments are unchanged.
See [`docs/stale-page-refresh-contract-2026-10-12.md`](docs/stale-page-refresh-contract-2026-10-12.md)
for the agreed safe refresh of published stale pages: one CMS queue/journal, published-only scoped
updates, ERP scheduler wake-ups every five minutes, coalescing, retries and separate cache delivery.
It supersedes earlier manual-only/runtime-freshness deferrals; it is a target specification, not a
completed implementation, runtime activation or authorization to publish content.
See [`docs/section-authoring-versioning-contract-2026-10-04.md`](docs/section-authoring-versioning-contract-2026-10-04.md)
for the agreed section working-copy, immutable saved-version, and same-version publication target.
It supersedes the older immediate-copy and duplicate-on-publish workflow requirements. This is a
specification with staged compatibility and acceptance gates, not an implemented or deployed change.
See [`docs/redirects-specification-2026-09-13.md`](docs/redirects-specification-2026-09-13.md) for the
approved redirect registry, CMS workflow, CSV import, public routing contract, migration-tool boundary,
acceptance criteria, and implementation responsibilities. This is a specification, not a deployed feature.
See [`docs/global-price-section-workbench.md`](docs/global-price-section-workbench.md) for the detailed
global price section editor, version history, validation, and publish-impact contract.
See [`docs/reference-data-and-runtime-model.md`](docs/reference-data-and-runtime-model.md) for the agreed
ERP-imported reference data and runtime/read-model boundary.
See [`docs/about-page-structure-2026-10-06.md`](docs/about-page-structure-2026-10-06.md) for the agreed
About page structure and the authoritative 2026-10-17 national-only correction: `/about`, `/ru/about`,
`/en/about` in one shared national locale group, all-Ukraine eligible offices/lawyers, own editable
history/founders, and the ordinary inherited `global_lead_form` with all runtime dependencies preserved.
The earlier regional decision is superseded: no regional About routes/pages, inheritance, locks or
filtering. The existing release audit records one national `uk` draft
(`e3338050-745a-4162-a46b-af4d15729094`), no created regional pages and `ru`/`en` placeholders only.
No schema migration, content publication or data deletion is needed; this documentation correction
does not claim a deployment. The specification retains backend/frontend responsibilities and
acceptance criteria.
Deployment and data-preservation evidence are recorded in
[`docs/about-national-only-rollout-2026-10-17.md`](docs/about-national-only-rollout-2026-10-17.md).
See [`docs/cms-front-reference-data-task.md`](docs/cms-front-reference-data-task.md) for the first CMS
frontend task around reference-data admin screens and endpoints.
See [`docs/source-diagnostics-and-bulk-bootstrap-task.md`](docs/source-diagnostics-and-bulk-bootstrap-task.md)
for the project-wide source diagnostics and mass authoring-page creation task.
See [`docs/article-import-specification-2026-10-16.md`](docs/article-import-specification-2026-10-16.md)
for the agreed import of legacy Ukrainian articles into release drafts: blog/case classification,
content conversion, taxonomy, authors and reviewers, future URLs, redirects, error handling and
acceptance. The [training report](docs/article-import-training-2026-10-15.md) records the two test
imports, known limitations and their completed cleanup; the mass import remains a separate step.

See [`docs/media-import-specification-2026-11-06.md`](docs/media-import-specification-2026-11-06.md)
for the agreed Media import: full text, per-item representation mode, embedded YouTube players,
lawyers displayed as participants through existing author relations, verified source dates,
ordinary non-featured drafts, and the required video/frontend preparation.

## Development Sequencing

Implementation should proceed from small, low-risk, release-grade slices toward the complex CMS loop.
Each module or module slice should have an explicit transfer plan before code is ported from
`notstrapitest`.

See [`docs/development-sequencing-and-module-plan.md`](docs/development-sequencing-and-module-plan.md).

## Release Contour

The first production-oriented CMS runtime should be release-ready but closed to indexing until a separate
explicit decision enables indexing. The approved target as of 2026-09-13 is a single first public launch
of the new site on `https://actum.ua`, with `actum.com.ua` retained for permanent redirects. This supersedes
the June first-go-live domain decision; it does not change the currently running site or authorize DNS,
runtime, indexing, or deployment changes. The redirect mechanism, populated migration map, and actual
public cutover are separate deliverables governed by the redirect specification linked above.

See [`docs/release-contour-requirements.md`](docs/release-contour-requirements.md).
See [`docs/release-infrastructure-architecture-2026-06-28.md`](docs/release-infrastructure-architecture-2026-06-28.md)
for the first release infrastructure plan, including Cloud Run, database, access, domain, indexing, and
rollback decisions that must be resolved before creating release resources.
See [`docs/release-infrastructure-execution-plan-2026-06-28.md`](docs/release-infrastructure-execution-plan-2026-06-28.md)
for the ordered implementation checklist, gates, stop conditions, and verification plan for creating the
closed `release` contour.
See [`docs/release-gcp-inventory-2026-06-28.md`](docs/release-gcp-inventory-2026-06-28.md) and
[`docs/release-infrastructure-command-runbook-2026-06-28.md`](docs/release-infrastructure-command-runbook-2026-06-28.md)
for the first preflight/inventory results and command-level implementation runbook.

## Starting Context

The current source of implementation knowledge is the sibling project:

- local path: `G:\работа\Actum\develop\notstrapitest`
- purpose: experimental CMS implementation without Strapi
- current summary: [`docs/notstrapitest-current-state.md`](docs/notstrapitest-current-state.md)

The most important result from `notstrapitest`: the model is viable. A live develop contour already proved
the loop:

`catalog -> authoring -> preview -> publish -> current snapshot -> public page`

The clean `CMS` implementation should preserve the proven product and architecture decisions, while
reworking project boundaries and code where the prototype accumulated experimental compromises.

## Governing Project

Cloud, deployment, IAM, secret management, rollback, and runtime decisions are governed by the sibling
repository:

- local path: `G:\работа\Actum\develop\gcp-infra-playbook`

`gcp-infra-playbook` has priority over this repository for shared GCP rules. If CMS documentation or code
ever conflicts with the playbook, the playbook wins until the discrepancy is explicitly discussed and
documented.

Before changing anything that touches GCP, Cloud Run, Cloud SQL, Cloud Build, Cloud Storage, Secret
Manager, IAM, deployment pipelines, or runtime environment variables, first read the relevant
`gcp-infra-playbook` context and run the required preflight if actual cloud state will be read or changed.

## Current Status

The stale-page refresh requirements were agreed on 2026-10-12. The canonical contract linked above
records scope, backend/frontend/integration responsibilities and acceptance tests. Existing source
components are only a partial foundation; no queue activation or application change accompanies this
documentation update. No separate starter-queue audit/approval is required by the target product flow.

The section authoring and publication requirements were revised on 2026-10-04. The target separates
the unsaved client working copy, saved immutable content, publication audit, and public page snapshots.
Implementation remains pending; the canonical contract above records its scope, confirmed no-change Save policy,
responsibilities, and reliability checks. Existing runtime descriptions below are not evidence that
this new workflow has shipped.

Created as the clean implementation project shell.

The `CMS-develop` repository remains the umbrella/context repository. Minimal deployable service skeletons
now live in the three canonical service repositories and the first `develop` Cloud Run contour has been
created.

This repository contains project documentation:

- this project goal and boundary document;
- the service split decision;
- the agreed develop cloud architecture;
- the actual develop runtime state;
- backend implementation requirements based on the reviewed `notstrapitest` refactoring assessments;
- the detailed global price section workbench contract;
- development sequencing and module transfer rules;
- a transferred current-state summary from `notstrapitest`;
- local Codex rules for working in this repository.

See [`docs/develop-runtime-state.md`](docs/develop-runtime-state.md) for the created Cloud Run services,
service accounts, Cloud SQL database/auth boundary, Secret Manager names, media bucket, Cloud Build
triggers, and verification results.
