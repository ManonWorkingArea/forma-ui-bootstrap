---
name: forma-ui-bootstrap
description: Use Forma's pinned V34 interactive HTML mockup as the design bootstrap for AI Native Engine UI/UX tasks. Activate for new Svelte UI, Backoffice or frontend screens, shared component implementation, responsive layouts, visual review, design-token decisions, and bug reports naming Core.*, Studio.*, Files.*, Directory.* or other UI Inspector references. Resolve the exact component, route, Visual Key, interaction and responsive reference before coding. Query the bundled local CLI and optionally render reference screenshots and bounding-box inventories using Chromium. Preserve the engine's extension and action contracts; never treat mockup data, simulated actions, selectors or DOM hashes as production APIs. Use for design handoff and implementation review, not backend feature implementation or automatic design approval.
---
# Forma UI Bootstrap — V34

## Starting point

Treat the immutable bundled mockup `assets/mockup/standalone.html` as the visual baseline, V33's Quiet Precision documentation as its design intent, and the current project's approved contracts/code as the authority for implementation and behavior. V34 is a review candidate, not an approved freeze. Read `references/REVIEW_BACKLOG.md` when evaluating completeness. Do not import the accumulated standalone HTML/CSS/JS wholesale into production.

Run from this skill directory (or invoke the script by its absolute path):

```bash
python3 scripts/forma_ui.py verify
python3 scripts/forma_ui.py layouts
python3 scripts/forma_ui.py layout sidebar
python3 scripts/forma_ui.py pages catalog
python3 scripts/forma_ui.py components DataTable
python3 scripts/forma_ui.py context Core.DataTable
```

If verification fails, stop using the mismatched snapshot and report it. The CLI is local/read-only except for explicitly requested capture output. It needs no service connection. Layout routes are `#pilot/admin/f33layouts`, `#pilot/admin/f33layouts/<id>` and `#pilot/admin/f33playground`. Optional browser capture requires Python Playwright and Chromium; don't invent browser evidence if unavailable.

## Resolve → reference → implement → review

1. Identify task type (new UI, component change, responsive bug, design review). Resolve workspace, route, component and intended behavior. Read the existing project's component exports, contracts and tests before editing. If there is an Inspector JSON, use it; never infer the target solely from a button label.
2. Resolve the composition first: **Layout Template → Page Pattern → Component**. Query `layouts`/`layout <id>` for the eight shell/content templates, then `pages`, `components`, `keys` and `context` for a small relevant slice; consult `references/DESIGN_SYSTEM.md` and `references/UI_INSPECTOR_CONTRACT.md` as needed. The page index contains inherited V33 tested example routes, not a full registry of all possible pages. Registry mappings are legacy selectors, not production APIs. See `references/TOOLS.md` for command recipes.
3. For a specific visual issue, inspect the actual mockup at the affected viewport. Capture clean and debug screenshots/inventories, or use the supplied owner evidence. Use `issue` with a selected reference for a structured handoff; `locate` gives candidate source snippets, not a guaranteed implementation location. Mark ambiguity rather than choosing a lookalike silently. If reference and documented design intent conflict, expose the difference; do not quietly canonize a mockup defect.
4. Map the pattern to reusable Svelte components and semantic tokens in the target repo. Reuse existing implementation first; only add a shared component when the needed contract does not exist. Keep business-specific views in extensions and avoid copying version-prefixed selectors from the mockup. Use semantic `data-ui-component` and explicit stable `data-ui-id` unique per route; use stable record keys in repeated elements, not translated labels, CSS classes, indexes or DOM hashes. Maintain explicit action-per-request, shared registered action dispatcher and authorization boundaries. Do not use direct DB access or treat an AI confirmation as permission. Do not introduce new runtime architecture for UI-only tasks.
5. For layout work, start from a layout template and its slots (`Core.Layout.*`, `data-layout-slot`), then map to the page pattern and finally to components. Preserve existing page behavior and test relevant states: loading, empty, error, disabled, readonly, confirmation, focus, responsive and reduced motion where applicable. Test the affected breakpoints, no horizontal scroll in DataTable, proportionate controls, no overlapping labels/assistant, and use clean browser screenshots as well as debug evidence. Use actual target-app screenshots for implementation acceptance, not reference-only captures. Follow the project's existing quality gates; do not modify protected acceptance tests or claim design freeze without owner approval.
6. Return a concise handoff with baseline SHA, route, component/reference/explicit ID, Visual Keys, changed files, actual checks/evidence, unresolved deviations and regression risk. Separate visual match, functional checks and owner acceptance. Never claim PASS for an unexecuted check.

## Required design rules

- Quiet Precision: neutral semantic surfaces, 13px base / 11px metadata, 4px spacing scale, 6px regular radius, 9px overlay radius, compact controls 30px. Read the token file instead of hard-coding separate per-module themes.
- Whole-canvas left/right sliding shell; no floating navigation drawer. Preserve mobile launcher dock and avoid overlapping controls. Record Detail is a full page, not an assistant-side drawer.
- Adaptive DataTable → structured records, no horizontal scrolling. Keep stable record IDs, selection/filter state and visible access to data.
- Visual 16px checkbox/radio independent of 44px mobile touch target. Respect content container size, not merely viewport size.
- Custom dialogs/prompts/toasts, accessible focus behavior, distinct destructive action. Keep published snapshots separate from draft editor state, and isolate authored canvas theme from editor UI.
- AI action UI: one registered action, gather inputs, exact proposal, explicit confirmation, edit/cancel/expiry/error and typed result. Keep preview-only writes simulated; no implied real execution.

## Load only relevant supporting files

- `references/VISUAL_KEYS.json`: machine-readable design rules and tokens, newly named semantic Visual Keys.
- `references/LAYOUT_REGISTRY.json`: eight layout templates with shell/content separation, slots, locks, defaults, responsive behavior, Visual Keys, normalized `forma.layout.config.v1` schema and agent-ready HTML examples.
- `references/COMPONENT_REGISTRY.json`: 140 selector mappings (some names repeat for different editor contexts); not 140 distinct component exports.
- `references/PAGE_INDEX.json`: 126 tested Pilot example routes, eight layout routes and the layout playground, with scope and widths.
- `references/DESIGN_SYSTEM.md`, `references/COMPONENT_INVENTORY.md`, `references/REVIEW_BACKLOG.md`: intent, specimen coverage, known gaps.
- `references/UI_INSPECTOR_CONTRACT.md`: V34/V34.1 bounding boxes, layout slot identity, name/reference semantics, clipboard/export limitations.
- `references/TOOLS.md`: CLI usage, deployment and integration conventions.
- `references/examples/`: actual V34 Inspector exports and historical V33/V34 test reports. These reports do not verify a future implementation.
- `assets/mockup/`: exact V34 standalone and inspector source, the V34 screenshot gallery and selected V33/CLI screenshots. Open visually on demand; avoid loading the entire HTML into context.
