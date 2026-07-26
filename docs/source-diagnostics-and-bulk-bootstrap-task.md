# Source Diagnostics And Bulk Bootstrap Task

## Status

Project-level product and implementation task for the clean `CMS` contour.

This document defines how the CMS should expose missing authoring-page diagnostics and mass page creation
for source-backed entities. It is primarily a frontend-facing task, but it is intentionally written as a
cross-project contract because the UX depends on backend `page-workbench` capabilities and on the agreed
source/runtime boundary.

## Goal

Give editors and operators a safe, explicit way to:

- detect source records that do not yet have CMS authoring pages;
- understand whether missing pages can be created or are blocked;
- preview a mass-creation plan before running it;
- create missing pages in bulk;
- review a clear execution report after the operation finishes.

## Problem

The system already contains ERP-owned or source-owned records such as regions, practices, services,
problems, and potentially lawyers. Over time, new source records can appear without corresponding CMS
authoring pages.

Without an explicit diagnostics and bootstrap layer, operators must guess:

- whether a missing public/editorial page is expected;
- whether the page already exists in authoring;
- whether the page can be created safely;
- which missing pages belong to one region, one subtree, or the whole service tree.

This creates hidden backlog, manual checks, and inconsistent operational behavior.

## Important Distinction

`bulk-bootstrap` is not `bulk-publish`.

- `bulk-bootstrap` creates missing authoring pages for source-backed entities.
- `bulk-publish` publishes already existing authoring pages.

The diagnostics described here are about source-to-authoring readiness first. Publish readiness remains a
separate concern and must not be mixed into the first version of this UI.

## Product Direction

The feature should be implemented as a reusable **source diagnostics** contour, not as isolated logic
inside one reference-data screen.

Reference-data screens are the natural operator entry points, but the core concept is broader:

- a source record may have CMS authoring state;
- that state may already exist, be missing, or be blocked from creation;
- the CMS should expose this as diagnostics and provide controlled bulk bootstrap actions.

This should become a shared UX pattern for source-backed entities instead of a one-off feature for
`regions`.

## Scope

### First Wave

The first release should support the source-backed generated page domain:

- `regions`
- `practices`
- `services`
- `problems`

The UI should use backend `page-workbench` bulk bootstrap planning and execution to show diagnostics and
run mass creation.

### Optional Next Wave

After the first wave is stable, the same contour may be extended to:

- `lawyers`

This extension should happen only if the backend contract for `lawyer_page` remains source-backed and
operationally consistent with the same diagnostics model.

### Out Of Scope For This Task

Do not mix these domains into the first implementation:

- editorial publications such as `blog`, `media`, and `case`;
- article/case/media editorial entity creation flows;
- global sections;
- single pages;
- bulk publish UX.

Editorial entities may need a separate diagnostics/creation model later, but they should not be forced
into the source-bootstrap UX just because they are editable in CMS.

## Backend Contract Assumptions

The frontend must treat the backend as the source of truth for planning and execution.

The frontend must not try to compute missing pages locally from reference lists.

The expected backend capabilities are:

- `POST /api/admin/page-workbench/bulk-bootstrap/plan`
- `POST /api/admin/page-workbench/bulk-bootstrap`

Planning is a dry run. Execution creates missing authoring pages and repairs existing pages whose
authoring state is missing schema-required section bindings.

The backend plan/result model should be consumed as-is, including statuses such as:

- `will_create`
- `will_repair`
- `already_exists`
- `blocked`

The frontend should also surface backend-provided reasons and diagnostics instead of inventing its own
heuristics.

An existing page row is not necessarily initialized. The page state exposes `initialization` with
`status`, expected/bound section-slot counts, and `missingSectionSlots`. When
`initialization.status = "repair_required"`, the workbench exposes the critical
`PAGE_AUTHORING_REPAIR_REQUIRED` diagnostic and blocks preview/publish readiness until bootstrap restores
the missing bindings. A successful repair returns `bootstrap.created = false`,
`bootstrap.repaired = true`; bulk planning/execution use `will_repair`/`repaired`.

## Scope Model

The frontend should be able to request planning and execution for several scopes, depending on the entry
point:

- whole service tree;
- one practice subtree;
- one service subtree;
- one page type;
- one or more regions;
- one generated source, optionally with descendants.

The exact scope used should depend on the screen and the user action.

Examples:

- `Regions` screen:
  use region-scoped planning/execution.
- `Practices` screen:
  use one practice subtree or one generated source.
- `Services` screen:
  use one service subtree or one generated source.
- diagnostics dashboard for the whole contour:
  use service-tree scope.

## UX Requirements

### 1. Diagnostics Summary

Relevant source-backed list screens should show a CMS diagnostics summary area near the top.

The summary should present:

- total missing pages that can be created;
- existing pages that require authoring repair;
- pages that already exist;
- blocked items;
- a clear call to action for planning and creation.

This summary should describe CMS authoring readiness, not publish status.

### 2. Row-Level Status

Each relevant list row should expose a compact CMS state indicator, for example:

- page exists;
- page exists but authoring repair is required;
- missing and creatable;
- blocked.

If the backend provides a reason, the UI should expose it through inline text, tooltip, drawer, or other
clear operator-facing affordance.

### 3. Plan Before Execution

The primary mass action should first open a planning step.

The user should be able to:

- request a plan for the current scope;
- review the returned list and summary;
- understand what will be created, repaired, and what is blocked;
- explicitly confirm execution.

The plan step is required. The first release should not run mass creation blindly from one click.

### 4. Execution Report

After running bulk bootstrap, the UI should show a report with at least:

- created;
- repaired;
- already existed;
- blocked;
- failed.

The report should stay available long enough for the operator to understand the result and should support
screen refresh without losing the meaning of the operation.

### 5. Refresh Behavior

Do not run a heavy full diagnostics recalculation on every screen render or every keystroke.

Recommended behavior:

- load the reference/source list first;
- then load diagnostics summary asynchronously;
- refresh diagnostics after mass creation;
- allow explicit manual refresh when useful.

If a screen needs fast first paint, diagnostics may be lazy-loaded after the main data table is visible.

## Frontend Structure Direction

The implementation should prefer reusable components and shared state handling over per-screen duplication.

The expected reusable UI pieces are:

- source diagnostics summary block;
- plan dialog or side panel;
- execution report dialog or panel;
- row-level status badge/pill for source-backed records.

The reference-data screens should provide the scope context, but the diagnostics widgets should not be
hardcoded only for one resource.

## Screen Placement

For the first release, the primary entry points should be the existing source/reference screens for:

- regions;
- practices;
- services;
- problems.

This is the right operational placement because users already think about these objects there.

However, the implementation should stay generic enough to support:

- a future shared diagnostics dashboard;
- future reuse inside workbench entry screens;
- future support for other source-backed domains.

## Operational Rules

- The frontend must not infer missing-page counts from public routes or from ad hoc record comparisons.
- The frontend must not mix bootstrap readiness with publish readiness in one status label.
- The frontend must not assume all source-backed domains use the same scope automatically; the correct
  scope should be chosen intentionally per screen/action.
- The frontend must preserve backend blocking reasons and present them clearly to operators.

## Acceptance Criteria

The first project slice is complete when all of the following are true:

1. On the relevant source-backed screens, the user can see CMS diagnostics summary for the current scope.
2. The user can request a dry-run plan before mass creation.
3. The user can run mass creation of missing pages from the current scope.
4. The UI shows a meaningful execution report after the action.
5. The frontend uses backend plan/execution contracts as the source of truth and does not locally invent
   missing-page calculations.
6. The first implementation supports `regions`, `practices`, `services`, and `problems`.
7. Editorial content creation flows are not mixed into this first contour.

## Delivery Notes

This task should be implemented as a project contour, not as a one-off patch to one screen.

The first concrete UI may appear on reference-data pages, but the code and naming should reflect the
broader purpose:

- source diagnostics;
- bootstrap planning;
- bulk authoring-page creation.
