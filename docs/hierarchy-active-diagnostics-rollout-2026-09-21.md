# Hierarchy active diagnostics: backend rollout — 2026-09-21

Backend commit `eac0ebbabbabee1b536bcdb57cbf8623ca52c852` was pushed to
`re-actum/cms-back` branches `develop`, `release`, and `codex/hierarchy-active-diagnostics`.
Both existing Cloud Build deployments succeeded in `composite-ally-360719/europe-central2`.

| Environment | Build | Active revision (100%) | Previous revision |
| --- | --- | --- | --- |
| develop | `c52e3d03-b4dd-439a-be0a-74f510d5dfce` | `cms-back-develop-00296-q5c` | `cms-back-develop-00295-wml` |
| release | `7d60119e-3258-4b56-945d-4950dda3e922` | `cms-back-release-00085-4sl` | `cms-back-release-00084-9jm` |

## Behavior

Disabled practices, services and problems no longer contribute their own findings
to active hierarchy/ancestor/ERP-group navigation counters. Existing raw diagnostics
remain available with `diagnosticsActive=false`. Enabling a record makes its current
findings active again. Enabled descendants and separate disabled-parent/enabled-child
warnings remain visible. No locale-scope changes were made.

## Checks

- Full suite: 1,034/1,034 tests, 119 suites; passed again after push.
- Typecheck/build passed, independent review clean.
- Health/readiness on both new revisions confirmed exact commit/build and database `ok`.
- Release admin smoke confirmed problem external ID `398`: hidden, diagnostics inactive,
  seven informational warnings retained, navigation own counters `0/0`.
- All two hidden hierarchy nodes in that release response had zero own counters.
- Develop admin endpoint returned 403 under the actual operator identity; its live
  functional admin check is not claimed. IAM/CMS roles were not changed.
- New revisions had no ERROR entries in the bounded post-deployment log check.

No frontend deployment, schema migration, content rebuild or data edits were performed.
Existing pipeline migration-job updates were not migration executions.

## Remaining CMS-front work

Yuriy must honor `diagnosticsActive` in row/header/field/detail diagnostic presentation.
Raw arrays must not be counted as active attention when the flag is false. Retain a
neutral hidden state and optional explicit pre-enable inspection; do not hide independent
active-child/page issues. Ready-made backend navigation indicators are authoritative.

Rollback: reviewed backend revert through existing pipelines, or an explicitly approved
emergency traffic return to the previous revisions above; no data rollback is needed.

Detailed backend contract: `cms-back/docs/service-hierarchy-active-diagnostics.md`.
Cloud record: `gcp-infra-playbook/docs/projects/cms-hierarchy-active-diagnostics-rollout-2026-09-21.md`.
