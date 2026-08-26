# -*- coding: utf-8 -*-
"""Work out the real release schedule of the Evolutions/ARG elements.

Several of these sit in the sheet as a single cell, but they were delivered in
instalments over weeks or months. Heroes Wiki logs each one with its date, so
this turns a lumped cell into the list of weeks it actually occupied.

Collects dates and counts only -- no message text.

    py build/arg_schedule.py     # writes build/data/arg_schedule.csv (+ .json)
"""
import collections, csv, datetime, json, os, re, sys, time
import urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CACHE = os.path.join(DATA, "wikicache")
BASE = "https://web.archive.org/web/20200514144559/http://heroeswiki.com/"
UA = {"User-Agent": "heroes-timeline/1.0"}

# sheet entry -> the wiki page that logs its instalments
SOURCES = [
    ("Hiro's SMS",                                   "Hiro's_messages"),
    ("Hiro's Blog",                                  "Hiro's_blog"),
    ("Hana's SMS",                                   "Hana's_messages"),
    ("Hana's Blog",                                  "Hana's_blog"),
    ("Rebel's SMS/emails",                           "Rebel's_messages"),
    ("Evs Dropper's blog",                           "Evs_Dropper's_blog"),
    ("9thwonders.com: Evsdropr messages and threads", "Evsdropr's_9thwonders.com_posts"),
    ("Bridget's messages",                           "Bridget_Bailey's_messages"),
    ("Pinehearst & Primatech SMS and emails",        "Pinehearst_and_Primatech_messages"),
]

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"])}
DATE = re.compile(r"\b(January|February|March|April|May|June|July|August|"
                  r"September|October|November|December)\s+(\d{1,2}),?\s+(20\d\d)")


def get(page, tries=4):
    os.makedirs(CACHE, exist_ok=True)
    url = BASE + page.replace("'", "%27")
    path = os.path.join(CACHE, re.sub(r"\W+", "_", url)[-120:] + ".html")
    if os.path.exists(path):
        return open(path, encoding="utf-8", errors="replace").read()
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                body = r.read().decode("utf-8", "replace")
            open(path, "w", encoding="utf-8").write(body)
            time.sleep(1.5)
            return body
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return None
            time.sleep(6 * (i + 1))
        except Exception:
            time.sleep(4 * (i + 1))
    return None


def dates_in(html):
    """one count per dated row; falls back to a plain scan for prose pages"""
    body = re.search(r'(?s)<div id="mw-content-text".*?>(.*?)<div class="printfooter"', html)
    seg = body.group(1) if body else html
    per = collections.Counter()
    for row in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", seg):
        m = DATE.search(re.sub(r"<[^>]+>", " ", row))
        if m:
            per[datetime.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))] += 1
    if not per:
        for m in DATE.finditer(re.sub(r"<[^>]+>", " ", seg)):
            per[datetime.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))] += 1
    return per


def monday(d):
    return d - datetime.timedelta(days=d.weekday())


def main():
    rows, summary = [], []
    for label, page in SOURCES:
        html = get(page)
        if not html or "no text in this page" in html:
            summary.append((label, page, 0, 0, "", "", "page not retrieved"))
            print("  %-46s %-34s NOT RETRIEVED" % (label[:46], page[:34]))
            continue
        per = dates_in(html)
        if not per:
            summary.append((label, page, 0, 0, "", "", "no dates on page"))
            print("  %-46s %-34s no dates found" % (label[:46], page[:34]))
            continue
        weeks = collections.Counter()
        for d, n in per.items():
            weeks[monday(d)] += n
        for w in sorted(weeks):
            rows.append({"element": label, "week_of": w.isoformat(),
                         "instalments": weeks[w], "source": page})
        summary.append((label, page, sum(per.values()), len(weeks),
                        min(per).isoformat(), max(per).isoformat(), ""))
        print("  %-46s %3d instalments over %2d weeks  %s -> %s"
              % (label[:46], sum(per.values()), len(weeks), min(per), max(per)))

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "arg_schedule.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["element", "week_of", "instalments", "source"])
        w.writeheader()
        w.writerows(rows)
    json.dump(rows, open(os.path.join(DATA, "arg_schedule.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    got = [s for s in summary if s[2]]
    print("\n%d of %d elements resolved | %d lumped cells -> %d weekly rows"
          % (len(got), len(SOURCES), len(got), len(rows)))
    for s in summary:
        if not s[2]:
            print("   unresolved: %s (%s)" % (s[0], s[6]))


if __name__ == "__main__":
    main()
