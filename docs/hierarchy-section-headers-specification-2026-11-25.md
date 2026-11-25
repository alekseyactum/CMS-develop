# Unified section headers for Practice, Service and Problem pages

Status: agreed specification, 2026-11-25. This document does not record implementation or rollout.
It supersedes the header field and validation rules for the nine editable slots listed below.

## 1. Scope

| Block | Practice | Service | Problem |
| --- | --- | --- | --- |
| Services | `practice_services_block` | — | — |
| Actions | `practice_actions` | `service_lawyer_actions` | `problem_lawyer_actions` |
| Problems | — | `service_problems_block` | — |
| What to do | — | `service_must_do` | `problem_must_do` |
| What not to do | — | `service_must_not_do` | `problem_must_not_do` |

Only the header of each slot changes. Keep the section order, visibility, required/optional status,
`variant` where present, item schemas and validation, item selection and ordering. The runtime
`practice_services` and `service_problems` slots remain read-only and stay paired with their respective
editable headers. Other sections and Intent pages are out of scope. The
[first-screen Intro contract](service-hierarchy-intro-specification-2026-11-24.md) is unchanged.

## 2. Fields and display

All four fields are plain text, with the same rules for UA, RU and EN. They do not have rich-text
controls, markup or link fields.

| Field | Role | Requirement |
| --- | --- | --- |
| `title` | Ordinary part of the H2 | May be empty if `accentTitle` has text. |
| `accentTitle` | Pink part of the same H2, placed after the ordinary part | May be empty if `title` has text. |
| `smallPinkText` | Separate smaller pink line above the H2 | Optional, at most 60 characters. |
| `greyText` | Smaller grey description below the H2 | Optional, at most 160 characters. |

The H2 is required **as a whole**, not as two separately required fields. Render exactly one H2.
Two nonblank parts are joined by one space, included in the limit of **40 characters for the whole H2**.
Render the nonblank part alone if the other is empty: an accent-only heading is allowed and is fully
pink. Do not search for a fragment inside `title` with the new format. Do not render empty auxiliary lines.
Keep existing section anchors; where a display label needs the visible heading, use the complete H2,
including when only the accent is present.

Example: `title = "Що робити"`, `accentTitle = "після відмови"` → one heading
«Що робити після відмови», with only «після відмови» in pink.

## 3. Validation and inheritance

- Treat whitespace-only values as empty. Trim heading parts at their edges when composing the H2;
  count Unicode code points in the visible text, including internal spaces and the separator. 40, 60
  and 160 are inclusive. Both heading parts empty or any exceeded limit is an **error**, not a warning.
  Attribute the heading error to the pair in the editor and an auxiliary error to its own field.
  Use the existing CMS validation and operation-blocking behavior; do not truncate inputs or change
  validation of other fields or slots.
- Check the effective header after applying inheritance. A regional heading inherits both parts together
  from the national variant of the same page and locale. Neither part can be overridden locally.
  `smallPinkText` and `greyText` inherit by default and may be overridden independently. Keep the
  existing distinction between inheritance and an explicit local override; do not materialize inherited
  values when changing a different field. There is no cross-locale or cross-node fallback.
- Treat all four fields as translatable text in existing CMS translation workflows. Validate the
  localized result with the same limits, without clipping or inventing a missing heading part.

## 4. Transition and compatibility

- Existing published snapshots and version history remain unchanged. Do not bulk republish or rewrite
  live content. Public rendering and the editor/preview must read old content during the transition.
- Old `lead` was the explanation below the H2, not the line above it. Where the new `greyText` has not
  been authored, project the old `lead` to visible plain text in reading order, preserving word
  boundaries. Preserve the original rich text in history. Do not restore old `lead` over an
  intentionally empty new value. Start `smallPinkText` empty. Keep text longer than 160 intact and show
  a field error for editorial correction.
- Interpret legacy heading pairs using their existing public rendering, which may highlight a
  fragment inside `title` or append a separate accent. If the legacy accent is already separate, do not
  move it. If the highlighted fragment is at the end of `title`, separate it into `accentTitle` only
  when this preserves the visible text and highlight. Do not append the same fragment twice.
- If the existing highlight is inside the heading and cannot be moved to the end without changing
  the wording, keep its legacy appearance. A change to either heading part requires the editor to
  arrange the two parts in the new format. Opening the editor or saving another field must not
  silently reorder or duplicate the heading. Apply the length rule to the text actually shown, not
  to a sum that counts a legacy embedded accent twice. Preserve over-limit text for manual correction.
- Before enforcing the new rules, run a read-only inventory by slot and locale for effective headings
  over 40, projected descriptions over 160, and legacy accents that need manual review. The inventory
  is for planning corrections, not updating records.

## 5. Implementation handoff and acceptance

- **CMS-back:** expose the common schema and combined heading rule, including field metadata in the
  editor; apply inheritance, translation, validation and legacy projection consistently to the nine slots.
- **CMS-front:** expose the four plain-text inputs, a shared H2 count and individual auxiliary counts;
  show errors without losing input. Use the existing regional controls and make it clear that
  either heading part may be used alone.
- **Site-front and preview:** render the shared header consistently for the nine slots, preserving existing
  list components and legacy rendering. Do not change the first-screen Intro or unrelated headings.

Verify with fixtures or test drafts:

1. Ordinary-only, accent-only, both parts, and whitespace-only in both parts. Cover 40/41 for a single
   part and for two parts including the separator; 60/61 and 160/161 for the two optional texts.
2. On each of Practice, Service and Problem, compare a national and regional variant in UA, RU and EN:
   the H2 inherits as one unit, each auxiliary field can be overridden or returned to inheritance
   without changing the other, and each translation follows the same limits.
3. Read an old standalone accent, a highlighted suffix and a highlighted middle. None are duplicated
   or reordered when opening or saving another field. Check old rich `lead`, an over-limit description
   and an explicitly cleared new description. Confirm the old public data and the original versions
   have not changed.
4. Compare before/after for all nine slots: the same item data, ordering and visibility; when only
   `accentTitle` is set, the H2 is present, pink and linked from the existing section anchor.
