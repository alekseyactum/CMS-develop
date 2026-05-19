# CMS Front Users Task

This document describes the first CMS user-management contract for the CMS frontend.

The backend now has a dedicated users foundation, but this is not yet a full login/session implementation.
Cloud Run remains the outer access boundary for develop. `x-cms-actor` is still a temporary develop-only
audit fallback and must not be treated as release authentication.

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

This layer is only the model and API foundation. A later task must replace the temporary develop actor fallback
with the chosen real auth/session boundary and then wire existing page, section, reference and publish actions
to the resolved CMS user.
