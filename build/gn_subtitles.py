# -*- coding: utf-8 -*-
"""Collect the second half of a graphic novel's name.

Many novels are billed as "Amanda's Journey, Part 1 - When Everything Changed":
a running title, then the subtitle that issue actually carries. The sheet only
ever held the first half, and Wikipedia's list does not record the second.

Heroes Wiki does, but only sideways -- the subtitle is the name of the issue's
title card, not a field on the page. So this reads the title-card image's own
filename and keeps it when it says something the running title does not.

That works for a good many and not for all: some pages name the title card
after the issue, and those subtitles are simply not recorded anywhere this can
reach. Those come back in "gaps" for a human to fill rather than guessed at.

    py build/gn_subtitles.py
"""
import io, json, os, re, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
HTML = os.path.join(HERE, os.pardir, "index.html")
OUT = os.path.join(DATA, "gn_subtitles.json")

# Subtitles that are real but recorded nowhere this script can read them, so
# they are written down by hand. Anything added here must come from the issue
# itself, not from a guess.
KNOWN = {
    "166": "1963, Part 1",
}

# a title card whose name is one of these says nothing about a subtitle
NOISE = re.compile(r"^(?:cover|title|untitled|novel|issue)$", re.I)


def card_name(url):
    """The image's own name, without the thumbnail prefix or the _title tail."""
    base = urllib.parse.unquote(url.rsplit("/", 1)[-1])
    base = re.sub(r"^\d+px-", "", base)
    base = re.sub(r"\.(jpg|jpeg|png|gif)$", "", base, flags=re.I)
    base = re.sub(r"[_ ]*title$", "", base, flags=re.I)
    return base.replace("_", " ").strip()


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def initials(s):
    return "".join(w[0] for w in re.findall(r"[A-Za-z]+", s)).lower()


def is_subtitle(candidate, title):
    """Keep a candidate only when it is genuinely a different name.

    Rules out the common cases: the card named after the issue, the card named
    after the issue minus its part number, an abbreviation like IFT for Isaac's
    First Time, and single bare words that carry no information.
    """
    if not candidate or NOISE.match(candidate):
        return False
    c, t = norm(candidate), norm(title)
    if not c or c == t or c in t or t in c:
        return False
    if c == initials(title) or len(c) <= 3:
        return False
    if len(candidate.split()) < 2:
        return False
    # "War Buddies 3" against "War Buddies, Part 3", or "Death of Hana 1"
    # against "The Death of Hana Gitelman, Part 1": the card is just the issue
    # named more loosely. A real subtitle says something the title does not.
    words = lambda s: set(re.findall(r"[a-z]+", s.lower())) - {"part", "the"}
    if words(candidate) <= words(title):
        return False
    return True


def titlecase(s):
    """The wiki files these in sentence case; the page shows them as names."""
    small = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in",
             "of", "on", "or", "the", "to", "with"}
    words = s.split()
    out = []
    for i, w in enumerate(words):
        if w.isupper() or any(ch.isdigit() for ch in w):
            out.append(w)
        elif i and w.lower() in small:
            out.append(w.lower())
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)


def main():
    html = io.open(HTML, encoding="utf-8").read()
    data = json.loads(re.search(
        r'<script type="application/json" id="timeline-data">(.*?)</script>',
        html, re.S).group(1))
    cards = json.load(io.open(os.path.join(DATA, "gn_wiki.json"),
                              encoding="utf-8")).get("found", {})

    titles = {}
    for entry in data["entries"]:
        for item in (entry.get("c") or {}).get("gn", []):
            if item.get("c"):
                titles[item["c"]] = item["t"]

    subs, gaps = dict(KNOWN), []
    for code, title in sorted(titles.items()):
        if code in subs:
            continue
        url = (cards.get(code) or {}).get("card")
        if not url:
            gaps.append({"c": code, "t": title, "why": "no title card on the wiki"})
            continue
        candidate = card_name(url)
        if is_subtitle(candidate, title):
            subs[code] = titlecase(candidate)

    named = len(subs)
    print("%d novels | %d subtitles | %d with no title card to read"
          % (len(titles), named, len(gaps)))
    for code in sorted(subs, key=lambda c: int(re.sub(r"\D", "", c) or 0)):
        print("  #%-5s %s" % (code, subs[code]))

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(
        {"subtitles": subs, "gaps": gaps}, ensure_ascii=False, indent=1))
    print("\nwrote %s" % OUT)


if __name__ == "__main__":
    main()
