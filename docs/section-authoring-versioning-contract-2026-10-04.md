# Section Authoring and Publication Contract

Decision date: 2026-10-04.

Status: agreed product direction and implementation requirements. A local candidate for the first
backend stage is documented under Implementation status; this is not a completed rollout or a completed
publication transition. The specification itself does not authorize schema execution or runtime changes.
The no-change Save policy below was explicitly confirmed by the user on the decision date.

This contract defines how CMS editors inspect section history, prepare a working copy, save immutable
content, and publish a saved version. It applies to editable page-owned and global-owned section
authoring. It supersedes older requirements that make taking a version as a basis immediately persist
a draft, restrict that action solely because a version is currently published or is the latest draft,
or require ordinary publication to duplicate already saved content.

The target user workflow is:

`View a saved version -> Take as basis -> Edit working copy -> Save version 5 -> Publish version 5`

## Scope and authority

This document owns the common workflow and reliability rules. Section-specific schemas still own their
fields, validation, locale, composition, ownership, and independent versus with-page publication policy.
The related documents must be read with this contract:

- [Section model foundation](section-model-foundation.md).
- [Backend implementation requirements](backend-implementation-requirements.md).
- [CMS frontend page authoring](cms-front-page-authoring-task.md).
- [Global price workbench](global-price-section-workbench.md).
- [Footer workbench](site-footer-section-workbench.md).
- [Layout and header requirements](site-layout-and-header-requirements.md).
- [Development sequencing](development-sequencing-and-module-plan.md).

Existing endpoint examples and dated implementation notes in those documents describe the compatibility
surface until implementation of this contract is verified. They are not permission to retain the old
copy-to-database workflow in the new editor. Shared cloud and deployment rules remain governed by the
sibling `gcp-infra-playbook`; this contract does not override them or authorize a deployment.

Out of scope:

- cloning a section into a different independent section identity;
- making ERP-owned, runtime, generated, or system-owned fields editable;
- introducing version history for non-versioned operational settings;
- changing locale rules or translating content between section identities;
- autosave, recovery after a browser restart, or automatic merging of concurrent edits;
- directly activating arbitrary historical section versions as a new restore workflow;
- deleting duplicate historical rows, renumbering history, or rewriting old snapshot references;
- changing public page snapshot rollback, section schemas, or header feature behavior.

## Content and publication concepts

| Concept | Meaning | Allowed changes |
| --- | --- | --- |
| Working copy | Client-held editable authoring content, optionally based on a saved version | Changes locally until explicit Save |
| Saved content version | Immutable authoring content belonging to one section identity and its declared locale scope | Content, identity, creation author/time, and source provenance never change |
| Publication event | Audit record identifying which saved version was activated, by whom, and when | Activation audit is append-only; original target, actor, and time are preserved |
| Current publication | Pointer or equivalent authoritative state identifying the active version | Changes only through an authorized publication workflow |
| Page snapshot | Immutable resolved public result with exact section references | A new result creates a new snapshot; historical snapshots are preserved |

Content immutability does not require a second identical content row at publication. Publication
metadata and current pointers are distinct from the authored content. A version that was published
previously is not necessarily the version active now. An inactive version remains available in history.

Validation results, current pointers, and propagation progress may be refreshed separately. They must
not overwrite the saved version's creation/provenance facts or replace earlier publication events with
one mutable last-publication timestamp. This audit rule does not require a project-wide event-sourcing
rewrite or dictate physical table names.

Legacy `draft` and `published` rows remain readable with their original IDs and numbers. They must not
be silently merged or relabelled as if a storage migration had already happened. In the transition,
clients must use the backend's explicit workflow state rather than infer actions from those enum names.

## Working copy and history

The editor must expose three separate actions with unambiguous meaning:

1. View saved content in read-only mode.
2. Take saved authoring content as the basis of a working copy.
3. Create an empty working copy from the section's allowed editable structure.

These actions do not create section versions, create another section identity, move current pointers,
change page bindings, publish content, or mark dependent pages stale. Any necessary explicit section or
page bootstrap is a separate operation, not a hidden effect of viewing or taking content as a basis.

Any accessible saved authoring version of the same editable section can be a basis, including the latest
saved version, the current published version, a former published version, and a legacy draft already
used by publication. A source can be reused more than once; taking it as a basis does not consume it.
Authorization, section identity, locale, and schema restrictions still apply.

Only editable authoring fields enter the buffer. Resolved public content, runtime data, readonly registry
text, source-only fields, and inherited presentation values must not become local overrides merely
because the editor viewed them. Page-owned composition controls retain their existing schema rules.

The UI keeps selected history and the working buffer as separate state. Viewing another saved version
must not destroy the buffer. The user must be able to return to it without a save. Saved history is
read-only for authored content even when it is the latest version; content editing always happens in
the working copy. The optional editorial version name below is a separate mutable metadata exception.

The working copy is visibly separate from stored history, with an unsaved indicator and either its
source version number or an empty-source label. Before saving it has no stored version ID, saved timestamp,
or publication action. Copying a whole section to another independent entity is not part of this UI.

Replacing a modified buffer, switching locale or section, or leaving the editor requires protection
against accidental loss. Cancellation preserves the buffer. Validation errors, conflicts, timeouts, and
other failed saves must not clear entered values. A pending or uncertain save response must not be
represented as success. Browser refresh or crash recovery is not promised without a separately specified
mechanism; the interface must not imply that local unsaved changes are stored on the server.

For initial selection, the UI should prefer a genuine saved unpublished working version when present;
otherwise it should present the current publication, or the empty state if no version exists. It must
not mistake a legacy draft already consumed by the active publication for a new unpublished change.
The detailed initial-focus presentation belongs to frontend implementation and must preserve these
invariants; opening a screen does not itself persist a working copy.

## Editorial version names (decision 2026-10-06)

Each saved section version may have an optional user-defined internal name. It is a navigation aid
for editors, not a public section heading, a status, or source provenance. Display the name separately
from the system status and `Based on #N`. Do not repurpose `changeOrigin.label`.

- Names are plain single-line text, up to 160 Unicode characters after outer whitespace trimming.
  Blank input clears the name to null. Names need not be unique; version UUID and number remain the
  identity. Render names as text, never HTML.
- Renaming is permitted on accessible editable saved versions, including historical, archived and
  currently published versions. A disabled local section does not prevent renaming its saved content.
  Runtime/system-only sections and inherited source versions remain read-only in the consuming context.
- A dedicated rename command requires section-write permission, exact version ownership and the
  expected **name revision**. Concurrent renames conflict rather than overwrite each other. A matching
  revision with the same normalized name is a no-op. Name author/time/revision are recorded separately
  from original content authorship, creation time and provenance.
- Renaming never creates a content version, changes its number/ID/content, moves heads, publishes,
  invalidates validation, changes authoring/publication tokens, makes dependents stale or rebuilds
  snapshots. Internal names and their audit metadata do not enter public payloads.
- Taking a version as a basis does not rename it or copy its name into another stored version. A new
  content version starts unnamed. The frontend may hold an intended name locally and apply it through
  the rename command after successful content Save using the exact `savedVersionId`. If Save returns
  an existing version (`created: false`), changing its name is an explicit rename of that same version,
  not a reason to create a duplicate. A failed rename must not trigger another content Save.
- A name belongs to an exact stored row, not its descendants. Legacy copy-on-publication produces a
  separate unnamed row; the original row retains its name. Same-row publication retains the name
  because identity stays the same. Do not infer identity from matching content or provenance.

Before content Save, a local working copy still has no stored version ID, number or saved timestamp.
The UI must distinguish unsaved content from a pending metadata rename. After a rename timeout, read
the exact version metadata before retrying; never auto-retry with a freshly fetched revision over
another editor's intervening name.

The backend implementation/API details are maintained in `CMS-back/docs/section-authoring-safe-save.md`.
This decision authorizes implementation, not shared-DB migration execution or deployment.

## Save contract

Only explicit Save persists the working content as a new immutable authoring version, subject to the
section's existing save validation rules and the no-change policy below. Older content is not updated
in place. Save does not publish content or change what the public site serves.

The logical save contract must carry:

- section identity and applicable authoring context;
- editable content and allowed composition changes, where that editor supports them;
- source version identity when the buffer was based on a saved version;
- expected current authoring state for conflict detection;
- a retry identity for this particular logical save operation.

Names such as `sourceRevisionId`, `expectedHeadRevisionId`, and `idempotencyKey` describe required
semantics here, not shipped JSON fields. Actor identity comes from authenticated server context, not
from a client-authoritative author name. Wire DTOs, errors, and capability names are a backend contract
deliverable before frontend implementation starts.

Source provenance and conflict detection must remain independent. If the editor takes version 3 as a
basis while version 5 is current, provenance is version 3 and the expected current state is version 5.
The same rule applies to an empty buffer: it has no source but still needs a concurrency expectation.

On conflict the server must not silently replace the current state. The response must identify that
newer state exists and allow the client to retain the submitted buffer for explicit reconciliation.
No automatic merge or last-writer-wins overwrite is introduced by this contract.

An accepted new save creates its version, provenance, applicable binding/composition changes, and
current authoring pointer atomically. Existing dependent-draft policies apply after a committed save,
not when the editor merely prepares a buffer. Server-side authorization and validation remain mandatory.

On success the response identifies the exact saved version and refreshes authoritative editor state.
The client may continue editing from that saved basis, but subsequent edits again exist only in its
working buffer. The recorded version never becomes mutable.

A successful response acknowledges the submitted buffer, not any newer text typed while that request
was in flight. Keep those later edits and reconcile their source/expected state with the acknowledged
save; do not overwrite them with response content or mark them saved. Stale history/refresh responses
must not replace a more recent selected view or working buffer either.

### Save without content changes

An explicit Save whose authoring state equals the latest saved authoring state returns the existing
version as unchanged without creating a duplicate. The response must distinguish this successful
no-change outcome from a rejected save and from creation of a new version. Equality
must be defined over the allowed authoring content and relevant composition, not resolved runtime
payloads or incidental JSON serialization. Restoring version 3 when the current authoring state is
different still produces a new saved restoration version, even if the buffer was not edited after
taking version 3 as its basis. Preserve existing IDs and content; do not search the whole history to
reactivate an older matching record as an implicit side effect of Save. For a legacy section, the backend
must expose the exact current saved authoring baseline rather than let the client infer it from enum
labels or the greatest version number.

Authorization, current-state conflict checks, and applicable validation run before accepting a
no-change outcome. An outdated request is not silently accepted merely because its content happens to
match. A no-change Save does not move current pointers, reset provenance, publish, or emit dependent
draft changes. The frontend may disable Save when equality is already known, but the server must enforce
this rule even for direct requests.

This policy is separate from retry safety: repeating the same logical network request must never
produce an extra version. Intentional restoration of different old content and a network retry are
different operations.

## Publication contract

Ordinary publication names an exact saved version belonging to the authorized section. It revalidates
that version against current publication requirements and applicable dependencies, records publication
audit metadata, and activates that same content version. It does not create an identical content version
only to distinguish `draft` from `published`.

Publication never includes unsaved browser changes implicitly. If version 6 is saved while publication
of version 5 is underway, the command must not silently switch to version 6 or erase its unpublished
status. Conflicting activation of the current publication must also be detected against an expected
state rather than silently overwriting another editor's intervening publication.

Version content, publication audit history, current activation, and dependent page rebuild outcome
must be separately representable. Activation audit and the corresponding current pointer must commit
atomically. Repeating the same publication request after a timeout returns its established outcome
without a second activation event or repeated uncontrolled side effects.

This scope does not add a new general-purpose button to reactivate any historical section version.
The normal restore flow is View -> Take as basis -> Save -> Publish with current validation. Existing
page snapshot rollback remains a different operation with its existing snapshot semantics.

Republishing or rebuilding an affected page must not require a fake content edit or an identical new
section version. Identical section content does not prove that all resolved dependencies or public
output are unchanged. Recovery of failed page rebuilds must be distinct from making new authoring
versions. A future explicit repeated activation operation, if needed, requires a defined audit and
retry policy; this contract does not invent that user operation.

## Page assembly and propagation boundaries

The same-version publication rule applies when the saved authoring content to publish already exists.
It does not prohibit creating a necessary version when publication first materializes inherited or
composed content into an independently stored local result. Such materialization is not duplication
solely for a lifecycle label and must retain provenance and exact snapshot references.

For `with_page` sections, section publication, required materialization, and the new page snapshot must
succeed atomically. Failure must not leave a partially activated section/page combination. Public
snapshots keep the resolved output and historical references needed for reliable page rollback.

For independent global sections, activation may succeed even when some dependent page rebuilds fail
or are skipped under existing policy. Responses and diagnostics must report the activated section and
per-page outcomes separately. Retry of failed rebuilds must not be confused with repeating a section
content save. Existing stale-dependency policies, enabled state, inheritance, and page assembly remain
backend-owned and must not be reconstructed independently in the frontend.

The 2026-10-12 [stale-page refresh contract](stale-page-refresh-contract-2026-10-12.md) specifies the
shared queue for published consumer updates. A source publication can trigger delayed/coalesced
refresh, while source Save alone cannot publish its working content. Public freshness and working
inheritance review remain independent. Coalescing demand never rewrites an already accepted immutable
publication plan or receipt. This addition does not itself activate the new writer or scheduling mode.

Header/footer layout delivery stays separate from page-owned snapshot content under the existing
layout contract. Runtime slots and non-versioned settings do not acquire a fake draft/history workflow.

## State and action consistency

The backend must return authoritative states consistently to editor, history, navigation, and page
workbench. At minimum clients must be able to distinguish a current publication, older publications,
genuine saved unpublished work, validation results, dependency staleness, and incomplete propagation.
Local unsaved changes are a separate frontend state, not a server draft/version.

One boolean for the existence of a legacy draft is not sufficient to signal unpublished changes.
Likewise, the largest version number must not be used as a substitute for backend action permissions.

Capabilities must distinguish read-only inspection, taking authoring content as a basis, saving,
publishing, site preview, and page snapshot rollback. Do not globally alias `canView` to `canPreview`
or copying to `canRollback`. Use explicit typed semantics/adapters for each endpoint family. Backend
command handlers enforce the same constraints; hiding a button is not authorization.

## Compatibility and implementation sequence

The sequence has independent acceptance gates. Each stage must identify which behavior is supported,
which endpoints remain legacy, and what is not implemented yet.

| Stage | Owner | Deliverable and gate |
| --- | --- | --- |
| Contract | Backend and product, with frontend review | This specification, concrete wire/error/action contract, regression scenarios |
| Safe authoring backend | Backend | Consistent read models, exact history reads, save provenance, conflict checks, retry safety, atomic writes; existing clients remain compatible |
| Working copy editor | CMS frontend, Yuri | Local buffer and readonly history, no persistent copy call, loss protection, new save contract; browser acceptance on one editor then remaining families |
| Publication transition | Backend with frontend integration | Same-version publication, activation history, legacy reads, assembly and diagnostics compatibility; no new-format writes before rollback/read compatibility is proven |
| Acceptance | Backend and frontend | Develop end-to-end tests, compatibility and failure checks, then separately authorized release work |

The working-copy stage intentionally does not by itself remove the legacy publication duplicate. Its
acceptance must not be advertised as completion of same-version publication.

The old `createDraftFromVersion` and section rollback-to-draft endpoints must not be used to implement
Take as basis. They remain a clearly identified compatibility surface until consumers are inventoried
and migrated. Their removal is a separate compatibility decision, not a prerequisite for the local form.

Preserve existing IDs, numbers, content, and snapshot references. Do not rewrite history to simulate
the new model. Storage changes, if required, must be additive or otherwise have an explicitly reviewed
compatibility plan. Enumerate all consumers of legacy lifecycle states before enabling new writes.

No service deployment, schema migration, page republish, or content mutation is authorized by recording
these requirements. Follow the governing playbook and obtain the required separate approvals. Before
enabling a new persisted format, prove that the designated rollback application version can read data
created by the new version; reverting an arbitrary old binary is not an adequate rollback plan.

## Acceptance checks

| Scenario | Required result | Verification level |
| --- | --- | --- |
| View, take as basis, create empty buffer, cancel | No new authoring records, changed pointers, bindings, or public state | API and browser |
| Edit from any accessible same-section saved version | Only the buffer changes; source content is intact and provenance is retained on Save | Unit, API, browser |
| Read history and return to the buffer | Unsaved content is preserved; historical content stays readonly | Browser |
| Replace buffer, switch locale, leave editor | Unsaved-change protection applies; cancel preserves work | Browser |
| Validation error, conflict, timeout | Entered content stays visible; no false success | API and browser |
| Continue typing while Save is in flight or receive refreshes out of order | Only submitted content is acknowledged; newer input and the latest chosen view survive | Browser and API |
| Save equals current saved authoring state | Existing version returned as unchanged; no new row, pointer movement, or dependent-draft event | Unit and database integration |
| Restore version 3 differing from current version 5 without further editing | New saved restoration version, with version 3 provenance; no implicit activation of version 3 | Unit and database integration |
| Two editors save from the same expected state | No silent head overwrite; one operation reports a conflict | Database integration |
| Source version 3 and expected head version 5 | Source and concurrency expectation are not conflated | Unit and database integration |
| Double-click or lost response followed by retry | One logical save/publication has one recorded outcome | API and database integration |
| Failure between record creation and pointer update | No partially applied operation | Database fault injection |
| Save version 6 during publication of version 5 | Version 5 is the explicit target; version 6 remains correctly represented | Database integration |
| Invalid content or unauthorized version/context | Publication is rejected without activation; permissions cannot be bypassed via direct API calls | Unit and API |
| With-page inheritance and materialization | Required materialization and snapshot activation are atomic | Database integration and snapshot regression |
| Independent activation with partial rebuild failure | Section activation and each affected page outcome are explicit and retryable | Integration |
| Page rebuild with unchanged section content | No artificial section content revision is required | Integration |
| Legacy history and page snapshot rollback | Original records remain readable and historical references reproduce the existing result | Migration fixture and snapshot regression |
| Later validation, activation, or propagation updates | Original version creation/provenance and earlier publication audit remain unchanged | Database integration |
| Readonly, ERP, runtime, and system fields | Taking a basis does not unlock or persist protected fields | Unit, API, browser |
| Prior supported client against upgraded backend | Compatible read/write behavior or explicit negotiated refusal, never silent corruption | Contract integration |
| Application rollback after new-format writes | Designated rollback version can safely read the resulting persisted state | Compatibility test |

Unit tests alone do not establish acceptance. Concurrency and atomicity require integration tests on a
non-live test database. Buffer preservation and action routing require browser tests. Fixture checks
must include legacy drafts, current and former publications, inherited sections, and old page snapshots.

Stop the transition if old snapshots/history stop reading, unsaved work can be silently lost, commands
substitute an implicit latest version, retries create uncontrolled duplicates, propagation failures are
reported as complete success, or rollback compatibility is unproven.

## Implementation status

The specification was recorded before implementation. On 2026-10-04 a local backend candidate for the
Safe authoring backend stage was prepared in `cms-back`, branch `codex/section-authoring-safe-save`.
Its concrete wire contract and compatibility boundaries are documented in that repository at
`docs/section-authoring-safe-save.md`.

The candidate covers readonly global/page-section authoring and exact history, source provenance,
guarded no-op Save, concurrency tokens, durable request receipts, atomic head/binding/composition and
stale-dependency writes, and consumed-draft status. Existing clients retain legacy Save semantics unless
they opt into the guard; the new working-copy endpoints require it. The additive receipt migration is
prepared but has not been executed. No existing history or public snapshots were rewritten.

Local compilation and all 1,259 contract/unit tests passed. A separate isolated MySQL 8.0.43 run passed
15 real concurrency/fault checks, including both save/publication orderings, and removed its generated
test database. The read-only migration inspector passed 27 isolated checks. Browser working-copy
acceptance belongs to the frontend stage. The owner subsequently approved source publication,
migration and deployment to develop, then release; actual rollout results are recorded separately in
the governing playbook. Same-version publication and activation audit remain unimplemented future
work; legacy draft-to-published copying is intentionally preserved.
