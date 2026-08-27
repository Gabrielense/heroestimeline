# -*- coding: utf-8 -*-
"""Find the graphic novels the wiki knows about and this site does not.

gn_wiki.json was built from Wikipedia's list, which stops short of a handful of
issues -- *Turning Point* among them -- so those have no blurb, no title card
and no link to follow. This asks Heroes Wiki directly, page by page, for the
ones that came back empty, and reports what is still missing afterwards.

    py build/gn_links.py            # fill the gaps
    py build/gn_links.py --audit    # just say what is missing
"""
import io, json, os, re, sys, time, urllib.parse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
HTML = os.path.join(HERE, os.pardir, "index.html")
OUT = os.path.join(DATA, "gn_extra.json")

LIVE = "https://heroeswiki.ddns.net/wiki/"
API = "https://heroeswiki.ddns.net/api.php?action=query&list=search&format=json&srlimit=3&srsearch="
UA = {"User-Agent": "heroes-timeline/1.0 (https://github.com/Gabrielense/heroestimeline)"}
MAX = 320


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return None
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def strip(s):
    s = re.sub(r"(?s)<(script|style|table|sup)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<div class=\"(?:thumb|toc)[^\"]*\".*?</div>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
    s = re.sub(r"\[\d+\]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def trim(text, cap=MAX):
    text = strip(text)
    if len(text) <= cap:
        return text
    cut, out = text[:cap], ""
    for sent in re.split(r"(?<=[.!?]) ", cut):
        if len(out) + len(sent) + 1 > cap:
            break
        out += sent + " "
    return (out or cut).strip()


"""Paragraphs that are furniture rather than a synopsis."""
JUNK = re.compile(r"^(several different covers|the following previews|this "
                  r"article|this page|for the|see also)", re.I)


def is_junk(text):
    """A navbox reads as a long paragraph and is not a synopsis: the run of
    every novel's name, bulleted apart. Nothing real carries four bullets."""
    return (not text or JUNK.match(text) or text.count("•") > 3
            or text.count(" • ") > 1)


def summary(h):
    # This wiki renders headings as <h2 id="Summary">, not the older
    # <span class="mw-headline"> form, and it repeats every id in the contents
    # box -- so anchor on the heading tag itself.
    m = re.search(r'(?s)<h[23] id="(?:Summary|Synopsis)"[^>]*>.*?</h[23]>'
                  r'(.*?)(?=<div class="mw-heading|<h[23] id=|<div id="catlinks")', h)
    if m:
        text = trim(m.group(1))
        if not is_junk(text):
            return text
    for m in re.finditer(r"(?s)<p>(.*?)</p>", h):
        text = trim(m.group(1))
        if len(text) > 60 and not is_junk(text):
            return text
    return ""


def images(h):
    out = []
    for m in re.finditer(r'"(/images/(?:thumb/)?[^"]+?\.(?:jpg|jpeg|png|JPG|PNG))"', h):
        u = "https://heroeswiki.ddns.net" + m.group(1)
        if any(bad in u.lower() for bad in ("crystal", "wikilogo", "button", "icon")):
            continue
        if u not in out:
            out.append(u)
    return out


def page_for(title):
    """The Graphic Novel: page, by name first and by search if that misses."""
    for name in ("Graphic Novel:" + title, title):
        u = LIVE + urllib.parse.quote(name.replace(" ", "_"), safe="_,:!?'()&./")
        h = get(u)
        if h and "noarticletext" not in h:
            return h, u
    raw = get(API + urllib.parse.quote("Graphic Novel " + title))
    if raw:
        try:
            hits = json.loads(raw).get("query", {}).get("search", [])
        except ValueError:
            hits = []
        for hit in hits:
            if not hit["title"].startswith("Graphic Novel:"):
                continue
            u = LIVE + urllib.parse.quote(hit["title"].replace(" ", "_"),
                                          safe="_,:!?'()&./")
            h = get(u)
            if h:
                return h, u
    return None, None


# Heroes Wiki files the Titan miniseries as stubs -- the Summary heading is
# there and empty -- so there is nothing to collect for those ten issues. What
# is written down instead is the series each belongs to, which is true of every
# part and is marked as such rather than passed off as a per-issue synopsis.
SERIES = [
    (re.compile(r"^Vengeance, Part", re.I),
     "From Heroes: Vengeance, Titan Comics' five-issue Heroes Reborn tie-in by "
     "Seamus Kevin Fahey and Zach Craley, drawn by Rubine, with a foreword by "
     "Tim Kring. It follows Oscar Gutierrez -- Carlos's older brother and the "
     "first El Vengador -- and how his story reaches Heroes Reborn."),
    (re.compile(r"^Godsend, Part", re.I),
     "From Heroes: Godsend, Titan Comics' five-issue prequel by Joey Falco and "
     "Roy Allan Martinez. It follows Farah Nazan in New York in 2001, coming to "
     "terms with her camouflage and invisibility in the wake of the attacks on "
     "the World Trade Center."),
]


def series_blurb(title):
    for pattern, text in SERIES:
        if pattern.match(title):
            return text
    return None


def main():
    html = io.open(HTML, encoding="utf-8").read()
    data = json.loads(re.search(
        r'<script type="application/json" id="timeline-data">(.*?)</script>',
        html, re.S).group(1))
    known = json.load(io.open(os.path.join(DATA, "gn_wiki.json"),
                              encoding="utf-8")).get("found", {})
    syn = json.load(io.open(os.path.join(DATA, "gn_synopses.json"),
                            encoding="utf-8"))

    titles = {}
    for entry in data["entries"]:
        for item in (entry.get("c") or {}).get("gn", []):
            if item.get("c"):
                titles[item["c"]] = item["t"]

    gaps = []
    for code, title in titles.items():
        has_img = bool((known.get(code) or {}).get("card"))
        has_blurb = bool((syn.get(code) or {}).get("desc"))
        if not (has_img and has_blurb):
            gaps.append((code, title, has_img, has_blurb))
    gaps.sort(key=lambda g: int(re.sub(r"\D", "", g[0]) or 0))

    print("%d novels, %d with something missing" % (len(titles), len(gaps)))
    if "--audit" in sys.argv:
        for code, title, img, blurb in gaps:
            print("  #%-6s %-46s card=%-5s blurb=%s" % (code, title[:46], img, blurb))
        return

    found, still = {}, []
    for n, (code, title, has_img, has_blurb) in enumerate(gaps, 1):
        h, u = page_for(title)
        if not h:
            still.append({"c": code, "t": title})
            print("  %3d/%d MISS  #%-6s %s" % (n, len(gaps), code, title))
            continue
        rec = {"wiki": u}
        if not has_blurb:
            b = summary(h) or series_blurb(title)
            if b:
                rec["d"] = b
        if not has_img:
            imgs = images(h)
            card = next((i for i in imgs if "_title" in i or "title" in i.lower()), None)
            if card or imgs:
                rec["card"] = card or imgs[0]
        found[code] = rec
        print("  %3d/%d ok    #%-6s blurb=%-5s card=%-5s %s"
              % (n, len(gaps), code, "d" in rec, "card" in rec, title[:40]))
        time.sleep(1)

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(
        {"found": found, "missing": still}, ensure_ascii=False, indent=1))
    print("\n%d filled, %d still missing -> %s" % (len(found), len(still), OUT))


if __name__ == "__main__":
    main()
