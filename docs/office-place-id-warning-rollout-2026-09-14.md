# Office Place ID warning rollout — 2026-09-14

Owner approved promotion to develop and release with automatic deployments. Playbook preflight passed
for the expected account and project before cloud reads. Canonical repository: `re-actum/cms-back`.

Both branches fast-forwarded from `b684c2594b32c6fda2bb37408c0ed67b38fe8478` to
`0ab9920076ac229e554a557e9d6c2a9c47579213`. Feature branch `codex/office-place-id-warning` has the same SHA.
No force push, migration execution, page republishing, content writes, IAM or pipeline changes.
The existing pipelines update migration job images but do not execute migrations.

Missing office `googlePlaceId` now has severity `warning` with a recommendation to fill it in.
Diagnostic code/field are unchanged. Coordinate, address, map URL and region checks remain unchanged.
Implementation contract: `cms-back/docs/office-google-place-id-warning-2026-09-14.md`.

## Deployment evidence

Project `composite-ally-360719`, region `europe-central2`.

| Environment | Build, SUCCESS | Previous revision | New ready revision, 100% traffic |
|---|---|---|---|
| develop | `62b921d2-e0e9-419e-bed6-af804f9ca086` | `cms-back-develop-00281-bl7` | `cms-back-develop-00282-xck` |
| release | `b222bf5e-8916-48c8-ad9e-c507fe2b95b2` | `cms-back-release-00070-smj` | `cms-back-release-00071-s6q` |

- Both authenticated health/readiness checks succeeded with the expected SHA and database status ok.
- Post-push full tests and application build passed after each promotion: 829 tests, zero failures/skips.
- Backend worktree clean; remote feature/develop/release refs verified equal.
- Read-only release office list before deployment showed `OFFICE_GOOGLE_PLACE_ID_REQUIRED` as `error`
  for office `e9e118cd-038f-4e90-aac9-75be521d4ac7`; after deployment it returned the same code/field as
  `warning`. No office data was edited by this rollout.
- Visibility/diagnosticsActive of that record differed between the two reads; this is not a controlled
  before/after measurement of aggregate counts. Local tests cover the summary-count behavior.
- No ERROR-or-higher log entries were returned for the two new revisions in the bounded post-deploy check.
- Develop admin functional/UI acceptance was not repeated; the operator previously had CMS_USER_NOT_FOUND
  there. No identity impersonation or access grants were used. Live functional evidence above is release API.

## Manual verification and rollback

Reopen an office card without Place ID: render the API warning, not a red error. Page republishing is not
needed. Other errors must remain unchanged. Frontend must use diagnostic severity rather than infer
severity from the preserved `_REQUIRED` code or requiredSourceFields metadata.

Risk: a frontend hardcoding error color may still need its own correction; browser UI was not verified.
Normal rollback is a reviewed revert of `0ab9920` through the existing pipelines; no DB rollback is needed.
Previous revisions above are emergency traffic rollback points only with explicit owner authorization.
