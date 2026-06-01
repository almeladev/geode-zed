#!/usr/bin/env python3
"""Generator for the Geode v1.0.0 proposal preview.

Renders a full editor mockup of the v1.0.0 proposal in BOTH variants, side by
side, so all of its changes can be judged in one image:

  1. Properties / fields / members carry the periwinkle "data" tone, in context
     among the gems.
  2. The hardened UI chrome: legible gutter line numbers and a search-field
     placeholder.
  3. A terminal strip whose ANSI "white" output is legible — the fix for
     Geode Light, where it used to be near-invisible.

Text is rendered with <tspan> runs so glyph spacing is exact. Kept in-repo so
the preview is reproducible.
"""
import html

PALETTES = {
    "dark": {
        "name": "Geode",
        "bg": "#1c1924", "surface": "#211e2a", "border": "#363142",
        "fg": "#e1e9ef", "ame": "#bca0ee", "sap": "#86a3e4", "cit": "#e6cd7a",
        "aqu": "#7eddd6", "eme": "#7dd980", "muted": "#978fac", "peri": "#a9b6e6",
        "linenum": "#8b84a0", "active_linenum": "#bca0ee", "active_line": "#221f2e",
        "placeholder": "#8c85a0", "comment": "#9690a4",
        "term_bg": "#1c1924", "term_green": "#7dd980", "term_blue": "#86a3e4",
        "term_white": "#bac5cf", "term_fg": "#e1e9ef", "term_dim": "#978fac",
    },
    "light": {
        "name": "Geode Light",
        "bg": "#f6f4fb", "surface": "#eeebf4", "border": "#d5d1e0",
        "fg": "#312a41", "ame": "#6e3dc2", "sap": "#315ab9", "cit": "#735c11",
        "aqu": "#196b66", "eme": "#216e23", "muted": "#696080", "peri": "#444d99",
        "linenum": "#6e6880", "active_linenum": "#6e3dc2", "active_line": "#efeaf7",
        "placeholder": "#6a647b", "comment": "#665d79",
        "term_bg": "#f6f4fb", "term_green": "#216e23", "term_blue": "#315ab9",
        "term_white": "#4e495e", "term_fg": "#312a41", "term_dim": "#696080",
    },
}

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "ui-sans-serif,system-ui,sans-serif"
LINE_H = 22
CODE_TOP = 92
GUTTER_W = 46
FONT = 13


def t(text, key):
    return (text, key)


# The snippet. Color keys index the active palette; "p" = periwinkle property.
SNIPPET = [
    [t("interface ", "ame"), t("User", "cit"), t(" {", "muted")],
    [t("  ", "muted"), t("id", "p"), t(": ", "muted"), t("number", "cit")],
    [t("  ", "muted"), t("profile", "p"), t(": { ", "muted"), t("name", "p"),
     t(": ", "muted"), t("string", "cit"), t("; ", "muted"), t("active", "p"),
     t(": ", "muted"), t("boolean", "cit"), t(" }", "muted")],
    [t("}", "muted")],
    [],
    [t("async function ", "ame"), t("loadUser", "sap"), t("(", "muted"),
     t("id", "fg"), t(": ", "muted"), t("number", "cit"), t("): ", "muted"),
     t("Promise", "cit"), t("<", "muted"), t("User", "cit"), t("> {", "muted")],
    [t("  ", "muted"), t("const ", "ame"), t("res", "fg"), t(" = ", "muted"),
     t("await ", "ame"), t("client", "fg"), t(".", "muted"), t("get", "sap"),
     t("(", "muted"), t("`/users/${", "eme"), t("id", "fg"), t("}`", "eme"), t(")", "muted")],
    [t("  ", "muted"), t("const ", "ame"), t("data", "fg"), t(" = ", "muted"),
     t("res", "fg"), t(".", "muted"), t("data", "p")],
    [t("  ", "muted"), t("return ", "ame"), t("{", "muted")],
    [t("    ", "muted"), t("id", "p"), t(": ", "muted"), t("data", "fg"),
     t(".", "muted"), t("id", "p"), t(",", "muted")],
    [t("    ", "muted"), t("name", "p"), t(": ", "muted"), t("data", "fg"),
     t(".", "muted"), t("profile", "p"), t(".", "muted"), t("name", "p"), t(",", "muted")],
    [t("    ", "muted"), t("active", "p"), t(": ", "muted"), t("data", "fg"),
     t(".", "muted"), t("profile", "p"), t(".", "muted"), t("active", "p"),
     t(" ?? ", "muted"), t("false", "aqu")],
    [t("  ", "muted"), t("}", "muted")],
    [t("}", "muted")],
    [],
    [t("const ", "ame"), t("user", "fg"), t(" = ", "muted"), t("await ", "ame"),
     t("loadUser", "sap"), t("(", "muted"), t("42", "aqu"), t(")", "muted")],
    [t("console", "fg"), t(".", "muted"), t("log", "sap"), t("(", "muted"),
     t("user", "fg"), t(".", "muted"), t("profile", "p"), t(".", "muted"),
     t("name", "p"), t(")", "muted")],
]

# Terminal strip: a prompt line and an ANSI "white" output line.
TERM = [
    [t("$ ", "term_green"), t("node ", "term_fg"), t("app.js", "term_blue")],
    [t("→ ", "term_dim"), t("Ada — profile loaded (active)", "term_white")],
]


def runs(line, pal):
    spans = []
    for text, key in line:
        if key == "p":  # "p" = periwinkle property tone
            key = "peri"
        spans.append(f'<tspan fill="{pal[key]}">{html.escape(text)}</tspan>')
    return "".join(spans)


def window(x, y, w, h, pal):
    out = []
    code_h = CODE_TOP + len(SNIPPET) * LINE_H + 8
    term_y = y + code_h + 10
    term_h = h - code_h - 10
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{pal["bg"]}" stroke="{pal["border"]}"/>')
    out.append(f'<clipPath id="clip{x}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/></clipPath>')
    out.append(f'<g clip-path="url(#clip{x})">')
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="36" fill="{pal["surface"]}"/>')
    out.append(f'<line x1="{x}" y1="{y+36}" x2="{x+w}" y2="{y+36}" stroke="{pal["border"]}"/>')
    for i, c in enumerate(("#eb9aaf" if pal["name"] == "Geode" else "#b22a45",
                           pal["cit"], pal["eme"])):
        out.append(f'<circle cx="{x+18+i*15}" cy="{y+18}" r="4" fill="{c}"/>')
    out.append(f'<text x="{x+w-14}" y="{y+22}" text-anchor="end" font-size="12.5" '
               f'fill="{pal["muted"]}" font-family="{SANS}">{html.escape(pal["name"])}</text>')
    # search field with placeholder (demonstrates the placeholder-contrast fix)
    sf_x = x + 78
    out.append(f'<rect x="{sf_x}" y="{y+50}" width="{w-96}" height="22" rx="6" '
               f'fill="{pal["surface"]}" stroke="{pal["border"]}"/>')
    out.append(f'<text x="{sf_x+10}" y="{y+65}" font-size="12" fill="{pal["placeholder"]}" '
               f'font-family="{SANS}">Search project… (placeholder)</text>')
    # gutter + code
    cy0 = y + CODE_TOP
    out.append(f'<line x1="{x+GUTTER_W}" y1="{y+82}" x2="{x+GUTTER_W}" y2="{term_y-10}" stroke="{pal["border"]}"/>')
    active = 16  # the console.log line — highlight it
    for i, line in enumerate(SNIPPET):
        ly = cy0 + i * LINE_H
        if i == active:
            out.append(f'<rect x="{x+GUTTER_W+1}" y="{ly-15}" width="{w-GUTTER_W-2}" height="{LINE_H}" fill="{pal["active_line"]}"/>')
        ncol = pal["active_linenum"] if i == active else pal["linenum"]
        out.append(f'<text x="{x+GUTTER_W-8}" y="{ly}" text-anchor="end" font-size="11.5" '
                   f'fill="{ncol}" font-family="{MONO}">{i+1}</text>')
        if line:
            out.append(f'<text x="{x+GUTTER_W+12}" y="{ly}" font-size="{FONT}" '
                       f'font-family="{MONO}" xml:space="preserve">{runs(line, pal)}</text>')
    # terminal strip
    out.append(f'<rect x="{x}" y="{term_y}" width="{w}" height="{term_h}" fill="{pal["term_bg"]}"/>')
    out.append(f'<line x1="{x}" y1="{term_y}" x2="{x+w}" y2="{term_y}" stroke="{pal["border"]}"/>')
    out.append(f'<text x="{x+16}" y="{term_y+20}" font-size="10.5" fill="{pal["muted"]}" '
               f'font-family="{SANS}" letter-spacing="0.8">TERMINAL</text>')
    for i, line in enumerate(TERM):
        out.append(f'<text x="{x+16}" y="{term_y+40+i*LINE_H}" font-size="{FONT}" '
                   f'font-family="{MONO}" xml:space="preserve">{runs(line, pal)}</text>')
    out.append('</g>')
    return "\n".join(out)


def build():
    win_w, win_h = 600, 560
    gap, pad = 28, 24
    W = pad * 2 + win_w * 2 + gap
    H = 96 + win_h + 24
    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{SANS}">',
        f'<rect width="{W}" height="{H}" rx="18" fill="#100d16"/>',
        f'<text x="{pad+2}" y="42" font-size="21" fill="#e1e9ef" font-weight="700">'
        f'Geode v1.0.0 — propiedades con color + accesibilidad</text>',
        f'<text x="{pad+2}" y="68" font-size="13.5" fill="#8a83a0">'
        f'Propiedades en periwinkle · números de línea y placeholder legibles · '
        f'texto «white» de terminal visible en el corte claro</text>',
        window(pad, 92, win_w, win_h, PALETTES["dark"]),
        window(pad + win_w + gap, 92, win_w, win_h, PALETTES["light"]),
        '</svg>',
    ]
    with open("assets/preview-v1.svg", "w", encoding="utf-8") as fh:
        fh.write("\n".join(s))
    print("wrote assets/preview-v1.svg")


if __name__ == "__main__":
    build()
