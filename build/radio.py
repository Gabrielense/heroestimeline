# -*- coding: utf-8 -*-
"""Broadcast dates for Heroes: The Official Radio Show, off the BBC itself.

The show is filed on this page beside the Heroes episode each edition discussed
rather than on its own Saturday, the same as Heroes Unmasked and for the same
reason -- so a week reads as one story beat. Which means the real date has to be
in the blurb, or it is nowhere.

bbc.co.uk/programmes still has the brand, both series and all 26 editions, with
a first-broadcast date on each, even though Radio 7 kept no recording of any of
them. The .json on the end of any programme URL gives it without scraping:

    https://www.bbc.co.uk/programmes/b00b5lm0            the brand
    https://www.bbc.co.uk/programmes/<pid>/children.json its series, its episodes

Episodes are matched to the timeline by the title the sheet already gives them
-- "#1x01: Episode 6" is Series 1, Episode 6 -- so this fails loudly rather than
silently mis-dating anything if those titles ever change.

    py build/radio.py

Writes build/data/radio.json for extras.py, which appends the date to the shared
blurb the `series` rule in manual_extras.json spreads over all 26.
"""
import io, json, os, re, sys, time, urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, TypeError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, os.pardir, "index.html")
OUT = os.path.join(HERE, "data", "radio.json")

BRAND = "b00b5lm0"
PAGE = "https://www.bbc.co.uk/programmes/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

# "The Official Radio Show (UK premiere date 9/1/2007) #1x01: Episode 6"
ROW = re.compile(r"^The Official Radio Show\b.*?#(\d)x\d\d:\s*(.+)$")

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def children(pid):
    out, page = [], 1
    while True:
        d = get("%s%s/children.json?limit=50&page=%d" % (PAGE, pid, page))
        kids = d.get("children", {}).get("programmes", [])
        out.extend(kids)
        if len(kids) < 50:
            return out
        page += 1
        time.sleep(0.5)


def pretty(iso):
    """2007-09-01 -> 1 September 2007"""
    y, m, d = iso[:10].split("-")
    return "%d %s %s" % (int(d), MONTHS[int(m) - 1], y)


def timeline_titles():
    html = io.open(HTML, encoding="utf-8").read()
    m = re.search(r'id="timeline-data">(.*?)</script>', html, re.S)
    data = json.loads(m.group(1)) if m else {"entries": []}
    out = []
    for entry in data["entries"]:
        for item in (entry.get("c") or {}).get("misc", []):
            if ROW.match(item["t"]):
                out.append(item["t"])
    return out


def main():
    # the BBC's own series are numbered the way the sheet numbers them
    by_series = {}
    for series in children(BRAND):
        n = re.search(r"(\d+)", series.get("title") or "")
        if not n:
            continue
        eps = {}
        for ep in children(series["pid"]):
            eps[(ep.get("title") or "").strip()] = ep
        by_series[n.group(1)] = eps
        print("series %s: %d editions" % (n.group(1), len(eps)))

    out, missed, odd = {}, [], []
    for title in timeline_titles():
        series, label = ROW.match(title).groups()
        ep = (by_series.get(series) or {}).get(label.strip())
        if not ep:
            missed.append(title)
            continue
        when = ep.get("first_broadcast_date") or ""
        if not when:
            missed.append(title)
            continue
        out[title] = {"aired": pretty(when), "l": PAGE + ep["pid"]}
        # every edition went out on a Saturday teatime; a midnight timestamp is
        # the BBC's record being incomplete rather than a different slot
        if when[11:16] == "00:00":
            odd.append("%s -> %s (no time on the BBC's record)" % (title, when[:10]))

    for t in missed:
        print("  no BBC page for %r" % t, file=sys.stderr)
    for note in odd:
        print("  check: %s" % note, file=sys.stderr)

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    print("%d of %d editions dated -> %s"
          % (len(out), len(out) + len(missed), OUT))


if __name__ == "__main__":
    main()
