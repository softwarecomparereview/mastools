#!/usr/bin/env python3
"""
text_stats.py — Print statistics about one or more text files.

Usage:
    python text_stats.py <file> [<file> ...]

Examples:
    python text_stats.py notes.txt
    python text_stats.py *.txt
    cat report.txt | python text_stats.py -
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


def analyse(text: str) -> dict:
    """Return a dictionary of statistics for *text*."""
    lines = text.splitlines()
    words = re.findall(r"\b\w+\b", text.lower())
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    word_freq = Counter(words)
    top_words = word_freq.most_common(10)

    avg_word_len = (
        sum(len(w) for w in words) / len(words) if words else 0
    )
    avg_sentence_len = (
        sum(len(s.split()) for s in sentences) / len(sentences)
        if sentences
        else 0
    )

    return {
        "characters": len(text),
        "characters_no_spaces": sum(1 for c in text if not c.isspace()),
        "lines": len(lines),
        "non_blank_lines": sum(1 for l in lines if l.strip()),
        "words": len(words),
        "unique_words": len(word_freq),
        "sentences": len(sentences),
        "paragraphs": len([p for p in text.split("\n\n") if p.strip()]),
        "avg_word_length": round(avg_word_len, 2),
        "avg_sentence_length_words": round(avg_sentence_len, 2),
        "top_words": top_words,
    }


def print_stats(name: str, stats: dict) -> None:
    """Pretty-print *stats* for a file identified by *name*."""
    sep = "─" * 50
    print(f"\n{sep}")
    print(f"  File : {name}")
    print(sep)
    print(f"  Characters            : {stats['characters']:>10,}")
    print(f"  Characters (no space) : {stats['characters_no_spaces']:>10,}")
    print(f"  Lines                 : {stats['lines']:>10,}")
    print(f"  Non-blank lines       : {stats['non_blank_lines']:>10,}")
    print(f"  Words                 : {stats['words']:>10,}")
    print(f"  Unique words          : {stats['unique_words']:>10,}")
    print(f"  Sentences             : {stats['sentences']:>10,}")
    print(f"  Paragraphs            : {stats['paragraphs']:>10,}")
    print(f"  Avg word length       : {stats['avg_word_length']:>10}")
    print(f"  Avg sentence length   : {stats['avg_sentence_length_words']:>10} words")
    if stats["top_words"]:
        print("\n  Top 10 words:")
        for word, count in stats["top_words"]:
            print(f"    {word:<20} {count:>5}")
    print(sep)


def process(source: str) -> None:
    """Read *source* (file path or '-' for stdin) and print stats."""
    if source == "-":
        text = sys.stdin.read()
        name = "<stdin>"
    else:
        path = Path(source)
        if not path.is_file():
            print(f"Warning: '{source}' is not a file — skipped.", file=sys.stderr)
            return
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"Error reading '{source}': {exc}", file=sys.stderr)
            return
        name = path.name

    stats = analyse(text)
    print_stats(name, stats)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Display statistics about text files."
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="file",
        help="Text file(s) to analyse, or '-' for stdin",
    )
    args = parser.parse_args()

    for f in args.files:
        process(f)


if __name__ == "__main__":
    main()
