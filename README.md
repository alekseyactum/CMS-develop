# CMS

Clean implementation repository for the Actum content platform.

This repository starts from the validated lessons of `notstrapitest`, but it is not a blind copy of that
prototype. `notstrapitest` was used as a working polygon for checking the CMS model without Strapi. `CMS`
is the place where the finished implementation should be built deliberately, with production-oriented
project structure, documentation, and runtime discipline.

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

The clean implementation is expected to be split into two application services:

- a Next.js frontend for public rendering, preview rendering, and the admin/editorial shell;
- a NestJS backend for authoring state, permissions, preview assembly, publish, snapshots, routes,
  rollback, diagnostics, and integrations.

The backend owns the CMS truth and the versioned published snapshot contract. The frontend renders public
and preview pages from backend contracts and must not become a second source of publish logic.

See [`docs/service-split-decision.md`](docs/service-split-decision.md).

## Backend Implementation Direction

The backend should not inherit the large prototype services as its target structure. The clean
implementation should port proven behavior from `notstrapitest` through typed page contexts, versioned
preview/snapshot contracts, focused domain services, and tests around the preserved edge cases.

See [`docs/backend-implementation-requirements.md`](docs/backend-implementation-requirements.md).

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

Created as the clean implementation project shell.

At this point the repository contains documentation only:

- this project goal and boundary document;
- the initial frontend/backend service split decision;
- backend implementation requirements based on the reviewed `notstrapitest` refactoring assessments;
- a transferred current-state summary from `notstrapitest`;
- local Codex rules for working in this repository.

No runtime resources, secrets, deployment triggers, or production-like release environment are created by
this initial setup.
