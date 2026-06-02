# Site Layout, Header, And Contact Settings Requirements

This document fixes the first release decision for site-wide layout data.

## Core Decision

Header, footer, footer practices, and contact settings are layout-level data.
They must not be copied into every page snapshot.

The public frontend reads two separate payloads:

- page payload: published content for the current page;
- layout payload: shared header/footer/contact data for the current locale.

Example:

```http
GET /api/public/layout?locale=uk
GET /api/public/pages/by-route?route=/contacts
```

CMS admin also has a layout preview endpoint:

```http
GET /api/admin/site-layout/preview?locale=uk
```

Admin preview returns the same layout shape, but uses the latest global section
editor state where a draft exists. It is intended for the CMS interface, not for
public rendering.

Page snapshots remain the source of truth for page-specific content: SEO, title,
body sections, page price, FAQ, lawyers/reviews/runtime blocks, and other page
sections.

Layout payload is the source of truth for:

- `site_header`;
- `site_header_services_menu`;
- `site_footer_practices`;
- `site_footer`;
- `site_contact_settings`.

Changing layout-level data must not republish all pages. Later the backend will
trigger frontend/CDN revalidation for layout tags or layout HTML cache.

## Admin Menu Placement

The CMS sidebar should show layout/global items in the `global_sections` group
("Глобальные" in the UI), but the group is mixed by design:

- `site_header`: versioned global section;
- `site_footer_practices`: versioned/read-only global diagnostics workbench;
- `site_footer`: versioned global section;
- `global_price`: versioned global section and page snapshot source;
- `site_contact_settings`: non-versioned site settings item.

`site_contact_settings` must use `kind = "site_settings"` and target
`site_settings_editor`, not `global_section_editor`. It is placed next to
header/footer because it affects the same public layout, but frontend must not
show draft/publish/history controls for it.

## `site_contact_settings`

`site_contact_settings` is not a section.

It is a simple site settings record for small operational data used by several
parts of the website.

It stores:

- primary phone;
- display phone;
- work time `{ from, to }`;
- `updatedAt`;
- `updatedBy`.

It does not have:

- draft;
- publish;
- section version history;
- rollback;
- inheritance;
- page snapshot refs;
- stale state.

It is used by:

- header;
- footer;
- contacts page;
- CTA/forms;
- other public places that need the same phone or work time.

Rule: site settings must not become a content dump. They are only for small
global operational values that are shared across multiple layout/page surfaces
and do not need authoring lifecycle.

## `site_header`

`site_header` is a layout-level global section with a normal global section
workflow:

- draft;
- publish;
- history;
- rollback/create draft from version;
- diagnostics.

Only minimal UI flags are versioned in the editable content:

```ts
{
  searchEnabled: boolean;
  contactButtonEnabled: boolean;
}
```

Everything else is read-only/system/runtime in the editor and public layout
payload:

- top-level navigation;
- about dropdown;
- services mega menu;
- phone and work time from `site_contact_settings`;
- language policy;
- mobile actions derived by frontend.

The global section editor response must expose three clear content layers:

- `readonlyContent`: navigation contract, services menu policy, labels, contact
  settings source, and editable field descriptions;
- `editableContent`: only the saved/draft values that frontend may send back;
- `workingContent`: merged content for current editor display.

`readonlyContent` also exposes explicit related endpoints so the CMS frontend
does not have to hardcode hidden relationships:

```ts
{
  layoutPreview: {
    endpoint: "/api/admin/site-layout/preview?locale=uk",
    usesLatestDrafts: true
  },
  publicLayout: {
    endpoint: "/api/public/layout?locale=uk",
    usesPublishedVersions: true
  },
  contactSettings: {
    source: "site_contact_settings",
    editableIn: "site_contact_settings",
    endpoint: "/api/admin/site-settings/contact",
    target: {
      kind: "site_settings_editor",
      settingsKey: "contact"
    },
    fields: ["phonePrimary", "phoneDisplay", "workTime"]
  }
}
```

The frontend must save only `editableContent` fields for `site_header`.

### Top-Level Navigation

Top-level header navigation is system-owned and not editable in the first
release:

- `home`;
- `about` dropdown;
- `services` mega menu;
- `lawyers`;
- `career`;
- `contacts`.

The `about` dropdown contains system links:

- about;
- blog;
- media;
- cases.

If a top-level or about-dropdown system page is not published, the public layout
keeps the item but marks it as disabled and emits admin diagnostics.

### Services Mega Menu

The `services` mega menu is always national for the first release. It does not
change by current regional page.

It contains:

- practices;
- services;
- problems.

Inclusion rules:

- practice: `show_on_site = true`, has label, has slug, has published page;
- service: `show_on_site = true`, `service_cond = true`, has label, has slug,
  has parent practice, has published page;
- problem: `show_on_site = true`, has label, has slug, has parent service and
  practice, has published page.

If an enabled object is missing label/slug/parent/published page, public layout
omits it from the mega menu and admin diagnostics warn about the issue.

Frontend owns visual column layout. Backend returns a structured tree, not
columns.

### Search

Search is only a UI trigger in the first release:

```ts
searchEnabled: true
```

Search API/indexing is a separate future task.

### Contact Button

The header contact button opens a frontend callback/contact modal:

```ts
{
  type: "callback_modal",
  label: "Зв'язатись"
}
```

The label is code-owned by locale in the first release.

### Languages

Layout payload exposes language policy only:

```ts
{
  locales: ["uk", "ru", "en"],
  defaultLocale: "uk"
}
```

Concrete alternate-language links are page context and must come from page
payload. If the current page is not published in another locale, the language is
shown disabled.

### Active Navigation

The active top-level navigation key comes from page payload, not layout payload.

Examples:

- generated practice/service/problem pages: `services`;
- lawyers list and lawyer profile: `lawyers`;
- contacts page: `contacts`;
- about/blog/media/cases: `about`.

## `site_footer_practices`

`site_footer_practices` is a layout-level read-only global workbench.

It is powered by practice reference data and public page availability.

It does not store or version the rendered practice list. Public layout contains
only valid/published links. Admin diagnostics explain omitted practice links.

Its editor `readonlyContent` exposes:

```ts
{
  layoutPreview: {
    endpoint: "/api/admin/site-layout/preview?locale=uk",
    usesLatestDrafts: true
  },
  publicLayout: {
    endpoint: "/api/public/layout?locale=uk",
    usesPublishedVersions: true
  },
  practiceSource: {
    source: "reference_data",
    resource: "practices",
    endpoint: "/api/admin/reference/practices",
    filters: { showOnSite: true },
    labelField: "translations.{locale}.menuTitle",
    routeField: "sourceFields.sourceSlug",
    editable: false
  }
}
```

## `site_footer`

`site_footer` is a layout-level editable global section for footer-owned
settings.

Editable content:

```ts
{
  socialUrls: {
    telegram?: string | null;
    youtube?: string | null;
    instagram?: string | null;
    facebook?: string | null;
    whatsapp?: string | null;
  };
  legalDocuments: {
    privacyPolicyMediaId: string | null;
    offerContractMediaId: string | null;
  };
}
```

`site_footer` no longer owns work time. Work time is read from
`site_contact_settings`.

Footer legal PDF files use media records with `usageType = "legal_document"`.
Missing legal files are warnings. Invalid media records are errors.

Its editor `readonlyContent` exposes:

```ts
{
  layoutPreview: {
    endpoint: "/api/admin/site-layout/preview?locale=uk",
    usesLatestDrafts: true
  },
  publicLayout: {
    endpoint: "/api/public/layout?locale=uk",
    usesPublishedVersions: true
  },
  contactSettings: {
    owner: "site_contact_settings",
    editable: false,
    endpoint: "/api/admin/site-settings/contact",
    target: {
      kind: "site_settings_editor",
      settingsKey: "contact"
    },
    fields: ["phonePrimary", "phoneDisplay", "workTime"]
  },
  legalDocumentsPolicy: {
    usageType: "legal_document",
    mediaMetaEndpoint: "/api/admin/media/meta",
    mediaListEndpoint: "/api/admin/media?usageType=legal_document&lifecycleState=active&uploadState=uploaded",
    mediaUploadEndpoint: "/api/admin/media/upload",
    allowedMimeTypes: ["application/pdf"],
    maxSizeBytes: 5242880,
    fields: ["privacyPolicyMediaId", "offerContractMediaId"]
  }
}
```
