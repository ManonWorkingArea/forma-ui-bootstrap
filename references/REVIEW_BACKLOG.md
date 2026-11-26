# V33 — Design freeze review backlog

Status: UI FOUNDATION REVIEW CANDIDATE. Owner visual approval required.

1. Review the new specimen library, account journeys, public patterns and AI interaction design; compare screenshots at actual device sizes.
2. Migrate remaining V1–V32 local component implementations to shared controls. Do not remove existing behavior while refactoring.
3. Audit all legacy screens in dark mode, including semantic colors, authored content isolation and hard-coded inline colors. Verify complete localization, font scaling, density, date/number/currency labels. Do not pretend currency formatting performs exchange-rate conversion.
4. Extend keyboard interaction and focus semantics across all old and new components. Full contrast, screen reader, real touch and reduced-motion validation pending. Confirm Android content URI file open, upload, LocalStorage and download behavior on device.
5. Expand functional regression to all legacy interactions and Starter/Pilot flows; current legacy checks are entry smoke. Verify unsaved protection, notification layering, shared pickers and actual editor integrations.
6. Decide whether advanced controls need deeper editing functionality (tree expansion, code syntax highlighting, rich table editing, touch drag/drop). Reference specimens cover the UI patterns; they do not promise full product functionality.
7. Freeze the design only after owner accepts visuals and scope. No backend or runtime changes in this mockup. Use explicit component contracts to implement the production UI, not the mockup's long accumulated CSS/JS wrappers.
