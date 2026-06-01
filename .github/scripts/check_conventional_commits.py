#!/usr/bin/env python3
"""Check that commit subject lines follow Conventional Commits.

CONTRIBUTING.md asks for Conventional Commit messages (e.g.
``feat(light): deepen citrine``); this enforces that automatically on the
commits a pull request adds. Merge commits are ignored (``git log --no-merges``)
since GitHub's merge commits are not authored by contributors.

No third-party dependencies — it shells out to ``git`` and matches a regex.

Run: python3 .github/scripts/check_conventional_commits.py [<range>]
The default range is ``origin/main..HEAD``.
"""
import re
import subprocess
import sys

# https://www.conventionalcommits.org — the conventional set plus `revert`.
TYPES = (
    "feat", "fix", "docs", "style", "refactor",
    "perf", "test", "build", "ci", "chore", "revert",
)

# <type>(<optional scope>)<optional !>: <description>
PATTERN = re.compile(rf"^(?:{'|'.join(TYPES)})(?:\([\w .,\-/]+\))?!?: .+")


def subjects(rev_range):
    out = subprocess.run(
        ["git", "log", "--no-merges", "--format=%s", rev_range],
        capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line.strip()]


def main() -> int:
    rev_range = sys.argv[1] if len(sys.argv) > 1 else "origin/main..HEAD"

    try:
        subs = subjects(rev_range)
    except subprocess.CalledProcessError as exc:
        print(f"FAIL: `git log {rev_range}` failed: {exc.stderr.strip()}", file=sys.stderr)
        return 1

    bad = [s for s in subs if not PATTERN.match(s)]
    if bad:
        print(f"FAIL: {len(bad)} commit subject(s) are not Conventional Commits:", file=sys.stderr)
        for s in bad:
            print(f"  - {s}", file=sys.stderr)
        print("\nExpected: <type>(<optional scope>): <description>", file=sys.stderr)
        print(f"Allowed types: {', '.join(TYPES)}", file=sys.stderr)
        return 1

    print(f"OK: {len(subs)} commit subject(s) follow Conventional Commits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
