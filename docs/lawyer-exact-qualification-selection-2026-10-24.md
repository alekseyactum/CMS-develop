# Exact Lawyer Qualification Selection - Agreed 2026-10-24

## Product Decision

The lawyer selection on a thematic page uses only the qualification of that exact topic and level.
This replaces practice-subtree aggregation and service-wide selection on problem pages.
It also supersedes the practice threshold `score > 2` approved on 2026-10-22.

| Page type | Eligible qualification | Threshold |
| --- | --- | --- |
| `practice_page` | Exact practice, with no service/problem ID or external ID | `score > 1` |
| `service_page` | Exact practice + service, with no problem ID or external ID | `score > 1` |
| `problem_page` | Exact practice + service + problem | `score > 1` |

- A missing qualification, null score or score <= 1 excludes the lawyer from that selection.
- Parent, child and sibling scores neither qualify a lawyer nor increase the selected score.
- An empty selection remains empty. Do not substitute a parent/child/sibling selection or lower score.
- Active/resolved qualifications and the existing lawyer visibility, slug and regional rules remain required.
- Duplicate eligible qualifications for one exact target use `MAX(score)` and produce one lawyer card.
- Order remains selected score descending, then the existing stable lawyer ordering. Keep the 80-card cap.

## Affected Surfaces

The rule applies to all three page types, in UK/RU/EN, national and regional variants:

- `*_lawyers`;
- `*_team_cta_top_lawyers`;
- `*_team_cta_lawyers`.

CMS section preview, full-page preview, publication assembly and published-selection refresh must use
the same selector. Public card shape, links and the no-link CTA behavior do not change. Historical
problem CTA `source` metadata remains service-shaped for compatibility; the exact problem for selection
is resolved from the page route, not inferred from that metadata.

## Deliberately Unchanged

- Lawyer profile `practices`: direct practice score >= 3, alphabetical display order, no child fallback.
- Lawyers directory practice membership: any qualification in that practice with score > 1, including children.
- Home team CTA: maximum across all qualification levels with score > 2 and the existing secondary ranking.
- Ordinary Home/About lawyer selection and About portraits: no new qualification gate.
- `Person.knowsAbout`: existing most-specific-target policy with score > 1.
- Regional availability, reviews, cases, publications, ERP import and qualification editing contracts.

A lawyer with direct practice score 2 can therefore appear on that practice page without that practice
appearing in the profile's `practices` list. Directory membership may also differ from the thematic page.
These are intentionally different consumers; do not silently unify them in this change.

## Acceptance Cases

1. Practice score 2 qualifies for that practice page; score 1, null or a missing direct score does not,
   even when a child service/problem is rated 5.
2. Service score 2 qualifies for that service page; a problem rated 5 cannot substitute a missing or
   low service score. A practice rated 5 cannot substitute it either.
3. Problem A score 2 qualifies only for A. A service rated 5 or sibling problem B rated 5 cannot
   substitute a missing or low score for A.
4. Scores from other practices/services/problems never enter the maximum or change the ranking.
5. Duplicate exact qualifications produce one card with the maximum eligible direct score.
6. Unresolved/inactive qualifications remain excluded. Unresolved child external IDs must not be
   mistaken for a direct parent qualification just because an internal child ID is null.
7. Lists and both CTA slots agree across locales, regions, preview and published-selection refresh.
8. Empty exact selections do not trigger broader fallback queries. Unchanged consumers retain their rules.

## Publication And Rollout

No schema/data migration or frontend contract change is required. This agreement does not authorize
an automatic rewrite or bulk republication of existing public snapshots.

After deployment, new assembly uses the new rules. Existing public selections adopt them through an
explicit page republication or an applicable published-selection refresh. Deploying code alone does not
mark snapshots stale. Before a broad rollout, a read-only old/new selection comparison is recommended
to identify pages that lose all lawyers and missing exact-level ERP assessments; this document is not
evidence that such a live-data comparison or deployment has been performed.
