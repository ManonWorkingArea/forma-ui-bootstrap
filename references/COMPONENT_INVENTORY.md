# V33 UI coverage map

Coverage means a reference specimen or existing working mockup is present, not production maturity or uniform implementation.

| Workstream | Reference | Coverage |
|---|---|---|
| Advanced selects | Advanced components | Search, group, multi, hierarchical path options; keyboard search/navigation |
| Calendar/date/time/color | Advanced components | Custom calendar and range; hour/minute selector popover; HEX/RGB/opacity/palette |
| Overlay | Feedback; Advanced components; Mobile patterns | Alert/confirm/prompt/toast/banner; tooltip 4 positions; popover; nested menu; sheet/full form |
| Text/code | Advanced components | Contenteditable rich text, basic formatting, links/image/table; JSON validation, sandboxed HTML/CSS preview |
| File/media | Files; Advanced components | Existing explorer/pickers, gallery/zoom/navigation, file metadata/drop specimen |
| Layout | Page patterns; Mobile patterns | Resizable split, collapse/restore, responsive data collection, wizard, mobile selection/reorder |
| Touch interactions | Touch interactions; Touch Interaction Lab | Shared Pointer Events engine, fourteen specimens, model-backed sortable/undo, wired Kanban/Gantt/Calendar/Workflow/Studio parts, Files long press/Move sheet, Gallery pinch, F33 DataTable selection/width, Chat/Inbox swipe, Directory select, Theme 44px controls, Layout Playground split, shell edge follow, sheet, pinch, resize and Inspector pick cancellation |
| Layout templates | Layout templates; Layout Playground | Eight shell/content templates with explicit `Core.Layout.*` slots, locks, slot labels, light/dark preview, 1440/768/390/320 behavior, copy reference/config and normalized JSON export |
| States | UX states | 20 visual states, retry/progress/partial result/conflict/unsaved examples |
| Master screens | Page patterns | 15 patterns; full-screen editor links into existing CMS/Studio |
| Account | Account journeys | 14 routes, sign in, registration, verification, recovery, invitations, onboarding, setup, switching, preferences/lock/expired |
| Frontend | Frontend patterns | 11 new public routes; existing home/catalog/portal pages; header/menu/footer/consent; published CMS/resource references |
| AI | AI action interface; assistant rail panel | 7 scenario choices: table/read, summary/chart, booking form/proposal/confirm, file, error/retry, denied, expired; local conversation/context |
| Appearance | Appearance & language | Light/dark/system, density, font/scale, sidebar width, contained layout, brand/logo/favicon, selected Thai labels and date/currency preview |
| Existing components | Design system, Form elements, Feedback, Component gallery | Prior V1–V32 reference examples preserved |
| Existing modules | Original Backoffice navigation | Workspace, CMS and builders, Files, Directory, Platform, Studio, System administration |

## Coverage boundaries

- Tree select uses hierarchical path labels, not a full lazy tree data source.
- Time selector uses custom popover with native hour/minute selects; several legacy inputs remain native.
- Rich editor has basic formatting; no complete schema, history/export pipeline or complex table editing.
- Code editor is a textarea with validation and sandbox preview, not syntax-complete IDE.
- Page pattern examples reuse current components or link to existing real mock screens; not every legacy screen is rebuilt.
- Layout templates are additive compositions, not new business screens. The playground preview mirrors the shell contract in a container-scoped stage; it is not a second application runtime.
- Account and frontend support flows are local specimens, not account or messaging services.
- AI context is a local selected record reference; requests are deterministic previews, not actual context-aware LLM calls. Confirmed writes remain disabled.
- Thai/English shell and selected system labels are implemented; complete translation of every older page and UI string is pending. Locale and currency presentation is not a full data formatting migration.
- All eight widths tested for new routes; legacy entry smoke at two widths, not full functional regression or accessibility certification.
