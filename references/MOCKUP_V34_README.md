# Forma V34 — UI Inspector

V33 remains the baseline UI Foundation review candidate. V34 adds a developer-facing debug overlay, without adding business features. V34.1 adds the Layout Templates catalog, eight direct layout routes and the Layout Playground on top of the same F33 extension pattern. V34.2 adds the shared `FormaTouch` Pointer Events engine, the Touch Interaction Lab (`#pilot/admin/f33touchlab`) and model-backed touch wiring for the shell, Kanban, Gantt, Calendar, Workflow and Studio parts.

Open `standalone.html` (or `index.html`). Navigate to Catalog or any other screen. Choose **UI foundation → Layout templates** (`#pilot/admin/f33layouts`), open a layout (`#pilot/admin/f33layouts/<id>`), or use **Layout playground** (`#pilot/admin/f33playground`). Use Debug, Alt+Shift+D, Pick, Parent, Copy reference or Export visible JSON. `screenshots/` contains actual Chromium captures; `example-reference-1440.json` and `example-reference-390.json` are selected Filter button references, and `example-inventory-*.json` are real downloaded inventories.

- `UI_INSPECTOR_CONTRACT.md`: naming, identity and implementation handoff.
- `INTERACTION_REGISTRY.json`: shared touch/pointer contracts, engine API, fourteen specimens and the nine `forma.touch.*` keys.
- `LAYOUT_REGISTRY.json`: eight layout templates, slot identities, locks, defaults, responsive behavior and `forma.layout.config.v1`.
- `MANIFEST.json` pins current V34.1 member checksums; `.github/package-baseline.json` keeps the original `skill.zip` digest as separate provenance.
- `COMPONENT_REGISTRY.json`: semantic adapter mappings.
- `source/ui-inspector.js`: standalone inspector source; the full merged application is in `standalone.html`.
- `TEST_REPORT.json`: initial run, post-fix observations and final focused checks.

V33 design freeze remains pending. The inspector is an additional design communication tool; it does not certify 100% design completeness. See V33 review backlog, retained under `reference/`.
