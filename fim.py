#!/usr/bin/env python3
"""Educational File Integrity Monitoring (FIM) for OWN test files only.

Baseline: SHA-256 hashes in plain text using `hash  samples/path` format.
Run: python3 fim.py baseline     # ONCE before edits
     python3 fim.py check        # As often as needed
"""
import argparse
import hashlib
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAMPLES = ROOT / "samples"
BASELINE = ROOT / "baseline.txt"
LINE_RE = re.compile(r"^([0-9a-f]{64})  (samples/[^\r\n]+)$")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_files():
    """Only user-owned files in samples/; never follow file symlinks."""
    if not SAMPLES.is_dir():
        raise RuntimeError("Missing samples/ folder.")
    found = {}
    for path in sorted(SAMPLES.rglob("*")):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(ROOT).as_posix()
            if "\n" in relative or "\r" in relative:
                raise RuntimeError("Newlines in filenames are unsupported.")
            found[relative] = sha256(path)
    return found


def load_baseline():
    if not BASELINE.is_file():
        raise RuntimeError("Missing baseline.txt. Run `python3 fim.py baseline` first.")
    trusted = {}
    for number, line in enumerate(BASELINE.read_text(encoding="utf-8").splitlines(), 1):
        match = LINE_RE.fullmatch(line)
        if not match:
            raise RuntimeError(f"Malformed baseline entry on line {number}.")
        digest, relative = match.groups()
        parts = Path(relative).parts
        if any(part in (".", "..") for part in parts) or relative in trusted:
            raise RuntimeError(f"Unsafe or duplicate baseline entry on line {number}.")
        trusted[relative] = digest
    if not trusted:
        raise RuntimeError("Baseline is empty.")
    return trusted


def print_clock():
    print("Timestamp:", datetime.now().astimezone().isoformat(timespec="seconds"))


def create_baseline():
    if BASELINE.exists():
        raise RuntimeError("baseline.txt already exists. Do NOT recreate it during the three tests.")
    current = current_files()
    if len(current) < 3:
        raise RuntimeError("Need at least three test files in samples/ first.")
    with BASELINE.open("x", encoding="utf-8", newline="\n") as f:
        for relative, digest in sorted(current.items()):
            f.write(f"{digest}  {relative}\n")
    print_clock()
    print(f"[BASELINE CREATED] {len(current)} files recorded in {BASELINE.name}")
    print("Original baseline now fixed: DO NOT run this command again during testing.")


def check():
    trusted = load_baseline()
    current = current_files()
    added = sorted(current.keys() - trusted.keys())
    deleted = sorted(trusted.keys() - current.keys())
    modified = sorted(name for name in (trusted.keys() & current.keys())
                      if trusted[name] != current[name])
    unchanged = len(trusted.keys() & current.keys()) - len(modified)
    print_clock()
    print("File Integrity Monitoring - SHA-256 check")
    for name in added:
        print(f"[ADDED]    {name}")
    for name in modified:
        print(f"[MODIFIED] {name}")
    for name in deleted:
        print(f"[DELETED]  {name}")
    print(f"Summary: ADDED={len(added)}, MODIFIED={len(modified)}, "
          f"DELETED={len(deleted)}, UNCHANGED={unchanged}")
    if not (added or modified or deleted):
        print("[CLEAN] All monitored files match the original baseline.")
    return bool(added or modified or deleted)


def main():
    parser = argparse.ArgumentParser(description="Monitor only files in ./samples using SHA-256")
    parser.add_argument("action", choices=["baseline", "check"])
    args = parser.parse_args()
    try:
        if args.action == "baseline":
            create_baseline()
            return 0
        else:
            return 1 if check() else 0  # 1 means an integrity alert, not a script crash
    except (OSError, RuntimeError) as exc:
        print(f"[ERROR] {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
