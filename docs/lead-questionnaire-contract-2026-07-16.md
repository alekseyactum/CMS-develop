# Lead Questionnaire Contract

Date: 2026-07-16

`lead_questionnaire` is the optional page-owned questionnaire used inside the composite lead block on
`practice_page`, `service_page`, and `problem_page`. It is disabled by default and may be enabled by an
editor when the page needs preliminary qualifying questions before the standard lead form.

## Canonical content

```json
{
  "finalMessageTitle": "Дякуємо за відповіді",
  "finalMessageDescription": [
    { "type": "paragraph", "text": "Ми зв'яжемося з вами." }
  ],
  "questions": [
    {
      "id": "preferred-contact",
      "question": "Як вам зручніше отримати відповідь?",
      "type": "single_choice",
      "required": false,
      "options": [
        { "id": "phone", "label": "Телефоном" },
        { "id": "messenger", "label": "У месенджері" }
      ]
    }
  ]
}
```

- `finalMessageTitle` is the optional heading shown after the questionnaire is completed.
- `finalMessageDescription` is the optional rich-text message shown with that heading.
- `questions` is optional. It may be omitted or stored as an empty array; in that case the composite
  lead block renders the standard required lead form without preliminary questionnaire steps.
- `question.id` and `option.id` are stable technical identifiers. The frontend must preserve them while
  labels and order are edited.
- `question.question` is the visible question text.
- `question.type` is either `single_choice` or `multiple_choice`. Free-text questionnaire questions are
  not supported; free text remains part of the standard lead form.
- `question.required` is a boolean and defaults to `false` when omitted from legacy content.
- `question.options` is required and non-empty for every supported question type.
- Array order is the canonical display order. There is no separate `sortOrder` field.

The lead block itself remains required through `lead_form`. An empty or absent questionnaire does not
disable the form and is not a validation issue. Question-level validation applies only to questions that
are actually present.

## Inheritance

Regional pages inherit questionnaire content from the matching base page by default:

- `finalMessageTitle`: `inherit` or `override`;
- `finalMessageDescription`: `inherit` or `override`;
- `questions`: `inherit`, `override`, or `append`.

The section remains one page-owned lifecycle unit. It is not independently published: its selected draft
is included when the owning page is published.

## Compatibility

Stored historical JSON is not rewritten by a database migration. The backend exposes old versions through
the canonical editor/read contract:

- `title` is read as `finalMessageTitle`;
- `description` is read as `finalMessageDescription`;
- question `label` is read as `question`;
- option `value` is read as option `id`;
- missing question/option IDs receive deterministic legacy fallback IDs;
- missing `required` is read as `false`.

Legacy `type: "text"` remains visible but fails validation, so the editor can explicitly replace or remove
that question. Every newly saved draft is stored in the canonical format above.
