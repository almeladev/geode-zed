# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing has been released yet. The first tagged release will move the entries
below under a versioned heading.

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
- Note in `CONTRIBUTING.md` documenting the two extra collaboration-cursor tints
  that sit outside the six-gem semantic palette.

[Unreleased]: https://github.com/almeladev/geode-zed/commits/main
