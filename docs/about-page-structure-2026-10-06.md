# About Page Structure and Implementation Specification

Date: 2026-10-06. Authoritative scope correction: 2026-10-17.

This is the agreed product scope for `about_page`, with implementation rules for `cms-back`,
`cms-front`, and `site-front`. It covers the national-only page in all three locales,
authoring, runtime data, and acceptance. Recording this specification does not implement the page,
create content, publish pages, or authorize deployment.

The 2026-10-17 correction supersedes the earlier 2026-10-06 decision to support regional About
variants, regional inheritance/locks, and regional office/lawyer filtering. That earlier decision is
historical, not an alternative supported contract. `about_page` has only `/about`, `/ru/about`, and
`/en/about`, in one shared national locale group. All other section, form, runtime dependency,
versioning, and publication contracts remain intact.

The supplied existing release audit records one national `uk` draft page,
`e3338050-745a-4162-a46b-af4d15729094`, no created regional About pages, and `ru`/`en` placeholders
only, not created translations. No database schema migration, content publication, or data deletion
is needed for this correction. This documentation update does not re-audit cloud state or claim that
the correction has been deployed.

The subsequent develop audit on 2026-10-17 found one historical regional `/donetsk/about` page with
saved section versions and an active snapshot, despite `draft` on the page record. The corrected
contract excludes that obsolete regional identity from operational About pages and public routes.
Preserve its database records and history; this change neither deletes them nor overwrites national
content. A page record's status alone does not establish whether a published snapshot exists.

The page introduces Actum as a company across all practices. It is not a family-law landing page.
The approved sequence is: introduction, company statement, history, founders, offices, cases,
lawyers, media publications, and the ordinary inherited global application form.

## 1. Approved Product Decisions

| Area | Decision |
| --- | --- |
| Page variants | National only; `uk`, `ru`, and `en` in one shared national locale group; no regional pages |
| Animated hero | Backend supplies an automatically selected runtime array of enabled lawyers with usable portraits; no manual selection |
| Hero geography | The entire eligible Actum team across Ukraine; no regional filtering |
| Hero ordering | Randomized ordering at assembly; no need for a different order on every browser refresh |
| Company history | Own editable content per locale; editor-managed events and order; no fixed product count |
| Founders | Own editable content per locale; exactly two people, displayed vertically one after the other, not a carousel |
| Office map | Existing ERP offices; selecting a list item centers the map; opening Google Maps is a separate action |
| Case, lawyer, and media showcases | Existing `auto` / `manual` selection principle; settings belong to About, not Home |
| Media showcase | Media publications only, not a mixed blog/media list |
| Office and lawyer geography | Eligible offices and lawyers across Ukraine; no regional filtering in runtime or selection pickers |
| Case and media selections | Page-owned localized About configuration; no regional inheritance or overrides |
| Contact form | Existing `global_lead_form` without page-owned fields; national page context has no selected region |

2026-10-06 clarification: the contact block is the ordinary `lead_form` inherited from
`global_lead_form`, together with the existing `lead_capture` context. There is no About-owned form,
field schema, submit label, or form editor. The global form contract owns its fields and presentation.

The remaining field names, limits, validation rules, and empty states below are implementation defaults
chosen to fit existing CMS conventions. They are not claims that these API fields already exist.
The initial carousel limit is 8, matching the existing Home showcase limit. This limit does not apply
to the hero's full lawyer pool, history, or offices.

## 2. Routes and Page Identity

| Locale | National route |
| --- | --- |
| `uk` | `/about` |
| `ru` | `/ru/about` |
| `en` | `/en/about` |

- Use `about_page` as the page type and `about` as the fixed page path.
- Enforce one national authoring page per locale, with no region context. All three locale members
  belong to one shared national locale group; a placeholder is not a created authoring page.
- Regional About routes and pages are unsupported. Reject regional creation/repair and route requests;
  do not generate regional candidates or silently reinterpret a regional request as national.
- Do not derive About availability from practice qualifications or require practice pages to exist first.
- Language switching stays within the shared national locale group. Public alternate links include
  only its published translations, never placeholders or drafts.
- Canonical paths use the resolved national locale path. Host selection follows the project's existing
  runtime configuration, not a new hardcoded host in this feature.
- Draft pages and missing locale placeholders are not public routes. Do not mass-create or
  publish pages when a developer registers the schema or an editor opens the workbench.
- Add normal catalog, workbench, navigation, preview, redirects, and published sitemap support.
  Listing a missing national locale placeholder is distinct from creating its authoring page.

Header, footer, and route/language navigation remain layout responsibilities, outside editable About
sections. Existing global About menu links are not permission to generate or publish missing pages.
Do not change global header routing semantics as an accidental part of this implementation.

## 3. Fixed Section Schema

The visual order is fixed. There is no arbitrary page builder, section insertion, or drag-and-drop
reordering of page sections. History events and manual showcase items have their own editable order.

The names below are target slot keys. Metadata does not count as a visible section. Slots sharing a
`compositeGroupKey` render as one visual section; they must not appear twice on the public page.

| Order | Target slots | Composite group | Authored content and runtime responsibility |
| --- | --- | --- | --- |
| Metadata | `seo` | None | Existing page SEO fields; canonical path is backend-owned |
| 1 | `about_intro`, `about_hero_lawyers` | `about_hero` | Localized H1/subtitle and runtime animation portraits |
| 2 | `about_statement` | None | Company statement with rich-text emphasis |
| 3 | `about_history` | None | Heading, lead, ordered milestones |
| 4 | `about_founders` | None | Exactly two founder records; two vertical bands |
| 5 | `about_offices_intro`, `about_offices` | `about_offices` | Introductory text plus read-only office/map data |
| 6 | `about_cases_intro`, `about_cases` | `about_cases` | Intro/selection config plus published case cards |
| 7 | `about_lawyers_intro`, `about_lawyers` | `about_lawyers` | Intro/selection config plus eligible lawyer cards |
| 8 | `about_media_intro`, `about_media` | `about_media` | Intro/selection config plus published media cards |
| 9 | `lead_form`, `lead_capture` | `about_lead` | Inherit-only global lead form plus existing runtime submission context |

All nine sections are part of the initial fixed design and enabled. Do not add editor visibility toggles
in the first implementation. A runtime list can be empty without removing its slot from the schema;
public empty-state rules below determine which visual parts remain visible.

Do not add Home's achievements, FAQ, prices, qualification questionnaire, or organization-profile editor
to this page simply because existing resolvers contain them.

## 4. National Content Ownership and Global Inheritance

There is no regional About base/override composition, regional inheritance, or regional field/heading
lock. The shared national locale group links translations; it does not make one locale the authoring
source for another. There is no cross-language authoring fallback or About-specific global registry.

SEO, H1/tagline, company statement, history, both founders, office introductory text, and showcase
headings, lead text, CTAs and selection configuration are own editable content of each national locale
page. History and founders are not inherit-only. Selection mode and selected IDs remain one coherent
page-owned configuration; no regional override or append strategy is needed.

Runtime portraits, offices and cards remain read-only and resolve across Ukraine using the eligibility
rules below. Removing regional locks from About must not weaken locks or inheritance on
practice/service/problem pages or other page types.

`lead_form` remains inherit-only from the ordinary `global_lead_form` in the requested locale, with no
page-owned override. `lead_capture` resolves the actual national page and locale with no selected page
region. Existing global-form, media, runtime source and snapshot dependencies remain required.

Edits participate in existing dependency/staleness and page publication flows. Saving a draft does not
silently change a published snapshot. Rebuilding or publishing resolves approved dependencies through
the backend. Missing required inherited global content remains an actionable blocker, not an empty
successful section or a silent language substitution.

## 5. Section Fields and Behavior

### 5.1 SEO

Reuse existing `seo` fields: required `title` and `description`, optional `ogImage`, and backend-owned
canonical resolution. Text is own editable content per locale. Do not expose a free-form canonical
editor that can point a locale page at the wrong route.

Existing structured-data support for `about_page` is not an authoring implementation. Reuse its AboutPage
and global organization references; validate output against the assembled page. Do not create a second
organization entity or import Home's organization-profile section into About.

### 5.2 Animated Hero

Editable `about_intro` fields:

- `title`: required localized page H1.
- `tagline`: optional localized subtitle.

`about_hero_lawyers` is read-only runtime data:

- Include all `show_on_site = true` lawyers with a nonempty display name and a usable public portrait.
- Do not apply competence scores, practice membership, a top-five ranking, or a region restriction.
- Use canonical lawyer IDs and the existing media-serving boundary. Return only public display data,
  not full ERP records, contacts, qualification internals, or authentication material.
- The minimal card contains `id`, `displayName`, and the resolved portrait reference/URL. Its exact wire
  names should follow the shared public media/card DTO where compatible.
- Portraits are animation elements, not profile links in the initial implementation. An unpublished or
  absent profile is therefore not a reason to omit an otherwise eligible portrait.
- Missing/unavailable photos or names cause omission with admin diagnostics, not blank animation cards.
- The array contains the whole eligible pool. Eight visible portrait positions in the mockup are a
  frontend layout decision, not a backend selection limit. With fewer portraits, use fewer positions
  rather than inventing duplicate people; with none, preserve the H1 and static brand composition.

Randomization is limited to this slot. Shuffle the resolved array in application code during assembly;
do not issue per-lawyer requests or add random full-table sorting to the database query. The same
assembled result and its retries must preserve one order. Do not shuffle independently during SSR
and hydration.

The current public API serves stored page snapshots. A public read or cache miss must not be treated
as permission to regenerate the array or modify a snapshot. Initially, a new preview/authorized page
snapshot build may choose a new permutation; repeated reads of that snapshot keep it. Source changes
must participate in the normal dependency/rebuild mechanism, including lawyers becoming visible,
hidden, newly eligible, or losing a usable photo. Runtime does not mean CI-time hardcoded data.

This exception does not change Home's deterministic selection or the lower About showcases. Random
order must not be counted as an authored content edit or force a new section content version.

### 5.3 Company Statement

- `lead`: required rich text using the existing supported rich-text format and sanitization.
- Preserve deliberate emphasis, such as a bold introductory sentence.
- The statement is own editable content per locale; no regional override or append behavior.
- Decorative backgrounds, typography, and shapes belong to the public frontend, not CMS fields.

### 5.4 Company History

- Own editable content of each national locale page, not inherited content.
- `title`: required section heading.
- `lead`: optional rich-text introduction.
- `items[]`: ordered events, at least one for publication; no hardcoded product count.
- Each event: stable `id`, required `dateLabel`, required `title`, optional rich-text `description`.
- `dateLabel` is display text supporting a year or a more precise date. It does not control ordering.
- Array order is authoritative. Editors can add, remove, and reorder events; there is no second
  competing `sortOrder` field.
- Repeated years are valid. Stable event IDs must remain unchanged during text edits and reordering.
- Use the existing structured-list editor conventions. The horizontal timeline/scroll interaction is
  a frontend concern, with all events reachable on mobile and by keyboard.
- Mockup years, trademark text, and unrelated placeholder copy are not seed content.

### 5.5 Two Founders

- `items[]` contains exactly two records with stable `id` values and explicit array order.
- Each record has required `name`, `role`, `quote`, and `photo` using the existing CMS media reference.
- `quote` uses supported text/rich text, not unrestricted HTML; `role` is the visible attribution.
- Keep the records page-owned. Do not require the founders to be active ERP lawyers and do not create
  a new ERP person entity for this feature.
- Render both blocks vertically, alternating image/text sides as in the design. Do not implement
  carousel arrows, automatic slide replacement, or arbitrary numbers of founders.
- Both founder records are own editable content of each national locale page, not inherited records.

### 5.6 Offices and Map

`about_offices_intro` has required `title` and optional `lead`. `about_offices` is read-only.

- Include all eligible visible offices in visible regions across Ukraine. No current-region filtering
  or practice-competence requirement.
- Reuse office IDs, localized addresses, region labels, coordinates, map URLs, and existing visibility
  and validation rules. No duplicate address, coordinate, or Google Place ID inputs in this section.
- Preserve established region/office ordering with stable ID tie-breakers. Do not collapse multiple
  offices in the same city into one record. Do not silently truncate the promised office list.
- Selecting an office highlights it and centers its valid map marker. Opening its resolved Google Maps
  target is a separate accessible action.
- Invalid coordinates must not create a marker at zero/zero. Keep a valid textual address available
  when possible, with an admin warning and a disabled map-centering action.
- Use existing backend map-link resolution and diagnostics. Do not introduce stricter Place ID rules
  or frontend URL guessing solely for About.
- With no eligible offices, omit the empty map/list block and emit an admin warning. A map-provider
  failure must leave the address list usable.

### 5.7 Case, Lawyer, and Media Showcases

Each editable intro contains `title`, optional `lead`, optional paired `ctaLabel` / controlled
`ctaTarget`, and the existing selection configuration:

```json
{
  "selectionMode": "auto",
  "selectedIds": []
}
```

| Runtime list | Source | Automatic ordering | Initial limit |
| --- | --- | --- | --- |
| `about_cases` | Published localized `case_page` cards | Featured first, publication date descending, stable ID | 8 |
| `about_lawyers` | Visible lawyers across Ukraine with published profiles in the requested locale; no regional filter | Existing CMS/ERP sort order, existing name fallback, stable ID | 8 |
| `about_media` | Published localized `media_page` cards only | Featured first, publication date descending, stable ID | 8 |

- Reuse canonical lawyer IDs and editorial locale-group IDs. Editorial selections resolve the
  published member in the requested locale, not an arbitrary localized page ID.
- In `auto`, ignore stored manual IDs. In `manual`, preserve ID order, enforce the limit, reject
  duplicates, and never supplement with automatic results.
- The lower lawyer carousel reuses the linked-profile card eligibility. Unlike the hero, it needs a
  published localized profile. Do not accidentally impose hero-only portrait or randomness rules on it.
- Keep selection-picker and runtime eligibility identical across Ukraine, with no regional membership
  filter in either `auto` or `manual` mode.
- Cases and media are company-wide in automatic mode. Manual selections do not imply new geographic
  editorial metadata or an invented region-classification algorithm.
- Missing, hidden, unpublished, deleted, wrong-type, or untranslated selected records
  are omitted with specific admin warnings. Stored selections stay inspectable so editors can fix them.
- With no public cards, hide the empty carousel and its otherwise orphaned heading/CTA. Do not block
  publication solely because a showcase is empty or contains fewer than eight eligible items.
- Resolve card labels, media, author data, and canonical links through existing public card contracts.
  Frontend must not query ERP separately, fabricate slugs, or display UUIDs as labels.
- CTA targets refer to existing case collection, lawyer directory, or media collection. A missing
  published target produces a warning and no live public link; do not invent regional collection URLs.

About's selection settings remain independent of Home. Reuse resolver helpers where appropriate,
but do not alias About's keys to Home slots whose locale, geography, or content-type rules differ.

### 5.8 Inherited Global Application Form

`lead_form` inherits the existing global application form, `global_lead_form`, in the requested locale.
No About locale page owns editable form content. Change the form through its existing global editor;
About inherits the resulting published content through the shared lifecycle.

The expected ordinary form fields are listed for orientation; the existing global form and sender
contract, not an About-specific schema, determine their labels, requirements, and available choices:

| Field | Initial behavior |
| --- | --- |
| Name | Required; reuse existing name validation and length limit |
| Phone | Required; reuse existing normalization/validation |
| Preferred contact method/messenger | Use existing supported choices and their stable identifiers; default to phone |
| Question description | Optional free text with the existing submission length limit |

No email, arbitrary extra questions, or competence questionnaire is added by this specification.
Contact choices, field labels, privacy wording, contact numbers, and validation should reuse appropriate
existing shared contracts rather than hardcoded mockup values. Supporting phones come from current
site contact settings; About introduces no regional phone administration.

`lead_capture` supplies the existing ordinary form contract with the actual `pageType`, `locale`,
`pagePath`, `publicPath`, and `regionSlug`. Preserve sender compatibility; do not add a new About-only
delivery endpoint or variant merely to rename the existing form. National context has no page region.

Keep visitor-entered form values separate from CMS section authoring. Do not store visitor phone/name
in section content, published payloads, URLs, analytics event payloads, or application logs. Reuse the
existing server-side validation, destination routing, abuse protection, and retry handling where they
are implemented. Validate page context server-side rather than trusting a browser-supplied region.

The backend currently exposes `lead_capture` context; that alone is not proof of an end-to-end submission
handler. Before frontend integration, identify the actual sender endpoint, supported contact choices,
validation, and response DTO. Document any missing delivery work separately. Do not claim form
completion merely because the inputs render or a button shows a local success message.

On validation/network errors preserve entered values; prevent duplicate in-flight submits; show success
only after confirmed server acceptance. Locale and national context (no page region) must reach the
receiving system correctly.

## 6. Authoring and Versioning

- Add About to the existing single-page navigation area, opening its national-only workbench with
  the active page locale. Reuse matrix, section editor, diagnostics, and page preview surfaces.
- Display the actual selected national page and locale; do not offer a regional selector or conflate
  UI language with content locale. Missing locale placeholders are not created pages.
- Runtime portraits, offices, and resolved cards are read-only. Editable sister sections own their
  texts and selection configuration. The picker is an admin tool, not a public ERP endpoint.
- History and founders use ordinary own-content editors and Save behavior per locale. Only the
  inherited global form is edited through its global source, not locally in About.
- Follow the [section authoring/versioning contract](section-authoring-versioning-contract-2026-10-04.md)
  and its actually supported endpoint capabilities. Version history is read-only; local working copies
  and explicit saves must not be confused with runtime results.
- Do not make About an excuse to implement another section-publication mechanism or to claim the
  separate same-version publication transition has shipped. Integrate with the available shared
  lifecycle; improvements to that lifecycle retain their own acceptance gates.

## 7. Validation and Diagnostics

Publication errors are reserved for invalid required content, invalid authoring configuration, unsafe
references, or unresolved dependencies that prevent a valid section from being assembled. In particular:

- Missing required SEO/H1/statement text, an empty required history, incomplete history records,
  invalid two-founder composition, or unusable required founder photos are errors.
- Invalid selection mode, duplicate IDs, IDs of an invalid input shape, or more than eight selected
  showcase IDs are errors. A syntactically valid ID whose source later becomes unavailable is a warning.
- Regional About identity/creation requests and page-owned overrides of the inherit-only global form
  are rejected by the backend even if sent outside the UI.
- Missing eligible portraits, an empty office list, omitted selected cards, and unavailable optional
  links are warnings with the empty-state behavior specified above.
- An absent localized linked profile affects the lower lawyer carousel, not a non-link hero portrait.
- Ordinary length/quality recommendations are warnings. Do not invent arbitrary blocking text-length
  rules beyond the shared storage, security, and field contracts.

Diagnostics identify page, locale, national context (no page region), slot, field/item, and reason.
The menu, matrix, editor, and preview must agree for the same context. Runtime/editor warnings must
not be exposed as internal diagnostic data in the public page payload.

## 8. Backend Work

1. Register `about_page`, section types, fixed slots/composite groups, localized fields, source policies,
   and national own-content permissions. Limit route support and page catalog/workbench source handling
   to national About locale identities; an enum entry alone is insufficient.
2. Add idempotent explicit authoring creation/repair for national locale pages only. Keep candidate
   enumeration read-only, preserve existing content, enforce identity uniqueness and locale grouping.
3. Implement all-Ukraine eligible hero, offices, lower lawyers, and media-only runtime paths. Factor out
   reusable read-model/card helpers without changing Home or Contacts behavior.
4. Add admin selection options matching public eligibility, locale, type, and stable identifiers without
   regional filtering. Return structured reasons for unavailable selections. Keep list queries bounded/batched
   and avoid per-card media, publication, or profile queries.
5. Preserve inherited global-form dependencies, runtime source changes, media resolution, snapshot assembly,
   preview, publication, diagnostic rollups, stale markers, and existing page rollback.
6. Bind the ordinary global lead form and preserve its existing submission context. Produce examples and
   OpenAPI/typed DTOs for the actual implementation, including empty and invalid-selection cases.
7. Cover national routes, rejected regional identities, shared locale grouping, section-schema, runtime,
   validation, global-form inheritance, and publication regressions before handing frontend developers
   a stable contract.

No database schema migration is needed for the 2026-10-17 correction. No new reference-data tables,
duplicated ERP objects, content publication or data deletion are required. Preserve all runtime
dependencies, including `lawyers`, `contacts_runtime`, `editorial:case`, and `editorial:media` collection
dependencies, together with the existing global-form, media and snapshot dependency lifecycle.

## 9. Frontend Work for Yuriy

### CMS frontend

- Add/render the backend-provided About navigation and workbench with national-only rows and all
  three locales. Use server identities and capabilities rather than hardcoded source IDs.
- Implement supported editors for hero text, rich-text statement, timeline items, two founders with
  media, introductory texts, and selection controls. The inherited global form is read-only here.
- Edit history/founders as own content per locale, without regional source controls or locks. Preserve
  unsaved changes on locale/context switches.
- Reuse `auto` / `manual`, ordered pickers, media controls, diagnostics, Save/Preview/Publish behavior,
  and authorization. No separate frontend selection or inheritance algorithm.
- Render runtime previews separately from editable content. Never write returned runtime arrays back
  as section authoring data or create records merely by inspecting a version.

### Public site frontend

- Support only backend-published `/about`, `/ru/about`, and `/en/about` and render the fixed ordered
  composites. Do not publish hardcoded `/about` mock content as a substitute for CMS data.
- Animate only the supplied whole-team portrait pool. Keep stable IDs, server/client initial order,
  responsive framing, image fallbacks, and a reduced-motion/static mode. No ERP fetches from the browser.
- Render the timeline, both founder bands, office list/map, three carousels, and inherited global form according
  to the approved design. The lower lawyer section is company-wide legal assistance, not family-law copy.
- Keep office-list selection and external map navigation separate. Handle multiple offices per city,
  missing markers, no eligible offices, and map-provider failure without hiding valid addresses.
- Use resolved card links and images; honor empty lists and unavailable links. Do not substitute blog
  cards into the media carousel or automatic replacements into an empty manual selection.
- Submit the existing global form's fields with validated page context through the real sender contract.
  Include loading, validation error, retry, and confirmed-success states.
- Test desktop and mobile, keyboard access, long names/translations, small portrait pools, horizontal
  overflow, reduced motion, and SSR/hydration. No overlapping cards or unreadable text.

Frontend integration starts from backend fixtures/DTOs, not from speculative endpoint names in a task.
Backend and frontend can prepare in parallel, but acceptance requires their joined behavior.

## 10. Acceptance Matrix

| Scenario | Required outcome |
| --- | --- |
| National pages in all three locales | Only `/about`, `/ru/about`, `/en/about`; no page region; fixed section order |
| Locale switch | One shared national locale group; only published locale alternatives are public |
| Regional About request or candidate enumeration | Regional routes/creation rejected; no regional rows, fallback pages, inheritance or locks |
| Possible page or saved draft | No public route/sitemap entry until normal publication |
| Create/repair requested twice | No duplicate page identities, bindings, or erased content |
| Hero and office coverage | Whole-team portrait pool and all eligible offices across Ukraine; no regional filtering |
| Visible lawyer with photo but no published profile | Can appear in hero; cannot appear as a linked lower-showcase profile |
| Hero with 0, 1, fewer than 8, and more than 8 portraits | Graceful rendering; no fabricated duplicates or backend eight-person cap |
| Repeated read or retry of one snapshot | Stable payload/order; no extra authored versions or writes |
| Source visibility/media changes and normal rebuild | Affected About pages are tracked; rebuilt portrait eligibility is correct |
| History/founder editing | Own editable content per locale; no regional inheritance or locks |
| National draft changes | Existing public snapshots do not silently change |
| Lower lawyers and selection picker | Same all-Ukraine eligibility in auto/manual; published localized profiles required; limit eight |
| Manual selection becomes unavailable | Warning with exact reason; omit item; no automatic replacement |
| Cases/media configuration | Own localized About configuration, independent of Home |
| About media query/selection | Media only; no blog cards |
| Office selection with valid/invalid coordinates | Correct marker centering, or usable text without a fake marker |
| Two founders | Both shown vertically; no carousel or third record |
| Form validation or network failure | No false success or lost input; duplicate in-flight submission prevented |
| Global form ownership | Ordinary inherited `global_lead_form`; no About-owned form editor or override |
| Successful national form submission | Confirmed receiver acceptance with correct page/locale and no selected page region |
| Menu, matrix, and editor validation | Consistent issue scope for the selected national locale page |
| Runtime dependency changes | Global-form, media and all About runtime dependencies still invalidate/rebuild through the existing lifecycle |
| Existing Home, Contacts, service hierarchy, and versioning | No changed eligibility, random ordering, routes, or publication semantics |

Use unit and contract tests for rules/DTOs, integration tests for global-form inheritance,
snapshot/dependency and submission behavior, and browser tests for CMS and public-site workflows.
A successful backend build does not establish frontend, form-delivery, or release acceptance.

## 11. Delivery Sequence

1. Backend contract and fixtures: schemas, national identity/shared locale group, global-form inheritance,
   validation, public payload examples, selection DTOs, and the actual form integration boundary.
2. Backend implementation and tests: runtime/read-model paths, authoring/workbench, dependency handling,
   snapshot publication, and navigation/catalog integration.
3. Yuriy: CMS authoring plus public rendering, then integration against backend fixtures and endpoints.
4. Joint acceptance: national-only behavior in all three locales, rejected regional requests,
   partial/unpublished content and locale placeholders, empty source data, and real test submission handling.
5. Separately approved rollout: verify the same feature and compatibility in `develop`, then `release`
   under the governing playbook. Do not bulk-publish pages, seed mock founders/history, change domains,
   open indexing, or change access as part of this documentation task.

## 12. Existing Contracts and Implementation Baseline

- [Home structure and selection contract](home-page-structure-2026-08-05.md).
- [Practice regional composition model](practice-page-structure-2026-06-13.md), for other page types;
  it does not apply to national-only About.
- [Section authoring and versioning](section-authoring-versioning-contract-2026-10-04.md).
- [Reference data and runtime boundary](reference-data-and-runtime-model.md).
- [Editorial content contract](editorial-content-specification-2026-08-23.md).
- [Structured-data requirements](json-ld-implementation-requirements-2026-08-03.md).
- [Lead questionnaire contract](lead-questionnaire-contract-2026-07-16.md), for the distinction from the
  universal contact form; this page adds no questionnaire.

Implementation inspection for this specification used local `re-actum/cms-back` commit
`18dc40a3be8796ccd4f49a2e0e6fa7046a299aa0`. This is the historical 2026-10-06 source-code baseline,
not a current implementation or deployment report. Required extensions below follow the authoritative
2026-10-17 national-only correction; earlier regional extension requirements are superseded.

| Existing code area | Relevant finding or required extension |
| --- | --- |
| `src/routing/public-route.types.ts` | `about_page` is declared |
| `src/routing/public-route-builder.ts` | Support only the three national locale routes; regional About must remain unsupported |
| `src/page-schemas/page-schema.types.ts`, `page-schema-registry.ts` | About authoring schema is absent |
| `src/page-workbench`, `src/pages-catalog`, `src/admin-navigation` | Integrate About national locale rows/placeholders, actions, and diagnostics; no regional candidates |
| `src/runtime-resolvers/page-runtime-resolver.service.ts` | Existing Home selectors, Contacts-only map, and `service_hierarchy` lead context require scoped adaptation |
| `src/lawyer-selection/home-lawyer-query.ts` | Home lawyer selection requires a published localized profile; do not reuse that eligibility for the hero unchanged |
| `src/public-pages/public-pages.service.ts` | Public reads serve stored snapshots; do not introduce a hidden live reshuffle on every GET |
| `src/structured-data` | About support exists at graph level; it does not establish schema/editor/public page completeness |

No other page type's behavior is superseded by this specification. The About-specific rules above
must be implemented and tested explicitly rather than inferred from similarly named Home slots.
