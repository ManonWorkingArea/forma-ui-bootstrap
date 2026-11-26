# Touch interaction coverage — V34.2

One shared Pointer Events engine (`FormaTouch`) owns gesture recognition for mouse, touch and pen. Module code subscribes to `formatouch:*` events or uses documented `data-touch*` / `data-sortable*` attributes; no module keeps its own touch recognizer.

**Evidence states:** `native-touch` = Chromium CDP emits real touch events; `pointer-fallback` = WebKit/Firefox pointer events or documented `FormaTouch` API; `physical` = **Pending Owner Review** until reviewed on a device.

| Surface | Gestures / interactions | Registry IDs | State changed | Evidence |
|---|---|---|---|---|
| Design System Touch Lab | tap, double tap, long press, swipe, sortable, cross-container, nested, cancel, auto-scroll, sheet, pinch, resize, shell, tap suppression | `core.*` | specimen counters, order arrays, sheet, zoom, panel, shell panel | native-touch (Chromium), pointer-fallback |
| Shell | sidebar swipe, assistant swipe, canvas follow | `shell.sidebar-swipe`, `shell.ai-swipe`, `shell.canvas-follow` | existing `shift-left` / `shift-right` classes, no main reflow | pointer-fallback; physical pending |
| Public layout | no slide, no assistant | `shell.canvas-follow` | unchanged public canvas | static check |
| Layout Playground | panel resize, split, direct routes | `layout.playground-panel`, `core.panel-resize` | panel width and split geometry | pointer-fallback |
| Kanban (workspace) | reorder, move between lanes | `kanban.reorder`, `core.cross-container` | `f24Tasks` status and order | pointer-fallback; physical pending |
| Calendar / Gantt | period swipe, bar drag | `calendar.swipe`, `gantt.drag` | view period, start/length | pointer-fallback |
| Files / Gallery / DataTable | row and card swipe | `files.swipe`, `gallery.swipe`, `datatable.row-swipe` | revealed action / active card | pointer-fallback |
| Workflow / builders | node and part drag, canvas pan/pinch | `workflow.node-drag`, `builder.part-order`, `builder.canvas-pan`, `builder.pinch-zoom` | node position, part order, canvas offset/zoom | pointer-fallback |
| Theme / Chat / Directory | preview pan, swipe archive, swipe action | `theme.preview-pan`, `chat.swipe-archive`, `directory.swipe` | preview offset, archived state, contact action | pointer-fallback |
| UI Inspector | pick and cancel during a gesture | `inspector.pick-cancel` | one reference, no underlying action | native-touch (Chromium) |
| Bottom sheets / panels | drag sheet, resize panel | `core.bottom-sheet`, `core.panel-resize` | snap state, size | native-touch (Chromium) |

## Contract

- Pointer Events only. HTML drag/drop remains a desktop fallback in the CMS builder.
- Pointer capture is released on `pointerup`, `pointercancel`, `lostpointercapture`, window blur and tab hide.
- Thresholds: tap slop 8px, drag threshold 6px, long press 500ms, double tap 320ms, auto-scroll edge 44px.
- Axis lock, tap suppression scoped to the gesture target, nested scroll yielding, reduced-motion respected.
- Sortable: handle, ghost, placeholder, same-group containers, cross-container and nested moves, keyboard Alt+Arrow, undo, and real mockup order/state updates.
- Touch targets 44–48px, safe-area padding, dynamic viewport and `visualViewport` keyboard handling.
- A persistent `role=status` live region announces gesture, pointer type and component identity.
- Physical-device verification remains **Pending Owner Review**; it is not implied by automated evidence.
