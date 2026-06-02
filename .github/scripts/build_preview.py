#!/usr/bin/env python3
"""Generate the README preview artwork straight from the theme.

`assets/preview-dark.svg`, `assets/preview-light.svg` and the combined
`assets/preview.svg` are *generated* from `themes/geode.json`, not hand-drawn,
so the artwork can never drift out of sync with the palette: every color the
mockup paints is read out of the theme, and translucent surfaces (the active
line, selections, focus rings) reuse the theme's own RGBA tokens and let SVG do
the compositing — so the only literal hex the artwork introduces is `#000000`
for drop shadows, which the theme already carries via `#00000000`. The result
is that `check_asset_colors.py` passes with no allowlist for these assets.

The mockup is deliberately language-agnostic: "code" is drawn as colored token
bars (never real source), so no language is favored. One shared layout function,
`window_content()`, renders a full Zed window; the dark and light previews are
the same drawing with two palettes, and the combined image is two of them set
side by side at a slight tilt.

  Run:  python3 .github/scripts/build_preview.py            # writes the 3 SVGs
        python3 .github/scripts/build_preview.py --print-allowlist
            # prints, per asset, any hex it uses that is NOT a theme color
            # (expected: none — confirms the empty allowlists stay honest)

No third-party dependencies.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THEME = ROOT / "themes" / "geode.json"
ASSETS = ROOT / "assets"

# ── Geometry (a ~16:10 editor window; tune here, everything else follows) ──
W, H = 1040, 648            # window body
PAD = 32                    # canvas margin around the window (room for shadow)
RADIUS = 13

TITLE_H = 38
TAB_H = 34
CRUMB_H = 24                # breadcrumb / toolbar strip under the tabs
STATUS_H = 30
PANEL_W = 222               # left project dock
GUTTER_W = 56               # line-number gutter
MINIMAP_W = 26
LINE_H = 22

CONTENT_TOP = TITLE_H
CONTENT_BOT = H - STATUS_H
EDITOR_X = PANEL_W
EDITOR_W = W - PANEL_W
CODE_TOP = TITLE_H + TAB_H + CRUMB_H
GUTTER_NUM_X = EDITOR_X + GUTTER_W - 11      # right edge for right-aligned numbers
CODE_X = EDITOR_X + GUTTER_W + 12
MINIMAP_X = W - MINIMAP_W - 12
CODE_RIGHT = MINIMAP_X - 18

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

# ── Token roles → syntax keys (kept restrained: most tokens neutral/muted,
#    gems spent sparingly, per the theme's "color only where it carries
#    meaning" principle). ──
ROLE = {
    "kw": "keyword", "fn": "function", "ns": "namespace", "ty": "type",
    "st": "string", "nu": "number", "cn": "constant", "pr": "property",
    "pa": "parameter", "va": "variable", "op": "punctuation",
    "co": "comment", "tag": "tag", "attr": "attribute",
}

# Each line: (indent_level, [(role, width), ...]). [] is a blank line.
# Designed to read like real code rhythm — imports, a comment, a type block,
# a function with an active line, a return, an exported function — without
# being any actual language.
CODE_LINES = [
    (0, [("kw", 46), ("va", 40), ("kw", 30), ("st", 86)]),
    (0, [("kw", 40), ("va", 30), ("kw", 26), ("ns", 64)]),
    (0, []),
    (0, [("co", 318)]),
    (0, [("kw", 54), ("ty", 72), ("op", 12)]),
    (1, [("pr", 56), ("op", 8), ("ty", 46)]),
    (1, [("pr", 44), ("op", 8), ("ty", 66)]),
    (1, [("pr", 60), ("op", 8), ("cn", 34)]),
    (0, [("op", 12)]),
    (0, []),
    (0, [("co", 224)]),
    (0, [("kw", 40), ("fn", 78), ("op", 6), ("pa", 44), ("op", 8), ("ty", 50), ("op", 12)]),
    (1, [("kw", 34), ("va", 40), ("op", 10), ("nu", 42)]),          # ACTIVE line (index 12)
    (1, [("va", 50), ("op", 6), ("pr", 46), ("op", 8), ("st", 64)]),
    (1, [("kw", 40), ("va", 54), ("op", 8), ("fn", 40), ("pr", 30)]),
    (0, [("op", 12)]),
    (0, []),
    (0, [("kw", 52), ("fn", 64), ("op", 6), ("pa", 40), ("op", 10)]),
    (1, [("kw", 38), ("va", 58), ("op", 8), ("pr", 48), ("op", 6), ("cn", 24)]),
    (1, [("tag", 44), ("attr", 34), ("op", 8), ("st", 52)]),
    (0, [("op", 12)]),
    (0, []),
]
ACTIVE = 12                 # active-line row (0-based index into CODE_LINES)
SEL = (5, 2)                # (row, token index) carrying a selection band
INDENT = 22                 # px per indent level

# Left dock file tree: (depth, kind, name_width, icon_role, selected)
#   kind: "open" / "folder" / "file"; icon_role tints the file chip.
TREE = [
    (0, "open", 64, "muted", False),
    (1, "file", 58, "fn", False),
    (1, "file", 50, "ty", False),
    (1, "open", 46, "muted", False),
    (2, "file", 52, "accent", True),
    (2, "file", 44, "st", False),
    (2, "file", 60, "muted", False),
    (1, "folder", 42, "muted", False),
    (0, "open", 56, "muted", False),
    (1, "file", 50, "ty", False),
    (1, "file", 62, "fn", False),
    (0, "file", 48, "muted", False),
    (0, "file", 40, "muted", False),
]

# Editor tabs: (name_width, active, modified)
TABS = [(56, False, False), (64, True, True), (48, False, False)]


# ───────────────────────────── color helpers ─────────────────────────────
def load_style(variant):
    theme = json.loads(THEME.read_text(encoding="utf-8"))
    for t in theme["themes"]:
        if t["name"] == variant:
            return t["style"]
    raise SystemExit(f"variant not found: {variant}")


def c(style, key):
    """A flat UI color token, e.g. 'editor.background'."""
    return style[key]


def syn(style, role):
    """A syntax color by our short role code."""
    return style["syntax"][ROLE[role]]["color"]


def fill(raw, attr="fill"):
    """Paint attributes for a theme color string (#rrggbb or #rrggbbaa).

    Alpha is emitted as `<attr>-opacity` so the hex stays 6-digit and traces
    straight back to the theme; SVG composites it over whatever is behind.
    """
    h = raw[:7]
    a = raw[7:9]
    if a and a.lower() != "ff":
        return f'{attr}="{h}" {attr}-opacity="{int(a, 16) / 255:.3f}"'
    return f'{attr}="{h}"'


def stroke(raw, width=1):
    return f'{fill(raw, "stroke")} stroke-width="{width}"'


# ───────────────────────────── svg primitives ────────────────────────────
def rect(x, y, w, h, *, r=0, f=None, s=None, sw=1, extra=""):
    a = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'width="{w:.1f}"', f'height="{h:.1f}"']
    if r:
        a.append(f'rx="{r}"')
    a.append(fill(f) if f else 'fill="none"')
    if s:
        a.append(stroke(s, sw))
    if extra:
        a.append(extra)
    return f'<rect {" ".join(a)}/>'


def line(x1, y1, x2, y2, raw, width=1):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'{stroke(raw, width)}/>')


def circle(cx, cy, r, raw, s=None, sw=1):
    a = [f'cx="{cx:.1f}"', f'cy="{cy:.1f}"', f'r="{r}"', fill(raw) if raw else 'fill="none"']
    if s:
        a.append(stroke(s, sw))
    return f'<circle {" ".join(a)}/>'


def bar(x, y, w, raw, h=6, r=3):
    return rect(x, y, w, h, r=r, f=raw)


def tri(cx, cy, raw, down=False):
    """A small chevron triangle (folder twirl)."""
    if down:
        d = f"M{cx-3.4:.1f} {cy-1.8:.1f} L{cx+3.4:.1f} {cy-1.8:.1f} L{cx:.1f} {cy+2.6:.1f} Z"
    else:
        d = f"M{cx-1.8:.1f} {cy-3.4:.1f} L{cx+2.6:.1f} {cy:.1f} L{cx-1.8:.1f} {cy+3.4:.1f} Z"
    return f'<path d="{d}" {fill(raw)}/>'


# ───────────────────────────── window content ────────────────────────────
def window_content(style):
    """All interior elements of one window, drawn in local [0,0]→[W,H]."""
    bg = c(style, "editor.background")
    panel_bg = c(style, "panel.background")
    title_bg = c(style, "title_bar.background")
    tabbar_bg = c(style, "tab_bar.background")
    tab_active = c(style, "tab.active_background")
    status_bg = c(style, "status_bar.background")
    border = c(style, "border")
    border_var = c(style, "border.variant")
    text = c(style, "text")
    muted = c(style, "text.muted")
    accent = c(style, "text.accent")
    icon_muted = c(style, "icon.muted")
    line_no = c(style, "editor.line_number")
    active_no = c(style, "editor.active_line_number")
    active_bg = c(style, "editor.active_line.background")
    indent_guide = c(style, "editor.indent_guide")
    selection = style["players"][0]["selection"]
    elem_sel = c(style, "element.selected")
    elevated = c(style, "elevated_surface.background")
    focus = c(style, "border.focused")
    err = c(style, "error")
    warn = c(style, "warning")
    ok = c(style, "success")
    accent_solid = style["accents"][0]

    s = []

    # Base canvas (editor surface fills the whole body).
    s.append(rect(0, 0, W, H, f=bg))

    # ── Title bar ──
    s.append(rect(0, 0, W, TITLE_H, f=title_bg))
    s.append(line(0, TITLE_H, W, TITLE_H, border))
    for i, raw in enumerate((err, warn, ok)):
        s.append(circle(22 + i * 16, TITLE_H / 2, 5.5, raw))
    # centered project / branch pill
    pill_w = 188
    s.append(rect((W - pill_w) / 2, 12, pill_w, 15, r=7, s=border))
    s.append(bar((W - pill_w) / 2 + 12, 16.5, 70, muted, h=6))
    # right-side window controls
    for i in range(3):
        s.append(circle(W - 26 - i * 15, TITLE_H / 2, 2.3, icon_muted))

    # ── Left project dock ──
    s.append(rect(0, CONTENT_TOP, PANEL_W, CONTENT_BOT - CONTENT_TOP, f=panel_bg))
    s.append(line(PANEL_W, CONTENT_TOP, PANEL_W, CONTENT_BOT, border))
    # dock header
    s.append(bar(18, CONTENT_TOP + 16, 78, muted, h=6))
    row_y = CONTENT_TOP + 40
    for depth, kind, nw, irole, sel in TREE:
        cy = row_y + 9
        x = 16 + depth * 16
        if sel:
            s.append(rect(8, row_y, PANEL_W - 16, 19, r=5, f=elem_sel))
        if kind in ("open", "folder"):
            s.append(tri(x + 3, cy, icon_muted, down=(kind == "open")))
            ix = x + 13
        else:
            ix = x + 4
        # file/folder icon chip
        chip = {"muted": icon_muted, "accent": accent, "fn": syn(style, "fn"),
                "ty": syn(style, "ty"), "st": syn(style, "st")}[irole]
        s.append(rect(ix, cy - 3.5, 7, 7, r=2, f=chip))
        label = text if sel else muted
        s.append(bar(ix + 13, cy - 3, nw, label, h=6))
        row_y += 20

    # ── Tab bar (over the editor only) ──
    s.append(rect(EDITOR_X, TITLE_H, EDITOR_W, TAB_H, f=tabbar_bg))
    s.append(line(EDITOR_X, TITLE_H + TAB_H, W, TITLE_H + TAB_H, border))
    tx = EDITOR_X
    for nw, active, modified in TABS:
        tw = nw + 56
        if active:
            s.append(rect(tx, TITLE_H, tw, TAB_H, f=tab_active))
            # hide the bottom border under the active tab (merge into editor)
            s.append(line(tx + 1, TITLE_H + TAB_H, tx + tw - 1, TITLE_H + TAB_H, tab_active, 2))
            s.append(line(tx, TITLE_H, tx, TITLE_H + TAB_H, border))
            s.append(line(tx + tw, TITLE_H, tx + tw, TITLE_H + TAB_H, border))
        icy = TITLE_H + TAB_H / 2
        s.append(rect(tx + 14, icy - 4, 8, 8, r=2, f=(syn(style, "fn") if active else icon_muted)))
        s.append(bar(tx + 28, icy - 3, nw, text if active else muted, h=6))
        if modified:
            s.append(circle(tx + tw - 14, icy, 3, accent))
        tx += tw

    # ── Breadcrumb / toolbar strip ──
    crumb_y = TITLE_H + TAB_H + CRUMB_H / 2
    bx = EDITOR_X + 16
    for w in (40, 52, 64):
        s.append(bar(bx, crumb_y - 3, w, muted, h=5))
        bx += w + 14
        if w != 64:
            s.append(tri(bx - 9, crumb_y, icon_muted))
    for i in range(3):  # toolbar controls on the right
        s.append(rect(W - 26 - i * 18, crumb_y - 5, 10, 10, r=2, s=icon_muted))

    # ── Editor: active line, gutter numbers, code, selection, cursor ──
    cursor_x = cursor_y = None
    for i, (indent, tokens) in enumerate(CODE_LINES):
        top = CODE_TOP + 14 + i * LINE_H
        num_baseline = top + 6
        if i == ACTIVE:
            s.append(rect(EDITOR_X, top - 8, CODE_RIGHT - EDITOR_X, LINE_H, f=active_bg))
        # gutter number
        is_active = i == ACTIVE
        num = str(i + 1)
        s.append(
            f'<text x="{GUTTER_NUM_X:.1f}" y="{num_baseline:.1f}" text-anchor="end" '
            f'font-size="11" {fill(active_no if is_active else line_no)}>{num}</text>'
        )
        # indent guides
        for lvl in range(indent):
            gx = CODE_X + lvl * INDENT - 6
            s.append(line(gx, top - 6, gx, top + 13, indent_guide))
        # tokens
        x = CODE_X + indent * INDENT
        if tokens and tokens[0][0] == "co":  # comment line
            s.append(bar(x, top, tokens[0][1], syn(style, "co"), h=6))
            continue
        for j, (role, w) in enumerate(tokens):
            if (i, j) == SEL:
                s.append(rect(x - 3, top - 4, w + 6, 14, r=3, f=selection))
            s.append(bar(x, top, w, syn(style, role)))
            x += w + 8
        if is_active:
            cursor_x, cursor_y = x + 1, top
    if cursor_x is not None:
        s.append(rect(cursor_x, cursor_y - 4, 2, 14, f=accent_solid))

    # ── Minimap sliver ──
    s.append(rect(MINIMAP_X, CODE_TOP, MINIMAP_W, CONTENT_BOT - CODE_TOP, f=bg))
    mm_top = CODE_TOP + 10
    for i, (indent, tokens) in enumerate(CODE_LINES):
        if not tokens:
            continue
        my = mm_top + i * 7
        mx = MINIMAP_X + 5 + indent * 3
        wsum = sum(w for _, w in tokens) * 0.16 + (len(tokens) - 1) * 1.5
        s.append(rect(mx, my, max(4, wsum), 2.4, r=1, f=muted, extra='fill-opacity="0.40"'))
    # viewport box
    s.append(rect(MINIMAP_X + 2, mm_top + (ACTIVE - 5) * 7, MINIMAP_W - 4, 13 * 7,
                  r=3, f=accent_solid, extra='fill-opacity="0.10"'))

    # ── Completions popup (the one signature element, anchored at the cursor) ──
    if cursor_x is not None:
        pw, ph = 286, 138
        px = min(max(cursor_x - 16, CODE_X), CODE_RIGHT - pw)
        py = cursor_y + 16
        s.append(rect(px, py, pw, ph, r=9, f=elevated, s=focus,
                      extra='filter="url(#pop)"'))
        rows = [("kw", 96, False), ("fn", 120, True), ("ty", 80, False), ("va", 108, False)]
        ry = py + 12
        for role, lw, selrow in rows:
            if selrow:
                s.append(rect(px + 6, ry, pw - 12, 26, r=6, f=elem_sel))
            s.append(rect(px + 16, ry + 8, 11, 11, r=3, f=syn(style, role)))
            s.append(bar(px + 36, ry + 10, lw, text if selrow else muted, h=6))
            s.append(bar(px + pw - 64, ry + 11, 44, muted, h=5, r=2))
            ry += 30

    # ── Status bar ──
    sy = CONTENT_BOT
    s.append(rect(0, sy, W, STATUS_H, f=status_bg))
    s.append(line(0, sy, W, sy, border))
    mid = sy + STATUS_H / 2
    # branch
    s.append(circle(20, mid, 3, accent))
    s.append(bar(28, mid - 3, 30, accent, h=6))
    # diagnostics
    s.append(circle(76, mid, 3, err))
    s.append(bar(83, mid - 2.5, 9, muted, h=5))
    s.append(circle(104, mid, 3, warn))
    s.append(bar(111, mid - 2.5, 9, muted, h=5))
    # right: position + language indicators
    rx = W - 18
    for w in (40, 30, 50):
        s.append(bar(rx - w, mid - 2.5, w, muted, h=5))
        rx -= w + 18

    return "".join(s)


# ───────────────────────────── document assembly ─────────────────────────
def defs():
    return (
        '<defs>'
        '<filter id="ds" x="-25%" y="-25%" width="150%" height="150%">'
        '<feDropShadow dx="0" dy="9" stdDeviation="15" flood-color="#000000" flood-opacity="0.30"/>'
        '</filter>'
        '<filter id="pop" x="-25%" y="-25%" width="150%" height="150%">'
        '<feDropShadow dx="0" dy="6" stdDeviation="11" flood-color="#000000" flood-opacity="0.34"/>'
        '</filter>'
        f'<clipPath id="w1"><rect x="0" y="0" width="{W}" height="{H}" rx="{RADIUS}"/></clipPath>'
        f'<clipPath id="w2"><rect x="0" y="0" width="{W}" height="{H}" rx="{RADIUS}"/></clipPath>'
        '</defs>'
    )


def window(style, gid, transform):
    border = c(style, "border")
    shadow = rect(0, 0, W, H, r=RADIUS, f=c(style, "editor.background"),
                  extra='filter="url(#ds)"')
    frame = rect(0, 0, W, H, r=RADIUS, s=border)
    return (
        f'<g transform="{transform}">'
        f'{shadow}'
        f'<g clip-path="url(#{gid})">{window_content(style)}</g>'
        f'{frame}'
        f'</g>'
    )


def doc(width, height, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}">'
        f'{defs()}{body}</svg>'
    )


def render_single(style):
    m = 48                  # margin: room for the soft drop shadow on all sides
    cw, ch = W + m * 2, H + m * 2 + 12
    return doc(cw, ch, window(style, "w1", f"translate({m},{m})"))


def render_combined(dark, light):
    overlap = 104           # px the two windows overlap in the middle
    tilt = 3.0              # degrees of mirrored tilt
    m = 60                  # margin: room for the tilt excursion + shadows
    cw = W * 2 - overlap + m * 2
    ch = H + m * 2 + 32
    lx, dx = m, W - overlap + m
    ly, dy = m + 28, m
    left = window(light, "w1", f"translate({lx},{ly}) rotate({-tilt},{W/2},{H/2})")
    right = window(dark, "w2", f"translate({dx},{dy}) rotate({tilt},{W/2},{H/2})")
    # light behind, dark in front (dark drawn last → on top at the seam)
    return doc(cw, ch, left + right)


# ───────────────────────────────── cli ───────────────────────────────────
HEX = re.compile(r"#[0-9a-fA-F]{6,8}")


def theme_hexes():
    return {"#" + m.group(0)[1:7].lower() for m in HEX.finditer(THEME.read_text())}


def foreign_hexes(svg, theme):
    used = {"#" + m.group(0)[1:7].lower() for m in HEX.finditer(svg)}
    return sorted(used - theme)


def main():
    ap = argparse.ArgumentParser(description="Generate Geode preview SVGs from the theme.")
    ap.add_argument("--print-allowlist", action="store_true",
                    help="print each asset's non-theme hexes (expected: none) and exit")
    args = ap.parse_args()

    dark = load_style("Geode Dark")
    light = load_style("Geode Light")
    outputs = {
        "preview-dark.svg": render_single(dark),
        "preview-light.svg": render_single(light),
        "preview.svg": render_combined(dark, light),
    }

    if args.print_allowlist:
        theme = theme_hexes()
        for name, svg in outputs.items():
            foreign = foreign_hexes(svg, theme)
            print(f"assets/{name}: {foreign if foreign else 'none (no allowlist needed)'}")
        return 0

    for name, svg in outputs.items():
        (ASSETS / name).write_text(svg + "\n", encoding="utf-8")
        print(f"wrote assets/{name} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
