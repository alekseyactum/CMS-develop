# Site Footer Section Workbench

This document fixes the first-release product and backend contract for the public site footer.

## Scope

The visual footer is not one fully editable CMS constructor.

It is assembled from three ownership layers:

- `site_footer_practices`: a read-only global section for the upper footer practice block;
- `site_footer`: a global CMS section for footer-owned editable settings and legal document refs;
- `site_contact_settings`: simple site settings for the public phone and work time.

The frontend may render these pieces as one visual `<Footer />`, but backend data ownership must stay
separate.

## Footer Global Sections

The footer is represented by two separate global sections:

```text
site_footer_practices / uk
site_footer_practices / ru
site_footer_practices / en

site_footer / uk
site_footer / ru
site_footer / en
```

Both sections are:

- `global_owned`;
- independent;
- fixed at page end;
- not page-owned;
- not overridden per page;
- layout-level payload sources;
- not copied into page snapshots;
- published without affected page snapshot rebuild.

The frontend may render them as one visual footer, but the backend must keep them as separate section
slots and separate section histories.

## Shared Section Rules

Use the normal global section rules unless this document explicitly says otherwise:

- errors block draft save and publish;
- warnings do not block draft save or publish, but must be visible in diagnostics, history, and global
  menu indicators;
- draft changes do not change the public layout payload;
- publish creates/reuses a published section version and affects the public layout payload;
- publish does not rebuild page snapshots;
- rollback creates a new draft copied from an old published version.

## `site_footer_practices`

The practice list shown at the top of the footer is not edited inside `site_footer`.

It is a separate read-only global section:

```text
sectionKey: site_footer_practices
source for rendered items: practice reference data
```

For the first release, the CMS editor may view this section and its diagnostics, but must not edit its
content.

### Code-Owned Content

`site_footer_practices` should not store editable settings in section version content.

The backend registry owns:

- localized block title:
  - `uk`: `ПРАКТИКИ`;
  - `ru`: `ПРАКТИКИ`;
  - `en`: `PRACTICES`;
- inclusion rules;
- sorting rule;
- diagnostics policy.

The frontend owns visual layout, including column count and responsive wrapping. The backend does not
send pre-split columns.

### Resolved Public Payload

The public payload is resolved from practice reference data for the active locale:

```ts
{
  title: string;
  items: Array<{
    label: string;
    href: string;
    sourcePracticeId: string;
  }>;
}
```

Rules:

- include every active/public-visible practice that passes the footer requirements;
- do not impose a backend `maxItems` limit in the first release;
- sort by localized practice name;
- link label comes from the practice localization `menuTitle`;
- no fallback from `menuTitle` to `publicName`;
- if `menuTitle` is missing for the active locale, omit the practice and add a warning;
- if public route/slug is missing, omit the practice and add a warning;
- do not add a separate "hide from footer" CMS field;
- do not store the rendered practice list in `site_footer` content;
- do not store the rendered practice list in `site_footer_practices` version content.

Open implementation note:

When practice reference data changes, `site_footer_practices` layout diagnostics and public layout cache
may need revalidation. This must not be treated as a page snapshot rebuild because footer practices are
served from the layout payload, not from page payloads.

## `site_footer`

`site_footer` is the lower footer settings section.

It uses the normal global section lifecycle:

- draft/published versions;
- history;
- validation;
- rollback by creating a new draft from an old version;
- publish into the shared layout payload.

The footer section is a shared fixed global section:

- fixed at page end;
- not page-owned;
- not overridden per page;
- ordinary drafts do not make page editors stale;
- publishing changes the layout payload and does not rebuild page snapshots.

## Editable Fields

The first editable `site_footer` content is intentionally narrow.

Editors may edit only:

- social network URLs;
- legal PDF document media refs for privacy policy and offer contract.

Suggested editable shape:

```ts
type SocialType = 'telegram' | 'youtube' | 'instagram' | 'facebook' | 'whatsapp';

{
  socialUrls: Partial<Record<SocialType, string | null>>;
  legalDocuments: {
    privacyPolicyMediaId: string | null;
    offerContractMediaId: string | null;
  };
}
```

Important:

- the allowed social network list is code-owned in backend registry;
- social order is code-owned in backend/frontend registry;
- editor changes only URLs;
- empty social URL means this social network is hidden;
- there is no separate `visible` flag in the first release;
- duplicates are impossible by contract because social URLs are keyed by social type;
- unknown social type from frontend is an error.

`workTime` is not owned by `site_footer`. It is stored in `site_contact_settings` and reused by header,
footer, contacts, and forms as one shared `from/to` time pair.

Social URLs are also locale-neutral. Legal PDF documents are locale-specific because documents may differ
by language.

## Read-Only / Code-Owned Fields

The CMS UI may display these footer parts, but they are not edited in `site_footer` for the first
release:

- practice links, owned by `site_footer_practices`;
- first-level site navigation links;
- contact label, public phone, and work time, which are owned by `site_contact_settings`;
- legal link labels;
- sitemap route;
- copyright format.

This keeps the first footer workflow reliable and avoids turning the footer into a free-form HTML/menu
builder.

## Contact Settings

The public phone and work time are owned by `site_contact_settings`.

Backend does not store, version, validate, or publish them in `site_footer`.
They are simple site settings without draft/publish/snapshot lifecycle and are reused by header, footer,
contacts, and forms.

## Site Navigation Links

Footer navigation links are first-level site links, not free editor-entered URLs.

For the first release they are code-owned route items. The footer UI may show them read-only.

Open implementation detail:

- initially labels may be locale constants in the renderer/route registry;
- later labels may come from page metadata such as `menuTitle`, if that becomes a stable CMS contract.

Do not duplicate editable footer labels until the page metadata contract is clear.

## Legal Links And Documents

Legal links use mixed ownership:

- sitemap is a system route;
- privacy policy and offer contract are CMS-managed legal PDF media records.

The `site_footer` version stores concrete media ids:

```ts
{
  legalDocuments: {
    privacyPolicyMediaId: string | null;
    offerContractMediaId: string | null;
  }
}
```

Public payload resolves those ids to stable public URLs:

```ts
{
  legalLinks: [
    { type: 'sitemap', label: string, url: string },
    { type: 'privacy_policy', label: string, url: string },
    { type: 'offer_contract', label: string, url: string }
  ]
}
```

Rules:

- legal labels are code-owned in backend registry by locale;
- sitemap label and route are code-owned;
- privacy/offer files are stored through the CMS media contour;
- physical files are in Cloud Storage or compatible object storage;
- DB stores only media metadata and ids;
- allowed mime: PDF only;
- max PDF size: 5 MB;
- missing privacy/offer file is a warning and the link is omitted from public payload;
- invalid mime/size is an error at upload/save;
- a media file used by a published footer version/layout payload cannot be deleted;
- rollback of `site_footer` restores the old media ids, so old published footer versions keep their
  original documents.

The CMS footer editor should show each linked PDF as filename, size, upload date, and open/download
action. Inline PDF preview is not required.

## Copyright

Copyright is not edited in CMS.

Backend registry provides read-only data such as:

```ts
{
  copyright: {
    prefix: 'Copyright',
    year: 2026
  }
}
```

The year should be generated from the current year at render/payload build time, not manually edited in
section content.

## Validation Policy

### `site_footer_practices`

Warnings:

- active practice has no `menuTitle` for the active locale, so it is omitted from footer;
- active practice has no public route/slug, so it is omitted from footer.

Errors should be reserved for broken backend state, invalid payload shape, or impossible route resolution
failures that prevent building the section at all.

### `site_footer`

Errors:

- invalid content object;
- invalid `socialUrls` shape;
- unknown social type;
- social URL has a non-HTTP(S) format;
- legal document media id points to missing media record;
- legal document media record is not a PDF;
- legal document media record exceeds 5 MB.

Warnings:

- social URL uses `http://` instead of `https://`;
- privacy policy PDF is missing;
- offer contract PDF is missing.

No warning is needed for an empty social URL. Empty URL simply means the social network is hidden.

Phone and work time are validated by the `site_contact_settings` API, not by `site_footer`.

## Frontend CMS Behavior

The dedicated footer screen should start from one aggregated endpoint:

```http
GET /api/admin/site-layout/footer-workbench?locale=uk&historyLimit=20&historyOffset=0
```

This endpoint is a screen convenience API. It does not replace the normal global
section lifecycle endpoints. It returns:

- `footerSection`: editable `site_footer` editor state;
- `footerPracticesSection`: read-only `site_footer_practices` preview and diagnostics;
- `layoutPreview.footer`: combined admin-preview footer payload;
- `contactSettings`: phone/work-time settings used by the footer;
- `mediaPolicy`: legal PDF constraints and media endpoints;
- `history`: `site_footer` version rows;
- `workbench`: frontend hints for editable/read-only response sources;
- `endpoints`: exact action endpoints for the screen.

The only editable footer draft payload is `footerSection.editableContent`.
Everything else in the workbench response is read-only context, a related
settings flow, or an action endpoint.

The workbench also exposes:

```ts
workbench.refreshAfterActions = {
  strategy: 'reload_workbench',
  method: 'GET',
  path: '/api/admin/site-layout/footer-workbench?locale=uk&historyLimit=20&historyOffset=0',
  appliesTo: [
    'footerSaveDraft',
    'footerValidateDraft',
    'footerPublishDraft',
    'footerRollback',
    'footerDraftFromVersion',
    'contactSettings',
    'mediaUpload'
  ]
}
```

This is the preferred first-release action flow. The frontend does not need
special wrapper endpoints for footer actions: after an action succeeds or
returns diagnostics, reload the workbench and replace the full screen state.

The global section validate response for `site_footer` returns both generic
`validation` and footer-specific `diagnostics`. The visible CMS form should use
`diagnostics` for field indicators, because it includes social URL checks and
legal PDF media checks.

The footer workbench should:

- use the aggregated workbench endpoint for the first screen load;
- show the locale-specific `site_footer_practices` state for read-only practice preview and diagnostics;
- show the locale-specific `site_footer` state for editable lower-footer settings;
- show read-only preview/info for non-editable footer parts;
- edit only social URLs and legal PDF media refs;
- use the media upload/picker flow for legal PDF files;
- save the full editable `site_footer` draft through the global sections API;
- use history/rollback/publish from the same global section workflow as other globals.

The UI should not expose editable fields for phone, first-level navigation, legal labels, sitemap, or
practice list ordering until the backend contract changes.
