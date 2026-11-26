#!/usr/bin/env python3
"""Lightweight public-preview smoke test for the pinned mockup, layout templates and playground."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

LAYOUT_IDS = ["sidebar", "semi", "full", "fullscreen", "split", "centered", "inspector", "public"]
LAYOUT_WIDTHS = [1440, 768, 390, 320]
THEMES = ("light", "dark")


def run_case(browser, base_url: str, name: str, width: int, height: int, output: Path) -> None:
    context = browser.new_context(
        viewport={"width": width, "height": height},
        has_touch=width < 600,
        device_scale_factor=1,
    )
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    response = page.goto(base_url, wait_until="load", timeout=20_000)
    page.wait_for_url("**/assets/mockup/standalone.html", timeout=10_000)
    page.wait_for_selector("#app", timeout=10_000)
    if response is None or response.status != 200:
        raise AssertionError(f"{name}: root response did not return HTTP 200")
    if not page.title():
        raise AssertionError(f"{name}: mockup has no title")
    if page.locator("#app").count() != 1:
        raise AssertionError(f"{name}: expected one app root")
    if page.evaluate("!window.FormaUIInspector"):
        raise AssertionError(f"{name}: Inspector API is unavailable")

    page.evaluate("FormaUIInspector.enable()")
    page.wait_for_timeout(250)
    if not page.evaluate("FormaUIInspector.visible.length > 0"):
        raise AssertionError(f"{name}: Inspector exposes no visible elements")
    page.screenshot(path=str(output / f"{name}-debug.png"), full_page=False)
    page.evaluate("FormaUIInspector.disable()")
    page.wait_for_timeout(100)
    page.screenshot(path=str(output / f"{name}-clean.png"), full_page=False)

    if page.evaluate("document.documentElement.scrollWidth > innerWidth"):
        raise AssertionError(f"{name}: document has horizontal overflow")
    if errors:
        raise AssertionError(f"{name}: page errors: {errors}")
    context.close()


def open_layouts_page(browser, base_url: str, width: int):
    context = browser.new_context(
        viewport={"width": width, "height": 900},
        has_touch=width < 600,
        device_scale_factor=1,
        permissions=["clipboard-read", "clipboard-write"],
    )
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base_url, wait_until="load", timeout=20_000)
    page.wait_for_url("**/assets/mockup/standalone.html", timeout=10_000)
    page.wait_for_selector("#app", timeout=10_000)
    page.evaluate("(h) => { location.hash = h }", f"#pilot/admin/f33layouts/{LAYOUT_IDS[0]}")
    page.wait_for_selector("#f33pg-preview .f33pv-frame", timeout=10_000)
    if not page.evaluate("!!window.FormaLayouts"):
        raise AssertionError("layout: window.FormaLayouts test API is unavailable")
    return context, page, errors


def set_layout(page, template: str, theme: str, width: int) -> None:
    page.evaluate(
        "([t, th, w]) => { window.FormaLayouts.setConfig({template: t, theme: th, viewport: w}) }",
        [template, theme, width],
    )
    page.wait_for_function(
        "([t, th]) => {const f = document.querySelector('#f33pg-preview .f33pv-frame');"
        "return !!f && f.dataset.layoutTemplate === t && f.dataset.f33Theme === th}",
        arg=[template, theme],
        timeout=5_000,
    )
    page.wait_for_timeout(80)


def frame_state(page) -> dict:
    return page.evaluate(
        """() => {
          const frame = document.querySelector('#f33pg-preview .f33pv-frame');
          if (!frame) return null;
          const shown = el => {
            const style = getComputedStyle(el);
            const box = el.getBoundingClientRect();
            return box.width > 0 && box.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
          };
          const slots = [...frame.querySelectorAll('[data-layout-slot]')];
          return {
            width: Math.round(frame.getBoundingClientRect().width),
            theme: frame.dataset.f33Theme,
            background: getComputedStyle(frame).backgroundColor,
            rootId: frame.querySelector('[data-layout-slot="content-layout"]')?.dataset.uiId || '',
            slots: slots.filter(shown).map(el => ({id: el.dataset.uiId, component: el.dataset.uiComponent, slot: el.dataset.layoutSlot})),
            labels: [...frame.querySelectorAll('.f33pv-slotlabel')].filter(el => getComputedStyle(el).display !== 'none').length,
            canvasTransform: getComputedStyle(frame.querySelector('.f33pv-canvas')).transform,
            aiOpen: frame.dataset.aiOpen,
            aiSlot: !!frame.querySelector('[data-layout-slot="ai-sidebar"]'),
            overflow: document.documentElement.scrollWidth > innerWidth,
            stageScroll: (() => {const stage = frame.parentElement; return stage ? stage.scrollWidth > stage.clientWidth : false})()
          };
        }"""
    )


def check_layout(page, template: str, theme: str, width: int) -> None:
    state = frame_state(page)
    if state is None:
        raise AssertionError(f"{template}/{theme}/{width}: preview frame is missing")
    if state["width"] != width:
        raise AssertionError(f"{template}/{theme}/{width}: frame width is {state['width']}")
    if state["theme"] != theme:
        raise AssertionError(f"{template}/{theme}/{width}: preview theme did not update")
    expected = "rgb(32, 35, 42)" if theme == "dark" else "rgb(255, 255, 255)"
    if state["background"] != expected:
        raise AssertionError(f"{template}/{theme}/{width}: unexpected frame background {state['background']}")
    if state["overflow"]:
        raise AssertionError(f"{template}/{theme}/{width}: document has horizontal overflow")
    if not state["rootId"].startswith(f"layout.{template}"):
        raise AssertionError(f"{template}/{theme}/{width}: missing content layout root id")
    ids = [slot["id"] for slot in state["slots"]]
    if len(ids) != len(set(ids)):
        raise AssertionError(f"{template}/{theme}/{width}: duplicate slot identities")
    if len(ids) < 3:
        raise AssertionError(f"{template}/{theme}/{width}: expected at least three visible slots")
    for slot in state["slots"]:
        if slot["id"] != f"layout.{template}" and not slot["id"].startswith(f"layout.{template}."):
            raise AssertionError(f"{template}/{theme}/{width}: unstable slot id {slot['id']}")
        if not slot["component"] or not slot["component"].startswith("Core."):
            raise AssertionError(f"{template}/{theme}/{width}: slot {slot['slot']} has no semantic component")
    if state["labels"] == 0:
        raise AssertionError(f"{template}/{theme}/{width}: slot labels are not visible")
    classify = page.evaluate(
        """() => {
          const frame = document.querySelector('#f33pg-preview .f33pv-frame');
          const roots = [frame.querySelector('[data-layout-slot="content-layout"]'), frame.querySelector('[data-layout-slot="application-shell"]')].filter(Boolean);
          const slots = [...frame.querySelectorAll('[data-layout-slot]')].filter(el => el.getBoundingClientRect().height > 0);
          return {
            roots: roots.map(el => window.FormaUIInspector.classify(el)),
            slots: slots.slice(0, 4).map(el => window.FormaUIInspector.classify(el))
          };
        }"""
    )
    for row in classify["roots"] + classify["slots"]:
        if row["kind"] != "layout":
            raise AssertionError(f"{template}/{theme}/{width}: {row['component']} was not classified as layout")
    if template == "public" and state["aiSlot"]:
        raise AssertionError(f"{template}/{theme}/{width}: public layout must not render an assistant slot")


def check_inspector(page, template: str, width: int) -> int:
    page.evaluate("FormaUIInspector.enable()")
    page.evaluate("FormaUIInspector.refresh()")
    page.wait_for_timeout(220)
    rows = page.evaluate(
        "FormaUIInspector.visible.filter(row => row.component.startsWith('Core.Layout') || row.component === 'Core.AppShell' || row.component === 'Core.FrontendShell')"
    )
    if not rows:
        raise AssertionError(f"{template}/{width}: Inspector listed no layout identities")
    for row in rows:
        bounds = row["visibleBounds"]
        if bounds["width"] <= 0 or bounds["height"] <= 0:
            raise AssertionError(f"{template}/{width}: Inspector bounds are empty for {row['component']}")
    page.evaluate("FormaUIInspector.disable()")
    page.wait_for_timeout(60)
    return len(rows)


def check_interaction(page, template: str, width: int) -> None:
    if page.locator("#f33pg-preview [data-demo-row]").count():
        row = page.locator("#f33pg-preview [data-demo-row]").first
        row.click()
        if row.get_attribute("aria-pressed") != "true":
            raise AssertionError(f"{template}/{width}: generic row selection did not update")
        result = page.locator("#f33pg-preview [data-demo-result]").text_content() or ""
        if "Selected" not in result:
            raise AssertionError(f"{template}/{width}: generic selection feedback is missing")
    elif page.locator("#f33pg-preview [data-split-row]").count():
        page.locator("#f33pg-preview [data-split-row]").nth(1).click()
        page.wait_for_timeout(120)
        if page.locator("#f33pg-preview .f33pv-frame").get_attribute("data-mobile-pane") not in (None, "detail"):
            raise AssertionError(f"{template}/{width}: split detail pane did not open")
        title = page.locator("#f33pg-preview [data-demo-title]").text_content() or ""
        if "Item" not in title:
            raise AssertionError(f"{template}/{width}: split detail did not update")
        if page.locator("#f33pg-preview .f33pv-mobileback").is_visible():
            page.locator("#f33pg-preview .f33pv-mobileback").click()
    else:
        clicked = page.evaluate(
            """() => {
              const frame = document.querySelector('#f33pg-preview .f33pv-frame');
              const button = frame?.querySelector('.f33pv-content button, .f33pv-authcard button, .f33pv-hero button');
              if (!button) return false;
              button.click();
              return true;
            }"""
        )
        if not clicked:
            raise AssertionError(f"{template}/{width}: no generic interaction target")


def check_canvas(page, template: str, width: int) -> None:
    frame = "#f33pg-preview .f33pv-frame"
    if template == "public":
        if page.locator(f"{frame} [data-layout-slot='ai-sidebar']").count() != 0:
            raise AssertionError("public: assistant slot must stay absent")
        if frame_state(page)["canvasTransform"] not in ("none", "matrix(1, 0, 0, 1, 0, 0)"):
            raise AssertionError("public: canvas must not slide")
        return
    if page.locator("#f33pg-root [data-config-key='aiAssistant']").is_disabled():
        return
    page.evaluate("window.FormaLayouts.setConfig({aiAssistant: true})")
    page.wait_for_function(
        "() => {const f = document.querySelector('#f33pg-preview .f33pv-frame');"
        "return !!f && f.dataset.aiOpen === 'true' && getComputedStyle(f.querySelector('.f33pv-canvas')).transform !== 'none'}",
        timeout=5_000,
    )
    page.evaluate("window.FormaLayouts.setConfig({aiAssistant: false})")
    page.wait_for_function(
        "() => {const f = document.querySelector('#f33pg-preview .f33pv-frame');"
        "return !!f && f.dataset.aiOpen === 'false' && ['none','matrix(1, 0, 0, 1, 0, 0)'].includes(getComputedStyle(f.querySelector('.f33pv-canvas')).transform)}",
        timeout=5_000,
    )
    if width <= 900 and page.locator(f"{frame} [data-layout-slot='context-sidebar']").count():
        page.click(f"{frame} .f33pv-topbar button[aria-label='Open context navigation']")
        page.wait_for_function(
            "(s) => {const f = document.querySelector(s);return !!f && f.dataset.contextOpen === 'true'}",
            arg=frame,
            timeout=5_000,
        )
        page.click(f"{frame} .f33pv-context button[aria-label='Close context navigation']")
        page.wait_for_function(
            "(s) => {const f = document.querySelector(s);return !!f && f.dataset.contextOpen === 'false'}",
            arg=frame,
            timeout=5_000,
        )


def check_playground_clipboard(browser, base_url: str, width: int) -> None:
    context, page, errors = open_layouts_page(browser, base_url, width)
    page.evaluate("(h) => { location.hash = h }", "#pilot/admin/f33playground")
    page.wait_for_selector("#f33pg-preview .f33pv-frame", timeout=10_000)
    page.evaluate("() => { window.FormaLayouts.setConfig({template: 'sidebar'}) }")
    page.wait_for_timeout(150)
    page.get_by_text("Copy Layout Reference").click()
    page.wait_for_timeout(250)
    reference = json.loads(page.evaluate("navigator.clipboard.readText()"))
    if reference.get("format") != "forma.layout.reference.v1" or not reference.get("slots"):
        raise AssertionError("playground: copied layout reference is invalid")
    page.get_by_text("Copy Configuration").click()
    page.wait_for_timeout(250)
    config = json.loads(page.evaluate("navigator.clipboard.readText()"))
    if config.get("format") != "forma.layout.config.v1" or config.get("template") != "sidebar":
        raise AssertionError("playground: copied normalized configuration is invalid")
    page.evaluate("() => { navigator.clipboard.writeText = () => { throw new Error('blocked') } }")
    page.get_by_text("Copy Configuration").click()
    page.wait_for_timeout(250)
    fallback = page.locator("#f33pg-fallback")
    if fallback.is_hidden() or "forma.layout.config.v1" not in (fallback.input_value() or ""):
        raise AssertionError("playground: clipboard fallback did not expose the text")
    page.evaluate("() => { delete navigator.clipboard.writeText }")
    with page.expect_download(timeout=10_000) as download:
        page.get_by_text("Export JSON").click()
    path = download.value.path()
    exported = json.loads(Path(path).read_text(encoding="utf-8"))
    if exported.get("format") != "forma.layout.config.v1" or exported.get("template") != "sidebar":
        raise AssertionError("playground: downloaded configuration is invalid")
    if errors:
        raise AssertionError(f"playground: page errors: {errors}")
    context.close()


def run_layout_width(browser, base_url: str, width: int) -> int:
    context, page, errors = open_layouts_page(browser, base_url, width)
    cases = 0
    for template in LAYOUT_IDS:
        for theme in THEMES:
            set_layout(page, template, theme, width)
            check_layout(page, template, theme, width)
            cases += 1
        rows = check_inspector(page, template, width)
        if rows == 0:
            raise AssertionError(f"{template}/{width}: no layout Inspector rows")
    for template in LAYOUT_IDS:
        set_layout(page, template, "light", width)
        check_interaction(page, template, width)
        check_canvas(page, template, width)
    if width <= 390:
        page.click(".main .top button.mobile")
        if "shift-left" not in page.evaluate("document.querySelector('.canvas').className"):
            raise AssertionError(f"layout width {width}: outer context canvas did not shift")
        page.keyboard.press("Escape")
        page.evaluate("openChathead()")
        if "shift-right" not in page.evaluate("document.querySelector('.canvas').className"):
            raise AssertionError(f"layout width {width}: outer assistant canvas did not shift")
        page.evaluate("if (ai) toggleAI()")
    if errors:
        raise AssertionError(f"layout width {width}: page errors: {errors}")
    context.close()
    return cases


def layout_canonical_defaults() -> dict:
    registry = json.loads((Path(__file__).resolve().parents[1] / "references/LAYOUT_REGISTRY.json").read_text(encoding="utf-8"))
    return {
        template["id"]: {
            "template": template["id"],
            "viewport": 1440,
            "theme": "light",
            **template["defaults"],
            "contentWidth": "fluid",
        }
        for template in registry["templates"]
    }


def open_detail(page, template: str) -> dict:
    page.evaluate("(h) => { location.hash = h }", f"#pilot/admin/f33layouts/{template}")
    page.wait_for_function(
        "(t) => {const f = document.querySelector('#f33pg-preview .f33pv-frame');"
        "return !!f && f.dataset.layoutTemplate === t}",
        arg=template,
        timeout=10_000,
    )
    page.wait_for_timeout(120)
    return page.evaluate("window.FormaLayouts.getConfig()")


def check_direct_copies(browser, base_url: str) -> None:
    context, page, errors = open_layouts_page(browser, base_url, 390)
    for template in LAYOUT_IDS:
        open_detail(page, template)
        page.get_by_text("Copy Layout Reference").click()
        page.wait_for_timeout(150)
        reference = json.loads(page.evaluate("navigator.clipboard.readText()"))
        if reference.get("format") != "forma.layout.reference.v1" or reference.get("template") != template:
            raise AssertionError(f"{template}: direct-route layout reference is invalid")
        if reference.get("route") != f"pilot/admin/f33layouts/{template}":
            raise AssertionError(f"{template}: layout reference route is {reference.get('route')}")
        slots = reference.get("slots") or []
        if not slots or not all(str(row.get("id", "")).startswith(f"layout.{template}") for row in slots):
            raise AssertionError(f"{template}: layout reference slots lost their instance context")
        page.get_by_text("Copy Configuration").click()
        page.wait_for_timeout(150)
        config = json.loads(page.evaluate("navigator.clipboard.readText()"))
        if config.get("format") != "forma.layout.config.v1" or config.get("template") != template:
            raise AssertionError(f"{template}: direct-route normalized configuration is invalid")
        page.evaluate("() => { navigator.clipboard.writeText = () => { throw new Error('blocked') } }")
        page.get_by_text("Copy Configuration").click()
        page.wait_for_timeout(150)
        fallback = page.locator("#f33pg-fallback")
        if fallback.is_hidden():
            raise AssertionError(f"{template}: direct-route clipboard fallback is hidden")
        fallback_config = json.loads(fallback.input_value())
        if fallback_config.get("template") != template:
            raise AssertionError(f"{template}: clipboard fallback lost the template context")
        page.evaluate("() => { delete navigator.clipboard.writeText }")
    if errors:
        raise AssertionError(f"direct-route copies: page errors: {errors}")
    context.close()


def check_focus(browser, base_url: str) -> None:
    context, page, errors = open_layouts_page(browser, base_url, 1440)
    page.evaluate("(h) => { location.hash = h }", "#pilot/admin/f33playground")
    page.wait_for_selector("#f33pg-root [data-config-key='template']", timeout=10_000)
    select = page.locator("#f33pg-root [data-config-key='template']")
    select.focus()
    select.select_option("semi")
    page.wait_for_timeout(200)
    active = page.evaluate("document.activeElement?.dataset?.configKey || ''")
    value = page.evaluate("document.querySelector('#f33pg-root [data-config-key=template]')?.value")
    if active != "template":
        raise AssertionError(f"playground: focus left the Template select ({active or 'none'})")
    if value != "semi":
        raise AssertionError("playground: Template select did not apply the change")
    if errors:
        raise AssertionError(f"playground focus: page errors: {errors}")
    context.close()


def check_canonical_defaults(browser, base_url: str) -> None:
    defaults = layout_canonical_defaults()
    context, page, errors = open_layouts_page(browser, base_url, 1440)
    page.evaluate("(h) => { location.hash = h }", "#pilot/admin/f33playground")
    page.wait_for_selector("#f33pg-root [data-config-key='template']", timeout=10_000)
    page.evaluate(
        "() => { window.FormaLayouts.setConfig({template: 'sidebar', theme: 'dark', viewport: 390, "
        "contextSidebar: false, aiAssistant: true, contentWidth: 'narrow'}) }"
    )
    page.wait_for_timeout(200)
    for template in LAYOUT_IDS:
        actual = open_detail(page, template)
        expected = defaults[template]
        if actual != expected:
            raise AssertionError(f"{template}: direct route kept stale playground state: {actual}")
        pressed = page.evaluate(
            """() => document.querySelector("#f33pg-root [data-config-key=viewport][data-config-value='1440']")?.getAttribute('aria-pressed')"""
        )
        if pressed != "true":
            raise AssertionError(f"{template}: controls do not expose canonical defaults")
    if errors:
        raise AssertionError(f"canonical defaults: page errors: {errors}")
    context.close()


def check_inactive_controls(browser, base_url: str) -> None:
    defaults = layout_canonical_defaults()
    context, page, errors = open_layouts_page(browser, base_url, 390)
    for template in LAYOUT_IDS:
        open_detail(page, template)
        state = page.evaluate(
            """() => {
              const frame = document.querySelector('#f33pg-preview .f33pv-frame');
              return {
                contextSlot: frame.querySelectorAll('[data-layout-slot="context-sidebar"]').length,
                contextButton: frame.querySelectorAll('button[aria-label="Open context navigation"]').length,
                aiSlot: frame.querySelectorAll('[data-layout-slot="ai-sidebar"]').length,
                launcher: frame.querySelectorAll('.f33pv-launcher').length,
                aiOpen: frame.dataset.aiOpen,
                transform: getComputedStyle(frame.querySelector('.f33pv-canvas')).transform,
                aiDisabled: document.querySelector('#f33pg-root [data-config-key=aiAssistant]')?.disabled
              };
            }"""
        )
        expect_context = defaults[template]["contextSidebar"]
        if bool(state["contextSlot"]) != expect_context:
            raise AssertionError(f"{template}: context slot state does not match the canonical config")
        if state["contextButton"] != (1 if expect_context else 0):
            raise AssertionError(f"{template}: inert context control is present")
        if state["aiSlot"] or state["launcher"]:
            raise AssertionError(f"{template}: disabled AI rendered a target or launcher")
        if state["aiOpen"] != "false":
            raise AssertionError(f"{template}: disabled AI set ai-open")
        if state["transform"] not in ("none", "matrix(1, 0, 0, 1, 0, 0)"):
            raise AssertionError(f"{template}: disabled AI shifted the canvas")
        if state["aiDisabled"]:
            continue
        page.evaluate("() => { window.FormaLayouts.setConfig({aiAssistant: true}) }")
        page.wait_for_timeout(150)
        enabled = page.evaluate(
            """() => {
              const frame = document.querySelector('#f33pg-preview .f33pv-frame');
              return {slot: frame.querySelectorAll('[data-layout-slot="ai-sidebar"]').length,
                      launcher: frame.querySelectorAll('.f33pv-launcher').length,
                      aiOpen: frame.dataset.aiOpen};
            }"""
        )
        if enabled["slot"] != 1 or enabled["aiOpen"] != "true":
            raise AssertionError(f"{template}: enabled AI did not open a real panel")
        if enabled["launcher"] != (1 if template != "fullscreen" else 0):
            raise AssertionError(f"{template}: launcher does not follow the immersive exception")
        page.evaluate("() => { window.FormaLayouts.setConfig({aiAssistant: false}) }")
        page.wait_for_timeout(150)
        closed = page.evaluate(
            """() => {
              const frame = document.querySelector('#f33pg-preview .f33pv-frame');
              return {slot: frame.querySelectorAll('[data-layout-slot="ai-sidebar"]').length,
                      launcher: frame.querySelectorAll('.f33pv-launcher').length,
                      aiOpen: frame.dataset.aiOpen};
            }"""
        )
        if closed["slot"] or closed["launcher"] or closed["aiOpen"] != "false":
            raise AssertionError(f"{template}: disabling AI left an inert target")
    if errors:
        raise AssertionError(f"inactive controls: page errors: {errors}")
    context.close()


def check_labels_geometry(browser, base_url: str, width: int) -> None:
    context, page, errors = open_layouts_page(browser, base_url, width)
    for template in LAYOUT_IDS:
        page.evaluate("(h) => { location.hash = h }", f"#pilot/admin/f33layouts/{template}")
        page.wait_for_function(
            "(t) => {const f = document.querySelector('#f33pg-preview .f33pv-frame');"
            "return !!f && f.dataset.layoutTemplate === t}",
            arg=template,
            timeout=10_000,
        )
        page.evaluate("(w) => { window.FormaLayouts.setConfig({viewport: w}) }", width)
        page.wait_for_timeout(150)
        result = page.evaluate(
            """() => {
              const frame = document.querySelector('#f33pg-preview .f33pv-frame');
              const frameRect = frame.getBoundingClientRect();
              const problems = [];
              for (const slot of frame.querySelectorAll('[data-layout-slot]')) {
                const slotRect = slot.getBoundingClientRect();
                if (slotRect.height <= 0) continue;
                const label = slot.querySelector(':scope > .f33pv-slotlabel');
                const rootSlot = slot.dataset.layoutSlot === 'application-shell' || slot.dataset.layoutSlot === 'content-layout';
                if (!label) { if (!rootSlot) problems.push('missing label ' + slot.dataset.layoutSlot); continue; }
                const labelRect = label.getBoundingClientRect();
                if (labelRect.width < 8 || labelRect.height < 8) problems.push('label too small ' + slot.dataset.layoutSlot);
                const maxHeight = slot.dataset.layoutSlot === 'primary-sidebar' ? 25 : 19;
                if (labelRect.left < slotRect.left - 1 || labelRect.right > slotRect.right + 1 ||
                    labelRect.top < slotRect.top - 1 || labelRect.bottom > slotRect.top + maxHeight) {
                  problems.push('label outside ' + slot.dataset.layoutSlot);
                }
                const child = [...slot.children].find(el => !el.classList.contains('f33pv-slotlabel') && getComputedStyle(el).display !== 'none');
                if (child) {
                  const childRect = child.getBoundingClientRect();
                  if (childRect.height > 0 && childRect.top < labelRect.bottom - 1) problems.push('label overlaps content ' + slot.dataset.layoutSlot);
                }
                if (slotRect.right > frameRect.right + 1) problems.push('slot overflows frame ' + slot.dataset.layoutSlot);
              }
              return {
                problems,
                overflow: document.documentElement.scrollWidth > innerWidth,
                labels: frame.querySelectorAll('.f33pv-slotlabel').length,
                identities: frame.querySelectorAll('[data-ui-id]').length
              };
            }"""
        )
        if result["labels"] == 0:
            raise AssertionError(f"{template}/{width}: slot labels are not visible by default")
        if result["problems"]:
            raise AssertionError(f"{template}/{width}: slot label geometry: {result['problems'][:3]}")
        if result["overflow"]:
            raise AssertionError(f"{template}/{width}: slot labels caused document overflow")
    labels_toggle = page.locator("#f33pg-root .f33pg-controls label", has_text="Slot labels").locator("input")
    identities = page.evaluate("document.querySelectorAll('#f33pg-preview .f33pv-frame [data-ui-id]').length")
    labels_toggle.uncheck()
    page.wait_for_timeout(100)
    hidden = page.evaluate("document.querySelectorAll('#f33pg-preview .f33pv-slotlabel:not([hidden])').length")
    visible = page.evaluate("[...document.querySelectorAll('#f33pg-preview .f33pv-slotlabel')].filter(el => getComputedStyle(el).display !== 'none').length")
    remaining = page.evaluate("document.querySelectorAll('#f33pg-preview .f33pv-frame [data-ui-id]').length")
    if visible != 0 or remaining != identities:
        raise AssertionError(f"labels/{width}: toggle removed Inspector identities or left labels visible")
    labels_toggle.check()
    if errors:
        raise AssertionError(f"slot labels {width}: page errors: {errors}")
    context.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:4173/")
    parser.add_argument("--out", default="browser-evidence")
    parser.add_argument("--chromium", default=None, help="Optional Chromium executable path")
    args = parser.parse_args()
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        launch_options = {"headless": True, "args": ["--disable-dev-shm-usage"]}
        if args.chromium:
            launch_options["executable_path"] = args.chromium
        browser = playwright.chromium.launch(**launch_options)
        try:
            run_case(browser, args.base_url, "desktop-1440", 1440, 900, output)
            run_case(browser, args.base_url, "mobile-390", 390, 844, output)
            cases = 0
            for width in LAYOUT_WIDTHS:
                cases += run_layout_width(browser, args.base_url, width)
                check_labels_geometry(browser, args.base_url, width)
            check_direct_copies(browser, args.base_url)
            check_focus(browser, args.base_url)
            check_canonical_defaults(browser, args.base_url)
            check_inactive_controls(browser, args.base_url)
            check_playground_clipboard(browser, args.base_url, 390)
        finally:
            browser.close()
    print(
        "Browser smoke: PASS (desktop-1440, mobile-390, "
        f"{cases} layout theme cases at {', '.join(map(str, LAYOUT_WIDTHS))}, direct copies, focus, canonical defaults, inactive controls, label geometry, playground copy/export)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
