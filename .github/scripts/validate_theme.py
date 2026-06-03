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
  - the UI chrome the user reads — muted/placeholder text, line numbers, muted
    icons — clears its floor against the panel/editor surface (text AA 4.5:1,
    icons the 3:1 of WCAG 1.4.11);
  - the eight base ANSI terminal colors clear AA against the terminal canvas;
  - the accents stay at least 40 degrees apart in hue;
  - members/properties (periwinkle) stay distinct from functions (sapphire),
    which share their hue by design, by a perceptual CIELAB lightness gap that
    also survives a simulated red-green color-vision deficiency.
  - the collaborator player colors are present and complete (Zed cycles through
    eight) and each cursor/block marker stays visible (the 3:1 of WCAG 1.4.11)
    on the editor canvas; every meaningful token also stays legible over every
    player's selection, not just the host's. Player colors may sit outside the
    accent set by design (a lighter amethyst and a warm amber fill the last two
    slots), so this checks visibility, not palette membership.

  Warnings (non-fatal)
  - any terminal ANSI color that collapses to the terminal background (so text
    in that color would be invisible) is reported but does not fail the build —
    a light theme's "bright_white" doing the same is a readability trade-off
    worth surfacing. Deliberate, conventional collisions (a dark theme's "black"
    being its own background) are allowlisted in INTENTIONAL_BG_COLLISIONS so
    only an *accidental* new collision surfaces.
  - any ANSI bright_/dim_ variant whose lightness runs the wrong way (a bright
    that is darker than its base, or a dim that is lighter) is flagged as a
    likely swap.
  - string and number share a tonal register, so a lightness-only check would call
    them "converged" under red-green color-vision deficiency. But they are different
    hues, and dichromacy preserves the blue-yellow axis, so they stay far apart in
    full color (~ΔE 40). We report (non-fatal) only a genuine collapse — a small
    CIELAB ΔE on the CVD-simulated pair — not a mere lightness coincidence; literals
    also lean on non-color cues (quotes, syntax), not hue.

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

# Members/properties (periwinkle) share a hue family with functions (sapphire)
# by design, so the 40-degree accent rule can't keep them apart. They separate by
# *lightness* instead — but a raw WCAG luminance ratio is a poor, easily-gamed
# proxy (it once sat at 1.30, fixed just under the 1.39 the palette happened to
# hit). We require a perceptual CIELAB lightness gap (ΔL*) with real margin, AND
# that the gap survives a simulated red-green color-vision deficiency — two blues
# that separate only by lightness are exactly where a dichromat is most at risk.
# The palette targets ΔL* ~12+ on both axes; the floors sit well below that so
# they catch a regression (the old near-isoluminant pairing was ΔL* < 4) without
# being reverse-engineered from the current value.
MIN_STRUCTURE_DELTA_L = 10.0       # ΔL* in CIELAB, normal vision
MIN_STRUCTURE_DELTA_L_CVD = 8.0    # ΔL* after simulating deuteranopia / protanopia

# Viénot 1999 dichromat simulation matrices, applied to *linear* sRGB.
CVD_MATRICES = {
    "deuteranopia": (
        (0.367, 0.861, -0.228),
        (0.280, 0.673, 0.047),
        (-0.012, 0.043, 0.969),
    ),
    "protanopia": (
        (0.152, 1.053, -0.205),
        (0.115, 0.786, 0.099),
        (-0.004, -0.048, 1.052),
    ),
}

# Syntax tokens that are deliberately low-contrast (suggestion previews) and so
# are excluded from the AA checks. Keep this list small and explicit.
DIM_TOKENS = {"predictive"}

# UI chrome that the user actually reads, with the background it sits on and the
# floor it must clear. Text needs AA (4.5:1); icons are graphical objects and
# need the 3:1 of WCAG 1.4.11. Deliberately dim tokens (disabled text/icons,
# predictive ghost text) are intentionally excluded, like DIM_TOKENS above.
UI_CONTRAST_CHECKS = (
    ("text.muted", "surface.background", AA_NORMAL),
    ("text.placeholder", "surface.background", AA_NORMAL),
    ("hint", "editor.background", AA_NORMAL),
    ("editor.line_number", "editor.background", AA_NORMAL),
    ("editor.hover_line_number", "editor.background", AA_NORMAL),
    ("icon.muted", "surface.background", AA_LARGE),
    ("icon.placeholder", "surface.background", AA_LARGE),
)

# The eight ANSI color slots, each of which also has a bright_ and dim_ variant.
ANSI_BASES = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")

# (theme name, terminal key) pairs whose collapse into the terminal background is
# a deliberate, conventional choice — a dark theme's ANSI "black" *is* its
# background. Listing them explicitly means a new, *accidental* collision still
# surfaces instead of hiding in expected noise.
INTENTIONAL_BG_COLLISIONS = {
    ("Geode Dark", "terminal.ansi.black"),
}


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


def _lab_lightness(hex_color):
    """CIELAB L* (perceptual lightness, 0-100) of an opaque sRGB color (D65)."""
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b, _ = _channels(hex_color)
    y = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    return 116 * y ** (1 / 3) - 16 if y > 0.008856 else 903.3 * y


def _lab(hex_color):
    """CIELAB (L*, a*, b*) of an opaque sRGB color (D65 white point)."""
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b, _ = _channels(hex_color)
    R, G, B = lin(r), lin(g), lin(b)
    x = (0.4124 * R + 0.3576 * G + 0.1805 * B) / 0.95047
    y = 0.2126 * R + 0.7152 * G + 0.0722 * B
    z = (0.0193 * R + 0.1192 * G + 0.9505 * B) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def _delta_e(c1, c2):
    """CIE76 color difference (Euclidean distance in CIELAB)."""
    return sum((p - q) ** 2 for p, q in zip(_lab(c1), _lab(c2))) ** 0.5


def _simulate_cvd(hex_color, matrix):
    """Project an sRGB color through a dichromat matrix (in linear sRGB) -> #RRGGBB."""
    def to_lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    def to_srgb(c):
        c = max(0.0, min(1.0, c))
        return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

    r, g, b, _ = _channels(hex_color)
    lr, lg, lb = to_lin(r), to_lin(g), to_lin(b)
    out = (to_srgb(row[0] * lr + row[1] * lg + row[2] * lb) for row in matrix)
    return "#%02x%02x%02x" % tuple(round(c * 255) for c in out)


def hue_degrees(hex_color):
    r, g, b, _ = _channels(hex_color)
    return colorsys.rgb_to_hls(r / 255, g / 255, b / 255)[0] * 360


def _hue_gap(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def check_quality(name, style, errors):
    """Enforce the contrast and hue promises for one theme variant.

    Missing keys are reported as clear errors rather than crashing; whatever
    surfaces do resolve are still checked.
    """
    bg = style.get("editor.background")
    if not bg:
        errors.append(f"{name}: missing 'editor.background'; skipping contrast checks")
        return

    # Backgrounds tokens may sit on, with the floor each must clear.
    surfaces = [("editor background", bg, AA_NORMAL)]

    def add_surface(label, key, floor):
        val = style.get(key)
        if val is None:
            errors.append(f"{name}: missing {key!r}; cannot check contrast on {label}")
            return
        surfaces.append((label, composite(val, bg), floor))

    add_surface("active line", "editor.active_line.background", AA_NORMAL)
    add_surface("search match", "search.match_background", AA_LARGE)
    add_surface("active search match", "search.active_match_background", AA_LARGE)
    # Overlay backgrounds that also sit on top of meaningful text.
    add_surface("selected element", "element.selected", AA_LARGE)
    add_surface("read highlight", "editor.document_highlight.read_background", AA_LARGE)
    add_surface("write highlight", "editor.document_highlight.write_background", AA_LARGE)

    # Every player's selection sits on top of meaningful code: the host's covers
    # what you select, a collaborator's covers what they select. Both must keep
    # the code under them legible, so each is added as a surface (AA-large 3:1),
    # not just players[0].
    players = style.get("players") or []
    if not (players and isinstance(players[0], dict) and players[0].get("selection")):
        errors.append(f"{name}: missing players[0].selection; cannot check contrast on selection")
    for i, p in enumerate(players):
        if isinstance(p, dict) and p.get("selection"):
            label = "selection" if i == 0 else f"selection (player {i})"
            surfaces.append((label, composite(p["selection"], bg), AA_LARGE))

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


def check_structure_separation(name, style, errors):
    """Require members/properties to stay distinct from functions by lightness.

    Periwinkle (``variable.member``) deliberately shares sapphire's (``function``)
    hue so member chains read as the same data family, which means the accent
    hue-separation rule can't tell them apart. Their distinction must come from
    lightness instead — but measured perceptually (CIELAB ΔL*), not as a raw WCAG
    luminance ratio, and the gap must also survive a simulated red-green
    color-vision deficiency, where two blues are most at risk of collapsing into
    one flat blue. Missing keys are skipped.
    """
    syntax = style.get("syntax", {})
    member = syntax.get("variable.member", {}).get("color")
    function = syntax.get("function", {}).get("color")
    if not (member and function and HEX.match(member) and HEX.match(function)):
        return

    delta_l = abs(_lab_lightness(member) - _lab_lightness(function))
    if delta_l < MIN_STRUCTURE_DELTA_L:
        errors.append(
            f"{name}: members ({member}) and functions ({function}) are only "
            f"ΔL*={delta_l:.1f} apart (needs >= {MIN_STRUCTURE_DELTA_L}) — they "
            f"share a hue by design, so they must separate by lightness"
        )

    for kind, matrix in CVD_MATRICES.items():
        dm, df = _simulate_cvd(member, matrix), _simulate_cvd(function, matrix)
        cvd_delta = abs(_lab_lightness(dm) - _lab_lightness(df))
        if cvd_delta < MIN_STRUCTURE_DELTA_L_CVD:
            errors.append(
                f"{name}: members ({member}) and functions ({function}) collapse to "
                f"ΔL*={cvd_delta:.1f} under simulated {kind} (needs >= "
                f"{MIN_STRUCTURE_DELTA_L_CVD}) — the two blues must stay legibly "
                f"distinct under red-green color-vision deficiency"
            )


# Zed cycles through eight collaborator player colors, so a theme must define
# exactly eight. Each is a solid marker on the canvas (a caret and a cursor
# block), so cursor and background are graphical objects that must clear the 3:1
# of WCAG 1.4.11 against the editor background to stay visible. Player colors are
# deliberately allowed outside the accent set (a lighter amethyst and a warm
# amber fill the last two slots), so this is a visibility check, not a
# palette-membership one; selection legibility is covered in check_quality.
PLAYER_COUNT = 8


def check_players(name, style, errors):
    """Require the collaborator player colors to be complete and visible.

    check_quality already treats each player's *selection* as a surface code
    must stay legible over. This covers the other half: the right *number* of
    players, and that each solid marker (cursor and its block background) stays
    visible against the editor canvas. Missing keys are skipped, not crashed on.
    """
    players = style.get("players") or []
    if len(players) != PLAYER_COUNT:
        errors.append(
            f"{name}: defines {len(players)} player color(s); Zed cycles through "
            f"{PLAYER_COUNT}, so the theme must define exactly {PLAYER_COUNT}"
        )

    bg = style.get("editor.background")
    if not bg:
        return
    for i, p in enumerate(players):
        if not isinstance(p, dict):
            continue
        for slot in ("cursor", "background"):
            val = p.get(slot)
            if not (val and HEX.match(val)):
                continue
            ratio = contrast_ratio(composite(val, bg), bg)
            if ratio < AA_LARGE:
                errors.append(
                    f"{name}: players[{i}].{slot} ({val}) is {ratio:.2f}:1 on the "
                    f"editor background (needs >= {AA_LARGE}:1 — a collaborator "
                    f"marker must stay visible on the canvas)"
                )


LITERAL_CVD_PAIRS = (("string", "number"),)
# string (emerald) and number (aquamarine) share a tonal register, so they coincide
# in *lightness* — a ΔL*-only check would call them "converged" under red-green CVD.
# But they are different hues, and red-green dichromacy preserves the blue-yellow
# axis, so the pair normally stays far apart in full color there (~ΔE 40: emerald
# leans yellow-green, aquamarine leans blue). Lightness is the wrong axis for a
# cross-hue pair, so we measure the full CIELAB ΔE on the CVD-simulated colors and
# warn only on a genuine collapse. (Contrast check_structure_separation, where
# members/functions share *one* hue, so ΔL* there is the only available axis — these
# two checks stay distinct on purpose.)
LITERAL_CVD_DELTA_E = 15.0


def check_literal_separation(name, style, warnings):
    """Warn only when two same-tonal-level value tokens truly collapse under CVD.

    ``string`` (emerald) and ``number`` (aquamarine) coincide in lightness but differ
    in hue; red-green color-vision deficiency keeps the blue-yellow axis, so they stay
    distinct in full color even when their ΔL* is ~0. We therefore measure the CIELAB
    ΔE between the CVD-simulated colors and surface a non-fatal warning only if it
    falls below LITERAL_CVD_DELTA_E — an actual perceptual collapse, not a lightness
    coincidence. Literals also lean on non-color cues (a string's quotes, the
    surrounding syntax), not hue.
    """
    syntax = style.get("syntax", {})
    for a, b in LITERAL_CVD_PAIRS:
        ca = syntax.get(a, {}).get("color")
        cb = syntax.get(b, {}).get("color")
        if not (ca and cb and HEX.match(ca) and HEX.match(cb)):
            continue
        for kind, matrix in CVD_MATRICES.items():
            de = _delta_e(_simulate_cvd(ca, matrix), _simulate_cvd(cb, matrix))
            if de < LITERAL_CVD_DELTA_E:
                warnings.append(
                    f"{name}: {a} ({ca}) and {b} ({cb}) collapse to ΔE={de:.1f} "
                    f"under simulated {kind} — they coincide in color, not just "
                    f"lightness; literals lean on non-color cues (quotes, syntax)"
                )


def check_ui_contrast(name, style, errors):
    """Enforce legible contrast for the UI chrome the validator used to ignore.

    check_quality only covers syntax tokens over the editor; line numbers,
    placeholders and muted icons sit on the panel/editor surfaces and are just as
    important to read. Each is composited over its background and compared to the
    floor in UI_CONTRAST_CHECKS.
    """
    for key, bg_key, floor in UI_CONTRAST_CHECKS:
        fg = style.get(key)
        bg = style.get(bg_key)
        if not fg or not bg:
            continue
        ratio = contrast_ratio(composite(fg, bg), bg)
        if ratio < floor:
            errors.append(
                f"{name}: {key} ({fg}) is {ratio:.2f}:1 on {bg_key} (needs >= {floor}:1)"
            )


def check_terminal_contrast(name, style, errors):
    """Require the eight base ANSI colors to be legible on the terminal canvas.

    A base ANSI color is ordinary program output, so it must clear AA against the
    terminal background. The conventional dark-theme "black" == background case is
    allowlisted in INTENTIONAL_BG_COLLISIONS; bright_/dim_ variants are governed by
    check_terminal_ramp instead.
    """
    bg = style.get("terminal.background")
    if not bg:
        return
    for base in ANSI_BASES:
        key = f"terminal.ansi.{base}"
        val = style.get(key)
        if not (val and HEX.match(val)):
            continue
        if (name, key) in INTENTIONAL_BG_COLLISIONS:
            continue
        ratio = contrast_ratio(composite(val, bg), bg)
        if ratio < AA_NORMAL:
            errors.append(
                f"{name}: {key} ({val}) is {ratio:.2f}:1 on the terminal "
                f"background (needs >= {AA_NORMAL}:1)"
            )


def check_terminal(name, style, warnings):
    """Surface ANSI colors that vanish into the terminal background.

    This is a warning, not an error: a color equal to the terminal background
    renders invisible, which is conventional for a dark theme's "black" but a
    readability trade-off for a light theme's "bright_white". We report it so
    it is a deliberate choice, and so an *accidental* collision can't hide.
    """
    bg = style.get("terminal.background")
    if not bg:
        return
    for key, val in style.items():
        if not (key.startswith("terminal.ansi.") and isinstance(val, str)):
            continue
        if key.endswith("background"):
            continue
        if not HEX.match(val):
            continue
        if (name, key) in INTENTIONAL_BG_COLLISIONS:
            continue
        if composite(val, bg) == composite(bg, bg):
            warnings.append(
                f"{name}: {key} ({val}) is identical to the terminal background "
                f"{bg} — text in this color would be invisible"
            )


def check_terminal_ramp(name, style, warnings):
    """Surface ANSI variants whose lightness runs the wrong way.

    A swapped ``bright_*``/``dim_*`` (bright darker than its base, or dim lighter)
    reads as a mistake, so each is reported as a non-fatal warning. The ``black``
    slot is exempt from the dim rule: in a dark theme it doubles as the terminal
    background, so its dim variant sitting marginally above the base is normal.
    """
    for base in ANSI_BASES:
        b = style.get(f"terminal.ansi.{base}")
        if not (b and HEX.match(b)):
            continue
        lb = _relative_luminance(b)
        bright = style.get(f"terminal.ansi.bright_{base}")
        if bright and HEX.match(bright) and _relative_luminance(bright) < lb:
            warnings.append(
                f"{name}: terminal.ansi.bright_{base} ({bright}) is darker than "
                f"terminal.ansi.{base} ({b}) — the bright variant should be lighter"
            )
        dim = style.get(f"terminal.ansi.dim_{base}")
        if base != "black" and dim and HEX.match(dim) and _relative_luminance(dim) > lb:
            warnings.append(
                f"{name}: terminal.ansi.dim_{base} ({dim}) is lighter than "
                f"terminal.ansi.{base} ({b}) — the dim variant should be darker"
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
    warnings = []

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
        check_structure_separation(name, t["style"], errors)
        check_players(name, t["style"], errors)
        check_ui_contrast(name, t["style"], errors)
        check_terminal_contrast(name, t["style"], errors)
        check_terminal(name, t["style"], warnings)
        check_terminal_ramp(name, t["style"], warnings)
        check_literal_separation(name, t["style"], warnings)

    if warnings:
        print(f"WARN: {len(warnings)} note(s) in {path}:", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)

    if errors:
        print(f"FAIL: {len(errors)} problem(s) in {path}:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {path} valid — {len(themes)} variant(s), all colors well-formed,")
    print("    AA contrast (syntax, UI chrome and base terminal colors), visible")
    print("    player markers and >= 40 deg accent separation hold in every variant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
