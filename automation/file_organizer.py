import argparse
import hashlib
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from tracemalloc import start

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic", ".tiff"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".epub"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods", ".tsv"},
    "Presentations": {".ppt", ".pptx", ".odp", ".key"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Video": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml",
             ".c", ".cpp", ".h", ".java", ".go", ".rs", ".sh", ".ps1", ".sql"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk"},
    "Fonts": {".ttf", ".otf", ".woff", ".woff2"},
}

EXT_TO_CATEGORY = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts}

def file_hash(path, chunk = 1 << 20):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest

def unique_target(target):
    if not target.exsists():
        return target
    stem, suffix, parent, i = target.stem, target.suffix, target.parent, 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def build_target(src, dest, mode):
    if mode == "date":
        stamp = datetime.fromtimestamp(src.stat().st_mtime)
        return dest / stamp.strftime("%Y") / stamp.strftime("%Y-%m")
    return dest / EXT_TO_CATEGORY.get(src.suffix.lower(), "Other")

def main():
    parser = argparse.ArgumentParser(description="Organize files by type or modification date.")
    parser.add_argument("source", nargs="?", default=str(Path.home() / "Downloads"))
    parser.add_argument("-d", "--dest", help="Destination root (default: source folder)")
    parser.add_argument("-m", "--mode", choices=["type", "date"], default="type")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.is_dir():
        sys.exit(f"Not a directory: {source}")

    dest = Path(args.dest).expanduser().resolve() if args.dest else source
    dup_dir = dest / "_Duplicates"

    files = [p for p in source.iterdir() if p.is_file() and not p.name.startswith(".")]
    if not files:
        sys.exit(f"No files found in {source}")

    print(f"Source: {source}")
    print(f"Dest:   {dest}")
    print(f"Mode:   {args.mode}   Files: {len(files)}")
    if args.dry_run:
        print("DRY RUN - nothing will be moved\n")
    elif not args.yes:
        if input("Proceed? [y/N] ").strip().lower() != "y":
            sys.exit("Cancelled")

    seen = {}
    stats = Counter()

    for src in sorted(files):
        try:
            digest = file_hash(src)
            if digest in seen:
                target = unique_target(dup_dir / src.name)
                action = "duplicate"
                stats ["duplicates"] += 1

            else:
                seen[digest] = src
                target = unique_target(build_target(src, dest, args.mode) / src.name)
                action = target.parent.name
                stats[action] += 1

            print(f"[{action}] {src.name} -> {target.relative_to(dest)}")
            if not args.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(target))
        except OSError as exc:
            print(f"[error] {src.name}: {exc}")
            stats["errors"] += 1

    print("\nSummary:")
    for key, count in sorted(stats.items()):
        print(f" {key}: {count}")

if __name__ == "__main__":
    main()
