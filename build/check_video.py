# -*- coding: utf-8 -*-
"""Verify every Heroes Unmasked file actually streams, and is an MP4 a browser
will play. Range-requests the first bytes of each and checks the ftyp box.

    py build/check_video.py          # exits non-zero if any file fails
"""
import json, os, re, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, os.pardir, "index.html")
DL = "https://archive.org/download/"
UA = {"User-Agent": "Mozilla/5.0"}


def dl_url(path):
    return DL + "/".join(urllib.parse.quote(p) for p in path.split("/"))


def main():
    data = json.loads(re.search(r'id="timeline-data">(.*?)</script>',
                                open(HTML, encoding="utf-8").read(), re.S).group(1))
    paths = []
    for e in data["entries"]:
        for items in (e.get("c") or {}).values():
            for it in items:
                if it.get("ia"):
                    paths.append((it["t"], it["ia"]))
    print("files to check: %d" % len(paths))

    bad = []
    for i, (title, path) in enumerate(paths, 1):
        url = dl_url(path)
        try:
            req = urllib.request.Request(url, headers={**UA, "Range": "bytes=0-63"})
            with urllib.request.urlopen(req, timeout=60) as r:
                head = r.read()
                ctype = r.headers.get("Content-Type", "")
                status = r.status
            # a real MP4 begins with a 'ftyp' box in the first 12 bytes
            ok = status in (200, 206) and ctype.startswith("video/") and b"ftyp" in head[:16]
            brand = head[8:12].decode("ascii", "replace") if b"ftyp" in head[:16] else "?"
            if not ok:
                bad.append((title, status, ctype))
            print("  %2d/%d %-4s %-9s brand=%-6s %s"
                  % (i, len(paths), "ok" if ok else "BAD", ctype[:9], brand, title[:44]))
        except Exception as ex:
            bad.append((title, "EXC", str(ex)))
            print("  %2d/%d BAD  %s -- %s" % (i, len(paths), title[:44], ex))

    print("\n%d ok, %d bad" % (len(paths) - len(bad), len(bad)))
    for b in bad:
        print("   FAILED:", b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
