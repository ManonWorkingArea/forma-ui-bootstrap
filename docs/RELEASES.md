# Release packaging

Release assets are generated from the tagged repository state, never from the working tree alone.

Required assets:

- `forma-ui-bootstrap-v<version>.zip`: complete repository bootstrap.
- `forma-ui-bootstrap-v<version>-standalone.html`: byte-identical standalone mockup.
- `skill.zip`: portable agent skill with `SKILL.md`, references, scripts, agent metadata and mockup assets.
- `release-manifest.json`: version, tag commit, artifact SHA-256 values and baseline package information.

Before creating a release, verify the supplied package files against `.github/package-baseline.json`, run all CI jobs, review Actions logs, and repeat the public-safety scan. Pre-release status must remain enabled until Owner approval.
