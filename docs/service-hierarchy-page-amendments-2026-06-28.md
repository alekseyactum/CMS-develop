# Service Hierarchy Page Amendments - 2026-06-28

This document captures the latest product decisions for the service hierarchy page family:

- `practice_collection_page`
- `practice_page`
- `service_page`
- `problem_page`

It amends the earlier structure documents and should be used as the next implementation checklist before
changing backend schemas, runtime resolvers, workbench matrices, or frontend rendering.

## Terminology

### `regional_offices`

`regional_offices` is the existing technical slot name. Despite the name, its product meaning is not a real
office list. It is a runtime section with links to regional alternatives of the same page.

Examples:

- on `/services`, Kyiv links to `/kyiv/services`;
- on `/services/family-law`, Odesa links to `/odesa/services/family-law`;
- on `/services/family-law/alimony`, Lviv links to `/lviv/services/family-law/alimony`.

Keep the existing slot key for now to avoid broad churn, but describe it in product/frontend copy as
regional page links or regional alternatives, not as physical offices.

### `local_offices`

`local_offices` is the proposed new runtime slot for real offices in the current regional context.

It is separate from `regional_offices`.

## Practice Collection Regional Links

`practice_collection_page` must also expose the regional-links section.

### Slot

- slot key: `regional_offices`
- kind: runtime/read-only
- regional scope: `national_only`
- page types: `practice_collection_page`
- position: after `practice_collection` and before the footer

### Behavior

The base/Ukraine `/services` page should list regional alternatives for the collection page.

Each item links to the published regional collection page for the same locale:

- Kyiv -> `/kyiv/services`
- Lviv -> `/lviv/services`
- Odesa -> `/odesa/services`

Regional `/region/services` pages must not include this slot.

### Eligibility

The runtime list should include a region only when all of the following are true:

- the region is visible/show-on-site;
- the region has at least one active visible service-hierarchy competence;
- the matching regional `practice_collection_page` exists;
- the matching regional page has a current published snapshot.

If an eligible region is missing the regional page or the page is not published, keep that as an admin
warning/diagnostic in CMS. The public payload should not render a broken link.

### Matrix

The page workbench matrix should expose a `regional_offices` column for `practice_collection_page`, but only
the base/Ukraine row should have an active cell. Regional rows intentionally omit the cell.

## Regional Links For Detail Pages

The existing `regional_offices` behavior remains correct for:

- `practice_page`
- `service_page`
- `problem_page`

The section should list links to regional alternatives of the same page:

- practice page -> same practice in the region;
- service page -> same service in the region;
- problem page -> same problem route in the region.

Eligibility rules:

- `practice_page`: active regional qualification for the current practice;
- `service_page`: active regional qualification for the current service, or practice-level fallback when
  the qualification is practice-wide;
- `problem_page`: same service/practice eligibility as the parent service, because there is no separate
  problem-level competence table.

The linked regional page must exist and be published. Missing or unpublished linked pages are admin
warnings, not silent removals in CMS.

## Local Offices On Regional Detail Pages

Regional practice/service/problem pages must expose a real office list for the current region.

### Slot

- proposed slot key: `local_offices`
- kind: runtime/read-only
- regional scope: `regional_only`
- page types:
  - `practice_page`
  - `service_page`
  - `problem_page`
- position: before the footer, after the main lead block and before any footer-only layout
- not editable in the page section editor

This amendment does not require `local_offices` on `practice_collection_page`. That can be added later if
the collection design needs it.

### Runtime Source

Use `cms_ref_offices` joined to the current region from the page route:

- office `show_on_site = true`;
- office has resolved `region_id`;
- region `source_slug` matches the current page `regionSlug`;
- region is visible/show-on-site.

### Payload

Recommended payload shape:

```json
{
  "kind": "local_offices",
  "region": {
    "id": "region-id",
    "externalId": "74",
    "sourceSlug": "kyiv",
    "title": "Kyiv",
    "menuTitle": "Kyiv",
    "sourceName": "Kyiv"
  },
  "items": [
    {
      "kind": "office",
      "id": "office-id",
      "externalId": "30",
      "title": "Kyiv office",
      "sourceName": "Kyiv office",
      "address": "Localized address",
      "sourceAddress": "ERP/source address",
      "mapUrl": "https://...",
      "googlePlaceId": "..."
    }
  ]
}
```

Address priority:

```txt
cms_ref_office_translations.address ?? cms_ref_offices.source_address
```

Sorting:

```txt
sort_order, then localized/source title or address, then stable id
```

### Diagnostics

An empty `local_offices.items` list is a warning, not a publish blocker.

Public frontend should hide the section when no offices are available. CMS should still show the warning so
editors understand that the regional page has no visible office data.

## Team CTA Dual Position

Pages `practice_page`, `service_page`, and `problem_page` need two possible positions for the team CTA.

### Slots

Add a top CTA slot immediately after `achievements_strip`:

- `practice_team_cta_top`
- `service_team_cta_top`
- `problem_team_cta_top`

Keep the existing lower CTA slots:

- `practice_team_cta`
- `service_team_cta`
- `problem_team_cta`

Both positions use the same content contract and the same inheritance rules.

### Visibility

Both top and lower CTA slots must be enableable/disableable.

Recommended defaults:

- top CTA: disabled
- lower CTA: enabled

This preserves the current page layouts while allowing editors to move the CTA upward when needed.

### Validation

At most one CTA position may be enabled on the same page.

If both top and lower CTA slots are enabled, backend validation must return an error attached to the lower
CTA slot:

```txt
TEAM_CTA_DUPLICATE_POSITION
```

The message should tell the editor to disable the lower CTA when the top CTA is enabled.

Both slots disabled should be allowed unless a later page-specific design makes the CTA mandatory again.

## Team CTA Content Shape

The old `team_cta` content model has a large `lead` field. This is not precise enough for rendering
separate paragraphs.

Use a paragraph array instead.

### New Shape

```json
{
  "title": "Section title",
  "paragraphs": [
    { "text": "First paragraph." },
    { "text": "Second paragraph." }
  ]
}
```

Field rules:

- `title` is required when the section is enabled;
- `paragraphs` is required when the section is enabled;
- minimum recommended paragraphs: 1;
- target maximum paragraphs: 4;
- more than 4 paragraphs should produce a warning, not an error, until the final frontend layout proves it
  must be strict;
- empty `paragraphs[].text` is an error;
- overlong title or paragraph text is a warning.

### Backward Compatibility

Backend and frontend should temporarily support old content:

```json
{ "title": "...", "lead": "..." }
```

If `paragraphs` is absent and `lead` exists, render `lead` as one paragraph. New frontend saves should send
`paragraphs`, not `lead`.

## Implementation Checklist

Backend:

- add `regional_offices` to `practice_collection_page` as `national_only`;
- extend `resolveRegionalOffices()` for `practice_collection_page`;
- add `local_offices` runtime slot for regional detail pages;
- add a resolver for local regional offices;
- add top team CTA slots and make lower team CTA slots disableable where needed;
- add page-level validation for duplicate CTA positions;
- migrate team CTA content schema from `lead` to `paragraphs[]` with fallback support.

Frontend:

- render `regional_offices` as regional alternatives, not as physical offices;
- show the `regional_offices` column for the practice collection base row;
- render `local_offices` only on regional detail pages;
- render top/lower CTA slots independently, but surface duplicate-position errors clearly;
- edit `paragraphs[]` for all team CTA slots and support old `lead` content until migration is complete.
