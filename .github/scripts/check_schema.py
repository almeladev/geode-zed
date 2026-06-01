#!/usr/bin/env python3
"""Validate the theme against Zed's theme JSON Schema (v0.2.0).

This complements ``validate_theme.py`` (which encodes Geode's own structural and
accessibility rules) by checking the file against the *shape* Zed expects.

The schema is **vendored** at ``.github/schemas/zed-theme-v0.2.0.json`` so the
check is deterministic and needs no network: zed.dev serves the canonical schema
behind a CDN that rejects automated fetches (HTTP 403), which used to make this
step a permanent ``SKIP`` in CI. The vendored copy pins the v0.2.0 shape and is
validated on every run instead.

Resolution order for the schema:
  1. the vendored file matching the theme's ``$schema`` version, if present;
  2. otherwise the remote ``$schema`` URL (best effort);
  3. otherwise ``SKIP`` (never a flaky failure).

The ``jsonschema`` package is still optional — without it the check ``SKIP``s.
A genuine schema violation, once a schema is resolved, is a hard error.

Refresh the vendored copy from upstream when zed.dev is reachable:
  curl -fsSL https://zed.dev/schema/themes/v0.2.0.json \
    -o .github/schemas/zed-theme-v0.2.0.json

Run: python3 .github/scripts/check_schema.py themes/geode.json
"""
import json
import os
import re
import sys
import urllib.request

# A browser-like UA; some CDNs reject the default urllib agent.
HEADERS = {"User-Agent": "Mozilla/5.0 (geode-zed schema check)"}

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "schemas")


def _vendored_schema_path(url):
    """Path to a vendored schema matching the version in ``url``, or None.

    The theme's ``$schema`` looks like
    ``https://zed.dev/schema/themes/v0.2.0.json``; we vendor it as
    ``schemas/zed-theme-v0.2.0.json``.
    """
    match = re.search(r"/themes/(v[\d.]+)\.json", url or "")
    if not match:
        return None
    candidate = os.path.join(SCHEMA_DIR, f"zed-theme-{match.group(1)}.json")
    return candidate if os.path.isfile(candidate) else None


def _load_schema(url):
    """Return (schema, source_label) or (None, reason) without ever raising."""
    vendored = _vendored_schema_path(url)
    if vendored:
        with open(vendored, encoding="utf-8") as fh:
            return json.load(fh), os.path.relpath(vendored)

    if not url:
        return None, "the theme declares no '$schema' URL and no vendored schema matches"

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp), url
    except Exception as exc:  # network/HTTP/JSON — all non-fatal here
        return None, f"could not fetch schema {url} ({type(exc).__name__}: {exc})"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_schema.py <theme.json>", file=sys.stderr)
        return 2
    path = sys.argv[1]

    with open(path, encoding="utf-8") as fh:
        theme = json.load(fh)

    try:
        from jsonschema.validators import validator_for
    except ImportError:
        print("SKIP: 'jsonschema' not installed — run `pip install jsonschema` to enable this check.")
        return 0

    schema, source = _load_schema(theme.get("$schema"))
    if schema is None:
        print(f"SKIP: {source}.")
        return 0

    cls = validator_for(schema)
    errors = sorted(cls(schema).iter_errors(theme), key=lambda e: list(e.path))
    if errors:
        print(f"FAIL: {len(errors)} schema violation(s) in {path} (against {source}):", file=sys.stderr)
        for e in errors[:50]:
            loc = "/".join(str(p) for p in e.path) or "<root>"
            print(f"  - {loc}: {e.message}", file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more", file=sys.stderr)
        return 1

    print(f"OK: {path} conforms to {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
