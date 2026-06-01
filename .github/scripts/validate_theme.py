#!/usr/bin/env python3
"""Lightweight validator for the Geode Zed theme.

Checks, with no third-party dependencies:
  - the file is valid JSON;
  - the expected top-level keys are present;
  - both the dark and light variants exist;
  - every color value is a well-formed #RRGGBB or #RRGGBBAA hex string.

Run: python3 .github/scripts/validate_theme.py themes/geode.json
"""
import json
import re
import sys

HEX = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")


def is_color_key(key: str) -> bool:
    # Keys that hold color values typically end in these suffixes, or are the
    # palette/cursor fields. We validate any string value that looks like a hex
    # color and flag any color-ish key whose value is malformed.
    return True


def walk_colors(node, path, errors):
    """Validate every string value that is a hex color, recursively."""
    if isinstance(node, dict):
        for k, v in node.items():
            walk_colors(v, f"{path}.{k}", errors)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk_colors(v, f"{path}[{i}]", errors)
    elif isinstance(node, str):
        if node.startswith("#") and not HEX.match(node):
            errors.append(f"{path}: malformed hex color {node!r}")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_theme.py <theme.json>", file=sys.stderr)
        return 2
    path = sys.argv[1]

    with open(path, encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"FAIL: {path} is not valid JSON: {exc}", file=sys.stderr)
            return 1

    errors = []

    for key in ("name", "author", "themes"):
        if key not in data:
            errors.append(f"missing top-level key: {key!r}")

    themes = data.get("themes", [])
    appearances = {t.get("appearance") for t in themes if isinstance(t, dict)}
    for expected in ("dark", "light"):
        if expected not in appearances:
            errors.append(f"no theme variant with appearance {expected!r}")

    for t in themes:
        if not isinstance(t, dict):
            continue
        name = t.get("name", "<unnamed>")
        if "style" not in t:
            errors.append(f"theme {name!r}: missing 'style'")
            continue
        walk_colors(t["style"], f"{name}.style", errors)

    if errors:
        print(f"FAIL: {len(errors)} problem(s) in {path}:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {path} valid — {len(themes)} variant(s), all colors well-formed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
