import argparse
import hashlib
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

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

# WIP