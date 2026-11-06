# Media video block: implementation and rollout

Date: 2026-11-06. Scope authorized by the user: implement the video block from
the Media import specification, verify, then push to develop and release.

**Completed:** all six requested deployments succeeded; active revisions carry
the video implementation, with 100% traffic and unchanged runtime configuration.

## Behaviour

- Shared structured YouTube block in the backend, CMS editor and public renderer.
- Both Media modes retain full text and original video positions; Blog and Case
  use the same additive contract without changing existing saved content.
- CMS accepts supported YouTube URLs, provides title/timing fields, diagnostics
  and an embedded preview. Existing add/delete/reorder/save workflows retain IDs.
- Only validated provider, video ID, plain title and optional start/end seconds
  are saved. Arbitrary iframe HTML, sources and executable attributes are rejected.
- The public player is server-rendered, lazy, responsive and accessible; the
  exact `www.youtube-nocookie.com` frame origin is allowed by the report-only CSP.
- Translation changes only title. The existing draft/preview/publication/snapshot
  lifecycle is retained. No database migration or automatic content publication.
- Pure local legacy adapter: [usage](../tools/media-import/README.md). All 23
  original iframes across 29 saved Media sources convert without issue. Actual
  full Media import and verification of every video's availability remain separate.

Participant presentation is outside this video change. No CMS content was written
or published during implementation. Cloud flags, secrets, IAM and database data
were not changed manually. Deployment uses existing branch triggers.

## Baseline / rollback

Preflight passed for the existing operator and GCP project
`composite-ally-360719`, region `europe-central2`. Existing 100% traffic revisions:

| Service | Before video |
| --- | --- |
| cms-back-develop | cms-back-develop-00403-np7 |
| cms-back-release | cms-back-release-00188-j8z |
| cms-front-develop | cms-front-develop-00290-ksg |
| cms-front-release | cms-front-release-00062-6kw |
| site-front-develop | site-front-develop-00143-fzp |
| site-front-release | site-front-release-00039-2gw |

Source bases: backend both branches `8c8c8b0`; CMS develop `8daf0143`, release
`2665c006`; site develop `28650eb`, release `4bc71d8`. Site branch trees matched
despite differing histories. CMS differed in unrelated working-copy/global-section
files; transfer only the video commit to release, preserving those differences.
Rollback is a scoped revert through the same git deployment flow. A runtime traffic
rollback is an emergency action requiring its own explicit decision.

## Verification

Backend: production and test-tree typechecks, build, 352 focused tests passed;
final publication suite 100/100 passed after strengthening preview assertions.
All 23 real converted blocks accepted by the compiled backend in both Media modes
(46 checks). Post-push video contract tests: 8/8 passed.

The full backend sandbox run was stopped after existing HTTP loopback tests failed
with `fetch failed`; it is not represented as a fully green regression run.
The pure Python adapter has five passing tests, including source order/identity,
unsupported hosts/parameters, timing, and the distinction between source links
and actual embedded video IDs.

CMS: 101 focused tests, full ESLint, typecheck, changed-file formatting and
independent contract/draft-flow review passed. The Next editor fixture compiled
and returned HTTP 200; its browser interaction run did not finish before a
tool/runtime restart, so a complete editor browser E2E result is not claimed.
The production Next build passed, including TypeScript and 28 generated pages.
An initial build failure came from a truncated generated `.next/dev` type file
left by the fixture; removing only that generated cache resolved it. The isolated
release cherry-pick passed 16 video/diagnostic tests, with the complete video
surface byte-identical to the tested develop change.

Site: typecheck, scoped ESLint, CSS lint, changed-file formatting and
AC/new-JS/test-edit guards passed. 29 new video tests cover safe parsing, SSR,
preview/public equality in both Media modes and ordering. The expanded targeted
run passed 91 tests with four unrelated failures in the unchanged schema-pull CLI
tests: their `file://${process.argv[1]}` entrypoint comparison fails on Windows.
Post-push video/CSP checks: 33/33 passed.

Actual local browser geometry checks and reviewed screenshots passed: at 375px,
the player is 343×200; at 1440px, 681.59×383.39. No horizontal overflow; text remains
before and after the player. The real YouTube embed returned HTTP 200 and its
title/poster loaded. This checks one representative embed, not playback of all 23.

Full formatting checks reported existing CRLF checkout differences (CMS 1118,
site 732 files). Broad site tests also hit unrelated form timeouts; that run did
not complete before the tool restart. These are recorded limitations, not green
full-suite results. Site local production builds are prohibited by its AGENTS;
the production build is performed by the existing Cloud Build pipeline.
The site's full Linux CI `quality-gate` subsequently passed on both branches:
formatting, JS/CSS lint, typecheck, the full unit suite and AC checks. The local
Windows findings therefore did not reproduce in the deployment environment.

## Deployment receipts

Backend `3dffec7` pushed to both branches. Cloud Build develop
`a00fb030-bdc3-4c28-900c-aeea8192f62b` and release
`556c09be-6f96-4a96-ae2a-4e251126f077` succeeded. New ready revisions
`cms-back-develop-00404-wth` and `cms-back-release-00189-2qv` have 100% traffic.
Both health endpoints return 200 with the expected SHA; both live admin Media
schemas expose the video policy. Runtime configuration digests match the baseline.

During frontend verification another task deployed backend commit `d758dbd`
(`fix(forms): make application emails readable`) on top of `3dffec7`. The ancestry
and diff were checked: it changes only form-delivery code/docs/tests and retains
the complete video change. Do not roll that independent change back as part of
video cleanup. Later observed revisions: develop `00405-l45`, release `00190-vx8`.

Site code pushed to develop `d49ea41` and release `2254df5`; resulting trees match.
CMS code pushed to develop `67f26a1` and release `8c37871`.
CMS post-push video tests: 8/8 passed. Root specification/adapter commit `73629396`
was pushed to the existing `codex/tz-2-to-tz-3-handoff` branch; its five tests passed
again after push.

| Service | Video commit | Successful Cloud Build | Ready revision |
| --- | --- | --- | --- |
| cms-front-develop | `67f26a1` | `3b6740d4-7b53-457d-86ab-cc46c869e438` | `cms-front-develop-00291-bbr` |
| cms-front-release | `8c37871` | `7e38ffa2-04da-4735-a27a-b140c13a8d48` | `cms-front-release-00063-bn2` |
| site-front-develop | `d49ea41` | `75919a67-6cb5-4a62-9c36-5837cb9e2885` | `site-front-develop-00144-s67` |
| site-front-release | `2254df5` | `5661a995-5505-4b1c-b250-1cb4de1a07db` | `site-front-release-00040-bcr` |

Final receipts confirm every latest-created revision is ready and serves 100% of
traffic. Frontend image tags match the successful build IDs for the exact pushed
commits. All six runtime configuration digests match their pre-change baselines.
Both backend health checks and Media schema reads return 200 and expose video.

Direct HTTP smoke of the protected frontends returns 401 both before and after
rollout with the available operator token. Authentication was not weakened to make
that check pass. Frontend acceptance here consists of successful CI/deploy/image
verification, local renderer/browser checks and CMS contract/draft tests; complete
live authenticated editor interaction is still a manual acceptance check.

Local receipts: `outputs/media-video-block-2026-11-06/final-runtime.json`,
`legacy-video-audit.json`, and site worktree `test-results/video-browser.json`
with desktop/mobile screenshots. These operational files are not committed.

## Acceptance procedure

In a Media draft, insert a video between two paragraphs, enter its URL and title,
change timing, reorder, save and reopen. Verify field diagnostics for an invalid
address/title/time. Compare preview and a deliberately published test snapshot
in both Media modes, including narrow/mobile geometry. Saving must not publish.
The actual import must flag unavailable/private/embedding-disabled videos rather
than count a valid-looking video ID as proof of playback.
