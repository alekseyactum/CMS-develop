# CMS Front Users Task

This document describes the first CMS user-management contract for the CMS frontend.

The backend now has a dedicated users foundation, but this is not yet a full login/session implementation.
Cloud Run remains the outer access boundary for develop. `x-cms-actor` is still a temporary develop-only
audit fallback and must not be treated as release authentication.

## Current Backend State

Backend now enforces CMS user resolution for all `/api/admin/**` routes through one shared admin auth guard.

That means:

- admin routes are no longer "open by accident";
- backend resolves one `currentUser` for the request;
- permission checks are enforced on admin endpoints by backend metadata;
- legacy write endpoints that still read `x-cms-actor` continue to work because backend now injects the
  resolved actor into request context for them.

Frontend does not need to implement login UI yet for develop, but it must understand that release auth will
replace this transitional mode.

## Endpoints

```text
GET   /api/admin/me
GET   /api/admin/users/meta
GET   /api/admin/users
GET   /api/admin/users/{userId}
POST  /api/admin/users
PATCH /api/admin/users/{userId}
```

## Identity Headers

Preferred future headers:

- `x-cms-user-id`;
- `x-cms-user-email`.

Temporary develop fallback:

- `x-cms-actor`.

`GET /api/admin/me` resolves the current CMS user by `x-cms-user-id` or `x-cms-user-email`. If those are not
present, develop can still use `x-cms-actor` as a temporary fallback. This fallback returns an admin-like
develop actor so existing development flows keep working until real CMS auth/session is wired.

Additionally, backend now supports an explicit develop anonymous bypass for environments where frontend login
is not implemented yet:

- `CMS_DEV_AUTH_ALLOW_ANONYMOUS=true`
- optional `CMS_DEV_AUTH_ANONYMOUS_ACTOR=develop-admin`

When enabled, admin requests without identity headers still resolve to a synthetic full-access develop user.
This is only a develop transition mechanism and must stay disabled for release auth.

## Roles And Permissions

Roles are fixed in backend code for now:

- `admin`;
- `editor`;
- `publisher`;
- `viewer`.

Permissions are also fixed in backend code:

- `pages.read`;
- `pages.write`;
- `pages.publish`;
- `sections.read`;
- `sections.write`;
- `sections.publish`;
- `reference.read`;
- `reference.write`;
- `users.read`;
- `users.manage`.

Use `GET /api/admin/users/meta` to render role selectors and permission descriptions. Do not hardcode roles
or permissions in the frontend.

## Users List

Use:

```text
GET /api/admin/users
```

Optional query params:

- `status`: `active` or `disabled`;
- `q`;
- `limit`;
- `offset`.

Each user has:

- `userId`;
- `email`;
- `displayName`;
- `status`;
- `identityProvider`;
- `externalIdentity`;
- `roles`;
- effective `permissions`;
- `createdAt`;
- `updatedAt`.

## Create User

Use:

```text
POST /api/admin/users
```

Body:

```json
{
  "email": "editor@actum.local",
  "displayName": "Editor Actum",
  "status": "active",
  "roles": ["editor"]
}
```

If `roles` is omitted, backend assigns `viewer`.

## Update User

Use:

```text
PATCH /api/admin/users/{userId}
```

Editable fields:

- `displayName`;
- `status`;
- `identityProvider`;
- `externalIdentity`;
- `roles`.

Use `status: "disabled"` instead of deleting users. Published/draft audit history should remain readable.

## Release Note

This layer is now the enforced backend foundation for admin identity and permissions, but it is still not the
final release login/session implementation. A later task must replace the temporary develop fallback and
anonymous bypass with the chosen real auth/session boundary while keeping the same DB-backed CMS user model,
roles, permissions, and `/api/admin/me` semantics.
