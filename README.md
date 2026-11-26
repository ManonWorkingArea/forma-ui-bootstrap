# Forma V34 + Agent Bootstrap

This is one portable bundle containing the original interactive HTML mockup and the reusable `forma-ui-bootstrap` agent skill.

- **Human preview:** open `assets/mockup/standalone.html` in a browser. Enable Debug to pick an element and copy/export a reference. Open `assets/mockup/screenshots/index.html` for original V34 screenshots.
- **Agent entrypoint:** `SKILL.md`. Place this folder in your agent host's skill directory, or point a repo agent to its absolute path. No host-specific installation was performed.
- **Query tools:** run `python3 scripts/forma_ui.py verify`, then `pages`, `components`, `keys`, `context`, `inspect`, `issue`, `locate`, `compare`, or `capture`. See `references/TOOLS.md`. Static commands require Python 3.9+; browser capture requires Playwright and Chromium.
- **Design contract:** `references/DESIGN_SYSTEM.md`, `VISUAL_KEYS.json`, `COMPONENT_REGISTRY.json`, `PAGE_INDEX.json`, `UI_INSPECTOR_CONTRACT.md`, `MANIFEST.json`.
- **Evidence:** `references/examples/` contains actual baseline captures and inventories; historical test reports are separate from skill tests.

The HTML is byte-identical to V34; no production application code was changed. This is a pinned review candidate, not a design freeze or production runtime. The page index covers known Pilot fixture routes, not all possible routes. Read-only CLI tooling is provided; no MCP server or Paseo/Pi/OpenCode registration is included.

CLI screenshots: `assets/mockup/screenshots/catalog-390-cli-clean.png`, `catalog-390-cli-debug.png`, `builder-1440-cli-clean.png`, `builder-1440-cli-debug.png`, `register-390-cli-clean.png`, `register-390-cli-debug.png`.

Bootstrap validation: `references/examples/BOOTSTRAP_TEST_REPORT.json` and `bootstrap-static-tests.txt`.
