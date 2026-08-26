# -*- coding: utf-8 -*-
"""Collect each episode's logline and title card from the archived Heroes Wiki.

Wikipedia's episode articles carry long plot recaps, so trimming one to a line
yields the opening beat rather than a description of the episode. Heroes Wiki's
"Summary" section is the NBC-style logline instead -- it names every thread in
the episode, which is the register the graphic novel blurbs already have.

Title cards there are named by episode code -- 1x09episodetitle.jpg -- and are
served over https, while the graphic novel pages use http. Both are accepted.

    py build/scrape_episodes.py            # writes build/data/ep_wiki.json
    py build/scrape_episodes.py --retry    # only re-attempt previous misses
"""
import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CACHE = os.path.join(DATA, "wikicache")
OUT = os.path.join(DATA, "ep_wiki.json")
TS = "20200514144559"
BASE = "https://web.archive.org/web/%s/http://heroeswiki.com/" % TS
UA = {"User-Agent": "heroes-timeline/1.0 (fan timeline; contact via github)"}
MAX = 400

IMG = re.compile(r'"(/web/\d+im_/https?://heroeswiki\.com/images/(?:thumb/)?[^"]+?'
                 r'\.(?:jpg|JPG|jpeg|png|PNG))"')


def get(url, tries=4):
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
            time.sleep(1.2)
            return body
        except urllib.error.HTTPError as e:
            if e.code in (404, 403):
                return None
            time.sleep(5 * (i + 1))          # 429 and friends: back off
        except Exception:
            time.sleep(4 * (i + 1))
    return None


def clean(s):
    s = re.sub(r"(?s)<(script|style|table)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<sup.*?</sup>", "", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).replace(" ,", ",").replace(" .", ".").strip()


def logline(html):
    """the Summary section -- every thread, not just the opening beat"""
    m = re.search(r'(?s)id="Summary".*?</h2>(.*?)<h2', html)
    if not m:
        return ""
    text = clean(m.group(1))
    if len(text) <= MAX:
        return text
    out = ""
    for sent in re.findall(r"[^.!?]*[.!?]", text):
        if len(out) + len(sent) > MAX:
            break
        out += sent
    return (out or text[:MAX]).strip()


def card(html, code):
    imgs = IMG.findall(html)
    want = (code or "").lower().replace("hr", "") + "episodetitle"
    for i in imgs:                      # the card named for this episode's code
        if want in i.lower():
            return "https://web.archive.org" + i
    for i in imgs:                      # any episode-title card on the page
        if "episodetitle" in i.lower():
            return "https://web.archive.org" + i
    return None


def main():
    html = open(os.path.join(HERE, os.pardir, "index.html"), encoding="utf-8").read()
    data = json.loads(re.search(r'id="timeline-data">(.*?)</script>', html, re.S).group(1))
    todo = []
    for e in data["entries"]:
        for it in (e.get("c") or {}).get("ep", []):
            if it.get("c"):
                todo.append((it["c"], it["t"]))

    prev = {}
    if os.path.exists(OUT):
        prev = json.load(open(OUT, encoding="utf-8")).get("found", {})
    if "--retry" in sys.argv:
        todo = [t for t in todo if t[0] not in prev]

    found, missing = dict(prev), []
    for n, (code, title) in enumerate(todo, 1):
        page = "Episode:" + urllib.parse.quote(title.replace(" ", "_"), safe="_,:!?'()&.")
        url = BASE + page
        h = get(url)
        if not h or "There is currently no text in this page" in h:
            missing.append([code, title])
            print("  %3d/%d MISS  %-8s %s" % (n, len(todo), code, title))
            continue
        rec = {"page": url}
        d = logline(h)
        c = card(h, code)
        if d:
            rec["d"] = d
        if c:
            rec["card"] = c
        found[code] = rec
        print("  %3d/%d ok    %-8s blurb=%-4d card=%-5s %s"
              % (n, len(todo), code, len(d), bool(c), title[:34]))

    json.dump({"found": found, "missing": missing},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print("\nDONE: %d episodes | %d with a logline | %d with a card | %d missing"
          % (len(found), sum(1 for v in found.values() if v.get("d")),
             sum(1 for v in found.values() if v.get("card")), len(missing)))


if __name__ == "__main__":
    main()
