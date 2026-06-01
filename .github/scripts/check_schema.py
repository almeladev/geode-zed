#!/usr/bin/env python3
"""Validate the theme against Zed's official published JSON Schema.

This is an *advisory* check that complements ``validate_theme.py`` (which
encodes Geode's own structural and accessibility rules). The schema URL is read
straight from the ``$schema`` field of the theme file, so it always tracks the
version the theme claims to target.

Because it depends on two things that are not always present — network access
to ``zed.dev`` and the optional ``jsonschema`` package — it degrades
gracefully: if either is missing it prints a ``SKIP`` note and succeeds, so it
never produces a flaky build for reasons outside the theme's control. When both
are available, a genuine schema violation is a hard error.

Run: python3 .github/scripts/check_schema.py themes/geode.json
"""
import json
import sys
import urllib.request

# A browser-like UA; some CDNs reject the default urllib agent.
HEADERS = {"User-Agent": "Mozilla/5.0 (geode-zed schema check)"}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_schema.py <theme.json>", file=sys.stderr)
        return 2
    path = sys.argv[1]

    with open(path, encoding="utf-8") as fh:
        theme = json.load(fh)

    url = theme.get("$schema")
    if not url:
        print(f"SKIP: {path} declares no '$schema' URL to validate against.")
        return 0

    try:
        from jsonschema.validators import validator_for
    except ImportError:
        print("SKIP: 'jsonschema' not installed — run `pip install jsonschema` to enable this check.")
        return 0

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            schema = json.load(resp)
    except Exception as exc:  # network/HTTP/JSON — all non-fatal here
        print(f"SKIP: could not fetch schema {url} ({type(exc).__name__}: {exc}).")
        return 0

    cls = validator_for(schema)
    errors = sorted(cls(schema).iter_errors(theme), key=lambda e: list(e.path))
    if errors:
        print(f"FAIL: {len(errors)} schema violation(s) in {path}:", file=sys.stderr)
        for e in errors[:50]:
            loc = "/".join(str(p) for p in e.path) or "<root>"
            print(f"  - {loc}: {e.message}", file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more", file=sys.stderr)
        return 1

    print(f"OK: {path} conforms to {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
