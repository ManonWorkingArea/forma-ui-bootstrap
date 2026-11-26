# Forma V34 + Agent Bootstrap

This is one portable bundle containing the original interactive HTML mockup and the reusable `forma-ui-bootstrap` agent skill.

- **Human preview:** open `assets/mockup/standalone.html` in a browser. Enable Debug to pick an element and copy/export a reference. Open `assets/mockup/screenshots/index.html` for original V34 screenshots.
- **Agent entrypoint:** `SKILL.md`. Place this folder in your agent host's skill directory, or point a repo agent to its absolute path. No host-specific installation was performed.
- **Query tools:** run `python3 scripts/forma_ui.py verify`, then `layouts`, `layout <id>`, `interactions`, `interaction <id>`, `pages`, `components`, `keys`, `context`, `inspect`, `issue`, `locate`, `compare`, or `capture`. See `references/TOOLS.md`. Static commands require Python 3.9+; browser capture requires Playwright and Chromium.
- **Design contract:** `references/DESIGN_SYSTEM.md`, `LAYOUT_REGISTRY.json`, `VISUAL_KEYS.json`, `COMPONENT_REGISTRY.json`, `PAGE_INDEX.json`, `UI_INSPECTOR_CONTRACT.md`, `MANIFEST.json`.
- **Touch foundation:** `#pilot/admin/f33touch` and `#pilot/admin/f33touchlab` expose the shared `FormaTouch` Pointer Events engine with fourteen specimens, live pointer/gesture state, sortable/cross/nested drag, sheets, pinch, resize and shell follow.
- **Layout templates:** `#pilot/admin/f33layouts` (catalog), `#pilot/admin/f33layouts/<id>` (one of eight templates) and `#pilot/admin/f33playground` (configuration, copy reference/config, normalized `forma.layout.config.v1` export).
- **Evidence:** `references/examples/` contains actual baseline captures and inventories; historical test reports are separate from skill tests.

The mockup is V34 plus the Owner-approved additive V34.1 layout templates and playground; every existing route, token and canvas behavior is preserved. No production application code was changed. This is a pinned review candidate, not a design freeze or production runtime. The page index covers known Pilot fixture routes, not all possible routes. Read-only CLI tooling is provided; no MCP server or Paseo/Pi/OpenCode registration is included.

CLI screenshots: `assets/mockup/screenshots/catalog-390-cli-clean.png`, `catalog-390-cli-debug.png`, `builder-1440-cli-clean.png`, `builder-1440-cli-debug.png`, `register-390-cli-clean.png`, `register-390-cli-debug.png`.

Bootstrap validation: `references/examples/BOOTSTRAP_TEST_REPORT.json` and `bootstrap-static-tests.txt`.

The 60 member checksums in `.github/package-baseline.json` describe the current V34.1 working tree; the immutable original `skill.zip` digest is retained separately as source provenance. `scripts/validate_repository.py` reports both, and `MANIFEST.json` pins the current V34.1 files.
