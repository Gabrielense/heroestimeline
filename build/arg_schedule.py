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


def flat(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def as_date(m):
    return datetime.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))


def entries_in(html):
    """Return [(date, label)] for every instalment on the page.

    Two layouts are in use and both must be handled: message logs are tables
    with a date per row, while the blogs give each post its own <h3> with the
    date inside the entry. Reading only table rows made 20- and 26-entry blogs
    look like single instalments.
    """
    body = re.search(r'(?s)<div id="mw-content-text".*?>(.*?)<div class="printfooter"', html)
    seg = body.group(1) if body else html
    # layout A: one <h3> per entry, date somewhere inside it
    by_head = []
    for c in re.split(r"(?s)(?=<h3)", seg)[1:]:
        head = re.search(r'(?s)<h3.*?<span class="mw-headline"[^>]*>(.*?)</span>', c)
        m = DATE.search(flat(c)[:600])
        if head and m:
            by_head.append((as_date(m), flat(head.group(1))[:90]))

    # layout B: one table row per entry
    by_row = []
    for row in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", seg):
        t = flat(row)
        m = DATE.search(t)
        if m:
            by_row.append((as_date(m), re.sub(re.escape(m.group(0)), "", t).strip(" ,-–—")[:90]))

    # A page can hold both a summary table and per-entry headings, so take
    # whichever structured reading finds more. There is deliberately no prose
    # fallback: scanning loose text scoops up cross-references and "see also"
    # dates, which inflated Hiro's blog to 32 instalments across four years.
    # A page with no structure is reported as needing review, not guessed at.
    return max((by_head, by_row), key=len)


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
        items = entries_in(html)
        if not items:
            summary.append((label, page, 0, 0, "", "", "no dates on page"))
            print("  %-46s %-34s no dates found" % (label[:46], page[:34]))
            continue
        by_week = collections.defaultdict(list)
        for d, lab in items:
            by_week[monday(d)].append((d, lab))
        for w in sorted(by_week):
            got = sorted(by_week[w])
            rows.append({
                "element": label,
                "week_of": w.isoformat(),
                "instalments": len(got),
                "dates": " | ".join(d.isoformat() for d, _ in got),
                "titles": " | ".join(t for _, t in got if t),
                "source": page,
            })
        days = [d for d, _ in items]
        summary.append((label, page, len(items), len(by_week),
                        min(days).isoformat(), max(days).isoformat(), ""))
        print("  %-46s %3d instalments over %2d weeks  %s -> %s"
              % (label[:46], len(items), len(by_week), min(days), max(days)))

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "arg_schedule.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["element", "week_of", "instalments",
                                          "dates", "titles", "source"])
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
