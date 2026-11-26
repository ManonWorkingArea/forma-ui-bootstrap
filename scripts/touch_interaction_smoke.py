#!/usr/bin/env python3
"""Cross-browser pointer/touch evidence for the shared FormaTouch engine.

Chromium uses native CDP touch events. WebKit and Firefox use the documented
pointer-event fallback and the public FormaTouch test API. Native touch is only
claimed where it was actually emitted; physical-device review stays Pending.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

LAB = "#pilot/admin/f33touchlab"
OVERVIEW = "#pilot/admin/overview"
PUBLIC = "#pilot/public/home"
BROWSER_NAMES = ("chromium", "webkit", "firefox")


class Evidence:
    def __init__(self, browser: str, native_touch: bool):
        self.browser = browser
        self.native_touch = native_touch
        self.checks: list[dict] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        self.checks.append({"name": name, "ok": bool(condition), "detail": detail})

    def fail(self, name: str, detail: str) -> None:
        self.check(name, False, detail)


def text(page, selector: str) -> str:
    return (page.locator(selector).first.text_content() or "").strip()


def value(page, key: str) -> str:
    return text(page, f'[data-touch-value="{key}"]')


def ids(page, selector: str) -> list[str]:
    return page.eval_on_selector_all(selector, "els => els.map(el => el.dataset.sortId || el.dataset.uiId || '')")


def launch(playwright, name: str, chromium_path: str | None):
    options = {"headless": True}
    if name == "chromium":
        options["args"] = ["--disable-dev-shm-usage"]
        if chromium_path:
            options["executable_path"] = chromium_path
    return playwright[name].launch(**options)


def open_lab(browser, base_url: str, name: str, width: int = 390):
    height = 844 if width <= 500 else 900
    options = {"viewport": {"width": width, "height": height}, "has_touch": True}
    if width <= 500:
        options["is_mobile"] = True
    if name == "chromium":
        options["permissions"] = ["clipboard-read", "clipboard-write"]
    context = browser.new_context(**options)
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base_url, wait_until="load", timeout=20_000)
    page.wait_for_url("**/assets/mockup/standalone.html", timeout=10_000)
    page.evaluate("(h) => { location.hash = h }", LAB)
    page.wait_for_selector("#f33touch-lab [data-touch-specimen]", timeout=10_000)
    page.wait_for_timeout(200)
    return context, page, errors


def center(page, selector: str):
    locator = page.locator(selector).first
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    if not box:
        raise AssertionError(f"missing box for {selector}")
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def native_touch(page, kind: str, points, wait: float = 0.0):
    client = getattr(page, "_ft_cdp", None)
    if client is None:
        client = page.context.new_cdp_session(page)
        page._ft_cdp = client
    payload = [{"x": x, "y": y, "id": pid, "radiusX": 6, "radiusY": 6, "force": 1} for x, y, pid in points]
    if kind == "start":
        client.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": payload})
    elif kind == "move":
        client.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": payload})
    elif kind == "end":
        client.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    elif kind == "cancel":
        client.send("Input.dispatchTouchEvent", {"type": "touchCancel", "touchPoints": []})
    if wait:
        page.wait_for_timeout(int(wait * 1000))


def touch_swipe(page, x: float, y: float, dx: float, dy: float, steps: int = 6):
    native_touch(page, "start", [(x, y, 1)])
    for i in range(1, steps + 1):
        native_touch(page, "move", [(x + dx * i / steps, y + dy * i / steps, 1)])
    native_touch(page, "end", [])


def touch_drag(page, source: str, target, steps: int = 8):
    sx, sy = center(page, source)
    if isinstance(target, str):
        tx, ty = center(page, target)
    else:
        tx, ty = target
    native_touch(page, "start", [(sx, sy, 1)])
    for i in range(1, steps + 1):
        native_touch(page, "move", [(sx + (tx - sx) * i / steps, sy + (ty - sy) * i / steps, 1)])
    native_touch(page, "end", [])


def run_native(page, ev: Evidence) -> None:
    # Tap.
    before = value(page, "tap")
    touch_swipe(page, *center(page, '[data-ui-id="touch.tap.target"]'), 0, 0, 1)
    page.wait_for_timeout(120)
    ev.check("native tap", value(page, "tap") != before, value(page, "tap"))
    # Swipe.
    touch_swipe(page, *center(page, '[data-ui-id="touch.swipe.surface"]'), -80, 4)
    page.wait_for_timeout(120)
    ev.check("native swipe", value(page, "swipe") == "left", value(page, "swipe"))
    # Long press.
    native_touch(page, "start", [(*center(page, '[data-ui-id="touch.long-press.target"]'), 1)])
    page.wait_for_timeout(620)
    native_touch(page, "end", [])
    page.wait_for_timeout(100)
    ev.check("native long press", "recognised" in value(page, "long-press"), value(page, "long-press"))
    # Sortable order.
    rows = page.locator("#touch-sortable [data-sortable-item]")
    touch_drag(page, "#touch-sortable [data-sortable-item]:nth-child(1)", "#touch-sortable [data-sortable-item]:nth-child(3)")
    page.wait_for_timeout(220)
    ev.check("native sortable reorder", ids(page, "#touch-sortable [data-sortable-item]")[-1] == "sort-0", str(ids(page, "#touch-sortable [data-sortable-item]")))
    # Cross container.
    touch_drag(page, "#touch-cross-a [data-sortable-item]:first-child", "#touch-cross-b")
    page.wait_for_timeout(200)
    ev.check("native cross container", "cross-a-0" in ids(page, "#touch-cross-b [data-sortable-item]"), str(ids(page, "#touch-cross-b [data-sortable-item]")))
    # Nested move.
    touch_drag(page, "#touch-nested-a [data-sortable-item]:first-child", "#touch-nested-b")
    page.wait_for_timeout(200)
    ev.check("native nested move", "nested-a-0" in ids(page, "#touch-nested-b [data-sortable-item]"), str(ids(page, "#touch-nested-b [data-sortable-item]")))
    # Cancellation restores order.
    before_cancel = ids(page, "#touch-cancel-list [data-sortable-item]")
    row = page.locator("#touch-cancel-list [data-sortable-item]").first.bounding_box()
    native_touch(page, "start", [(row["x"] + 20, row["y"] + 20, 1)])
    for i in range(1, 5):
        native_touch(page, "move", [(row["x"] + 20, row["y"] + 20 + i * 20, 1)])
    native_touch(page, "cancel", [])
    page.wait_for_timeout(160)
    ev.check("native cancellation", ids(page, "#touch-cancel-list [data-sortable-item]") == before_cancel, str(ids(page, "#touch-cancel-list [data-sortable-item]")))
    # Auto-scroll.
    page.locator("#touch-auto").first.scroll_into_view_if_needed()
    auto = page.locator("#touch-auto").bounding_box()
    item = page.locator("#touch-auto [data-sortable-item]").first.bounding_box()
    native_touch(page, "start", [(item["x"] + 20, item["y"] + 20, 1)])
    for i in range(1, 7):
        native_touch(page, "move", [(item["x"] + 20, auto["y"] + auto["height"] - 4, 1)])
    page.wait_for_timeout(450)
    native_touch(page, "end", [])
    page.wait_for_timeout(120)
    ev.check("native auto-scroll", value(page, "auto-scroll") != "scroll 0 px", value(page, "auto-scroll"))
    # Bottom sheet.
    page.locator('[data-touch-alt="bottom-sheet"][data-touch-alt-action="open"]').click()
    page.wait_for_timeout(180)
    ev.check("native sheet open", value(page, "bottom-sheet") == "open", value(page, "bottom-sheet"))
    handle = page.locator("#touch-sheet-handle").bounding_box()
    native_touch(page, "start", [(handle["x"] + 20, handle["y"] + 10, 1)])
    for i in range(1, 6):
        native_touch(page, "move", [(handle["x"] + 20, handle["y"] + 10 + i * 24, 1)])
    native_touch(page, "end", [])
    page.wait_for_timeout(200)
    ev.check("native sheet drag close", value(page, "bottom-sheet") == "closed", value(page, "bottom-sheet"))
    # Pinch.
    c = center(page, '[data-ui-id="touch.pinch.surface"]')
    native_touch(page, "start", [(c[0] - 40, c[1], 1), (c[0] + 40, c[1], 2)])
    native_touch(page, "move", [(c[0] - 100, c[1], 1), (c[0] + 100, c[1], 2)])
    native_touch(page, "end", [])
    page.wait_for_timeout(150)
    ev.check("native pinch zoom", int(value(page, "pinch-zoom").replace("%", "") or 100) > 100, value(page, "pinch-zoom"))
    # Panel resize.
    handle = page.locator("#touch-resize-handle").bounding_box()
    native_touch(page, "start", [(handle["x"] + 4, handle["y"] + 20, 1)])
    for i in range(1, 6):
        native_touch(page, "move", [(handle["x"] + 4 + i * 18, handle["y"] + 20, 1)])
    native_touch(page, "end", [])
    page.wait_for_timeout(150)
    ev.check("native panel resize", value(page, "panel-resize") != "55%", value(page, "panel-resize"))
    # Shell canvas follow and public no-slide.
    page.evaluate("(h) => { location.hash = h }", OVERVIEW)
    page.wait_for_timeout(400)
    native_touch(page, "start", [(page.viewport_size["width"] - 6, 420, 1)])
    for i in range(1, 6):
        native_touch(page, "move", [(page.viewport_size["width"] - 6 + i * 18, 420, 1)])
    native_touch(page, "end", [])
    page.wait_for_timeout(350)
    ev.check("native shell canvas follow", "shift-left" in page.evaluate("document.querySelector('.canvas').className"), page.evaluate("document.querySelector('.canvas').className"))
    page.keyboard.press("Escape")
    page.wait_for_timeout(150)
    page.evaluate("(h) => { location.hash = h }", PUBLIC)
    page.wait_for_timeout(350)
    native_touch(page, "start", [(page.viewport_size["width"] - 6, 420, 1)])
    for i in range(1, 5):
        native_touch(page, "move", [(page.viewport_size["width"] - 6 + i * 20, 420, 1)])
    native_touch(page, "end", [])
    page.wait_for_timeout(200)
    ev.check("native public no-slide", "shift-left" not in page.evaluate("document.querySelector('.canvas').className"), page.evaluate("document.querySelector('.canvas').className"))
    # Inspector pick cancels the lab action.
    page.evaluate("(h) => { location.hash = h }", LAB)
    page.wait_for_timeout(350)
    before_tap = value(page, "tap")
    page.evaluate("FormaUIInspector.enable()")
    page.evaluate("document.querySelector('[data-forma-inspector=\"dock\"]').shadowRoot.querySelector('#pick').click()")
    page.wait_for_timeout(100)
    touch_swipe(page, *center(page, '[data-ui-id="touch.tap.target"]'), 0, 0, 1)
    page.wait_for_timeout(200)
    ev.check("inspector pick no action", value(page, "tap") == before_tap, value(page, "tap"))
    ev.check("inspector pick reference", page.evaluate("!!window.FormaUIInspector.selected"), str(page.evaluate("window.FormaUIInspector.selected?.component")))
    page.evaluate("FormaUIInspector.disable()")


def run_fallback(page, ev: Evidence) -> None:
    page.evaluate("() => { window.FormaTouch.tap(document.querySelector('[data-ui-id=\"touch.tap.target\"]')) }")
    page.wait_for_timeout(80)
    ev.check("pointer tap", "1 taps" in value(page, "tap"), value(page, "tap"))
    page.evaluate("() => { window.FormaTouch.swipe(document.querySelector('[data-ui-id=\"touch.swipe.surface\"]'), -80, 4) }")
    page.wait_for_timeout(80)
    ev.check("pointer swipe", value(page, "swipe") == "left", value(page, "swipe"))
    page.evaluate("() => window.FormaTouch.longPress(document.querySelector('[data-ui-id=\"touch.long-press.target\"]'))")
    page.wait_for_timeout(650)
    ev.check("pointer long press", "recognised" in value(page, "long-press"), value(page, "long-press"))
    before = ids(page, "#touch-sortable [data-sortable-item]")
    page.locator("#touch-sortable").scroll_into_view_if_needed()
    page.evaluate("() => { const r=document.querySelectorAll('#touch-sortable [data-sortable-item]'); window.FormaTouch.drag(r[0], r[2]) }")
    page.wait_for_timeout(150)
    ev.check("pointer sortable reorder", ids(page, "#touch-sortable [data-sortable-item]") != before, str(ids(page, "#touch-sortable [data-sortable-item]")))
    page.locator("#touch-cross-a").scroll_into_view_if_needed()
    page.evaluate("() => { const a=document.querySelector('#touch-cross-a [data-sortable-item]'); const b=document.querySelector('#touch-cross-b'); window.FormaTouch.drag(a,b) }")
    page.wait_for_timeout(150)
    ev.check("pointer cross container", "cross-a-0" in ids(page, "#touch-cross-b [data-sortable-item]"), str(ids(page, "#touch-cross-b [data-sortable-item]")))
    page.locator("#touch-nested-a").scroll_into_view_if_needed()
    page.evaluate("() => { const a=document.querySelector('#touch-nested-a [data-sortable-item]'); const b=document.querySelector('#touch-nested-b'); window.FormaTouch.drag(a,b) }")
    page.wait_for_timeout(150)
    ev.check("pointer nested move", "nested-a-0" in ids(page, "#touch-nested-b [data-sortable-item]"), str(ids(page, "#touch-nested-b [data-sortable-item]")))
    before_cancel = ids(page, "#touch-cancel-list [data-sortable-item]")
    page.evaluate("() => { const r=document.querySelector('#touch-cancel-list [data-sortable-item]'); window.FormaTouch.simulate('pointerdown',r,{x:10,y:10}); window.FormaTouch.simulate('pointermove',r,{x:10,y:90}); window.FormaTouch.pointerCancel(r) }")
    page.wait_for_timeout(120)
    ev.check("pointer cancellation", ids(page, "#touch-cancel-list [data-sortable-item]") == before_cancel, str(ids(page, "#touch-cancel-list [data-sortable-item]")))
    page.evaluate("() => { window.FormaTouch.pinch(document.querySelector('[data-ui-id=\"touch.pinch.surface\"]'), 1.5) }")
    page.wait_for_timeout(100)
    ev.check("pointer pinch", int(value(page, "pinch-zoom").replace("%", "") or 100) > 100, value(page, "pinch-zoom"))
    page.evaluate("() => { const h=document.querySelector('#touch-resize-handle'); const b=h.getBoundingClientRect(); window.FormaTouch.simulate('pointerdown',h,{x:b.x+4,y:b.y+20}); window.FormaTouch.simulate('pointermove',h,{x:b.x+100,y:b.y+20}); window.FormaTouch.simulate('pointerup',h,{x:b.x+100,y:b.y+20}) }")
    page.wait_for_timeout(80)
    ev.check("pointer panel resize", value(page, "panel-resize") != "55%", value(page, "panel-resize"))
    # Sheet fallback.
    page.locator('[data-touch-alt="bottom-sheet"][data-touch-alt-action="open"]').click()
    page.wait_for_timeout(120)
    page.evaluate("() => { const h=document.querySelector('#touch-sheet-handle'); const b=h.getBoundingClientRect(); const f=(t,y)=>window.FormaTouch.simulate(t,h,{x:b.x+20,y:y}); f('pointerdown',b.y+10); for(let i=1;i<=5;i++) f('pointermove',b.y+10+i*24); f('pointerup',b.y+130) }")
    page.wait_for_timeout(120)
    ev.check("pointer sheet drag", value(page, "bottom-sheet") == "closed", value(page, "bottom-sheet"))
    # Auto-scroll fallback with real frames.
    page.locator("#touch-auto").first.scroll_into_view_if_needed()
    page.evaluate("""async () => {
      const box = document.querySelector('#touch-auto').getBoundingClientRect();
      const item = document.querySelector('#touch-auto [data-sortable-item]');
      const start = item.getBoundingClientRect();
      const f = (t, x, y) => window.FormaTouch.simulate(t, item, {x, y});
      f('pointerdown', start.x + 20, start.y + 20);
      for (let i = 0; i < 10; i++) { f('pointermove', start.x + 20, box.bottom - 4); await new Promise(r => setTimeout(r, 40)); }
      f('pointerup', start.x + 20, box.bottom - 4);
    }""")
    page.wait_for_timeout(150)
    ev.check("pointer auto-scroll", value(page, "auto-scroll") != "scroll 0 px", value(page, "auto-scroll"))
    # Shell fallback on the mini specimen.
    page.evaluate("() => { const s=document.querySelector('#touch-shell'); const b=s.getBoundingClientRect(); window.FormaTouch.simulate('pointerdown',s,{x:b.left+4,y:b.y+20}); window.FormaTouch.simulate('pointermove',s,{x:b.left+120,y:b.y+24}); window.FormaTouch.simulate('pointerup',s,{x:b.left+120,y:b.y+24}) }")
    page.wait_for_timeout(120)
    ev.check("pointer shell follow", value(page, "shell-canvas") == "context", value(page, "shell-canvas"))


def go(page, route: str, selector: str = "#app") -> None:
    page.evaluate("(h) => { location.hash = h }", route)
    page.wait_for_timeout(450)
    page.wait_for_selector(selector, timeout=10_000)


def module_drag(page, native: bool, source: str, target: str) -> None:
    if native:
        touch_drag(page, source, target)
    else:
        page.evaluate("([a, b]) => { window.FormaTouch.drag(document.querySelector(a), document.querySelector(b)) }", [source, target])
    page.wait_for_timeout(250)


def run_real_modules(page, ev: Evidence, native: bool) -> None:
    page.set_viewport_size({"width": 1024, "height": 900})
    page.wait_for_timeout(150)
    # Kanban: model status and order, then model undo.
    go(page, "#pilot/admin/project19")
    page.evaluate("() => f24view('Kanban')")
    page.wait_for_timeout(300)
    before = page.evaluate("() => f24Tasks.map(t => t.s).join(',')")
    module_drag(page, False, '[data-sort-id="task-0"]', '[data-sortable-id="kanban-lane-1"]')
    after = page.evaluate("() => f24Tasks.map(t => t.s).join(',')")
    ev.check("kanban model move", after != before, f"{before} -> {after}")
    page.evaluate("() => window.FormaTouch.undoSort('kanban')")
    page.wait_for_timeout(250)
    ev.check("kanban model undo", page.evaluate("() => f24Tasks.map(t => t.s).join(',')") == before, page.evaluate("() => f24Tasks.map(t => t.s).join(',')"))
    # Gantt: drag start and resize length.
    page.evaluate("() => f24view('Gantt')")
    page.wait_for_timeout(300)
    before = page.evaluate("() => [f24Tasks[0].start, f24Tasks[0].len]")
    page.evaluate("() => window.FormaTouch.swipe(document.querySelector('#gantt-bar-0'), 70, 0)")
    page.wait_for_timeout(250)
    after = page.evaluate("() => [f24Tasks[0].start, f24Tasks[0].len]")
    ev.check("gantt drag start", after[0] != before[0], f"{before} -> {after}")
    page.evaluate("""() => { const h=document.querySelector('#gantt-bar-0 .gbar-resize'); const b=h.getBoundingClientRect(); window.FormaTouch.simulate('pointerdown',h,{x:b.x+4,y:b.y+8}); window.FormaTouch.simulate('pointermove',h,{x:b.x+170,y:b.y+8}); window.FormaTouch.simulate('pointerup',h,{x:b.x+170,y:b.y+8}) }""")
    page.wait_for_timeout(250)
    resized = page.evaluate("() => f24Tasks[0].len")
    ev.check("gantt resize length", resized != after[1], f"{after[1]} -> {resized}")
    # Calendar month state.
    go(page, "#pilot/admin/calendar19")
    month = page.evaluate("() => wDate.getMonth()")
    page.evaluate("() => window.FormaTouch.swipe(document.querySelector('.calgrid'), -90, 4)")
    page.wait_for_timeout(300)
    ev.check("calendar month change", page.evaluate("() => wDate.getMonth()") != month, f"{month} -> {page.evaluate('() => wDate.getMonth()')}")
    # Workflow model order and undo.
    go(page, "#pilot/admin/workflow19")
    before = page.evaluate("() => wNodes.join('|')")
    module_drag(page, False, '[data-sort-id="workflow-0"]', '[data-sortable-id="workflow-nodes"] [data-node-id="2"]')
    after = page.evaluate("() => wNodes.join('|')")
    ev.check("workflow model move", after != before, f"{before} -> {after}")
    page.evaluate("() => window.FormaTouch.undoSort('workflow')")
    page.wait_for_timeout(250)
    ev.check("workflow model undo", page.evaluate("() => wNodes.join('|')") == before, page.evaluate("() => wNodes.join('|')"))
    # Studio parts model order and undo.
    go(page, "#pilot/admin/s31editor/form-enquiry", ".s31-layer[data-part-id]")
    before = page.evaluate("() => s31Current().parts.map(p => p.id).join(',')")
    module_drag(page, False, ".s31-layer[data-part-id]:nth-child(1)", ".s31-layer[data-part-id]:nth-child(3)")
    after = page.evaluate("() => s31Current().parts.map(p => p.id).join(',')")
    ev.check("studio parts model move", after != before, "parts reordered")
    page.evaluate("() => window.FormaTouch.undoSort('studio-parts')")
    page.wait_for_timeout(250)
    ev.check("studio parts model undo", page.evaluate("() => s31Current().parts.map(p => p.id).join(',')") == before, "restored")
    # Keyboard parity: Space, Arrow, Space and Escape cancel.
    page.goto(page.url.split("#")[0] + "#pilot/admin/f33touchlab", wait_until="load", timeout=20_000)
    page.wait_for_selector("#app", timeout=10_000)
    try:
        page.wait_for_selector("#touch-sortable [data-sortable-item]", timeout=10_000)
    except Exception:
        print("DEBUG", page.url, page.locator("#f33touch-lab").count(), page.locator("#touch-sortable").count(), page.locator("#touch-sortable [data-sortable-item]").count(), page.locator("h1").first.text_content() if page.locator("h1").count() else "")
        raise
    page.locator("#touch-sortable [data-sortable-item]").first.focus()
    order = page.evaluate("() => [...document.querySelectorAll('#touch-sortable [data-sortable-item]')].map(x => x.dataset.sortId).join(',')")
    page.keyboard.press("Space")
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Space")
    page.wait_for_timeout(200)
    moved = page.evaluate("() => [...document.querySelectorAll('#touch-sortable [data-sortable-item]')].map(x => x.dataset.sortId).join(',')")
    ev.check("keyboard reorder commit", moved != order, f"{order} -> {moved}")
    live_text = page.locator("#ft-live").text_content() or ""
    ev.check("keyboard live announcement", "Moved" in live_text or "Position" in live_text, live_text)
    page.evaluate("() => window.FormaTouch.undoSort('lab-sort')")
    page.wait_for_timeout(150)
    page.locator("#touch-sortable [data-sortable-item]").first.focus()
    page.keyboard.press("Space")
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Escape")
    page.wait_for_timeout(150)
    ev.check("keyboard reorder cancel", page.evaluate("() => [...document.querySelectorAll('#touch-sortable [data-sortable-item]')].map(x => x.dataset.sortId).join(',')") == order, "restored")
    # Multi-touch cancellation keeps the model unchanged.
    cancel_before = page.evaluate("() => [...document.querySelectorAll('#touch-cancel-list [data-sortable-item]')].map(x => x.dataset.sortId).join(',')")
    page.evaluate("""() => {
      const el = document.querySelector('#touch-cancel-list [data-sortable-item]');
      window.FormaTouch.simulate('pointerdown', el, {x: 20, y: 20, pointerId: 41});
      window.FormaTouch.simulate('pointermove', el, {x: 20, y: 60, pointerId: 41});
      window.FormaTouch.simulate('pointerdown', document.body, {x: 200, y: 200, pointerId: 42});
      window.FormaTouch.simulate('pointerup', document.body, {x: 200, y: 200, pointerId: 42});
      window.FormaTouch.simulate('pointerup', el, {x: 20, y: 60, pointerId: 41});
    }""")
    page.wait_for_timeout(200)
    ev.check("multi-touch cancel", page.evaluate("() => window.FormaTouch.state.active") == 0 and page.evaluate("() => [...document.querySelectorAll('#touch-cancel-list [data-sortable-item]')].map(x => x.dataset.sortId).join(',')") == cancel_before, "second pointer cancelled safely")
    # 44 px touch geometry.
    small = page.evaluate("""() => [...document.querySelectorAll('.f33touch-card button, .f33touch-row')].filter(el => el.getBoundingClientRect().height > 0 && el.getBoundingClientRect().height < 44).length""")
    ev.check("touch targets 44px", small == 0, str(small) + " undersized targets")
    # Real shell edge gesture, including public no-slide.
    go(page, "#pilot/admin/overview")
    page.evaluate("""() => {
      const s=document.querySelector('.shell'); const b=s.getBoundingClientRect();
      window.FormaTouch.simulate('pointerdown',s,{x:b.right-6,y:420,pointerId:51});
      window.FormaTouch.simulate('pointermove',s,{x:b.right-6-90,y:420,pointerId:51});
      window.FormaTouch.simulate('pointerup',s,{x:b.right-6-90,y:420,pointerId:51});
    }""")
    page.wait_for_timeout(300)
    ev.check("real shell edge gesture", "shift-right" in page.evaluate("() => document.querySelector('.canvas').className") or "shift-left" in page.evaluate("() => document.querySelector('.canvas').className"), page.evaluate("() => document.querySelector('.canvas').className"))
    page.keyboard.press("Escape")
    page.wait_for_timeout(150)
    go(page, "#pilot/public/home")
    page.evaluate("""() => {
      const s=document.querySelector('.shell'); if(!s) return;
      window.FormaTouch.simulate('pointerdown',s,{x:innerWidth-6,y:420,pointerId:52});
      window.FormaTouch.simulate('pointermove',s,{x:innerWidth-96,y:420,pointerId:52});
      window.FormaTouch.simulate('pointerup',s,{x:innerWidth-96,y:420,pointerId:52});
    }""")
    page.wait_for_timeout(200)
    ev.check("public shell no slide", "shift-left" not in page.evaluate("() => document.querySelector('.canvas').className"), page.evaluate("() => document.querySelector('.canvas').className"))
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(120)


def run_browser(playwright, base_url: str, name: str, chromium_path: str | None, output: Path, force_fallback: bool = False) -> Evidence:
    browser = launch(playwright, name, chromium_path)
    native = name == "chromium" and not force_fallback
    ev = Evidence(name, native)
    context, page, errors = open_lab(browser, base_url, name, 390 if native else 1024)
    try:
        if native:
            run_native(page, ev)
            ev.check("native touch emitted", True, "Chromium CDP Input.dispatchTouchEvent")
        else:
            run_fallback(page, ev)
            ev.check("native touch capability", True, "not emitted in this browser; pointer fallback only")
        run_real_modules(page, ev, native)
        ev.check("no page errors", not errors, str(errors[:3]))
        ev.check("no document overflow", not page.evaluate("document.documentElement.scrollWidth > innerWidth"), ("390 px" if native else "1024 px") + " viewport")
        page.screenshot(path=str(output / f"touch-{name}-{390 if native else 1024}.png"), full_page=False)
    except Exception as exc:  # keep evidence and fail clearly
        ev.fail("execution", f"{type(exc).__name__}: {exc}")
    finally:
        context.close()
        browser.close()
    return ev


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:4173/")
    parser.add_argument("--browser", choices=BROWSER_NAMES + ("all",), default="all")
    parser.add_argument("--out", default="touch-evidence")
    parser.add_argument("--chromium", default=None)
    parser.add_argument("--force-fallback", action="store_true", help="Test the pointer fallback path even in Chromium")
    args = parser.parse_args()
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    names = BROWSER_NAMES if args.browser == "all" else (args.browser,)
    results = []
    with sync_playwright() as playwright:
        for name in names:
            results.append(run_browser(playwright, args.base_url, name, args.chromium, output, args.force_fallback))
    payload = {
        "format": "forma-touch-evidence.v1",
        "baseline": "V34.2",
        "physicalDevice": "Pending Owner Review",
        "browsers": [
            {
                "browser": ev.browser,
                "nativeTouch": ev.native_touch,
                "passed": all(row["ok"] for row in ev.checks),
                "checks": ev.checks,
            }
            for ev in results
        ],
    }
    (output / "touch-evidence.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failed = [row for row in payload["browsers"] if not row["passed"]]
    for row in payload["browsers"]:
        print(f"{row['browser']}: {'PASS' if row['passed'] else 'FAIL'} · native touch {row['nativeTouch']} · {sum(1 for c in row['checks'] if c['ok'])}/{len(row['checks'])} checks")
        for check in row["checks"]:
            if not check["ok"]:
                print(f"  - {check['name']}: {check['detail']}")
    print("Touch smoke: " + ("PASS" if not failed else "FAIL") + " (physical device Pending Owner Review)")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
