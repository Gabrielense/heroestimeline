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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import season4
from naming import slug

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
    # Season four's codes shift under its merged two-hour premiere, and the page
    # looks every blurb and card up by code. Shift them at the door, so nothing
    # downstream has to know the sheet numbers that season one too high.
    eps = season4.remap_keys(load("ep_synopses.json"))
    epimgs = season4.remap_keys(load("ep_wiki.json").get("found", {}))
    # Cards we hold locally. Hot-linking the Wayback Machine failed ~half of all
    # image requests and took 10-20s when it answered, so a downloaded copy wins
    # whenever we have one; the archive URL stays as the fallback.
    local = load("cards.json")
    # "Amanda's Journey, Part 1 - When Everything Changed": the running title
    # and the subtitle that issue carries are one name, and the sheet only ever
    # held the first half. build/gn_subtitles.py explains where these come from.
    gn_subs = load("gn_subtitles.json").get("subtitles", {})

    # Wikipedia's list stops short of a few dozen issues -- Turning Point, the
    # Titan miniseries -- so gn_links.py asks Heroes Wiki for those directly.
    # Anything it found fills a hole; it never overwrites what we already had.
    extra_gn = load("gn_extra.json").get("found", {})
    for num, rec in extra_gn.items():
        if rec.get("d") and not (syn.get(num) or {}).get("desc"):
            syn.setdefault(num, {})["desc"] = rec["d"]
        if rec.get("card") and not (imgs.get(num) or {}).get("card"):
            imgs.setdefault(num, {})["card"] = rec["card"]
        if rec.get("wiki") and not (imgs.get(num) or {}).get("page"):
            imgs.setdefault(num, {})["page"] = rec["wiki"]

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
        if local.get("gn-" + num):
            e["img"] = local["gn-" + num]
        if gn_subs.get(num):
            e["sub"] = gn_subs[num]
        if e:
            gn[num] = e

    ep = {}
    # The wiki's logline names every thread in the episode; Wikipedia's article
    # is a long plot recap, and trimming one to a line yields only its opening
    # beat. So the logline wins, and Wikipedia fills the gaps.
    for code in sorted(set(eps) | set(epimgs)):
        rec = eps.get(code) or {}
        img = epimgs.get(code) or {}
        e = {}
        if img.get("d"):
            e["d"] = img["d"]
        elif rec.get("d"):
            e["d"] = rec["d"]
        if img.get("card"):
            e["img"] = img["card"]
        if img.get("page"):
            e["wiki"] = img["page"]
        if local.get("ep-" + code):
            e["img"] = local["ep-" + code]
        if e:
            ep[code] = e

    # Webisodes, keyed by the code the timeline uses ("01", "10-11", "32-36").
    # Their subtitles ride along here rather than in the sheet: "Damen Peak" and
    # "A Modest Talent" are one name, and the sheet only ever held the first half.
    web = {}
    for code, rec in load("web_wiki.json").get("found", {}).items():
        e = {}
        for src, dst in (("b", "d"), ("sub", "sub"), ("img", "img"),
                         ("wiki", "wiki")):
            if rec.get(src):
                e[dst] = rec[src]
        if local.get("web-" + code):
            e["img"] = local["web-" + code]
        if e:
            web[code] = e

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

    # Blurbs and pictures for the sites, the Evolutions artefacts and the iStory
    # chapters, merged onto whatever sites.json already knew about each site.
    evo_site = load("evo_site_wiki.json")
    for title, rec in (evo_site.get("site") or {}).items():
        e = site.setdefault(title, {})
        if rec.get("b"):
            e["d"] = rec["b"]
        if rec.get("img"):
            e["img"] = local.get("site-" + slug(title)) or rec["img"]
        if rec.get("wiki"):
            e["wiki"] = rec["wiki"]
    evo = {}
    for title, rec in (evo_site.get("evo") or {}).items():
        e = {}
        if rec.get("b"):
            e["d"] = rec["b"]
        if rec.get("img"):
            e["img"] = local.get("evo-" + slug(title)) or rec["img"]
        if rec.get("wiki"):
            e["wiki"] = rec["wiki"]
        if e:
            evo[title] = e
    # One picture stands for every iStory chapter -- they were text, and the
    # wiki holds no art for them one by one.
    for title, rec in (evo_site.get("istory") or {}).items():
        e = dict(istory.get(title) or {})
        if rec.get("b"):
            e["d"] = rec["b"]
        if rec.get("wiki"):
            e["wiki"] = rec["wiki"]
        if e:
            istory[title] = e

    # The wiki serves whatever thumbnail width the page happened to ask for;
    # an 80px logo is a favicon, not a card. Ask for a card-sized one.
    shared = evo_site.get("istory_img")
    if shared:
        shared = re.sub(r"/\d+px-", "/250px-", shared)

    out = {"gn": gn, "ep": ep, "web": web, "site": site, "istory": istory,
           "evo": evo, "as_sites": evo_site.get("as_sites") or [],
           "istory_img": local.get("istory") or shared}
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
    print("episodes %3d blurbs, %3d title cards"
          % (sum(1 for v in ep.values() if "d" in v),
             sum(1 for v in ep.values() if "img" in v)))
    print("webisode %3d blurbs, %3d title cards, %3d subtitles"
          % (sum(1 for v in web.values() if "d" in v),
             sum(1 for v in web.values() if "img" in v),
             sum(1 for v in web.values() if "sub" in v)))
    print("sites    %3d linked, %3d with a picture" % (len(site),
          sum(1 for v in site.values() if "img" in v)))
    print("evo      %3d artefacts" % len(evo))
    print("istory   %3d chapters" % len(istory))
    print("wrote %.1f KB into index.html" % (len(blob) / 1024))


if __name__ == "__main__":
    main()
