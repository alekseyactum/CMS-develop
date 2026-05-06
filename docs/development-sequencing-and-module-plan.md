# Development Sequencing And Module Plan

This document records the working rules for expanding the `CMS` project requirements and implementing
the clean project step by step.

## Purpose

`CMS` should be built as a release-oriented implementation, not as a blind migration of the
`notstrapitest` prototype.

The project should grow through small, reviewable modules. Each module should have a short transfer plan,
tests, and an explicit decision about what is preserved, what is rewritten, and what is intentionally not
carried forward.

## Critical Review Rule

Codex must keep an engineering review posture.

If a requested direction looks fragile, premature, excessive, hard to maintain, or based on a weak
premise, Codex should state the concern first and propose a more rational alternative. Agreement is not
automatic. If a known risk is accepted, the risk should be documented in the related markdown context or
module plan.

## Code Transfer Rule

Code from `notstrapitest` should not be copied literally by default.

For each module or module slice:

- identify the proven behavior that should survive;
- identify the prototype shortcuts that should not be preserved;
- write or port tests for the behavior before rewriting risky logic;
- optimize the organization of the code where the benefit is obvious;
- avoid perfectionist refactors that do not improve readability, testability, or delivery safety;
- keep behavior and contracts more important than line-by-line similarity.

## Readability Rule

Human-readable code is a project requirement.

Prefer:

- clear use-case flow;
- explicit names;
- small focused modules;
- typed inputs and outputs;
- simple composition over hidden inheritance;
- obvious errors and validation;
- local helpers where they clarify behavior.

Avoid:

- giant services that own several unrelated responsibilities;
- universal nullable context objects;
- unnecessary abstraction layers;
- abstract base classes that hide the main flow;
- `any` as an escape hatch;
- wrappers that only pass through to another service without defining a useful boundary.

## Query Policy

Use TypeORM for simple operations:

- simple `findOne`;
- simple `find`;
- simple `save`;
- simple transactions where TypeORM entity persistence is the clearest option;
- obvious lookups with one or two direct conditions.

Use parameterized raw SQL for non-trivial queries:

- joins across several tables;
- conditional search logic;
- route diagnostics;
- published snapshot lookup;
- generated listing projections;
- readiness and operator dashboards;
- aggregate or reporting queries;
- queries where SQL is clearer for the team than TypeORM QueryBuilder.

Raw SQL should live in query/repository modules, not be scattered through use-case services. It must be
parameterized, reviewed, and covered by tests for important behavior.

## Module Transfer Brief

Before implementing a module or module slice, create a short plan that answers:

- What behavior from `notstrapitest` is being preserved?
- What is being rewritten for the clean `CMS` implementation?
- Which code organization problem is being solved?
- Which tests will prove the behavior?
- Which queries use TypeORM and which use raw SQL?
- Which parts are expected to be release-grade immediately?
- What is explicitly out of scope for this slice?

The brief can be a markdown document, a section in an existing requirements document, or a tracked task
plan, depending on the size of the slice.

## Release-Grade Definition

When a module is small enough to finish safely, it should be implemented in release-grade form from the
start.

Release-grade means:

- no real secrets in code, markdown, logs, or test fixtures;
- typed configuration and validation;
- explicit errors for invalid input;
- tests for core behavior;
- stable public or internal contracts;
- documented assumptions;
- no dependency on demo-only data for normal behavior;
- no hidden runtime side effects;
- no production-like runtime creation without a separate playbook-governed decision.

This does not mean creating release Cloud Run services, production-like IAM, Cloud Build triggers, or
shared GCP resources early. Runtime and deployment decisions remain governed by `gcp-infra-playbook`.

## Implementation Sequence

Prefer a low-risk foundation before moving into complex CMS behavior.

Recommended early sequence:

1. Backend skeleton, configuration, database module, and health endpoint.
2. SQL migration runner and migration tracking.
3. Route builder and URL rules.
4. Regional token resolver.
5. JSON merge and section extraction utilities.
6. Password hashing and authentication primitives.
7. Snapshot and preview contract types with validation.
8. Catalog read projections for the first MVP page types.
9. `services_root` authoring and preview.
10. `practice_page` authoring and preview.
11. Publish current snapshot and public snapshot lookup.
12. Next.js public render from the snapshot contract.

This sequence may change, but changes should be justified by risk, dependency order, and delivery value.

## Low-Risk First Candidates

These modules are relatively self-contained and useful as early implementation slices.

| Candidate | Recommendation | Reason |
| --- | --- | --- |
| Configuration and env validation | Start early | Small, required by everything, release-grade validation is valuable. |
| Database module | Start early | Independent foundation and easy to verify through health checks. |
| SQL migration runner | Start early | Small, operationally important, establishes SQL discipline. |
| Health endpoint | Start early | Very small and proves app wiring. |
| Route builder | Start early | Pure logic, easy tests, important URL contract. |
| Regional token resolver | Start early | Pure logic, low dependencies, used later by preview and publish. |
| JSON merge and section extraction | Start early | Pure rules, important edge cases, easy tests. |
| Password hashing | Good early slice | Small, self-contained, testable. |
| Token/session auth | Do after auth decision | Prototype approach works, but the release project should decide whether to use a standard library. |
| Runtime section cache | Later | Small, but its real contract depends on runtime rendering and publishing. |
| Stale rebuild worker | Later | The file is small, but the behavior depends on the publish/rebuild pipeline. |

## Do Not Start With

Avoid starting the clean project with these large or highly coupled prototype areas:

- full `PageAuthoringService`;
- full `PagePreviewService`;
- full `PublishingService`;
- `PublishedPayloadRuntimeService`;
- public HTML renderer from the Nest backend;
- release readiness cockpit;
- all page types at once.

These areas should be rebuilt through smaller vertical slices after the foundation is in place.

## Immediate Safe First Slice

The first implementation slice should be:

`config -> database module -> migration runner -> health endpoint`

This is small enough to make release-grade immediately and useful enough to establish project structure,
testing style, and operational discipline.

The migration runner should enforce unique, monotonically ordered migration filenames. Duplicate sequence
numbers should be treated as an error in the clean project, even if the prototype tolerated them.

After that, the next safe slice should be:

`route builder -> regional token resolver -> JSON merge and section utilities`

These modules are pure or nearly pure and will support the first CMS authoring and preview flow.

## Acceptance Gates

Each completed slice should pass these gates:

- build succeeds;
- relevant tests pass;
- module behavior is manually verifiable if it has runtime behavior;
- markdown context is updated if architecture, workflow, contracts, or runtime expectations changed;
- no unrelated prototype behavior was imported accidentally;
- any accepted risk is documented.
