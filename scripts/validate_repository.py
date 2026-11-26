#!/usr/bin/env python3
"""Validate the public repository, immutable package baseline and safety boundary."""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "references"
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"JSON parse failed for {path.relative_to(ROOT)}: {exc}")
        return {}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


required = [
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "index.html",
    "release.json",
    "release-manifest.json",
    ".gitignore",
    "references/LAYOUT_REGISTRY.json",
    "references/INTERACTION_REGISTRY.json",
    "references/INTERACTION_COVERAGE.md",
    "docs/QUICKSTART.md",
    "docs/LIFECYCLE.md",
    "docs/RELEASES.md",
    ".github/pull_request_template.md",
    ".github/labels.json",
    ".github/workflows/ci.yml",
    ".github/workflows/pages.yml",
]
for rel in required:
    if not (ROOT / rel).is_file():
        fail(f"missing required file: {rel}")

issue_templates = [
    "ui_bug.yml",
    "responsive_bug.yml",
    "design_improvement.yml",
    "interaction_improvement.yml",
    "feature_request.yml",
]
issue_fields = [
    "Mockup Version",
    "Page / Route",
    "Component Name",
    "Component Reference ID",
    "Visual Design Key",
    "Viewport",
    "Screenshot",
    "Current Behavior",
    "Expected Behavior",
    "Priority",
    "Additional Notes",
]
for name in issue_templates:
    path = ROOT / ".github/ISSUE_TEMPLATE" / name
    if not path.is_file():
        fail(f"missing issue template: {name}")
        continue
    text = path.read_text(encoding="utf-8")
    for field in issue_fields:
        if field not in text:
            fail(f"{name}: missing issue field: {field}")

baseline = load_json(ROOT / ".github/package-baseline.json")
ORIGINAL_SOURCE_SHA256 = "2c5b17775227085a1f9ccebf1c84521d0857555b5431cdc55bff332f3fdf1db8"
if baseline.get("format") != "forma-package-baseline.v1":
    fail("unexpected package baseline format")
if baseline.get("baseline") != "V34.2":
    fail("package baseline must identify the current V34.2 baseline")
if baseline.get("member_checksum_scope") != "current V34.2 working tree":
    fail("package baseline must declare the current V34.2 member checksum scope")
if baseline.get("source") != "skill.zip" or baseline.get("source_sha256") != ORIGINAL_SOURCE_SHA256:
    fail("original source package provenance must stay immutable")
if not baseline.get("source_provenance"):
    fail("package baseline must distinguish source provenance from member checksums")
if baseline.get("file_count") != 60 or len(baseline.get("files", [])) != 60:
    fail("authorized dev baseline must contain exactly 60 V34.2 member files")
for row in baseline.get("files", []):
    path = ROOT / row["path"]
    if not path.is_file():
        fail(f"V34.2 member file missing: {row['path']}")
    elif path.stat().st_size != row["bytes"]:
        fail(f"V34.2 member file size changed: {row['path']}")
    elif sha256(path) != row["sha256"]:
        fail(f"V34.2 member file checksum changed: {row['path']}")

manifest = load_json(REF / "MANIFEST.json")
if manifest.get("scope") != "current V34.2 member checksums":
    fail("manifest must declare its current V34.2 member checksum scope")
for rel, expected in manifest.get("sha256", {}).items():
    path = ROOT / rel
    if not path.is_file() or sha256(path) != expected:
        fail(f"pinned manifest checksum failed: {rel}")

registry = load_json(REF / "COMPONENT_REGISTRY.json")
page_index = load_json(REF / "PAGE_INDEX.json")
visual = load_json(REF / "VISUAL_KEYS.json")
if len(registry.get("components", [])) != 166:
    fail("component registry must contain 166 mappings")
pages = page_index.get("pages", [])
if len(pages) != 128 or len({row.get("route") for row in pages}) != 128:
    fail("page index must contain 128 unique routes")
keys = visual.get("keys", [])
if len(keys) != 24 or len({row.get("id") for row in keys}) != 24:
    fail("visual keys must contain 24 unique IDs")
if registry.get("format") != "forma-ui-component-registry.v1":
    fail("unexpected component registry format")
if not str(page_index.get("baseline", "")).startswith("V34"):
    fail("page index baseline is not V34")
if not str(visual.get("baseline", "")).startswith("V34"):
    fail("visual keys baseline is not V34")

classify_rule = "kind:/^Core\\.Layout(\\.|$)/.test(explicit)||el.hasAttribute('data-layout-slot')?'layout':'content'"
for rel in ("assets/mockup/ui-inspector.js", "assets/mockup/standalone.html"):
    if classify_rule not in (ROOT / rel).read_text(encoding="utf-8"):
        fail(f"layout classification rule is out of sync in {rel}")

layout_registry = load_json(REF / "LAYOUT_REGISTRY.json")
layout_ids = ["sidebar", "semi", "full", "fullscreen", "split", "centered", "inspector", "public"]
layout_templates = layout_registry.get("templates", [])
component_names = {row.get("component") for row in registry.get("components", [])}
visual_ids = {row.get("id") for row in keys}
page_routes = {row.get("route") for row in pages}
if layout_registry.get("format") != "forma-layout-registry.v1":
    fail("unexpected layout registry format")
if layout_registry.get("configSchema") != "forma.layout.config.v1":
    fail("layout registry config schema must be forma.layout.config.v1")
if layout_registry.get("responsiveWidths") != [1440, 768, 390, 320]:
    fail("layout registry responsive widths must be 1440, 768, 390, 320")
if [row.get("id") for row in layout_templates] != layout_ids:
    fail("layout registry must contain exactly the eight layout ids in order")
layout_fields = layout_registry.get("config", {}).get("fields", {})
for field in ("template", "viewport", "theme", "contentWidth", "aiAssistant", "inspectorPanel"):
    if field not in layout_fields:
        fail(f"layout config schema missing field: {field}")
for required_route in ["pilot/admin/f33layouts", "pilot/admin/f33playground"] + [
    f"pilot/admin/f33layouts/{layout_id}" for layout_id in layout_ids
]:
    if required_route not in page_routes:
        fail(f"page index missing layout route: {required_route}")
for template in layout_templates:
    tid = template.get("id")
    if template.get("route") != f"pilot/admin/f33layouts/{tid}" or template.get("example_route") != template.get("route"):
        fail(f"{tid}: layout route does not match the direct route")
    shell = template.get("shell", {})
    content = template.get("content", {})
    if shell.get("region") != "shell" or content.get("region") != "content":
        fail(f"{tid}: shell and content regions must stay separate")
    if shell.get("component") not in component_names or content.get("component") not in component_names:
        fail(f"{tid}: layout root component missing from COMPONENT_REGISTRY")
    slots = template.get("slots", [])
    if not slots:
        fail(f"{tid}: layout has no slots")
    slot_names = [slot.get("name") for slot in slots]
    if len(slot_names) != len(set(slot_names)):
        fail(f"{tid}: duplicate slot names")
    for slot in slots:
        if slot.get("region") not in {"shell", "content"}:
            fail(f"{tid}.{slot.get('name')}: invalid slot region")
        if slot.get("component") not in component_names:
            fail(f"{tid}.{slot.get('name')}: slot component missing from COMPONENT_REGISTRY")
    components = template.get("components", {})
    for name in components.get("required", []) + components.get("optional", []):
        if name not in component_names:
            fail(f"{tid}: layout component missing from COMPONENT_REGISTRY: {name}")
    defaults = template.get("defaults", {})
    for field in ("primarySidebar", "contextSidebar", "pageHeader", "toolbar", "footer", "aiAssistant", "inspectorPanel"):
        if field not in defaults or not isinstance(defaults[field], bool):
            fail(f"{tid}: layout defaults missing boolean {field}")
    schema = template.get("config", {}).get("schema", {})
    for field in layout_fields:
        if field not in schema:
            fail(f"{tid}: per-layout schema missing {field}")
    for field, lock in template.get("locked", {}).items():
        if field not in layout_fields or not isinstance(lock.get("value"), bool) or not lock.get("reason"):
            fail(f"{tid}: invalid lock for {field}")
        if defaults.get(field) != lock.get("value"):
            fail(f"{tid}: lock value must match the default for {field}")
    responsive = template.get("responsive", {})
    if set(responsive) != {"1440", "768", "390", "320"} or not all(responsive.values()):
        fail(f"{tid}: responsive behavior must cover 1440, 768, 390 and 320")
    for key in template.get("visual_keys", []):
        if key not in visual_ids:
            fail(f"{tid}: unknown Visual Key {key}")
    example = template.get("example_html", "")
    if f'data-ui-id="layout.{tid}"' not in example:
        fail(f"{tid}: example_html missing the content layout root id")
    for slot in slots:
        slot_id = f'data-ui-id="layout.{tid}.{slot["name"]}"'
        if slot_id not in example:
            fail(f"{tid}: example_html missing {slot_id}")
        if f'data-layout-slot="{slot["name"]}"' not in example:
            fail(f"{tid}: example_html missing data-layout-slot for {slot["name"]}")

interaction_registry = load_json(REF / "INTERACTION_REGISTRY.json")
if interaction_registry.get("format") != "forma-interaction-registry.v1":
    fail("unexpected interaction registry format")
if interaction_registry.get("baseline") != "V34.2":
    fail("interaction registry baseline must be V34.2")
engine = interaction_registry.get("engine", {})
if "defineSortable" not in engine.get("api", []):
    fail("interaction engine must expose the model-backed defineSortable contract")
for api in ("state", "log", "gestures", "cancel", "simulate", "defineSortable", "undoSort", "redoSort", "announce"):
    if api not in engine.get("api", []):
        fail(f"interaction engine API missing: {api}")
if engine.get("name") != "FormaTouch":
    fail("interaction engine must be FormaTouch")
touch_keys = [row.get("id") for row in keys if str(row.get("id", "")).startswith("forma.touch.")]
if len(touch_keys) != 9 or set(touch_keys) != set(interaction_registry.get("touchVisualKeys", [])):
    fail("interaction registry must define the nine forma.touch.* keys")
specimens = interaction_registry.get("specimens", [])
if len(specimens) != 14 or len({row.get("id") for row in specimens}) != 14:
    fail("interaction registry must contain fourteen unique specimens")
interaction_rows = interaction_registry.get("interactions", [])
if len(interaction_rows) != 32 or len({row.get("id") for row in interaction_rows}) != 32:
    fail("interaction registry must contain 32 unique interactions")
interaction_ids = {row.get("id") for row in interaction_rows}
for required in ("shell.sidebar-swipe", "shell.ai-swipe", "core.tap", "core.sortable", "core.cancel", "core.pinch-zoom", "core.panel-resize", "kanban.reorder", "gantt.drag", "calendar.swipe", "workflow.node-drag", "builder.part-order"):
    if required not in interaction_ids:
        fail(f"interaction registry missing {required}")
for row in interaction_rows:
    if not row.get("component") or row.get("component") not in component_names:
        fail(f"{row.get('id')}: interaction component missing from COMPONENT_REGISTRY")
    if not row.get("visualKeys") or any(key not in visual_ids for key in row.get("visualKeys", [])):
        fail(f"{row.get('id')}: interaction Visual Key missing")
coverage = (REF / "INTERACTION_COVERAGE.md").read_text(encoding="utf-8")
if "lab-only" not in coverage or "Pending Owner Review" not in coverage:
    fail("coverage matrix must distinguish lab-only surfaces and pending physical review")
for template in layout_templates:
    if "touch" not in layout_registry:
        fail("layout registry must describe touch interaction impact")
        break
for route in ("pilot/admin/f33touch", "pilot/admin/f33touchlab"):
    if route not in page_routes:
        fail(f"page index missing touch route: {route}")

release = load_json(ROOT / "release.json")
release_manifest = load_json(ROOT / "release-manifest.json")
if release.get("version") != "v1.0.0-rc.1" or release_manifest.get("version") != "v1.0.0-rc.1":
    fail("release metadata must be v1.0.0-rc.1")
if release.get("stable") is not False or release.get("status") != "release-candidate":
    fail("release metadata must remain an unstable release candidate")

index_text = (ROOT / "index.html").read_text(encoding="utf-8")
if "assets/mockup/standalone.html" not in index_text:
    fail("root index does not target the unchanged standalone mockup")
pages_action = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
if "branches: [dev]" not in pages_action or "deploy-pages@v4" not in pages_action:
    fail("Pages deployment must target dev and use deploy-pages")

fixture_domains = {"example.com", "example.test", "example"}
allowed_urls = {
    "http://www.w3.org/2000/svg",
    "http://www.w3.org/2000/svg\\",
    "http://.",
}
text_suffixes = {".html", ".js", ".json", ".md", ".py", ".yml", ".yaml", ".txt"}
secret_patterns = {
    "GitHub token": re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "secret assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token|private[_-]?key)\b"
        r"\s*[:=]\s*[\"']?[A-Za-z0-9_./+-]{16,}"
    ),
}
url_pattern = re.compile(r"https?://[^\s\"'<>)]+")
email_pattern = re.compile(r"(?i)[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})")
real_emails: list[tuple[str, str, str]] = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in text_suffixes:
        continue
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    for label, pattern in secret_patterns.items():
        for match in pattern.finditer(text):
            fail(f"possible {label} in {rel}:{text.count(chr(10), 0, match.start()) + 1}")
    for match in url_pattern.finditer(text):
        value = match.group(0).rstrip(".,")
        if value in allowed_urls or value.startswith("http://.") or value.startswith("http://www.w3.org/2000/svg") or value == "http://":
            continue
        host = (urlparse(value).hostname or "").lower()
        if host in {"127.0.0.1", "localhost"}:
            continue
        if host in fixture_domains or host.endswith(".example.test") or host.endswith(".example") or host in {"github.com", "manonworkingarea.github.io", "docs.github.com"}:
            continue
        fail(f"unapproved URL in {rel}: {value}")
    for match in email_pattern.finditer(text):
        domain = match.group(1).lower()
        if domain in fixture_domains or domain.endswith(".example.test") or domain.endswith(".example"):
            continue
        real_emails.append((rel, str(text.count(chr(10), 0, match.start()) + 1), match.group(0)))
for rel, line, value in real_emails:
    fail(f"non-fixture email in {rel}:{line}: {value}")

png_signature = b"\x89PNG\r\n\x1a\n"
for path in sorted((ROOT / "assets/mockup/screenshots").glob("*.png")):
    try:
        data = path.read_bytes()
        if not data.startswith(png_signature):
            raise ValueError("invalid signature")
        offset = len(png_signature)
        chunks = []
        while offset < len(data):
            if offset + 12 > len(data):
                raise ValueError("truncated chunk")
            length = struct.unpack(">I", data[offset : offset + 4])[0]
            chunk_type = data[offset + 4 : offset + 8].decode("ascii")
            offset += 12 + length
            if offset > len(data):
                raise ValueError("chunk exceeds file")
            chunks.append(chunk_type)
        if chunks[:1] != ["IHDR"] or chunks[-1:] != ["IEND"]:
            raise ValueError("missing PNG header or terminator")
        unexpected = sorted(set(chunks) - {"IHDR", "IDAT", "IEND"})
        if unexpected:
            fail(f"unexpected PNG chunks in {path.name}: {unexpected}")
    except Exception as exc:
        fail(f"invalid PNG {path.name}: {exc}")

forbidden = ["engine", "wrangler.jsonc", "foundation.json", "wrangler.json"]
for value in forbidden:
    if (ROOT / value).exists():
        fail(f"forbidden AI Native Engine or infrastructure path present: {value}")

if ERRORS:
    print("Repository validation: FAIL", file=sys.stderr)
    for error in ERRORS:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print("Repository validation: PASS")
print(f"- original source provenance: skill.zip {ORIGINAL_SOURCE_SHA256[:12]}… (immutable)")
print(f"- current V34.2 member checksums: {baseline['file_count']} files verified")
print("- registry: 166 mappings")
print("- page index: 128 unique routes")
print("- visual keys: 24 unique IDs (9 forma.touch.*)")
print("- issue templates: 5 complete")
print("- public safety: no disallowed secrets, URLs, emails or PNG metadata")
