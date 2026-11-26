# Changelog

All notable repository and design-reference changes are recorded here. The UI mockup itself is versioned by baseline and remains unchanged in this release candidate unless an Owner-approved issue explicitly records a design revision.

## Unreleased - V34.2 touch interactions

### Fixed

- Files rows/cards use shared long press and multi-select while preserving checkboxes and the existing Move/Copy/Trash sheet; Gallery viewer uses shared pinch with native scroll preserved; F33 DataTable has touch selection, a visible action bar and persisted column-width gesture.
- Chat and Inbox swipes mutate read/archive state with visible buttons; Directory long press mutates `d29Selected`; Theme controls are 44px and hover-free; the real Layout Playground split separator uses shared resize and updates actual pane geometry.
- Real Kanban movement now mutates `f24Tasks` status and order and survives re-render; Gantt drag/resize mutates `start`/`len`; Calendar swipe changes `wDate`; Workflow order mutates `wNodes`/`f24NodeTypes`; Studio part order mutates `s31Current().parts`.
- Sortable is model-backed through `FormaTouch.defineSortable(group,{apply,undo,redo})`; undo/redo uses inverse model operations and survives DOM replacement. Ctrl+Z is scoped to the focused sortable container.
- Keyboard parity: Space starts, Arrow moves, Space commits, Escape restores; Alt+Arrow is an immediate alias with one live announcement per state change.
- The real shell uses 20 px edge gestures, drives the actual `.canvas` transform without transition during drag and settles through `shift-left`/`shift-right`; public stays no-slide.
- Auto-scroll is disabled under reduced motion; a second pointer either starts a declared pinch or cancels the active gesture safely.
- Touch smoke launches Chromium, WebKit and Firefox with browser-compatible options and reports native touch honestly; real module state, keyboard, undo, multi-touch, shell and 44 px geometry are asserted. Files/Gallery/DataTable/Chat/Directory/Theme remain explicitly Lab-only.

### Added

- One shared `FormaTouch` Pointer Events engine with tap, double tap, long press, swipe, pan, drag, sortable, resize, pinch, pointer capture, cancellation, axis lock, rAF updates, edge auto-scroll, momentum, nested-scroll yielding, tap suppression and reduced-motion behavior.
- Design System routes `#pilot/admin/f33touch` and `#pilot/admin/f33touchlab` with fourteen working specimens, live gesture/pointer/component log and keyboard/button alternatives.
- Sortable foundation with handle, ghost, placeholder, cross-container and nested moves, keyboard movement, undo and real mockup order/state updates.
- Touch behavior for shell canvas follow (live transform then existing shift classes), layout panels, bottom sheets, pinch, builders and documented module hooks.
- `references/INTERACTION_REGISTRY.json` (`forma-interaction-registry.v1`), `references/INTERACTION_COVERAGE.md`, CLI `interactions` / `interaction <id>`, and the nine `forma.touch.*` Visual Keys.
- Cross-browser `scripts/touch_interaction_smoke.py` with Chromium native CDP touch and WebKit/Firefox pointer fallback; CI installs all three browsers.

## Unreleased - V34.1 layout templates

### Added

- Eight layout templates (`sidebar`, `semi`, `full`, `fullscreen`, `split`, `centered`, `inspector`, `public`) under `#pilot/admin/f33layouts`, each with a direct route and a generic interactive example.
- `#pilot/admin/f33playground`: template selector, shell/content controls, 1440/768/390/320 viewport, light/dark preview, locked-control reasons, copy layout reference, copy configuration, normalized `forma.layout.config.v1` JSON export and a bounded `window.FormaLayouts` test API.
- `references/LAYOUT_REGISTRY.json` (`forma-layout-registry.v1`) with shell/content separation, slot metadata, required/optional components, locks, defaults, responsive behavior, Visual Keys and agent-ready HTML examples.
- CLI `layouts [query]` and `layout <id>`; unknown ids exit non-zero.
- Explicit `Core.Layout.*` / `data-layout-slot` Inspector identities and layout-kind classification in both inspector implementations.

### Fixed

- Direct layout routes now expose Copy Layout Reference, Copy Configuration and JSON export with the same clipboard fallback as the Playground, using the route, template and slot context of that route.
- Direct layout routes start from the template's canonical defaults instead of retaining Playground customization.
- The Playground keeps focus on the Template select after a template change.
- Context and assistant controls only render for enabled slots: no inert context launcher, no disabled-AI launcher, no `ai-open` state and no empty assistant target.
- Slot labels reserve a label band instead of overlaying content, name both the slot and its `Core.Layout.*` component, wrap at 9–10px, and stay legible without horizontal overflow at 320, 390, 768 and 1440.
- Direct layout routes reset to canonical defaults on every genuine entry, including detail → non-layout page → the same detail, while a same-route repaint keeps user changes.
- The role=status announcement region now lives outside the replaced workbench, so template changes stay announced to assistive technology.
- Package baseline metadata now separates immutable original `skill.zip` provenance from current V34.1 member checksums; validator output reports both.

### Changed

- `PAGE_INDEX.json` now lists 126 routes including the layout catalog, eight layout routes and the playground; `COMPONENT_REGISTRY.json` lists 140 mappings including layout and slot identities.
- `VISUAL_KEYS.json` keeps the same 16 key IDs and adds provisional layout tokens.
- Layout workflow is now Layout Template → Page Pattern → Component in `SKILL.md` and the documentation.
- Refreshed `MANIFEST.json` and the authorized dev package baseline. No release metadata, workflows, screenshots, examples or release assets changed.

## v1.0.0-rc.1 - 2026-11-26

### Added

- Initial public repository for the Forma UI Bootstrap V34.
- Human and agent entrypoints, component registry, page index, visual keys, inspector contract, local CLI and screenshot evidence from the supplied package.
- GitHub issue intake, labels, pull-request template and development lifecycle documentation.
- Static validation, browser smoke checks and dev-branch GitHub Pages deployment.
- Traceable release-candidate assets: complete agent bootstrap, unchanged standalone mockup and portable skill package.

### Baseline

- Supplied package SHA-256: `2c5b17775227085a1f9ccebf1c84521d0857555b5431cdc55bff332f3fdf1db8`.
- Mockup baseline: V34, byte-identical to the supplied standalone HTML.
- No design freeze is implied by this release candidate.
