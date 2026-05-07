# Service Split Decision

This document records the first real implementation boundary for the clean `CMS` project.

## Decision

`CMS` will be implemented as three application services:

- `site-front`: Next.js public site frontend;
- `cms-front`: Next.js admin/editorial frontend;
- `cms-back`: NestJS backend.

The split is not cosmetic. It defines which service owns public rendering, which service owns the admin
surface, which service owns content state, and how preview and publishing should work.

## Why This Split Fits The Product

The CMS is not a generic admin CRUD application. It controls legal-site content where the public surface
needs stable routes, SEO metadata, localized URLs, preview, publish, rollback, and diagnostic visibility.

Next.js fits the public and visual side of that product:

- public page rendering;
- route-level rendering behavior;
- metadata, canonical URLs, hreflang, sitemap, and robots integration;
- visual preview using the same rendering components as the public site;
- admin shell and custom editorial screens in a separate CMS frontend.

NestJS fits the source-of-truth and publishing side:

- authoring data;
- catalog and directory data;
- authentication, roles, and permissions;
- preview assembly and quality checks;
- publish pipeline;
- current published snapshots;
- route registry and aliases;
- rollback;
- stale/rebuild tracking;
- ERP integration boundaries;
- operator diagnostics and readiness checks.

## Backend Responsibility Change

The backend should not be designed as the final public HTML renderer.

The backend is the publishing engine and public data contract owner. Its main artifact for public runtime
is a versioned snapshot contract that the frontend renders.

Backend-owned responsibilities:

- authoring model and draft state;
- validation and quality-policy checks;
- preview payload generation from draft state;
- publish and rollback decisions;
- durable snapshot creation;
- current published state;
- public route lookup;
- public snapshot API;
- route and alias diagnostics;
- integration with ERP-owned read-only data;
- cache invalidation or revalidation signals for the frontend.

Backend should expose public data through stable APIs that read published state, not draft authoring
tables.

Example public surfaces to design:

- `GET /api/public/pages/by-route`;
- `GET /api/public/routes`;
- `GET /api/public/sitemap`;
- `GET /api/public/robots-policy`;
- a publish/rollback-triggered revalidation signal or webhook for the frontend.

## Frontend Responsibility

The frontends should render public, admin, and editorial preview surfaces from backend contracts.

`site-front` responsibilities:

- public route handling;
- page rendering from published snapshot payloads;
- metadata rendering from published snapshot payloads;
- frontend cache behavior and route revalidation.

`cms-front` responsibilities:

- admin shell;
- custom editor screens;
- preview rendering from backend preview payloads;
- admin workflow UX for authoring, publish, rollback, diagnostics, and readiness.

The frontends must not become a second source of CMS truth. They should not read authoring tables directly,
reconstruct publish rules, or decide what is publishable.

## Snapshot Contract

The snapshot payload becomes the primary contract between backend and frontend.

It should be explicit and versioned. At minimum, the design should account for:

- `schemaVersion`;
- `pageType`;
- `locale`;
- `route`;
- `canonicalRoute`;
- `seo`;
- `breadcrumbs`;
- `sections`;
- `structuredData`;
- `children` or generated list references;
- `publishedAt`;
- source snapshot/version identifiers.

Changes to this contract are architecture changes and should be documented with code changes.

## Preview And Publish Flow

Preview and publish should remain backend-governed.

Recommended direction:

1. Editor changes authoring data through admin UI.
2. Frontend calls backend preview endpoint.
3. Backend assembles preview payload and quality-policy results from draft state.
4. Frontend renders the preview payload using public rendering components.
5. Backend performs publish when requested and permitted.
6. Backend writes a durable snapshot and marks it current.
7. Backend emits or exposes a revalidation signal for affected frontend routes.
8. Frontend re-renders public routes from current published snapshots.

This preserves the proven `notstrapitest` loop while moving final HTML rendering to Next.js:

`catalog -> authoring -> preview -> publish -> current snapshot -> Next.js public page`

## Operational Consequences

The split introduces more runtime discipline:

- three Docker images;
- three Cloud Run services when deployed;
- separate env and secret injection surfaces;
- authenticated service-to-service API access rules;
- separate health checks;
- separate rollback paths;
- documented deployment ordering when backend contracts change.

Any GCP, Cloud Run, Cloud Build, Secret Manager, IAM, or runtime decision for these services remains
governed by `gcp-infra-playbook`.

## Initial MVP Boundary

The split should not expand the first implementation scope by itself.

The recommended MVP remains narrow:

- `services_root`;
- `practice_page`;
- `uk` and `ru`;
- base and regional page variants;
- preview;
- publish;
- current published snapshot;
- public route lookup;
- public page rendering in Next.js;
- basic route diagnostics.

Other page types and deeper workflows should be added after the first clean loop is working end to end.
