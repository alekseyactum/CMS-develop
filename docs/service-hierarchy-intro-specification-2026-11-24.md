# Unified Intro for Practice, Service, Problem and Intent pages

Status: agreed specification, 2026-11-24. This document does not record an implementation or rollout.
It supersedes the older first-screen Intro field, presentation and validation rules for these four
slots only: `practice_intro`, `service_intro`, `problem_intro` and `intent_intro`. A Problem and an
Intent are different page types. Other slots with “Intro” in their name are not part of this change.

## 1. Content and display

Intro remains one required section, in its existing first-screen position. It has the same four text
fields on all four page types, in UA, RU and EN:

| Field | Type | Requirement and presentation |
| --- | --- | --- |
| `lead` | Plain text | Optional, up to **40 characters**. Display as a separate short pink line above the main heading. |
| `title` | Plain text | Required, non-blank, up to **100 characters**. This is the complete large heading (H1). |
| `accentTitle` | Plain text | Optional. It contains a fragment already present in `title`. Highlight that fragment in pink within the same H1. Do not render it as a separate line or append it to the heading. No independent 40-character limit applies to this field. |
| `bigtext` | Rich text blocks | New, optional, up to **600 characters of visible text**. Use the standard CMS rich-text editor. Render the formatted content beneath the heading within the same Intro section. |

The optional CTA and its existing fields and behavior are outside this change. The separate
`practice_intro_text` and `intent_intro_text` sections remain independent and unchanged.

## 2. Validation

- The maximum values are inclusive: 40, 100 and 600 characters are allowed; exceeding any limit is
  an **error**. Count the text the reader sees, including spaces, and not rich-text markup, links'
  targets or JSON overhead.
- An absent or empty optional field does not cause a validation issue. An empty or whitespace-only
  `title` retains the existing required-heading check.
- A nonempty `accentTitle` must be found within the effective `title`. A missing match is an
  **error**; neither CMS nor site-front may append the accent as a fallback.
- Register the errors against their fields and use the normal CMS validation, diagnostics and
  blocking behavior for the corresponding operation. Do not add an Intro-specific bypass, downgrade
  the errors to warnings, or change draft/publication behavior for other fields. Check the effective
  section after applying inheritance, not just the fields stored in a regional override.

## 3. Ownership and inheritance

- National practices, services and problems own their Intro for each language. On regional pages of
  these types, the source is the national page of the same type, hierarchy node and language.
- Regional `title` and `accentTitle` always inherit together. They cannot be overridden locally.
  Regional `lead` and `bigtext` inherit by default and may be overridden independently.
- Each national and regional Intent variant owns all four Intro fields. The existing one-time
  Intent title initialization is unchanged; it is not live inheritance.
- Do not automatically insert or inflect a region name in the Intro heading in this scope.

## 4. Transition

- Preserve existing `title`, `accentTitle` and CTA values. Keep the old `lead` in the same field,
  converting a rich-text value to all of its visible text in reading order. Preserve the original
  formatting in existing version history. Do not truncate any field.
- Do not copy a prior `lead`, the separate `Intro text`, or any other text into `bigtext`. It
  starts empty for existing pages. A previously absent `accentTitle` starts empty.
- Preserve existing local overrides and inheritance. Do not turn inherited content into local copies.
  If transferred values violate a new rule, report the error for editorial correction; do not
  silently shorten, discard or rewrite the content.
- Keep existing published snapshots and history intact. No automatic or manual republication is
  required for this transition. Keep the public reader compatible with already published Intro data
  while the new contract is introduced.

## 5. Implementation handoff and acceptance

- **CMS-back:** register the common schema, validate all four Intro types through the existing
  validation pipeline, and handle the transition without modifying published snapshots.
- **CMS-front:** expose the four fields with their correct editors, show the standard field errors,
  and enforce the regional editability rules. Do not change the button or other Intro text section
  controls.
- **Site-front (separate task):** implement the first-screen display for **all four types**, including
  wiring `intent_intro` into Intent page rendering. Verify the separate pink lead, the single H1
  with an in-place highlight, the formatted `bigtext`, graceful display when optional fields are
  empty, and unchanged CTA behavior.

Acceptance includes exact boundaries (40/41, 100/101, 600/601), blank required title, empty optional
fields, an accent that matches and one that does not, rich text whose markup does not count toward
the limit, and existing over-limit values retained without loss. Use a national/regional pair in the
same language to verify the locked headings and independent text overrides, a separate Intent pair
to verify independent content, and UA/RU/EN to verify no cross-language inheritance. Verify on test
pages or fixtures; compare existing published snapshots for no change.
