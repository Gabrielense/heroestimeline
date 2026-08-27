# -*- coding: utf-8 -*-
"""Cover art for the physical releases, and stills for the Reborn episodes.

The thirty-two boxes, books, magazines and soundtracks had nothing to show for
themselves, and four Heroes Reborn episodes never got a title card. Heroes Wiki
has art for most of it -- filed under names that rarely match how the sheet
writes them, so this leans on the wiki's own search.

Amazon is deliberately not used: those URLs rot and block hot-linking.

    py build/phys_cards.py
    py build/phys_cards.py --probe "Saving Charlie (book)"
"""
import io, json, os, re, sys, time, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scrape_evo_sites import get, page, images, pick, search_page

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
HTML = os.path.join(HERE, os.pardir, "index.html")
OUT = os.path.join(DATA, "phys_cards.json")

# The sheet's wording against the wiki's. Only where search cannot get there.
ALIASES = {
    "Season 1 Blu-ray": "Heroes: The Complete First Season",
    # Without these, strip_notes() asks for a page that does not exist, search
    # answers with season one -- the first hit for any of them -- and seasons
    # two and three end up wearing the season one box.
    "Heroes: The Complete Second Season (DVD/Blu-ray)":
        "Heroes: The Complete Second Season (DVD)",
    "Heroes: The Complete Third Season (DVD/Blu-ray)":
        "Heroes: The Complete Third Season (DVD)",
    "Heroes: The Complete Fourth Season (DVD/Blu-ray)":
        "Heroes: The Complete Fourth Season (DVD)",
    "Heroes Original Soundtrack": "Heroes Original Soundtrack",
    "Heroes: Original Score from the Television Series": "Heroes: Original Score",
    "Saving Charlie (book)": "Saving Charlie",
    "Heroes Revealed book": "Heroes Revealed",
    "Heroes Vol. 1: Vengeance Vol.1 (issues #174-#178)": "Heroes: Vengeance",
    "Heroes Vol. 2: Godsend Vol.2 (issues #179-183)": "Heroes: Godsend",
    "Heroes: Omnibus (issues #001-085)": "Heroes: Omnibus",
    "Heroes, Volume 1 (Issues #001-#034)": "Heroes: Volume One",
    "Heroes, Volume 2 (Issues #035-#080)": "Heroes: Volume Two",
}

# what a cover looks like, roughly, versus a screencap or a logo
PREFER = ("cover", "dvd", "bluray", "blu-ray", "boxart", "box", "magazine",
          "soundtrack", "book", "volume", "omnibus")


def strip_notes(title):
    """"Heroes: The Complete Second Season (DVD/Blu-ray)" -> the name a wiki
    page would actually use."""
    t = re.sub(r"\((?:DVD|Blu-ray|book|Paperback|issues?|Issues?)[^)]*\)", "", title)
    t = re.sub(r"\(.*?\)", "", t)
    return re.sub(r"\s+", " ", t).strip(" -–—")


def art_for(title):
    for name in (ALIASES.get(title), title, strip_notes(title)):
        if not name:
            continue
        h, u = page(name)
        if h:
            img = pick(images(h, u), *PREFER)
            if img:
                return img, u
    found = search_page(strip_notes(title))
    if found:
        h, u = page(found)
        if h:
            img = pick(images(h, u), *PREFER)
            if img:
                return img, u
    return None, None


def main():
    if "--probe" in sys.argv:
        name = sys.argv[sys.argv.index("--probe") + 1]
        img, u = art_for(name)
        print("PAGE:", u, "\nIMG:", img)
        return

    # build/magazine.py owns these. The wiki's per-issue pages are redirects to
    # one article whose infobox is a cast panel, so search here finds the same
    # picture for all twelve, and the real covers are files no article links.
    skip = re.compile(r"Official Magazine")

    html = io.open(HTML, encoding="utf-8").read()
    data = json.loads(re.search(
        r'<script type="application/json" id="timeline-data">(.*?)</script>',
        html, re.S).group(1))
    extras = json.loads(re.search(
        r'<script type="application/json" id="extras-data">(.*?)</script>',
        html, re.S).group(1))

    phys, reborn = [], []
    for entry in data["entries"]:
        for item in (entry.get("c") or {}).get("phys", []):
            phys.append(item["t"])
        for item in (entry.get("c") or {}).get("ep", []):
            code = item.get("c") or ""
            if code.startswith("HR") and not (extras.get("ep", {}).get(code) or {}).get("img"):
                reborn.append((code, item["t"]))

    out = {"phys": {}, "reborn_eps": {}, "missing": []}

    print("physical releases: %d" % len(phys))
    for n, title in enumerate(sorted(set(phys)), 1):
        if skip.search(title):
            continue
        img, u = art_for(title)
        if img:
            out["phys"][title] = {"img": img, "src": u}
        else:
            out["missing"].append(title)
        print("  %2d/%d %-5s %s" % (n, len(set(phys)), bool(img), title[:52]))
        time.sleep(1)

    print("\nReborn episodes without a card: %d" % len(reborn))
    for code, title in reborn:
        h, u = page("Episode:" + title)
        img = pick(images(h, u), "title", "episodetitle", "promo") if h else None
        if img:
            out["reborn_eps"][code] = {"img": img, "src": u}
        else:
            out["missing"].append(code)
        print("  %-8s %-5s %s" % (code, bool(img), title[:40]))
        time.sleep(1)

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print("\n%d covers, %d stills, %d not found -> %s"
          % (len(out["phys"]), len(out["reborn_eps"]), len(out["missing"]), OUT))


if __name__ == "__main__":
    main()
