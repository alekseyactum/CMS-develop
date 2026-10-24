# Exact Lawyer Qualification Selection Rollout - 2026-10-24

Status: develop and release deployed and verified.

The owner explicitly approved promotion, push and deployment to both develop and release.
Mandatory Actum GCP preflight passed for `composite-ally-360719`, region `europe-central2`.

## Scope And Source

- Backend candidate: `7e08b5484131c24740af771ba0b3127e60d601e0`, branch
  `codex/exact-lawyer-qualification-selection`, repository `re-actum/cms-back`.
- Product specification: `CMS-develop` commit `360a8907995367becc122f3da241cad38aed64d6`;
  [agreed exact-level selection](lawyer-exact-qualification-selection-2026-10-24.md).
- Both environment branches initially pointed at `37fea0d42e4981b2982a24b13521315c6ebd93b4`.
- The candidate is a fast-forward of both branches. Only the selector, tests and backend documentation
  differ. Build configs and migrations are identical to the baseline.
- Practice/service/problem lists and both team CTA slots use only the exact page-level qualification
  with `score > 1`. Parent, child and sibling scores do not qualify or boost a lawyer. No fallback.
- Profile practices, directory, Home/About, JSON-LD and ERP contracts are unchanged.

Deployment uses the existing enabled branch triggers and configs:

| Environment | Trigger | Branch | Config |
| --- | --- | --- | --- |
| develop | `757154f2-e42e-48cc-8bab-2de92021dfbe` | `^develop$` | `cloudbuild.yaml` |
| release | `237cd212-f0f3-44af-a681-0099b8a1c13d` | `^release$` | `cloudbuild.release.yaml` |

No manual service/env/IAM/secret/scheduler/pipeline change, migration execution, frontend deploy,
ERP data write, forced refresh or real-page publication is included. Existing pipelines update saved
migration/effects job images as usual; they do not execute those jobs.

## Baseline And Rollback Points

Read-only checks at approximately `2026-10-24T12:13Z`: health/readiness 200, database `ok`, exact
baseline source/build, latest-created equals latest-ready, 100% traffic, service and job images match.

| Environment | Baseline ready revision | Baseline build |
| --- | --- | --- |
| develop | `cms-back-develop-00360-xsc` | `cae938cd-ec4d-4daf-9d84-1ffb4354460b` |
| release | `cms-back-release-00146-4bj` | `0e0cbe7f-4ee8-4cb7-9888-054bbc9d9d31` |

Normalized configuration hashes exclude image, build identity and volatile client nonce:

| Environment | Service | Annotations | Migration job | Effects job |
| --- | --- | --- | --- | --- |
| develop | `d32ebaa8dd4523f89b64b653b5dc6ae0afafccf26b4dcf92dfb3c61abd3e476b` | `9d22d4dfb61bd64e7848e99dfa5cfc94a36a37b14903936d7f5793bf7293fff0` | `17e79ab644b2e2580972e444e39def97e1bbb88ac44ca1b252c63e373328d2dc` | `8cd382268339eb2eef8279892893e42ab89b3faae706d3947a06ec80ce19785c` |
| release | `17d9e3901b1ec71534568d68ab791eab660ef9ef65611fd458d905d64f359594` | `3fb8874f32564c65f73d56f6da5e285cdbd38bf1ccc489904048107b9f7ce502` | `d3fc7e2881c0d1ca374382f9bd71c492699f28300ff5ee59ded1887900131d25` | `b79664791336446a7af7b9ef7ed2b05205347dd1dfabc8176c1859322534a73e` |

Public control sample `/lawyers/bondar-artem-vasylovych`: develop returns 404; release snapshot 22,
ID `55423069-5f6f-4cb2-a149-3eea3be62473`, normalized payload hash
`a399802bfce476fdade492aadaf0c94ec3dcd602a4b403b212f6bc745217fecd`.

## Verification

Before promotion: production build passed; full suite 4,283 tests, 4,281 passed, two skipped, no failures
with localhost available. The first sandboxed full run could not connect to local HTTP test servers;
the unrestricted-localhost repeat passed. After each environment push, all 247 focused regression
tests passed again.

Develop push triggered build `d8ea102c-77bf-49b5-afc5-e900b7303ae8` at
`2026-10-24T12:13:58.997620Z` for the exact candidate. It succeeded at
`2026-10-24T12:17:07.311877Z`. Read-only smoke at `2026-10-24T12:21:05.9685086Z` confirmed:

- Ready revision `cms-back-develop-00361-r7z`, latest-created equals latest-ready, 100% traffic.
- Exact commit/build identity, health/readiness 200 and database `ok`.
- All four normalized configuration hashes equal the baseline; both saved job images match the service.
- Latest migration/effects execution identities are unchanged; public control sample remains 404.
- No ERROR-or-higher entries for the new revision in the bounded post-deploy log check.

Release push triggered build `2ab87558-a349-406c-ae00-3beca6c2e0ea` at
`2026-10-24T12:26:45.139151Z` for the same candidate. It succeeded at
`2026-10-24T12:29:42.691125Z`. Read-only smoke at `2026-10-24T12:30:38.9252653Z` confirmed:

- Ready revision `cms-back-release-00147-8xv`, latest-created equals latest-ready, 100% traffic.
- Exact commit/build identity, health/readiness 200 and database `ok`.
- All four normalized configuration hashes equal the baseline; both saved job images match the service.
- Latest migration/effects execution identities are unchanged.
- Public control snapshot remains 22 with the same ID and payload hash as before deployment.
- No ERROR-or-higher entries for the new revision in the bounded post-deploy log check.

Both remote environment refs were verified as `7e08b5484131c24740af771ba0b3127e60d601e0`.
The backend worktree is clean. Product-specification changes were already pushed in `360a8907`.

An initial Git fetch could not select a stored GitHub credential. Supplying the already configured
account name for the individual Git command resolved it; no credentials or Git configuration changed.

## Manual Acceptance

Open practice, service and problem lawyer-section previews in CMS and compare them with their exact
ERP qualification rows. A direct score 2 qualifies; 1 or a missing direct row does not, even with a
parent, child or sibling score 5. Check both team CTA slots as well. These live UI/data acceptance
checks were not performed by this rollout. To apply the result to an existing public page immediately,
review its normal publication plan and explicitly republish it; do not assume deployment did so.

## Publication Boundary And Recovery

Deploy alone neither rewrites public snapshots nor marks them stale. Existing thematic selections adopt
the new rules on explicit page republication or an applicable published-selection refresh. The smoke
does not publish pages or claim a site-wide old/new lawyer membership comparison.

Preferred rollback is a reviewed revert of `7e08b54` through the same pipelines. The revisions above
are emergency traffic rollback points, subject to explicit approval. No schema rollback or data restore
is needed. Already refreshed/published selections would need a separate controlled refresh/republication
to adopt restored selector rules; rolling back code alone does not rewrite them.
