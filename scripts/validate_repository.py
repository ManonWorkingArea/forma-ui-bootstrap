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
if baseline.get("file_count") != 60 or len(baseline.get("files", [])) != 60:
    fail("package baseline must contain exactly 60 files")
for row in baseline.get("files", []):
    path = ROOT / row["path"]
    if not path.is_file():
        fail(f"original package file missing: {row['path']}")
    elif path.stat().st_size != row["bytes"]:
        fail(f"original package file size changed: {row['path']}")
    elif sha256(path) != row["sha256"]:
        fail(f"original package file checksum changed: {row['path']}")

manifest = load_json(REF / "MANIFEST.json")
for rel, expected in manifest.get("sha256", {}).items():
    path = ROOT / rel
    if not path.is_file() or sha256(path) != expected:
        fail(f"pinned manifest checksum failed: {rel}")

registry = load_json(REF / "COMPONENT_REGISTRY.json")
page_index = load_json(REF / "PAGE_INDEX.json")
visual = load_json(REF / "VISUAL_KEYS.json")
if len(registry.get("components", [])) != 114:
    fail("component registry must contain 114 mappings")
pages = page_index.get("pages", [])
if len(pages) != 116 or len({row.get("route") for row in pages}) != 116:
    fail("page index must contain 116 unique routes")
keys = visual.get("keys", [])
if len(keys) != 16 or len({row.get("id") for row in keys}) != 16:
    fail("visual keys must contain 16 unique IDs")
if registry.get("format") != "forma-ui-component-registry.v1":
    fail("unexpected component registry format")
if page_index.get("baseline") != "V34":
    fail("page index baseline is not V34")
if not str(visual.get("baseline", "")).startswith("V34"):
    fail("visual keys baseline is not V34")

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
print(f"- original package: {baseline['file_count']} byte-identical files")
print("- registry: 114 mappings")
print("- page index: 116 unique routes")
print("- visual keys: 16 unique IDs")
print("- issue templates: 5 complete")
print("- public safety: no disallowed secrets, URLs, emails or PNG metadata")
