<div align="center">

# Geode

**A gem-toned theme for [Zed](https://zed.dev).**
Color only where it carries meaning — dark and light, cut from the same stone.

[![License: MIT](https://img.shields.io/badge/license-MIT-196b66?style=flat-square)](LICENSE)

</div>

<img src="assets/preview.svg" width="100%" alt="Geode for Zed — light and dark windows" />

<div align="center"><sub>Geode Light (back) · Geode (front)</sub></div>

## Why Geode

Most dark themes color everything. Geode does the opposite: color goes only on the tokens worth finding — keywords, types, functions, strings and values. Variables and parameters stay neutral, and properties take periwinkle, so the shape of your data shows without competing with the gems. Light and dark share the same hues, so the two cuts feel like one theme.

- **Dark and light, one theme.** Both share the same palette — switch any time without relearning your colors.
- **Easy on the eyes.** High contrast and color‑blind‑friendly in both, so code stays clear day or night.
- **Color with meaning.** Only the parts worth finding get color, so your eye lands on the logic, not a rainbow.
- **Styled everywhere.** Editor, terminal, git changes and diagnostics all match — nothing left unstyled.

## Palette

<img src="assets/palette.svg" width="100%" alt="Geode palette — six gems, periwinkle and neutrals, in dark and light" />

The light cut keeps the same hues as the dark one, deepened just enough for a pale background.

## Install

> Geode isn't in the Zed extension registry **yet** — until it's published, use the manual install below.

**Manual** (works today)

1. Copy `themes/geode.json` into your Zed themes folder — `~/.config/zed/themes/`
   on macOS and Linux, or `%APPDATA%\Zed\themes\` on Windows.
2. Run `theme selector: toggle` and pick **Geode** or **Geode Light**.

**From the Zed registry** _(once published)_

1. Open the command palette — <kbd>Cmd</kbd>/<kbd>Ctrl</kbd> <kbd>Shift</kbd> <kbd>P</kbd> — and run `zed: extensions`.
2. Search for **Geode** and install.
3. Run `theme selector: toggle` and pick **Geode** or **Geode Light**.

## Development

Geode is a pure theme — no Rust, no build step. The whole thing lives in one file, `themes/geode.json`, written against Zed's theme schema `v0.2.0`.

1. Run `zed: install dev extension` and point it at this folder.
2. Edit the JSON, then `zed: reload extensions` to see changes live.

> Close `geode.json` in Zed before editing it from another tool — an open editor buffer will overwrite your changes when it saves.

## Contributing

Issues and pull requests are welcome. [`CONTRIBUTING.md`](./CONTRIBUTING.md) covers local setup and the rules that keep the palette coherent. Changes that affect how colors look should include a before/after note.

## License

[MIT](./LICENSE) © Almela
