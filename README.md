# Heroes: A Complete Multimedia Timeline

An interactive version of [the source spreadsheet](https://docs.google.com/spreadsheets/d/1Ci6zyz2nhjgrCurrhSDrD_jvtfXBLq_l9CWLpKDe3NE/edit) —
559 releases across 214 weeks and 7 parallel media, from the 2006 pilot to the
announcement of *Heroes: Eclipsed*.

`index.html` is the whole site: no build step, no dependencies, no network calls
beyond Google Fonts. Open it directly or drop it on any static host.

## What it does

- **Timeline view** — one row per week, releases grouped by medium, eras as
  sticky sections.
- **Grid view** — the original 8-column matrix, with the header row and date
  column pinned.
- **Compact mode** — collapses each week onto a single line (roughly halves the
  page height).
- **Activity rail** — one bar per week, height = releases that week, colour =
  era. Hover for detail, click to jump.
- **Era ribbon** — the eight eras as one proportional bar; click a segment to jump.
- **Search** across titles, episode/issue codes and dates (`2009-09` works).
- **Filters** by medium and by era (collapsed by default); shift-click an era to
  isolate it.
- **Permalinks** — jumping to a week writes `#w<row>` to the URL.
- Keyboard: `/` search · `t` timeline · `g` grid · `c` compact · `Esc` clear.

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

`sync.py` patches 30 entries on the way through — see `TITLE_FIXES`, `ROW_FIXES`
and `MARKER_FIXES` there. They are applied in the pipeline rather than in the
sheet so they survive the next sync; delete a line to let the sheet's own
wording back through. Every one was checked against Wikipedia's episode and
graphic novel lists, and all 173 numbered graphic novels now match it exactly.

Most are plain misspellings ("Explosing" → "Exploding", "Gilteman" →
"Gitelman", "Amost" → "Almost"). Three are factual:

- **#166–173** are *From the Files of **Primatech***, not "of Company".
- **#162** is *Second Chances*; the sheet repeated *Starting Over* from #159.
- ***The Official Magazine* #11 appears twice.** The magazine ran twelve
  bi-monthly issues to December 2009, so the October 2009 entry is **#12**.

`MARKER_FIXES` relabels the date column's own dividers — the sheet's
"BEFORE PREMIERE" reads as **PRE-LAUNCH** on the page.

## A note on the UK tie-ins

BBC Two's *Heroes Unmasked* and the tie-in radio show ran on their own British
schedule, weeks or months behind the US broadcast. The sheet places them beside
the episode each one is about rather than on their UK air date, so a week reads
as a single story beat across every medium; where a UK premiere date was
recorded, it stays in the entry text. The site preserves that as-is.

## Files

```
index.html        the site (data inlined)
build/sync.py     re-reads the sheet and rewrites the data block
build/sheet.xlsx  last downloaded copy of the sheet
```

Heroes is a trademark of NBCUniversal. This is an unofficial fan reference.
