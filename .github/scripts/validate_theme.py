#!/usr/bin/env python3
"""Validator for the Geode Zed theme.

With no third-party dependencies, this enforces both structural integrity and
the accessibility/coherence promises Geode makes in its README:

  Structure
  - the file is valid JSON;
  - the expected top-level keys are present;
  - both the dark and light variants exist;
  - every color value is a well-formed #RRGGBB or #RRGGBBAA hex string.

  Quality (the claims that used to be checked by hand)
  - every *meaningful* syntax token clears WCAG AA (4.5:1) against the editor
    background AND against the composited active-line background;
  - meaningful tokens stay above the AA-large 3:1 floor over the selection and
    over search-match highlights;
  - the accents stay at least 40 degrees apart in hue.

The predictive/ghost-text token is intentionally dim and is excluded from the
contrast checks (it is not a "meaningful" token).

Run: python3 .github/scripts/validate_theme.py themes/geode.json
"""
import colorsys
import json
import re
import sys

HEX = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")

# WCAG AA thresholds and the documented palette rule.
AA_NORMAL = 4.5
AA_LARGE = 3.0
MIN_HUE_SEPARATION = 40.0

# Syntax tokens that are deliberately low-contrast (suggestion previews) and so
# are excluded from the AA checks. Keep this list small and explicit.
DIM_TOKENS = {"predictive"}


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


def _channels(hex_color):
    """Return (r, g, b, a) as 0-255 ints; alpha defaults to 255."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    a = int(h[6:8], 16) if len(h) >= 8 else 255
    return r, g, b, a


def _relative_luminance(hex_color):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b, _ = _channels(hex_color)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast_ratio(fg, bg):
    l1, l2 = _relative_luminance(fg), _relative_luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def composite(fg, bg):
    """Composite a possibly-translucent fg over an opaque bg -> opaque #RRGGBB."""
    fr, fg_, fb, fa = _channels(fg)
    br, bg_, bb, _ = _channels(bg)
    a = fa / 255
    out = (
        round(fr * a + br * (1 - a)),
        round(fg_ * a + bg_ * (1 - a)),
        round(fb * a + bb * (1 - a)),
    )
    return "#%02x%02x%02x" % out


def hue_degrees(hex_color):
    r, g, b, _ = _channels(hex_color)
    return colorsys.rgb_to_hls(r / 255, g / 255, b / 255)[0] * 360


def _hue_gap(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def check_quality(name, style, errors):
    """Enforce the contrast and hue promises for one theme variant."""
    bg = style["editor.background"]
    active_line = composite(style["editor.active_line.background"], bg)

    # Backgrounds tokens may sit on, with the floor each must clear.
    selection = composite(style["players"][0]["selection"], bg)
    search = composite(style["search.match_background"], bg)
    active_search = composite(style["search.active_match_background"], bg)
    surfaces = [
        ("editor background", bg, AA_NORMAL),
        ("active line", active_line, AA_NORMAL),
        ("selection", selection, AA_LARGE),
        ("search match", search, AA_LARGE),
        ("active search match", active_search, AA_LARGE),
    ]

    for token, spec in style.get("syntax", {}).items():
        if token in DIM_TOKENS:
            continue
        color = spec.get("color")
        if not color:
            continue
        for surface_name, surface, floor in surfaces:
            ratio = contrast_ratio(color, surface)
            if ratio < floor:
                errors.append(
                    f"{name}: syntax {token!r} ({color}) is {ratio:.2f}:1 on "
                    f"{surface_name} (needs >= {floor}:1)"
                )

    # Accents must stay a recognizable family: >= 40 degrees apart in hue.
    accents = style.get("accents", [])
    hues = [(i, hue_degrees(c)) for i, c in enumerate(accents)]
    for x in range(len(hues)):
        for y in range(x + 1, len(hues)):
            gap = _hue_gap(hues[x][1], hues[y][1])
            if gap < MIN_HUE_SEPARATION:
                errors.append(
                    f"{name}: accents[{hues[x][0]}] and accents[{hues[y][0]}] "
                    f"are only {gap:.1f} deg apart (needs >= {MIN_HUE_SEPARATION})"
                )


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
        check_quality(name, t["style"], errors)

    if errors:
        print(f"FAIL: {len(errors)} problem(s) in {path}:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {path} valid — {len(themes)} variant(s), all colors well-formed,")
    print("    AA contrast and >= 40 deg accent separation hold in every variant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
