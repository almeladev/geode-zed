# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The theme validator now warns (non-fatal) when a `terminal.ansi.*` color
  collapses to the terminal background and would render invisible — surfacing,
  for example, that `Geode Light`'s `bright_white` equals its terminal canvas.
- `check_version_sync.py` and a CI step that guard that the `version` in
  `extension.toml` always has a matching section in `CHANGELOG.md`.
- `CONTRIBUTING.md` and the PR template now document running the validators
  locally before pushing.
- The contrast checks now also cover the selected-element, read-highlight and
  write-highlight overlays, not just selection and search matches.
- An `.editorconfig` documenting the repository's whitespace conventions.

### Changed

- The CI workflow pins Python (`actions/setup-python`) and now also runs when
  `extension.toml` or `CHANGELOG.md` change. It now declares least-privilege
  `permissions` and cancels superseded in-progress runs per ref.
- `Geode Light`'s `terminal.ansi.bright_white` no longer equals the terminal
  background, so bright-white terminal text stays visible.

### Fixed

- The theme validator no longer crashes with a `KeyError` on a malformed
  variant (missing `editor.background`, `players`, search keys); it reports a
  clear error and checks whatever surfaces do resolve.
- `check_version_sync.py` no longer leaks file handles (reads both files with a
  context manager).

## [0.1.0] - 2026-06-01

### Added

- **Geode**, a gem-toned theme for Zed, with `Geode` (dark) and `Geode Light`
  (light) variants in a single theme family.
- Six-gem accent palette — five working accents, amethyst (keywords), sapphire
  (functions), citrine (types), aquamarine (literals) and emerald (strings), plus
  ruby reserved for errors and removed diff lines.
- Full editor chrome, terminal ANSI palette, collaboration cursors and
  diagnostics, all derived from the same palette.
- WCAG AA contrast for every meaningful token in both variants.
- CI workflow that validates `themes/geode.json` (valid JSON, both variants
  present, all colors well-formed `#RRGGBB`/`#RRGGBBAA`).
- CI now also enforces Geode's quality promises automatically: WCAG AA (4.5:1)
  for meaningful tokens over the editor background and the active line, the
  AA-large 3:1 floor over selection and search highlights, and the ~40° minimum
  hue separation between accents. The workflow also runs when the validator
  script itself changes.
- Note in `CONTRIBUTING.md` documenting the two extra collaboration-cursor tints
  that sit outside the six-gem semantic palette.

[Unreleased]: https://github.com/almeladev/geode-zed/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/almeladev/geode-zed/releases/tag/v0.1.0
