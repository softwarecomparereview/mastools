#!/usr/bin/env python3
"""
file_organizer.py — Organize files in a directory by type or date.

Usage:
    python file_organizer.py <source_dir> [--by date|type] [--dry-run]

Examples:
    python file_organizer.py ~/Downloads
    python file_organizer.py ~/Downloads --by date
    python file_organizer.py ~/Downloads --dry-run
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Mapping of file extensions to category folder names
EXTENSION_MAP = {
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".gif": "Images", ".bmp": "Images", ".svg": "Images",
    ".webp": "Images", ".ico": "Images", ".tiff": "Images",
    # Videos
    ".mp4": "Videos", ".mov": "Videos", ".avi": "Videos",
    ".mkv": "Videos", ".wmv": "Videos", ".flv": "Videos",
    ".webm": "Videos",
    # Audio
    ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio",
    ".aac": "Audio", ".ogg": "Audio", ".m4a": "Audio",
    # Documents
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".xls": "Documents", ".xlsx": "Documents", ".ppt": "Documents",
    ".pptx": "Documents", ".odt": "Documents", ".ods": "Documents",
    ".odp": "Documents",
    # Text / Code
    ".txt": "Text", ".md": "Text", ".rst": "Text", ".csv": "Text",
    ".py": "Code", ".js": "Code", ".ts": "Code", ".html": "Code",
    ".css": "Code", ".java": "Code", ".c": "Code", ".cpp": "Code",
    ".h": "Code", ".go": "Code", ".rs": "Code", ".sh": "Code",
    # Archives
    ".zip": "Archives", ".tar": "Archives", ".gz": "Archives",
    ".bz2": "Archives", ".xz": "Archives", ".7z": "Archives",
    ".rar": "Archives",
    # Executables / Installers
    ".exe": "Executables", ".msi": "Executables", ".dmg": "Executables",
    ".deb": "Executables", ".rpm": "Executables", ".appimage": "Executables",
}


def get_category(path: Path) -> str:
    """Return the category folder name for a given file."""
    return EXTENSION_MAP.get(path.suffix.lower(), "Misc")


def get_date_folder(path: Path) -> str:
    """Return a YYYY-MM folder name based on the file's modification time."""
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return mtime.strftime("%Y-%m")


def unique_dest(dest: Path) -> Path:
    """Return a non-colliding destination path by appending a counter."""
    if not dest.exists():
        return dest
    stem, suffix, parent = dest.stem, dest.suffix, dest.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def organize(source_dir: Path, by: str, dry_run: bool) -> None:
    """Move files from *source_dir* into sub-folders grouped by *by*."""
    if not source_dir.is_dir():
        print(f"Error: '{source_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    moved = 0
    skipped = 0

    for item in sorted(source_dir.iterdir()):
        if item.is_dir():
            continue  # skip sub-directories

        try:
            folder_name = get_date_folder(item) if by == "date" else get_category(item)
            dest_dir = source_dir / folder_name
            dest = unique_dest(dest_dir / item.name)

            if dry_run:
                print(f"[dry-run] Would move: {item.name}  →  {folder_name}/")
            else:
                dest_dir.mkdir(exist_ok=True)
                shutil.move(str(item), str(dest))
                print(f"Moved: {item.name}  →  {folder_name}/")
            moved += 1
        except OSError as exc:
            print(f"Skipped '{item.name}': {exc}", file=sys.stderr)
            skipped += 1

    if moved == 0 and skipped == 0:
        print("No files to organize.")
    elif dry_run:
        print(f"\n{moved} file(s) would be moved (dry-run, nothing changed).")
    else:
        print(f"\n{moved} file(s) moved, {skipped} skipped.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Organize files in a directory by type or date."
    )
    parser.add_argument("source_dir", help="Directory to organize")
    parser.add_argument(
        "--by",
        choices=["type", "date"],
        default="type",
        help="Group files by 'type' (default) or 'date'",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving any files",
    )
    args = parser.parse_args()

    organize(Path(args.source_dir), args.by, args.dry_run)


if __name__ == "__main__":
    main()
