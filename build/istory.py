# -*- coding: utf-8 -*-
"""The iStory, chapter by chapter.

The sheet gives every chapter its own row -- "Cap. 101" through "Cap. 906" --
so the page should give every chapter its own blurb, not repeat the volume's
description fifty-eight times. Heroes Wiki keeps a "<volume> chapter summaries"
page for most of them, one section per chapter, and those sections usually carry
their own screenshot too.

Writes build/data/istory.json keyed by the chapter code the timeline uses, which
is what extrasFor() in index.html looks up first.

    py build/istory.py
    py build/istory.py --probe "Slow Burn"
"""
import io, json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scrape_evo_sites import get, page, images, pick, strip, trim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
HTML = os.path.join(HERE, os.pardir, "index.html")
OUT = os.path.join(DATA, "istory.json")

# which volume each chapter number belongs to, and the page that describes it
VOLUMES = [
    (101, 106, "Operation Splinter"),
    (201, 206, "Operation Bad Blood"),
    (301, 304, "The Private"),
    (401, 412, "The Agent"),
    (501, 505, "The Civilian"),
    (601, 606, "Faction Zero"),
    (701, 710, "Slow Burn"),
    (801, 804, "The Puppet Master"),
    (901, 906, "Purpose"),
]


def volume_of(number):
    for lo, hi, name in VOLUMES:
        if lo <= number <= hi:
            return name
    return None


def chapter_sections(html):
    """{chapter number: section html} for a chapter-summaries page."""
    out = {}
    parts = re.split(r'<h[23] id="Chapter_(\d+)"[^>]*>.*?</h[23]>', html, flags=re.S)
    for i in range(1, len(parts) - 1, 2):
        try:
            out[int(parts[i])] = parts[i + 1]
        except ValueError:
            continue
    return out


def summary_of(section):
    """The chapter's own two-line synopsis.

    Each section holds three things: a line naming the chapter, a tinted table
    with the synopsis NBC published, and a collapsed table with a step-by-step
    walkthrough of every choice. The synopsis is the one worth showing -- the
    walkthrough is a solution guide and far too long for a blurb -- so this
    reads the tinted table and stops.
    """
    m = re.search(r'<table style="[^"]*background-color:\s*#CCD5F4[^"]*">(.*?)</table>',
                  section, re.S)
    if not m:
        # a few volumes use a plain paragraph instead of the tinted table
        m = re.search(r"<p>(?!<a[^>]*class=\"external)(.*?)</p>", section, re.S)
    return trim(strip(m.group(1))) if m else ""


def name_and_date(section):
    """("The Neighbor", "2009-07-22") from the line under the heading."""
    m = re.search(r">Chapter\s*\d+:\s*([^<]+)</a>\s*\(released\s*"
                  r"(\d{1,2})/(\d{1,2})/(\d{4})", section)
    if not m:
        m2 = re.search(r">Chapter\s*\d+:\s*([^<]+)<", section)
        return (m2.group(1).strip() if m2 else None), None
    return (m.group(1).strip(),
            "%s-%02d-%02d" % (m.group(4), int(m.group(2)), int(m.group(3))))


def volume_page(name):
    """(html, url) for the chapter summaries, falling back to the volume."""
    for candidate in (name + " chapter summaries", name):
        html, url = page(candidate)
        if html:
            return html, url
    return None, None


def main():
    probe = None
    if "--probe" in sys.argv:
        probe = sys.argv[sys.argv.index("--probe") + 1]

    html = io.open(HTML, encoding="utf-8").read()
    data = json.loads(re.search(
        r'<script type="application/json" id="timeline-data">(.*?)</script>',
        html, re.S).group(1))

    # every chapter code the timeline actually uses, in order
    wanted = []
    for entry in data["entries"]:
        for item in (entry.get("c") or {}).get("evo", []):
            code = item.get("c") or ""
            if not code.startswith("Cap."):
                continue
            for number in re.findall(r"\d+", code):
                wanted.append((code, int(number), item["t"]))

    volumes = sorted({volume_of(n) for _, n, _ in wanted} - {None})
    if probe:
        volumes = [v for v in volumes if v.lower() == probe.lower()]
    print("%d chapter rows across %d volumes" % (len(wanted), len(volumes)))

    out, missing = {}, []
    for name in volumes:
        html_v, url = volume_page(name)
        if not html_v:
            missing.append(name)
            print("  MISS  %s" % name)
            continue
        sections = chapter_sections(html_v)
        art = pick(images(html_v, url), "istory", "title", "logo")
        print("  %-22s %2d chapter sections  art=%s"
              % (name, len(sections), bool(art)))

        for code, number, title in wanted:
            if volume_of(number) != name:
                continue
            section = sections.get(number)
            rec = {"vol": name, "wiki": url}
            if section:
                blurb = summary_of(section)
                if blurb:
                    rec["d"] = blurb
                chapter_name, released = name_and_date(section)
                if chapter_name:
                    rec["sub"] = chapter_name
                if released:
                    rec["released"] = released
                shot = pick(images(section, url), "istory", "chapter")
                if shot:
                    rec["img"] = shot
            if not rec.get("img") and art:
                rec["img"] = art
            # a row covering two volumes at once keeps both blurbs apart
            existing = out.get(code)
            if existing and existing.get("d") and rec.get("d"):
                rec["d"] = "%s %s: %s" % (existing["d"], name, rec["d"])
                rec["vol"] = "%s / %s" % (existing["vol"], name)
            out[code] = rec
        time.sleep(1)

    if probe:
        for code, rec in sorted(out.items()):
            print("\n%s [%s]\n  %s\n  %s"
                  % (code, rec.get("vol"), rec.get("d", "(no summary)")[:200],
                     rec.get("img", "(no image)")))
        return

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print("\n%d chapters | %d with a blurb | %d with a picture | %d volumes missed"
          % (len(out), sum(1 for v in out.values() if v.get("d")),
             sum(1 for v in out.values() if v.get("img")), len(missing)))
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
