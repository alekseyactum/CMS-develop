# CMS Front Page Authoring Task

This document is the first implementation task for CMS frontend page authoring screens.

The backend contract is available in Swagger/OpenAPI. Use OpenAPI examples as the primary source for
request/response shapes, especially for authoring state, preview, publish, and rollback.

## Endpoints

```text
GET  /api/admin/page-schemas
GET  /api/admin/page-schemas/{pageType}
GET  /api/admin/navigation
GET  /api/admin/page-workbench/tree
GET  /api/admin/page-workbench/service-tree
GET  /api/admin/page-workbench/page-types/{pageType}
GET  /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/row
GET  /api/admin/page-workbench/pages/{pageId}/row
GET  /api/admin/page-workbench/pages/{pageId}/history
POST /api/admin/page-workbench/bulk-publish/plan
POST /api/admin/page-workbench/bulk-publish
POST /api/admin/page-workbench/pages/bootstrap
POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/bootstrap
POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/open
POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/open-editor
GET  /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor
GET  /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/inspect
PATCH /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/state
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/draft
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/validate
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/publish
GET  /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/history
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/rollback
GET  /api/admin/page-workbench/pages/{pageId}/snapshots
GET  /api/admin/page-workbench/pages/{pageId}/snapshots/{snapshotId}
POST /api/admin/page-workbench/pages/{pageId}/preview
POST /api/admin/page-workbench/pages/{pageId}/publish
POST /api/admin/page-workbench/pages/{pageId}/rollback
GET  /api/admin/pages
POST /api/admin/pages/bootstrap
GET  /api/admin/pages/{pageId}/authoring
GET  /api/admin/pages/{pageId}/sections/{slotKey}/editor
PATCH /api/admin/pages/{pageId}/sections/{slotKey}/editor/state
POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/draft
POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/validate
POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/publish
GET  /api/admin/pages/{pageId}/sections/{slotKey}/editor/history
POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/rollback
POST /api/admin/pages/{pageId}/sections/{slotKey}/draft
POST /api/admin/pages/{pageId}/preview
POST /api/admin/pages/{pageId}/publish
POST /api/admin/pages/{pageId}/rollback
```

For the page workbench section draft wrapper
`POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/draft`, do not assume that every
non-saved form state arrives as HTTP 400. Editor-form validation failures are returned as a normal response:

```ts
{
  saved: boolean;
  saveDraft: SaveDraftResult | null;
  diagnostics: {
    status: 'ok' | 'warning' | 'error';
    errorCount: number;
    warningCount: number;
    issues: Array<{
      severity: 'error' | 'warning';
      code: string;
      fieldPath: string;
      itemId?: string;
      field?: string;
      message: string;
    }>;
  } | null;
  compositeGroup: CompositeGroup | null;
  workbench: PageWorkbenchRowRefreshResponse;
}
```

If `saved: false`, no draft version was persisted and `saveDraft` is `null`; use `diagnostics.issues[]` to
highlight form fields. This covers composition errors and content validation errors. Page `price` drafts
reuse `global_price` validation, so readonly fields and invalid `items[]` come back as field-level
diagnostics. Missing page/slot, disabled sections, runtime slots, and other non-form failures remain HTTP
errors.

All write operations may send `x-cms-actor` until real CMS auth/session audit is wired.
Navigation and other user-aware endpoints should send one of the current identity headers:
`x-cms-user-id`, `x-cms-user-email`, or temporary develop-only `x-cms-actor`.

## Admin Navigation

Use:

```text
GET /api/admin/navigation?locale=uk
GET /api/admin/navigation?locale=uk&includeIndicators=true
```

This endpoint is the source for the left CMS menu. Do not build the whole sidebar by hardcoding separate
frontend lists. Backend groups navigation by domain and filters system/admin entries by the current user's
permissions. The menu is also the first-level attention map for the CMS: it should help an editor quickly
see where there are validation issues, unpublished/stale changes, and incomplete publication coverage.

The response contains `groups`:

- `practices`: the group itself is the clickable root for `practice_collection_page` ("Услуги"/services on
  the public site). It opens the page/workbench for the public list of all practices. Its `items` contain
  only the complete non-regional practice -> service -> problem page tree. Practice/service/problem child
  nodes open the matching generated page workbench. Regional page variants are not expanded in the left
  menu; they are shown inside the selected page workbench.
- `lawyer_pages`: generated public lawyer profile pages. This is separate from the lawyers reference
  dictionary: the menu item opens the page/workbench area for lawyer profile pages that should exist for
  visible lawyers, while `reference_data/lawyers` opens the ERP/CMS lawyer record editor.
- `publications`: content-like publication collections, initially articles, cases, and media mentions.
  This group opens publication lists, not operational queues. Queues such as "requires review" can be
  added later as a dashboard, not mixed into the content tree.
- `global_sections`: shared layout/global area. It contains versioned global sections
  `site_header`, `site_footer_practices`, `site_footer`, `global_price`, `global_achievements`,
  `global_lead_form`, and the non-versioned settings
  item `site_contact_settings`. The versioned sections are backed by `/api/admin/global-sections`.
  `site_contact_settings` is backed by `/api/admin/site-settings/contact`. The global price editor manages
  the upper shared source; concrete generated pages expose their own page `price` slot when the page is
  opened in the workbench.
- `reference_data`: editable CMS reference resources from ERP-owned source objects. The
  practice/service/problem dictionaries are represented by one `service_hierarchy` item, not by separate
  top-level `practices`, `services`, and `problems` items. Other regular items are lawyers, regions,
  offices, and reviews. Competencies are intentionally not exposed as a separate regular editor menu item.
- `single_pages`: fixed standalone pages, initially home, about, career, lawyer license, and contacts.
  Each node opens the matching page workbench.
- `users`: CMS users list. Role and permission management is intentionally not shown as a separate menu
  item until that workflow is implemented. Backend returns this group only for users with `users.read`
  permission, which currently means admin-level access.

For the first release-oriented slice, backend should return the full practice/service/problem tree in one
navigation response. This keeps the frontend simple and lets the menu work as a full CMS map. The endpoint
must still keep the payload lightweight: no full section content, no full diagnostics lists, and no page
version history in the menu response. If the tree becomes too heavy later, the same contract may grow a
lazy-loading mode without changing the meaning of menu nodes.

For the practices group, the frontend should render the group row itself as the services/practice
collection root. Use the group's own `route`, `target`, `endpoint`, and `indicators` for click/open and
stats. Then recursively render `group.items` as the practice/service/problem children. Do not render a
separate `practice_collection_page` item inside the group.

For practice/service/problem child nodes, `endpoint` now opens a source-scoped matrix:

```text
GET /api/admin/page-workbench/page-types/practice_page?locale=uk&sourceId=<practice-id>
GET /api/admin/page-workbench/page-types/service_page?locale=uk&sourceId=<service-id>
GET /api/admin/page-workbench/page-types/problem_page?locale=uk&sourceId=<problem-id>
```

Use this endpoint for the main screen after a sidebar click. It returns the usual `PageWorkbenchMatrixResponse`
with `columns`, `summary`, and `rows`, but only for the selected source: the base Ukraine-wide row plus
regional rows. The call is read-only and should not create missing pages. If a row has `page: null` and
`actions.canBootstrap: true`, show a create/bootstrap action instead of silently creating the page on click.
Use `response.scope` for the screen context:

```json
{
  "scope": {
    "kind": "generated_source",
    "source": {
      "id": "service-cms-id",
      "resource": "services",
      "title": "Divorce support",
      "sourceSlug": "divorce-support",
      "pagePath": "services/family-law/divorce-support",
      "publicPath": "/services/family-law/divorce-support",
      "diagnostics": []
    }
  }
}
```

For fixed page-type matrices `scope.kind` is `page_type` and `scope.source` is `null`. Do not derive the
currently opened practice/service/problem from `rows[0]`; rows are page variants, while `scope.source`
is the selected sidebar object.

### Central Service-Tree Workbench Screen

This is the main screen opened from the `practices` sidebar group. The frontend should treat it as a
matrix of page variants for one selected site object.

Click mapping:

- click the `practices` group row itself: call its returned `endpoint`, which opens
  `practice_collection_page` for the public services/practices collection;
- click a practice node: call
  `GET /api/admin/page-workbench/page-types/practice_page?locale=<locale>&sourceId=<practice-id>`;
- click a service node: call
  `GET /api/admin/page-workbench/page-types/service_page?locale=<locale>&sourceId=<service-id>`;
- click a problem node: call
  `GET /api/admin/page-workbench/page-types/problem_page?locale=<locale>&sourceId=<problem-id>`.

Screen title and context:

- use `response.scope.source.title` for practice/service/problem screens;
- use the page type title for `practice_collection_page`;
- use `response.scope.source.resource`, `sourceSlug`, `pagePath`, `publicPath`, and `diagnostics` for a
  small read-only context panel if needed;
- do not infer the opened object from regional rows.

Rows:

- `response.rows` contains page variants, not tree children;
- `row.kind === "base"` is the Ukraine-wide/non-regional page;
- `row.kind === "regional"` is one expected regional inheritor;
- regional rows are already filtered by backend through region qualifications, so the frontend should not
  add missing rows for every region from the region dictionary;
- if `row.page === null`, the CMS page does not exist yet;
- if `row.page !== null`, use `row.page.publishState`, `row.page.currentSnapshot`, and
  `row.page.sectionSummary` for compact row state.

Columns and cells:

- `response.columns` is the canonical slot order for the table header;
- `row.cells` are the actual cells for that row. Match cells to columns by `slotKey`;
- `cell.kind === "section"` is an editable/versioned CMS section summary;
- `cell.kind === "runtime"` is a read-only runtime/read-model slot;
- `cell.status`, `cell.diagnostics`, and `cell.actions` are backend-computed. The frontend should display
  them, not recalculate publishability locally;
- section cell content is intentionally absent. Open the editor endpoint to read draft/published content.

Actions:

- show buttons from `row.actions` and `cell.actions`;
- call URLs from `row.endpoints` and `cell.endpoints`;
- if an action flag is false or endpoint is `null`, hide/disable that action;
- for a not-created row, use `row.endpoints.bootstrap` exactly as returned. Regional bootstrap endpoints
  include `body.regionId`;
- after bootstrap/save/validate/publish/rollback/visibility changes, replace the affected row with
  `response.workbench.row` when the action response includes it;
- after actions that can change sidebar counters, reload
  `GET /api/admin/navigation?locale=<locale>&includeIndicators=true`.

Optional quick-open endpoints:

- `POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/open` creates/opens the generated
  page authoring state and returns `{ open, defaultEditorTarget, workbench }`;
- `POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/open-editor` does the same and
  also returns `editor` and `localeDiagnostics` for the backend-selected default section;
- do not use these endpoints for a normal sidebar click if the design expects a read-only matrix first.
  Use them only for explicit "open editor" / "create and edit" interactions.

Recommended central screen layout:

- top summary: `response.summary.errors`, `warnings`, `pagesNotCreated`, `pagesNotPublished`,
  `pagesDraftChanged`, `pagesRequireReview`;
- locale attention tabs: use `response.localeDiagnostics.locales`. The opened matrix remains scoped to
  `response.locale`; `response.rows` and `response.summary` describe only that locale. `localeDiagnostics`
  is a compact all-locale summary for quick orientation and switching, not three embedded matrices;
- first row group: base page;
- second row group: regional pages, using `row.region.title` and `row.regionSlug`;
- section grid: render cells in `response.columns` order;
- editor drawer/panel: opened through `cell.endpoints.editor`;
- page buttons: preview/publish/rollback/snapshots from `row.endpoints`;
- page creation button: bootstrap from `row.endpoints.bootstrap` when `row.page === null`.

Do not use `/api/admin/reference/...` endpoints to build this central page workbench. Reference endpoints
are for editing ERP/CMS dictionary objects. The page workbench is driven by
`/api/admin/page-workbench/page-types/...`.

The endpoint should return only menu items that can be opened now. Target-state items from the long-term
requirements may stay documented, but unfinished entries should not be returned as disabled/planned nodes
in the runtime menu. This keeps the CMS sidebar a working tool rather than a map of promises.

Indicators are optional and should be included only when requested:

- `GET /api/admin/navigation?locale=uk` may return the tree without stats;
- `GET /api/admin/navigation?locale=uk&includeIndicators=true` returns the same tree with lightweight
  `indicators`;
- the response includes `generatedAt`, an ISO timestamp showing when the backend assembled the menu and
  indicators;
- navigation indicators are intentionally summary-only. They are not the same thing as opening every
  workbench matrix: the backend does not attach full rows, locale diagnostics, runtime payload checks,
  section content, or history to the sidebar response;
- deep runtime-linked diagnostics remain on the selected matrix/editor screen. The sidebar can show enough
  counters to orient the editor, but it must not block CMS shell rendering on full matrix validation;
- the first implementation does not need backend menu filters such as `filter=errors` or
  `filter=attention`; if the frontend needs quick filters, it can derive them locally from the returned
  indicators.

Refresh policy for the sidebar:

- load navigation when the CMS shell opens;
- reload it after changing locale;
- reload it after successful save, publish, rollback, reference-data update, localization update,
  global-section/settings update, media change that affects diagnostics, or user-management change;
- optional background refresh is allowed every 60-120 seconds while the tab is active;
- do not reload navigation on every render, hover, or input keystroke;
- when replacing the tree after refresh, preserve expanded menu keys, selected node, and scroll position.

Each item can include:

- `route`: frontend route to open;
- `target`: typed backend-owned instruction for what the UI should open, for example
  `page_workbench`, `publication_list`, `global_section_editor`, `reference_list`, `single_page_workbench`,
  or `users_list`;
- `endpoint`: backend endpoint that should be used to load the main data for that menu item, when it is
  useful to expose directly;
- `children`: nested entries, for example the service tree page collections;
- `source`: source object identity for generated tree nodes. This is not an indicator and should be read
  from the item root, not from `indicators`;
- `indicators`: optional lightweight stats for the menu/statistical addon.

For clickable root groups such as `practices`, the group can include the same `route`, `target`, and
`endpoint` fields as an item. Planned/unopenable nodes should normally be omitted from the response.
The `availability` field is intentionally not part of the current navigation contract.

Example menu item:

```json
{
  "key": "practice:10",
  "title": "Військовий адвокат",
  "source": {
    "resource": "practices",
    "id": "practice-cms-id",
    "externalId": "10"
  },
  "target": {
    "kind": "page_workbench",
    "pageType": "practice_page",
    "sourceId": "practice-cms-id"
  },
  "children": [],
  "indicators": {
    "diagnostics": {
      "own": { "errors": 0, "warnings": 2 },
      "regional": { "errors": 1, "warnings": 4 },
      "children": { "errors": 0, "warnings": 38 }
    },
    "attention": {
      "own": {
        "stale": true,
        "reasons": {
          "draftChanges": true,
          "staleDependencies": false
        }
      },
      "regional": { "staleCount": 3 },
      "children": { "staleCount": 6 }
    },
    "publication": {
      "own": {
        "published": true
      },
      "regional": {
        "publishedCount": 15,
        "totalCount": 17
      },
      "children": {
        "publishedCount": 200,
        "totalCount": 1329
      }
    }
  }
}
```

`diagnostics.own` means errors/warnings for the base non-regional page of the current node.
`diagnostics.regional` means regional inheritors of the same node only. `diagnostics.children` means child
practice/service/problem nodes below this node, including their regional inheritors where relevant. If the
node has no child page nodes, `diagnostics.children` is `null`.

For menu display, `attention` intentionally combines draft changes and stale dependencies into one
editor-facing signal: "this node needs attention". For the sidebar:

```text
attention.own.stale = attention.own.reasons.draftChanges OR attention.own.reasons.staleDependencies
```

Internally backend must keep draft and stale states separate, because they require different publish/review
behavior. The menu aggregate may expose reasons so the frontend can show a tooltip or details, but the
primary sidebar signal should stay simple. Regional and children attention scopes use only `staleCount`.

`publication` is a short coverage counter. For practice/service/problem nodes it should help show how many
base, regional, and descendant pages are already published from the expected total:

- `publication.own.published`: whether the base non-regional page for this node is currently published;
- `publication.regional.publishedCount/totalCount`: regional variants only for the same node. Use this
  for the "regional inheritors published from all enabled regions" column;
- `publication.children.publishedCount/totalCount`: child service/problem pages below this node, including
  their regional variants where they exist. If the node has no child page nodes, `publication.children` is
  `null`.

Regional totals must include only expected regional pages: visible regions where the node is applicable by
the region competence model. Disabled regions and non-applicable region/node pairs do not count as missing
pages. Children totals must likewise include only visible/applicable ERP objects and expected regional
inheritors.

Sidebar formulas for the statistical addon:

- errors: `diagnostics.own.errors`, with regional/children values shown separately or combined visually in
  brackets by the frontend;
- warnings: `diagnostics.own.warnings`, with regional/children values shown separately or combined visually
  in brackets by the frontend;
- stale marker: `attention.own.stale`, plus `attention.regional.staleCount` and
  `attention.children.staleCount` where present;
- own published state: `publication.own.published`;
- children published ratio: if `publication.children.totalCount > 0`, show
  `publication.children.publishedCount/publication.children.totalCount`;
- regional ratio for practice/service/problem nodes: if `publication.regional.totalCount > 0`, show
  `publication.regional.publishedCount/publication.regional.totalCount`.

The navigation API should not return `status`, `availability`, `publication.*.notCreatedCount`, or
`publication.*.notPublishedCount` for the practice tree. The frontend derives row color/priority from
errors, warnings, and attention values. Detailed reasons for missing publication belong to the opened page
workbench, not to the menu.

Group-specific indicator rules:

- `global_sections`: use `diagnostics.own`, `attention.own`, `publication.own`, and `publishImpact`.
  `publishImpact.affectedPages.count` and `publishImpact.affectedBindings.count` count only pages/bindings
  whose public snapshot would actually change after publishing the global section. For `global_price`, count
  pages using inherit/append or field-level inherit/append; do not count full override, fully independent
  overridden fields, or disabled price sections. For `global_achievements` and `global_lead_form`, count
  pages whose inherited page slot depends on the global source. For `site_header`, `site_footer_practices`,
  and `site_footer`, snapshot impact should be zero/empty because they are layout payload sources, not page
  snapshot section refs.
- `reference_data`: the group itself uses simple aggregate `diagnostics.own.errors/warnings` and
  `records.visibleCount/totalCount`. The `service_hierarchy` item uses `own/children` scopes for
  diagnostics and records. Do not add a separate `attention` layer for dictionaries; the frontend can treat
  non-zero diagnostics as the signal.
- `single_pages`: use `diagnostics.own`, `attention.own`, and `publication.own`. If a single page later
  becomes regional, include `publication.regional`; otherwise omit it.
- `lawyer_pages`: use the same generated-page indicator model as other generated collections, but without
  practice/service/problem descendants. The expected total is driven by visible lawyers that should be
  shown on the public site.
- `users`: use `users.activeCount/totalCount` for the first implementation. More user states such as
  pending invites, locked users, or missing roles belong to the later user/permissions workflow.

### Reference Data Hierarchy

The `reference_data` group contains one hierarchy item for the practice/service/problem dictionaries:

```json
{
  "key": "service_hierarchy",
  "title": "Иерархия услуг",
  "kind": "reference_tree_root",
  "route": "/reference/service-hierarchy",
  "target": {
    "kind": "reference_list",
    "referenceResource": "practices"
  },
  "endpoint": {
    "method": "GET",
    "path": "/api/admin/reference/practices"
  },
  "indicators": {
    "diagnostics": {
      "own": { "errors": 2, "warnings": 5 },
      "children": { "errors": 10, "warnings": 35 }
    },
    "records": {
      "own": { "visibleCount": 8, "totalCount": 10 },
      "children": { "visibleCount": 112, "totalCount": 170 }
    }
  },
  "children": []
}
```

This root opens the central screen with the list of all practices. It also contains the full sidebar tree
down to service nodes:

```text
Иерархия услуг -> central list of practices
  Practice -> central list of this practice services
    Service -> central list of this service problems
```

Problems are not rendered as left-menu nodes. They are edited only in the central screen after selecting a
service. Clicking a menu node changes the central screen context; it does not open object detail directly.
Object detail/editing belongs to the central list/table UI.

Practice node example:

```json
{
  "key": "reference:practice:practice-id",
  "title": "Військовий адвокат",
  "kind": "reference_tree_node",
  "source": {
    "resource": "practices",
    "id": "practice-id",
    "externalId": "10"
  },
  "flags": {
    "showOnSite": false
  },
  "target": {
    "kind": "reference_children_list",
    "parentResource": "practices",
    "parentId": "practice-id",
    "childrenResource": "services"
  },
  "endpoint": {
    "method": "GET",
    "path": "/api/admin/reference/services?parentPracticeId=practice-id"
  },
  "indicators": {
    "diagnostics": {
      "own": { "errors": 0, "warnings": 1 },
      "children": { "errors": 3, "warnings": 12 }
    },
    "records": {
      "own": { "visibleCount": 0, "totalCount": 1 },
      "children": { "visibleCount": 20, "totalCount": 31 }
    }
  },
  "children": []
}
```

Service node example:

```json
{
  "key": "reference:service:service-id",
  "title": "Оскарження рішення ВЛК",
  "kind": "reference_tree_node",
  "source": {
    "resource": "services",
    "id": "service-id",
    "externalId": "25"
  },
  "flags": {
    "showOnSite": true
  },
  "target": {
    "kind": "reference_children_list",
    "parentResource": "services",
    "parentId": "service-id",
    "childrenResource": "problems"
  },
  "endpoint": {
    "method": "GET",
    "path": "/api/admin/reference/problems?parentServiceId=service-id"
  },
  "children": []
}
```

Use CMS record IDs in `parentPracticeId` and `parentServiceId`, not ERP external IDs. ERP IDs remain in
`source.externalId` for display/debugging.

The tree intentionally includes objects with `show_on_site = false`. Use `flags.showOnSite` to render them
as disabled/muted, but keep them expandable. `records.visibleCount` counts only `show_on_site = true`;
`records.totalCount` counts all records. If a disabled parent has enabled children, backend reports a
warning and still returns the children.

Current backend implementation note:

- `lawyer_pages`, `single_pages`, `global_sections`, `reference_data`, and `users` can now return menu
  indicators when `includeIndicators=true`;
- reference dictionary indicators are intentionally aggregate-only and do not return full diagnostic lists;
- global section impact is a lightweight count, not a page rebuild plan. Open the global section editor or
  page workbench for detailed actions.

Important: `GET /api/admin/page-workbench/tree` remains the page-type workbench tree, not the whole CMS
sidebar. Use `/api/admin/navigation?locale=uk&includeIndicators=true` for the sidebar entry points and the
practice/service/problem hierarchy with menu indicators. `GET /api/admin/page-workbench/service-tree`
remains a lower-level helper for the service tree without the full CMS sidebar groups.

Do not build the practice/service/problem sidebar from `/api/admin/reference/problems` or other reference
list endpoints. The sidebar hierarchy itself comes from `/api/admin/navigation`. Reference endpoints are
used after the editor opens an ERP-data context, including the hierarchy contexts
`/api/admin/reference/services?parentPracticeId=...` and
`/api/admin/reference/problems?parentServiceId=...`.

Reference-data detail/list responses may expose nested lightweight summaries for dictionary editing. For
example, a practice record can include `children.services[]`, and a service summary inside that list can
include `children.problems[]`. This is a convenience for reference screens only. The main CMS sidebar
still uses `/api/admin/navigation`.

## Global Sections

Use:

```text
GET  /api/admin/global-sections?locale=uk
GET  /api/admin/global-sections/{sectionKey}/locale-diagnostics
GET  /api/admin/global-sections/{sectionKey}/editor?locale=uk
GET  /api/admin/global-sections/{sectionKey}/public-content?locale=uk
POST /api/admin/global-sections/{sectionKey}/draft?locale=uk
POST /api/admin/global-sections/{sectionKey}/validate?locale=uk
POST /api/admin/global-sections/{sectionKey}/publish?locale=uk
GET  /api/admin/global-sections/{sectionKey}/history?locale=uk&limit=50&offset=0
POST /api/admin/global-sections/{sectionKey}/rollback?locale=uk
```

`POST /api/admin/global-sections/{sectionKey}/validate?locale=...` has two modes:

- stored-version mode: send `{ "sectionVersionId": "...", "recordDiagnostics": true }` or an empty
  body to validate the latest draft. This can record diagnostics for the stored version and returns a
  fresh `editor`;
- unsaved-form mode: send `{ "content": { ... } }`, where `content` has the same shape as the
  `/draft` request body. This validates the current form in memory, returns `validation`,
  `diagnostics`, and normalized `workingContent`, but returns `editor: null` and does not create a
  draft/version/history row.

Do not send `content` together with `sectionVersionId`. `recordDiagnostics: true` is also forbidden with
`content`, because there is no stored version to attach diagnostics to.

For global sections, `actions.canValidate` means that the section editor supports validation. It may be
`true` even when no draft exists yet, because the frontend can validate unsaved `content`.

Supported editable section keys now:

- `site_header`;
- `site_footer_practices` as a read-only/global diagnostics workbench;
- `site_footer`;
- `global_price`;
- `global_achievements`;
- `global_lead_form`.

`site_header` is the layout-level header/menu source. Its first editable content contract is
`{ searchEnabled: boolean, contactButtonEnabled: boolean }`. System navigation, the about dropdown,
the services mega menu, phone, work time, language policy, and mobile layout are read-only/runtime data.
It is not part of any page authoring section list.

Preferred startup endpoint for the dedicated header screen:

```text
GET /api/admin/site-layout/header-workbench?locale=uk&historyLimit=20&historyOffset=0
```

Use it when the user clicks `site_header` in the CMS sidebar. It returns the
normal `site_header` editor response, the current admin layout preview for the
header, current published header content, contact settings, version history,
grouped diagnostics, and exact action endpoints. This lets the screen render
the editable flags, read-only navigation/services menu, phone/work-time panel,
history list, and "current site" comparison state without manually stitching
several initial requests together.

When opening `GET /api/admin/global-sections/site_header/editor?locale=uk`, use:

- `editableContent` for the form values that may be saved back to
  `POST /api/admin/global-sections/site_header/draft?locale=uk`;
- `readonlyContent.navigation`, `readonlyContent.aboutDropdown`, and
  `readonlyContent.servicesMenu` to explain/show the read-only header contract;
- `readonlyContent.layoutPreview.endpoint` to refresh the full admin layout preview after draft changes;
- `readonlyContent.contactSettings.endpoint` and `readonlyContent.contactSettings.target` to open the
  separate contact settings editor for phone/work-time fields.

The header editor should not save phone/work-time values through the global section draft endpoint.
Those values belong to `site_contact_settings`.

In the workbench response:

- save only the object referenced by `workbench.editableSource`, currently
  `section.editableContent`;
- display navigation from `layoutPreview.header.navigation`;
- display services mega menu from `layoutPreview.header.servicesMenu.items`;
- display phone/work time from `contactSettings.settings`;
- display current published header content from `publishedContent.workingContent`
  when the design needs a "current site" comparison;
- show screen indicators from `diagnostics.header`, `diagnostics.navigation`,
  `diagnostics.servicesMenu`, and `diagnostics.contactSettings`;
- use `endpoints.*` for save/validate/publish/history/rollback/contact settings
  rather than hardcoding URLs in the component.

After header actions, use the same simple refresh rule as the footer screen:

- call the action endpoint from `endpoints.*`;
- process the immediate result and show operation diagnostics/messages;
- then call `workbench.refreshAfterActions.path` and replace the whole screen state with the returned
  workbench payload.

`workbench.refreshAfterActions.appliesTo` lists the action keys that should trigger this reload:
`saveDraft`, `validateDraft`, `publishDraft`, `rollback`, `draftFromVersion`, and `contactSettings`.

`POST /api/admin/global-sections/site_header/validate?locale=uk` returns both:

- `validation`: blocking validation result suitable for operation result state;
- `diagnostics`: header-specific diagnostics for visible form indicators.

For display, an empty/legacy `site_header` may be shown with backend defaults
`searchEnabled: true` and `contactButtonEnabled: true`. This does not weaken saving:
when the frontend creates or updates a draft, it must submit both boolean fields explicitly.

`site_footer` and `site_footer_practices` are layout-level footer sources. They are exposed through the
global section workbench for authoring/diagnostics and through public layout payload for frontend
rendering. Their detailed first-release contract is fixed in `docs/site-footer-section-workbench.md` and
`docs/site-layout-and-header-requirements.md`.

For the footer screen:

- prefer the screen-level startup endpoint
  `GET /api/admin/site-layout/footer-workbench?locale=uk&historyLimit=20&historyOffset=0`;
- practices in the footer are not edited through `site_footer`; they are a separate read-only/runtime
  powered global section `site_footer_practices`, built from practice reference data;
- `site_footer_practices` shows all active practices that have a locale `menuTitle` and public route;
  missing `menuTitle` or route omits the practice and adds a warning;
- `site_footer` edits only footer-owned settings for now: social URLs and legal PDF media refs;
- `site_footer.localeScope` is `shared`: those fields use one draft, published version, and history for all
  languages; `site_footer_practices` remains localized;
- public phone and work time are read from `site_contact_settings`, not from `site_footer`;
- allowed social network types and order are code-owned; the editor changes only URLs, and an empty URL
  hides the social network without warning;
- privacy/offer legal documents are uploaded through the media contour as PDF files up to 5 MB; missing
  document refs are warnings and invalid media refs are errors;
- first-level navigation links, contact label, legal link labels, sitemap route, and copyright are shown
  as read-only/code-owned;
- `site_contact_settings` is a simple settings API, not a draft/publish section.

The footer workbench response contains the initial data for the whole screen:

- `footerSection`: render editable form values from `footerSection.editableContent`;
- `footerPracticesSection`: render the read-only upper practice list preview from
  `footerPracticesSection.workingContent`;
- `footerPublishedContent`: render the lower-footer "current site" comparison from
  `footerPublishedContent.workingContent`;
- `footerPracticesPublishedContent`: render the practice-footer "current site" comparison from
  `footerPracticesPublishedContent.workingContent`;
- `layoutPreview.footer`: render/check the combined footer payload that the public layout would use in
  admin preview mode;
- `contactSettings.settings`: show phone/work-time as read-only footer context and link to the separate
  contact settings editor when needed;
- `mediaPolicy`: use PDF mime/size rules and media endpoints for privacy policy / offer contract picker;
- `history`: render the footer version/history panel;
- `diagnostics.footer`, `diagnostics.footerPractices`, and `diagnostics.contactSettings`: render screen
  badges and warnings;
- `endpoints.*`: use backend-provided URLs for save, validate, publish, rollback, history, media, layout
  preview, and contact settings actions.

When saving the footer draft from the workbench screen, send only the object referenced by
`workbench.editableSource`, currently `footerSection.editableContent`, to
`endpoints.footerSaveDraft.path`. Do not send `footerPracticesSection`, `layoutPreview`,
`contactSettings`, or `mediaPolicy` as footer content.

After footer actions, prefer a simple full workbench refresh instead of stitching partial responses:

- call the action endpoint from `endpoints.*`;
- process the immediate result and show operation diagnostics/messages;
- then call `workbench.refreshAfterActions.path` and replace the whole screen state with the returned
  workbench payload.

`workbench.refreshAfterActions.appliesTo` lists the action keys that should trigger this reload:
`footerSaveDraft`, `footerValidateDraft`, `footerPublishDraft`, `footerRollback`,
`footerDraftFromVersion`, `contactSettings`, and `mediaUpload`.

`POST /api/admin/global-sections/site_footer/validate?locale=uk` returns both:

- `validation`: blocking publish/save validation result suitable for operation result state;
- `diagnostics`: footer-specific diagnostics including social URL errors and legal PDF warnings/errors.

Use `diagnostics` for the visible footer form indicators. Missing privacy/offer PDFs are warnings. Invalid
social URLs or invalid/missing selected media records are errors.

When opening `GET /api/admin/global-sections/site_footer_practices/editor?locale=uk`, use:

- `workingContent.title` and `workingContent.items` for the read-only footer practice preview;
- `diagnostics` for omitted practices, missing `menuTitle`, or missing route/slug warnings;
- `readonlyContent.practiceSource` to show where the list comes from;
- `readonlyContent.layoutPreview.endpoint` to refresh the full layout preview.

The frontend must not send draft/save/publish actions for `site_footer_practices`; its `actions.canSaveDraft`
is false.

When opening `GET /api/admin/global-sections/site_footer/editor?locale=uk`, use:

- `localeScope` to determine whether locale tabs represent independent editable lifecycles; for
  `site_footer` it is `shared`;
- `editableContent.socialUrls` for social links;
- `editableContent.legalDocuments.privacyPolicyMediaId`;
- `editableContent.legalDocuments.offerContractMediaId`;
- `readonlyContent.legalDocumentsPolicy` for the legal PDF media picker/upload constraints;
- `readonlyContent.contactSettings.endpoint` and `readonlyContent.contactSettings.target` to open the
  separate contact settings editor when the user wants to change phone/work-time;
- `readonlyContent.layoutPreview.endpoint` to refresh the full admin layout preview after draft changes.

The footer editor should save only the `site_footer` editable content through
`POST /api/admin/global-sections/site_footer/draft?locale=uk`. Phone/work-time values belong to
`site_contact_settings`, and footer practices belong to `site_footer_practices`.

The locale query remains part of the endpoint because the response also contains localized read-only
labels and preview routes. Saving through `uk`, `ru`, or `en` changes the same shared footer section. The
frontend must therefore show one footer history/state rather than three independent drafts. A returned
physical `section.locale` of `uk` is the canonical storage locale and is not a locale mismatch.

`global_price` uses the same global section lifecycle, but its detailed workbench contract is fixed in
`docs/global-price-section-workbench.md`.

For the global price screen:

- the backend persists only editable content: `{ "items": [...] }`;
- the top section header (`title`, `accentText`, `description`) is read-only content from backend registry
  for the active locale;
- editor responses should expose `readonlyContent`, `editableContent`, and full `workingContent`;
- draft save accepts only `{ content: { items } }` and returns `saved: true | false` with diagnostics;
- per-card apply buttons are local UI state only; backend persistence happens through the global draft
  save action;
- publishing is triggered from the history action for `latest_draft`, and publish response contains
  affected snapshot rebuild results.

The editor response includes `schema.fields`. Use it as the current backend contract for required fields
and simple field shapes. For `global_price`, use the dedicated workbench contract above because it adds
read-only header content, item-level diagnostics, computed working content, and history actions.

Generated `practice_page`, `service_page`, and `problem_page` schemas expose a page
`price` slot. This slot is not edited through the global section screen. It is a page-owned section with
`sourcePolicy: "price_inheritance"`:

- base non-regional generated pages source their page `price` from the locale-specific `global_price`;
- regional generated pages source their page `price` from the matching base non-regional page price
  section;
- the page `price` may inherit the source and may locally override/append only fields allowed by
  `slot.fieldPolicies`;
- the canonical page price payload is `title`, `accentText`, `description`, and `items`. The first three
  fields are hydrated from the locale-specific `global_price` registry and are exposed as inherit-only.
  Only `items` may use `inherit`, `override`, or `append`;
- `lead` and `notes` are not part of the `global_price` contract. Page-specific price copy belongs to the
  separate `practice_price_text` or `service_price_text` section. Do not submit system price header fields
  as local editable content;
- page editor `content.source` and `content.resolved.*` include the hydrated system header even though the
  persisted global section version stores only editable `{ items }`;
- inherited price local drafts are partial deltas. If `items` inherit from the source, the save request
  does not need to include local `items`; backend validates the composed resolved content;
- public snapshots store the resolved price payload and keep separate source/local section refs for
  diagnostics and rollback.

On page publish, a base non-regional generated page may create a local published `price` version even when
the editor did not save a local price draft. This happens when the page price fully inherits from
`global_price`: backend materializes the resolved inherited price as the base page's own published price
layer, so regional pages can inherit from that concrete base version. In `publish.withPageSectionCommits`,
this case has `draftVersionId: null` and `sourceSectionVersionId` set to the upstream published version.

Preview does not materialize that local version. If the page has no local price draft/published version yet,
backend composes the source content and returns it with a virtual page-owned section provenance for preview
only. The frontend should treat this as renderable preview content, not as a saved local section version.

This means the global price screen edits the shared source, while the page section editor edits the local
page/regional layer. Header/footer remain direct shared globals and do not create page-local section
versions.

Generated `practice_page`, `service_page`, and `problem_page` schemas also expose two required inherited
global content slots:

- `achievements_strip`, `sectionType: "global_achievements"`,
  `sourcePolicy: "global_section_inheritance"`, `globalSectionKey: "global_achievements"`;
- `lead_form`, `sectionType: "global_lead_form"`,
  `sourcePolicy: "global_section_inheritance"`, `globalSectionKey: "global_lead_form"`.

Base non-regional generated pages source these slots from the locale global section. Regional generated
pages source them from the matching base page local section. `achievements_strip` is inherit-only at the
page layer. `lead_form` is also page-level read-only for the current implementation pass: it inherits the
global/base content and can be opened for diagnostics/history, but page editors must not show save,
override, append, disable, or drag/reorder UI for it. `practice_collection_page`
intentionally does not expose either slot. `lead_form` is CMS-authored form content; `lead_capture`
remains the read-only runtime context for the actual lead form behavior.

`global_lead_form` does not own phone numbers. Do not render or submit `content.phones` for this global
section. Phone display must come from the single global contact/settings source used by the site, not from
individual lead form versions.

For `global_achievements.items[].sourceLogo` uploads, use media owner context:

```json
{
  "ownerResource": "global_sections",
  "ownerId": "global_achievements"
}
```

The backend still tolerates ownerless legacy media, but media owned by another resource is diagnosed on the
achievements section.

Price preview modes are intentionally separate:

- `latest_draft` preview composes the latest available source draft/published version with the latest
  available local draft/published version;
- `published` preview composes only the current published source and local versions, even if newer drafts
  already exist.

The public snapshot/publish path uses the same backend composition rule as `published` preview: the
snapshot stores only the resolved price payload, while section refs keep the exact source/local versions
that produced it.

Regional inherited CMS text sections may expose locked section headings. The backend marks these fields in
schema/editor payloads as `semanticRole: "section_heading"` and `regionalInheritanceLocked: true`. In
regional editors, do not offer `override` or `append` for such fields; keep them inherited from the
base/global source. The backend also rejects saves where a regional composition would effectively override a
locked heading, including whole-section `strategy: "override"` without an explicit `title: inherit`.

Page section validation now has a first practice-specific hard-error layer. The editor may save incomplete
drafts, but `validate` records blocking `publish_validation` errors for empty enabled structured sections
such as `practice_actions`, `practice_faq`, and `lead_questionnaire`; workbench readiness then blocks page
publish through the existing section validation diagnostics. Warning-grade quality checks are still a later
backend pass.

Global sections declare `localeScope` in list, diagnostics, editor, public-content, and history responses.
Most global sections are `localized`: `uk`, `ru`, and `en` have separate records and histories.
`site_footer` is `shared`: every requested locale reads and writes one footer lifecycle. The requested
locale still controls localized read-only/runtime decoration in the response.

When a global section screen needs tab/header indicators for all locales, use the lightweight diagnostics
endpoint instead of loading three full editors:

```http
GET /api/admin/global-sections/{sectionKey}/locale-diagnostics
```

It returns `locales[]` for `uk`, `ru`, and `en`, each with `status`, `facts`, and `diagnostics`.
Use the full editor endpoint only for the currently opened locale form.
For a shared section, locale entries intentionally describe the same underlying section/version state;
do not render them as three independently editable footer versions.

When the screen needs to compare the edited draft with what is currently active for public rendering, use:

```http
GET /api/admin/global-sections/{sectionKey}/public-content?locale=uk
```

This returns only the current published version merged with backend-owned readonly/runtime data:

```ts
{
  sectionKey:
    | 'global_price'
    | 'global_achievements'
    | 'global_lead_form'
    | 'site_header'
    | 'site_footer_practices'
    | 'site_footer';
  locale: 'uk' | 'ru' | 'en';
  localeScope: 'localized' | 'shared';
  publishedVersion: SectionVersion | null;
  readonlyContent: object | null;
  editableContent: object;
  workingContent: object;
  diagnostics: Diagnostics | null;
}
```

Do not use this endpoint as the editing form source. The editor form still comes from
`GET /api/admin/global-sections/{sectionKey}/editor?locale=...`. Use `public-content` for "current site"
preview/comparison panels, published-state checks, and layout-level public payload debugging. Dedicated
header/footer workbench startup responses already include the relevant published-content blocks, so the
frontend normally does not need an extra initial request for those screens.

Save draft:

```json
{
  "content": {
    "socialUrls": {
      "telegram": "https://t.me/example",
      "youtube": null,
      "instagram": null,
      "facebook": null,
      "whatsapp": null
    },
    "legalDocuments": {
      "privacyPolicyMediaId": null,
      "offerContractMediaId": null
    }
  }
}
```

Validate and publish may omit `sectionVersionId`; backend then uses the latest draft:

```json
{}
```

Publishing `site_header`, `site_footer_practices`, or `site_footer` creates the new published global
section version but does not rebuild page snapshots. These are layout-level sources, so frontend preview
and public rendering read them through the layout payload.

Publishing `global_price`, `global_achievements`, or `global_lead_form` uses affected page snapshot
rebuild: backend creates the new published global source and plans/rebuilds affected page snapshots without
touching unrelated page-owned draft sections.

The publish response contains:

- `publish.publishedVersionId`: the new published section version;
- `publish.affectedPages`: pages that depend on this global section; for layout globals this may be empty;
- `publish.affectedBindings`: exact page-section bindings affected by the new section version; for layout
  globals this may be empty;
- `publish.rebuiltSnapshots`: rebuild result per affected page, with `status = rebuilt | skipped | failed`;
  for layout globals this may be empty;
- `editor`: fresh global-section editor state after publish.

For the UI this means: show publish success from `publishedVersionId`. Show rebuild impact from
`rebuiltSnapshots` only when the section actually uses snapshot rebuild, currently `global_price`,
`global_achievements`, and `global_lead_form`.
For `site_header`/`site_footer_practices`/`site_footer`, the important follow-up is layout preview/public
layout refresh, not page workbench rebuild.

For inherited global page slots, affected rebuilds apply to pages that directly depend on the global
source, normally the base non-regional generated pages. Regional pages depend on the matching base page
local layer and should be reviewed/republished through the regional page workflow when that layer changes.

All mutation responses return a fresh `editor` object. Use it to replace the current editor state after
save, validate, publish, or rollback.

## Basic Flow

1. Load page schemas/meta.
2. Load the page workbench tree.
3. Open a page type workbench matrix.
4. Bootstrap or open a concrete page from the selected row.
5. Render `authoring.page`, editable `authoring.sections`, and read-only `authoring.runtimeSlots`.
6. Open a concrete section through the workbench section editor endpoint.
7. Save/validate/publish that section through the workbench section action endpoints.
8. Build preview through the workbench page action endpoint.
9. Publish a page through the workbench page action endpoint.
10. Rollback through the workbench page action endpoint when needed.

The frontend must not reconstruct publish rules. Backend decides what can be saved, previewed, published,
or rolled back.

## Page Schemas

Use:

```text
GET /api/admin/page-schemas
GET /api/admin/page-schemas/{pageType}
```

This is the UI metadata source for page authoring. It returns:

- registered `pageTypes`;
- supported `locales`;
- route template and route params;
- whether regional routes are supported;
- whether the body allows editor-added sections;
- fixed section slots;
- runtime slots;
- section fields and required/optional state;
- section ownership/publish/composition rules needed to decide which controls to show.
- optional `sourcePolicy` for special source resolution. Current values are `price_inheritance` and
  `global_section_inheritance`.

The frontend should use this endpoint to build page creation forms and section editors. Do not hardcode
the available page types, slots, route params, or field lists in the frontend.

## Page Workbench

Use:

```text
GET /api/admin/page-workbench/tree?locale=uk
GET /api/admin/page-workbench/service-tree?locale=uk
GET /api/admin/page-workbench/page-types/{pageType}?locale=uk
GET /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/row?locale=uk
GET /api/admin/page-workbench/pages/{pageId}/row
GET /api/admin/page-workbench/pages/{pageId}/history?limit=50&offset=0
POST /api/admin/page-workbench/bulk-publish/plan
POST /api/admin/page-workbench/bulk-publish
POST /api/admin/page-workbench/pages/bootstrap
POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/open?locale=uk
POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/open-editor?locale=uk
GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor
GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/inspect
PATCH /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/state
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/draft
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/validate
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/publish
GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/history
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/rollback
GET /api/admin/page-workbench/pages/{pageId}/snapshots?limit=50&offset=0
GET /api/admin/page-workbench/pages/{pageId}/snapshots/{snapshotId}
POST /api/admin/page-workbench/pages/{pageId}/preview
POST /api/admin/page-workbench/pages/{pageId}/publish
POST /api/admin/page-workbench/pages/{pageId}/rollback
```

This is the source for the main page workbench screen: left tree plus section matrix. It is intentionally
summary-only and must not replace the section editor.

`GET /tree` returns page groups and page-type nodes:

- fixed page types already supported by the workbench: `contacts_page`, `lawyers_page`;
- generated collections: `practice_page`, `service_page`, `problem_page`, and `lawyer_page`;
- `practice_page`, `service_page`, and `problem_page` already return generated matrix rows from CMS
  reference data; `lawyer_page` is still visible as a generated collection but not fully matrix-managed yet;
- `variantMode`: `single`, `regional`, or `generated_collection`;
- `createdCount` and high-level summary counters for badges.

`GET /service-tree` returns the real service-tree hierarchy for the left page workbench area:

```text
GET /api/admin/page-workbench/service-tree?locale=uk
```

The response has a collection root plus practice nodes:

- `collection`: the `practice_collection_page` root ("services"/"all practices" public page);
- `collection.children`: practice nodes;
- practice node children: service nodes;
- service node children: problem nodes;
- `nodes`: the top-level practice nodes kept as a backward-compatible shortcut. New sidebar/workbench UI
  code should prefer `collection`.

Each node contains:

- `sourceRecord`: the CMS reference object that drives the generated page;
- `page`: existing CMS page state, or `null` when the page is not created yet;
- `diagnostics`: source/page blockers and warnings;
- `actions.canOpen`: open the page workbench/editor when `page` exists;
- `actions.canBootstrap`: create the CMS page from this source object when backend says it is safe.

Use this endpoint for the tree-like left UI where practices contain services and services contain
problems. This tree intentionally does not expand regional variants. Use `GET /page-types/{pageType}` when
the user opens a matrix/table for one page type and needs base/regional page rows.

`GET /page-types/{pageType}` returns:

- `columns`: fixed section/runtime slots from the backend page schema;
- `columns[].compositeGroupKey`: optional key telling the UI that several columns belong to one visual
  block, for example editable CMS block settings plus a runtime list from reference data;
- `rows[].compositeGroups`: backend-built UI grouping for cells that share `compositeGroupKey`. This is
  the preferred contract for rendering one editor-facing visual section from several technical cells. It
  does not merge section lifecycles or replace `cells`; it only tells the UI which cells belong together,
  which member is the `primarySlotKey`, which members are editable/readonly/runtime, the aggregated
  diagnostics, and the primary editor endpoints/actions for the group;
- `rows[].compositeGroups[].endpoints.editor`: open this endpoint for a composite visual section. It points
  to the group's primary editable section. The editor response now includes a top-level `compositeGroup`
  with full member context for that visual section;
- runtime cells without an editor endpoint must not be opened directly. They return
  `actions.canOpen: false` and `endpoints.editor: null`; when runtime data belongs to a composite visual
  section, open the matching `rows[].compositeGroups[].endpoints.editor` instead;
- section columns may include `defaultVisibility: "enabled" | "disabled"`. This is the backend contract for
  bootstrap defaults. Do not infer default visibility only from `required`/`canDisable`; for example
  `practice_intro_text` and `practice_actions` are optional and disableable but default to enabled;
- `rows`: concrete page variants for the selected locale;
- `rows[].pagePath` and `rows[].publicPath`: backend-computed route fields for the row. For existing
  pages they mirror `row.page.pagePath` / `row.page.publicPath`; for not-created generated rows they show
  the route that will be used after bootstrap. They may be `null` only when the row is not route-ready;
- for generated service-tree rows, `sourceRecord`: the source practice/service/problem record that drives
  the row and route;
- for generated regional rows, `region` and `regionSlug`: the CMS region source used to build the
  regional route;
- row-level `actions`: whether the UI can open, bootstrap, preview, publish, rollback, or view the
  current snapshot for the page;
- row-level `endpoints`: backend-owned action URLs for the row. Use them together with `actions`; if an
  action is not available, the matching endpoint is `null`;
- row-level `readiness`: action-specific explanations for `preview` and `publish`. Use
  `row.readiness.preview.ready` / `row.readiness.publish.ready` as the detailed state behind the button
  and show `row.readiness.*.reasons` in tooltips, disabled-state messages, or page banners. Warnings may
  appear in `reasons` without disabling the action; critical reasons are the blockers;
- row-level `diagnostics`: publish blockers and warnings for the whole page;
- `cells`: one summary cell per section/runtime slot;
- `summary`: counters for the whole opened matrix. `summary.errors` and `summary.warnings` are row-level
  counters, so page diagnostics such as `PAGE_NOT_CREATED` are included, not only section cell diagnostics.
- `localeDiagnostics`: counters for the same matrix scope across all public locales. For source-scoped
  screens, the backend preserves the opened `sourceId` for every locale. Use `localeDiagnostics.locales[]`
  for the UA/RU/EN attention badges and `item.endpoint` to switch locale; do not fetch three full matrices
  just to build the badges.

`GET /pages/{pageId}/row` returns one fresh matrix row for an already created page. Use it after section
editor actions such as save draft, validate, publish independent section, rollback, enable, or disable.
The response gives backend-computed cell statuses, diagnostics, and actions, so the frontend can replace
the row in the opened matrix without recalculating publish or visibility rules locally.

For generated service-tree page types, call the same matrix endpoint:

```text
GET /api/admin/page-workbench/page-types/practice_collection_page?locale=uk
GET /api/admin/page-workbench/page-types/practice_page?locale=uk
GET /api/admin/page-workbench/page-types/service_page?locale=uk
GET /api/admin/page-workbench/page-types/problem_page?locale=uk
```

Each generated row is tied to one visible reference object from the CMS database:

- `practice_collection_page`: one synthetic source row, not an ERP object. It has no `practiceId`, always
  uses `pagePath = "services"`, and should be presented to editors as "Практики" even though the public
  route stays `/services`;
- `practice_page`: one visible practice;
- `service_page`: one visible service with `serviceCond=true` and a resolved visible practice;
- `problem_page`: one visible problem with resolved visible practice and service.

For `practice_collection_page`, `practice_page`, `service_page`, and `problem_page`, the matrix now
returns both:

- base non-regional rows, for example `/services/family-law`;
- regional rows for expected visible regions with a valid `sourceSlug`, for example
  `/kyiv/services/family-law`.

Expected regional rows are not "all regions". Backend filters them through the region-competence model:

- `practice_collection_page`: visible regions that have at least one active visible practice competence;
- `practice_page`: visible regions with an active region qualification for that practice;
- `service_page` and `problem_page`: visible regions with an active region qualification for the parent
  practice of that service/problem.

Disabled regions, regions without `sourceSlug`, and region/source pairs without an active matching
qualification are not returned as rows and should not be counted as missing pages by the frontend.

Regional rows still use the same `sourceRecord` as the base page. The region is a separate row field:

```json
{
  "kind": "regional",
  "title": "Kyiv / Family law",
  "pagePath": "services/family-law",
  "publicPath": "/kyiv/services/family-law",
  "regionSlug": "kyiv",
  "region": {
    "resource": "regions",
    "id": "region-1",
    "externalId": "74",
    "title": "Kyiv",
    "locale": "uk",
    "sourceSlug": "kyiv",
    "showOnSite": true,
    "diagnostics": []
  }
}
```

Rows contain `sourceRecord`:

```json
{
  "pageType": "practice_page",
  "resource": "practices",
  "id": "practice-1",
  "externalId": "10",
  "title": "Family law",
  "locale": "uk",
  "sourceSlug": "family-law",
  "showOnSite": true,
  "routeParams": {
    "practiceSlug": "family-law"
  },
  "pagePath": "services/family-law",
  "publicPath": "/services/family-law",
  "parentRefs": {},
  "diagnostics": []
}
```

If the generated page is not created yet, `row.page = null` and `actions.canBootstrap = true` when
`row.pagePath` and `row.publicPath` are available and there are no critical route/source diagnostics.
Use `row.endpoints.bootstrap` for creation. For regional generated rows this endpoint includes a default
body with `regionId`, so the frontend should send that body instead of reconstructing it locally:

```json
{
  "method": "POST",
  "path": "/api/admin/page-workbench/generated-sources/practice_page/practice-1/bootstrap?locale=uk",
  "body": {
    "regionId": "region-kyiv"
  }
}
```

Use row-level route fields for UI display. `sourceRecord.pagePath` / `sourceRecord.publicPath` still
describe the base source route; regional rows may have a different `row.publicPath`. Prefer backend-owned
generated bootstrap:

```text
POST /api/admin/page-workbench/generated-sources/practice_collection_page/practice_collection/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/practice_page/{sourceRecord.id}/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/service_page/{sourceRecord.id}/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/problem_page/{sourceRecord.id}/bootstrap?locale=uk
```

2026-06-05 addition: generated rows also expose direct open endpoints on `row.endpoints`. Use these for
clicking a generated base/regional row instead of hardcoding the generated-source URLs in the frontend:

```json
{
  "endpoints": {
    "open": {
      "method": "POST",
      "path": "/api/admin/page-workbench/generated-sources/practice_page/practice-1/open?locale=uk"
    },
    "openEditor": {
      "method": "POST",
      "path": "/api/admin/page-workbench/generated-sources/practice_page/practice-1/open-editor?locale=uk"
    }
  }
}
```

For regional generated rows, the same endpoints include the required body:

```json
{
  "method": "POST",
  "path": "/api/admin/page-workbench/generated-sources/practice_page/practice-1/open-editor?locale=uk",
  "body": {
    "regionId": "region-kyiv"
  }
}
```

`open` creates/opens the page authoring state and returns the default editor target. `openEditor` does the
same and additionally returns the default section editor payload. For the practice collection and practice
pages this is the main path for opening the first workable editor screen from the matrix.

Request body may be empty. For practice collection/practice/service/problem generated pages, backend
creates minimal valid draft content for required page-owned sections:

- `seo`: `title` and `description` from the source object title;
- intro section: `title` from the source object title;
- paired runtime block headings, for example `service_problems_block` / `service_lawyers_block`;
- optional FAQ/consultation CTA sections are created as bindings but disabled until the editor enables and
  fills them.

The request body may still contain overrides for initial section content. Object-shaped section content is
shallow-merged over backend defaults:

```json
{
  "initialSectionContents": {
    "seo": {
      "title": "Custom SEO title"
    }
  }
}
```

To create/open a regional generated page, call the same endpoint and pass the returned `row.region.id` as
`regionId`:

```json
{
  "regionId": "region-1"
}
```

Backend rereads the source object, and when `regionId` is present also rereads the region source. It
verifies slugs/parent links/route, creates or opens the page with the same `pagePath` and the selected
`regionSlug`, and returns `{ bootstrap, workbench }`. This should be the default frontend path for creating
generated practice/service/problem pages, because the frontend does not have to trust its own assembled URL
and does not have to invent the first draft payload.

The older generic bootstrap still exists for fixed pages or advanced flows:

```json
{
  "pageType": "practice_page",
  "locale": "uk",
  "pagePath": "services/family-law",
  "regionSlug": null
}
```

If a source slug or required parent relation is missing, backend returns a generated row with critical
diagnostics such as `PAGE_SOURCE_SLUG_MISSING`, `PAGE_SOURCE_PARENT_UNRESOLVED`,
`PAGE_SOURCE_PARENT_NOT_VISIBLE`, or `PAGE_SOURCE_ROUTE_INVALID`; in that case `canBootstrap=false`.
The frontend should show these diagnostics and route the editor to fix the underlying reference record.

`POST /pages/bootstrap` creates or opens a page authoring instance from the selected workbench row and
returns `{ bootstrap, workbench }`. The request body is the same as `POST /api/admin/pages/bootstrap`:

```json
{
  "pageType": "contacts_page",
  "locale": "uk",
  "pagePath": "contacts",
  "regionSlug": null,
  "initialSectionContents": {
    "seo": {
      "title": "Contacts"
    }
  }
}
```

Use this endpoint for `actions.canBootstrap`. After success, replace the not-created row with
`response.workbench.row`. The frontend should not build routes or section bindings itself; backend resolves
the page schema, route, shared sections, initial section versions, and row state. If a page already exists
for the same public route, the endpoint returns `bootstrap.created = false` plus the existing page row.

The workbench section editor endpoints wrap the same editor logic as
`/api/admin/pages/{pageId}/sections/{slotKey}/editor...`, but always return a fresh workbench row:

- `GET /pages/{pageId}/sections/{slotKey}/editor`: returns `{ editor, workbench }`;
- `PATCH /pages/{pageId}/sections/{slotKey}/editor/state`: returns `{ updateState, workbench }`;
- `POST /pages/{pageId}/sections/{slotKey}/editor/draft`: returns `{ saveDraft, workbench }`;
- `POST /pages/{pageId}/sections/{slotKey}/editor/validate`: returns `{ validation, workbench }`;
- `POST /pages/{pageId}/sections/{slotKey}/editor/publish`: returns `{ publish, workbench }`;
- `GET /pages/{pageId}/sections/{slotKey}/editor/history`: returns `{ history, workbench }`;
- `POST /pages/{pageId}/sections/{slotKey}/editor/rollback`: returns `{ rollback, workbench }`.

Use these workbench endpoints for the main page editor UI. The nested operation object contains the same
payload as the lower-level authoring endpoint, and `response.workbench.row` is the row that should replace
the current matrix row after the action. This removes the need for the frontend to manually call
`GET /pages/{pageId}/row` after every save, validation, publish, rollback, enable, or disable action.

The matrix also exposes these URLs directly on every editable section cell:

```json
{
  "slotKey": "seo",
  "actions": {
    "canOpen": true,
    "canSaveDraft": true,
    "canPublish": false,
    "canViewHistory": true
  },
  "endpoints": {
    "editor": {
      "method": "GET",
      "path": "/api/admin/page-workbench/pages/page-contacts-uk/sections/seo/editor"
    },
    "history": {
      "method": "GET",
      "path": "/api/admin/page-workbench/pages/page-contacts-uk/sections/seo/editor/history?limit=20&offset=0"
    },
    "saveDraft": {
      "method": "POST",
      "path": "/api/admin/page-workbench/pages/page-contacts-uk/sections/seo/editor/draft"
    },
    "validateDraft": {
      "method": "POST",
      "path": "/api/admin/page-workbench/pages/page-contacts-uk/sections/seo/editor/validate"
    },
    "publishDraft": null,
    "rollback": {
      "method": "POST",
      "path": "/api/admin/page-workbench/pages/page-contacts-uk/sections/seo/editor/rollback"
    }
  }
}
```

Frontend rule: show controls from `actions`, call URLs from `endpoints`. Do not hardcode
`/pages/{pageId}/sections/{slotKey}/...` in UI components. Runtime cells without editor endpoints are
non-openable (`actions.canOpen=false`). Composite groups that include runtime members remain openable
through the group's primary editable section endpoint.

Pure runtime cells can still be inspected when the backend exposes `actions.canInspect=true` and
`endpoints.inspect`. This is intentionally separate from `actions.canOpen`: `canOpen` means "open editable
section editor", while `canInspect` means "open a read-only diagnostic/runtime payload view". Do not ignore
`canOpen=false` to force an editor-like modal for runtime cells; call `endpoints.inspect` instead.

`GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/inspect` returns:

```json
{
  "runtime": {
    "slotKey": "local_offices",
    "kind": "runtime",
    "sectionType": "local_offices",
    "readOnly": true,
    "runtimeSlot": {},
    "payload": { "items": [] },
    "diagnostics": {
      "errors": 0,
      "warnings": 1,
      "missingPublished": false,
      "missingSourcePreview": false,
      "missingSourcePublished": false,
      "stale": false
    },
    "reasons": [
      {
        "code": "PAGE_RUNTIME_LIST_EMPTY",
        "severity": "warning",
        "slotKey": "local_offices",
        "sectionType": "local_offices"
      }
    ]
  },
  "workbench": {},
  "localeDiagnostics": {}
}
```

Use `runtime.reasons[]` for the explanation of warnings/errors shown on the runtime cell. Use
`response.workbench.row` to refresh the matrix row after inspection if the UI keeps the modal open.

The workbench page action endpoints wrap the same lifecycle logic as `POST /api/admin/pages/{pageId}/...`,
but they also return `workbench`, a fresh row-refresh payload for the affected page:

- `POST /pages/{pageId}/preview`: returns `{ preview, workbench }`;
- `POST /pages/{pageId}/publish`: returns `{ publish, workbench }`;
- `POST /pages/{pageId}/rollback`: returns `{ rollback, workbench }`.

Use these endpoints for page buttons on the matrix screen. The request bodies are the same as the existing
page lifecycle endpoints. After a successful action, replace the row with `response.workbench.row` and keep
using backend-provided `actions`/`diagnostics`.

The matrix exposes page action URLs directly on `row.endpoints`:

```json
{
  "endpoints": {
    "refresh": {
      "method": "GET",
      "path": "/api/admin/page-workbench/pages/page-contacts-uk/row"
    },
    "bootstrap": null,
    "preview": {
      "method": "POST",
      "path": "/api/admin/page-workbench/pages/page-contacts-uk/preview"
    },
    "publish": null,
    "rollback": null,
    "history": {
      "method": "GET",
      "path": "/api/admin/page-workbench/pages/page-contacts-uk/history?limit=50&offset=0"
    },
    "snapshots": {
      "method": "GET",
      "path": "/api/admin/page-workbench/pages/page-contacts-uk/snapshots"
    },
    "currentSnapshot": null
  }
}
```

The matrix response also exposes screen-level bulk publish actions:

```json
{
  "endpoints": {
    "bulkPublishPlan": {
      "method": "POST",
      "path": "/api/admin/page-workbench/bulk-publish/plan",
      "body": {
        "locale": "uk",
        "scope": {
          "kind": "pages",
          "pageIds": ["page-contacts-uk"]
        }
      }
    },
    "bulkPublish": {
      "method": "POST",
      "path": "/api/admin/page-workbench/bulk-publish",
      "body": {
        "locale": "uk",
        "scope": {
          "kind": "pages",
          "pageIds": ["page-contacts-uk"]
        }
      }
    }
  }
}
```

Use `bulkPublishPlan` to show what will happen before "publish all". Use `bulkPublish` for the actual
operation. Do not implement publish-all as frontend `Promise.all`; the backend response has one summary and
per-page statuses.

Every section/runtime cell now exposes `relationship`. This is the only field the UI should use to display
whether a cell is self-owned, inherited, global, runtime, or not created. Do not infer that from
`composition.strategy` alone.

Examples:

```json
{
  "slotKey": "seo",
  "composition": { "strategy": "override" },
  "relationship": {
    "role": "self_owned",
    "inheritanceStrategy": "none",
    "isInherited": false,
    "sourceSectionId": null,
    "localSectionId": "section-seo"
  }
}
```

Here `composition.strategy = "override"` is an internal authoring strategy, not inheritance. Since
`sourceSectionId` is `null`, this is a standalone page section.

```json
{
  "slotKey": "price",
  "relationship": {
    "role": "child",
    "inheritanceStrategy": "append",
    "isInherited": true,
    "sourceSectionId": "section-price-parent",
    "localSectionId": "section-price-local"
  }
}
```

This is a real child section. Show inheritance only when `relationship.isInherited = true`.

`draftVersion` and `publishedVersion` summaries now include audit fields:

```json
{
  "sectionVersionId": "section-seo-published-v1",
  "versionNo": 1,
  "lifecycleState": "published",
  "createdBy": "editor-1",
  "createdAt": "2026-05-21T10:00:00.000Z",
  "publishedBy": "publisher-1",
  "publishedAt": "2026-05-21T11:00:00.000Z"
}
```

Use `row.diagnostics` for page-level issues, and `cell.diagnostics` only for section-level issues. For
example, `PAGE_NO_CURRENT_SNAPSHOT` belongs to the row, not to a section cell. If `row.endpoints.publish`
is `null`, read `row.readiness.publish.reasons` for the user-facing reason; common cases are "already
published" or "blocked by validation errors / empty required sections".

`PAGE_SECTION_DRAFT_STALE` is an attention/review notice, not a hard publish blocker. It means a
source-backed section has inherited changes that have not yet been accepted into the current page snapshot.
If `row.actions.canPublish` is still true, the frontend should allow page publish and show that publishing
the page will accept the current backend-resolved section content. Do not force editors to create a child
section draft only to clear stale state.

For generated service-tree pages, the backend now resolves missing runtime/read-model payloads during
preview and publish. The frontend does not need to manually send payloads for these slots:

- `practice_collection`;
- `practice_services`;
- `practice_lawyers`;
- `service_problems`;
- `service_lawyers`;
- `problem_lawyers`.

The resolver reads CMS reference tables, uses the page route context (`services`,
`services/{practiceSlug}`, `services/{practiceSlug}/{serviceSlug}`, etc.), and returns list payloads with
route-ready items. For `practice_collection_page`, the runtime payload is a practice tree: base rows list
all visible practices with nested visible services, while regional rows list visible practices that have an
active region qualification for the selected visible region with nested visible services under those
practices. Nested services use `show_on_site=true` and `service_cond=true`. Practice and service ordering is
CMS `sort_order`, then localized/source display name, then stable id. If a practice or service has a
missing or unpublished linked generated page, keep it visible in the admin runtime/editor context and show
the backend warning/diagnostic rather than silently hiding it from editors. If the frontend sends a
`runtimePayloads` entry for one of these slots, backend keeps the provided payload and does not resolve that
same slot again. This is mainly useful for tests or transitional UI experiments; normal CMS frontend code
should let backend resolve service-tree runtime slots.

`practice_collection_page` exposes `practice_collection_intro` + runtime `practice_collection` as one
composite workbench group with `groupKey: "practice_collection"`. In the matrix, render this pair as one
editor-facing section/card. Open and save through the group's primary slot
`practice_collection_intro`; show the runtime `practice_collection` diagnostics as the readonly/runtime
part of the same visual section. The primary editor endpoint returns the intro section in `editor` and the
resolved runtime practice tree in `compositeGroup.members[]`, not inside `editor.section.content`.

`practice_collection_page` matrix rows now include row-level diagnostics for this runtime tree. Treat
`PAGE_RUNTIME_REQUIRED_LIST_EMPTY` as a critical publish blocker and show its `slotKey`/message near the
`practice_collection` runtime cell. Treat `PAGE_LINKED_PAGE_NOT_CREATED` and
`PAGE_LINKED_PAGE_NOT_PUBLISHED` as warning-level admin diagnostics; their reason payload includes
`sourceType`, `sourceId`, and `publicPath` so the UI can point the editor to the affected practice/service.
Warnings do not remove the item from the admin context and do not by themselves block page publish.

`practice_page` matrix rows now also run a lightweight runtime linked-page diagnostic pass for
`practice_services`, `practice_related_legal`, and `practice_lawyers`. The backend uses the same runtime
resolver as preview/publish, then compares each runtime item `publicPath` with the generated page catalog.
Cell warning counters are written to the matching runtime cells (`cell.diagnostics.warnings`), while the
detailed reasons stay in `row.diagnostics.blockingReasons` with `slotKey`, `sectionType`, `sourceType`,
`sourceId`, and `publicPath`. These warnings do not block page publish by themselves. For CMS page workbench
purposes, legal-only service rows (`legal_cond=true`, `service_cond=false`) are regular `service_page`
generated sources, so their page creation/publish lifecycle is the same as ordinary services.

For `practice_collection_page`, regional `seo` and `practice_collection_intro` should appear as inherited
from the base page until the editor explicitly overrides them. Regional canonical route is self-canonical,
for example `/kyiv/services`, not canonicalized to the base `/services`.

Runtime resolution can block preview/publish with `PAGE_RUNTIME_RESOLUTION_FAILED` when the page route no
longer matches visible reference data or a visible child item has no required source slug. Show this as a
backend validation error and route the editor to fix the underlying reference object.

Snapshot history endpoints support the rollback UI:

- `GET /pages/{pageId}/history`: returns historical page snapshots as row-history items with matrix-like
  cells;
- `GET /pages/{pageId}/snapshots`: returns historical page snapshots, newest first;
- `GET /pages/{pageId}/snapshots/{snapshotId}`: returns one snapshot with its public payload.

Use `/history` for the row history panel because it already groups snapshot section refs by workbench
cells. Use `/snapshots` only when the UI needs the raw snapshot list. Each snapshot item contains:

- `snapshotId`, `snapshotNo`, `status`;
- `createdBy` / `createdAt`: who created this snapshot and when;
- `activatedBy` / `activatedAt`: who made it current and when, only for the current snapshot;
- `isCurrent`: whether this snapshot is currently served publicly;
- `sectionRefs`: exact section versions used by that snapshot.

Use the detail endpoint when the editor clicks "view" on a historical snapshot. It returns the same metadata
plus `publicPayload`, so the UI can preview exactly what rollback would restore. To rollback, send the chosen
`snapshotId` as `sourceSnapshotId` to `POST /pages/{pageId}/rollback`. Rollback creates a new current snapshot;
it does not mutate the historical snapshot.

For this first slice, `contacts_page` and `lawyers_page` are supported as single-row matrices. Generated
service-tree matrices are available for base and regional practice collection, practice, service, and
problem pages.

Generated service-tree schemas now pair editable CMS block sections with runtime/read-model slots through
`compositeGroupKey`, so the UI can render them as one block:

- `practice_collection_intro` + `practice_collection` use `practice_collection`;
- `practice_services_block` + `practice_services` use `practice_services`;
- `practice_related_legal_block` + `practice_related_legal` use `practice_related_legal`;
- `practice_reviews_block` + `practice_reviews` use `practice_reviews`;
- `practice_lawyers_block` + `practice_lawyers` use `practice_lawyers`;
- `service_problems_block` + `service_problems` use `service_problems`;
- `service_lawyers_block` + `service_lawyers` use `service_lawyers`;
- `problem_reviews_block` + `problem_reviews` use `problem_reviews`;
- `problem_lawyers_block` + `problem_lawyers` use `problem_lawyers`;
- `lead_questionnaire` + `lead_form` + `lead_capture` use `lead_block` on service-hierarchy detail pages.

The `*_block` section stores CMS-authored title/lead/settings for the block. The runtime slot stores the
read-only list contract. Optional page-owned `*_faq` and `*_consultation_cta` sections are also present
and may be enabled/disabled through backend-provided actions. Price sections are modeled as source-backed
page-owned sections: base generated pages inherit from `global_price`, while regional generated pages
inherit from the matching base page price section.

For every listed composite group, the section editor endpoint keeps the normal `editor` object scoped to
the opened primary section. If the opened slot belongs to a composite group, the same response also returns
`compositeGroup`. Its `members[]` contain section members with `section`, `content`, `actions`,
`diagnostics`, and `reasons`, plus runtime members with `runtimeSlot`, resolved `payload`, `diagnostics`,
and `reasons`. Runtime and inherited read-only members are display context only; save/validate/publish
buttons still belong to the primary section/editor actions.

2026-06-04 schema refinement for the first service-hierarchy designs:

- `breadcrumbs` are not editable section cells. They are generated public/runtime metadata from route/page
  context and should be rendered by the site frontend outside the CMS section list.
- For `practice_collection_page`, `practice_page`, `service_page`, and `problem_page`, breadcrumbs are
  generated by the backend in the page payload. The frontend must render the returned breadcrumb array and
  must not rebuild labels client-side from source objects. Backend label priority is
  `menuTitle ?? publicName ?? sourceName`, with source fallback only when editorial labels are missing.
  Regional pages include a separate region breadcrumb before the "Practices" breadcrumb.
- `practice_collection_page` exposes `practice_collection_intro` and runtime `practice_collection`; it does
  not expose `lead_capture` in the first collection-page design slice.
- `practice_page`, `service_page`, and `problem_page` expose required inherited `achievements_strip` and
  `lead_form` slots. `practice_collection_page` does not.
- `practice_intro` and other `*_intro` hero slots now include optional `ctaLabel` and `ctaTarget` fields.
- `practice_page` additionally exposes optional page-owned `practice_intro_text`, `practice_actions`,
  `practice_team_cta`, `practice_optional_text`, optional `lead_questionnaire`, runtime `practice_cases`,
  runtime `practice_reviews`, and runtime `lead_capture`.
- `service_page` and `problem_page` also expose optional `lead_questionnaire` plus runtime `lead_capture`;
  the required inherited `achievements_strip` and `lead_form` slots above apply to them too.
- `lead_form` is the CMS-authored shared form content section. `lead_capture` is read-only runtime data
  for the standard service-hierarchy lead form and is not edited through a section form.
- `lead_questionnaire` is the page-specific questionnaire section. It is disabled by default until the
  editor enables and fills it. A typical draft payload is
  `{ "finalMessageTitle": "...", "finalMessageDescription": [...], "questions": [{ "id": "minor_children", "question": "...", "type": "single_choice", "required": false, "options": [{ "id": "yes", "label": "Так" }] }] }`.
  Only `single_choice` and `multiple_choice` are supported. Preserve stable question/option IDs and use
  array order for display order. The backend reads old `title`/`description`/`label`/`value` aliases but
  stores every newly saved draft in the canonical format. See
  [`lead-questionnaire-contract-2026-07-16.md`](lead-questionnaire-contract-2026-07-16.md).

2026-06-09/10 `practice_page` structure checkpoint: do not treat the whole backend scaffold as the final
screen structure. The global recognition strip after the hero is implemented as `achievements_strip`.
The agreed target keeps `practice_services_block` + `practice_services` as the required services list
(`service_cond=true`), adds a
separate optional "Може зацікавити" composite list for `legal_cond=true` and `service_cond=false`, splits
generic text content into three fixed optional slots (`practice_intro_text`, `practice_reviews_text`,
`practice_price_text`), and makes `practice_actions` an enabled-by-default action list with 2-8 items.
The backend exposes bootstrap defaults through `defaultVisibility`: `practice_intro_text` and
`practice_actions` default to enabled, while `practice_related_legal_block`, `practice_reviews_text`,
`practice_price_text`, `practice_faq`, and `lead_questionnaire` default to disabled. Regional editable
text/metadata sections inherit from the base page by default.

2026-06-13 update: the target `practice_page` structure is fixed in
`docs/practice-page-structure-2026-06-13.md`. Frontend-relevant decisions:

- render backend slots sharing `compositeGroupKey` as one visual block where the page design treats them as
  one section. Prefer `row.compositeGroups` over client-side pairing heuristics; keep `cells` as the raw
  technical state and use the group's `primarySlotKey`/`endpoints` for the editable part;
- section headings are locked for regional override, even when other section fields remain overrideable;
- `practice_team_cta` and `practice_lawyers_block` + `practice_lawyers` are separate sections with the same
  lawyer eligibility source but different UI behavior: showcase without URL vs selection with lawyer-page
  links;
- the bottom lead area is one visual block made from `lead_questionnaire`, inherited `lead_form`, and
  runtime `lead_capture`;
- `lead_form` is edited through global sections and is read-only inside the page section editor.

2026-06-15 `problem_page` implementation update:

- The backend now exposes the first full editor slice for `problem_page`; use
  [`problem-page-structure-2026-06-15.md`](problem-page-structure-2026-06-15.md) as the slot checklist.
- `problem_page` uses the same regional-base inheritance philosophy as `practice_page`: base content is
  the source, regional pages review/publish inherited stale changes, and section headings are locked on
  regional pages.
- The previous single `problem_guidance` concept was replaced with fixed slots because the design requires
  independent lifecycle/visibility for `problem_must_do`, `problem_must_not_do`,
  `problem_lawyer_actions`, and two accent text sections.
- `problem_reviews_block` + `problem_reviews`, `problem_lawyers_block` + `problem_lawyers`, and
  `lead_questionnaire` + `lead_form` + `lead_capture` should be rendered as composite UI blocks.
- `problem_cases` is currently a runtime placeholder that may return an empty list by design.

2026-06-16 `service_page` implementation update:

- The backend now exposes the first full editor slice for `service_page`; use
  [`service-page-structure-2026-06-16.md`](service-page-structure-2026-06-16.md) as the slot checklist.
- `service_page` uses the same regional-base inheritance philosophy as `practice_page` and `problem_page`:
  base content is the source, regional pages review/publish inherited stale changes, and section headings
  are locked on regional pages.
- `service_problems_block` + `service_problems`, `service_reviews_block` + `service_reviews`,
  `service_lawyers_block` + `service_lawyers`, and `lead_questionnaire` + `lead_form` + `lead_capture`
  should be rendered as composite UI blocks.
- The previous shallow service-page slice is replaced by fixed slots because the design requires
  independent lifecycle/visibility for three accent text sections, three advisory sections, and the
  separate text/runtime composites around problems, reviews, lawyers, and lead capture.
- `service_cases` is currently a runtime placeholder that may return an empty list by design.
- Current default visibility:
  - enabled: `service_accent_text_1`, `service_lawyer_actions`, `service_accent_text_2`,
    `service_must_not_do`, `service_accent_text_3`, `service_must_do`, `service_team_cta`,
    `service_faq`;
  - disabled: `service_price_text`, `lead_questionnaire`.

2026-06-17 runtime-regions update:

- `practice_page`, `service_page`, and `problem_page` now also expose a standalone runtime slot
  `regional_offices`.
- This slot is national-only. The backend includes it for the Ukraine/base row and omits it completely
  from regional rows. Frontend should treat missing regional cells as intentional, not as broken data.
- The payload is read-only and contains `title`, `accentTitle`, `titleSuffix`, and `items[]`.
- `items[]` contains only regions that are both eligible by active competencies and backed by an existing
  published regional page of the same page type.
- The matrix may show a warning with code `PAGE_RUNTIME_LIST_EMPTY` when the national page has no eligible
  published regional targets yet. This is an editor warning, not a publish blocker.
- Public rendering should hide this section when the runtime payload resolves to no items.

2026-06-28 service-hierarchy amendment:

- Use [`service-hierarchy-page-amendments-2026-06-28.md`](service-hierarchy-page-amendments-2026-06-28.md)
  as the current product contract for the latest regional links, local offices, and team CTA changes.
- `practice_collection_page` should also expose `regional_offices` for the base/Ukraine row. This is a
  read-only regional-link section pointing to published regional collection alternatives such as
  `/kyiv/services`. Regional collection rows intentionally omit the slot.
- Treat the technical slot key `regional_offices` as "regional alternatives", not as a real office list.
- Real offices on regional detail pages should use a separate runtime slot, `local_offices`, on
  `practice_page`, `service_page`, and `problem_page`. Render it only on regional pages and hide it publicly
  when the runtime list is empty.
- Team CTA now has two possible positions on detail pages: a top slot after `achievements_strip` and the
  existing lower slot. Both can be enabled/disabled; if both are enabled, backend should return an error on
  the lower slot and the UI should guide the editor to disable one position.
- Team CTA editors should move from one large `lead` field to `paragraphs[]`. Until existing drafts are
  migrated, render old `lead` as a single paragraph when `paragraphs` is absent.

Section cells contain only metadata and status:

- ids: `bindingId`, `sectionId`, `sourceSectionId`, `localSectionId`;
- state: `visibility`, `draftStatus`, `draftVersion`, `publishedVersion`;
- ownership/publish info: `ownershipScope`, `publishMode`, `composition`;
- `diagnostics`: errors, warnings, missing published version, stale state;
- `actions`: what the UI may show (`canOpen`, `canEdit`, `canSaveDraft`, `canPublish`, etc.).
- `actions.canEnable` / `actions.canDisable`: show section visibility controls computed by the backend.

Section cells do not contain section content. When the editor opens one cell, load the full edit state
through `GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor`.

The workbench editor wrapper returns:

- `editor`: the ordinary section editor state for the opened section only;
- `compositeGroup`: `null` for a standalone section, or the full visual group context when the opened slot
  belongs to a backend `compositeGroupKey`;
- `workbench`: the fresh row after the operation;
- `localeDiagnostics`: compact all-locale diagnostics on editor-open responses.

Do not write runtime data into `editor.section.content`. For composite UI sections, render editable fields
from `editor.content`, then render read-only companions from `compositeGroup.members[]`. The same
`compositeGroup` contract is returned after save draft, validate, independent section publish, rollback,
and section state changes, so the modal can refresh without a second call.

Runtime cells represent read-model data, not editable CMS drafts. They expose `source` metadata and should
be shown as read-only blocks in the matrix.

For standalone runtime cells with warnings, use `cell.actions.canInspect` and `cell.endpoints.inspect`.
The inspect response carries the resolved read-only payload and the exact `runtime.reasons[]`; this is the
place to explain warnings for `local_offices`, `regional_offices`, runtime reviews, runtime cases, and
similar slots that have no editable section content.

Runtime editorial case items keep raw relation ids and now include hydrated relation labels when the
backend can resolve them. This applies to page/runtime payloads such as `practice_cases`,
`service_cases`, and `problem_cases`:

```json
{
  "title": "Успішні справи АКТУМ з сімейного права",
  "relations": {
    "practiceId": "practice-cms-id",
    "serviceId": "service-cms-id",
    "problemId": null,
    "practice": {
      "kind": "practice",
      "id": "practice-cms-id",
      "externalId": "10",
      "sourceSlug": "family-law",
      "title": "Family law",
      "displayTitle": "Family law",
      "menuTitle": "Family law",
      "sourceName": "Family source"
    },
    "service": {
      "kind": "service",
      "id": "service-cms-id",
      "externalId": "101",
      "sourceSlug": "alimony",
      "title": "Alimony",
      "displayTitle": "Alimony",
      "menuTitle": "Alimony",
      "sourceName": "Alimony source"
    }
  }
}
```

Use `relations.practice.displayTitle`, `relations.service.displayTitle`, and
`relations.problem.displayTitle` for UI labels. Keep `practiceId`, `serviceId`, and `problemId` as the
stable technical keys.

For `practice_cases`, `service_cases`, and `problem_cases`, `payload.title` is the display heading for
the whole runtime block. It comes from `translations.{locale}.casesSectionTitle` on the current
practice/service/problem reference object. The frontend should render this value as-is and should not try
to assemble grammar-sensitive headings from `publicName` or `menuTitle`. If the reference field is empty,
the backend returns a generic localized fallback so preview stays renderable, while reference diagnostics
warn the editor that a better heading should be filled in.

The same rule applies to editorial authors. Runtime publication items keep technical ids in
`authors.primaryLawyerAuthorId`, `authors.legalReviewerLawyerId`, and `authors.cmsUserAuthorId`, and now
return read-only hydrated author objects when the backend can resolve them:

```json
{
  "authors": {
    "primaryLawyerAuthorId": "lawyer-cms-id",
    "legalReviewerLawyerId": null,
    "cmsUserAuthorId": null,
    "primaryLawyerAuthor": {
      "kind": "primary_lawyer_author",
      "id": "lawyer-cms-id",
      "externalId": "100",
      "displayName": "Olena Lawyer",
      "title": "Olena Lawyer",
      "publicName": "Olena Lawyer",
      "sourceName": "Olena source",
      "slug": "olena-lawyer"
    },
    "legalReviewerLawyer": null,
    "cmsUserAuthor": null
  }
}
```

Use `authors.primaryLawyerAuthor.displayName`, `authors.legalReviewerLawyer.displayName`, or
`authors.cmsUserAuthor.displayName` for cards and previews. Keep the `...Id` fields as the stable keys.

Use row-level `actions` for page buttons:

- `actions.canBootstrap`: show create/bootstrap page action when the row is not created yet;
- `actions.canOpen`: open page authoring state;
- `actions.canPreview`: allow preview build for the current draft/published mix;
- `actions.canPublish`: allow page publish;
- `actions.canRollback`: allow rollback flow only when the page already has a current snapshot;
- `actions.canViewCurrentSnapshot`: show current public snapshot details.

Use row-level `readiness.preview.reasons` and `readiness.publish.reasons` for action tooltips and
disabled-state explanations. Use row-level `diagnostics.blockingReasons` for general page
banners/status. The frontend should display messages and codes, but should not recreate the rules.
Important codes:

- `PAGE_NOT_CREATED`;
- `PAGE_ALREADY_PUBLISHED`;
- `PAGE_SECTION_DRAFT_STALE` - warning/attention; page publish can accept the current resolved inherited
  state when no critical blockers remain;
- `PAGE_SECTION_VALIDATION_FAILED`;
- `PAGE_SECTION_VALIDATION_WARNING`;
- `PAGE_REQUIRED_SECTION_EMPTY`;
- `PAGE_ENABLED_SECTION_EMPTY`;
- `PAGE_SOURCE_SECTION_EMPTY`;
- `PAGE_SOURCE_SECTION_NOT_PUBLISHED`;
- `PAGE_REQUIRED_INDEPENDENT_SECTION_NOT_PUBLISHED`;
- `PAGE_NO_CURRENT_SNAPSHOT`.

`PAGE_ENABLED_SECTION_EMPTY` means the section is optional by schema, but currently enabled on the page and
has neither a draft nor a published version. The backend treats enabled sections as part of the page, so
preview/publish can be hidden until the section is filled or disabled by a supported action.

Source-backed sections have their own readiness flags. `diagnostics.missingSourcePreview` means an
inherited/global source has neither draft nor published content, so the page cannot be previewed or
published. `diagnostics.missingSourcePublished` means the source has no published version, so page publish
is blocked; preview can still be available if the source has a draft. The matching readiness codes are
`PAGE_SOURCE_SECTION_EMPTY` and `PAGE_SOURCE_SECTION_NOT_PUBLISHED`. Use row actions/readiness as the
button authority instead of checking only the local section binding.

## Pages Catalog

Use:

```text
GET /api/admin/pages
```

Optional query params:

- `pageType`;
- `locale`;
- `status`;
- `q`;
- `limit`;
- `offset`.

This endpoint is the source for the CMS screen "Pages". It returns one row per page with:

- page identity and route: `pageId`, `pageType`, `locale`, `regionSlug`, `pagePath`, `publicPath`;
- raw page `status`;
- derived `publishState`: `not_published`, `published`, `draft_changed`, `requires_review`;
- current published snapshot summary, if it exists;
- section summary: total bindings, draft bindings, stale bindings, missing published bindings;
- `createdAt` and `updatedAt`.

Use `publishState` for badges in the page list. Use `sectionSummary.staleBindings > 0` to show that the
page has inherited changes needing attention. This does not by itself mean publish is blocked; use
row-level `actions.canPublish` / `readiness.publish.ready` for the actual button state. The catalog does
not replace `GET /api/admin/pages/{pageId}/authoring`;
it only helps the frontend choose which page to open.

## Authoring State

`GET /api/admin/pages/{pageId}/authoring` returns:

- `page`: page identity, locale, route, public path, and status;
- `sections`: CMS section slots;
- `runtimeSlots`: read-only runtime/read-model slots.

For each item in `sections`, pay attention to:

- `slotKey`: stable key used in save/preview/publish workflows;
- `fields`: editable field contract for the UI;
- `layout`: where the section belongs;
- `ownershipScope`: `page_owned`, `global_owned`, etc.;
- `publishMode`: `with_page` or `independent`;
- `visibility`: enabled/disabled state;
- `draftStatus`: `fresh` or `draft_stale`;
- `composition`: inherit/override/append rules;
- `draftVersion` and `publishedVersion`.

Only page-owned, editable slots should expose draft editing controls. Shared/global/runtime slots should be
displayed as part of the page state, but not edited through the page-owned draft endpoint.

## Section Editor

Use:

```text
GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor
```

This endpoint opens one CMS section from the workbench matrix. It is the main payload for the section edit
screen. The response shape is:

```json
{
  "editor": {},
  "workbench": {
    "row": {}
  }
}
```

Use `response.editor` to render the section editor and `response.workbench.row` to refresh the matrix row
behind the opened editor.

Implementation note, 2026-06-09: `response.workbench.row` from the section editor wrapper is source-aware
and must match the row shape returned by the page-type matrix and row refresh endpoints. For generated
regional rows this includes `rowKey`, `kind`, `title`, `sourceTitle`, `regionTitle`, `displayTitle`,
`sourceRecord`, `region`, `regionSlug`, `pagePath`, and `publicPath`. The frontend should not special-case
editor rows as plain catalog rows.

`response.editor` contains:

- `page`: page identity and route;
- `slot`: schema-driven section metadata: fields, layout, content shape, allowed composition strategies;
  inherited/source-backed sections also include `slot.fieldPolicies`, so the UI knows which fields may
  inherit, override, or append;
- `section`: binding/current authoring state: ids, ownership, publish mode, visibility, composition,
  draft/published version refs;
- `content.draft`: full current draft content for this section, if a draft exists;
- `content.published`: full current published content for this section, if a published version exists;
- `content.source`: for inherited/source-backed sections, the current source draft/published versions;
- `content.local`: for inherited/source-backed sections, the page/regional local draft/published versions;
- `content.resolved.draft`: backend-composed draft preview content from source + local, when it can be
  resolved;
- `content.resolved.published`: backend-composed published content from source + local, when it can be
  resolved;
- `diagnostics.draftValidation`: latest recorded publish validation state for the draft, if available;
- `diagnostics.errors` and `diagnostics.warnings`;
- `actions`: backend-computed flags for the UI.

For normal non-inherited sections, `content.source`, `content.local`, and `content.resolved.*` may be
`null`; use the existing `content.draft` / `content.published` fields. For page price sections, prefer
showing the three-layer view:

- source: inherited parent content;
- local: what this page/region changes;
- resolved: what preview/publish will render.

The frontend should not merge source and local content itself. Use `content.resolved.*` for the preview of
the final section result, and use `section.composition` plus `slot.fieldPolicies` only to render controls.
For inherited price sections, `content.resolved.draft` is the editor's latest-draft preview and
`content.resolved.published` is the currently published result. Do not show draft-resolved content as if it
were already public.

Runtime/read-model payloads keep media ids as stable references and may also include ready-to-render URL
fields. Current examples:

- lawyer cards/profile: `photoMediaId` plus `photoMediaUrl`;
- editorial/case cards: `coverMediaId` plus `coverMediaUrl`.

Use the URL field for rendering when present. Keep the id for editing/saving and diagnostics. Do not issue
one `GET /api/admin/media/{mediaId}` per card just to render lists.

Implementation note, 2026-06-13: inherited page sections now save field-level composition together with the
section draft. When an editor changes a field that is inherited by default, the frontend must send the new
local `content` and the intended `composition` in the same draft-save request. Example for overriding only
`ctaLabel` while all other fields keep inheriting from the source:

```json
{
  "content": {
    "title": "Inherited title or local working value",
    "ctaLabel": "Regional CTA"
  },
  "composition": {
    "strategy": "inherit",
    "fields": [
      { "field": "ctaLabel", "strategy": "override" }
    ]
  }
}
```

If a field should return to inheritance, remove that field override or send it as `inherit` according to
the UI state. Saving a local draft does not by itself accept `draft_stale`; stale inherited changes remain
attention until page publish accepts the current resolved content.

Important boundaries:

- Workbench matrix cells are summary-only.
- Section editor is the place where full section content appears.
- Runtime slots must not call this endpoint; they are read-model blocks and should stay read-only in this
  slice.
- `actions.canSavePageDraft` means the backend can save this slot as a page-owned draft.
- `actions.canSaveIndependentDraft` means the backend can save this slot as an independent/global section
  draft.
- `actions.canEnableSection` and `actions.canDisableSection` mean the backend allows changing only the
  page binding visibility for this slot.
- The frontend should use the page-scoped editor action endpoints below for both cases. The frontend does
  not need to decide which low-level section lifecycle endpoint is correct.

## Section Editor Actions

Use these endpoints from the section edit screen:

```text
PATCH /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/state
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/draft
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/validate
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/publish
GET  /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/history
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/rollback
```

State request body:

```json
{
  "visibility": "disabled"
}
```

Use this endpoint for section enable/disable switches in the page editor. It updates only the page-section
binding visibility. It does not create a new section draft and does not change published section versions.
The backend rejects disabling fixed/required slots where the page schema does not allow it. The response
returns `previousVisibility`, the new `visibility`, and a reloaded `editor` payload.
In the workbench wrapper, read it as `response.updateState.editor` and then replace the matrix row with
`response.workbench.row`.

Draft request body:

```json
{
  "content": {
    "title": "Contacts"
  }
}
```

The backend decides whether this is a `with_page` page-owned section or an `independent` global section.
The response returns operation metadata plus a reloaded `editor` payload. Use `response.editor` as the new
current section state in the UI on the lower-level endpoint. In the workbench wrapper, use
`response.saveDraft.editor` and then replace the matrix row with `response.workbench.row`.

Validate request body:

```json
{
  "sectionVersionId": "optional-draft-version-id",
  "recordDiagnostics": true
}
```

If `sectionVersionId` is omitted, the backend validates the current draft visible in the editor payload.
The response returns `ok`, `errors`, `warnings`, `validationRunId`, and a reloaded `editor` payload.
Warnings are non-blocking editor-quality diagnostics: `ok` and stored validation `status` are still based
on errors only. When `recordDiagnostics=true`, the saved warning list is visible later in
`editor.diagnostics.warnings`; the matrix also exposes aggregate warning counts on the section cell and row.
In the workbench wrapper, use `response.validation.editor` and `response.workbench.row`.

Publish request body:

```json
{
  "sectionVersionId": "optional-draft-version-id"
}
```

This endpoint is only for independent sections such as shared/global sections. Page-owned sections are
published with the page through `POST /api/admin/pages/{pageId}/publish`.
In the workbench wrapper, use `response.publish.editor` and `response.workbench.row`.

History:

```text
GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/history?limit=50&offset=0
```

The response returns version rows for the section currently opened through the page editor:

- draft, published and archived versions;
- version content for preview/review;
- `changeReason` plus computed `changeOrigin`;
- `createdBy`, `createdAt`, `publishedBy`, `publishedAt`;
- `isCurrentDraft` and `isCurrentPublished`;
- `canRollback`, which is true only for published versions.

`changeOrigin` uses the same UI contract as global section history. Manual edits are marked as
`{ code: "ME", label: null }`; rollback rows are marked as `RB#<sourceVersionNo>` and repeated rollbacks as
`RB#<sourceVersionNo>_<repeatNo>`; draft-from-version/copy rows use `FV` with the same label pattern.

Rollback:

```text
POST /api/admin/pages/{pageId}/sections/{slotKey}/editor/rollback
```

For the workbench UI use:

```text
POST /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor/rollback
```

Request body:

```json
{
  "sourcePublishedVersionId": "section-contacts-header-published-v1"
}
```

Rollback does not move the published pointer backwards. It creates a new draft copied from the selected
published version and returns a reloaded `editor` payload. For page-owned sections the backend also points
the page binding to the new rollback draft. For independent/global sections the backend updates the section
latest draft pointer, and pages keep their published state until a later publish/rebuild.
In the workbench wrapper, use `response.rollback.editor` and `response.workbench.row`.

The older `POST /api/admin/pages/{pageId}/sections/{slotKey}/draft` endpoint still exists for the first
page-owned slice, but new CMS page editor UI should prefer the `/editor/draft` endpoint.

The lower-level `/api/admin/pages/.../editor...` endpoints still exist and keep the same operation payloads.
For the main CMS page workbench, prefer the `/api/admin/page-workbench/...` wrappers because they remove
one extra refresh request after every action.

## Preview

Use:

```text
POST /api/admin/pages/{pageId}/preview
```

The response payload is the protected preview payload for the preview frontend. Preview may include latest
draft state and runtime payloads supplied by the backend/admin flow. The public frontend must not use this
endpoint.

## Publish

Use:

```text
POST /api/admin/pages/{pageId}/publish
```

The response contains:

- `snapshotId`;
- `snapshotNo`;
- `publicPath`;
- `withPageSectionCommits`;
- final public `payload`.

After publish, the public frontend should read the current published snapshot/public endpoint. It should
not read authoring state.

## Rollback

Use:

```text
POST /api/admin/pages/{pageId}/rollback
```

Rollback creates a new current snapshot from a historical source snapshot. It does not mean the frontend
should manually assemble old page state.

## Planned Backend Follow-Ups For CMS Front

The current page workbench slice is intentionally limited to the first usable page-editor flow. The backend
team plans to add the following pieces next, so the frontend should keep screens modular and avoid hardcoding
temporary assumptions:

- Practice/service/problem hierarchy: generated workbench rows and page schemas for practice, service,
  and problem are present for base and regional variants. The backend service-tree endpoint stays
  non-regional for the left hierarchy; the opened matrix is where regional page rows appear.
- Dependency-aware runtime/read-model slots: practice pages should expose services, service pages should
  expose problems, and generated pages should be driven by CMS reference data rather than frontend guesses.
- Richer page bootstrap for generated lawyer pages remains future work. Practice, service, and problem
  pages should already be created through `POST /api/admin/page-workbench/generated-sources/.../bootstrap`;
  this endpoint now also supplies minimal required section drafts when the frontend sends an empty body.
- Section action coverage for future movable/blog-like sections: add/remove/reorder will come later and
  should be a backend-owned action layer, not a frontend-only mutation.
- Warning diagnostics: section validation warnings are now persisted beside validation errors and returned
  through editor validate responses, editor `diagnostics.warnings`, and workbench cell/row warning counters.
  They are editor-quality signals and do not make validation `status=failed` by themselves.
- Typed client generation: OpenAPI should remain the source for DTOs; frontend should prefer generated
  clients when that pipeline is connected.

## UI Notes

- Show `draft_stale` clearly as inherited-change attention. Publishing the page is allowed when backend
  row readiness has no critical blockers and acts as acceptance of the current resolved content.
- Keep preview and published/current state visually distinct.
- Do not allow editing runtime slots directly from the page section draft form.
- Do not infer publishability only from visible fields. Backend publish validation is the final authority.
