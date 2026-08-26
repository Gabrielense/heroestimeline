/* Where to watch, per country.
 *
 * JustWatch has no public REST API and its GraphQL endpoint sends no CORS
 * headers, so the page cannot ask it directly. This proxies one request per
 * country, flattens the answer into the shape the panel renders, and lets the
 * edge cache hold it -- these offers change on the order of weeks.
 *
 *   GET /api/watch        country guessed from the caller (Vercel's geo header)
 *   GET /api/watch?c=BR   that country, whatever the caller's IP says
 *
 * The response is { c, auto, shows: { heroes, reborn } }, and `shows` is the
 * same shape build/watch_snapshot.py bakes into index.html as a fallback, so
 * one renderer covers both. No key, no account, nothing to configure.
 */

const ENDPOINT = 'https://apis.justwatch.com/graphql';
const IMAGES = 'https://images.justwatch.com';

const HEROES = 'ts20598';        /* Heroes (2006)        */
const REBORN = 'ts21672';        /* Heroes Reborn (2015) */

const CAP = 6;                   /* offers kept per kind; the JustWatch link covers the tail */
const TIMEOUT = 8000;

/* Any country JustWatch knows is fair game -- the page's picker is only a
 * shortlist. An unknown one comes back as an upstream error and the page falls
 * back to its own links, which is the same thing an allowlist would do, minus
 * the maintenance. The language only decides the wording JustWatch returns. */
const LANGUAGE = {
  BR: 'pt', PT: 'pt',
  ES: 'es', MX: 'es', AR: 'es', CL: 'es', CO: 'es', PE: 'es',
  FR: 'fr', BE: 'fr',
  DE: 'de', AT: 'de', CH: 'de',
  IT: 'it', NL: 'nl', PL: 'pl', SE: 'sv', NO: 'no', DK: 'da', FI: 'fi',
  JP: 'ja', KR: 'ko', TR: 'tr', RU: 'ru'
};

const QUERY = `
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
}`;

const KIND = {
  FLATRATE: 'stream', FLATRATE_AND_BUY: 'stream',
  FREE: 'free', ADS: 'free',
  RENT: 'rent', BUY: 'buy'
};
const ORDER = { stream: 0, free: 1, rent: 2, buy: 3 };

function iconUrl(tpl) {
  return tpl ? IMAGES + tpl.replace('{profile}', 's100').replace('{format}', 'png') : '';
}

function page(path) {
  return path ? 'https://www.justwatch.com' + path : '';
}

/* One entry per provider per kind, in JustWatch's own order. Deduped on the
 * destination as well as the provider: the ad-supported tiers ("Netflix
 * Standard with Ads") are separate packages pointing at the very same page. */
function offers(raw) {
  const out = [], seen = new Set(), kept = {};
  for (const o of raw || []) {
    const kind = KIND[o && o.monetizationType];
    const url = o && o.standardWebURL;
    const pkg = (o && o.package) || {};
    if (!kind || !url || !pkg.clearName) continue;
    const byPkg = kind + '|p|' + pkg.packageId, byUrl = kind + '|u|' + url;
    if (seen.has(byPkg) || seen.has(byUrl) || (kept[kind] || 0) >= CAP) continue;
    seen.add(byPkg); seen.add(byUrl);
    kept[kind] = (kept[kind] || 0) + 1;
    out.push({ k: kind, n: pkg.clearName, i: iconUrl(pkg.icon), u: url });
  }
  out.sort((a, b) => ORDER[a.k] - ORDER[b.k]);
  return out;
}

function show(node) {
  if (!node) return null;
  const content = node.content || {};
  const out = { t: content.title || '', u: page(content.fullPath), o: offers(node.offers), s: {} };
  for (const season of node.seasons || []) {
    const c = season.content || {};
    if (c.seasonNumber === null || c.seasonNumber === undefined) continue;
    out.s[String(c.seasonNumber)] = { u: page(c.fullPath), o: offers(season.offers) };
  }
  return out;
}

async function justwatch(country) {
  const stop = new AbortController();
  const timer = setTimeout(() => stop.abort(), TIMEOUT);
  try {
    const r = await fetch(ENDPOINT, {
      method: 'POST',
      signal: stop.signal,
      headers: {
        'content-type': 'application/json',
        /* JustWatch turns away obviously scripted callers */
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) heroestimeline'
      },
      body: JSON.stringify({
        query: QUERY,
        variables: {
          heroes: HEROES, reborn: REBORN,
          country: country, language: LANGUAGE[country] || 'en'
        }
      })
    });
    if (!r.ok) throw new Error('justwatch http ' + r.status);
    const payload = await r.json();
    if (payload.errors) throw new Error('justwatch: ' + JSON.stringify(payload.errors).slice(0, 200));
    const data = payload.data || {};
    return { heroes: show(data.heroes), reborn: show(data.reborn) };
  } finally {
    clearTimeout(timer);
  }
}

module.exports = async function handler(req, res) {
  res.setHeader('access-control-allow-origin', '*');
  if (req.method === 'OPTIONS') { res.status(204).end(); return; }
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.setHeader('cache-control', 'no-store');
    res.status(405).json({ error: 'method not allowed' });
    return;
  }

  const asked = String((req.query && req.query.c) || '').toUpperCase();
  const auto = !/^[A-Z]{2}$/.test(asked);
  const country = auto
    ? String(req.headers['x-vercel-ip-country'] || 'US').toUpperCase()
    : asked;

  /* Without ?c the answer depends on the caller's IP, so it must not be shared
   * by the CDN. The page asks that way once, remembers what came back, and
   * pins ?c on every request after -- and those cache. */
  res.setHeader('cache-control', auto
    ? 'no-store'
    : 'public, s-maxage=21600, stale-while-revalidate=604800');

  if (!/^[A-Z]{2}$/.test(country)) {
    res.status(400).json({ error: 'bad country' });
    return;
  }

  try {
    const shows = await justwatch(country);
    res.status(200).json({ c: country, auto: auto, shows: shows });
  } catch (err) {
    res.setHeader('cache-control', 'no-store');
    res.status(502).json({ c: country, error: String((err && err.message) || err) });
  }
};
