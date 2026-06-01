#!/usr/bin/env python3
"""Guard that the README's SVG assets stay in sync with the theme.

`assets/palette.svg` and `assets/preview.svg` are hand-authored, so a color the
theme changes (e.g. the periwinkle members) can silently drift out of date in
the artwork the README shows. This keeps them honest: every hex an asset uses
must be a color the theme actually defines.

  - palette.svg is a pure swatch sheet of the theme's palette, so *every* hex
    in it must exist in themes/geode.json — no allowlist.
  - preview.svg is a mockup whose chrome uses a few composited/blended surfaces
    (panel layers, mixed backgrounds) that are not literal theme tokens; those
    are allowlisted explicitly below.

assets/preview-v1.svg is intentionally a frozen snapshot of the v1.0.0 palette
(see CHANGELOG.md), so it is deliberately NOT validated here.

No third-party dependencies.

Run: python3 .github/scripts/check_asset_colors.py
"""
import re
import sys

THEME = "themes/geode.json"

# Each asset maps to the set of hexes it may use that are NOT theme colors.
# Keep allowlists minimal and documented — they are the only escape hatch.
ALLOWLISTS = {
    "assets/palette.svg": set(),
    "assets/preview.svg": {
        # Composited mockup chrome (panel layers / blended surfaces), not tokens.
        "#292434", "#2f3f36", "#3a334a", "#413a53",
        "#ded5ee", "#ebe6f7", "#eee9f8",
    },
}

HEX = re.compile(r"#[0-9a-fA-F]{6,8}")


def hexes(text):
    """All #rrggbb / #rrggbbaa literals, normalized to lowercase #rrggbb."""
    return {"#" + m.group(0)[1:7].lower() for m in HEX.finditer(text)}


def main() -> int:
    try:
        with open(THEME, encoding="utf-8") as fh:
            theme_colors = hexes(fh.read())
    except OSError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    failed = False
    for asset, allow in ALLOWLISTS.items():
        try:
            with open(asset, encoding="utf-8") as fh:
                used = hexes(fh.read())
        except OSError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1

        foreign = sorted(used - theme_colors - allow)
        if foreign:
            failed = True
            print(
                f"FAIL: {asset} uses {len(foreign)} color(s) not in {THEME} "
                f"(and not allowlisted): {', '.join(foreign)}.\n"
                f"      Align the asset with the theme, or add a deliberate "
                f"composited color to the allowlist in this script.",
                file=sys.stderr,
            )
        else:
            print(f"OK: {asset} colors all trace back to {THEME}.")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
