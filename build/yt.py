# -*- coding: utf-8 -*-
"""Check a YouTube id before it goes into manual_extras.json.

A few things here survive only because somebody recorded them off the
television -- the Super Bowl spot, the teaser NBC slipped into the Olympics --
so the `yt` field points at a stranger's upload, and the upload date is how you
tell the real thing from a later re-cut. This prints it, with the length and the
title, so a `yt` can be checked without opening a browser.

    py build/yt.py SP2u3Im4AVE 1gvDteBO4io
    py build/yt.py --search "Heroes Reborn announcement promo 2014"
"""
import json, re, sys, urllib.parse, urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, TypeError):
    pass

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def one(vid):
    try:
        body = fetch("https://www.youtube.com/watch?v=" + urllib.parse.quote(vid))
    except Exception as e:
        print("%-12s ERROR %s" % (vid, e))
        return
    def grab(pat, default="?"):
        m = re.search(pat, body)
        return m.group(1) if m else default
    print("%-12s %-25s %5ss  %s" % (
        vid,
        grab(r'"uploadDate":"([^"]+)"')[:10],
        grab(r'"lengthSeconds":"(\d+)"'),
        grab(r'<meta name="title" content="([^"]*)"')))


def search(query):
    body = fetch("https://www.youtube.com/results?search_query="
                 + urllib.parse.quote(query))
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", body)
    if not m:
        sys.exit("YouTube did not return a result payload")
    hits = []

    def walk(node):
        if isinstance(node, dict):
            if "videoRenderer" in node:
                v = node["videoRenderer"]
                hits.append((v.get("videoId"),
                             "".join(r.get("text", "")
                                     for r in v.get("title", {}).get("runs", [])),
                             v.get("lengthText", {}).get("simpleText", "")))
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(json.loads(m.group(1)))
    for vid, title, length in hits[:15]:
        print("%-12s %-7s %s" % (vid, length, title))


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--search":
        search(" ".join(args[1:]))
        return
    for vid in args:
        one(vid)


if __name__ == "__main__":
    main()
