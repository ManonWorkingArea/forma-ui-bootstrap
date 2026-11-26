# Development and review lifecycle

## Branch contract

| Branch | Purpose | Merge authority |
| --- | --- | --- |
| `main` | Approved release baseline | Owner approval required |
| `dev` | Development and continuous Owner review | Reviewed PR |
| `fix/*` | Evidence-backed bug fix | Merge to `dev` after review |
| `feature/*` | Feature or approved design improvement | Merge to `dev` after review |

GitHub Pages deploys automatically after a push to `dev`. A release is a separate Owner-authorized action and must be tagged from the approved baseline.

## Review sequence

1. Owner tests the current Preview.
2. Owner files a structured issue or provides an Element Reference.
3. Lead Agent verifies the issue, captures the baseline and defines acceptance criteria.
4. Developer Agent changes only the approved scope on the relevant branch.
5. UI, responsive behavior and regression checks run.
6. Before/after screenshots and inventories are attached to the PR.
7. Design references are updated only where the accepted change affects them.
8. The change is reviewed and merged to `dev`.
9. Pages updates automatically and Owner reviews the live result.
10. Owner explicitly authorizes a release.

## Browser evidence

Static validation runs the CLI and registry checks. Browser evidence runs `scripts/browser_smoke.py` for routes, layouts, labels and copy/export, then `scripts/touch_interaction_smoke.py` for shared pointer/touch behavior. Chromium uses native CDP touch; WebKit and Firefox use the documented pointer fallback. Native touch is claimed only for the browser that emitted it. Physical-device status remains **Pending Owner Review** and is not implied by CI.

## Evidence standard

Before and after evidence must identify the mockup version, route, component, reference ID, Visual Key, viewport and app revision. Use clean screenshots for visual review and debug/inventory captures for references. Missing evidence is an unresolved item, not a PASS.

## Versions and releases

Use Semantic Versioning after `v1.0.0-rc.1`. A stable release is never inferred from a passing build. Release notes must state the exact baseline, commit, asset checksums, validation status and any unresolved limitations.
