#!/usr/bin/env python3
"""Lightweight public-preview smoke test for the unchanged V34 mockup."""
from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


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
        finally:
            browser.close()
    print("Browser smoke: PASS (desktop-1440, mobile-390)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
