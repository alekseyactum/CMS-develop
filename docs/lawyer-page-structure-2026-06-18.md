# Lawyer Page Structure

This document fixes the agreed target structure for `lawyer_page`.

## Current Amendment — 2026-10-11: Related-Section Headings

The lawyer's CMS profile may override the headings of its three runtime lists independently per locale:

- `casesSectionTitle`: for example, `Справи Маргарити`;
- `publicationsSectionTitle`: for example, `Публікації Маргарити`;
- `reviewsSectionTitle`: for example, `Відгуки про Маргариту`.

Store complete plain-text headings, not a name in a grammatical case. No automatic declension or
cross-locale copying is introduced. Optional fields accept trimmed strings up to 255 characters or null;
blank clears the override, omission preserves it. Missing values use
generic localized fallbacks: UK `Справи` / `Публікації` / `Відгуки`, RU `Дела` / `Публикации` / `Отзывы`,
EN `Cases` / `Publications` / `Reviews`. The lawyer cases heading deliberately omits "successful".

An empty/whitespace-only heading produces `LAWYER_SECTION_TITLE_MISSING` with severity `warning`
only when that localized runtime list has eligible items and the lawyer is visible. No warning is
needed for an empty/hidden section. The fallback remains usable; saving and publishing are not blocked.
This applies independently to all three headings and each locale, even if its translation row is absent.
ERP profile/list/menu diagnostics cover all locales; page matrix, runtime inspection and page-menu
diagnostics cover only the requested locale. These checks use current source data for the next rendering,
not an already published snapshot. No page publication is required before reporting the warning.
This rule supersedes the original baseline's empty-related-list warning: empty lists are valid and hidden.

The runtime lists remain read-only at page level: relations, filters, ordering and empty-section hiding
are unchanged. This supersedes the baseline's system-only-title rule, not its runtime ownership model.
Frontend renders the existing section `title`; CMS edits the three fields in the localized lawyer profile.
ERP must not overwrite them. Title-only changes participate in stale detection; existing snapshots stay
immutable until the normal publication/rebuild. Three additive nullable translation columns are required;
no backfill, live migration, deploy or rebuild is authorized by this specification update alone.

### Current year-only period contract

The later approved decisions supersede the October 6 free-text/month and single-year descriptions below.
New structured `experienceItems` and `additionalEducationItems` use the same three explicit facts:
`startYear`, `endYear`, `isOngoing`. Months are not supported. With `isOngoing=false`, a null end year is
a single year and a non-null end year is a closed range; ongoing items require a null end year. Years
must be integers no later than the current UTC year, and an end cannot precede the start. A null start
is a savable incomplete draft that blocks publication of that nonempty item.

Ukrainian items own stable IDs, order and period facts; translations own descriptions and inherit those
facts. `periodLabel` is derived per locale, never parsed back into dates. Additional-education structured
reads also expose deprecated `year=startYear` for compatibility. Existing label-only experience and
year-only additional education stay supported until explicitly converted; no automatic backfill or
structured-to-legacy downgrade is allowed. These period changes use the existing JSON columns, not a
new migration. They do not change formal `educationItems` or the separate `legalPracticeStartYear`.

## Prior Amendment — 2026-10-06

The updated lawyer layout extends the existing profile model with three CMS-owned fields:

- `legalPracticeStartYear`: nullable integer year (not a date), common to all locales and editable in CMS.
  ERP must not overwrite it. The site derives calendar years of practice at rendering time; the published
  payload must not freeze a precomputed number of years. Unknown means hide the seniority line, not zero.
- `experienceItems[]`: stable `experienceItemId`, localized `periodLabel`, rich description; Ukrainian
  items own the fact set and ordering, other locales translate the same IDs. Free-text periods support
  year-only, month/year and ongoing work without inventing precise dates.
- `additionalEducationItems[]`: stable `additionalEducationItemId`, shared integer `year`, localized rich
  description; separate from formal education/degree data and its search markup.

The certificate is already sufficient for the layout and is not changed. Main `educationItems`, photos,
names, role, summary, practices, cases, publications, reviews and licensing-partnership flag retain their
existing meaning. Booking/calendar remains a separate feature, not a new biography field.

New fields are optional: empty lists or an unknown start year do not block publication. Incomplete
nonempty items are diagnosed and cannot be published as valid cards. Stable IDs, cross-locale consistency,
year validity and order are enforced by the backend. The year must be an integer from 1 through the current
UTC year. With only a year known, seniority is a calendar difference, not exact completed anniversaries.

Legacy `experienceText` is retained. For each locale, null `experienceItems` uses legacy prose; an explicit
empty array clears the visible experience without resurrecting old prose; nonempty items replace prose.
The old text stays in storage. Configuring one locale must not silently erase another locale's legacy
biography. No automatic prose-to-timeline conversion or bulk content rewrite is authorized.

Storage is additive: `legal_practice_start_year` in `cms_ref_lawyers` and nullable JSON columns
`experience_items_json` / `additional_education_items_json` in `cms_ref_lawyer_translations`.
Existing reference admin endpoints, metadata, diagnostics and the runtime `lawyer_profile` payload are
extended; these are still not editable page-section drafts. Dependent pages use the normal stale and
publication workflow. Current backend details and request/response examples are maintained in
`cms-back/docs/lawyer-page-runtime-backend.md`.

The earlier sections below preserve the original June decision and rationale. Their statements that the
profile expansion is not yet implemented, and their narrative-only experience model, are historical;
this amendment and the current backend contract supersede them. In particular, no generic lead-form
substitution for the separately planned appointment calendar is introduced by this work.

## Original Baseline — 2026-06-18

At the time of this baseline, the backend exposed only a minimal `seo` + runtime `lawyer_profile` slice.

## Page Rules

- `lawyer_page` is a generated page from a lawyer reference-data object.
- Public route: `/lawyers/:lawyerSlug`.
- Regional variants do not exist.
- Localized versions are required for `uk`, `ru`, and `en`.
- Slots are fixed and not movable.
- Header, footer, breadcrumbs, footer-practices block, and site footer are outside the editable page schema.
- The page should stay mostly profile-driven / runtime-driven. Do not turn it into a stack of loosely
  authored CMS narrative sections.
- The hero CTA should lead to the common lead form block on the same page. There is no separate
  booking/schedule section in the first slice.

## Slots

1. `seo`
   - Required metadata section.
   - Page-owned editable content.
   - Per-locale.
   - Fields: `title`, `description`, optional `ogImage`.
   - Canonical is backend-owned and self-canonical.
   - Default title/description may be seeded from the lawyer name, but remain editable in CMS.

2. `lawyer_profile`
   - Required runtime/profile section.
   - Read-only at page level.
   - Fixed at the top of the page after breadcrumbs.
   - This is one structured profile block, not several independent page sections.
   - Source: lawyer reference data, localized lawyer profile fields, and lawyer qualifications.
   - The section should contain:
     - `photoMediaId` required;
     - `fullName` required;
     - `roleLabel` required, with initial seeded defaults `Адвокат` / `Адвокат` / `Lawyer`;
     - `licenseNumber` expected; empty value is a warning for now;
     - `practices[]` runtime list from active lawyer qualifications with `score > 1`;
     - `professionalSummary` required;
     - `educationItems[]` optional list;
     - `experienceText` optional.
   - The profile must not expose a separate public contacts block. The visible small factual field under the
     hero is the lawyer license / certificate number, not office contact data.
   - `practices[]` item contract:
     - practice identity;
     - localized display title;
     - public path of the related `practice_page`, when available.
   - `educationItems[]` item fields:
     - `educationItemId` required, CMS-generated, stable, locale-neutral, and read-only;
     - `institution` required;
     - `degree` optional;
     - `specialization` optional;
     - `periodLabel` optional;
     - `note` optional.
   - `Education` / `Experience` headings are system-localized labels, not editor-owned page fields.
   - CTA inside the hero/profile block is system-owned and targets the common lead form block below.

3. `lawyer_cases`
   - Runtime/read-model section.
   - Optional visible block, default enabled.
   - Read-only in CMS.
   - Title is system-defined/read-only.
   - Source: successful cases linked to the current lawyer.
   - Empty list is a warning, not a publish blocker; public frontend may hide the block when empty.

4. `lawyer_publications`
   - Runtime/read-model section.
   - Optional visible block, default enabled.
   - Read-only in CMS.
   - Title is system-defined/read-only.
   - Source: publications linked to the current lawyer.
   - Empty list is a warning, not a publish blocker; public frontend may hide the block when empty.

5. `lawyer_reviews`
   - Runtime/read-model section.
   - Optional visible block, default enabled.
   - Read-only in CMS.
   - Title is system-defined/read-only.
   - Source: reviews linked to the current lawyer.
   - Empty list is a warning, not a publish blocker; public frontend may hide the block when empty.

6. `lead_form` + `lead_capture`
   - Composite visual block at the bottom of the page.
   - Required.
   - Fixed after reviews.
   - `lead_form` is the common inherited/global form-content section.
   - `lead_capture` is runtime form context.
   - There is no dedicated `lawyer_booking` section in the first slice.
   - There is no page-specific `lead_questionnaire` in the first slice unless a later product decision
     introduces one explicitly.

## Recommended Universal Profile Model

The lawyer page should use one universal profile model instead of trying to support arbitrary biography
layouts per lawyer.

Recommended structure:

1. Hero identity
   - photo;
   - full name;
   - short role label;
   - license/certificate number;
   - CTA to the common lead form.

2. Core professional summary
   - one required localized summary field that answers who this lawyer is professionally and what kind of
     work they do;
   - this is the main replacement for the current vague "big biography paragraph" approach.

3. Education
   - optional structured list;
   - each item may be short and factual instead of forcing a long narrative.

4. Experience
   - optional localized narrative field;
   - used only when a lawyer really has a meaningful experience story to show.

5. Practices
   - runtime list from lawyer qualifications;
   - kept out of manual editing so it always matches the service hierarchy logic.

Why this shape:

- it is stable across all lawyers;
- it avoids weak filler text when a full biography does not exist;
- it gives the frontend a predictable layout;
- it keeps factual data factual and narrative data optional;
- it reduces the risk of turning each lawyer page into a custom editorial project.

## Ownership And Editor Flow

`lawyer_page` itself should stay mostly read-only from the page-editor perspective.

- `seo` is edited in page authoring.
- `lawyer_profile` is rendered on the page as runtime data.
- The actual editable source of `lawyer_profile` belongs to lawyer reference data, not to page section
  drafts.

Expected ownership split:

- lawyer base record:
  - `showOnSite` read-only ERP/source flag;
  - `slug` CMS-generated read-only stable slug;
  - `photoMediaId` CMS-owned editable field;
  - `sortOrder` CMS-owned editable field;
  - `licenseNumber` ERP/source-owned read-only field.

- lawyer localized profile fields:
  - `publicName` required;
  - `roleLabel` required, seeded by default;
  - `professionalSummary` required;
  - `educationItems[]` optional;
  - `experienceText` optional.

- lawyer qualifications:
  - read-only ERP/source-owned runtime source for `practices[]`.

Frontend consequence:

- opening `lawyer_profile` from page authoring should be treated as a read-only runtime/profile screen;
- when the editor needs to change profile data, the UI should navigate to or embed the lawyer
  reference-data editor rather than creating page section drafts.

## Target `reference_data/lawyers` Contract

To make `lawyer_profile` real and stable, the lawyer reference-data resource should become the editing
surface for the public lawyer profile.

Target contract:

- `sourceFields` (ERP-owned, read-only):
  - `sourceName`;
  - `licenseNumber` (today it is stored as `license`);
  - `showOnSite` stays top-level resource state and is also read-only from CMS editing.

- `cmsFields` (CMS-owned):
  - `slug` read-only generated stable public slug;
  - `photoMediaId` editable;
  - `sortOrder` editable.

- `relationFields` / `relations` (read-only helper data):
  - `regionId`, `officeId`, external ids, and readable linked region/office objects;
  - useful for diagnostics and internal orientation, but not a public contacts block.

- `translations[locale]` (editable localized public profile fields):
  - `publicName` required;
  - `roleLabel` required;
  - `professionalSummary` required;
  - `educationItems` optional list;
  - `experienceText` optional.

Recommended translation payload shape:

```json
{
  "uk": {
    "publicName": "Харченко Оксана Олексіївна",
    "roleLabel": "Адвокат",
    "professionalSummary": "Фахівчиня з ...",
    "educationItems": [
      {
        "educationItemId": "4bb28c7e-0000-4000-8000-000000000001",
        "institution": "КНУ ім. Тараса Шевченка",
        "degree": "магістр",
        "specialization": "міжнародне право",
        "periodLabel": null,
        "note": null
      }
    ],
    "experienceText": "Працює з ..."
  }
}
```

`educationItems` should stay editor-owned but structured. Do not hide it inside one long rich-text field.
Every real education fact has one backend-generated `educationItemId` shared by all locale translations.
The primary Ukrainian profile owns the shared item set and ordering. Other locales translate the fields of
those items and cannot independently create, remove, or re-key education facts. Array position and
localized text never define education-item identity.

## Target API/Storage Direction

The current lawyer translation model is too small for the agreed page.

Current state:

- `cms_ref_lawyer_translations.public_name`
- `cms_ref_lawyer_translations.description`

Target direction:

- keep `public_name`;
- add `role_label`;
- add `professional_summary`;
- add `education_items_json`;
- add `experience_text`.

Recommended storage choices:

- `role_label`: short text column;
- `professional_summary`: text column;
- `education_items_json`: JSON column or text-JSON column;
- `experience_text`: text column.

This is a better fit than overloading one generic `description` field because:

- summary, education, and experience have different meaning;
- education is repeatable structured data, not just prose;
- the frontend can render a stable layout without parsing ad hoc text conventions.

## Target Runtime Payload For `lawyer_profile`

After backend expansion, the runtime payload should move closer to this shape:

```json
{
  "kind": "lawyer_profile",
  "id": "lawyer-1",
  "externalId": "501",
  "slug": "olena-lawyer",
  "photoMediaId": "media-1",
  "fullName": "Харченко Оксана Олексіївна",
  "roleLabel": "Адвокат",
  "licenseNumber": "AA 123456",
  "professionalSummary": [
    { "type": "paragraph", "children": [{ "text": "Фахівчиня з ..." }] }
  ],
  "educationItems": [
    {
      "educationItemId": "4bb28c7e-0000-4000-8000-000000000001",
      "institution": "КНУ ім. Тараса Шевченка",
      "degree": "магістр",
      "specialization": "міжнародне право",
      "periodLabel": null,
      "note": null
    }
  ],
  "experienceText": [
    { "type": "paragraph", "children": [{ "text": "Працює з ..." }] }
  ],
  "practices": []
}
```

Important corrections compared with the current minimal payload:

- `roleLabel` must stop reusing the license field;
- `licenseNumber` should be a separate factual field;
- `contacts` should disappear from the public profile payload;
- region/office may remain internal helper data in reference-data APIs, but not as the main public profile
  presentation model.

## Validation And Publish Expectations

For visible lawyers and generated `lawyer_page` rows:

- missing `slug` is an error;
- missing `photoMediaId` is at least a warning;
- missing `publicName` in any required locale is an error;
- missing `roleLabel` in any required locale is an error;
- missing `professionalSummary` in any required locale is an error;
- empty `educationItems` is allowed;
- a missing, duplicated, unknown, or locale-mismatched `educationItemId` is an error;
- every translated education item must use the shared item set and must have a non-empty localized
  `institution` value;
- empty `experienceText` is allowed;
- empty `licenseNumber` is a warning for now;
- overlong `publicName`, `roleLabel`, summary, experience, or education item text should produce warnings.

Because lawyer pages are multilingual, the expected direction is full `uk` / `ru` / `en` translation
coverage for visible lawyers. A visible lawyer with missing public profile translations should be treated as
not ready for a clean public profile page.

## Recommended Backend Implementation Slice

When this work starts in `cms-back`, the least confusing sequence is:

1. extend `cms_ref_lawyer_translations` with the new public profile fields;
2. extend reference-data meta for `lawyers` so the new translation fields are visible/editable in admin API;
3. add validation/diagnostics for the new required fields;
4. update the runtime resolver for `lawyer_profile`;
5. only after that expand `lawyer_page` schema/workbench/editor surfaces for cases/publications/reviews if
   needed.

This keeps the source of truth correct first, and only then expands the page runtime that depends on it.

## Backend Gap To Current Implementation

Current implementation is still narrower than this target:

- `cms_ref_lawyer_translations` currently stores only `public_name` and `description`;
- runtime `lawyer_profile` currently returns `role`, `bio`, and `contacts`, where `role` is effectively the
  license value and `contacts` still expose region/office helper data;
- there is no first-class structured storage yet for `roleLabel`, `professionalSummary`, `educationItems`,
  and `experienceText`.

So the future backend expansion should move in this direction:

- stop treating license as the visual role label;
- stop modeling the public lawyer block around contacts;
- either repurpose `description` into `professionalSummary` plus add new structured fields, or add a richer
  localized profile payload for lawyers;
- keep the result in lawyer reference data, not in page section drafts.

## Validation Notes

- Missing `photoMediaId` on `lawyer_profile` should be treated as a warning or error depending on final media
  policy; target direction is to avoid publishing visibly broken lawyer pages.
- Empty `fullName` or `professionalSummary` is an error.
- Empty `educationItems[]` is allowed.
- Empty `experienceText` is allowed.
- Long `professionalSummary`, `experienceText`, and education item fields should produce warnings.
- Empty runtime lists for `lawyer_cases`, `lawyer_publications`, and `lawyer_reviews` should not block
  publish in the first slice.

## Frontend Notes

- Render `lawyer_profile` as one universal profile block. Do not split it into extra editable page sections
  such as separate CMS-managed `biography`, `education`, or `experience` sections.
- The page should stay visually rich but structurally predictable across all lawyers.
- System-owned block titles for cases/publications/reviews should remain stable and localized.
- The hero CTA should scroll or jump to the common lead form block on the same page.
