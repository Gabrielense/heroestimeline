# Heroes: A Complete Multimedia Timeline

An interactive version of [the source spreadsheet](https://docs.google.com/spreadsheets/d/1Ci6zyz2nhjgrCurrhSDrD_jvtfXBLq_l9CWLpKDe3NE/edit) —
559 releases across 214 weeks and 7 parallel media, from the 2006 pilot to the
announcement of *Heroes: Eclipsed*.

`index.html` is the whole site: no build step, no dependencies, no bundler. Open
it directly or drop it on any static host. The one optional extra is
`api/watch.js`, a keyless serverless function behind the where-to-watch panel —
without it the page still works and falls back to a baked-in snapshot.

## What it does

- **Timeline view** — one row per week, releases grouped by medium, eras as
  sticky sections.
- **Grid view** — the original 8-column matrix, with the header row and date
  column pinned.
- **Compact mode** — collapses each week onto a single line (roughly halves the
  page height).
- **Activity rail** — one bar per week, height = releases that week, colour =
  era. Hover for detail, click to jump.
- **Volume markers** — short colour lines above the rail, each as wide as the
  weeks its volume covers; click one to jump. Off-air stretches hold their width
  and draw nothing.
- **Header tally** — one box per medium, split so iStory chapters are counted
  apart from the rest of the Evolutions material.
- **Where to watch** — per-country streaming, rental and purchase offers on any
  episode. See below.
- **Where to buy** — per-country listings and shop searches on any physical
  release, with a blurb. See below.
- **Search** across titles, episode/issue codes and dates (`2009-09` works).
- **Filters** by medium and by era, collapsed by default.
- **Play in place** — 59 entries open an Internet Archive player without leaving
  the page. See below.
- **Permalinks** — jumping to a week writes `#w<row>` to the URL.

## Watching things

Entries with a ▶ open an `archive.org/embed` player in a panel over the page.
Nothing is rehosted here; it streams from the Internet Archive, and every panel
links back to the item.

That covers all 46 *Heroes Unmasked* episodes, 12 of the 13 *Inside the Eclipse*
shorts — episode 9 is not on archive.org — and the **unaired pilot**, the one
episode of the series that was never broadcast and has never been sold
anywhere, which is why it has a player but no *where to watch*. The webisode
item is a single 1.4 GB ZIP and the graphic novels are five volume PDFs, so
neither can be deep-linked per entry yet; both stay as collection links in the
footer.

The *Unmasked* map lives in `UNMASKED_FILES` in `sync.py`. Regenerate it with:

```bash
py build/link_archive.py
```

It matches on **title, not episode code** — on purpose. The archive item counts
"A Heroes Welcome" and "The Story So Far" as episodes of their own, so from
episode 9 on its numbering runs one ahead of the sheet's, and matching by code
would silently shift 14 entries onto the wrong video. `--check` exits non-zero
if anything goes unmatched in either direction.

## Where to watch

Open any episode and the panel lists where that **season** can be streamed,
rented or bought in your country, with a picker to change country. Only the
televised run has anything to list — the novels, the ARG and the webisodes were
never licensed anywhere — so the section is absent everywhere else, and on the
unaired pilot.

The data is JustWatch's. Their GraphQL endpoint sends no CORS headers, so the
page cannot call it directly; `api/watch.js` proxies one request per country,
flattens the offers and lets the CDN hold the answer for six hours. It needs no
key, no account and no environment variables — deploying the folder to Vercel is
the whole setup.

Country comes from three places, in order: whatever the reader picked (kept in
`localStorage`), the caller's IP (Vercel's `x-vercel-ip-country`, read on the
one request the page makes without `?c=`), then the browser's own locale.
JustWatch answers for far more countries than the 25 in the picker, and any
two-letter code works if you pass it by hand.

When the function cannot be reached — the file opened off disk, the deploy
static-only, JustWatch down — the panel falls back to a snapshot inlined in
`index.html` and says how old it is. That snapshot covers US, GB and BR:

```bash
py build/watch_snapshot.py
```

It refreshes `build/data/watch_snapshot.json` and rewrites the `#watch-fallback`
block in `index.html` in place. It sends the same query and produces the same
shape as `api/watch.js`, so one renderer covers both. Worth re-running whenever
the show changes hands — it was last taken 26 Aug 2026, when *Heroes* was on
Netflix in all three and *Heroes Reborn* was nowhere in Brazil.

## Where to buy

Open any physical release — a disc set, a magazine, a book, a soundtrack, a
collected volume — and the panel shows a blurb and somewhere to get it, for your
country. It draws a hard line between two things:

- **Buy** — listings JustWatch has confirmed for that country, disc sellers
  included. Season one in the US resolves to an actual `amazon.com/dp/…` page.
- **Search** — a search on the shops that serve that country (Amazon's local
  marketplace plus eBay, or Mercado Livre in Brazil, Allegro in Poland, Yahoo!
  Auctions in Japan). A search page always resolves, so it can disappoint but it
  can never 404.

That split is the whole design, because **nothing here can be assumed to be on
sale**. Most of these objects are long out of print, and availability differs by
country — the season sets are buyable in the US and the UK and nowhere on
JustWatch's Brazilian listings.

### Why not just link to Amazon

Amazon has no open API. The Product Advertising API issues keys only to
Associates accounts that have already made three qualifying sales, and the
public site answers a script with 503 or a captcha — worse, `amazon.com/dp/<any
ISBN>` returns HTTP 200 whether or not that marketplace carries the book, so a
product link cannot even be validated by fetching it. Guessing one would mean
shipping links that quietly go nowhere.

Everything else keyless was tried and came up short:

| Source | Verdict |
| --- | --- |
| **JustWatch** | Works. Per-country, confirmed, includes disc sellers. Only covers the show itself — no books, magazines or albums. |
| **Apple / iTunes Search** | Keyless and per-country, and `lookup?id=&country=` is a real availability test. But its catalogue holds almost none of this outside the US. |
| **Google Books** | 429 without an API key, every time. |
| **Open Library** | Solid edition data and ISBNs, almost no descriptions. Searching it by title returned a *Lunar Jim* annual for "Heroes Revealed" — fuzzy title matching is not safe here. |
| **MusicBrainz** | Keyless, finds the soundtracks with barcodes. No purchase links. |
| **Wikipedia** | Keyless, reliable, has a page for every group of objects here. Blurbs only. |

So the links come from JustWatch where they can be confirmed and from search
everywhere else, and the blurb comes from Wikipedia with attribution.

### Blurbs

Written per *group* rather than per object — the four DVD editions of season one
all describe the same season — keyed to `BUY_GROUPS` in `index.html`:

```bash
py build/buy_blurbs.py
```

It rewrites the `#buy-data` block. Nine groups have one (the four seasons, the
series, *Reborn*, the score, the graphic novels, *Saving Charlie*); the
magazines and *Heroes Revealed* have no Wikipedia page, so they get search links
and no blurb rather than an invented one.

## Refreshing the data

The sheet's contents live in one `<script type="application/json"
id="timeline-data">` block inside `index.html`. To pull in edits made to the
spreadsheet:

```bash
py build/sync.py
```

It downloads the sheet, re-parses it, and rewrites only that block — everything
else in `index.html` is left alone, so the page can be hand-edited freely. Use
`--offline` to re-parse the already-downloaded `build/sheet.xlsx`. Needs
`openpyxl`.

## Two things the parser handles

**Dates.** The spreadsheet's locale is day-first, but the dates were typed
month-first. Every value Sheets actually parsed therefore came out with its day
and month swapped (`10/2/2006` was stored as 2 October → 10 February); values
whose first number was over 12 were never parsed and stayed literal text. The
sync script swaps the parsed ones back. The check that this is right: with the
swap, all 210 dates land in strict chronological order and 180 of them fall on a
Monday. Without it, they don't.

**Eras.** The sheet encodes them as cell fill colours, not as a column. The five
volumes use one green ramp, *Heroes Reborn* uses gold, and off-air stretches use
a near-black that the legend doesn't name. Those map to `v1`–`v5`, `hr` and
`gap` in `sync.py`.

## Corrections

`sync.py` patches 31 entries on the way through — see `TITLE_FIXES`, `ROW_FIXES`,
`DATE_LABELS` and `EXTRA_LINKS` there. They are applied in the pipeline rather than in the
sheet so they survive the next sync; delete a line to let the sheet's own
wording back through. Every one was checked against Wikipedia's episode and
graphic novel lists, and all 173 numbered graphic novels now match it exactly.

Most are plain misspellings ("Explosing" → "Exploding", "Gilteman" →
"Gitelman", "Amost" → "Almost"). Three are factual:

- **#166–173** are *From the Files of **Primatech***, not "of Company".
- **#162** is *Second Chances*; the sheet repeated *Starting Over* from #159.
- ***The Official Magazine* #11 appears twice.** The magazine ran twelve
  bi-monthly issues to December 2009, so the October 2009 entry is **#12**.

`DATE_LABELS` handles undated rows in the date column: the sheet's
"BEFORE PREMIERE" becomes the first row's own date, reading **Pre-pilot**.
Anything else undated still renders as a divider above the row
("CANCELLATION", "HEROES REBORN").

## A note on the UK tie-ins

BBC Two's *Heroes Unmasked* and the tie-in radio show ran on their own British
schedule, weeks or months behind the US broadcast. The sheet places them beside
the episode each one is about rather than on their UK air date, so a week reads
as a single story beat across every medium; where a UK premiere date was
recorded, it stays in the entry text. The site preserves that as-is.

## Files

```
index.html               the site (data inlined)
api/watch.js             where-to-watch proxy (JustWatch, keyless)
build/sync.py            re-reads the sheet and rewrites the data block
build/link_archive.py    regenerates the Heroes Unmasked -> archive.org map
build/watch_snapshot.py  refreshes the offline where-to-watch fallback
build/buy_blurbs.py      refreshes the where-to-buy blurbs (Wikipedia)
build/sheet.xlsx         last downloaded copy of the sheet
```

Heroes is a trademark of NBCUniversal. This is an unofficial fan reference.
