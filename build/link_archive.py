# -*- coding: utf-8 -*-
"""Regenerate sync.py's UNMASKED_FILES map from the archive.org item.

    py build/link_archive.py            # print the map and a match report
    py build/link_archive.py --check    # exit non-zero if anything is unmatched

The archive item numbers Heroes Unmasked's first season differently from the
sheet -- it counts "A Heroes Welcome" and "The Story So Far" as episodes of
their own, so from episode 9 on, its numbering runs one ahead. Matching on
episode code would silently shift 14 entries; this matches on title instead and
reports anything it cannot place, in both directions.

Paste the printed block over UNMASKED_FILES in sync.py, then re-run sync.py.
"""
import json, re, sys, urllib.request

IDENT = "heroes.unmasked.behind-the-scenes"
HTML = __file__.rsplit("build", 1)[0] + "index.html"
TAGS = re.compile(r"\.(HDTV|PDTV|WS|XviD|XVID|DVDRip|x264)\b", re.I)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def archive_titles():
    url = "https://archive.org/metadata/" + IDENT
    md = json.load(urllib.request.urlopen(url, timeout=60))
    out = {}
    for f in md["files"]:
        name = f["name"]
        if not name.lower().endswith(".mp4"):
            continue
        m = re.match(r"Heroes\.Unmasked\.S\d\dE\d\d\.(.*)$", name.split("/")[-1])
        if not m:
            print("  unparsed filename: %s" % name, file=sys.stderr)
            continue
        title = m.group(1)
        cut = TAGS.search(title)
        if cut:
            title = title[:cut.start()]
        out.setdefault(norm(title.replace(".", " ")), name)
    return out


def sheet_titles():
    html = open(HTML, encoding="utf-8").read()
    data = json.loads(re.search(r'id="timeline-data">(.*?)</script>', html, re.S).group(1))
    # The behind-the-scenes column holds Inside Heroes, the disc featurettes and
    # the commentaries as well now. Only the Unmasked episodes are in this
    # archive item, and sync.py names them so they can be told apart.
    for e in data["entries"]:
        for it in (e.get("c") or {}).get("bts", []):
            if it["t"].startswith("Unmasked: ") or "Inside the Eclipse" in it["t"]:
                yield e["r"], it["t"]


def main():
    arch = archive_titles()
    mapping, missing = {}, []
    for row, title in sheet_titles():
        # sync.py names these "Unmasked: A New Dawn (UK premiere date ...)";
        # the archive item knows them as "A New Dawn"
        bare = re.sub(r"^Unmasked:\s*", "", title)
        key = norm(re.sub(r"\s*\(.*?\)\s*$", "", bare).strip())
        if key in arch:
            # keyed on the bare title: sync.py matches before it renames
            mapping[bare] = arch[key]
        else:
            missing.append((row, title))

    unused = sorted(set(arch.values()) - set(mapping.values()))

    print("UNMASKED_FILES = {")
    for k in sorted(mapping):
        print("    %-34s %s," % (json.dumps(k) + ":", json.dumps(mapping[k])))
    print("}")
    print()
    print("matched %d, unmatched %d, archive files unused %d"
          % (len(mapping), len(missing), len(unused)), file=sys.stderr)
    for row, t in missing:
        # the Inside the Eclipse entries are a different item and link separately
        note = "" if "Inside the Eclipse" not in t else "  (separate archive item - expected)"
        print("  UNMATCHED r%-4d %s%s" % (row, t, note), file=sys.stderr)
    for u in unused:
        print("  UNUSED %s" % u, file=sys.stderr)

    if "--check" in sys.argv:
        hard = [m for m in missing if "Inside the Eclipse" not in m[1]]
        if hard or unused:
            sys.exit(1)


if __name__ == "__main__":
    main()
