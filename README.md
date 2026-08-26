# mastools

A small collection of practical command-line utilities written in Python.
No third-party dependencies — everything runs on the standard library
(Python 3.8+).

## Tools

### `tools/file_organizer.py`

Organize the files in a directory into sub-folders, grouped either by file
type (Images, Videos, Documents, Code, …) or by modification date
(`YYYY-MM`).

```bash
# Group by type (default)
python tools/file_organizer.py ~/Downloads

# Group by modification date instead
python tools/file_organizer.py ~/Downloads --by date

# Preview what would happen without moving anything
python tools/file_organizer.py ~/Downloads --dry-run
```

Notes:

- Sub-directories are left untouched; only regular files are moved.
- Name collisions are resolved by appending a counter (`report_1.pdf`).
- Files that cannot be read or moved are skipped with a warning instead of
  aborting the run.
- Unrecognized extensions go into a `Misc/` folder.

### `tools/text_stats.py`

Print statistics about one or more text files: character, word, line,
sentence and paragraph counts, average word/sentence length, and the ten
most frequent words.

```bash
python tools/text_stats.py notes.txt

# Multiple files at once
python tools/text_stats.py *.txt

# Read from stdin
cat report.txt | python tools/text_stats.py -
```

## Contributing

Each tool is a single self-contained script under `tools/` with a usage
docstring at the top. Keep new tools dependency-free where possible.
