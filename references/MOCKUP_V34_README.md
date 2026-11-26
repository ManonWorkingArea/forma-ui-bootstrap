# Forma V34 — UI Inspector

V33 remains the baseline UI Foundation review candidate. V34 adds a developer-facing debug overlay, without adding business features.

Open `standalone.html` (or `index.html`). Navigate to Catalog or any other screen. Use Debug, Alt+Shift+D, Pick, Parent, Copy reference or Export visible JSON. `screenshots/` contains actual Chromium captures; `example-reference-1440.json` and `example-reference-390.json` are selected Filter button references, and `example-inventory-*.json` are real downloaded inventories.

- `UI_INSPECTOR_CONTRACT.md`: naming, identity and implementation handoff.
- `COMPONENT_REGISTRY.json`: semantic adapter mappings.
- `source/ui-inspector.js`: standalone inspector source; the full merged application is in `standalone.html`.
- `TEST_REPORT.json`: initial run, post-fix observations and final focused checks.

V33 design freeze remains pending. The inspector is an additional design communication tool; it does not certify 100% design completeness. See V33 review backlog, retained under `reference/`.
