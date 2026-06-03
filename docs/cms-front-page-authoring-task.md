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
GET  /api/admin/page-workbench/pages/{pageId}/row
POST /api/admin/page-workbench/pages/bootstrap
POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/bootstrap
GET  /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor
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
  `site_header`, `site_footer_practices`, `site_footer`, `global_price`, and the non-versioned settings
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

The endpoint should return only menu items that can be opened now. Target-state items from the long-term
requirements may stay documented, but unfinished entries should not be returned as disabled/planned nodes
in the runtime menu. This keeps the CMS sidebar a working tool rather than a map of promises.

Indicators are optional and should be included only when requested:

- `GET /api/admin/navigation?locale=uk` may return the tree without stats;
- `GET /api/admin/navigation?locale=uk&includeIndicators=true` returns the same tree with lightweight
  `indicators`;
- the response includes `generatedAt`, an ISO timestamp showing when the backend assembled the menu and
  indicators;
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
  overridden fields, or disabled price sections. For `site_header`, `site_footer_practices`, and
  `site_footer`, snapshot impact should be zero/empty because they are layout payload sources, not page
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
GET  /api/admin/global-sections/{sectionKey}/editor?locale=uk
POST /api/admin/global-sections/{sectionKey}/draft?locale=uk
POST /api/admin/global-sections/{sectionKey}/validate?locale=uk
POST /api/admin/global-sections/{sectionKey}/publish?locale=uk
GET  /api/admin/global-sections/{sectionKey}/history?locale=uk&limit=50&offset=0
POST /api/admin/global-sections/{sectionKey}/rollback?locale=uk
```

Supported editable section keys now:

- `site_header`;
- `site_footer_practices` as a read-only/global diagnostics workbench;
- `site_footer`;
- `global_price`.

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
header, contact settings, version history, grouped diagnostics, and exact
action endpoints. This lets the screen render the editable flags, read-only
navigation/services menu, phone/work-time panel, and history list without
manually stitching several initial requests together.

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

Generated `practice_page`, `service_page`, and `problem_page` schemas also expose an optional page
`price` slot. This slot is not edited through the global section screen. It is a page-owned section with
`sourcePolicy: "price_inheritance"`:

- base non-regional generated pages source their page `price` from the locale-specific `global_price`;
- regional generated pages source their page `price` from the matching base non-regional page price
  section;
- the page `price` may inherit the source, override allowed fields, or append allowed list/rich-text
  fields;
- public snapshots store the resolved price payload and keep separate source/local section refs for
  diagnostics and rollback.

This means the global price screen edits the shared source, while the page section editor edits the local
page/regional layer. Header/footer remain direct shared globals and do not create page-local section
versions.

Price preview modes are intentionally separate:

- `latest_draft` preview composes the latest available source draft/published version with the latest
  available local draft/published version;
- `published` preview composes only the current published source and local versions, even if newer drafts
  already exist.

The public snapshot/publish path uses the same backend composition rule as `published` preview: the
snapshot stores only the resolved price payload, while section refs keep the exact source/local versions
that produced it.

Global sections are locale-specific. Opening the editor for `site_footer?locale=uk` reads or creates the
Ukrainian global footer section record. Russian and English versions are separate section records and
separate version histories.

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

Publishing `global_price` uses affected page snapshot rebuild: backend creates the new published price
source and plans/rebuilds affected page snapshots without touching unrelated page-owned draft sections.

The publish response contains:

- `publish.publishedVersionId`: the new published section version;
- `publish.affectedPages`: pages that depend on this global section; for layout globals this may be empty;
- `publish.affectedBindings`: exact page-section bindings affected by the new section version; for layout
  globals this may be empty;
- `publish.rebuiltSnapshots`: rebuild result per affected page, with `status = rebuilt | skipped | failed`;
  for layout globals this may be empty;
- `editor`: fresh global-section editor state after publish.

For the UI this means: show publish success from `publishedVersionId`. Show rebuild impact from
`rebuiltSnapshots` only when the section actually uses snapshot rebuild, currently `global_price`.
For `site_header`/`site_footer_practices`/`site_footer`, the important follow-up is layout preview/public
layout refresh, not page workbench rebuild.

For `global_price`, affected rebuilds apply to pages that directly depend on the global source, normally
the base non-regional generated pages. Regional pages depend on the base page price layer and should be
reviewed/republished through the regional page workflow when that layer changes.

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
- optional `sourcePolicy` for special source resolution. Currently only `price_inheritance` exists.

The frontend should use this endpoint to build page creation forms and section editors. Do not hardcode
the available page types, slots, route params, or field lists in the frontend.

## Page Workbench

Use:

```text
GET /api/admin/page-workbench/tree?locale=uk
GET /api/admin/page-workbench/service-tree?locale=uk
GET /api/admin/page-workbench/page-types/{pageType}?locale=uk
GET /api/admin/page-workbench/pages/{pageId}/row
POST /api/admin/page-workbench/pages/bootstrap
POST /api/admin/page-workbench/generated-sources/{pageType}/{sourceId}/bootstrap?locale=uk
GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor
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
- row-level `diagnostics`: publish blockers and warnings for the whole page;
- `cells`: one summary cell per section/runtime slot;
- `summary`: counters for the whole opened matrix. `summary.errors` and `summary.warnings` are row-level
  counters, so page diagnostics such as `PAGE_NOT_CREATED` are included, not only section cell diagnostics.

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

- `practice_collection_page`: one synthetic source row, not an ERP object. It has no `practiceId` and
  always uses `pagePath = "services"`;
- `practice_page`: one visible practice;
- `service_page`: one visible service with `serviceCond=true` and a resolved visible practice;
- `problem_page`: one visible problem with resolved visible practice and service.

For `practice_collection_page`, `practice_page`, `service_page`, and `problem_page`, the matrix now
returns both:

- base non-regional rows, for example `/services/family-law`;
- regional rows for visible regions with a valid `sourceSlug`, for example `/kyiv/services/family-law`.

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
Use row-level route fields for UI display. `sourceRecord.pagePath` / `sourceRecord.publicPath` still
describe the base source route; regional rows may have a different `row.publicPath`. Prefer backend-owned
generated bootstrap:

```text
POST /api/admin/page-workbench/generated-sources/practice_collection_page/practice_collection/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/practice_page/{sourceRecord.id}/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/service_page/{sourceRecord.id}/bootstrap?locale=uk
POST /api/admin/page-workbench/generated-sources/problem_page/{sourceRecord.id}/bootstrap?locale=uk
```

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

The workbench page action endpoints wrap the same lifecycle logic as `POST /api/admin/pages/{pageId}/...`,
but they also return `workbench`, a fresh row-refresh payload for the affected page:

- `POST /pages/{pageId}/preview`: returns `{ preview, workbench }`;
- `POST /pages/{pageId}/publish`: returns `{ publish, workbench }`;
- `POST /pages/{pageId}/rollback`: returns `{ rollback, workbench }`.

Use these endpoints for page buttons on the matrix screen. The request bodies are the same as the existing
page lifecycle endpoints. After a successful action, replace the row with `response.workbench.row` and keep
using backend-provided `actions`/`diagnostics`.

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
route-ready items. For `practice_collection_page`, the base page lists all visible practices; regional rows
list visible practices that have an active region qualification for the selected visible region. If the
frontend sends a `runtimePayloads` entry for one of these slots, backend keeps the provided payload and does
not resolve that same slot again. This is mainly useful for tests or transitional UI experiments; normal CMS
frontend code should let backend resolve service-tree runtime slots.

Runtime resolution can block preview/publish with `PAGE_RUNTIME_RESOLUTION_FAILED` when the page route no
longer matches visible reference data or a visible child item has no required source slug. Show this as a
backend validation error and route the editor to fix the underlying reference object.

Snapshot history endpoints support the rollback UI:

- `GET /pages/{pageId}/snapshots`: returns historical page snapshots, newest first;
- `GET /pages/{pageId}/snapshots/{snapshotId}`: returns one snapshot with its public payload.

Use the list endpoint to open the page history panel. Each item contains:

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

- `practice_services_block` + `practice_services` use `practice_services`;
- `practice_lawyers_block` + `practice_lawyers` use `practice_lawyers`;
- `service_problems_block` + `service_problems` use `service_problems`;
- `service_lawyers_block` + `service_lawyers` use `service_lawyers`;
- `problem_lawyers_block` + `problem_lawyers` use `problem_lawyers`.

The `*_block` section stores CMS-authored title/lead/settings for the block. The runtime slot stores the
read-only list contract. Optional page-owned `*_faq` and `*_consultation_cta` sections are also present
and may be enabled/disabled through backend-provided actions. Price sections are modeled as source-backed
page-owned sections: base generated pages inherit from `global_price`, while regional generated pages
inherit from the matching base page price section.

Section cells contain only metadata and status:

- ids: `bindingId`, `sectionId`, `sourceSectionId`, `localSectionId`;
- state: `visibility`, `draftStatus`, `draftVersion`, `publishedVersion`;
- ownership/publish info: `ownershipScope`, `publishMode`, `composition`;
- `diagnostics`: errors, warnings, missing published version, stale state;
- `actions`: what the UI may show (`canOpen`, `canEdit`, `canSaveDraft`, `canPublish`, etc.).
- `actions.canEnable` / `actions.canDisable`: show section visibility controls computed by the backend.

Section cells do not contain section content. When the editor opens one cell, load the full edit state
through `GET /api/admin/page-workbench/pages/{pageId}/sections/{slotKey}/editor`.

Runtime cells represent read-model data, not editable CMS drafts. They expose `source` metadata and should
be shown as read-only blocks in the matrix.

Use row-level `actions` for page buttons:

- `actions.canBootstrap`: show create/bootstrap page action when the row is not created yet;
- `actions.canOpen`: open page authoring state;
- `actions.canPreview`: allow preview build for the current draft/published mix;
- `actions.canPublish`: allow page publish;
- `actions.canRollback`: allow rollback flow only when the page already has a current snapshot;
- `actions.canViewCurrentSnapshot`: show current public snapshot details.

Use row-level `diagnostics.blockingReasons` for page banners/tooltips. The frontend should display the
messages and codes, but should not recreate the rules. Important codes:

- `PAGE_NOT_CREATED`;
- `PAGE_SECTION_DRAFT_STALE`;
- `PAGE_SECTION_VALIDATION_FAILED`;
- `PAGE_REQUIRED_SECTION_EMPTY`;
- `PAGE_REQUIRED_INDEPENDENT_SECTION_NOT_PUBLISHED`;
- `PAGE_NO_CURRENT_SNAPSHOT`.

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
page requires review before publish. The catalog does not replace `GET /api/admin/pages/{pageId}/authoring`;
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
The response returns `ok`, `errors`, `validationRunId`, and a reloaded `editor` payload.
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
- `createdBy`, `createdAt`, `publishedBy`, `publishedAt`;
- `isCurrentDraft` and `isCurrentPublished`;
- `canRollback`, which is true only for published versions.

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
- Warning diagnostics: currently critical validation is the main blocker; field-level warnings will become
  part of section/page diagnostics without blocking every save.
- Typed client generation: OpenAPI should remain the source for DTOs; frontend should prefer generated
  clients when that pipeline is connected.

## UI Notes

- Show `draft_stale` clearly: the page/section requires review before publish.
- Keep preview and published/current state visually distinct.
- Do not allow editing runtime slots directly from the page section draft form.
- Do not infer publishability only from visible fields. Backend publish validation is the final authority.
