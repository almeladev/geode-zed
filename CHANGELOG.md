# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- The README preview (`assets/preview.svg`) redraws the agent panel's message
  composer to match Zed's UI — a paper-plane send control, the expand affordance,
  a reticle and text-plus-chevron model selectors. Artwork only; the theme is
  unchanged.

## [2.0.0] - 2026-06-02

### Changed

- **BREAKING — naming only, the colors are unchanged.** The dark variant is renamed
  from **Geode** to **Geode Dark**, so the two cuts read as an explicit pair in Zed's
  theme picker — matching the editor's own built-ins (`One Dark` / `One Light`,
  `Gruvbox Dark` / `Gruvbox Light`) and Catppuccin. The extension is still **Geode** in
  the registry, and **Geode Light** is unchanged.
- If your settings pinned `"theme": "Geode"`, switch it to `"theme": "Geode Dark"` (or
  pick **Geode Dark** from `theme selector: toggle`).

## [1.1.4] - 2026-06-02

### Changed

- **The README's design principles drop the color-science jargon.** "The gems are a
  set" and "Readable everywhere" no longer cite the 40°-hue separation or the
  WCAG AA / AA-large ratios; the user-facing pitch stays in plain language, while the
  exact figures remain in `CONTRIBUTING.md` and the reader-facing summary in the
  README's Accessibility section.

## [1.1.3] - 2026-06-02

### Changed

- **The README "Accessibility" section is rewritten in plain, user-facing
  language.** It now says what a reader gets — comfortable contrast in both the light
  and dark cuts, and a palette that never leans on red-versus-green alone — instead of
  the contrast ratios, CIELAB ΔE and color-vision-deficiency simulation, which stay
  documented in `CONTRIBUTING.md`.

## [1.1.2] - 2026-06-02

### Changed

- **The string↔number color-vision-deficiency check now measures full color, not
  just lightness.** `string` (emerald) and `number` (aquamarine) sit at the same
  tonal level, so the previous ΔL\*-only check reported them as "converging" under
  simulated deuteranopia/protanopia — but they are different hues, and red-green CVD
  preserves the blue-yellow axis, where the pair stays ~ΔE 40 apart (clearly distinct
  for a dichromat). `validate_theme.py` now computes the CIELAB ΔE on the
  CVD-simulated colors and warns only on a genuine collapse, so the lightness-only
  warning no longer fires. `CONTRIBUTING.md` is corrected to match. The
  member/function guard is unchanged — those share one hue, so lightness (ΔL\*) is
  the right axis there.

### Added

- A **README "Accessibility"** section that surfaces the WCAG AA and
  color-vision-deficiency testing (previously documented only in `CONTRIBUTING.md`)
  and states the literal-token nuance honestly: `string` and `number` coincide in
  brightness but stay distinct in color for red-green CVD, and lean on quotes and
  surrounding syntax besides.

## [1.1.1] - 2026-06-02

### Changed

- **Docs brought in line with the 1.1.0 palette.** `CONTRIBUTING.md` now documents
  parameters' own recessive tint, the current periwinkle (`#c0c2e8` / `#343a82`)
  and the real member/function guard (`MIN_STRUCTURE_DELTA_L` plus the
  color-vision-deficiency floor), and records that amber now also carries
  `string.regex`, not just collaborator cursors.

### Added

- The theme validator now reports the string↔number ΔL\* under simulated
  deuteranopia/protanopia as a **non-fatal warning**: six same-tonal-level hues
  can't all stay distinct under dichromacy, so literals lean on non-color cues
  (quotes, syntax), and the warning keeps that trade-off visible rather than silent.

### Fixed

- The changelog's compare links: they pointed at `v`-prefixed tags, but the repo's
  tags are unprefixed, so the links 404'd. They now use the real tag names, and the
  previously-absent `[1.1.0]` link is restored. Also the non-breaking hyphens in
  `README.md`.

## [1.1.0] - 2026-06-02

### Changed

- **Parameters get their own recessive tint.** `variable.parameter` and
  `parameter` used to share the foreground color, so a function's inputs were
  indistinguishable from any ordinary variable. They now take a calm
  lavender-gray — `#a9a2bd` (dark) and `#5b5470` (light) — a touch quieter than
  plain text and clearly apart from the periwinkle of members. The three read as
  a gentle hierarchy in both cuts (foreground → member → parameter, each step
  receding a little further toward the canvas) without spending a gem on them.
  Both tones clear WCAG AA over canvas and active line (≥ 5.7:1), sit ΔL\* ~19–24
  from the foreground and ~10–11 from members, and keep the same ~261° hue across
  cuts. Variables themselves stay neutral.
- **Regular expressions take an amber of their own.** `string.regex` shared the
  aquamarine of `number`/`boolean`/`constant`, so a regex and a nearby number
  looked identical even though a pattern is a language within the language. It
  now uses the warm amber that already lived in the palette as a collaboration
  cursor — `#efa880` (dark) and, darkened to clear AA on the pale canvas,
  `#9c5018` (light): the one warm tone, sitting ~150° off aquamarine and well
  clear of citrine types. `string.escape` and `string.special` stay aquamarine —
  only the regex itself peels away. `palette.svg` is updated to show both new
  tones.

## [1.0.2] - 2026-06-02

### Changed

- **Periwinkle members separate from sapphire functions more, and more
  robustly.** 1.0.1 lifted the member↔function gap to a 1.40:1 luminance ratio,
  but that ratio is a weak proxy: perceptually the two blues sat only ~10 ΔL\*
  apart (dark) and ~9.5 (light), and under simulated red-green color-vision
  deficiency the light cut dropped to ~8.9 — close enough that a `foo.bar()`
  chain still read as fairly flat. Periwinkle (`property`, `field`,
  `variable.member`) is retuned to `#c0c2e8` (dark) and `#343a82` (light): the
  same calm lavender hue (~236°), but a lighter, lower-chroma dark cut and a
  deeper light cut. That widens the perceptual gap to ΔL\* ~12.2 / ~12.6 and adds
  a second, hue-independent separation axis — members are now a notably *calmer*
  blue than vivid sapphire functions, reinforcing "a calm periwinkle, not a gem."
  Both tones still clear WCAG AA over canvas, active line, selection and search
  (≥ 9.3:1), and stay ~24–26° clear of amethyst keywords. `palette.svg` and
  `preview.svg` are updated to match.

### Added

- The member/function guard is now **perceptual and color-vision-deficiency
  aware.** `check_structure_separation` no longer trusts a raw WCAG luminance
  ratio (which once sat at `1.30`, fixed just under the value the palette
  happened to hit). It now requires a CIELAB lightness gap (`MIN_STRUCTURE_DELTA_L`,
  ΔL\* ≥ 10) that must also survive a simulated **deuteranopia and protanopia**
  (Viénot 1999, in pure Python — `MIN_STRUCTURE_DELTA_L_CVD`, ΔL\* ≥ 8). The
  floors sit well below the palette's ~12 ΔL\* so they catch a regression — the
  old near-isoluminant pairing scored ΔL\* < 6 and now fails CI — without being
  reverse-engineered from the current colors.

## [1.0.1] - 2026-06-02

### Changed

- **Periwinkle members now separate from sapphire functions by weight.** In
  1.0.0 members/properties (`#a8afe6` dark / `#444d99` light) sat only ~12° off
  sapphire functions at nearly the same luminance — a 1.19:1 contrast between
  the two, so `foo.bar()` read as one flat blue (and was indistinguishable under
  mild color-vision deficiency). Periwinkle is retuned to `#b9bdf0` (dark) and
  `#3a4090` (light): same calm lavender hue (~236°), but a lighter dark cut and a
  deeper light cut lift the member↔function contrast to ~1.40:1 while staying
  ~26° clear of amethyst keywords. Both tones still clear WCAG AA over the canvas,
  active line, selection and search (≥ 6.4:1 on every surface). The `palette.svg`
  and `preview.svg` artwork is updated to match.

### Added

- The theme validator now enforces the member/function separation it couldn't
  catch before: members and functions share a hue by design, so the accent
  hue-separation rule can't tell them apart — `check_structure_separation`
  requires a minimum luminance contrast (`MIN_STRUCTURE_SEPARATION`, 1.30:1)
  between them instead, so this exact regression fails CI rather than slipping
  through.

## [1.0.0] - 2026-06-02

### Added

- **Member & property highlighting in periwinkle.** `property`, `field` and
  `variable.member` move from neutral foreground to a calm blue-lavender —
  `#a8afe6` (dark) and `#444d99` (light) — that reads as the shape of the data.
  Locals and parameters stay foreground, so member chains and object keys
  (`user.profile.name`, JSON/CSS keys) stand out as structure while staying
  distinct from sapphire functions and citrine types. Both tones clear WCAG AA
  (8.7:1 dark, 6.9:1 light) over the canvas, active line, selection and search.
- The validator now enforces the contrast it used to ignore: UI chrome the user
  reads (`text.muted`, `text.placeholder`, `editor.line_number`,
  `editor.hover_line_number`, `hint` at AA; muted/placeholder icons at the 3:1
  graphical floor) and the eight base `terminal.ansi.*` colors against the
  terminal canvas. A regression now fails CI instead of slipping through.
- A **Periwinkle** swatch in `assets/palette.svg`.
- A **vendored** copy of Zed's theme JSON Schema at
  `.github/schemas/zed-theme-v0.2.0.json`. `check_schema.py` now validates
  against it by default, so the schema check is offline and deterministic
  instead of a permanent `SKIP` whenever `zed.dev`'s CDN rejects the fetch
  (HTTP 403). It still falls back to the remote `$schema` URL, then to `SKIP`.
- The theme validator now warns (non-fatal) when an ANSI `bright_`/`dim_`
  variant runs the wrong way — a bright that is darker than its base, or a dim
  that is lighter — which usually means the two were swapped.
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
- `check_schema.py` and an advisory CI step that validate the theme against
  Zed's published JSON Schema (the `$schema` URL in the theme). It degrades
  gracefully — skipping when the schema can't be fetched or `jsonschema` isn't
  installed — so it never produces a flaky build.
- `check_conventional_commits.py` and a `Lint commits` workflow that enforce
  [Conventional Commits](https://www.conventionalcommits.org) on the commits a
  pull request adds (the convention `CONTRIBUTING.md` already asks for).

### Changed

- The README now leads with installing Geode from the **Zed extension registry**
  (it has been published) instead of the manual copy, and gains a "What the gems
  mean" rundown mapping each accent — and the new periwinkle members — to the
  syntax it carries.
- The CI workflow pins Python (`actions/setup-python`) and now also runs when
  `extension.toml` or `CHANGELOG.md` change. It now declares least-privilege
  `permissions` and cancels superseded in-progress runs per ref.
- The terminal-invisibility warning now consults an explicit allowlist
  (`INTENTIONAL_BG_COLLISIONS`), so the dark theme's deliberate `terminal.ansi.black`
  -on-background no longer emits a permanent warning while a new, *accidental*
  collision still surfaces.
- `Geode Light`'s `terminal.ansi.bright_white` no longer equals the terminal
  background, so bright-white terminal text stays visible.

### Fixed

- **Legibility of the UI chrome**, which the validator hadn't been checking.
  `editor.line_number` (3.8:1 dark / 3.5:1 light) and `text.placeholder` (3.6 /
  3.1) were below AA and `icon.placeholder` (2.9 / 2.7) below the 3:1 floor; all
  now clear their thresholds in both variants.
- **`Geode Light` terminal "white" was nearly invisible** at 1.88:1.
  `terminal.ansi.white` is now a legible gray (`#4e495e`, 7.9:1) with
  `bright_white`/`dim_white` retuned to keep the ramp ordered and readable.
- The `preview.svg` collaboration-presence dots used a stale amber (`#d9a05a`)
  that no longer exists in the palette; they now use the actual warm player
  tints — `#efa880` in the dark window and `#bf6a25` in the light one.
- The theme validator no longer crashes with a `KeyError` on a malformed
  variant (missing `editor.background`, `players`, search keys); it reports a
  clear error and checks whatever surfaces do resolve.
- `check_version_sync.py` no longer leaks file handles (reads both files with a
  context manager).

### Removed

- The unused `.github/scripts/_gen_v1_previews.py` generator, a one-off script
  that was dead weight.

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
- A CI guard (`.github/scripts/check_asset_colors.py`) that keeps the README's
  artwork in sync with the theme: every color in `assets/palette.svg` and
  `assets/preview.svg` must trace back to a color `themes/geode.json` defines.


[unreleased]: https://github.com/almeladev/geode-zed/compare/2.0.0...HEAD
[2.0.0]: https://github.com/almeladev/geode-zed/compare/1.1.4...2.0.0
[1.1.4]: https://github.com/almeladev/geode-zed/compare/1.1.3...1.1.4
[1.1.3]: https://github.com/almeladev/geode-zed/compare/1.1.2...1.1.3
[1.1.2]: https://github.com/almeladev/geode-zed/compare/1.1.1...1.1.2
[1.1.1]: https://github.com/almeladev/geode-zed/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/almeladev/geode-zed/compare/1.0.2...1.1.0
[1.0.2]: https://github.com/almeladev/geode-zed/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/almeladev/geode-zed/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/almeladev/geode-zed/compare/0.1.0...1.0.0
[0.1.0]: https://github.com/almeladev/geode-zed/releases/tag/0.1.0
