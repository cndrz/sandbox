import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def unique_target(target: Path, claimed: set) -> Path:
    """Return a path that doesn't exist on disk and isn't already claimed in this run."""
    if not target.exists() and target not in claimed:
        return target
    i = 1
    while True:
        candidate = target.with_name(f"{target.stem} ({i}){target.suffix}")
        if not candidate.exists() and candidate not in claimed:
            return candidate
        i += 1


def apply_case(name: str, case: str) -> str:
    if case == "lower":
        return name.lower()
    if case == "upper":
        return name.upper()
    if case == "title":
        return name.title()
    if case == "swap":
        return name.swapcase()
    return name


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bulk file renamer with regex, numbering, prefix/suffix, and case changes.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python rename.py . --dry-run\n"
            "  python rename.py ./Downloads --regex 'IMG_(\\d+)' --replace 'Vacation_\\1' --apply\n"
            "  python rename.py . --prefix 'Project_' --suffix '_final' --apply --yes\n"
            "  python rename.py . --number --pad 3 --start 1 --apply\n"
            "  python rename.py . --case lower --ext .jpg --apply\n"
        ),
    )

    parser.add_argument("source", nargs="?", default=".", help="Directory to rename files in (default: current directory)")
    parser.add_argument("-r", "--regex", help="Regex pattern to match against the filename stem")
    parser.add_argument("-R", "--replace", default="", help="Replacement string (supports groups like \\1, \\2)")
    parser.add_argument("--prefix", help="Text to prepend to the filename stem")
    parser.add_argument("--suffix", help="Text to append to the filename stem (before extension)")
    parser.add_argument("-n", "--number", action="store_true", help="Append sequential numbering to the filename stem")
    parser.add_argument("--start", type=int, default=1, help="Starting number for numbering (default: 1)")
    parser.add_argument("--pad", type=int, default=0, help="Zero-pad numbers to this width (e.g. 3 -> 001)")
    parser.add_argument("-c", "--case", choices=["lower", "upper", "title", "swap"], help="Change case of the filename stem")
    parser.add_argument("-e", "--ext", help="Change file extension (e.g. .txt or txt)")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Make regex matching case-insensitive")
    parser.add_argument("-x", "--exclude", action="append", default=[], help="Regex pattern to exclude files (can be used multiple times)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview changes without renaming (default)")
    parser.add_argument("--apply", action="store_true", help="Actually rename files")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation when applying")
    parser.add_argument("--undo-log", default="rename_undo.json", help="Name of undo log file (saved in source directory)")

    args = parser.parse_args()

    if args.apply:
        args.dry_run = False

    source = Path(args.source).expanduser().resolve()
    if not source.is_dir():
        sys.exit(f"Not a directory: {source}")

    files = [
        p for p in source.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.name != args.undo_log
    ]
    if not files:
        sys.exit(f"No files found in {source}")

    flags = re.IGNORECASE if args.ignore_case else 0
    pattern = re.compile(args.regex, flags) if args.regex else None
    excludes = [re.compile(e, flags) for e in args.exclude]

    plan = []
    claimed = set()
    count = args.start

    for src in sorted(files):
        name = src.name

        if any(ex.search(name) for ex in excludes):
            continue

        stem = src.stem
        ext = src.suffix
        new_stem = stem

        # Regex
        if pattern:
            if not pattern.search(new_stem):
                continue
            new_stem = pattern.sub(args.replace, new_stem)

        # Case
        if args.case:
            new_stem = apply_case(new_stem, args.case)

        # Prefix / suffix
        if args.prefix:
            new_stem = args.prefix + new_stem
        if args.suffix:
            new_stem = new_stem + args.suffix

        # Numbering
        if args.number:
            num_str = str(count).zfill(args.pad) if args.pad > 0 else str(count)
            new_stem = f"{new_stem}{num_str}"
            count += 1

        # Extension
        if args.ext:
            new_ext = args.ext if args.ext.startswith(".") else f".{args.ext}"
        else:
            new_ext = ext

        new_name = new_stem + new_ext
        if new_name == name:
            continue

        target = unique_target(src.with_name(new_name), claimed)
        claimed.add(target)
        plan.append((src, target))

    if not plan:
        sys.exit("No changes to make.")

    print(f"Source: {source}")
    print(f"Files scanned: {len(files)} | Planned renames: {len(plan)}\n")
    for src, target in plan:
        print(f"{src.name} -> {target.name}")

    if args.dry_run:
        print("\nDRY RUN - nothing renamed. Use --apply to execute.")
        return

    if not args.yes:
        confirm = input("\nProceed with renames? [y/N] ").strip().lower()
        if confirm != "y":
            sys.exit("Cancelled")

    undo_moves = []
    for src, target in plan:
        try:
            src.rename(target)
            undo_moves.append({"from": str(target), "to": str(src)})
        except OSError as exc:
            print(f"[error] Failed to rename {src.name}: {exc}")

    if undo_moves:
        log_path = source / args.undo_log
        log_data = {"created": datetime.now().isoformat(), "moves": undo_moves}
        try:
            with log_path.open("w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2)
            print(f"\nUndo log saved to: {log_path}")
        except OSError as exc:
            print(f"\n[error] Failed to write undo log: {exc}")


if __name__ == "__main__":
    main()
