# Service Page Structure

This document fixes the agreed first backend/editor structure for `service_page`.

Status on 2026-06-16: implemented in `cms-back` as the first usable service-page workbench/editor slice.
Public visual rendering is still a frontend task.

## Page Rules

- `service_page` is a generated service-hierarchy page:
  `/services/:practiceSlug/:serviceSlug`.
- Base pages own the editable content. Regional pages inherit editable content from the base by default.
- Regional section headings are locked: regional editors can review/publish inherited changes, but they
  cannot override section headings such as `title` and `accentTitle`.
- Slots are fixed and not movable.
- Header, footer, breadcrumbs, and route/context navigation are outside the editable page schema.
- Runtime/read-model slots are read-only for the editor and are opened through a composite editable sister
  section when the UI treats them as one visual block.

## Slots

1. `seo`
   - Required metadata.
   - Regional inheritance from base.

2. `service_intro`
   - Required hero/content section.
   - Fields: `title`, optional `accentTitle`, optional `lead`, optional `ctaLabel`, optional `ctaTarget`.
   - `title` and `accentTitle` are locked on regional pages.

3. `achievements_strip`
   - Required global inherited achievements strip.

4. `service_problems_block` + `service_problems`
   - Composite group: `service_problems`.
   - Required.
   - `service_problems_block` stores editable title/lead.
   - `service_problems` is runtime/read-model data for current service problems.
   - First-pass runtime filter: current service only, `show_on_site = true`.
   - Problems may exist without a published `problem_page`; such rows stay visible in admin payloads with
     warnings and must render as disabled/non-link items publicly.
   - Empty runtime list is a publish-blocking error.

5. `service_accent_text_1`
   - Optional, default enabled.
   - Fields: optional `title`, optional `lead`.

6. `service_lawyer_actions`
   - Optional, default enabled.
   - Advisory structured section.
   - Fields: `title`, optional `accentTitle`, optional `lead`, optional `variant`, required `items`.
   - Default `variant`: `card_grid`.

7. `service_accent_text_2`
   - Optional, default enabled.
   - Fields: optional `title`, optional `lead`.

8. `service_must_not_do`
   - Optional, default enabled.
   - Same field contract as `service_lawyer_actions`.

9. `service_accent_text_3`
   - Optional, default enabled.
   - Fields: optional `title`, optional `lead`.

10. `service_must_do`
    - Optional, default enabled.
    - Same field contract as `service_lawyer_actions`.

11. `service_team_cta`
    - Optional, default enabled.
    - Editable text block for the team/support CTA.
    - Fields: `title`, optional `lead`.

12. `service_cases`
    - Runtime/read-model slot.
    - Currently returns a route-aware empty list until the cases read model is ready.
    - Empty list is allowed for now and should surface as a warning, not a blocker.

13. `service_reviews_block` + `service_reviews`
    - Composite group: `service_reviews`.
    - Required.
    - `service_reviews_block` stores editable title/lead.
    - `service_reviews` is runtime/read-model data.
    - First-pass runtime filter: current service + region.

14. `price`
    - Inherited `global_price` page-level section.

15. `service_price_text`
    - Optional text section near prices.
    - Disabled by default.
    - Fields: optional `title`, optional `lead`.

16. `service_faq`
    - Optional, default enabled.
    - Fields: `title`, optional `items`.

17. `service_lawyers_block` + `service_lawyers`
    - Composite group: `service_lawyers`.
    - Required.
    - Editable title/lead plus runtime lawyer list.
    - Public cards link to lawyer profile pages.
    - Lawyer runtime uses current practice + service + region context and existing qualification rules.
    - Competence threshold remains `score > 1`.

18. `lead_questionnaire` + `lead_form` + `lead_capture`
    - Composite group: `lead_block`.
    - `lead_questionnaire` is optional and disabled by default.
    - `lead_form` inherits from `global_lead_form`.
    - `lead_capture` is runtime form context.

19. `regional_offices`
    - Runtime/read-model section.
    - Fixed after the lead block and before the footer.
    - National-only: only the Ukraine/base `service_page` has this slot; regional service pages do not.
    - Read-only in CMS.
    - Resolved payload fields: `title`, `accentTitle`, `titleSuffix`, `items`.
    - Items are eligible regions with:
      - active/show-on-site region visibility;
      - active regional qualification for the current service, or practice-level fallback where service
        qualification is absent;
      - a published regional `service_page` for the same service route.
    - Empty list is a warning on the national page, not a publish blocker.
    - Public rendering should hide the whole section when no eligible items exist.

## Validation Notes

- Empty enabled advisory `items` lists are validation errors.
- Advisory item count target is 2-8; outside this range is a warning.
- Long section titles, accent titles, leads, item titles, and item descriptions produce warnings.
- `service_problems` empty list is a blocker.
- `service_cases` may be empty for now by design.

## Frontend Notes

- Render backend slots sharing `compositeGroupKey` as one visual block where the page design treats them as
  one section.
- Keep save/validate/publish actions scoped to the primary editable section returned by the editor wrapper.
- Use runtime members from `compositeGroup.members[]`; do not write runtime payloads into editable section
  content.
- Do not open raw runtime cells directly. `service_problems`, `service_cases`, `service_reviews`,
  `service_lawyers`, `lead_capture`, and `regional_offices` expose read-only/runtime behavior.
- Supported advisory `variant` names for this slice:
  - `card_grid` - default card/grid style from the current design;
  - `compact_grid` - reserved frontend variant;
  - `step_list` - reserved frontend variant.
