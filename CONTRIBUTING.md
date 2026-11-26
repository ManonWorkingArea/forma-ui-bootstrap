# Contributing

This repository is the source of truth for the Forma V34 UI bootstrap. The mockup is an immutable review baseline unless an approved change specifically requests a design revision. Do not refactor or redesign unrelated areas.

## Before starting

1. Read `SKILL.md`, `RULES.md` when present in the consuming project, and the affected reference files.
2. Reproduce the issue using the public Preview.
3. Attach the Page / Route, Component Name, Component Reference ID, Visual Design Key and viewport.
4. Use the matching GitHub issue form. Do not report a suspected defect as confirmed until it has evidence.

## Branches

- `main`: approved release baseline. Changes require Owner approval.
- `dev`: development and Owner review. Pages deploys automatically from this branch.
- `fix/<short-name>`: evidence-backed bug fixes.
- `feature/<short-name>`: features or approved design improvements.

Start work from `dev` unless the Owner directs otherwise. Never merge a future change into `main` without explicit Owner approval.

## Lifecycle

1. Owner tests the public Preview and files an issue or structured Element Reference.
2. The Lead Agent verifies the reference and defines acceptance criteria.
3. A Developer Agent works on the appropriate branch.
4. The change is checked at the reported viewport and relevant responsive breakpoints.
5. Before/after screenshots and Inspector inventories are retained.
6. Affected design references are updated together.
7. The change is reviewed and merged to `dev`.
8. Pages deploys the Preview and the Owner reviews it.
9. Release occurs only on explicit Owner instruction.

## Change requirements

- Preserve the interactive behavior and design identity of the mockup.
- Keep `SKILL.md` at the repository root.
- Do not add a backend, database, authentication, MCP server or unrelated infrastructure.
- Do not add a License without Owner direction.
- Do not commit credentials, private URLs, internal endpoints, customer data, personal data or AI Native Engine source.
- Run `python3 scripts/forma_ui.py verify`, `python3 scripts/test_forma_ui.py` and `python3 scripts/validate_repository.py` before opening a pull request.
- Use Semantic Versioning for post-`v1.0.0-rc.1` releases.

## Public evidence

Screenshots and Inspector exports can contain labels or sample content. Review every attachment before publishing. The V34 fixtures are synthetic, but future evidence must still be checked for secrets and personal or confidential information.
