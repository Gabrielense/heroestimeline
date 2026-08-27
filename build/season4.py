# -*- coding: utf-8 -*-
"""Season four's premiere was one two-hour episode, not two.

The sheet lists "Orientation" and "Jump, Push, Fall" as 4x01 and 4x02, which
makes the season read as nineteen episodes and pushes every later code one
number too high -- the site called *Ink* 4x03 where Wikipedia and Heroes Wiki
both call it episode 2. Volume 5 ran eighteen episodes.

So the pair merges into a single item and the rest of the season shifts down.
Both sync.py (which writes the timeline codes) and extras.py (whose blurbs and
title cards are keyed by those codes) import this, so the two can never drift.

    4x01 + 4x02  ->  4x01  "Orientation / Jump, Push, Fall"
    4x03 .. 4x19 ->  4x02 .. 4x18
"""

MERGED_CODE = "4x01"
MERGED_TITLE = "Orientation / Jump, Push, Fall"
ABSORBED = "4x02"                       # the code that stops existing

# old code -> new code, for everything after the premiere
SHIFT = {"4x%02d" % n: "4x%02d" % (n - 1) for n in range(3, 20)}


def remap_code(code):
    """The code an old season-four number becomes. Anything else is returned
    unchanged, so this is safe to call on every code in the timeline."""
    return SHIFT.get(code, code)


def remap_keys(by_code):
    """Rebuild a {code: value} map onto the new numbering.

    The absorbed episode's own entry is dropped: its blurb and title card
    described the second hour of a premiere that is now one item, and the
    merged episode keeps 4x01's. Collisions cannot happen -- the shift only
    ever moves a code downwards into the slot the previous one just left.
    """
    out = {}
    for code, value in by_code.items():
        if code == ABSORBED:
            continue
        out[remap_code(code)] = value
    return out


def merge_entries(entries):
    """Collapse the premiere wherever it appears in a list of timeline weeks,
    then renumber the rest of the season. Returns how many codes it touched."""
    touched = 0
    for entry in entries:
        eps = (entry.get("c") or {}).get("ep")
        if not eps:
            continue
        keep = []
        for item in eps:
            code = item.get("c")
            if code == ABSORBED:
                touched += 1
                continue                # folded into 4x01 below
            if code == MERGED_CODE:
                item["t"] = MERGED_TITLE
                touched += 1
            elif code in SHIFT:
                item["c"] = SHIFT[code]
                touched += 1
            keep.append(item)
        if keep:
            entry["c"]["ep"] = keep
        else:
            del entry["c"]["ep"]
            if not entry["c"]:
                del entry["c"]
    return touched
