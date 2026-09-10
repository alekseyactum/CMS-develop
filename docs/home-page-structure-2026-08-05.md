# Home Page Structure - Agreed Target - 2026-08-05

This document fixes the agreed product and backend/editor contract for `home_page`.

Implementation status, 2026-08-05: the backend contract described below is implemented on the
`cms-back` branch `codex/home-page-backend`. The implementation includes the fixed schema, localized
bootstrap and idempotent repair of legacy home pages, runtime practice/lawyer/case/publication resolution,
selection validation and diagnostics, publication guards, public payload metadata, and home FAQ JSON-LD.
It does not include the CMS/public frontend adaptation or deployment to `develop`/`release`.

## Page Rules

- `home_page` is the unique non-regional root page for each public locale:
  - Ukrainian: `/`;
  - Russian: `/ru`;
  - English: `/en`.
- The page has no regional children and does not use regional base/override/append inheritance.
- Each locale owns its editable home-page text. Runtime entities are resolved in the requested locale.
- Section order is fixed. Editors cannot add arbitrary sections, move fixed sections, or change the visual
  page composition.
- Header and footer are layout-level global sections and are outside the editable `home_page` schema.
- Runtime/read-model slots are read-only. Where editable text/configuration and runtime cards form one
  visual section, they share a `compositeGroupKey`.
- All main visual sections are fixed and enabled. Only the FAQ and lead-form composites can be disabled.
- A missing, hidden, unpublished, deleted, or untranslated selected object is omitted from the public
  runtime list and produces an admin warning. It does not by itself block home-page publication.
- Public payloads must never expose broken links for omitted or unavailable selected objects.

## Selection Contract

The lawyer, case, and publication showcases use the same explicit selection model:

```json
{
  "selectionMode": "auto",
  "selectedIds": []
}
```

Rules:

- `selectionMode` is required and supports `auto` or `manual`.
- In `auto` mode, backend ignores `selectedIds` and resolves up to the fixed section limit.
- In `manual` mode, backend returns only selected objects. It does not supplement the result with
  automatically selected objects.
- Array order in `selectedIds` is public card order.
- Duplicated selected IDs are invalid editor input.
- The editor accepts no more IDs than the section limit.
- Empty manual selection and an empty resolved runtime list are warnings. The public frontend hides the
  empty card/list part of the composite section.
- Selection configuration is page-owned and versioned with the editable sister section. Runtime card data
  remains read-only and is rebuilt from current source/read-model data during preview and publish.

Canonical identifiers:

- lawyers use the canonical CMS/ERP lawyer ID;
- cases use the editorial locale-group ID rather than one localized page ID;
- blog/media publications use the editorial locale-group ID rather than one localized page ID.

For editorial selections, backend resolves the published member of the locale group for the requested
locale. A locale group without a published member in that locale produces a warning and no public item.

## Target Section Order

### 1. `seo`

- Type: editable metadata section.
- Required and fixed.
- Fields follow the existing page SEO contract: `title`, `description`, optional `canonicalPath`, and
  optional `ogImage`.
- Canonical paths are backend-owned and must resolve to `/`, `/ru`, or `/en` for the matching locale.

### 2. `organization_profile`

- Type: editable metadata section.
- Required and fixed.
- It remains the authoritative CMS source for organization and website identity used by home-page JSON-LD.
- It is not a separate visible block in the public page body.
- Fields follow the existing contract: `name`, optional `alternateName`, optional `legalName`, optional
  `websiteName`, optional `websiteAlternateName`, and optional `logoUrl`.

### 3. `home_intro`

- Type: editable hero section.
- Required, fixed, and cannot be disabled.
- Fields:
  - `title` required and usable as the accessible page H1;
  - `tagline` optional;
  - `lead` optional rich text;
  - `ctaLabel` optional;
  - `ctaTarget` optional controlled internal target.
- The Actum logo, brand typography, background composition, and decorative shapes are frontend-owned
  presentation. The page section must not duplicate the global brand logo as arbitrary editor content.
- `ctaLabel` and `ctaTarget` must be supplied as a valid pair.

### 4. `achievements_strip`

- Type: inherited shared/global recognition section.
- Source: `global_achievements`.
- Required, fixed, and cannot be disabled or overridden on the page.
- Uses the existing inherit-only `achievements_strip` contract.

### 5. `home_practices_intro` + `home_practices`

- Composite group: `home_practices`.
- Purpose: the design block titled as services while presenting the public practice/service tree.
- Required, fixed, and cannot be disabled.

`home_practices_intro`:

- Type: editable page-owned content.
- Fields:
  - `title` required;
  - `lead` optional rich text;
  - `ctaLabel` optional;
  - `ctaTarget` optional controlled internal target, normally the practice collection route.

`home_practices`:

- Type: runtime/read-model list.
- Source: all practices with `show_on_site = true`, including their visible public services.
- Ordering: existing ERP/CMS practice `sort_order`, then localized/source name, then stable ID. Services
  preserve their existing ERP/CMS order inside each practice.
- There is no manual practice selection and no home-specific practice order.
- Missing public target pages produce admin warnings and must not create broken public links.
- An entirely empty practice list is a publish-blocking runtime error because it indicates an invalid main
  navigation/read-model state.

### 6. `home_team_cta` + `home_team_cta_lawyers`

- Composite group: `home_team_cta`.
- Purpose: the large explanatory text plus the single lawyer card shown near the top of the design.
- Required, fixed, and cannot be disabled.

`home_team_cta`:

- Type: editable page-owned content and selection configuration.
- Fields:
  - `title` optional;
  - `paragraphs` optional list;
  - `variant` optional;
  - `selectionMode` required, default `auto`;
  - `selectedIds` optional list, used only in `manual` mode.

`home_team_cta_lawyers`:

- Type: runtime/read-model lawyer showcase.
- Limit: 1 lawyer.
- Auto mode: first eligible visible lawyer in ERP/CMS order.
- Manual mode: the selected lawyer only.
- Reuses the existing no-navigation team CTA card behavior unless the final frontend design explicitly
  introduces lawyer-profile navigation for this block.

### 7. `home_cases_intro` + `home_cases`

- Composite group: `home_cases`.
- Purpose: the successful-cases carousel.
- Required, fixed, and cannot be disabled.

`home_cases_intro`:

- Type: editable page-owned content and selection configuration.
- Fields:
  - `title` required;
  - `lead` optional rich text;
  - `ctaLabel` optional;
  - `ctaTarget` optional controlled case-collection target;
  - `selectionMode` required, default `auto`;
  - `selectedIds` optional ordered locale-group IDs.

`home_cases`:

- Type: runtime/read-model list of published localized `case_page` cards.
- Limit: 8 cases.
- Auto ordering: `isFeatured` first, then `publishedAt` descending, then stable ID.
- Manual ordering: exact `selectedIds` order, without automatic supplementation.

### 8. `home_accent_text`

- Type: editable page-owned accent statement.
- Required, fixed, and cannot be disabled.
- Fields:
  - `title` optional;
  - `lead` required rich text;
  - `variant` optional frontend presentation key.

### 9. `home_lawyers_block` + `home_lawyers`

- Composite group: `home_lawyers`.
- Purpose: the main Actum lawyer/team carousel.
- Required, fixed, and cannot be disabled.

`home_lawyers_block`:

- Type: editable page-owned content and selection configuration.
- Fields:
  - `title` required;
  - `lead` optional rich text;
  - `ctaLabel` optional;
  - `ctaTarget` optional controlled lawyers-directory target;
  - `selectionMode` required, default `auto`;
  - `selectedIds` optional ordered lawyer IDs.

`home_lawyers`:

- Type: runtime/read-model lawyer list.
- Limit: 8 lawyers.
- Auto source: lawyers with `show_on_site = true`.
- Auto ordering: ERP/CMS `sort_order`, then localized/source name, then stable ID. Auto selection is
  deterministic and never random.
- Manual ordering: exact `selectedIds` order, without automatic supplementation.
- Public cards link only to published localized lawyer pages.

### 10. `home_price_text` + `price`

- Composite group: `home_price`.
- Purpose: the price block rendered as the accordion/list shown in the approved design.
- Required, fixed, and cannot be disabled.

`home_price_text`:

- Type: editable page-owned section introduction.
- Fields:
  - `title` required;
  - `lead` optional rich text.

`price`:

- Type: inherited shared/global price section.
- Source: `global_price`.
- Page behavior: inherit only. Home-page editors do not duplicate or override the global price items.
- Accordion behavior is frontend presentation and does not turn price items into FAQ items.

### 11. `home_publications_intro` + `home_publications`

- Composite group: `home_publications`.
- Purpose: one mixed publications carousel containing articles and media materials.
- Required, fixed, and cannot be disabled.

`home_publications_intro`:

- Type: editable page-owned content and selection configuration.
- Fields:
  - `title` required;
  - `lead` optional rich text;
  - `ctaLabel` optional;
  - `ctaTarget` optional controlled publications target;
  - `selectionMode` required, default `auto`;
  - `selectedIds` optional ordered editorial locale-group IDs.

`home_publications`:

- Type: runtime/read-model mixed list.
- Included types: published localized `blog_page` and `media_page`.
- Limit: 8 publications across both types, not 8 per type.
- Auto ordering across the combined stream: `isFeatured` first, then `publishedAt` descending, then stable
  ID.
- Manual ordering: exact `selectedIds` order across both content types, without automatic supplementation.
- Each item exposes its resolved page type and canonical public route so frontend does not infer routes.

### 12. `home_faq`

- Type: editable page-owned FAQ.
- Optional, enabled by default, and independently disableable.
- Fixed immediately before the lead-form composite.
- Fields extend the existing FAQ contract for the home-page design:
  - `title` required when enabled;
  - `lead` optional rich text rendered between the title and question list;
  - `items` optional list of stable question/answer records.
- The `lead` extension is specific to `home_faq`; FAQ sections on practices, services, problems, and intent
  pages retain their existing `title` plus `items` contract.
- Disabled FAQ is absent from the public page payload and JSON-LD.
- Enabled and published FAQ contributes `FAQPage` structured data from the same resolved public content.

### 13. `lead_form` + `lead_capture`

- Composite group: `home_lead_block`.
- Purpose: the application/contact form immediately before the global footer.
- Optional as one visual group, enabled by default, and independently disableable.
- One page-level visibility switch controls the complete composite. Turning the block off removes both the
  inherited form presentation and runtime capture context from the public home payload.

`lead_form`:

- Type: inherited shared/global form content.
- Source: `global_lead_form`.
- Page behavior: inherit only; home-page editors do not override the global form content.

`lead_capture`:

- Type: runtime form context and submit contract.
- Reuses the existing lead-capture boundary and must not expose credentials or provider implementation
  details to the frontend.

The agreed home design does not require a page-specific `lead_questionnaire`. It can be added only through
a later explicit product amendment.

### 14. `site_footer`

- Type: layout-level global section.
- It is rendered after the page payload and remains outside `home_page` authoring and publication.

## Auto-Selection Rules

Auto selection is deterministic and evaluated for the requested locale during preview and snapshot build:

| Showcase | Eligible source | Ordering | Limit |
| --- | --- | --- | --- |
| Team CTA lawyer | visible lawyers | ERP/CMS order | 1 |
| Main lawyers | `show_on_site = true` lawyers | ERP/CMS `sort_order`, name, stable ID | 8 |
| Cases | published localized `case_page` | `isFeatured`, `publishedAt` descending, stable ID | 8 |
| Publications | published localized `blog_page` + `media_page` | `isFeatured`, `publishedAt` descending, stable ID | 8 combined |

Random selection and request-to-request card rotation are not allowed. The same source state must produce
the same snapshot payload.

## Validation And Diagnostics

- Missing required authored text is a publish-blocking error.
- Invalid selection mode, duplicate selected IDs, or more IDs than the section limit is a validation error.
- Empty manual selection is a warning.
- Hidden, deleted, missing, unpublished, or untranslated selected objects produce item-level warnings.
- Auto mode with fewer than the target number of eligible objects is a warning, not an error.
- Auto/manual lawyer, case, or publication runtime resolving to zero items is a warning, not an error; the
  public frontend hides the empty runtime card list.
- An empty `home_practices` runtime list is an error and blocks publish.
- Disabled `home_faq` and `home_lead_block` do not validate their content dependencies and do not produce
  missing-content diagnostics.
- Diagnostics identify the slot, selection mode, selected canonical ID where applicable, requested locale,
  and omission reason.

## Public Payload And Frontend Rules

- Frontend renders backend slot order and does not reconstruct the home composition independently.
- Slots sharing a `compositeGroupKey` form one visual section.
- Frontend never fetches ERP data directly for home showcases.
- Runtime items contain localized display fields, media, resolved `pageType`, and backend-built public route.
- Frontend must not infer editorial translation relationships or synthesize localized URLs.
- Frontend hides empty runtime card/list members while preserving any valid editable sister content when
  the design supports a text-only state.
- Branding artwork, carousel behavior, accordion behavior, spacing, and decorative shapes remain frontend
  presentation concerns.

## Structured Data Rules

- The Ukrainian home page is the primary source of the full global `WebSite` and Actum `Organization`
  nodes, following `docs/json-ld-implementation-requirements-2026-08-03.md`.
- Russian and English home pages reference the global organization and website nodes by stable `@id` and
  expose their own localized page properties.
- The home page has no `BreadcrumbList`.
- Visible typed runtime entities may be referenced only when supported by the structured-data contract.
  Backend must not convert arbitrary visual cards into unsupported schema.org nodes.
- `FAQPage` is emitted only from the enabled, published `home_faq` content rendered publicly.

## Bootstrap And Migration Target

- Backend bootstrap creates one `home_page` per locale and rejects duplicate root pages for the same
  locale.
- New pages default lawyer, case, and publication selection to `auto`.
- `home_faq` and `home_lead_block` default to enabled.
- Bootstrap creates all required page-owned sister sections and inherited bindings needed by the fixed
  composition.
- Existing home-page records created from the earlier `seo` + `organization_profile` scaffold require an
  idempotent repair/backfill that adds missing bindings without replacing existing drafts or published
  metadata.
- Schema, bootstrap, repair, preview, publish, runtime resolution, diagnostics, and public snapshot tests
  must cover all three locales and both selection modes.

## Explicitly Out Of Scope

- Regional home pages.
- Editor-defined section ordering or arbitrary dynamic sections.
- Randomized showcase content.
- Page-level overrides of global achievements, global prices, or global lead-form content.
- Direct frontend access to ERP/read-model tables.
- A page-specific questionnaire unless added by a later product decision.
