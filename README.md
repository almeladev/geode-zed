<div align="center">

# Geode

**💎 A gem-toned theme for [Zed](https://zed.dev).**
Color only where it carries meaning — dark and light, cut from the same stone.

[![License: MIT](https://img.shields.io/badge/license-MIT-196b66?style=flat-square)](LICENSE)

</div>

<img src="assets/preview.svg" width="100%" alt="Geode for Zed — light and dark windows" />

<div align="center"><sub>Geode Light (back) · Geode (front)</sub></div>

## Why Geode

Most dark themes color everything. Geode does the opposite: the canvas is a quiet, violet‑tinted stone, and color is spent only on the tokens worth finding — keywords, types, functions, strings and values. Variables stay neutral and parameters recede a touch further, while properties take a calm periwinkle — the shape of the data — so your eye lands where the logic is.

A few principles hold the palette together:

- **Amethyst leads.** It's the signature accent and runs through the whole UI — selection, focus, the active line — so the editor feels of one piece.
- **The gems are a set, not a scatter.** Every accent shares one tonal level and stays at least 40° apart in hue, in both variants.
- **Structure shows its shape.** Members and properties take a calm periwinkle — not a gem — so object keys and member chains read as data structure without competing with the accents.
- **One color, one meaning.** Ruby is reserved for things that went wrong — errors and removed lines — so it never cries wolf on an ordinary number.
- **Readable everywhere.** Every meaningful token clears WCAG AA (4.5:1) against the canvas in both cuts — including on the active line — and stays above the AA‑large 3:1 floor under selections and search highlights.

## Palette

<img src="assets/palette.svg" width="100%" alt="Geode palette — six gems, periwinkle and neutrals, in dark and light" />

The light cut keeps the same hues as the dark one and only darkens each gem as far as a pale background needs — yellows and teals deepen into bronze and forest rather than washing out.

**What the gems mean** — color is spent on roles, not decoration:

- **Amethyst** — keywords, and the UI's signature: selection, focus, the active line
- **Sapphire** — functions and namespaces
- **Citrine** — types, enums and attributes
- **Aquamarine** — constants, numbers and booleans
- **Emerald** — strings
- **Ruby** — errors and removed lines, and nothing else

Variables stay neutral and parameters take a quieter recessive tone of their own; properties and members take a calm periwinkle, and regular expressions a warm amber — the one warm tone, for a language within the language — so the shape of the data shows without competing with the gems.

## Install

**From the Zed registry** (recommended)

1. Open the command palette — <kbd>Cmd</kbd>/<kbd>Ctrl</kbd> <kbd>Shift</kbd> <kbd>P</kbd> — and run `zed: extensions`.
2. Search for **Geode** and install.
3. Run `theme selector: toggle` and pick **Geode** or **Geode Light**.

**Manual** (for development or pinning a version)

1. Copy `themes/geode.json` into your Zed themes folder — `~/.config/zed/themes/`
   on macOS and Linux, or `%APPDATA%\Zed\themes\` on Windows.
2. Run `theme selector: toggle` and pick **Geode** or **Geode Light**.

## Development

Geode is a pure theme — no Rust, no build step. The whole thing lives in one file, `themes/geode.json`, written against Zed's theme schema `v0.2.0`.

1. Run `zed: install dev extension` and point it at this folder.
2. Edit the JSON, then `zed: reload extensions` to see changes live.

> Close `geode.json` in Zed before editing it from another tool — an open editor buffer will overwrite your changes when it saves.

## Contributing

Issues and pull requests are welcome. [`CONTRIBUTING.md`](./CONTRIBUTING.md) covers local setup and the rules that keep the palette coherent. Changes that affect how colors look should include a before/after note.

## License

[MIT](./LICENSE) © Almela
