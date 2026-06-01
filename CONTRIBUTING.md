# Contributing to Geode

Thanks for your interest in improving Geode! This is a theme-only Zed extension,
so contributing is mostly about color and contrast.

## Local setup

1. Install [Zed](https://zed.dev).
2. Clone this repository.
3. In Zed, run `zed: install dev extension` and select the repository folder.
4. Edit `themes/geode.json`, then run `zed: reload extensions` to preview.

> Close `themes/geode.json` in Zed before editing it elsewhere — an open editor
> buffer can overwrite external changes on save.

## Design principles

Please keep changes consistent with the ideas that make Geode coherent:

- **Amethyst is the hero accent.** Keep it the most prominent color and the one
  used across interactive UI (selection, focus, active line).
- **Structure stays neutral.** Variables, parameters and properties use the
  foreground color; reserve gems for keywords, types, functions, strings and
  literals.
- **One color, one meaning.** Ruby is for errors and removed diff lines only.
- **Keep the gems a family.** Accents share a tonal register and a minimum hue
  separation of ~40°. Both variants share the same hues.
- **Respect contrast.** Every meaningful token must meet WCAG AA against its
  background in both the dark and light variants.

> **Collaboration cursors are the one exception to the six-gem set.** Zed needs
> eight distinct `players` colors, so the six gems are extended with two extra
> tints — a lighter amethyst and a warm coral/amber — used only for collaborator
> cursors and selections. They never carry syntax or UI meaning, so they stay
> outside the semantic palette.

## Submitting changes

- Use clear, [Conventional Commit](https://www.conventionalcommits.org) messages
  (e.g. `feat(light): deepen citrine for better contrast`).
- Update `CHANGELOG.md` under `[Unreleased]`.
- Bump the `version` in `extension.toml` for releases (Semantic Versioning).
- If a change affects how colors look, include before/after notes or a snippet
  in the pull request description.
