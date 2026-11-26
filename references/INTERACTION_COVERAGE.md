# Touch interaction coverage — V34.2 corrective

One shared Pointer Events engine (`FormaTouch`) owns gesture recognition. Modules subscribe through `formatouch:*` events, model callbacks or `data-touch*` / `data-sortable*` attributes. No module keeps a duplicate touch recognizer.

**Evidence states:** `native-touch` = Chromium CDP emits real touch; `pointer-fallback` = WebKit/Firefox pointer events through the documented API; `lab-only` = the interaction exists only in the Design System Touch Lab and is **not** wired to that module; `physical` = **Pending Owner Review** until reviewed on a device. Synthetic WebKit/Firefox pointer checks are not native touch.

| Surface | Wired? | Verified by smoke | Model/state changed | Evidence |
|---|---|---|---|---|
| Shell | yes | yes (all engines) | existing `shift-left` / `shift-right` classes after live `.canvas` follow; 20 px edge rule | Chromium native touch + pointer fallback |
| Touch Lab (14 specimens) | yes | yes (all engines) | specimen counters, order arrays, sheet, zoom, panel, shell classes | Chromium native touch + pointer fallback |
| Kanban (`project19`) | yes | yes (all engines) | `f24Tasks` status and order, survives re-render | pointer fallback |
| Gantt (`project19`) | yes | yes (all engines) | `f24Tasks[i].start` and `.len` | pointer fallback |
| Calendar (`calendar19`) | yes | yes (all engines) | `wDate` month state | pointer fallback |
| Workflow (`workflow19`) | yes | yes (all engines) | `wNodes` / `f24NodeTypes` order | pointer fallback |
| Studio parts (`s31editor/form-enquiry`) | yes | yes (all engines) | `s31Current().parts` order, saved and re-rendered | pointer fallback |
| Layout Playground split | yes | Lab panel resize only | split percentage / panel size | pointer fallback |
| UI Inspector pick | yes | Chromium | one reference, underlying lab action suppressed | Chromium native touch |
| Files | **lab-only** | no module run | not wired in this round | Lab only / Pending |
| Gallery | **lab-only** | no module run | not wired in this round | Lab only / Pending |
| DataTable | **lab-only** | no module run | not wired in this round | Lab only / Pending |
| Chat / Inbox | **lab-only** | no module run | not wired in this round | Lab only / Pending |
| Directory | **lab-only** | no module run | not wired in this round | Lab only / Pending |
| Theme preview | **lab-only** | no module run | not wired in this round | Lab only / Pending |
| Page builder (`builder19`) | n/a | — | Route redirects to CMS; `wBlocks` model exists but is not exposed by a route | Not claimed |

## Contract

- Pointer Events only. HTML drag/drop remains a desktop fallback in the CMS builder.
- Tap slop 8px, drag threshold 6px, long press 500ms, double tap 320ms, auto-scroll edge 44px.
- Auto-scroll is disabled under `prefers-reduced-motion`, as are transitions and momentum.
- Pointer capture is released on `pointerup`, `pointercancel`, `lostpointercapture`, blur and tab hide.
- A second pointer either starts a declared pinch from the shared pointer map or cancels the active gesture safely; `FormaTouch.state.active` returns to zero.
- Model-backed sortable: stable item ids, source/target containers, indices, `defineSortable(group,{apply,undo,redo})`, inverse model undo/redo, re-render from model state. Ctrl+Z is scoped to the focused sortable container.
- Keyboard parity: Space starts, Arrow moves, Space commits, Escape restores; Alt+Arrow is an immediate alias. One `#ft-live` `role=status` announcement per state change.
- Real shell uses 20 px edge gestures and settles through the existing canvas shift classes; public canvas never slides.
- Touch targets are 44–48px and the smoke asserts no visible lab target below 44px.
- Physical-device verification remains **Pending Owner Review**; it is not implied by CI or synthetic pointer tests.
