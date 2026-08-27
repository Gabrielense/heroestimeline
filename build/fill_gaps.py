# -*- coding: utf-8 -*-
"""Go after the entries that still say nothing about themselves.

build/blurb_audit.py finds them; this tries to fill them. Each title is
resolved against Heroes Wiki -- by name, then by the wiki's own search -- and
whatever blurb and picture that page holds is kept.

It writes build/data/gap_fill.json and nothing else. Anything it cannot find is
listed in "missing" there, which is the honest answer for the entries that were
never written about anywhere: the UK radio show has no page at all.

    py build/fill_gaps.py                # every column with gaps
    py build/fill_gaps.py --only misc
"""
import io, json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scrape_evo_sites import resolve, images, pick, lead, section, trim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
AUDIT = os.path.join(DATA, "blurb_audit.json")
OUT = os.path.join(DATA, "gap_fill.json")

# columns worth asking the wiki about. Physical media is left out: the buy
# panel already carries a blurb per group of objects, which is the level at
# which the text is actually true.
COLUMNS = ["evo", "misc", "bts"]

# the sheet's wording against the wiki's, where search cannot bridge it
ALIASES = {
    "Are You A Hero?": "Are you a hero?",
    "brianundaunted.imeem.com": "Brian Undaunted",
    "Devin's PDA (personal digital assistant)": "Devin's PDA",
    "Heroes Reborn: Enigma (iOS/Android)": "Heroes Reborn: Enigma",
    "Gemini: Heroes Reborn (PC/PS4/XBOX One)": "Gemini: Heroes Reborn",
    "Global News Interactive / The Drucker Files": "Global News Interactive",
    "9thwonders.com: Evsdropr messages and threads": "Evsdropr's 9thwonders.com posts",
    "HeroTruther YouTube channel": "HeroTruther",
    "iStory's SMS": "iStory",
    "Mohinder's Apartment (BBC Evolutions)": "Mohinder's apartment",
    "Habbo's Interactivity": "Habbo Hotel",
    "Claire & the Cat flash animation": "Claire and the cat",
    "Topps Heroes Series 1 Trading Card Set": "Topps",
    "Heroes: Origins announced": "Heroes: Origins",
    "Inside Heroes #1 to #8": "Inside Heroes",
}

# The parenthetical is this site's own note, not part of the name -- strip it
# before asking anyone else about it.
NOISE = re.compile(r"\s*\((?:UK premiere date[^)]*|iOS/Android|PC/PS4/XBOX One|"
                   r"personal digital assistant|BBC Evolutions)\)\s*", re.I)


def clean(title):
    return NOISE.sub(" ", title).strip()


def blurb_of(html):
    return trim(section(html, "Summary", "Synopsis", "Overview", "Description",
                        "About", "Plot") or lead(html) or "")


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    audit = json.load(io.open(AUDIT, encoding="utf-8"))
    gaps = [r for r in audit["missing"] if r["k"] in COLUMNS]
    if only:
        gaps = [r for r in gaps if r["k"] == only]

    # one lookup per distinct title, however many rows share it
    titles = {}
    for row in gaps:
        titles.setdefault((row["k"], row["t"]), row)
    print("%d entries without a blurb, %d distinct titles"
          % (len(gaps), len(titles)))

    out = json.load(io.open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    out.setdefault("missing", [])
    found = 0
    for n, (key, title) in enumerate(sorted(titles), 1):
        group = out.setdefault(key, {})
        if title in group:                       # already answered on a past run
            continue
        html, url, name = resolve(ALIASES.get(title) or clean(title))
        if not html:
            out["missing"].append({"k": key, "t": title})
            print("  %3d/%d MISS  %-46s" % (n, len(titles), title[:46]))
            continue
        rec = {"wiki": url}
        text = blurb_of(html)
        if text:
            rec["d"] = text
        art = pick(images(html, url), "title", "logo", "screen", "cap")
        if art:
            rec["img"] = art
        if rec.get("d") or rec.get("img"):
            group[title] = rec
            found += 1
        print("  %3d/%d ok    %-46s b=%-4s img=%-5s  %s"
              % (n, len(titles), title[:46], len(rec.get("d", "")),
                 bool(rec.get("img")), name))
        time.sleep(1)

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print("\n%d filled | %d still with nothing written about them anywhere"
          % (found, len(out["missing"])))
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
