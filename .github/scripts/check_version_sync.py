#!/usr/bin/env python3
"""Guard that the released version is documented.

A release is only "real" once its version appears in the changelog, so this
keeps `extension.toml` and `CHANGELOG.md` from drifting apart: the `version`
declared in `extension.toml` must have a matching `## [<version>]` section in
`CHANGELOG.md`.

No third-party dependencies — `extension.toml`'s `version` line is simple
enough to read with a regex.

Run: python3 .github/scripts/check_version_sync.py
"""
import re
import sys

EXTENSION_TOML = "extension.toml"
CHANGELOG = "CHANGELOG.md"

VERSION_LINE = re.compile(r'^\s*version\s*=\s*"([^"]+)"\s*$', re.MULTILINE)


def main() -> int:
    try:
        with open(EXTENSION_TOML, encoding="utf-8") as fh:
            toml = fh.read()
        with open(CHANGELOG, encoding="utf-8") as fh:
            changelog = fh.read()
    except OSError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    match = VERSION_LINE.search(toml)
    if not match:
        print(f"FAIL: no version line found in {EXTENSION_TOML}", file=sys.stderr)
        return 1
    version = match.group(1)

    heading = re.compile(rf"^##\s*\[{re.escape(version)}\]", re.MULTILINE)
    if not heading.search(changelog):
        print(
            f"FAIL: {EXTENSION_TOML} declares version {version!r} but {CHANGELOG} "
            f"has no '## [{version}]' section. Add a changelog entry for this release.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: version {version} from {EXTENSION_TOML} is documented in {CHANGELOG}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
