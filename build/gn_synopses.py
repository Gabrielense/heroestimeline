# -*- coding: utf-8 -*-
"""Extract per-issue graphic novel facts from Wikipedia's list article.

Wikipedia is CC BY-SA: derivatives and commercial use are both allowed, with
attribution and a share-alike notice. That is why the novel blurbs come from
here rather than from heroeswiki, whose text is CC BY-NC-ND.

    py build/gn_synopses.py        # writes build/data/gn_synopses.json
"""
import json, os, re, sys, urllib.request

SRC = ("https://en.wikipedia.org/w/index.php"
       "?title=List_of_Heroes_graphic_novels&action=raw")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "gn_synopses.json")
CACHE = os.path.join(HERE, "data", "gn_list.wiki")


def source():
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        return open(CACHE, encoding="utf-8").read()
    req = urllib.request.Request(SRC, headers={"User-Agent": "heroes-timeline/1.0"})
    body = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    open(CACHE, "w", encoding="utf-8").write(body)
    return body


def clean(s):
    s = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", "", s, flags=re.S)
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)      # [[a|b]] -> b
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)               # [[a]]   -> a
    s = re.sub(r"'''?", "", s)
    s = re.sub(r"\{\{[^}]*\}\}", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    wiki = source()

    # each issue row opens with a bare number cell; everything up to the next
    # such cell belongs to that issue
    marks = [(int(m.group(1)), m.start(), m.end()) for m in
             re.finditer(r'(?m)^\|\s*(?:rowspan="2"\s*\|\s*)?(\d{1,3})\s*$', wiki)]
    out = {}
    for i, (num, start, end) in enumerate(marks):
        block = wiki[end: marks[i + 1][1] if i + 1 < len(marks) else end + 2500]
        rec = {}
        t = re.search(r"\|title=\s*([^|}]+?)\s*[|}]", block)
        if t:
            rec["title"] = clean(t.group(1))
        d = re.search(r"(?m)^\|\s*(\d{4}-\d{2}-\d{2})\s*$", block)
        if d:
            rec["date"] = d.group(1)
        # capture the whole line: a piped [[link|label]] would truncate on '|'
        syn = re.search(r'\|\s*colspan="4"\s*\|\s*([^\n]+)', block)
        if syn:
            s = clean(syn.group(1))
            if len(s) > 15:
                rec["desc"] = s
        credits = re.findall(r"(?m)^\|([A-Z][^\n|]{2,40})$", block)
        credits = [clean(c) for c in credits if not re.match(r"^\d", c.strip())]
        if len(credits) >= 2:
            rec["writer"], rec["artist"] = credits[0], credits[1]
        if rec.get("desc") or rec.get("title"):
            out[str(num)] = rec

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    withdesc = sum(1 for v in out.values() if v.get("desc"))
    withcred = sum(1 for v in out.values() if v.get("writer"))
    print("%d issues | %d with a blurb | %d with credits -> %s"
          % (len(out), withdesc, withcred, os.path.relpath(OUT, HERE)))
    sample = out.get("1") or next(iter(out.values()))
    print("sample:", json.dumps(sample, ensure_ascii=False)[:220])


if __name__ == "__main__":
    main()
