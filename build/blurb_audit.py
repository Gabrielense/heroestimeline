# -*- coding: utf-8 -*-
"""Which entries still say nothing about themselves.

Walks every release on the timeline, looks it up the same way the page does,
and reports the ones with no blurb -- and, separately, the ones with no picture
and the ones that are not clickable at all, since an entry with neither is dead
weight on the row.

    py build/blurb_audit.py
    py build/blurb_audit.py --list evo    # every gap in one column
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, os.pardir, "index.html")
OUT = os.path.join(HERE, "data", "blurb_audit.json")

COLUMNS = ["ep", "gn", "web", "evo", "unm", "phys", "misc"]
NAMES = {"ep": "Episodes", "gn": "Graphic novels", "web": "Webisodes",
         "evo": "Evolutions & iStory", "unm": "Heroes Unmasked",
         "phys": "Physical media", "misc": "Misc. releases"}


def block(html, ident):
    m = re.search(r'<script type="application/json" id="%s">(.*?)</script>'
                  % ident, html, re.S)
    return json.loads(m.group(1)) if m else {}


def lookup(x, key, item):
    """The same order index.html uses in extrasFor()."""
    code, title = item.get("c"), item["t"]
    if key == "gn":
        return (code and (x.get("gn") or {}).get(code)) or (x.get("gn") or {}).get(title)
    if key == "ep":
        return code and (x.get("ep") or {}).get(code)
    if key == "web":
        return code and (x.get("web") or {}).get(code)
    if key == "phys":
        return (x.get("phys") or {}).get(title)
    if key == "misc":
        return (x.get("misc") or {}).get(title)
    if key == "evo":
        site = (x.get("site") or {}).get(title)
        if site:
            return site
        evo = (x.get("evo") or {}).get(title)
        if evo:
            return evo
        ist = x.get("istory") or {}
        return (code and ist.get(code)) or ist.get(title)
    return None


def main():
    html = io.open(HTML, encoding="utf-8").read()
    data = block(html, "timeline-data")
    x = block(html, "extras-data")

    rows, totals = [], {}
    for entry in data.get("entries", []):
        for key in COLUMNS:
            for item in (entry.get("c") or {}).get(key, []):
                rec = lookup(x, key, item) or {}
                blurb = bool(rec.get("d"))
                picture = bool(rec.get("img"))
                # what makes a row clickable: something to say, something to
                # play, or a shop to send you to
                opens = bool(blurb or picture or rec.get("site") or item.get("ia")
                             or (item.get("l") or "").startswith(
                                 "https://archive.org/details/")
                             or key == "phys")
                t = totals.setdefault(key, {"n": 0, "blurb": 0, "img": 0, "dead": 0})
                t["n"] += 1
                t["blurb"] += blurb
                t["img"] += picture
                if not opens:
                    t["dead"] += 1
                if not blurb:
                    rows.append({"k": key, "d": entry.get("d") or entry.get("m") or "",
                                 "c": item.get("c") or "", "t": item["t"],
                                 "img": picture, "opens": opens})

    print("%-22s %5s %8s %8s %8s" % ("", "items", "blurbs", "pictures", "dead"))
    for key in COLUMNS:
        t = totals.get(key)
        if not t:
            continue
        print("%-22s %5d %7d%% %7d%% %8d"
              % (NAMES[key], t["n"], 100 * t["blurb"] // t["n"],
                 100 * t["img"] // t["n"], t["dead"]))
    total = sum(t["n"] for t in totals.values())
    missing = len(rows)
    print("\n%d of %d releases have no blurb (%d%%)"
          % (missing, total, 100 * missing // total))

    want = None
    if "--list" in sys.argv:
        want = sys.argv[sys.argv.index("--list") + 1]
    for key in COLUMNS:
        gaps = [r for r in rows if r["k"] == key]
        if not gaps:
            continue
        print("\n%s -- %d without a blurb%s"
              % (NAMES[key], len(gaps), ":" if want == key else
                 " (--list %s to see them)" % key))
        if want == key:
            for r in gaps:
                print("  %-10s %-8s %-44s%s%s"
                      % (r["d"], r["c"], r["t"][:44],
                         "" if r["img"] else "  no picture",
                         "" if r["opens"] else "  DOES NOT OPEN"))

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps({"totals": totals, "missing": rows}, ensure_ascii=False, indent=1))
    print("\nwrote %s" % OUT)


if __name__ == "__main__":
    main()
