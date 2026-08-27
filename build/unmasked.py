# -*- coding: utf-8 -*-
"""Blurbs, UK air dates and intertitles for the 46 Heroes Unmasked episodes.

One Heroes Wiki article carries all of them, an <h3> each under a season <h2>,
so this reads that page rather than 46 pages. The gallery at the foot has the
intertitle card for a handful of episodes; those are matched back by title.

The timeline calls them "Unmasked: A New Dawn (UK premiere date 7/25/2007)" --
sync.py adds the prefix, and the sheet carries the parenthetical -- so the keys
here are written the same way, taken from index.html itself rather than guessed.
Run sync.py first.

    py build/unmasked.py            # writes build/data/unmasked.json

Requires nothing but the standard library. Uses the fetcher and the page cache
in scrape_evo_sites, so a second run costs nothing.
"""
import io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_evo_sites as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "unmasked.json")
HTML = os.path.join(HERE, os.pardir, "index.html")

# The wiki spells four of them differently from the sheet, and knows nothing
# about the two the BBC ran as specials rather than as numbered episodes.
SPELLING = {
    "the h.r.g. files": "the h.r.g. file",
    "opening pandora's box": "opening pandora's box",
    "new heroes on the block": "new heroes on the block",
    "heroes by design": "heroes by design",
}


def key(title):
    """Loose enough to survive the sheet's capitals and its parentheses."""
    t = re.sub(r"^Unmasked:\s*", "", title)
    t = re.sub(r"\s*\(.*?\)\s*$", "", t)
    t = t.lower().strip()
    return SPELLING.get(t, t)


def sections(html):
    """(heading, inner html) for every <h3> on the page, in order."""
    parts = re.split(r'<h3\b[^>]*>(.*?)</h3>', html, flags=re.S)
    out = []
    for i in range(1, len(parts) - 1, 2):
        head = S.strip(parts[i])
        body = re.split(r'<h[12]\b', parts[i + 1], maxsplit=1)[0]
        out.append((head, body))
    return out


AIRED = re.compile(r"Aired\s+(.{4,24}?\d{4})\b")


def gallery(html):
    """The intertitle cards at the foot, keyed by the title in their caption."""
    found = {}
    tail = html.split('id="Gallery"', 1)
    if len(tail) < 2:
        return found
    # One <li> per picture, and the caption rides in the img's alt -- which sits
    # *before* the src. Pairing across the whole block rather than inside one
    # box hands every picture the next box's caption.
    for box in re.split(r'<li class="gallerybox"', tail[1])[1:]:
        img = re.search(r'src="(/images/[^"]+?\.(?:jpg|JPG|jpeg|png|PNG))"', box)
        cap = re.search(r'<div class="gallerytext">(.*?)</div>', box, re.S)
        if not (img and cap):
            continue
        name = S.strip(cap.group(1))
        name = re.sub(r'\s*intertitle\s*$', "", name).strip().strip('"').strip()
        if name:
            found[name.lower()] = "https://heroeswiki.ddns.net" + img.group(1)
    return found


def full_size(url):
    """The mirror only serves the thumbnail widths that already exist on disk --
    asking it for a 250px copy of a 120px thumb is a 404 -- so take the
    original, which for these screen-caps is small anyway."""
    return re.sub(r"/images/thumb/(.+?)/[^/]+$", r"/images/\1", url)


def timeline_titles():
    html = io.open(HTML, encoding="utf-8").read()
    data = json.loads(re.search(r'id="timeline-data">(.*?)</script>',
                                html, re.S).group(1))
    out = []
    for e in data["entries"]:
        for it in (e.get("c") or {}).get("bts", []):
            if it["t"].startswith("Unmasked: "):
                out.append(it["t"])
    return out


def main():
    html, url = S.page("Heroes Unmasked")
    if not html:
        sys.exit("could not read the Heroes Unmasked article")

    art = gallery(html)
    by_key = {}
    for head, body in sections(html):
        text = S.strip(body)
        aired = AIRED.search(text)
        text = AIRED.sub("", text, count=1).strip()
        # "This episode focuses on Claire" reads as a caption once it is sitting
        # under the title it describes; the site's other blurbs start on the verb
        text = re.sub(r"^(?:In this episode,\s*|This episode\s+)", "", text)
        text = text[:1].upper() + text[1:] if text else text
        rec = {"d": S.trim(text, 420), "wiki": url}
        if aired:
            rec["aired"] = aired.group(1).strip()
        pic = art.get(head.strip().lower())
        if pic:
            rec["img"] = full_size(pic)
        by_key[key(head)] = rec

    out, missing = {}, []
    for title in timeline_titles():
        rec = by_key.get(key(title))
        if rec:
            out[title] = dict(rec)
        else:
            missing.append(title)

    # Thirty-three of them have no intertitle on the wiki. Rather than leave
    # those panels blank, the series' own title card stands in, the way one
    # picture stands for all the iStory chapters.
    logo = S.pick(S.images(html, url), "heroes_unmasked")

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps({"found": out, "missing": missing, "wiki": url,
                    "series_img": full_size(logo) if logo else None},
                   ensure_ascii=False, indent=1))
    print("%d of %d Unmasked episodes described, %d with an intertitle"
          % (len(out), len(out) + len(missing),
             sum(1 for v in out.values() if v.get("img"))))
    for m in missing:
        print("  no article section: %s" % m)
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
