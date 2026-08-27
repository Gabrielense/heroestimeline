# -*- coding: utf-8 -*-
"""Covers and contents for Heroes: The Official Magazine.

Every issue had its own page on the wiki once; they are all redirects now to
one article that carries the lot, and none of them names a cover -- the infobox
shows a cast panel. So all twelve issues were wearing issue one's picture, which
was not even issue one's cover.

The covers do exist, uploaded under names no article links: `Magazine Issue N`,
with a second `… Exclusive` for the subscriber edition Titan sent out instead of
the newsstand one. This takes the newsstand cover where there is one -- issue
two survives only as the subscriber edition -- and reads the article's own
`===Issue N===` sections for the cover months, the release dates and what was
inside.

    py build/magazine.py

Writes build/data/magazine.json, which extras.py merges into the physical
releases before the hand-written layer, so anything here can still be overridden
by hand in manual_extras.json.
"""
import io, json, os, re, sys, urllib.parse, urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, TypeError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "magazine.json")
API = "https://heroeswiki.ddns.net/api.php"
ARTICLE = "Heroes: The Official Magazine"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# The wiki's own file names, which no article links to. Issue two's newsstand
# cover was never uploaded; the subscriber one stands in, and the blurb says so.
COVERS = {
    "01": "Magazine Issue 1 real.jpg",
    "02": "Magazine Issue 2 Exclusive.JPG",
    "03": "Magazine Issue 3.jpg",
    "04": "Magazine Issue 4.jpg",
    "05": "Magazine Issue 5.JPG",
    "06": "Magazine Issue 6.JPG",
    "07": "Magazine Issue 7.JPG",
    "08": "Magazine Issue 8.jpg",
    "09": "Magazine Issue 9.jpg",
    "10": "Magazine Issue 10.jpg",
    "11": "Magazine Issue 11.jpg",
    "12": "Magazine issue 12.jpg",
}
SUBSCRIBER_ONLY = {"02"}

# The Heroes Reborn one is a different magazine, and a different article.
REBORN = {
    "title": "Heroes Reborn: Event Series – The Official Magazine #01",
    "file": "Heroes reborn magazine 1.jpg",
    "wiki": "Heroes Reborn: Event Series - The Official Magazine",
}

TITLE = "Heroes: The Official Magazine #%s"
HOW_MANY = 5                       # features to list before "and more"


def api(params):
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def wikitext(title):
    d = api({"action": "query", "prop": "revisions", "rvprop": "content",
             "rvslots": "main", "titles": title, "format": "json",
             "formatversion": "2"})
    for p in d["query"]["pages"]:
        if "revisions" in p:
            return p["revisions"][0]["slots"]["main"]["content"]
    return None


def image_urls(files):
    """File name -> the original's URL. Never a thumb: this mirror only serves
    thumbnail widths that already exist on disk."""
    out = {}
    files = list(files)
    for i in range(0, len(files), 20):
        d = api({"action": "query", "prop": "imageinfo", "iiprop": "url",
                 "titles": "|".join("File:" + f for f in files[i:i + 20]),
                 "format": "json", "formatversion": "2"})
        for p in d["query"]["pages"]:
            info = (p.get("imageinfo") or [{}])[0]
            if info.get("url"):
                out[p["title"][len("File:"):]] = info["url"]
    return out


def plain(text):
    """Wiki markup down to the words. Piped links keep the label."""
    text = re.sub(r"\[https?://\S+?\s+([^\]]*)\]", "", text)   # bare (excerpt) links
    text = re.sub(r"\[https?://\S+\]", "", text)
    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    text = text.replace("'''''", "").replace("'''", "").replace("''", "")
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def features(body):
    """The bullets under one issue, as readable phrases.

    Most read `'''Name''' - what it is`, in which case what it is says more than
    the name does. Issue one has no names at all, only the descriptions.
    """
    out = []
    for line in body.split("\n"):
        if not line.startswith("*") or line.startswith("**"):
            continue
        line = plain(line.lstrip("*").strip())
        if not line:
            continue
        m = re.match(r"^(.{2,60}?)\s+[-–—]\s+(.+)$", line)
        if m:
            line = m.group(2)
        line = line.rstrip(" .").strip()
        # the boilerplate every issue carried, listed once at the top of the
        # article and not worth repeating twelve times
        if re.match(r"^(An Editorial|Heroes Headlines|Heroes Mail|A competition)",
                    line, re.I):
            continue
        # a heading for the sub-bullets under it ("Three interviews:"), and the
        # tails links leave behind once they are stripped
        if line.endswith(":") or len(line) < 12 or re.match(r"^(at|and|or)\b", line):
            continue
        # sentence case belongs to the sentence these are joined into, not to
        # each fragment -- but not at the cost of a name's capital
        if re.match(r"^(A|An|The|Interview|Article|Look|Profile|Facts|Guide)\b",
                    line):
            line = line[0].lower() + line[1:]
        out.append(line)
    return out


def sentence(items):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return "; ".join(items[:-1]) + "; and " + items[-1]


def issue_sections(text):
    """The article covers two magazines and numbers both from one. Everything
    under the Heroes Reborn heading is the other one, and its Issue 1 would
    otherwise overwrite this one's."""
    m = re.search(r"\n==\s*\[\[Heroes Reborn\]\]\s*==\n", text)
    return (text[:m.start()], text[m.end():]) if m else (text, "")


def parse(text):
    """One record per issue, from the article's own ===Issue N=== sections."""
    out = {}
    parts = re.split(r"\n===\s*Issue (\d+)\s*===\n", "\n" + text.lstrip("\n"))
    for i in range(1, len(parts) - 1, 2):
        num, body = "%02d" % int(parts[i]), parts[i + 1]
        head = body.split("Contents/Features")[0]
        months = ""
        for line in head.split("\n"):
            line = plain(line)
            if line and not line.lower().startswith("released"):
                months = line
                break
        released = ""
        m = re.search(r"Released\s+(.+)", head)
        if m:
            released = plain(m.group(1)).rstrip(".")
        feats = features(body)
        bits = []
        if months:
            bits.append("The %s issue" % months)
        if released:
            bits.append("released %s" % released)
        lead = ", ".join(bits)
        rec = {}
        if lead:
            rec["d"] = lead + "."
        if feats:
            shown = feats[:HOW_MANY]
            more = " There was more in it than that." if len(feats) > HOW_MANY else ""
            rec["d"] = (rec.get("d", "") + " Inside: " + sentence(shown) + "." + more).strip()
        out[num] = rec
    return out


def main():
    text = wikitext(ARTICLE)
    if not text:
        sys.exit("could not read %r off the wiki" % ARTICLE)
    heroes, reborn = issue_sections(text)
    issues = parse(heroes)
    reborn_rec = (parse(reborn) or {}).get("01", {})
    print("article: %d issues parsed, %d for Heroes Reborn"
          % (len(issues), 1 if reborn_rec else 0))

    urls = image_urls(list(COVERS.values()) + [REBORN["file"]])
    missing = [f for f in COVERS.values() if f not in urls]
    if missing:
        print("  no such file: %s" % ", ".join(missing), file=sys.stderr)

    out = {}
    for num, fname in sorted(COVERS.items()):
        rec = dict(issues.get(num) or {})
        if urls.get(fname):
            rec["img"] = urls[fname]
        if num in SUBSCRIBER_ONLY:
            rec["d"] = (rec.get("d", "") + " Titan ran two covers an issue, one "
                        "for the newsagents and one for subscribers; only the "
                        "subscriber cover survives for this one.").strip()
        rec["wiki"] = "https://heroeswiki.ddns.net/wiki/" + \
                      urllib.parse.quote(ARTICLE + " #" + num.lstrip("0"))
        out[TITLE % num] = rec

    rec = dict(reborn_rec)
    if urls.get(REBORN["file"]):
        rec["img"] = urls[REBORN["file"]]
    if rec:
        rec["wiki"] = "https://heroeswiki.ddns.net/wiki/" + \
                      urllib.parse.quote(REBORN["wiki"])
        out[REBORN["title"]] = rec

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    print("%d covers, %d blurbs -> %s"
          % (sum(1 for v in out.values() if v.get("img")),
             sum(1 for v in out.values() if v.get("d")), OUT))


if __name__ == "__main__":
    main()
