import shutil
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

DOWNLOADS = Path.home() / "Downloads"

# folder name -> extensions that go in it
RULES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".pptx", ".xlsx", ".csv"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi"},
    "Audio": {".mp3", ".wav", ".flac"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".js", ".ts", ".py", ".json", ".html", ".css"},
    "Installers": {".exe", ".msi", ".dmg", ".apk"},
}

# partial downloads, skip these until they finish
TEMP_EXT = {".crdownload", ".part", ".tmp", ".download"}


def category_for(ext: str) -> str:
    for folder, exts in RULES.items():
        if ext in exts:
            return folder
    return "Other"


def unique_path(dest: Path) -> Path:
    """report.pdf exists -> report (1).pdf, report (2).pdf, ..."""
    candidate = dest
    i = 1
    while candidate.exists():
        candidate = dest.with_name(f"{dest.stem} ({i}){dest.suffix}")
        i += 1
    return candidate


def wait_until_stable(path: Path, checks: int = 3, interval: float = 1.0) -> bool:
    """Wait until the file size stops changing. False if the file vanished."""
    last_size, stable = -1, 0
    while stable < checks:
        if not path.exists():
            return False
        size = path.stat().st_size
        stable = stable + 1 if size == last_size else 0
        last_size = size
        time.sleep(interval)
    return True


def organize(path: Path) -> None:
    if path.suffix.lower() in TEMP_EXT or not path.is_file():
        return
    if not wait_until_stable(path):
        return

    target_dir = DOWNLOADS / category_for(path.suffix.lower())
    target_dir.mkdir(exist_ok=True)
    dest = unique_path(target_dir / path.name)

    try:
        shutil.move(str(path), str(dest))
    except PermissionError:
        print(f"Skipped (file in use): {path.name}")
        return
    print(f"{path.name} -> {dest.relative_to(DOWNLOADS)}")


class Handler(FileSystemEventHandler):
    def _handle(self, p: str) -> None:
        path = Path(p)
        # top level only, so files we already sorted are ignored
        if path.parent == DOWNLOADS:
            threading.Thread(target=organize, args=(path,), daemon=True).start()

    def on_created(self, event):
        if not event.is_directory:
            self._handle(event.src_path)

    def on_moved(self, event):
        # browsers rename file.crdownload -> file.pdf when done
        if not event.is_directory:
            self._handle(event.dest_path)


if __name__ == "__main__":
    observer = Observer()
    observer.schedule(Handler(), str(DOWNLOADS), recursive=False)
    observer.start()
    print(f"Watching {DOWNLOADS} (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
