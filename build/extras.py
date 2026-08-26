# -*- coding: utf-8 -*-
"""Merge the collected extras into the <script id="extras-data"> block in index.html.

Inputs, all under build/data/ and each produced by its own collector:

    gn_synopses.json   per-issue blurbs + credits   (gn_synopses.py, Wikipedia CC BY-SA)
    gn_wiki.json       per-issue title card + cover (scrape_wiki.py, heroeswiki)
    sites.json         old promo/ARG site snapshots (find_sites.py, Wayback CDX)
    istory.json        per-chapter blurbs           (scrape_wiki.py, heroeswiki)

Every value is a URL or a short blurb. No media is copied: images are hot-linked
from the Wayback Machine and video streams from archive.org.

    py build/extras.py
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
HTML = os.path.join(HERE, os.pardir, "index.html")


def load(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        print("  (missing, skipped) %s" % name)
        return {}
    return json.load(open(p, encoding="utf-8"))


def main():
    syn = load("gn_synopses.json")
    imgs = load("gn_wiki.json").get("found", {})
    sites = load("sites.json").get("found", {})
    istory = load("istory.json")

    gn = {}
    for num, rec in syn.items():
        e = {}
        if rec.get("desc"):
            e["d"] = rec["desc"]
        if rec.get("writer"):
            e["by"] = rec["writer"] + (" / " + rec["artist"] if rec.get("artist") else "")
        img = imgs.get(num) or {}
        for src, dst in (("card", "img"), ("cover", "cover"), ("page", "wiki")):
            if img.get(src):
                e[dst] = img[src]
        if e:
            gn[num] = e

    site = {}
    for title, rec in sites.items():
        e = {"url": rec["url"]}
        if rec.get("ts"):
            e["ts"] = rec["ts"][:6]          # YYYYMM is all the label needs
        if rec.get("domain"):
            e["dom"] = rec["domain"]
        if rec.get("note"):
            e["note"] = rec["note"]
        site[title] = e

    out = {"gn": gn, "site": site, "istory": istory}
    blob = json.dumps(out, ensure_ascii=False, separators=(",", ":"))

    html = open(HTML, encoding="utf-8").read()
    pat = re.compile(r'(<script type="application/json" id="extras-data">).*?(</script>)', re.S)
    if not pat.search(html):
        sys.exit('no <script id="extras-data"> block in index.html')
    open(HTML, "w", encoding="utf-8").write(
        pat.sub(lambda m: m.group(1) + blob + m.group(2), html, count=1))

    print("novels   %3d blurbs, %3d title cards, %3d covers"
          % (sum(1 for v in gn.values() if "d" in v),
             sum(1 for v in gn.values() if "img" in v),
             sum(1 for v in gn.values() if "cover" in v)))
    print("sites    %3d linked" % len(site))
    print("istory   %3d chapters" % len(istory))
    print("wrote %.1f KB into index.html" % (len(blob) / 1024))


if __name__ == "__main__":
    main()
