import argparse
import subprocess
import sys
from pathlib import Path

def git(repo: Path, *args: str) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output = True,
        text = True,
        encoding = "utf-8",
        errors = "replace",
    )
    return result.returncode, result.stdout.strip()

def check(repo: Path, fetch: bool) -> dict:
    if fetch:
        git(repo, "fetch", "--quiet")

    _, branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    _, status = git(repo, "status", "--porcelain")
    dirty = len(status.splitlines()) if status else 0

    # counts commits behind/ahead of the upstream branch
    code, counts = git(repo, "rev-list", "--left-right", "--count", "@{u}...HEAD")
    if code == 0:
        behind, ahead = map(int, counts.split())
        has_upstream = True
    else:
        behind = ahead = 0
        has_upstream = False

# WIP - CONTINUE HERE #