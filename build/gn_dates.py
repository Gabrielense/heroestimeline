# -*- coding: utf-8 -*-
"""Check the graphic novel dates against Wikipedia's list.

Wikipedia's List of Heroes graphic novels carries a release date per issue, and
it is a third opinion -- independent of both the spreadsheet this site is built
from and User:Iheartheroes' hand-kept list. Where all three agree there is
nothing to think about; where they split, the odd one out is worth a look.

Reads the cached copy in data/gn_list.wiki (fetched by whatever put it there)
and compares by issue number.

    py build/gn_dates.py
    py build/gn_dates.py --all
"""
import datetime, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
HTML = os.path.join(HERE, os.pardir, "index.html")
WIKI = os.path.join(DATA, "gn_list.wiki")
OUT = os.path.join(DATA, "gn_dates.json")

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}


def monday(iso):
    d = datetime.date(*map(int, iso.split("-")))
    return (d - datetime.timedelta(days=d.weekday())).isoformat()


def wiki_dates():
    """{issue number: (iso date, title)} from the cached wikitext.

    The list is a run of table rows; each issue's number, title and date sit in
    the same row, so the rows are split first and read one at a time rather
    than matching across the whole file, which would pair up the wrong two.
    """
    text = io.open(WIKI, encoding="utf-8").read()
    out = {}
    for row in re.split(r"\n\|-", text):
        # the issue number is a cell of its own, often spanning two rows
        num = re.search(r'\|\s*(?:rowspan="\d+"\s*\|\s*)?(\d{1,3})\s*\n', row)
        # the title lives in the cite template that links the PDF
        title = re.search(r"\|\s*title\s*=\s*([^}|\n]+)", row)
        # and the date is a bare ISO cell
        date = re.search(r"\|\s*(\d{4}-\d{2}-\d{2})\s*\n", row)
        if not (num and date):
            continue
        out[num.group(1)] = (date.group(1),
                             title.group(1).strip() if title else "")
    return out


def ours():
    html = io.open(HTML, encoding="utf-8").read()
    data = json.loads(re.search(
        r'<script type="application/json" id="timeline-data">(.*?)</script>',
        html, re.S).group(1))
    out = {}
    for entry in data["entries"]:
        if not entry.get("d"):
            continue
        for item in (entry.get("c") or {}).get("gn", []):
            if item.get("c"):
                out[item["c"]] = (entry["d"], item["t"])
    return out


def main():
    if not os.path.exists(WIKI):
        raise SystemExit("no cached %s" % WIKI)
    theirs, mine = wiki_dates(), ours()
    print("Wikipedia lists %d dated issues | we hold %d" % (len(theirs), len(mine)))

    same, week, off, missing = 0, [], [], []
    for num, (date, title) in sorted(theirs.items(), key=lambda kv: int(kv[0])):
        if num not in mine:
            missing.append({"c": num, "t": title, "d": date})
            continue
        our_date, our_title = mine[num]
        if our_date == date:
            same += 1
        elif monday(our_date) == monday(date):
            week.append({"c": num, "t": our_title, "ours": our_date, "wiki": date})
        else:
            off.append({"c": num, "t": our_title, "ours": our_date, "wiki": date})

    print("\n%d agree exactly | %d differ inside one week | %d land elsewhere"
          % (same, len(week), len(off)))
    print("\nDIFFERENT WEEK:")
    for row in off:
        print("  #%-5s %-40s ours %s  wikipedia %s"
              % (row["c"], row["t"][:40], row["ours"], row["wiki"]))
    if "--all" in sys.argv and week:
        print("\nsame week, different day:")
        for row in week:
            print("  #%-5s %-40s ours %s  wikipedia %s"
                  % (row["c"], row["t"][:40], row["ours"], row["wiki"]))
    if missing:
        print("\n%d issues Wikipedia dates that we do not carry by that number"
              % len(missing))

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(
        {"agree": same, "same_week": week, "different_week": off,
         "not_ours": missing}, ensure_ascii=False, indent=1))
    print("\nwrote %s" % OUT)


if __name__ == "__main__":
    main()
