# Office address warning threshold rollout — 2026-09-14

Owner approved develop/release automatic deployment. Playbook preflight passed before cloud reads.
Canonical `re-actum/cms-back` feature/develop/release now point to
`780110a0028ec052517bd5c7979e3f5f2c76cd3c`, fast-forward from
`0ab9920076ac229e554a557e9d6c2a9c47579213`.

Localized office addresses now warn only above 100 characters (previously 70). Required-address,
short-address and other validation behavior is unchanged. No migration execution, content changes,
republishing, IAM or pipeline changes. Existing pipeline updates migration job images without execution.

## Evidence

Project `composite-ally-360719`, region `europe-central2`.

| Environment | Successful build | Previous revision | New ready revision, 100% traffic |
|---|---|---|---|
| develop | `cc156689-c71a-45ff-ac8c-f454f8457599` | `cms-back-develop-00282-xck` | `cms-back-develop-00283-rch` |
| release | `4c37aa8a-42bf-483d-9e53-59f5a20bbcf9` | `cms-back-release-00071-s6q` | `cms-back-release-00072-fn8` |

- Health/ready succeeded on both environments with expected SHA and database ok.
- All 830 tests and application build passed after each push; backend working tree clean.
- Release read-only office list before/after: office `dc843fa4-ea77-4781-b420-045e6c0de18c` retained
  uk/ru/en lengths 60/71/79; its two length warnings disappeared. Office
  `683574e3-1e5b-4f98-b69c-42ff004838d3` retained lengths 80/84/76; its three length warnings disappeared.
- No office data was written. Live checks cover these examples; 100/101 boundaries are covered by tests.
- No ERROR-or-higher entries returned for new revisions during the bounded post-deploy check.
- Browser UI and develop admin functional check were not performed; functional live evidence is release API.

## Manual check / rollback

Reopen the office card: addresses of 100 characters or fewer should not have a length warning. No page
republishing is needed. Addresses above 100 still warn; this is not a hard save limit or DB capacity change.
Risk: long addresses may still wrap in frontend layouts; existing display behavior is unchanged.
Normal rollback: reviewed revert of `780110a` via existing pipelines; no DB rollback. Emergency traffic
rollback to prior revisions above needs explicit approval. Implementation contract is in
`cms-back/docs/office-address-warning-limit-2026-09-14.md`.
