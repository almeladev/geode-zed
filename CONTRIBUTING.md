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
python3 .github/scripts/check_asset_colors.py
python3 .github/scripts/check_version_sync.py
python3 .github/scripts/check_conventional_commits.py   # checks origin/main..HEAD
```

The first enforces structure, well-formed hex, WCAG AA contrast and the ~40°
accent separation (and prints non-fatal warnings, e.g. for ANSI colors that sit
on the terminal background). The second keeps the README artwork honest: every
color in `assets/palette.svg` and `assets/preview.svg` must trace back to a
color the theme defines, so a token you re-tune can't silently drift out of date
in the swatches and preview. The third guards that any released `version` in
`extension.toml` has a matching section in `CHANGELOG.md`. The fourth checks that
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
- **Structure has its own color.** Variables use the foreground color; parameters
  (`variable.parameter`, `parameter`) take a quieter recessive tint of their own
  (`#a9a2bd` dark / `#5b5470` light), and members and properties (`property`,
  `field`, `variable.member`) use
  **periwinkle** (`#c0c2e8` dark / `#343a82` light) — a calm blue-lavender that
  reads as the shape of the data. It is not an accent (not in `accents`), so the
  40° rule doesn't apply, but it must clear AA and stay visibly distinct from
  both sapphire functions and citrine types. Both cuts share the same hue (~236°),
  intentionally close to sapphire — so periwinkle separates from functions by
  **weight, not hue**. The validator enforces this perceptually: a CIELAB
  lightness gap (`MIN_STRUCTURE_DELTA_L`, ΔL* >= 10) that must also survive a
  simulated red-green color-vision deficiency (`MIN_STRUCTURE_DELTA_L_CVD`,
  ΔL* >= 8) between members and functions, or a
  `foo.bar()` chain starts to read as one flat blue. Keep that gap when retuning.
  Reserve the gems for keywords, types, functions, strings and literals.
- **One color, one meaning.** Ruby is for errors and removed diff lines only.
- **Keep the gems a family.** Accents share a tonal register and a minimum hue
  separation of ~40°. Both variants share the same hues. Note the amethyst↔sapphire
  pair already sits right at that 40° floor, so retune hues carefully — the
  validator will reject anything that closes the gap further.
- **Respect contrast — all of it.** Every meaningful token must meet WCAG AA
  against its background in both variants. So must the UI chrome you read all day
  (`text.muted`, `text.placeholder`, `editor.line_number`, muted icons) and the
  eight base terminal colors — `validate_theme.py` now enforces these too, so a
  regression fails CI. The one exception is predictive (ghost) text: it is
  intentionally dim to read as a suggestion, so the validator skips it.
- **Don't lean on red↔green alone.** Color-blind readers can't separate ruby from
  emerald, so diffs and diagnostics must keep working through Zed's structural
  cues (gutter +/− markers, diagnostic icons) and the semantic `*.background`
  tints — never through hue by itself.
- **WCAG AA is contrast against the background, not between tokens.** Six
  same-tonal-level hues can't all stay distinct under color-vision deficiency:
  emerald strings and aquamarine numbers converge under simulated deuteranopia
  and protanopia. Literals lean on non-color cues instead — a string's quotes and
  the surrounding syntax — exactly as diffs and diagnostics lean on the gutter and
  icons. `validate_theme.py` reports that CVD lightness gap as a non-fatal warning
  so the trade-off stays visible.

> **Two tints sit outside the six-gem set.** Zed needs eight distinct `players`
> colors, so the gems are extended with a lighter amethyst (collaborator cursors
> only) and a warm amber. The amber does double duty — a collaborator cursor
> (`#efa880` dark / `#bf6a25` light) and, since 1.1.0, `string.regex`, the one warm
> syntax tone, darkened to clear AA on the pale canvas (`#efa880` dark / `#9c5018`
> light). Reserve amber for regex; it is the only token outside the gems.

## Submitting changes

- Use clear, [Conventional Commit](https://www.conventionalcommits.org) messages
  (e.g. `feat(light): deepen citrine for better contrast`).
- Update `CHANGELOG.md` under `[Unreleased]`.
- Bump the `version` in `extension.toml` for releases (Semantic Versioning).
- If a change affects how colors look, include before/after notes or a snippet
  in the pull request description.
