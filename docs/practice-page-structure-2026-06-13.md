# Practice Page Structure - Agreed Target - 2026-06-13

This document fixes the agreed target structure for `practice_page`.

It is a product/implementation target for the next page-workbench pass. It does not mean every slot below
is already implemented in backend code exactly this way.

2026-06-13 implementation status: the first backend pass aligned the main `practice_page` schema order,
composite groups, `practice_related_legal`, `practice_reviews_block`, `practice_reviews_text`,
`practice_price_text`, inherited regional source policies, inherit-only page-level `lead_form` strategies,
runtime resolvers for related legal, reviews, regional services, and regional lawyers, and hard page-editor
read-only behavior for inherit-only page slots such as `lead_form`. It also marks section-heading fields in
schema/editor payloads, blocks regional heading overrides in page authoring, and adds the first hard-error
content validation rules for structured practice sections. It also persists section validation warnings in
the section lifecycle tables and returns them through editor validation, editor diagnostics, and workbench
cell/row diagnostics. Legal-only service rows (`legal_cond=true`, `service_cond=false`) are generated
`service_page` sources for CMS page workbench purposes. The page workbench matrix now uses the backend
runtime resolver to add linked-page warning diagnostics to `practice_services`, `practice_related_legal`,
and `practice_lawyers` runtime cells. Schema/workbench columns expose `defaultVisibility`;
`practice_intro_text` and `practice_actions` default to enabled, while the other optional practice sections
still default to disabled.

## General Rules

- `practice_page` is a generated service-hierarchy page for one practice:
  `/services/{practiceSlug}` and regional variants such as `/{regionSlug}/services/{practiceSlug}`.
- Header, footer, breadcrumbs, and route/context navigation are outside editable page sections.
- Public canonical URLs are backend-owned and self-canonical for both base and regional routes.
- Regional pages inherit editable page-owned content from the matching base/Ukraine page by default.
- Regional divergence must be explicit through section/field composition override or append where the
  schema allows it.
- `draft_stale` is an editor attention/review marker, not a hard publish blocker. Publishing a page accepts
  the current backend-resolved inherited content when no critical validation or runtime blockers remain.
- Section headings are locked for regional override. The base page/global source may edit a section
  heading, but a regional page must inherit it. This rule applies to section titles/headings, not to SEO
  title, page title, FAQ item questions, action item titles, lawyer names, or runtime object names.
- Runtime/read-model slots are read-only for the editor. They may be paired with editable CMS text through
  `compositeGroupKey`; frontend should render each composite group as one visual block.
- Runtime rows with missing or unpublished linked public pages stay visible in admin payloads with warnings.
  Public rendering must not create broken links; use disabled/non-link rendering where needed.
- Long text warnings are editor-quality diagnostics unless explicitly marked as errors below.

## Target Section Order

### 1. `seo`

- Type: editable metadata section.
- Required.
- Fixed position.
- Regional behavior: inherited from base by default; explicit override allowed.
- Canonical path is backend-owned/self-canonical, not editor-owned.
- Fields:
  - `title` required, default from practice name, editor-editable.
  - `description` required, default from practice name or backend default, editor-editable.
  - `ogImage` optional.
- Validation:
  - empty required fields are errors;
  - SEO length/quality issues are warnings;
  - bad media reference is warning when a frontend/site fallback can be used.

### 2. `practice_intro`

- Type: editable hero/intro section.
- Required.
- Fixed position.
- Cannot be disabled.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Fields:
  - `title` required, default from practice name, section-heading locked for regional override.
  - `lead` optional rich text.
  - `ctaLabel` optional.
  - `ctaTarget` optional controlled target, not a free external URL.
- Validation:
  - missing title is an error;
  - `ctaLabel` and `ctaTarget` must be a valid pair;
  - CTA target must be one of backend-supported choices.

### 3. `achievements_strip`

- Type: inherited shared/global recognition section.
- Source: `global_achievements`.
- Required.
- Fixed after hero.
- Present on home page and service-hierarchy pages except `practice_collection_page`.
- Page-level override/append is not allowed.
- Cannot be disabled or moved.
- Fields from global source:
  - `items[]` required.
  - Item `sourceName` required unless `sourceLogo` exists.
  - Item `sourceLogo` optional media/text-logo fallback.
  - Item `achievementText` required.
- Validation:
  - fewer than 3 items is a warning;
  - empty `achievementText` is an error;
  - missing both `sourceName` and `sourceLogo` is an error;
  - bad media reference is warning if text fallback exists and error if no logo/name fallback exists;
  - overlong `sourceName` or `achievementText` is a warning.

### 4. `practice_services_block` + `practice_services`

- Composite group: `practice_services`.
- Purpose: main service list for the current practice.
- Required.
- Fixed position.
- Cannot be disabled.

`practice_services_block`:

- Type: editable CMS text block.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Fields:
  - `title` required, section-heading locked for regional override.
  - `accentTitle` optional highlighted title fragment, inherited from the base page and locked for regional override.
  - `lead` optional rich text/plain text.

`practice_services`:

- Type: runtime/read-model list.
- Runtime source:
  - current practice services;
  - `show_on_site = true`;
  - `service_cond = true`;
  - regional rows additionally filter by regional competence.
- Routes use the normal service-page route structure.
- Ordering: `sort_order`, then localized/source name, then stable id.
- Validation/diagnostics:
  - empty runtime list blocks publish;
  - missing or unpublished linked service page is an admin warning;
  - public item renders disabled/non-link when no published target exists.

### 5. `practice_related_legal_block` + `practice_related_legal`

- Composite group: `practice_related_legal`.
- Purpose: separate "may interest you" list, not part of the main services list.
- Optional.
- Can be disabled.
- Fixed position after `practice_services`.

`practice_related_legal_block`:

- Type: editable CMS text block.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Fields:
  - `title` required when enabled, section-heading locked for regional override.
  - `accentTitle` optional highlighted title fragment, inherited from the base page and locked for regional override.
  - `lead` optional rich text/plain text.

`practice_related_legal`:

- Type: runtime/read-model list.
- Runtime source:
  - current practice rows;
  - `show_on_site = true`;
  - `legal_cond = true`;
  - `service_cond = false`;
  - regional rows additionally filter by regional competence.
- Routes use the same generated service-page route shape as service pages.
- Validation/diagnostics:
  - empty enabled runtime list is a warning, not a publish blocker;
  - missing or unpublished linked page is an admin warning and public disabled/non-link item.

### 6. `practice_intro_text`

- Type: optional editable text section.
- Variant: `accent_panel`.
- Position: after `practice_related_legal`.
- Enabled by default.
- Can be disabled.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Append is not allowed.
- Cannot be moved.
- Fields:
  - `title` optional, section-heading locked for regional override.
  - `description` / `lead` optional rich text/plain text.
- Validation:
  - enabled section with no title and no text is an error;
  - overlong title/text is a warning.

### 7. `practice_actions`

- Type: editable structured list section.
- Purpose: lawyer action list.
- Optional but enabled by default.
- Can be disabled.
- Fixed position after `practice_intro_text`.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Append is not allowed.
- Cannot be moved.
- Fields:
  - `title` required, section-heading locked for regional override.
  - `description` / `lead` optional rich text/plain text.
  - `items[]` required when enabled.
- Item fields:
  - `title` required.
  - `description` optional.
- Validation:
  - enabled section with empty item list is an error;
  - target item count is 2-8;
  - empty item title is an error;
  - overlong title/description/item text is a warning.

### 8. `practice_team_cta`

- Type: editable text plus runtime lawyer showcase.
- Purpose: introduce lawyers one by one; card interaction advances/changes selected lawyer in JS.
- Required.
- Fixed position after `practice_actions`.
- Cannot be disabled.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Append is not allowed.
- Cannot be moved.
- No URL navigation from lawyer cards in this section.
- Fields:
  - `title` optional, section-heading locked for regional override; absence is valid and has no diagnostic.
  - `lead` optional rich text/plain text.
  - optional secondary/help text if the frontend design needs it.
- Runtime lawyer source:
  - lawyers linked to the practice;
  - active/show-on-site lawyers only;
  - regional rows filter by region and lawyer competence;
  - competence score must be greater than 1.
- Validation/diagnostics:
  - empty lawyer collection is a warning, not a blocker;
  - bad/missing photo is a warning and should use frontend fallback;
  - overlong title is a warning.

### 9. `practice_cases`

- Type: runtime/read-model list.
- Required in page structure.
- Cases read model is not ready yet.
- Empty placeholder is allowed for now and should produce a warning, not a publish blocker.

### 10. `practice_reviews_block` + `practice_reviews`

- Composite group: `practice_reviews`.
- Required.
- Fixed after cases.

`practice_reviews_block`:

- Type: editable CMS text block.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Fields:
  - `title` required, section-heading locked for regional override.
  - `lead` optional.

`practice_reviews`:

- Type: runtime/read-model list.
- Source: `cms_ref_reviews`.
- Filters:
  - current practice identifier;
  - current region for regional pages.
- Runtime order is not important for the current CMS decision.
- Validation/diagnostics:
  - empty reviews list is a warning, not a blocker.

### 11. `practice_reviews_text`

- Type: optional editable text section.
- Variant: `proof_band`.
- Position: after `practice_reviews`.
- Disabled by default.
- Can be disabled/enabled independently.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Append is not allowed.
- Cannot be moved.
- Fields:
  - `title` optional, section-heading locked for regional override.
  - `description` / `lead` optional rich text/plain text.
- Validation:
  - enabled section with no title and no text is an error;
  - overlong title/text is a warning.

### 12. `price`

- Type: inherited price section.
- Required.
- Fixed after `practice_reviews_text`.
- Cannot be disabled.
- Source/inheritance:
  - base practice page inherits from `global_price`;
  - regional practice page inherits from the matching base practice page price section.
- Page-level editor may use the existing price inheritance model, including allowed override/append
  behavior where already supported by price schema.
- Validation/diagnostics:
  - incomplete or suspicious price content is a warning unless the price schema marks it as an error;
  - parent/global draft changes produce stale/admin warning;
  - page publish accepts current published inherited price and does not publish global price drafts.

### 13. `practice_price_text`

- Type: optional editable text section.
- Variant: `price_note`.
- Position: after `price`.
- Disabled by default.
- Can be disabled/enabled independently.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Append is not allowed.
- Cannot be moved.
- Fields:
  - `title` optional, section-heading locked for regional override.
  - `description` / `lead` optional rich text/plain text.
- Validation:
  - enabled section with no title and no text is an error;
  - overlong title/text is a warning.

### 14. `practice_faq`

- Type: optional editable FAQ section.
- Position: after `practice_price_text`, before `practice_lawyers`.
- Disabled by default.
- Can be disabled/enabled.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Append is allowed for FAQ items.
- Cannot be moved.
- Fields:
  - `title` required when enabled, section-heading locked for regional override.
  - `items[]`.
- Item fields:
  - `question` required.
  - `answer` required rich text/plain text.
  - `sortOrder` / editor order.
- Validation:
  - enabled section with empty item list is an error;
  - fewer than 3 questions is a warning;
  - empty question or answer is an error;
  - overlong title/question/answer is a warning.

### 15. `practice_lawyers_block` + `practice_lawyers`

- Composite group: `practice_lawyers`.
- Purpose: choose a concrete lawyer.
- Required.
- Fixed after FAQ and before the lead block.
- Cannot be disabled.

`practice_lawyers_block`:

- Type: editable CMS text block.
- Regional behavior: inherited from base by default.
- Fields:
  - `title` required, section-heading locked for regional override.
  - `description` / `lead` optional and overrideable.
- Append is not allowed.

`practice_lawyers`:

- Type: runtime/read-model list.
- Runtime source:
  - lawyers linked to current practice;
  - active/show-on-site lawyers only;
  - regional rows filter by region and lawyer competence;
  - competence score must be greater than 1;
  - one lawyer may have multiple competencies, match by any eligible competence.
- Card behavior:
  - lawyer card links to the lawyer public page;
  - missing or unpublished lawyer page renders disabled/non-link and produces admin warning.
- Validation/diagnostics:
  - empty lawyer collection is a warning, not a blocker;
  - bad/missing photo is a warning with frontend fallback;
  - overlong title/description/name/position is a warning.

### 16. Lead Block: `lead_questionnaire` + `lead_form` + `lead_capture`

- Composite visual block at the bottom of `practice_page`.
- Composite group key in workbench responses: `lead_block`.
- Position: after `practice_lawyers`.
- Frontend should render these backend slots as one lead/application block. Use `row.compositeGroups`
  when available instead of pairing these slots locally.
- The slots intentionally keep different lifecycles.

`lead_questionnaire`:

- Type: optional page-specific questionnaire section.
- Disabled by default.
- Can be disabled/enabled.
- Regional behavior: inherited from base by default; explicit override allowed except section title.
- Append is allowed for questions.
- Cannot be moved separately from the lead block.
- Fields:
  - `finalMessageTitle` optional final-state heading.
  - `finalMessageDescription` optional final-state rich text.
  - `questions[]`.
- Question fields:
  - `id` required stable technical ID.
  - `question` required.
  - `type`: `single_choice` or `multiple_choice`.
  - `options[]` required, each with stable `id` and visible `label`.
  - `required` boolean, default `false` for legacy content.
  - array order is display order; there is no `sortOrder` field.
- Validation:
  - missing or empty `questions` is allowed and means that the required standard lead form is shown
    without preliminary questionnaire steps;
  - empty question is an error;
  - unsupported question type is an error;
  - duplicate/missing question or option ID is an error;
  - question without options is an error;
  - empty option label is an error;
  - overlong final message/question/option text is a warning.
- Canonical payload and legacy read compatibility are fixed in
  `docs/lead-questionnaire-contract-2026-07-16.md`.

`lead_form`:

- Type: inherited CMS-authored global form-content section.
- Source: `global_lead_form`.
- Required.
- Page-level read-only for practice pages.
- Use the existing inheritance chain model, similar to price, to avoid a large global-dependency refactor.
- Page-level override/append is not allowed for this product pass.
- Cannot be disabled or moved separately from the lead block.
- Edited only through the global section editor.
- Global fields may include:
  - `title`;
  - `phones[]`;
  - `description`;
  - `fields[]`;
  - `submitLabel`;
  - `messengerOptions[]`;
  - consent/legal text.
- Validation lives at the global section level. Broken global form data appears on dependent pages as
  dependency diagnostics.

`lead_capture`:

- Type: runtime/read-model form context.
- Not editable.
- Not a global section.
- Provides the stable form submission/runtime contract for the public frontend.

### 17. `regional_offices`

- Type: runtime/read-model section.
- Purpose: show eligible regional office/page links before the footer on the Ukraine/base page only.
- Fixed position after the lead block and before the footer.
- National-only: present on the base/Ukraine `practice_page`; regional practice pages must not have this
  slot in the workbench/editor at all.
- Read-only in CMS.
- Fields in resolved payload:
  - `title`;
  - `accentTitle`;
  - `titleSuffix`;
  - `items[]`.
- Runtime source:
  - active/show-on-site regions;
  - current practice regional competencies;
  - only regions that also have a published regional `practice_page` for the same practice.
- Item contract:
  - region identity/localized title fields;
  - regional public path for the linked practice page.
- Validation/diagnostics:
  - empty list on the national page is a warning, not a blocker;
  - public rendering should hide the whole section when no eligible items exist.

## Implementation Notes

- Keep two different lawyer sections:
  - `practice_team_cta` is a lawyer showcase with in-section JS switching and no lawyer-page URL.
  - `practice_lawyers_block` + `practice_lawyers` is lawyer selection with links to lawyer pages.
- Do not duplicate lawyer eligibility business logic. Use one runtime resolver path where possible, with
  different output modes for showcase vs selection.
- Composite groups are a presentation/editor contract, not a requirement to collapse backend slots into
  one physical section.
- The old generic `practice_optional_text` should be retired in favor of the three fixed text variants:
  `practice_intro_text`, `practice_reviews_text`, and `practice_price_text`.

## 2026-06-28 Amendments

Use [`service-hierarchy-page-amendments-2026-06-28.md`](service-hierarchy-page-amendments-2026-06-28.md)
as the latest product contract.

### Team CTA Positions

`practice_page` should support two positions for the team CTA:

- `practice_team_cta_top` immediately after `achievements_strip`;
- existing lower `practice_team_cta` in the current lower-page position.

Both slots are optional and can be enabled/disabled. Recommended defaults:

- `practice_team_cta_top`: disabled;
- `practice_team_cta`: enabled.

If both slots are enabled, backend validation should return an error on the lower `practice_team_cta` slot.

### Team CTA Content

The old large `lead` field should be replaced by:

```json
{
  "title": "Section title",
  "paragraphs": [
    { "text": "First paragraph." }
  ]
}
```

Fallback: if `paragraphs` is absent and legacy `lead` exists, render `lead` as one paragraph.

`title` is optional. An absent or empty title does not produce an error or warning. When present, it may
still receive the standard overlength warning.

### Local Offices

Regional `practice_page` rows should expose a new read-only/runtime `local_offices` slot with real offices
in the current region. It is separate from `regional_offices`, which remains the national-only regional
alternative link section.
