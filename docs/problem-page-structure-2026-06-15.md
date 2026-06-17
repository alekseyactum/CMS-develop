# Problem Page Structure

This document fixes the agreed first backend/editor structure for `problem_page`.

Status on 2026-06-15: implemented in `cms-back` schema/runtime as the first usable problem-page workbench
slice. Public visual rendering is still a frontend task.

## Page Rules

- `problem_page` is a generated service-hierarchy page:
  `/services/:practiceSlug/:serviceSlug/:problemSlug`.
- Base pages own the editable content. Regional pages inherit editable content from the base by default.
- Regional section headings are locked: regional editors can review/publish inherited changes, but they
  cannot override section headings such as `title` and `accentTitle`.
- Slots are fixed and not movable.
- Header, footer, breadcrumbs, and route/context navigation are outside the editable page schema.

## Slots

1. `seo`
   - Required metadata.
   - Regional inheritance from base.

2. `problem_intro`
   - Required hero/content section.
   - Fields: `title`, optional `accentTitle`, optional `lead`, optional `ctaLabel`, optional `ctaTarget`.
   - `title` and `accentTitle` are locked on regional pages.

3. `achievements_strip`
   - Required global inherited achievements strip.

4. `problem_must_do`
   - Required advisory list.
   - Fields: `title`, optional `accentTitle`, optional `lead`, optional `variant`, required `items`.
   - Default `variant`: `card_grid`.

5. `problem_accent_text_1`
   - Optional, default enabled.
   - Fields: optional `title`, optional `lead`.

6. `problem_must_not_do`
   - Optional, default enabled.
   - Same fields as `problem_must_do`.

7. `problem_accent_text_2`
   - Optional, default enabled.
   - Fields: optional `title`, optional `lead`.

8. `problem_lawyer_actions`
   - Optional, default enabled.
   - Same fields as `problem_must_do`.

9. `problem_team_cta`
   - Optional, default enabled.
   - Editable text block for the team/support CTA.
   - Fields: `title`, optional `lead`.

10. `problem_cases`
    - Runtime/read-model slot.
    - Currently returns a route-aware empty list until the cases read model is ready.

11. `problem_reviews_block` + `problem_reviews`
    - Composite group: `problem_reviews`.
    - `problem_reviews_block` stores editable title/lead.
    - `problem_reviews` is runtime/read-model data.
    - First-pass filter: current service + region, not problem id.

12. `price`
    - Inherited `global_price` page-level section.

13. `problem_faq`
    - Optional, default enabled.
    - Fields: `title`, optional `items`.

14. `problem_lawyers_block` + `problem_lawyers`
    - Composite group: `problem_lawyers`.
    - Editable title/lead plus runtime lawyer list.
    - Lawyer runtime uses the current practice/service/problem route context and existing qualification
      rules.

15. `lead_questionnaire` + `lead_form` + `lead_capture`
    - Composite group: `lead_block`.
    - `lead_questionnaire` is optional and disabled by default.
    - `lead_form` inherits from `global_lead_form`.
    - `lead_capture` is runtime form context.

16. `regional_offices`
    - Runtime/read-model section.
    - Fixed after the lead block and before the footer.
    - National-only: only the Ukraine/base `problem_page` has this slot; regional problem pages do not.
    - Read-only in CMS.
    - Resolved payload fields: `title`, `accentTitle`, `titleSuffix`, `items`.
    - Items are eligible regions with:
      - active/show-on-site region visibility;
      - active regional qualification for the current service, or practice-level fallback where service
        qualification is absent;
      - a published regional `problem_page` for the same route.
    - Empty list is a warning on the national page, not a publish blocker.
    - Public rendering should hide the whole section when no eligible items exist.

## Validation Notes

- Empty enabled advisory `items` lists are validation errors.
- Advisory item count target is 2-8; outside this range is a warning.
- Long section titles, leads, item titles, and item descriptions produce warnings.
- `problem_cases` may be empty for now by design.

## Frontend Notes

- Render `compositeGroupKey` groups as one visual block where the design treats them as one section.
- Keep saving/validation actions scoped to the primary editable section in the editor response.
- Use runtime members from `compositeGroup.members[]`; do not write runtime payloads into editable
  section content.
- Do not open raw runtime cells directly. `problem_cases`, `problem_reviews`, `problem_lawyers`, and
  `lead_capture`, and `regional_offices` expose `endpoints.editor: null` and `actions.canOpen: false`;
  runtime members inside composite visual sections are inspected through the primary editable section editor.
- Supported advisory `variant` names for this slice:
  - `card_grid` - default card/grid style from the current design;
  - `compact_grid` - reserved frontend variant;
  - `step_list` - reserved frontend variant.
