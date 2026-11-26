# Touch interaction coverage — V34.2 final

One shared Pointer Events engine (`FormaTouch`) owns gesture recognition. Modules subscribe through `formatouch:*` events, model callbacks or `data-touch*` / `data-sortable*` attributes. No module keeps a duplicate touch recognizer.

**Evidence states:** `native-touch` = Chromium CDP emits real touch; `pointer-fallback` = WebKit/Firefox pointer events through the documented API; `physical` = **Pending Owner Review**. Synthetic WebKit/Firefox pointer checks are not native touch.

| Surface | Verified by smoke | State changed | Evidence |
|---|---|---|---|
| Shell | all engines | 20px edge drag follows on the real `.canvas`, then settles through `shift-left`/`shift-right`; public never slides | Chromium native touch + pointer fallback |
| Touch Lab (14 specimens) | all engines | counters, order arrays, sheet, zoom, panel, shell classes | Chromium native touch + pointer fallback |
| Kanban (`project19`) | all engines | `f24Tasks` status and order, survives re-render | pointer fallback |
| Gantt (`project19`) | all engines | `f24Tasks[i].start` and `.len` | pointer fallback |
| Calendar (`calendar19`) | all engines | `wDate` month state | pointer fallback |
| Workflow (`workflow19`) | all engines | `wNodes` / `f24NodeTypes` order | pointer fallback |
| Studio parts (`s31editor/form-enquiry`) | all engines | `s31Current().parts` order, saved and re-rendered | pointer fallback |
| Files (`flmy`) | all engines | long press selects rows/cards and exposes the existing Move/Copy/Trash sheet; checkbox and keyboard remain | pointer fallback |
| Gallery viewer | all engines | shared pinch zoom, fit/reset/fullscreen buttons; native pan/scroll preserved | pointer fallback |
| F33 DataTable | all engines | row selection with a visible action bar; header swipe changes persisted column-width state | pointer fallback |
| Chat (`chat19`) | all engines | swipe marks read/unread; visible **Mark unread** button | pointer fallback |
| Inbox (`inbox19`) | all engines | swipe archives or toggles read; visible Archive button | pointer fallback |
| Directory (`d29people`) | all engines | long press mutates `d29Selected`; visible bulk-action bar | pointer fallback |
| Theme builder (`theme.control-targets`) | all engines | controls are ≥44px, tap/keyboard reachable; no hover-only action | pointer fallback |
| Layout Playground split | all engines | shared separator resize updates the actual split percentage and pane width | pointer fallback |
| UI Inspector pick | Chromium | one reference, underlying lab action suppressed | Chromium native touch |

## Explicit limitations

- **Page builder:** the `builder19` admin route redirects to CMS. Its `wBlocks` model is not exposed; no drag coverage is claimed for that inaccessible route.
- **DataTable columns:** the F33 static specimen supports persisted *width* changes, not full column reorder. Other DataTable variants are documented as static.
- **Physical devices:** not tested. Status remains **Pending Owner Review**.
- **WebKit/Firefox:** pointer fallback only; native touch is not claimed for those engines.

## Contract

- Pointer Events only. HTML drag/drop remains a desktop fallback in the CMS builder.
- Tap slop 8px, drag threshold 6px, long press 500ms, double tap 320ms, auto-scroll edge 44px.
- Auto-scroll is disabled under `prefers-reduced-motion`, as are transitions and momentum.
- Pointer capture is released on `pointerup`, `pointercancel`, `lostpointercapture`, blur and tab hide.
- A second pointer either starts a declared pinch from the shared pointer map or cancels the active gesture safely; `FormaTouch.state.active` returns to zero.
- Model-backed sortable: stable item ids, source/target containers, indices, `defineSortable(group,{apply,undo,redo})`, inverse model undo/redo and re-render from model state. Ctrl+Z is scoped to the focused sortable container.
- Keyboard parity: Space starts, Arrow moves, Space commits, Escape restores; Alt+Arrow is an immediate alias. One `#ft-live` `role=status` announcement per state change.
- Touch targets are 44–48px, including the theme builder and lab controls.
