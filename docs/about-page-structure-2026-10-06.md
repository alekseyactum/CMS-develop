# About Page Structure and Implementation Specification

Date: 2026-10-06.

This is the agreed product scope for `about_page`, with implementation rules for `cms-back`,
`cms-front`, and `site-front`. It covers the national page, regional variants, all three locales,
authoring, runtime data, and acceptance. Recording this specification does not implement the page,
create content, publish pages, or authorize deployment.

The page introduces Actum as a company across all practices. It is not a family-law landing page.
The approved sequence is: introduction, company statement, history, founders, offices, cases,
lawyers, media publications, and the ordinary inherited global application form.

## 1. Approved Product Decisions

| Area | Decision |
| --- | --- |
| Page variants | One national page and regional variants; `uk`, `ru`, and `en` for each |
| Animated hero | Backend supplies an automatically selected runtime array of enabled lawyers with usable portraits; no manual selection |
| Hero geography | The entire Actum team on both national and regional pages, not just the current region |
| Hero ordering | Randomized ordering at assembly; no need for a different order on every browser refresh |
| Company history | Editor-managed events and order; no fixed product count |
| Founders | Exactly two people, displayed vertically one after the other, not a carousel |
| Office map | Existing ERP offices; selecting a list item centers the map; opening Google Maps is a separate action |
| Case, lawyer, and media showcases | Existing `auto` / `manual` selection principle; settings belong to About, not Home |
| Media showcase | Media publications only, not a mixed blog/media list |
| Regional differences | Adaptable introductory text and SEO; local offices and lower lawyer showcase; shared company history and founders |
| Regional cases and media | Inherit national About selections by default; explicit regional manual selections are allowed |
| Contact form | Existing `global_lead_form` without page-owned fields; actual page region accompanies the submission context |

2026-10-06 clarification: the contact block is the ordinary `lead_form` inherited from
`global_lead_form`, together with the existing `lead_capture` context. There is no About-owned form,
field schema, submit label, or form editor. The global form contract owns its fields and presentation.

The remaining field names, limits, validation rules, and empty states below are implementation defaults
chosen to fit existing CMS conventions. They are not claims that these API fields already exist.
The initial carousel limit is 8, matching the existing Home showcase limit. This limit does not apply
to the hero's full lawyer pool, history, or offices.

## 2. Routes and Page Identity

| Locale | National | Regional |
| --- | --- | --- |
| `uk` | `/about` | `/{regionSlug}/about` |
| `ru` | `/ru/about` | `/ru/{regionSlug}/about` |
| `en` | `/en/about` | `/en/{regionSlug}/about` |

- Use `about_page` as the page type and `about` as the fixed page path.
- Enforce one authoring page per locale and region context; an empty region denotes the national page.
- Resolve regions from existing visible ERP/CMS region records with valid slugs. Do not derive About
  availability from practice qualifications or require practice pages to exist first.
- A region is not an alternative language. Each national/regional identity has its own locale group.
- Language switching preserves the region. Public alternate links include only published translations
  of that same variant, not another region's page.
- Canonical paths use the resolved variant path. Host selection follows the project's existing runtime
  configuration, not a new hardcoded host in this feature.
- Draft pages and merely possible regional variants are not public routes. Do not mass-create or
  publish pages when a developer registers the schema or an editor opens the workbench.
- Add normal catalog, workbench, navigation, preview, redirects, and published sitemap support.
  Listing a possible regional row is distinct from creating its authoring page.

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

## 4. Regional Inheritance

Regional authoring inherits from the national About page of the **same locale**. Reuse the existing
base/override composition and dependency model, not frontend merging or independent copied defaults.
There is no cross-language authoring fallback and no About-specific global-section registry.

| Content | Regional rule |
| --- | --- |
| SEO title/description/image | Inherit by default; explicit override allowed; canonical path remains regional |
| Hero H1/subtitle and company statement | Inherit by default; explicit override allowed |
| Hero lawyer array | Resolve the whole team; ignore regional filtering deliberately |
| History and both founders | Inherit-only from national About in the same locale; no regional override or append |
| Office introductory text | Inherit; allow regional lead-text override; keep the section heading inherited |
| Office rows and markers | Resolve only offices of the current region |
| Lower lawyer showcase | Inherit configuration by default; local manual selection allowed; always enforce regional eligibility |
| Case and media showcases | Inherit national About configuration; allow local selection override; no automatic geographic filtering |
| Showcase headings | Inherit from national About; do not relax existing section-heading locks across other page types |
| Showcase lead text | Inherit by default; explicit regional override allowed |
| Form presentation | Inherit-only from `global_lead_form`; no national or regional page-level overrides |
| Form context | Resolve from the actual page and locale; national has no selected page region |

`about_intro.title` is the page H1, not an ordinary locked section heading. Preserve its explicit regional
override capability without weakening heading locks on practice/service/problem pages.

For a regional lawyer block, inherited `auto` means automatic selection in the current region, not the
national page's already resolved cards. Inherited `manual` uses the inherited IDs but still filters by
region; omitted out-of-region selections receive diagnostics. An empty result never silently borrows
lawyers from another region. Editors can switch to local `auto` or a local manual selection.

Selection mode and selected IDs are overridden as one configuration. Do not accidentally combine a
regional mode with unrelated national IDs. This first version does not need append composition.

National edits participate in existing dependency/staleness and page publication flows. Saving a base
draft does not silently change a regional published page. Rebuilding or publishing resolves approved
dependencies through the backend. Missing required inherited content is an actionable blocker, not an
empty successful section or a silent language substitution.

## 5. Section Fields and Behavior

### 5.1 SEO

Reuse existing `seo` fields: required `title` and `description`, optional `ogImage`, and backend-owned
canonical resolution. Regional text overrides are allowed. Do not expose a free-form canonical editor
that can accidentally point every regional page at the national route.

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
- Regional pages may override the statement; no append behavior in the first version.
- Decorative backgrounds, typography, and shapes belong to the public frontend, not CMS fields.

### 5.4 Company History

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
- Regional pages show inherited records read-only, with access to their national source.

### 5.6 Offices and Map

`about_offices_intro` has required `title` and optional `lead`. `about_offices` is read-only.

- National page: visible offices in visible regions. Regional page: the same eligibility plus exact
  current-region filtering. No practice-competence requirement.
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
- Empty regional results do not fall back to another city's offices. With no offices, omit the empty
  map/list block and emit an admin warning. A map-provider failure must leave the address list usable.

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
| `about_lawyers` | Visible lawyers with published profiles in the requested locale; regional membership filter when applicable | Existing CMS/ERP sort order, existing name fallback, stable ID | 8 |
| `about_media` | Published localized `media_page` cards only | Featured first, publication date descending, stable ID | 8 |

- Reuse canonical lawyer IDs and editorial locale-group IDs. Editorial selections resolve the
  published member in the requested locale, not an arbitrary localized page ID.
- In `auto`, ignore stored manual IDs. In `manual`, preserve ID order, enforce the limit, reject
  duplicates, and never supplement with automatic results.
- The lower lawyer carousel reuses the linked-profile card eligibility. Unlike the hero, it needs a
  published localized profile. Do not accidentally impose hero-only portrait or randomness rules on it.
- Regional lawyer membership must use the existing canonical region/office association resolver.
  Keep selection-picker and runtime eligibility identical; do not infer region from an address string.
- Cases and media are company-wide in automatic mode. Regional manual selection does not imply new
  geographic editorial metadata or an invented region-classification algorithm.
- Missing, hidden, unpublished, deleted, wrong-type, untranslated, or out-of-region selected records
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
Neither the national nor a regional About page owns editable form content. Change the form through
its existing global editor; About inherits the resulting published content through the shared lifecycle.

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
only after confirmed server acceptance. Region and locale must reach the receiving system correctly.

## 6. Authoring and Versioning

- Add About to the existing single-page navigation area, opening its national/regional workbench with
  the active page locale. Reuse matrix, section editor, diagnostics, and page preview surfaces.
- Display the actual selected page, locale, and region; do not conflate UI language with content locale.
- Runtime portraits, offices, and resolved cards are read-only. Editable sister sections own their
  texts and selection configuration. The picker is an admin tool, not a public ERP endpoint.
- Regional inherit-only history/founders show their source and resolved content. Do not display a Save
  action that pretends to edit them locally.
- Follow the [section authoring/versioning contract](section-authoring-versioning-contract-2026-10-04.md)
  and its actually supported endpoint capabilities. History is read-only; local working copies and
  explicit saves must not be confused with runtime results.
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
- A regional override of inherit-only content is rejected by the backend even if sent outside the UI.
- Missing eligible portraits, an empty office list, omitted selected cards, and unavailable optional
  links are warnings with the empty-state behavior specified above.
- An absent localized linked profile affects the lower lawyer carousel, not a non-link hero portrait.
- Ordinary length/quality recommendations are warnings. Do not invent arbitrary blocking text-length
  rules beyond the shared storage, security, and field contracts.

Diagnostics identify page, locale, region, slot, field/item, and reason. The menu, matrix, editor, and
preview must agree for the same context. Runtime/editor warnings must not be exposed as internal
diagnostic data in the public page payload.

## 8. Backend Work

1. Register `about_page`, section types, fixed slots/composite groups, localized fields, source policies,
   and field-level regional permissions. Extend route support and the required page catalog/workbench
   source handling; an enum entry alone is insufficient.
2. Add idempotent explicit authoring creation/repair for national and regional variants. Keep candidate
   enumeration read-only, preserve existing content, enforce identity uniqueness and locale grouping.
3. Implement hero, regional offices, regional lower lawyers, and media-only runtime paths. Factor out
   reusable read-model/card helpers without changing Home or Contacts behavior.
4. Add admin selection options matching public eligibility, locale, type, region, and stable identifiers.
   Return structured reasons for unavailable selections. Keep list queries bounded/batched and avoid
   per-card media, publication, or profile queries.
5. Integrate inherited section dependencies, source changes, media resolution, snapshot assembly,
   preview, publication, diagnostic rollups, stale markers, and existing page rollback.
6. Bind the ordinary global lead form and preserve its existing submission context. Produce examples and
   OpenAPI/typed DTOs for the actual implementation, including empty and invalid-selection cases.
7. Cover route, locale-group, section-schema, runtime, validation, inheritance, and publication regressions
   before handing frontend developers a stable contract.

No new reference-data tables or duplicated ERP objects are prescribed. Decide whether additive storage
changes are actually necessary during implementation; do not assume a migration is either required or
unnecessary merely from the page design.

## 9. Frontend Work for Yuriy

### CMS frontend

- Add/render the backend-provided About navigation and workbench with national/regional rows and all
  three locales. Use server identities and capabilities rather than hardcoded source IDs.
- Implement supported editors for hero text, rich-text statement, timeline items, two founders with
  media, introductory texts, and selection controls. The inherited global form is read-only here.
- Show history/founders read-only in regional pages, with a link to the national source. Support explicit
  regional overrides only where the schema allows them and preserve unsaved changes on context switches.
- Reuse `auto` / `manual`, ordered pickers, media controls, diagnostics, Save/Preview/Publish behavior,
  and authorization. No separate frontend selection or inheritance algorithm.
- Render runtime previews separately from editable content. Never write returned runtime arrays back
  as section authoring data or create records merely by inspecting a version.

### Public site frontend

- Support backend-published national/regional routes in all locales and render the fixed ordered
  composites. Do not publish hardcoded `/about` mock content as a substitute for CMS data.
- Animate only the supplied whole-team portrait pool. Keep stable IDs, server/client initial order,
  responsive framing, image fallbacks, and a reduced-motion/static mode. No ERP fetches from the browser.
- Render the timeline, both founder bands, office list/map, three carousels, and inherited global form according
  to the approved design. The lower lawyer section is company-wide legal assistance, not family-law copy.
- Keep office-list selection and external map navigation separate. Handle multiple offices per city,
  missing markers, no local offices, and map-provider failure without hiding valid addresses.
- Use resolved card links and images; honor empty lists and unavailable links. Do not substitute blog
  cards into the media carousel or national lawyers into an empty regional carousel.
- Submit the existing global form's fields with validated page context through the real sender contract.
  Include loading, validation error, retry, and confirmed-success states.
- Test desktop and mobile, keyboard access, long names/translations, small portrait pools, horizontal
  overflow, reduced motion, and SSR/hydration. No overlapping cards or unreadable text.

Frontend integration starts from backend fixtures/DTOs, not from speculative endpoint names in a task.
Backend and frontend can prepare in parallel, but acceptance requires their joined behavior.

## 10. Acceptance Matrix

| Scenario | Required outcome |
| --- | --- |
| National and regional pages in all three locales | Correct identity, path, locale, region, and fixed section order |
| Regional locale switch | Same region; only published locale alternatives are public |
| Possible page or saved draft | No public route/sitemap entry until normal publication |
| Create/repair requested twice | No duplicate page identities, bindings, or erased content |
| Hero on two different regions | Same whole-team eligibility, not region-restricted membership |
| Visible lawyer with photo but no published profile | Can appear in hero; cannot appear as a linked lower-showcase profile |
| Hero with 0, 1, fewer than 8, and more than 8 portraits | Graceful rendering; no fabricated duplicates or backend eight-person cap |
| Repeated read or retry of one snapshot | Stable payload/order; no extra authored versions or writes |
| Source visibility/media changes and normal rebuild | Affected About pages are tracked; rebuilt portrait eligibility is correct |
| Regional history/founder edit attempt | Rejected; national same-locale source remains authoritative |
| National draft changes | Existing public regional snapshots do not silently change |
| Regional lower lawyers | Eligible local lawyers only in auto, inherited manual, and local manual modes |
| Manual selection becomes unavailable | Warning with exact reason; omit item; no automatic replacement |
| Regional cases/media without override | Inherit About national configuration, not Home's configuration |
| About media query/selection | Media only; no blog cards |
| Office selection with valid/invalid coordinates | Correct marker centering, or usable text without a fake marker |
| Two founders | Both shown vertically; no carousel or third record |
| Form validation or network failure | No false success or lost input; duplicate in-flight submission prevented |
| Successful national/regional form submission | Confirmed receiver acceptance with correct page, locale, and region context |
| Menu, matrix, and editor validation | Consistent issue scope for the selected locale/region |
| Existing Home, Contacts, service hierarchy, and versioning | No changed eligibility, random ordering, routes, or publication semantics |

Use unit and contract tests for rules/DTOs, integration tests for inheritance, snapshot/dependency and
submission behavior, and browser tests for CMS and public-site workflows. A successful backend build
does not establish frontend, form-delivery, or release acceptance.

## 11. Delivery Sequence

1. Backend contract and fixtures: schemas, regional identity, inheritance, validation, public payload
   examples, selection DTOs, and the actual form integration boundary.
2. Backend implementation and tests: runtime/read-model paths, authoring/workbench, dependency handling,
   snapshot publication, and navigation/catalog integration.
3. Yuriy: CMS authoring plus public rendering, then integration against backend fixtures and endpoints.
4. Joint acceptance: one national and at least two different regional contexts, all three locales,
   partial/unpublished content, empty source data, and real test submission handling.
5. Separately approved rollout: verify the same feature and compatibility in `develop`, then `release`
   under the governing playbook. Do not bulk-publish pages, seed mock founders/history, change domains,
   open indexing, or change access as part of this documentation task.

## 12. Existing Contracts and Implementation Baseline

- [Home structure and selection contract](home-page-structure-2026-08-05.md).
- [Practice regional composition model](practice-page-structure-2026-06-13.md).
- [Section authoring and versioning](section-authoring-versioning-contract-2026-10-04.md).
- [Reference data and runtime boundary](reference-data-and-runtime-model.md).
- [Editorial content contract](editorial-content-specification-2026-08-23.md).
- [Structured-data requirements](json-ld-implementation-requirements-2026-08-03.md).
- [Lead questionnaire contract](lead-questionnaire-contract-2026-07-16.md), for the distinction from the
  universal contact form; this page adds no questionnaire.

Implementation inspection for this specification used local `re-actum/cms-back` commit
`18dc40a3be8796ccd4f49a2e0e6fa7046a299aa0`. This is a source-code baseline, not a new deployment report.

| Existing code area | Relevant finding or required extension |
| --- | --- |
| `src/routing/public-route.types.ts` | `about_page` is declared |
| `src/routing/public-route-builder.ts` | Regional About is not currently allowed; extend deliberately |
| `src/page-schemas/page-schema.types.ts`, `page-schema-registry.ts` | About authoring schema is absent |
| `src/page-workbench`, `src/pages-catalog`, `src/admin-navigation` | Integrate About national/regional source rows, actions, and diagnostics |
| `src/runtime-resolvers/page-runtime-resolver.service.ts` | Existing Home selectors, Contacts-only map, and `service_hierarchy` lead context require scoped adaptation |
| `src/lawyer-selection/home-lawyer-query.ts` | Home lawyer selection requires a published localized profile; do not reuse that eligibility for the hero unchanged |
| `src/public-pages/public-pages.service.ts` | Public reads serve stored snapshots; do not introduce a hidden live reshuffle on every GET |
| `src/structured-data` | About support exists at graph level; it does not establish schema/editor/public page completeness |

No existing page type's behavior is superseded by this specification. The About-specific rules above
must be implemented and tested explicitly rather than inferred from similarly named Home slots.
