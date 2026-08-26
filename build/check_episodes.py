# -*- coding: utf-8 -*-
"""Verify each episode blurb is attached to the right episode.

Counts matching proves nothing: if Wikipedia numbers a two-hour premiere as one
row, every later code shifts by one and each blurb lands on its neighbour. So
compare the sheet's title against Wikipedia's for the same code.

    py build/check_episodes.py        # exits non-zero on any title mismatch
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.loads(re.search(r'id="timeline-data">(.*?)</script>',
                            open(os.path.join(HERE, os.pardir, "index.html"),
                                 encoding="utf-8").read(), re.S).group(1))
have = json.load(open(os.path.join(HERE, "data", "ep_synopses.json"), encoding="utf-8"))
sys.path.insert(0, HERE)
from ep_synopses import ALIAS      # deliberate one-row-covers-two pairings


def norm(s):
    s = s.lower().replace("&", "and").replace("’", "'")
    return re.sub(r"[^a-z0-9]", "", s)


rows = []
for e in data["entries"]:
    for it in (e.get("c") or {}).get("ep", []):
        if it.get("c"):
            rows.append((it["c"], it["t"]))

bad, nodata, ok = [], [], 0
for code, title in rows:
    rec = have.get(code)
    if not rec:
        nodata.append((code, title))
        continue
    wt, a, b = rec.get("title", ""), norm(title), norm(rec.get("title", ""))
    # the sheet splits some episodes Wikipedia keeps whole ("The Eclipse,
    # Part 1" vs "The Eclipse"), so one title being a prefix of the other is
    # the same episode, not a shift
    shared = b and (a.startswith(b) or b.startswith(a)) and min(len(a), len(b)) > 6
    aliased = norm(ALIAS.get(title, "")) == b and b != ""
    if a == b or shared or aliased:
        ok += 1
    else:
        bad.append((code, title, wt))

print("%d episodes | %d aligned | %d mismatched | %d without a blurb"
      % (len(rows), ok, len(bad), len(nodata)))
for code, sheet, wiki in bad:
    print("   MISMATCH %-8s sheet %-34s wikipedia %s" % (code, sheet[:34], wiki))
for code, title in nodata:
    print("   no blurb %-8s %s" % (code, title))
sys.exit(1 if bad else 0)
