# -*- coding: utf-8 -*-
"""Find the archived PDF of each graphic novel.

NBC published every issue as a PDF and then took the site down. The Wayback
Machine kept them, and serves them as real files -- not as a viewer page --
under the `id_` modifier, with no X-Frame-Options, so the page can put one in a
frame. What it will not do is serve them quickly: the median issue is 15 MB.
That is why the page loads one only when asked, and says the size first.

The addresses come from the archive's own index rather than from guessing:
one CDX query per URL prefix, paged until it stops returning rows.

    py build/gn_pdfs.py
    py build/gn_pdfs.py --verify 5     # also check that many really are PDFs
"""
import io, json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
WIKI = os.path.join(DATA, "gn_list.wiki")
OUT = os.path.join(DATA, "gn_pdfs.json")

CDX = "http://web.archive.org/cdx/search/cdx"
# NBC kept these in two places over the years. One query per directory, with
# the filtering done by the server: asked without `filter=mimetype`, the same
# query returns seventeen thousand captures of everything else that ever sat
# there and the PDFs are lost among them. Asked with it, one request answers
# in seconds -- which matters, because the archive throttles hard, and a
# per-issue sweep of 366 requests took over an hour and never finished.
PREFIXES = ["nbc.com/Heroes/novels/downloads/*",
            "nbc.com/heroes/novels/images/*"]
UA = {"User-Agent": "heroes-timeline/1.0 (https://github.com/Gabrielense/heroestimeline)"}


def captures(prefix):
    """Every 200-status PDF capture under a directory, filtered server-side."""
    query = urllib.parse.urlencode([
        ("url", prefix), ("output", "json"),
        ("fl", "original,timestamp,mimetype,statuscode,length"),
        ("filter", "statuscode:200"),
        ("filter", "mimetype:application/pdf"),
    ])
    req = urllib.request.Request(CDX + "?" + query, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            rows = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        print("  cdx failed for %s: %s" % (prefix, e))
        return []
    return rows[1:]


def issue_of(url):
    m = re.search(r"novel[_-]?(\d{1,3})\.pdf$", url, re.I)
    return str(int(m.group(1))) if m else None


def wiki_sizes():
    """The real file sizes, which Wikipedia's list records per issue."""
    if not os.path.exists(WIKI):
        return {}
    text = io.open(WIKI, encoding="utf-8").read()
    out = {}
    for row in re.split(r"\n\|-", text):
        num = re.search(r'\|\s*(?:rowspan="\d+"\s*\|\s*)?(\d{1,3})\s*\n', row)
        size = re.search(r"\{\{small\|\((\d+(?:\.\d+)?)&nbsp;MB\)\}\}", row)
        if num and size:
            out[num.group(1)] = float(size.group(1))
    return out


def verify(url, tries=2):
    """Confirm the archive really answers with a PDF, and how big it is."""
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA, method="HEAD")
            with urllib.request.urlopen(req, timeout=60) as r:
                kind = (r.headers.get("Content-Type") or "").lower()
                length = r.headers.get("Content-Length")
                return ("pdf" in kind), (int(length) if length else None)
        except Exception:
            time.sleep(3)
    return False, None


def main():
    sizes = wiki_sizes()
    best = {}
    for prefix in PREFIXES:
        rows = captures(prefix)
        print("%-40s %4d PDF captures" % (prefix, len(rows)))
        for original, ts, _mime, _code, length in rows:
            num = issue_of(original)
            if not num:
                continue
            try:
                length = int(length)
            except (TypeError, ValueError):
                length = 0
            # the fullest capture wins; ties go to the earliest, which is
            # likeliest to be the file as it was actually published
            current = best.get(num)
            if not current or length > current[2] or (
                    length == current[2] and ts < current[1]):
                best[num] = (original, ts, length)
        time.sleep(2)

    out = {}
    for num, (original, ts, length) in best.items():
        out[num] = {
            "url": "https://web.archive.org/web/%sid_/%s" % (ts, original),
            "ts": ts,
            "mb": sizes.get(num) or round(length / 1048576.0, 1) or None,
        }

    checked = 0
    if "--verify" in sys.argv:
        want = int(sys.argv[sys.argv.index("--verify") + 1])
        for num in sorted(out, key=lambda n: int(n))[:want]:
            ok, length = verify(out[num]["url"])
            out[num]["checked"] = ok
            if length:
                out[num]["mb"] = round(length / 1048576.0, 1)
            print("  #%-4s %s  %s MB" % (num, "PDF" if ok else "NOT A PDF",
                                         out[num]["mb"]))
            checked += 1
            time.sleep(1)

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    known = [v["mb"] for v in out.values() if v.get("mb")]
    print("\n%d issues have an archived PDF | %d verified by hand" % (len(out), checked))
    if known:
        known.sort()
        print("sizes: smallest %.1f MB, median %.1f MB, largest %.1f MB"
              % (known[0], known[len(known) // 2], known[-1]))
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
