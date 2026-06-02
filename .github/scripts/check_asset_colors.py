#!/usr/bin/env python3
"""Guard that the README's SVG assets stay in sync with the theme.

The README's artwork must never drift from the palette, so this keeps it honest:
every hex an asset uses must be a color the theme actually defines.

  - palette.svg is a hand-authored swatch sheet of the theme's palette, so
    *every* hex in it must exist in themes/geode.json.
  - preview*.svg (the dark, light and combined mockups) are GENERATED from the
    theme by build_preview.py and paint only theme colors — translucent
    surfaces (active line, selections, focus rings) reuse the theme's own RGBA
    tokens and let SVG composite them, so they introduce no foreign colors.

No allowlist is needed today; each asset is still listed below so it is
explicitly checked. (build_preview.py --print-allowlist confirms none drift in.)

No third-party dependencies.

Run: python3 .github/scripts/check_asset_colors.py
"""
import re
import sys

THEME = "themes/geode.json"

# Each asset maps to the set of hexes it may use that are NOT theme colors.
# The previews are generated straight from the theme (build_preview.py) and use
# only theme colors, so every set is empty — the keys exist purely so each asset
# is explicitly checked. If a deliberate composited color is ever introduced,
# add it here with a comment; it is the only escape hatch.
ALLOWLISTS = {
    "assets/palette.svg": set(),
    "assets/preview.svg": set(),
    "assets/preview-dark.svg": set(),
    "assets/preview-light.svg": set(),
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
