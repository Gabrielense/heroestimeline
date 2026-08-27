# -*- coding: utf-8 -*-
"""The HeroTruther videos, which no longer exist anywhere.

Five videos went up on a YouTube channel during the Heroes Reborn campaign in
2015. The channel was deleted, the account name was later taken by somebody
unrelated -- which is what the timeline's link still points at -- and the videos
themselves are gone. Heroes Wiki wrote down what was in them, so that account
is all that is left.

This reads the wiki's section per video and keeps the title, the date it went
up, and what it showed.

    py build/herotruther.py
"""
import io, json, os, re, time, urllib.parse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(DATA, "herotruther.json")

PAGE = "https://heroeswiki.ddns.net/wiki/HeroTruther"
UA = {"User-Agent": "heroes-timeline/1.0 (https://github.com/Gabrielense/heroestimeline)"}

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return None
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def strip(s):
    s = re.sub(r"(?s)<(script|style|table)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<div class=\"(?:thumb|toc)[^\"]*\".*?</div>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), s)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&quot;", '"'),
                 ("&#039;", "'"), ("&lt;", "<"), ("&gt;", ">")):
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s)
    # Dropping the tags leaves a space wherever a link sat, which lands in front
    # of the punctuation that followed it and inside every quoted phrase.
    s = re.sub(r"\s+([.,;:!?])", r"\1", s)
    s = re.sub(r'(^|\s)"\s+', r'\1"', s)      # space after an opening quote
    s = re.sub(r'\s+"(\s|$|[.,])', r'"\1', s)  # space before a closing one
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)
    return s.strip()


def iso(text):
    m = re.search(r"(%s)\s+(\d{1,2}),\s*(\d{4})" % "|".join(MONTHS), text)
    if not m:
        return None
    return "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(1)], int(m.group(2)))


def trim(text, cap=300):
    if len(text) <= cap:
        return text
    cut, out = text[:cap], ""
    for sent in re.split(r"(?<=[.!?]) ", cut):
        if len(out) + len(sent) + 1 > cap:
            break
        out += sent + " "
    return (out or cut).strip()


def sections(html):
    """(heading, body html) for every h3 under the Heroes Evolutions heading.

    This wiki renders headings as <h3 id="...">Text</h3>, not the older
    <span class="mw-headline"> form, and the table of contents repeats every
    id -- so start from the *second* time the section heading appears.
    """
    hits = [m.start() for m in re.finditer(r'<h2 id="Heroes_Evolutions"', html)]
    if not hits:
        return []
    start = hits[-1]
    end = html.find('<h2 id="History"', start)
    chunk = html[start:end if end > start else len(html)]
    parts = re.split(r'<h3 id="[^"]*">(.*?)</h3>', chunk, flags=re.S)
    out = []
    for i in range(1, len(parts) - 1, 2):
        out.append((strip(parts[i]), parts[i + 1]))
    return out


def main():
    html = get(PAGE)
    if not html:
        raise SystemExit("could not read %s" % PAGE)

    videos = []
    for title, body in sections(html):
        text = strip(body)
        videos.append({
            "t": title,
            "d": iso(text),
            "b": trim(text),
        })

    # The channel the timeline links to today is somebody else's; the original
    # was deleted. A capture from the campaign is the honest thing to point at.
    channel = None
    for m in re.finditer(r'href="(https?://[^"]*youtube\.com/[^"]+)"', html):
        channel = m.group(1)
        break
    archive = None
    if channel:
        probe = get("https://archive.org/wayback/available?url=%s&timestamp=2015"
                    % urllib.parse.quote(channel, safe=""))
        if probe:
            try:
                snap = json.loads(probe).get("archived_snapshots", {}).get("closest")
                if snap and snap.get("available"):
                    archive = snap["url"]
            except ValueError:
                pass

    out = {
        "channel": channel,
        "channel_archive": archive,
        "channel_note": "The original channel was deleted; the name now belongs "
                        "to an unrelated account, so the live link goes nowhere "
                        "near these videos.",
        "videos": videos,
        "wiki": PAGE,
    }
    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))

    print("%d videos" % len(videos))
    for v in videos:
        print("  %-11s %-46s %d chars" % (v["d"] or "no date", v["t"][:46],
                                          len(v["b"])))
    print("channel:", channel or "none found")
    print("archive:", archive or "none found")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
