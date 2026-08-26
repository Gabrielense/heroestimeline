"""Blurbs for the physical-media panel.

The obvious source for "what is this and where do I buy it" is the shop listing
itself, and for these 32 objects that shop is Amazon. Amazon has no open API:
the Product Advertising API needs an Associates account with three qualifying
sales before it issues keys, and the public site answers a script with 503 or a
captcha. Everything else keyless was tried and came up short -- Apple's Search
API carries almost none of this catalogue outside the US, Google Books answers
429 without a key, Open Library holds the editions but almost no descriptions.

So the blurb comes from Wikipedia, which does have a page for every group of
objects here, is keyless, and can be quoted with attribution. It is written once
per *group* (a season, the score, the graphic novels) rather than per object,
because that is the level at which the text is actually true -- the four DVD
sets of season one all describe the same season.

    python build/buy_blurbs.py

Rewrites the #buy-data block in index.html. Run from the project root.
"""

import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

API = 'https://en.wikipedia.org/api/rest_v1/page/summary/'
UA = {'User-Agent': 'heroestimeline/1.0 (https://github.com/Gabrielense/heroestimeline)'}

# keys must match buyGroup() in index.html
GROUPS = [
    ('s1',      'Heroes season 1'),
    ('s2',      'Heroes season 2'),
    ('s3',      'Heroes season 3'),
    ('s4',      'Heroes season 4'),
    ('series',  'Heroes (American TV series)'),
    ('reborn',  'Heroes Reborn (miniseries)'),
    ('music',   'Music of Heroes'),
    ('comics',  'List of Heroes graphic novels'),
    ('charlie', 'Heroes: Saving Charlie'),
]

LIMIT = 320          # a blurb, not an article


def summary(title):
    url = API + urllib.parse.quote(title.replace(' ', '_'), safe='():,')
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def trim(text):
    """First sentences that fit inside LIMIT, never a mid-sentence cut."""
    text = re.sub(r'\s+', ' ', (text or '')).strip()
    if len(text) <= LIMIT:
        return text
    cut = text[:LIMIT]
    stop = max(cut.rfind('. '), cut.rfind('! '), cut.rfind('? '))
    return (cut[:stop + 1] if stop > 80 else cut.rstrip() + '…').strip()


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = {'d': date.today().isoformat(), 'g': {}}
    for key, title in GROUPS:
        try:
            d = summary(title)
        except urllib.error.HTTPError as e:
            print('%-8s %s -> HTTP %s (skipped)' % (key, title, e.code))
            continue
        blurb = trim(d.get('extract'))
        if not blurb:
            print('%-8s %s -> empty (skipped)' % (key, title))
            continue
        out['g'][key] = {
            't': d.get('title') or title,
            'b': blurb,
            'u': (((d.get('content_urls') or {}).get('desktop') or {}).get('page')
                  or 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(title.replace(' ', '_')))
        }
        print('%-8s %s (%d chars)' % (key, out['g'][key]['t'], len(blurb)))

    path = os.path.join(root, 'index.html')
    html = io.open(path, encoding='utf-8', newline='').read()
    tag = '<script type="application/json" id="buy-data">'
    if tag not in html:
        print('index.html has no #buy-data block -- nothing written')
        return 1
    blob = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
    html = re.sub(re.escape(tag) + r'.*?</script>', tag + blob + '</script>', html, count=1, flags=re.S)
    io.open(path, 'w', encoding='utf-8', newline='').write(html)
    print('inlined %d bytes into index.html' % len(blob))
    return 0


if __name__ == '__main__':
    sys.exit(main())
