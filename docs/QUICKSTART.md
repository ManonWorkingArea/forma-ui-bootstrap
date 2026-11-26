# Quick start

## Human review

1. Open the public Preview URL from the repository homepage.
2. The root page redirects to the unchanged V34 `assets/mockup/standalone.html`.
3. Use the top-bar **Debug** control on desktop or the bottom-left control on narrow/editor views. `Alt+Shift+D` also toggles the Inspector.
4. Select **Pick**, choose an element, and copy or export its structured reference.
5. Use the matching issue form and attach a clean screenshot plus the reference JSON when available.
6. Review real module touch behavior on Project (Kanban/Gantt), Calendar, Workflow and Studio parts; files/gallery/directory/chat/theme are Lab-only this round.
7. Review touch interactions at `#pilot/admin/f33touch` or `#pilot/admin/f33touchlab`.
8. Review layout templates at `#pilot/admin/f33layouts`, open a direct template route (`#pilot/admin/f33layouts/<id>`) or configure one in `#pilot/admin/f33playground`.

The Preview is static. It needs no install, backend, account or database.

## AI agent workflow

Run commands from the repository root:

```bash
python3 scripts/forma_ui.py verify
python3 scripts/forma_ui.py layouts
python3 scripts/forma_ui.py interactions
python3 scripts/forma_ui.py interaction shell.sidebar-swipe
python3 scripts/forma_ui.py layout sidebar
python3 scripts/forma_ui.py pages catalog
python3 scripts/forma_ui.py components Core.DataTable
python3 scripts/forma_ui.py keys forma.collection.adaptive
python3 scripts/forma_ui.py context Core.DataTable
python3 scripts/forma_ui.py tokens
```

For a selected reference:

```bash
python3 scripts/forma_ui.py inspect references/examples/example-inventory-1440.json 'Core.Button@1vrx2c5'
python3 scripts/forma_ui.py issue references/examples/example-reference-1440.json \
  --problem 'Describe the observed behavior' \
  --expected 'Describe the required behavior'
python3 scripts/forma_ui.py compare before.json after.json
```

Read `SKILL.md` before implementation. Resolve the composition in order: **Layout Template → Page Pattern → Component**, then the exact route, reference and Visual Key, then inspect the consuming application's contracts and tests. Use `references/UI_INSPECTOR_CONTRACT.md` for identity and evidence rules.

Browser capture is optional and requires Python Playwright plus Chromium:

```bash
python3 scripts/forma_ui.py capture pilot/admin/catalog --width 390 --height 844 --out /tmp/forma-catalog
```

Capture output belongs in temporary evidence locations until reviewed. Do not add it to the repository automatically.
