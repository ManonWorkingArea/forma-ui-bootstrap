# Forma UI Inspector v1.0

## Usage

Open standalone.html, navigate to a page and choose Debug (top bar on larger screens; bottom-left on narrow screens or editor routes). Alt+Shift+D toggles the inspector. The panel can collapse and expand. Debug is off on initial load. It is local-only, uses no network, and does not change application data.

- Components: named UI patterns, common controls and semantic regions.
- Controls: interactive controls and mapped control components.
- All elements: rendered HTML elements, excluding debug UI, decorative SVG internals and non-rendered elements.
- Labels: toggle names; IDs: show the instance suffix alongside the component name.
- Filter: component, full reference or label text.
- Pick: intercepts the next element click/tap instead of activating its normal action; Parent selects the nearest mapped ancestor (or direct parent in All elements mode).
- Copy reference: copies structured JSON, or shows a selectable textarea if the clipboard API is unavailable.
- Export visible JSON: exports the inventory for the current viewport and filter.
- Open dialogs are inspected in isolation. The CMS visual editor has its own embedded inspector. Other sandboxed previews and browser-native file/PDF controls are outside scope.

## Reference naming contract

A canonical component name (e.g. `Core.DataTable.Toolbar`, `Core.Button`, `Core.AI.ActionCard`, `Files.Picker`, `Studio.Canvas`) is independent of the UI's presentation language. A reference combines route, canonical component name and a hash of a deterministic DOM path. For example:

`pilot/admin/catalog#Core.Button@1vrx2c5`

This is the Filter button in the current Catalog specimen. Its reference was verified across a re-render and the desktop/mobile examples. The same type may have many instances, so communicate the route, reference, visible label and source hint, not the type alone. Fallback hashes are NOT guaranteed across DOM restructure, reordered records or route changes. For production, author explicit semantic identity:

```html
<button data-ui-component="Core.Button" data-ui-id="catalog.filter.open">Filter</button>
```

`data-ui-component` takes precedence over the selector mapping. Explicit `Core.Layout.*` names and any element with `data-layout-slot` are classified as `layout`; layout slots therefore render in the layout color instead of the content color. The same rule is kept in `assets/mockup/ui-inspector.js` and the inline inspector in `standalone.html`. `data-ui-id` should be unique per route and stable across rendering, responsive modes and translation. Use explicit IDs for every important component instance and stable business record keys for repeating components. The current V34 is a compatibility adapter over V33's legacy HTML, not a full migration of all markup to explicit IDs.

Layout identities use `Core.Layout.<Template>` on the content root and `Core.Layout.<Slot>` on every slot, for example `data-ui-component="Core.Layout.PageHeader" data-ui-id="layout.sidebar.page-header" data-layout-slot="page-header"`. Slot names are lowercase, hyphenated and stable: `primary-sidebar`, `context-sidebar`, `top-bar`, `top-nav`, `workspace-toolbar`, `page-header`, `toolbar`, `content`, `list-pane`, `detail-pane`, `inspector`, `footer`, `public-header`, `public-footer`, `ai-sidebar`. Playground instances use `layout.playground.<template>.<slot>`.

`COMPONENT_REGISTRY.json` documents the adapter mappings. Fallback elements use `HTML.TAG` or semantic `Core.*` names. In a dense view labels may be suppressed to prevent collision; filtering, Pick and JSON export expose the remaining references. Bounds are CSS pixels, viewport-relative; visible bounds account for viewport and overflow clipping. Overlay follows scrolling and layout changes while enabled. It does not modify CSS dimensions of inspected elements. No input field values are exported; labels and DOM keys may contain sample/user-provided text, so review before sharing.

## AI issue template

```
Route: pilot/admin/catalog
Component: Core.Button
Reference: pilot/admin/catalog#Core.Button@1vrx2c5
Label: Filter
Problem: On mobile, button and adjacent controls are too close.
Expected: Keep the 44px touch target and consistent visual spacing.
Evidence: Attach screenshot and exported reference JSON.
```

## Implementation boundary

The standalone HTML retains V33 plus one inspector script and a small integration hook for the CMS builder. `source/ui-inspector.js` is the independent debug implementation. V34.1 adds `FormaUIInspector.classify(element)` returning `{component, kind, selector, mapped}` so layout classification can be verified without reading canvas pixels. The browser test environment did not allow system clipboard writes; the manual fallback and JSON download were verified. No backend, registry mutation, authorization or Core Engine change is made. Production implementation should gate this inspector behind a developer mode and explicit semantic IDs.
