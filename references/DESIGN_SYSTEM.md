# Forma — Quiet Precision

## Intent

A compact, calm application foundation. Prefer useful hierarchy, direct labels, consistent surfaces and legible information over decorative cards. The engine and first-party modules should consume the same reusable UI contracts; the standalone mockup is a reference implementation, not the production component library.

## Shared tokens (V33)

| Token | Light | Dark |
|---|---|---|
| Surface | #ffffff | #20232a |
| Raised | #fafbfc | #262a32 |
| Text | #23252b | #e8eaf0 |
| Muted | #666d78 | #a7afbd |
| Border | #e1e4e9 | #3b414d |
| Soft/selected | #eff1f4 | #303641 |
| Action | #292d36 | #b6c7e3 |
| On action | #ffffff | #17202c |
| Focus | #7790b3 | #a9c0e9 |
| Success | #386c52 | #8bc6a3 |
| Warning | #91652d | #e3bb78 |
| Error | #ad4449 | #f1a3a5 |

Base text 13px, metadata 11px, compact control 30px, standard 34px, comfortable 38px. Row baselines 34/39/45px. Main spacing increments 4px; use 8/12/16/20 for internal groups. Radius 6px, overlays 9px, one low elevation for surfaces and a stronger elevation for overlays only. Use text and icons alongside state colors. Focus ring visible, reduced-motion preference respected.

## Shell and navigation

Primary icon rail + contextual navigation + main content + assistant side panel. Whole canvas shifts to reveal navigation/assistant. No floating navigation drawer. Desktop contextual width adjustable 168–256px. Mobile retains the canvas motion and uses a dedicated bottom launcher dock; mobile preview bubble suppressed to prevent obscured controls. Full-screen authoring tools omit the launcher. Large forms may use a full-screen dialog; context actions use a sheet on mobile.

## Layout templates (V34.1)

Layout work starts from a template, not from a component. Model every screen as **Application Shell × Content Layout**:

- Application shell: primary rail, context sidebar, top bar or top navigation, workspace toolbar and assistant sidebar. It owns canvas sliding.
- Content layout: page header, toolbar, content, split panes, properties inspector and footer. It never replaces the shell.
- Templates: `sidebar`, `semi`, `full`, `fullscreen`, `split`, `centered`, `inspector`, `public`. Read `LAYOUT_REGISTRY.json`; do not invent a ninth template without an approved registry change.
- Layout identities are explicit: `Core.Layout.<Template>` on the content root, `Core.Layout.<Slot>` on every slot, plus `data-ui-id` and `data-layout-slot`. Shell and content stay separate in markup and data.
- Public keeps the existing `publiccanvas` exception: no canvas slide and no assistant. Fullscreen suppresses the mobile launcher, matching editor behavior.
- The layout playground previews inside a container-scoped in-page stage (not an iframe). Fixed simulated widths (1440/768/390/320) scroll inside their stage only; the document never overflows.

Slot labels occupy a reserved top band instead of floating over content (30px inside content slots, 66px on the primary rail). Each label names the stable slot and its semantic component, for example `content · Core.Layout.Content`. General labels use 10px and the rail uses 9px; text wraps rather than truncating the identity. Toggle labels without removing Inspector identities and never allow them to overlap content or create horizontal page overflow.

Provisional layout tokens: inspector 280px (240–320), split list 320px (280–360), content measure 960px standard / 680px narrow, centered card 420px, slot label 11px with a 4px radius. Keep controls compact 30px, standard 34px and touch 44px at ≤768px. Use existing semantic color pairs only; reduced motion removes sliding transitions.

## Touch and pointer interactions (V34.2)

Use one shared Pointer Events engine for mouse, touch and pen. Real modules use model callbacks (`defineSortable({apply,undo,redo})`) so drag results survive re-render; the shell uses a 20px edge gesture and existing shift classes. Keyboard Space/Arrow/Space/Escape mirrors pointer reorder with one live announcement per state change. Modules subscribe to `formatouch:*` events or `data-touch*` / `data-sortable*` attributes; they never add their own touch recognizer. Tap slop is 8px, drag threshold 6px, long press 500ms, double tap 320ms, auto-scroll edge 44px. Release pointer capture on pointerup, pointercancel, lostpointercapture, blur and tab hide. Suppress only the click that follows a gesture.

Sortable and drag surfaces use a handle, ghost and placeholder with same-group containers, cross-container/nested moves, keyboard Alt+Arrow, undo and real local state. Touch targets are 44–48px inside safe areas, including Files, Directory, Theme builder and the Layout Playground split separator; dynamic viewport and visualViewport keyboard handling are required. Keep non-hover fallbacks and persistent live announcements of gesture, pointer type and component identity. Physical-device verification remains Pending Owner Review.

## Reusable component contracts

These are implementation handoff contracts, not backend contracts.

- Field: label, value, required, help, error, disabled, read-only; emit change/blur; preserve input across validation.
- Select/record picker: options or a registered source, identity key, label, selection mode, search, loading, no results; emit selected IDs; restore focus.
- Date/range: canonical date values; explicit range apply; keyboard navigation; localized display. Do not mutate saved dates merely because timezone display changed.
- Collection: stable row IDs, search/filter/sort, paging, selection, bulk actions, adaptive list; no horizontal scrolling for data tables.
- Detail: identity header, metadata, tabs, relationships, timeline, attachments, status and edit action; navigate back without losing collection state.
- Modal/confirmation: title, description, intent, buttons, optional body; top-layer focus trap and restore focus; distinguish destructive actions; never treat dismissal as approval.
- Toast/banner: kind, message, action when relevant, dismiss; errors remain understandable without color.
- File viewer: asset reference, metadata, MIME-appropriate preview/fallback, zoom/navigation/download. Never copy file content unnecessarily for mere attachments.
- Workspace editor: list/details own document lifecycle, full-screen editor owns an edit session; layers/canvas/inspector, draft/published separation, undo/redo, breakpoint preview and export.
- AI action UI: select a single registered action, gather inputs, render the exact proposal, explicitly confirm, support edit/cancel/expiry/error, render typed result/reference. Backend authorization is independent of UI confirmation. V33 never executes real writes.

## Responsive and frontend

Use container queries for data and editor layouts; do not assume viewport equals content width. Keep visual checkbox/radio dimensions at 16px independent of 44px touch rows. Test 1920/1440/1280/1024/768/430/390/320 widths. On narrow screens use structured records, stacked sections and one editor pane at a time. Public pages use a separate responsive header/navigation/footer and customer account layout. Published content derives from published snapshots, not drafts. Theme for editor controls is separate from website/document design.

## Acceptance

Use `UI foundation` as the index. Review screenshots and interactions together. Implementation should replace duplicate legacy code with shared component exports gradually, rather than reproducing mockup version-specific wrappers. Do not declare design freeze before owner visual review and closure of the review backlog.
