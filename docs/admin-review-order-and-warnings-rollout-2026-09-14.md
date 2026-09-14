# Admin review ordering and text warnings rollout — 2026-09-14

Owner explicitly approved develop/release automatic deployment. Playbook preflight passed before cloud
reads. `re-actum/cms-back` feature/develop/release all point to
`b61a6776f55358e95abe4033e2ae5c344a7eee03`, fast-forward from
`780110a0028ec052517bd5c7979e3f5f2c76cd3c`.

Admin reviews now sort by publication date descending, undated last, then author and ID. All-empty
uk/ru/en text produces no translation warnings; partial translations retain missing-language warnings.
Public runtime/order, import, data/schema, IAM and pipelines were not changed. No migrations executed or
pages republished. Existing pipelines update migration job images without running them.

## Deployment

Project `composite-ally-360719`, region `europe-central2`.

| Environment | Successful build | Previous revision | New ready revision, 100% traffic |
|---|---|---|---|
| develop | `72ef5660-2e25-456c-ba43-ae94ad7fd668` | `cms-back-develop-00283-rch` | `cms-back-develop-00284-cvp` |
| release | `beeba229-d322-4ade-a5d8-532508f6635b` | `cms-back-release-00072-fn8` | `cms-back-release-00073-k69` |

Both health/ready checks passed with expected SHA and database ok. All 840 tests and application build
passed after each push. Remote refs match and backend worktree is clean. No ERROR-or-higher entries
were returned for these revisions during the bounded post-deploy check.

## Read-only release API verification

- Before deployment, review external ID 1320 had three missing-text warnings with three empty texts.
- After deployment, traversed all 512 reviews in six pages (limit 100). All IDs unique; publication dates
  monotonically descending across page boundaries. Repeated first page preserved its ID sequence.
- 35 all-empty reviews: no translation warnings. 469 partially translated reviews: warning count matched
  missing languages and all such diagnostics retained warning severity. Remaining 8 were fully translated.
- Review 1320 now has zero text warnings; no review text or fields were manually changed.
- No undated reviews occurred in the live sample. Null-last/tie-break ordering is verified by the SQL
  generation contract tests, not claimed as exercised with live undated records or every collation tie.
- The initial verification script failed parsing PowerShell's automatically decoded DateTime as a string;
  corrected operator-side date handling and reran successfully. This was not an application failure.
- Browser UI and develop admin functional acceptance were not performed; live functional evidence is release API.

## Manual acceptance / risk / rollback

Refresh the admin reviews list/card. Review 1320 should show no missing-text warnings; partial translations
should retain them. Check new-to-old dates and stable page transitions. No page republishing is needed.
Offsets remain live pagination and can shift during concurrent data changes; first-page stability above is
only the observed smoke interval. No performance improvement or index claim is made.
Normal rollback is a reviewed revert of b61a677 via existing pipelines, no DB rollback. Previous revisions
above are emergency traffic rollback points only with explicit owner approval.
Implementation contract: `cms-back/docs/admin-review-order-and-text-diagnostics-2026-09-14.md`.
