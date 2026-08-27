# -*- coding: utf-8 -*-
"""Turn the hand-written data files into the two the page is built from.

Nothing here is scraped. It folds together:

  data/disc_extras.json   what is on the DVDs and Blu-rays, and the commentaries
  data/herotruther.json   the five lost videos (written by build/herotruther.py)
  data/manual_extras.json the hand-written layer: releases no sheet row covers,
                          and blurbs no collector can reach

and writes:

  data/additions.json     rows for sync.py to fold into the timeline
  data/hand_extras.json   their blurbs, for extras.py

Both outputs are generated in full every run. Nothing is edited by hand in
either of them -- put it in manual_extras.json instead.

    py build/make_additions.py
"""
import io, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

WIKI = "https://web.archive.org/web/20200514171611/https://heroeswiki.com/"

GROUPS = ("gn", "ep", "web", "evo", "bts", "site", "istory", "phys", "misc")

# What each set's extras are called on the page. The prefix does two jobs: it
# says which box the thing is in, and it keeps "Genetics of a Scene" -- which
# exists on three of them -- from colliding with itself.
SET_NAME = {"s1": "Season 1 Extras", "s1ce": "Collector's Edition Extras",
            "s2": "Season 2 Extras", "s3": "Season 3 Extras",
            "s4": "Season 4 Extras", "hr": "Heroes Reborn Extras"}


def load(name, default=None):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return default if default is not None else {}
    return json.load(io.open(path, encoding="utf-8"))


def main():
    discs = load("disc_extras.json")
    ht = load("herotruther.json")
    manual = load("manual_extras.json")

    rows = []
    blurbs = {g: {} for g in GROUPS}
    for group, recs in (manual.get("blurbs") or {}).items():
        blurbs.setdefault(group, {}).update(recs)

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

    # --- releases written straight into manual_extras.json --------------------
    for row in manual.get("rows", []):
        rows.append(dict(row))

    # --- what is on the discs ------------------------------------------------
    # Each extra is its own release, in the week its set came out, because that
    # is when it first existed. The ones that had already gone out somewhere
    # else -- Sword Saint, the Drucker report, three webisode series -- are not
    # here at all: they are listed on the day they appeared, and the panel says
    # the discs carry them too. disc_extras.json's "not_entries" says which.
    for entry in discs.get("sets", []):
        season, date = entry["season"], entry["d"]
        for extra in discs.get("extras", {}).get(season, []):
            title = "%s: %s" % (SET_NAME[season], extra["t"])
            row = {"d": date, "k": extra.get("k", "bts"), "t": title}
            if entry.get("src"):
                row["l"] = entry["src"]
            rows.append(row)
            note = extra.get("b", "")
            if extra.get("rt"):
                note = "%s Runs about %s on %s." % (note, extra["rt"], entry["set"])
            elif entry.get("set"):
                note = "%s On %s." % (note, entry["set"])
            rec = {"d": note.strip()}
            # No extra has cover art of its own. The box it came in does, and
            # extras.py resolves this to whatever picture that release carries.
            if entry.get("art"):
                rec["artof"] = entry["art"]
            blurbs[row["k"]][title] = rec

        com = discs.get("commentaries", {}).get(season)
        if com:
            title = "%s: Episode Commentaries" % SET_NAME[season]
            rows.append({"d": date, "k": "bts", "t": title,
                         "l": "https://tvacdb.sandboxen.com/series/heroes"})
            rec = {"d":
                   "%d tracks on %s, covering %s. Cast, directors and writers "
                   "rotate through each one rather than sitting the whole episode."
                   % (com["n"], entry["set"], com["eps"])}
            if entry.get("art"):
                rec["artof"] = entry["art"]
            blurbs["bts"][title] = rec

    # manual blurbs win over anything generated above, so a disc extra can be
    # rewritten by hand without unpicking disc_extras.json
    for group, recs in (manual.get("blurbs") or {}).items():
        blurbs.setdefault(group, {}).update(recs)

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
    for note in discs.get("not_entries", []):
        print("  not an entry: %s" % note.split(" -- ")[0])


if __name__ == "__main__":
    main()
