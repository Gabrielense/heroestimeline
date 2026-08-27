# -*- coding: utf-8 -*-
"""Collect blurbs + images for the Heroes Evolutions / promo-site items.

Three groups, matching how index.html looks each one up:

    site    the 19 entries in extras-data's `site` map, plus the three `evo`
            items that are really websites (Claire's/Zach's MySpace, Hiro's Blog)
    evo     the remaining named `evo` artefacts -- games, videos, SMS/e-mail
            campaigns, in-fiction blogs -- keyed by title
    istory  the iStory chapters, keyed by their chapter code ("Cap. 101"),
            because that is the key index.html uses (EXTRAS.istory[it.c]).
            They share one title card, given once as top-level "istory_img".

Sources, in order: the live heroeswiki mirror at heroeswiki.ddns.net, then the
2020 Wayback snapshot of heroeswiki.com. Pages already in build/data/wikicache/
are reused; new fetches land there under the same filename scheme the episode
scraper uses.

    py build/scrape_evo_sites.py            # writes build/data/evo_site_wiki.json
    py build/scrape_evo_sites.py --probe X  # dump one page's summary, for tuning
"""
import html as htmlmod
import io, json, os, re, sys, time, urllib.parse, urllib.request, urllib.error

try:
    sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
except (AttributeError, TypeError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CACHE = os.path.join(DATA, "wikicache")
OUT = os.path.join(DATA, "evo_site_wiki.json")
HTML = os.path.join(HERE, os.pardir, "index.html")

LIVE = "https://heroeswiki.ddns.net/wiki/"
TS = "20200514144559"
ARCH = "https://web.archive.org/web/%s/http://heroeswiki.com/" % TS
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "heroes-timeline/1.0 (fan timeline; contact via github)"}
MAX = 320


def cache_path(url):
    return os.path.join(CACHE, re.sub(r"\W+", "_", url)[-120:] + ".html")


def get(url, tries=3):
    os.makedirs(CACHE, exist_ok=True)
    path = cache_path(url)
    if os.path.exists(path):
        return open(path, encoding="utf-8", errors="replace").read()
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read().decode("utf-8", "replace")
            open(path, "w", encoding="utf-8").write(body)
            time.sleep(1.0)
            return body
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return None
            time.sleep(4 * (i + 1))
        except Exception:
            time.sleep(4 * (i + 1))
    return None


def page(name):
    """try the live mirror, fall back to the Wayback copy; returns (html, url)"""
    quoted = urllib.parse.quote(name, safe="_,:!?'()&./")
    for base in (LIVE, ARCH):
        h = get(base + quoted)
        if h and "There is currently no text in this page" not in h \
              and "Wayback Machine has not archived" not in h:
            # a live-mirror miss still returns 200 with a "no text" notice
            if 'noarticletext' in h and base is LIVE:
                continue
            return h, base + quoted
    return None, None


def strip(s):
    s = re.sub(r"(?s)<(script|style|table|sup)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<div class=\"(?:thumb|toc)[^\"]*\".*?</div>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = htmlmod.unescape(s)
    s = re.sub(r"\[\d+\]", "", s)
    return re.sub(r"\s+", " ", s).replace(" ,", ",").replace(" .", ".").strip()


def trim(text, limit=MAX):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    out = ""
    for sent in re.findall(r"[^.!?]*[.!?]", text):
        if len(out) + len(sent) > limit:
            break
        out += sent
    out = out.strip()
    if out:
        return out
    cut = text[:limit]
    return cut[:cut.rfind(" ")].rstrip(",;:") + "..."


def lead(h, limit=MAX):
    """the article's opening prose, before the first section heading"""
    body = re.search(r'(?s)<div[^>]+class="[^"]*mw-parser-output[^"]*"(.*)', h)
    body = body.group(1) if body else h
    body = re.split(r'(?s)<h2', body)[0]
    paras = re.findall(r"(?s)<p\b[^>]*>(.*?)</p>", body)
    buf = []
    for p in paras:
        t = strip(p)
        if len(t) < 25:
            continue
        buf.append(t)
        if len(" ".join(buf)) > limit:
            break
    return trim(" ".join(buf), limit)


def section(h, *ids):
    """text of a named section, e.g. Summary / Synopsis / Plot"""
    for i in ids:
        m = re.search(r'(?s)id="%s"(.*?)(?:<h[12]\b|<div class="printfooter)' %
                      re.escape(i), h)
        if not m:
            continue
        chunk = re.sub(r"(?s)^.*?</h[23]>", "", m.group(1), count=1)
        t = strip(chunk)
        if len(t) > 25:
            return t
    return ""


IMG_LIVE = re.compile(r'"(/images/(?:thumb/)?[^"]+?\.(?:jpg|JPG|jpeg|png|PNG|gif|GIF))"')
IMG_ARCH = re.compile(r'"(/web/\d+im_/https?://heroeswiki\.com/images/(?:thumb/)?'
                      r'[^"]+?\.(?:jpg|JPG|jpeg|png|PNG|gif|GIF))"')

SKIP_IMG = ("crystal", "wiki.png", "wikilogo", "button", "icon", "spoiler",
            "nuvola", "ambox", "poweredby", "mediawiki", "favicon", "bullet",
            "arrow", "magnify", "edit.png", "commons", "stub", "disambig")


def images(h, url):
    """every content image on the page, biggest-looking first, as absolute URLs"""
    out = []
    if url and "web.archive.org" in url:
        for i in IMG_ARCH.findall(h):
            out.append("https://web.archive.org" + i)
    for i in IMG_LIVE.findall(h):
        out.append("https://heroeswiki.ddns.net" + i)
    seen, keep = set(), []
    for u in out:
        if any(s in u.lower() for s in SKIP_IMG):
            continue
        if u in seen:
            continue
        seen.add(u)
        keep.append(u)
    return keep


def pick(imgs, *prefer):
    for want in prefer:
        for u in imgs:
            if want.lower() in u.lower():
                return u
    return imgs[0] if imgs else None


# --- finding the right page --------------------------------------------------
# The sheet's wording is not the wiki's: "Hana's SMS" is filed under "Hana's
# messages", "Rebel's SMS/emails" under "Rebel's messages". Rather than keep a
# hand-written map in step with 100-odd titles, ask the wiki's own search and
# take the top hit -- the mirror runs MediaWiki, so api.php answers.
SEARCH = "https://heroeswiki.ddns.net/api.php?action=query&list=search&format=json&srlimit=3&srsearch="

# where search alone lands on the wrong page, or would waste a request
ALIASES = {
    "Hana's SMS":                            "Hana's messages",
    "Hana's emails":                         "Hana's messages",
    "Hiro's SMS":                            "Hiro's messages",
    "Rebel's SMS/emails":                    "Rebel's messages",
    "Bridget's messages":                    "Bridget Bailey's messages",
    "Pinehearst & Primatech SMS and emails": "Pinehearst and Primatech messages",
    "Evs Dropper's blog":                    "Evs Dropper's blog",
    "Claire's MySpace":                      "Claire Bennet's MySpace",
    "Zach's MySpace":                        "Zach's MySpace",
    "Hiro's Blog":                           "Hiro's blog",
}


def search_page(title):
    """Top search hit for a title, or None."""
    try:
        raw = get(SEARCH + urllib.parse.quote(title))
        if not raw:
            return None
        hits = json.loads(raw).get("query", {}).get("search", [])
        return hits[0]["title"] if hits else None
    except Exception:
        return None


def resolve(title):
    """(html, url, page name) for a timeline title, trying the alias, the title
    itself, then whatever the wiki's search thinks it is."""
    tried = []
    for name in (ALIASES.get(title), title):
        if not name or name in tried:
            continue
        tried.append(name)
        h, u = page(name)
        if h:
            return h, u, name
    found = search_page(title)
    if found and found not in tried:
        h, u = page(found)
        if h:
            return h, u, found
    return None, None, None


def blurb_for(h):
    """The summary section reads better than the lead for these -- the lead is
    often one line of navigation -- so prefer it and fall back."""
    return (section(h, "Summary", "Synopsis", "Overview", "Description",
                    "About", "Plot") or lead(h) or "").strip()


def collect(titles, want_image=True, label=""):
    out, missing = {}, []
    for n, title in enumerate(sorted(titles), 1):
        h, u, name = resolve(title)
        if not h:
            missing.append(title)
            print("  %3d/%d MISS  %s" % (n, len(titles), title))
            continue
        rec = {}
        b = blurb_for(h)
        if b:
            rec["b"] = trim(b)
        if want_image:
            img = pick(images(h, u), "title", "logo", "screen", "cap")
            if img:
                rec["img"] = img
        rec["wiki"] = u
        if rec.get("b") or rec.get("img"):
            out[title] = rec
        else:
            missing.append(title)
        print("  %3d/%d ok    %-42s b=%-4s img=%-5s %s"
              % (n, len(titles), title[:42], len(rec.get("b", "")),
                 bool(rec.get("img")), name))
        time.sleep(1)
    print("%s: %d found, %d missing" % (label, len(out), len(missing)))
    return out, missing


def read_block(html, block_id):
    m = re.search(r'<script type="application/json" id="%s">(.*?)</script>'
                  % block_id, html, re.S)
    return json.loads(m.group(1)) if m else {}


def main():
    if "--probe" in sys.argv:
        name = sys.argv[sys.argv.index("--probe") + 1]
        h, u, got = resolve(name)
        if not h:
            print("MISS", name)
            return
        print("URL:", u, "\nPAGE:", got)
        print("BLURB:", trim(blurb_for(h)))
        for i in images(h, u)[:12]:
            print("IMG:", i)
        return

    html = io.open(HTML, encoding="utf-8").read()
    data = read_block(html, "timeline-data")
    extras = read_block(html, "extras-data")

    # Three sites the sheet files under Evolutions. They are websites, and the
    # page should treat them as such.
    AS_SITES = ["Claire's MySpace", "Zach's MySpace", "Hiro's Blog"]

    evo_titles, istory_titles = set(), set()
    for entry in data.get("entries", []):
        for item in (entry.get("c") or {}).get("evo", []):
            if item["t"] in AS_SITES:
                continue
            (istory_titles if item.get("c") else evo_titles).add(item["t"])

    site_titles = set(extras.get("site", {})) | set(AS_SITES)

    print("sites %d | evolutions %d | istory %d"
          % (len(site_titles), len(evo_titles), len(istory_titles)))

    site, miss_site = collect(site_titles, True, "sites")
    evo, miss_evo = collect(evo_titles, True, "evolutions")
    istory, miss_ist = collect(istory_titles, False, "istory")

    # One image stands for every iStory chapter: they were text, and the wiki
    # has no art for them individually.
    shared = None
    for title in ("Heroes Evolutions", "iStory"):
        h, u, _ = resolve(title)
        if h:
            shared = pick(images(h, u), "logo", "title", "evolutions")
            if shared:
                break

    out = {"istory_img": shared, "site": site, "evo": evo, "istory": istory,
           "as_sites": AS_SITES,
           "missing": sorted(miss_site + miss_evo + miss_ist)}
    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1))
    print("\nwrote %s" % OUT)
    print("shared iStory image: %s" % (shared or "NONE"))


if __name__ == "__main__":
    main()
