"""Bakes the where-to-watch fallback into index.html.

The page asks /api/watch for live offers. When that call cannot be made -- the
file opened straight off disk, the function cold-failing, JustWatch down -- it
falls back to the snapshot this script writes, so the panel still says something
useful instead of nothing. Snapshot countries are the three the page leads with;
every other country needs the live call.

The GraphQL query here is the same one api/watch.js sends, and the shape it
writes is the same shape the function returns, so whatever renders one renders
the other.

    python build/watch_snapshot.py            # refresh and inline

Run it from the project root.
"""

import io
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import date

ENDPOINT = 'https://apis.justwatch.com/graphql'
IMAGES = 'https://images.justwatch.com'

SHOWS = [('heroes', 'ts20598'), ('reborn', 'ts21672')]
SNAPSHOT_COUNTRIES = [('US', 'en'), ('GB', 'en'), ('BR', 'pt')]

QUERY = """
query Watch($heroes: ID!, $reborn: ID!, $country: Country!, $language: Language!) {
  heroes: node(id: $heroes) { ...Title }
  reborn: node(id: $reborn) { ...Title }
}
fragment Title on MovieOrShow {
  content(country: $country, language: $language) { title fullPath }
  offers(country: $country, platform: WEB) { ...Offer }
  ... on Show {
    seasons {
      content(country: $country, language: $language) { seasonNumber fullPath }
      offers(country: $country, platform: WEB) { ...Offer }
    }
  }
}
fragment Offer on Offer {
  monetizationType
  standardWebURL
  package { clearName packageId icon }
}
"""

KIND = {
    'FLATRATE': 'stream', 'FLATRATE_AND_BUY': 'stream', 'CINEMA': None,
    'FREE': 'free', 'ADS': 'free',
    'RENT': 'rent', 'BUY': 'buy',
}
ORDER = {'stream': 0, 'free': 1, 'rent': 2, 'buy': 3}


def icon_url(tpl):
    if not tpl:
        return ''
    return IMAGES + tpl.replace('{profile}', 's100').replace('{format}', 'png')


CAP = 6          # per kind; the JustWatch link covers the long tail


def offers(raw):
    """One entry per provider per kind, in JustWatch's own order.

    Deduped on the destination as well as the provider: the ad-supported tiers
    ("Netflix Standard with Ads", "Amazon Prime Video with Ads") are separate
    packages pointing at the very same page, and listing both twice says
    nothing a reader can act on.
    """
    out, seen, kept = [], set(), {}
    for o in raw or []:
        kind = KIND.get(o.get('monetizationType'))
        url = o.get('standardWebURL')
        pkg = o.get('package') or {}
        if not kind or not url or not pkg.get('clearName'):
            continue
        keys = ((kind, 'p', pkg.get('packageId')), (kind, 'u', url))
        if any(k in seen for k in keys) or kept.get(kind, 0) >= CAP:
            continue
        seen.update(keys)
        kept[kind] = kept.get(kind, 0) + 1
        out.append({'k': kind, 'n': pkg['clearName'], 'i': icon_url(pkg.get('icon')), 'u': url})
    out.sort(key=lambda o: ORDER[o['k']])
    return out


def page(path):
    return 'https://www.justwatch.com' + path if path else ''


def show(node):
    if not node:
        return None
    content = node.get('content') or {}
    out = {'t': content.get('title') or '', 'u': page(content.get('fullPath')),
           'o': offers(node.get('offers')), 's': {}}
    for season in node.get('seasons') or []:
        c = season.get('content') or {}
        n = c.get('seasonNumber')
        if n is None:
            continue
        out['s'][str(n)] = {'u': page(c.get('fullPath')), 'o': offers(season.get('offers'))}
    return out


def fetch(country, language):
    body = json.dumps({'query': QUERY, 'variables': {
        'heroes': SHOWS[0][1], 'reborn': SHOWS[1][1],
        'country': country, 'language': language}}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get('errors'):
        raise RuntimeError(json.dumps(payload['errors'])[:400])
    data = payload.get('data') or {}
    return {key: show(data.get(key)) for key, _ in SHOWS}


def inline(root, snapshot):
    """Replace the #watch-fallback block in index.html, in place."""
    path = os.path.join(root, 'index.html')
    html = io.open(path, encoding='utf-8', newline='').read()
    tag = '<script type="application/json" id="watch-fallback">'
    if tag not in html:
        print('index.html has no #watch-fallback block -- snapshot not inlined')
        return False
    blob = json.dumps(snapshot, ensure_ascii=False, separators=(',', ':'))
    html = re.sub(re.escape(tag) + r'.*?</script>', tag + blob + '</script>', html, count=1, flags=re.S)
    io.open(path, 'w', encoding='utf-8', newline='').write(html)
    print('inlined %d bytes into index.html' % len(blob))
    return True


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    snapshot = {'d': date.today().isoformat()}
    for country, language in SNAPSHOT_COUNTRIES:
        try:
            snapshot[country] = fetch(country, language)
        except (urllib.error.URLError, RuntimeError, ValueError) as err:
            print('%s failed: %s' % (country, err))
            return 1
        counts = ', '.join('%s %d' % (k, len(v['o'])) for k, v in snapshot[country].items() if v)
        print('%s ok (%s)' % (country, counts))

    out = os.path.join(root, 'build', 'data', 'watch_snapshot.json')
    io.open(out, 'w', encoding='utf-8').write(json.dumps(snapshot, ensure_ascii=False, indent=1))
    print('wrote %s' % out)
    inline(root, snapshot)
    return 0


if __name__ == '__main__':
    sys.exit(main())
