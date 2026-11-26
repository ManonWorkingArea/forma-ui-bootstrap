# Changelog

All notable repository and design-reference changes are recorded here. The UI mockup itself is versioned by baseline and remains unchanged in this release candidate unless an Owner-approved issue explicitly records a design revision.

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
- Slot labels reserve a small label band instead of overlaying content, and stay legible without horizontal overflow at 320, 390, 768 and 1440.
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
