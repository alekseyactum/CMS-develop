# notstrapitest Current State Transfer

This document captures the useful project result that should be carried into the clean `CMS`
implementation.

Source project:

- local path: `G:\работа\Actum\develop\notstrapitest`
- role: prototype and validation polygon for a CMS without Strapi
- current-state source document: `notstrapitest/docs/09-current-state.md`
- release discipline source document: `notstrapitest/docs/11-release-candidate-checklist.md`

## Why notstrapitest existed

`notstrapitest` was created to test whether Actum should build a custom CMS model instead of adapting
Strapi's content model to a complex legal-site publishing workflow.

The tested domain includes:

- legal-service landing pages;
- regional page variants;
- practices, services, problems, lawyers, cases, and articles;
- page sections and generated sections;
- read-only directory data that may later come from ERP;
- preview, publish, current public rendering, rollback, and diagnostics.

## Proven Result

The prototype proved that the custom CMS direction is workable.

The live develop implementation already covered the practical publishing loop:

`catalog -> authoring -> preview -> publish -> current snapshot -> public page`

That loop was validated for representative routes including:

- `/kyiv/services/family-law`
- `/services/family-law/divorce-support`
- `/services/family-law/divorce-support/property-division`

## Implemented Prototype Capabilities

The `notstrapitest` develop contour already includes:

- NestJS + TypeORM backend;
- explicit SQL migrations and demo/reference seeds;
- DB-backed admin authentication through users, roles, permissions, and bearer tokens;
- React Admin shell on `/admin/`;
- fallback admin workbench on `/admin/workbench.html`;
- dashboard overview;
- catalog screens for internal entity directories;
- custom page authoring flows;
- preview, publish, current snapshot inspection, snapshot history, and rollback;
- public HTML rendering from current snapshots;
- read-only `GET /api/pages/by-route`;
- route-chain diagnostics;
- route alias registry with unresolved-route repair actions;
- release readiness cockpit;
- stale rebuild queue visibility;
- develop Cloud Run runtime and Cloud Build trigger for the prototype's `develop` branch.

## Page Types Already In The Live Loop

The prototype supports these page types in authoring, preview, publish, and runtime composition:

- `services_root`
- `practice_page`
- `service_page`
- `problem_page`
- `lawyers_root`
- `lawyer_page`
- `articles_root`
- `article_page`
- `cases_root`
- `case_page`

The services tree supports regional inheritance. Lawyer, article, and case pages are currently modeled as
locale-only flat routes.

## Key Architecture Lessons

The clean CMS should carry forward these decisions:

- Public slugs for page routes belong to the page authoring layer, not to catalog identity.
- Catalog entities should stay stable and internal where possible.
- Preview must run before publish and expose quality-policy failures.
- Publish should create durable snapshots.
- Public runtime should read current published state, not draft authoring state.
- Rollback should create a new current snapshot from a historical payload.
- Published route registry is necessary for stable child links, breadcrumbs, aliases, and diagnostics.
- Generated lists should be hydrated from current published child pages where possible.
- Regional pages should inherit from published base state, not from drafts.
- Stale descendants should be tracked and rebuilt through a queue, not manually republished everywhere.
- Operator UI needs readiness, alias, route, and snapshot diagnostics, not just content forms.

## Important Boundary

`notstrapitest` is still a test polygon. Its runtime is intentionally closed to indexing:

- `SITE_INDEXING_ENABLED=false`;
- site-wide `X-Robots-Tag: noindex, nofollow`;
- `robots.txt` blocks indexing;
- `sitemap.xml` remains empty.

The clean `CMS` repository should not inherit a production/indexing decision automatically. That decision
belongs to a separate release/runtime design step governed by `gcp-infra-playbook`.

## Out Of Scope In The Prototype

The prototype intentionally left these items unfinished or outside its current scope:

- full revisioned published graph;
- generic page-owned root routing beyond fixed roots;
- separate Cloud Run worker;
- deeper content entities in live authoring UI;
- real ERP import;
- production-like release contour.

## What CMS Should Do Next

Recommended first implementation direction:

- define the clean repository structure;
- move the proven domain model into explicit product and architecture docs;
- decide which prototype code is worth porting and which parts should be rewritten;
- design the snapshot-first published state, dependency tracking, stale diagnostics, and cache/rebuild
  model for the first release;
- reconsider a fuller published graph only later if snapshot-first plus dependency tracking proves
  insufficient for real release requirements;
- define the CMS runtime environments only after consulting `gcp-infra-playbook`;
- keep `notstrapitest` available as a reference until CMS reaches feature parity for the validated loop.
