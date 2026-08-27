# -*- coding: utf-8 -*-
"""Turn the hand-written data files into the two the page is built from.

Nothing here is scraped. It folds together:

  data/disc_extras.json   what is on the DVDs and Blu-rays, and the commentaries
  data/herotruther.json   the five lost videos (written by build/herotruther.py)

and writes:

  data/additions.json     rows for sync.py to fold into the timeline
  data/hand_extras.json   their blurbs, for extras.py

hand_extras.json also holds blurbs written directly by hand -- for the unaired
pilot, Novel Approach, the Damen Peak making-of -- so those are preserved
rather than overwritten.

    py build/make_additions.py
"""
import io, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

WIKI = "https://web.archive.org/web/20200514171611/https://heroeswiki.com/"

SEASON_NAME = {"s1": "Season 1", "s2": "Season 2", "s3": "Season 3",
               "s4": "Season 4", "hr": "Heroes Reborn"}


def load(name, default=None):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return default if default is not None else {}
    return json.load(io.open(path, encoding="utf-8"))


def main():
    discs = load("disc_extras.json")
    ht = load("herotruther.json")
    hand = load("hand_extras.json")

    rows = []
    blurbs = {"gn": {}, "ep": {}, "evo": {}, "misc": {}}
    # keep anything written straight into hand_extras by hand
    for group in ("gn", "ep", "evo", "misc", "web", "site", "istory", "phys"):
        if group in hand and group in blurbs:
            blurbs[group].update(hand[group])
        elif group in hand:
            blurbs[group] = hand[group]

    # --- Novel Approach ------------------------------------------------------
    # It is a reprint collection, not an issue of the run, so it reads as Bonus
    # like the other two the sheet never numbered.
    rows.append({"d": "2010-03-10", "k": "gn", "c": "Bonus",
                 "t": "Novel Approach: The Hiro Collection",
                 "l": WIKI + "Novel_Approach:_The_Hiro_Collection"})

    # --- the HeroTruther videos ----------------------------------------------
    for video in ht.get("videos", []):
        if not video.get("d"):
            continue
        title = "HeroTruther: " + video["t"]
        rows.append({"d": video["d"], "k": "evo", "t": title,
                     "l": ht.get("wiki")})

    for n, date in (("1", "2015-11-19"), ("2", "2016-01-07")):
        rows.append({"d": date, "k": "evo",
                     "t": "Making of the Damen Peak Video, Part %s" % n})

    # --- what is on the discs ------------------------------------------------
    # Each extra is its own release, in the week its set came out, because that
    # is when it first existed -- several of these are the only surviving copy
    # of something that went out years earlier.
    for entry in discs.get("sets", []):
        season, date = entry["season"], entry["d"]
        for extra in discs.get("extras", {}).get(season, []):
            title = "%s: %s" % (SEASON_NAME[season], extra["t"])
            rows.append({"d": date, "k": "misc", "t": title})
            note = extra.get("b", "")
            if extra.get("rt"):
                note = "%s Runs about %s on %s." % (note, extra["rt"], entry["set"])
            elif entry.get("set"):
                note = "%s On %s." % (note, entry["set"])
            blurbs["misc"][title] = {"d": note.strip()}

        com = discs.get("commentaries", {}).get(season)
        if com:
            title = "%s Episode Commentaries" % SEASON_NAME[season]
            rows.append({"d": date, "k": "misc", "t": title,
                         "l": "https://tvacdb.sandboxen.com/series/heroes"})
            blurbs["misc"][title] = {"d":
                "%d tracks on %s, covering %s. Cast, directors and writers "
                "rotate through each one rather than sitting the whole episode."
                % (com["n"], entry["set"], com["eps"])}

    io.open(os.path.join(DATA, "additions.json"), "w", encoding="utf-8").write(
        json.dumps(rows, ensure_ascii=False, indent=1))
    io.open(os.path.join(DATA, "hand_extras.json"), "w", encoding="utf-8").write(
        json.dumps(blurbs, ensure_ascii=False, indent=1))

    by_kind = {}
    for row in rows:
        by_kind[row["k"]] = by_kind.get(row["k"], 0) + 1
    print("%d additions: %s" % (len(rows), ", ".join(
        "%d %s" % (n, k) for k, n in sorted(by_kind.items()))))
    print("%d hand-written blurbs" % sum(len(v) for v in blurbs.values()))
    for note in discs.get("corrections", []):
        print("  note: %s" % note)


if __name__ == "__main__":
    main()
