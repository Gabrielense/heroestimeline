# -*- coding: utf-8 -*-
"""Collect each webisode's blurb and title card from the Heroes Wiki.

Same reasoning as scrape_episodes.py: Heroes Wiki's "Summary" section is the
NBC-style logline -- a couple of bullets naming every thread in the short --
which is the register the episode and graphic novel blurbs already have.

Webisodes differ from episodes in three ways worth spelling out:

  * the sheet groups some parts under one code ("10-11" is Hard Knox 1 & 2,
    "32-36" is Dark Matters 2 through 6), while the wiki keeps one page per
    part, so a code's blurb is built from every part it covers;
  * most carry a SUBTITLE under the title in the infobox ("A Modest Talent"),
    which the episodes never do;
  * only some have a "Webisode<N>title.jpg" card. Where there is none, the
    infobox still carries a still from the short, which is used instead.

Pages come from the live mirror first and fall back to the Wayback snapshot
the episode scraper uses.

    py build/scrape_webisodes.py            # writes build/data/web_wiki.json
    py build/scrape_webisodes.py --retry    # only re-attempt previous misses
"""
import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error

try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CACHE = os.path.join(DATA, "wikicache")
OUT = os.path.join(DATA, "web_wiki.json")

LIVE = "https://heroeswiki.ddns.net/wiki/"
LIVE_ROOT = "https://heroeswiki.ddns.net"
TS = "20200514144559"
WAYBACK = "https://web.archive.org/web/%s/http://heroeswiki.com/" % TS
UA = {"User-Agent": "heroes-timeline/1.0 (fan timeline; contact via github)"}
MAX = 320

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}

# live-mirror images; the Wayback copies keep the /web/...im_/ prefix instead
LIVE_IMG = re.compile(r'<img src="(/images/[^"]+?\.(?:jpg|JPG|jpeg|png|PNG))"')
WB_IMG = re.compile(r'"(/web/\d+im_/https?://heroeswiki\.com/images/(?:thumb/)?[^"]+?'
                    r'\.(?:jpg|JPG|jpeg|png|PNG))"')


def get(url, tries=4):
    """fetch with the episode scraper's cache-file convention"""
    os.makedirs(CACHE, exist_ok=True)
    key = re.sub(r"\W+", "_", url)[-120:] + ".html"
    path = os.path.join(CACHE, key)
    if os.path.exists(path):
        return open(path, encoding="utf-8", errors="replace").read()
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                body = r.read().decode("utf-8", "replace")
            open(path, "w", encoding="utf-8").write(body)
            time.sleep(1.0)
            return body
        except urllib.error.HTTPError as e:
            if e.code in (404, 403):
                return None
            time.sleep(5 * (i + 1))
        except Exception:
            time.sleep(4 * (i + 1))
    return None


def page(title):
    """live mirror first, Wayback second -- returns (html, url) or (None, None)"""
    quoted = urllib.parse.quote(title.replace(" ", "_"), safe="_,:!?'()&./")
    for base in (LIVE + quoted, WAYBACK + quoted):
        h = get(base)
        if h and "There is currently no text in this page" not in h:
            return h, base
    return None, None


def clean(s):
    s = re.sub(r"(?s)<(script|style|table)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<sup.*?</sup>", "", s)
    s = re.sub(r"(?s)</li>", ". ", s)          # bullets are sentences here
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = s.replace(" ,", ",").replace(" .", ".").replace("..", ".")
    return s.strip()


def summary(html):
    """the Summary section -- a bullet per beat, flattened into sentences"""
    m = re.search(r'(?s)id="Summary".*?</h2>(.*?)<(?:h2|div class="mw-heading)', html)
    if not m:
        return ""
    return clean(m.group(1))


def trim(s, cap=MAX):
    """whole sentences only, never past cap characters"""
    if len(s) <= cap:
        return s
    out = ""
    for sent in re.findall(r"[^.!?]*[.!?]", s):
        if len(out) + len(sent) > cap:
            break
        out += sent
    return (out or s[:cap]).strip()


def infobox(html):
    """(subtitle, ISO date) from the header cell and the 'First released' row"""
    sub = date = None
    box = re.search(r'(?s)<table class="infobox".*?</table>', html)
    if box:
        b = box.group(0)
        head = re.search(r'(?s)<th[^>]*colspan="2"[^>]*>(.*?)</th>', b)
        if head:
            sp = re.search(r'(?s)<span[^>]*>(.*?)</span>\s*$', head.group(1)) \
                 or re.search(r'(?s)<br\s*/?>\s*<span[^>]*>(.*?)</span>', head.group(1))
            if sp:
                t = clean(sp.group(1))
                if t and len(t) < 80:
                    sub = t
        d = re.search(r'(?s)<th>\s*First released:?\s*</th>\s*<td>(.*?)</td>', b)
        if d:
            raw = clean(d.group(1))
            m = re.search(r"([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})", raw)
            if m and m.group(1) in MONTHS:
                date = "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(1)], int(m.group(2)))
    return sub, date


def images(html, url):
    """(title card, still) -- the WebisodeNtitle card wins where one exists"""
    if url.startswith(LIVE_ROOT):
        found = [LIVE_ROOT + i for i in LIVE_IMG.findall(html)]
    else:
        found = ["https://web.archive.org" + i for i in WB_IMG.findall(html)]
    card = next((i for i in found if "title" in i.rsplit("/", 2)[-1].lower()), None)
    still = next((i for i in found if i != card), None)
    return card, still


def parts(title):
    """'Hard Knox, Parts 3 & 4' -> ('Hard Knox', [3, 4])"""
    m = re.match(r"(.*?),\s*Parts?\s+(.*)$", title)
    if not m:
        return title, []
    nums = [int(n) for n in re.findall(r"\d+", m.group(2))]
    return m.group(1), nums


def sheet_webisodes():
    html = open(os.path.join(HERE, os.pardir, "index.html"), encoding="utf-8").read()
    data = json.loads(re.search(r'id="timeline-data">(.*?)</script>', html, re.S).group(1))
    for e in data["entries"]:
        for it in (e.get("c") or {}).get("web", []):
            if it.get("c"):
                yield it["c"], it["t"]


def main():
    todo = list(sheet_webisodes())

    prev = {}
    if os.path.exists(OUT):
        prev = json.load(open(OUT, encoding="utf-8")).get("found", {})
    if "--retry" in sys.argv:
        todo = [t for t in todo if t[0] not in prev]

    found, missing = dict(prev), []
    for n, (code, title) in enumerate(todo, 1):
        series, nums = parts(title)
        pages = ["Webisode:%s, Part %d" % (series, i) for i in nums] or ["Webisode:" + series]

        blurbs, subs, url, card, still, date = [], [], None, None, None, None
        for p in pages:
            h, u = page(p)
            if not h:
                continue
            if url is None:
                url = u
            s = summary(h)
            if s:
                blurbs.append(s)
            sub, d = infobox(h)
            if sub and sub not in subs:
                subs.append(sub)
            if date is None:
                date = d
            c, st = images(h, u)
            card = card or c
            still = still or st

        if url is None:
            missing.append(code)
            print("  %2d/%d MISS  %-6s %s" % (n, len(todo), code, title))
            continue

        rec = {"t": title, "wiki": url}
        if subs:
            rec["sub"] = " / ".join(subs)
        if date:
            rec["d"] = date
        b = trim(" ".join(blurbs))
        if b:
            rec["b"] = b
        img = card or still
        if img:
            rec["img"] = img
        found[code] = rec
        print("  %2d/%d ok    %-6s blurb=%-3d img=%-5s sub=%-5s %s"
              % (n, len(todo), code, len(b), bool(img), bool(subs), title[:32]))

    os.makedirs(DATA, exist_ok=True)
    json.dump({"found": found, "missing": missing},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print("\nDONE: %d webisodes | %d with a blurb | %d with an image | %d with a date | %d missing"
          % (len(found), sum(1 for v in found.values() if v.get("b")),
             sum(1 for v in found.values() if v.get("img")),
             sum(1 for v in found.values() if v.get("d")), len(missing)))


if __name__ == "__main__":
    main()
