# -*- coding: utf-8 -*-
"""Check our dates against User:Iheartheroes' release-date list.

Theirs is the most careful timeline Heroes Wiki ever had, and it was built
independently of the spreadsheet this site comes from -- so where the two
disagree, one of them is wrong and it is worth knowing which.

Fetches their page from the Wayback Machine, parses the day-by-day tables, and
compares episodes, graphic novels and webisodes by title.

    py build/date_diff.py
    py build/date_diff.py --all     # include the entries only one side lists
"""
import datetime, io, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
HTML = os.path.join(HERE, os.pardir, "index.html")
CACHE = os.path.join(DATA, "wikicache", "iheartheroes_release_dates.html")
OUT = os.path.join(DATA, "date_diff.json")

SOURCE = ("https://web.archive.org/web/20200514170613/"
          "https://heroeswiki.com/User:Iheartheroes/Release_dates")
UA = {"User-Agent": "heroes-timeline/1.0 (https://github.com/Gabrielense/heroestimeline)"}

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}

# their prefixes against our columns
KIND = {"E": "ep", "GN": "gn", "W": "web"}
COMPARE = ("ep", "gn", "web")


def fetch():
    if os.path.exists(CACHE):
        return io.open(CACHE, encoding="utf-8").read()
    req = urllib.request.Request(SOURCE, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode("utf-8", "replace")
    io.open(CACHE, "w", encoding="utf-8").write(body)
    return body


def monday(iso):
    """The Monday of that date's week. The sheet files everything by week, so a
    day's difference inside one week is a convention, not a disagreement."""
    d = datetime.date(*map(int, iso.split("-")))
    return d - datetime.timedelta(days=d.weekday())


def days_between(a, b):
    return (datetime.date(*map(int, b.split("-"))) -
            datetime.date(*map(int, a.split("-")))).days


def norm(title):
    """Match on the words, not the punctuation: the two lists disagree about
    ampersands, ellipses, capital letters and the odd definite article."""
    t = title.lower()
    t = t.replace("&amp;", "and").replace("&", "and")
    t = re.sub(r"^(the|a)\s+", "", t)
    t = re.sub(r"[^a-z0-9]+", "", t)
    return t


def parse(html):
    """{normalised title: (iso date, kind, title as they wrote it)}"""
    out, year, month = {}, None, None
    # Their page nests year tables inside month tables inside day rows, but the
    # headings appear in order, so a single pass over the markup tracks them.
    token = re.compile(
        r'<span style="font-size:132%;">\s*<i>(\d{4})</i>'          # year
        r'|<span style="font-size:120%;">\s*<i>([A-Z][a-z]+)</i>'   # month
        r'|<td width="8%"[^>]*>\s*(\d{1,2})\s*</td>'                # day
        r'|(?:^|\s)(E|GN|W|IS|HE|V|B):\s*<a[^>]*>(.*?)</a>')        # an entry
    day = None
    for m in token.finditer(html):
        if m.group(1):
            year, month, day = int(m.group(1)), None, None
        elif m.group(2):
            month, day = MONTHS.get(m.group(2)), None
        elif m.group(3):
            day = int(m.group(3))
        elif m.group(4) and year and month and day:
            kind = KIND.get(m.group(4))
            if not kind:
                continue
            title = re.sub(r"<[^>]+>", "", m.group(5)).strip()
            title = title.replace("&amp;", "&").replace("&#39;", "'")
            if not title:
                continue
            out.setdefault(norm(title),
                           ("%04d-%02d-%02d" % (year, month, day), kind, title))
    return out


def ours():
    html = io.open(HTML, encoding="utf-8").read()
    data = json.loads(re.search(
        r'<script type="application/json" id="timeline-data">(.*?)</script>',
        html, re.S).group(1))
    out = {}
    for entry in data["entries"]:
        date = entry.get("d")
        if not date:
            continue
        for kind in COMPARE:
            for item in (entry.get("c") or {}).get(kind, []):
                out.setdefault(norm(item["t"]), (date, kind, item["t"]))
    return out


def main():
    theirs, mine = parse(fetch()), ours()
    print("theirs %d entries | ours %d" % (len(theirs), len(mine)))

    same, moved, only_them, only_us = 0, [], [], []
    for key, (date, kind, title) in sorted(theirs.items()):
        if key not in mine:
            only_them.append({"t": title, "k": kind, "d": date})
            continue
        our_date, our_kind, our_title = mine[key]
        if our_date == date:
            same += 1
        else:
            moved.append({"t": our_title, "k": kind,
                          "ours": our_date, "theirs": date,
                          "days": days_between(date, our_date),
                          "same_week": monday(our_date) == monday(date)})
    for key, (date, kind, title) in sorted(mine.items()):
        if key not in theirs:
            only_us.append({"t": title, "k": kind, "d": date})

    within = [r for r in moved if r["same_week"]]
    real = [r for r in moved if not r["same_week"]]
    print("\n%d agree exactly | %d differ inside one week | %d land in a "
          "different week" % (same, len(within), len(real)))
    print("\nsame week -- the sheet files by Monday, they file by release day:")
    for row in within:
        print("  %-4s %-42s ours %s  theirs %s  (%+d)"
              % (row["k"], row["t"][:42], row["ours"], row["theirs"], row["days"]))
    print("\nDIFFERENT WEEK -- worth checking one by one:")
    for row in real:
        print("  %-4s %-42s ours %s  theirs %s  (%+d)"
              % (row["k"], row["t"][:42], row["ours"], row["theirs"], row["days"]))

    print("\n%d only on their list | %d only on ours" % (len(only_them), len(only_us)))
    if "--all" in sys.argv:
        for label, rows in (("only theirs", only_them), ("only ours", only_us)):
            print("\n%s:" % label)
            for row in rows:
                print("  %-4s %s  %s" % (row["k"], row["d"], row["t"][:52]))

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(
        {"source": SOURCE, "agree": same, "disagree": moved,
         "only_theirs": only_them, "only_ours": only_us},
        ensure_ascii=False, indent=1))
    print("\nwrote %s" % OUT)


if __name__ == "__main__":
    main()
