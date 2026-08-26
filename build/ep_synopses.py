# -*- coding: utf-8 -*-
"""Extract per-episode blurbs from Wikipedia's Heroes season articles.

Same licence reasoning as the graphic novels: Wikipedia is CC BY-SA, so trimming
a summary down to a line is fine. Summaries there run ~400 characters, so only
the opening sentence or two is kept -- enough to place the episode, not a recap.

    py build/ep_synopses.py            # writes build/data/ep_synopses.json
    py build/ep_synopses.py --refresh  # re-download the season articles
"""
import json, os, re, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(DATA, "ep_synopses.json")
RAW = "https://en.wikipedia.org/w/index.php?title=%s&action=raw"

# article -> code prefix for that season
SEASONS = [
    ("Heroes season 1", "1x"),
    ("Heroes season 2", "2x"),
    ("Heroes season 3", "3x"),
    ("Heroes season 4", "4x"),
    ("Heroes Reborn (miniseries)", "HR1x"),
]
MAX = 220

# Where the sheet splits an episode Wikipedia keeps as one row, and the titles
# are too different for the prefix fallback to spot. Both halves of a two-hour
# premiere share the one blurb, same as the Eclipse two-parter does.
ALIAS = {
    "Jump, Push, Fall": "Orientation",       # season 4's two-hour premiere
}


def source(article):
    cache = os.path.join(DATA, re.sub(r"\W+", "_", article) + ".wiki")
    if os.path.exists(cache) and "--refresh" not in sys.argv:
        return open(cache, encoding="utf-8").read()
    url = RAW % urllib.parse.quote(article.replace(" ", "_"))
    req = urllib.request.Request(url, headers={"User-Agent": "heroes-timeline/1.0"})
    body = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    os.makedirs(DATA, exist_ok=True)
    open(cache, "w", encoding="utf-8").write(body)
    return body


def clean(s):
    s = re.sub(r"(?s)<ref[^>]*>.*?</ref>|<ref[^>]*/>", "", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"'''?", "", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def trim(s):
    """first sentence or two, never past MAX characters"""
    out = ""
    for sent in re.findall(r"[^.!?]*[.!?]", s) or [s]:
        if out and len(out) + len(sent) > MAX:
            break
        out += sent
        if len(out) > MAX * 0.55:
            break
    out = (out or s).strip()
    if len(out) > MAX:
        cut = out[:MAX].rsplit(" ", 1)[0]
        out = cut.rstrip(",;:") + "…"
    return out


def norm(s):
    s = s.lower().replace("&", "and").replace("’", "'")
    return re.sub(r"[^a-z0-9]", "", s)


def sheet_episodes():
    """the sheet's own episode codes and titles -- the thing we must match"""
    html = open(os.path.join(HERE, os.pardir, "index.html"), encoding="utf-8").read()
    data = json.loads(re.search(r'id="timeline-data">(.*?)</script>', html, re.S).group(1))
    for e in data["entries"]:
        for it in (e.get("c") or {}).get("ep", []):
            if it.get("c"):
                yield it["c"], it["t"]


def main():
    """Blurbs are attached by TITLE, never by episode number.

    Wikipedia counts Heroes' two-hour premieres as one row, so its season 4
    numbering runs one behind the sheet's from episode 2 on; and the Reborn
    article also lists the Dark Matters webisodes, which collide by number with
    the real episodes. Matching on title sidesteps both. The season prefix is
    kept in the key so the two different "Brave New World" episodes (4x19 and
    HR1x01) can't be confused for each other.
    """
    pool = {}          # (prefix, normalised title) -> blurb
    for article, prefix in SEASONS:
        try:
            wiki = source(article)
        except Exception as e:
            print("  %-28s FAILED %s" % (article, e))
            continue
        blocks = re.findall(r"\{\{Episode list(.*?)\n\s*\}\}", wiki, re.S)
        n = 0
        for b in blocks:
            # a two-part episode shares one row as EpisodeNumber2_1 / _2; the
            # Reborn miniseries numbers straight off EpisodeNumber with no "2"
            nums = re.findall(r"\|\s*EpisodeNumber2(?:_\d)?\s*=\s*(\d+)", b)
            if not nums:
                nums = re.findall(r"\|\s*EpisodeNumber(?:_\d)?\s*=\s*(\d+)", b)
            title = re.search(r"\|\s*Title\s*=\s*(.*?)\s*\n", b)
            summ = re.search(r"\|\s*ShortSummary\s*=\s*(.*?)(?=\n\s*\|\s*[A-Za-z]+\s*=|\Z)", b, re.S)
            if not nums or not summ:
                continue
            desc = trim(clean(summ.group(1)))
            if not desc:
                continue
            if not title:
                continue
            wt = clean(title.group(1))
            pool[(prefix, norm(wt))] = {"d": desc, "title": wt}
            n += 1
        print("  %-28s %2d blocks -> %2d titled rows" % (article, len(blocks), n))

    out, missed = {}, []
    for code, sheet_title in sheet_episodes():
        prefix = re.match(r"(HR\d+x|\d+x)", code).group(1)
        key = norm(ALIAS.get(sheet_title, sheet_title))
        rec = pool.get((prefix, key))
        if not rec:
            # "The Eclipse, Part 1" against Wikipedia's single "The Eclipse" row
            for (p, k), v in pool.items():
                if p == prefix and (key.startswith(k) or k.startswith(key)) and min(len(k), len(key)) > 6:
                    rec = v
                    break
        if rec:
            out[code] = rec
        else:
            missed.append((code, sheet_title))

    os.makedirs(DATA, exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    lens = sorted(len(v["d"]) for v in out.values())
    print("\n%d episodes matched by title | blurb median %d chars, max %d -> %s"
          % (len(out), lens[len(lens) // 2], lens[-1], os.path.relpath(OUT, HERE)))
    for code, t in missed:
        print("   no match: %-8s %s" % (code, t))


if __name__ == "__main__":
    main()
