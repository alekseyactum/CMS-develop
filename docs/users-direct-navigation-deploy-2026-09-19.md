# Users Direct Navigation Deployment

## Scope

- User approved pushing and deploying the backend-only navigation fix on 2026-09-19.
- Repository: `re-actum/cms-back`.
- Commit: `0be3c1d7db0ecc2cee1eb28f0d00d240e1dd7f3a`.
- Both `develop` and `release` were fast-forwarded from
  `f394448fef9818a1be7eef006021c44f7c8005bf` to this commit.
- Existing Cloud Build push triggers perform deployment. No pipeline changes.
- The users navigation group links directly to `/admin/users` with no children.
  `users.read` and active/total user counters remain in place.
- No frontend source changes, database migrations, or manual content changes.

## Verification

- GCP preflight passed for project `composite-ally-360719`.
- TypeScript test compilation passed.
- All 18 scoped admin-navigation tests passed, including the post-push run.
- The actual backend response was checked against the existing frontend adapter
  locally for `uk`, `ru`, and `en`, with indicators enabled and disabled.
- The frontend keeps the locale prefix, produces a leaf without children, resolves
  the direct route, and matches it as the active item. Permission exclusion passed.

## Develop

- Build: `3bad72fa-048f-4a99-a699-6a365c7148fd`, `SUCCESS`.
- Active revision: `cms-back-develop-00292-89b`, 100% traffic.
- `/api/health`: `ok`, reporting commit `0be3c1d7db0ecc2cee1eb28f0d00d240e1dd7f3a`.
- `/api/ready`: `ready`.
- Authenticated `/api/admin/navigation?locale=uk&includeIndicators=false` and
  `includeIndicators=true`: direct `/admin/users` route, zero children,
  `users.read`; counters present when requested.

## Release

- Build: `776fee42-328e-4af0-afe9-295f98f52f6e`, `SUCCESS`.
- Active revision: `cms-back-release-00081-z7c`, ready with 100% traffic.
- `/api/health`: `ok`, reporting commit `0be3c1d7db0ecc2cee1eb28f0d00d240e1dd7f3a`.
- `/api/ready`: `ready`.
- Authenticated `/api/admin/navigation?locale=uk&includeIndicators=false` and
  `includeIndicators=true`: direct `/admin/users` route, zero children,
  `users.read`; counters present when requested.
- Both builds updated their existing migration job images as part of the normal
  pipeline; no migration job was executed.
- Manual acceptance: reload CMS and click the top-level users entry. It should
  open the existing users page in one click without a nested item. Live browser
  interaction was not automated; verification used the authenticated backend API
  and the existing frontend adapter.

## Rollback

Previous ready revisions, captured before deployment:

- Develop: `cms-back-develop-00291-6ds`.
- Release: `cms-back-release-00080-j6w`.

The normal rollback is to revert commit `0be3c1d` on the affected deploy branch
and let its existing Cloud Build trigger deploy the revert. An explicitly approved
urgent rollback can route traffic to the previous ready revision, followed by a
matching Git revert. No database rollback is required.
