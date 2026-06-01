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

## Validate before you push

The same checks CI runs are plain Python with no dependencies, so run them
locally before opening a pull request:

```sh
python3 .github/scripts/validate_theme.py themes/geode.json
python3 .github/scripts/check_version_sync.py
python3 .github/scripts/check_conventional_commits.py   # checks origin/main..HEAD
```

The first enforces structure, well-formed hex, WCAG AA contrast and the ~40°
accent separation (and prints non-fatal warnings, e.g. for ANSI colors that sit
on the terminal background). The second guards that any released `version` in
`extension.toml` has a matching section in `CHANGELOG.md`. The third checks that
your commit subjects follow [Conventional Commits](https://www.conventionalcommits.org).

One more check runs in CI — it validates the theme against Zed's theme JSON
Schema. The schema is **vendored** at `.github/schemas/zed-theme-v0.2.0.json`, so
the check is offline and deterministic; it only needs the `jsonschema` package
(and skips cleanly without it):

```sh
python3 -m pip install jsonschema
python3 .github/scripts/check_schema.py themes/geode.json
```

Refresh the vendored schema from upstream when zed.dev is reachable (its CDN
otherwise rejects automated fetches):

```sh
curl -fsSL https://zed.dev/schema/themes/v0.2.0.json \
  -o .github/schemas/zed-theme-v0.2.0.json
```

## Design principles

Please keep changes consistent with the ideas that make Geode coherent:

- **Amethyst is the hero accent.** Keep it the most prominent color and the one
  used across interactive UI (selection, focus, active line).
- **Structure stays neutral.** Variables, parameters and properties use the
  foreground color; reserve gems for keywords, types, functions, strings and
  literals.
- **One color, one meaning.** Ruby is for errors and removed diff lines only.
- **Keep the gems a family.** Accents share a tonal register and a minimum hue
  separation of ~40°. Both variants share the same hues. Note the amethyst↔sapphire
  pair already sits right at that 40° floor, so retune hues carefully — the
  validator will reject anything that closes the gap further.
- **Respect contrast.** Every meaningful token must meet WCAG AA against its
  background in both the dark and light variants. The one exception is
  predictive (ghost) text: it is intentionally dim to read as a suggestion, so
  don't push it up to AA — the CI validator skips it for that reason.

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
