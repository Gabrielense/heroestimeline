# -*- coding: utf-8 -*-
"""Verify every downloaded card is a complete image before it enters history.

A fetch that is interrupted mid-write leaves a truncated file that still looks
plausible on disk, and a half-written JPEG committed to git is worse than a
missing one: it renders as a broken image rather than being hidden.

Checks the magic bytes at both ends -- a JPEG must open FFD8 and close FFD9, a
PNG must open with its signature and close with IEND -- plus a sane size.

    py build/check_cards.py        # exits non-zero if any file is bad
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(HERE, os.pardir, "assets", "cards")
MIN_BYTES = 500


def check(path):
    size = os.path.getsize(path)
    if size < MIN_BYTES:
        return "only %d bytes" % size
    with open(path, "rb") as f:
        head = f.read(8)
        f.seek(-12, os.SEEK_END)
        tail = f.read()
    if head[:2] == b"\xff\xd8":
        return None if b"\xff\xd9" in tail else "JPEG has no end marker (truncated)"
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return None if b"IEND" in tail else "PNG has no IEND chunk (truncated)"
    return "not a JPEG or PNG (starts %s)" % head[:4].hex()


def main():
    if not os.path.isdir(CARDS):
        sys.exit("no assets/cards directory")
    files = sorted(f for f in os.listdir(CARDS) if not f.startswith("."))
    bad = []
    total = 0
    for f in files:
        p = os.path.join(CARDS, f)
        total += os.path.getsize(p)
        why = check(p)
        if why:
            bad.append((f, why))
    print("%d files, %.1f MB" % (len(files), total / 1e6))
    print("complete: %d | bad: %d" % (len(files) - len(bad), len(bad)))
    for f, why in bad:
        print("   BAD %-16s %s" % (f, why))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
