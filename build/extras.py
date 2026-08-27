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


CARDS = os.path.join(HERE, os.pardir, "assets", "cards")


def on_disk(name):
    """A card someone dropped into assets/cards by hand, without going through
    fetch_cards. Some art exists only as a screenshot off a site that will not
    give a URL up -- saving the file under the right name is the whole of it."""
    for ext in (".jpg", ".jpeg", ".png"):
        if os.path.exists(os.path.join(CARDS, name + ext)):
            return "assets/cards/" + name + ext
    return None


def tidy(text):
    """Close the gaps that dropping a tag leaves behind.

    A blurb assembled from wiki HTML ends up with a space wherever a link sat,
    which lands in front of the punctuation that followed it: "Claire 's",
    "video .", "\" Where Are The Heroes?". Cheaper to repair here, once, than to
    re-crawl every collector when one of them gets it wrong.
    """
    if not text:
        return text
    # a non-breaking space between every word of a title survives as &#160;
    # unless it is decoded here -- the wiki uses them to stop titles wrapping
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    for entity, char in (("&nbsp;", " "), ("&amp;", "&"), ("&quot;", '"'),
                         ("&#039;", "'"), ("&lt;", "<"), ("&gt;", ">")):
        text = text.replace(entity, char)
    text = text.replace(" ", " ")
    text = re.sub(r"\s+([.,;:!?%)])", r"\1", text)
    text = re.sub(r"\s+('s|'re|'ve|'ll|'d|n't)\b", r"\1", text)
    text = re.sub(r"([(“])\s+", r"\1", text)
    text = re.sub(r'(^|\s)"\s+', r'\1"', text)
    text = re.sub(r'\s+"(\s|$|[.,])', r'"\1', text)
    return re.sub(r"\s{2,}", " ", text).strip()


def load(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        print("  (missing, skipped) %s" % name)
        return {}
    return json.load(open(p, encoding="utf-8"))


_TITLES = {}


def timeline_titles(key):
    """Every title the timeline holds in one column, read back out of the data
    block sync.py wrote. Used to spread one blurb over a run of entries."""
    if not _TITLES:
        html = open(HTML, encoding="utf-8").read()
        m = re.search(r'id="timeline-data">(.*?)</script>', html, re.S)
        data = json.loads(m.group(1)) if m else {"entries": []}
        for entry in data["entries"]:
            for col, items in (entry.get("c") or {}).items():
                _TITLES.setdefault(col, []).extend(it["t"] for it in items)
    return _TITLES.get(key, [])


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
    # where the archive still holds NBC's own PDF of an issue, and how big it is
    gn_pdf = load("gn_pdfs.json")

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
        if gn_pdf.get(num):
            e["pdf"] = gn_pdf[num]
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
    # istory.json is keyed by chapter code -- "Cap. 101" -- and the page looks
    # a chapter up by code first, so each of the fifty-eight gets its own
    # synopsis and its volume's own art. The volume-level entries below stay as
    # a fallback for any row whose code we cannot place.
    for code, rec in list(istory.items()):
        card = rec.get("vol") and local.get("istory-" + slug(rec["vol"]))
        if card:
            rec["img"] = card
    for title, rec in (evo_site.get("istory") or {}).items():
        e = dict(istory.get(title) or {})
        if rec.get("b"):
            e["d"] = rec["b"]
        if rec.get("wiki"):
            e["wiki"] = rec["wiki"]
        if e:
            istory[title] = e

    # Cover art for the boxes, books, magazines and soundtracks, and stills for
    # the Reborn episodes that never got a title card.
    art = load("phys_cards.json")
    phys = {}
    for title, rec in (art.get("phys") or {}).items():
        e = {"img": local.get("phys-" + slug(title)) or rec["img"]}
        if rec.get("src"):
            e["wiki"] = rec["src"]
        phys[title] = e
    # The twelve issues of the magazine, whose per-issue pages are all redirects
    # to one article that names no cover -- so phys_cards found the same picture
    # twelve times. build/magazine.py digs the real covers out of the wiki's file
    # namespace and reads the article's contents list for what was in each.
    # It wins over phys_cards outright; the "serve our own" pass below swaps in
    # the downloaded copy, the same as for every other picture here.
    for title, rec in load("magazine.json").items():
        phys.setdefault(title, {}).update(rec)

    for code, rec in (art.get("reborn_eps") or {}).items():
        e = ep.setdefault(code, {})
        if not e.get("img"):
            e["img"] = local.get("ep-" + code) or rec["img"]
        if rec.get("src") and not e.get("wiki"):
            e["wiki"] = rec["src"]

    # The HeroTruther videos exist only as the wiki's account of them, so that
    # account is the blurb. The channel itself is gone; herotruther.json holds a
    # capture of the real one from the campaign, which is what the entries link.
    ht = load("herotruther.json")
    for video in ht.get("videos", []):
        title = "HeroTruther: " + video["t"]
        e = {}
        if video.get("b"):
            e["d"] = video["b"]
        card = local.get("evo-" + slug(title)) or on_disk("evo-" + slug(title))
        if card:
            e["img"] = card
        if ht.get("channel_archive"):
            e["site"] = ht["channel_archive"]
            e["note"] = ht.get("channel_note")
        if video.get("wiki") or ht.get("wiki"):
            e["wiki"] = video.get("wiki") or ht["wiki"]
        if e:
            evo[title] = e

    # Everything that is not a release of the story itself: the adverts, the
    # tour, the fan club, the programmes about the show. Keyed by title.
    misc = {}

    # Behind the scenes: the 46 Heroes Unmasked episodes, Inside Heroes, the
    # disc featurettes and the commentaries. Keyed by title.
    #
    # Thirteen of the Unmasked episodes have their intertitle on the wiki and
    # thirty-three do not; rather than leave those panels blank, the series'
    # own title card stands in, the way one picture stands for every iStory
    # chapter.
    bts = {}
    unm = load("unmasked.json")
    series_card = local.get("bts-unmasked") or unm.get("series_img")
    for title, rec in (unm.get("found") or {}).items():
        e = {}
        if rec.get("d"):
            e["d"] = rec["d"]
        if rec.get("wiki"):
            e["wiki"] = rec["wiki"]
        e["img"] = rec.get("img") or series_card
        if not e["img"]:
            del e["img"]
        # These sit beside the episode they are about rather than on their own
        # UK date -- the footer says why -- so the real date has to be in the
        # blurb, or it is nowhere.
        if rec.get("aired"):
            e["d"] = (e.get("d", "").rstrip() + " ").lstrip() + \
                     "First shown on BBC Two, %s." % rec["aired"]
        bts[title] = e

    # Written by hand, for what no collector can reach. Merged last, so it wins.
    hand = load("hand_extras.json")
    for group, target in (("gn", gn), ("ep", ep), ("web", web), ("evo", evo),
                          ("bts", bts), ("site", site), ("istory", istory),
                          ("phys", phys), ("misc", misc)):
        for key, rec in (hand.get(group) or {}).items():
            target.setdefault(key, {}).update(rec)

    # One blurb across a whole run of entries -- fifteen weeks of the radio
    # show, six of The Post Show -- rather than the same paragraph written out
    # fifteen times. An entry with a blurb of its own keeps it.
    by_group = {"gn": gn, "ep": ep, "web": web, "evo": evo, "bts": bts,
                "site": site, "istory": istory, "phys": phys, "misc": misc}
    spread = 0
    for rule in (load("manual_extras.json").get("series") or []):
        target = by_group.get(rule.get("g"))
        if target is None:
            continue
        pat = re.compile(rule["re"])
        fields = {k: v for k, v in rule.items() if k not in ("g", "re", "card")}
        # one picture for the whole run, fetched once under the rule's own name
        if rule.get("card") and local.get(rule["card"]):
            fields["img"] = local[rule["card"]]
        for title in timeline_titles(rule["g"]):
            if not pat.search(title):
                continue
            rec = target.setdefault(title, {})
            for k, v in fields.items():
                rec.setdefault(k, v)
            spread += 1
    if spread:
        print("series   %3d entries covered by a shared blurb" % spread)

    # A disc extra has no art of its own, so it borrows the cover of the box it
    # came in -- named by make_additions.py as `artof`, resolved here because
    # this is where the physical releases' pictures are known.
    borrowed = 0
    for table in (bts, evo):
        for rec in table.values():
            box = rec.pop("artof", None)
            if box and not rec.get("img"):
                art = (phys.get(box) or {}).get("img")
                if art:
                    rec["img"] = art
                    borrowed += 1
    if borrowed:
        print("discs    %3d extras showing the cover of the set they are on"
              % borrowed)

    # Where fetch_cards.py has copied a picture down, serve our own rather than
    # someone's hobby server. Only the title-keyed groups: the rest are handled
    # where they are built, keyed by code.
    for group, table in (("evo", evo), ("site", site), ("phys", phys),
                         ("misc", misc), ("bts", bts)):
        for title, rec in table.items():
            if str(rec.get("img", "")).startswith("http"):
                own = local.get("%s-%s" % (group, slug(title)))
                if own:
                    rec["img"] = own

    # The wiki serves whatever thumbnail width the page happened to ask for;
    # an 80px logo is a favicon, not a card. Ask for a card-sized one.
    shared = evo_site.get("istory_img")
    if shared:
        shared = re.sub(r"/\d+px-", "/250px-", shared)

    out = {"gn": gn, "ep": ep, "web": web, "site": site, "istory": istory,
           "evo": evo, "bts": bts, "phys": phys, "misc": misc,
           "as_sites": evo_site.get("as_sites") or [],
           "istory_img": local.get("istory") or shared}

    # one pass over every blurb, whichever collector wrote it
    for group in ("gn", "ep", "web", "site", "istory", "evo", "bts", "phys",
                  "misc"):
        for rec in out[group].values():
            for field in ("d", "by", "note", "sub"):
                if rec.get(field):
                    rec[field] = tidy(rec[field])
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
    print("bts      %3d behind the scenes, %3d with a picture"
          % (len(bts), sum(1 for v in bts.values() if "img" in v)))
    print("physical %3d with cover art" % len(phys))
    print("misc     %3d real-world releases" % len(misc))
    print("istory   %3d chapters" % len(istory))
    print("wrote %.1f KB into index.html" % (len(blob) / 1024))


if __name__ == "__main__":
    main()
