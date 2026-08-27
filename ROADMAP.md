# Roadmap

Working list for the next pass. Ticked items are done and pushed.

## 0. Cleanup and corrections

- [x] Drop the "long out of print" line from the buy panel for good
- [x] Remove the footer "Where to find it" section — the panel says it now
- [ ] `Global News Interactive` → `Global News Interactive / The Drucker Files`,
      so it is findable under both, and note it is on the S2 DVD extras
- [x] Claire's MySpace, Zach's MySpace and Hiro's Blog become **websites**
- [x] *Vengeance* and *Godsend* are not webcomics — stop grouping the full
      volumes under the webcomic blurb
- [x] Season 4 has **18** episodes: the premiere is one two-hour episode, so
      `4x02 Jump, Push, Fall` merges into `4x01 Orientation` and 4x03–4x19
      renumber down. Verified against the cached `Heroes_season_4.wiki`
- [x] *Turning Point* (#10) has no link — and audit the rest for the same gap
      (36 issues were missing a card, a blurb or both; all filled)
- [x] Dead `e._blob`
- [ ] Stale README file list

## 1. Scraped data (one JSON per collector, then wired in)

- [x] **Webisodes** — blurb + title card for all 32, same treatment as the
      graphic novels and episodes
- [x] **Websites** — pictures and blurbs for the site entries
- [x] **Heroes Evolutions** — blurb + picture for the rest
- [x] **iStory, chapter by chapter** — all 58 chapters have their own synopsis
      and their volume's own art, keyed by the code the sheet uses
      (`build/istory.py`). Chapter names read as subtitles. The long
      walkthrough tables on those pages are deliberately left alone — they are
      solution guides, not blurbs
- [~] **Physical media** — 20 of the 32 have cover art. The twelve without are
      the ones Heroes Wiki has no page for: both graphic-novel omnibuses, the
      Vengeance hardcover, the Reborn eBook collections, the Reborn magazine,
      Heroes Revealed, the Collector's Edition, the Complete Series box, the
      Season 1 Blu-ray and the Original Score. Needs another source
- [x] **Heroes Reborn episodes** — all four filled; *Brave New World* uses a
      promotional still, since no title card exists
- [x] **Graphic novel subtitles** — all 39, from the release-date lists, in
      `build/data/gn_subtitles_manual.json`. Plus the 22 webisode ones
- [x] **Unaired pilot** — its chapter title is *In His Own Image*; blurb and
      card now sit above the video
- [~] **HeroTruther** — the five videos are listed with dates and blurbs, and
      the channel link now points at a 2016 capture of the real one rather than
      the stranger who took the name. *4th of July Fail* survives on YouTube and
      uses that thumbnail. **The other four thumbnails still need saving out of
      the VK mirror by hand** — vkvideo.ru renders its catalogue in JavaScript,
      so nothing server-side has the image URLs. Drop them into `assets/cards/`
      named for the entry and they appear:
      `evo-herotruther-woman-pushes-truck-with-one-hand.jpg`,
      `evo-herotruther-motorcycle-miracle.jpg`,
      `evo-herotruther-parkour-leap-epic.jpg`.
      *The Time Has Come* has no thumbnail anywhere
- [x] **Disc extras** — 43 of them, each its own entry in the week its set came
      out, from `build/data/disc_extras.json`
- [x] **Audio commentaries** — one entry per season, episodes named in the blurb
- [x] **Graphic novel dates against Wikipedia's list** — `py build/gn_dates.py`.
      It found two weeks the sheet had wrong, both confirmed against
      Iheartheroes: *Viewpoints* and *From the Files of Primatech, Part 8*.
      `DATE_MOVES` in sync.py lifts them into the right week, and the check now
      comes back clean. The other 113 differences are a day either side of a
      Monday — the novels went out on Tuesdays
- [~] **Cross-check** against User:Iheartheroes' release-date list —
      `py build/date_diff.py`. **241 agree exactly.** 11 differ by a single day,
      which is the sheet filing by Monday against their filing by release day —
      not errors. **Seven land in a different week and want a human:**
      *June 13th, Part One* is **theirs** that is wrong (Wikipedia's own Reborn
      air dates say 29 Oct 2015, as we have it). *Viewpoints* was **ours** and
      is fixed. **Five are still open**, and Wikipedia cannot settle them:
      *The Rogue* and *The Last Shangri-La* carry no issue number in either
      list, and *Vengeance* 1–3 are Titan's printed comics, outside the
      webcomic list entirely. 52 entries are only on their list, 48 only on
      ours; `build/data/date_diff.json` has all of it

## 2. New entries

- [x] *Novel Approach: The Hiro Collection* (#167b, 10 Mar 2010) and the six
      novels it collects
- [x] *Making of the Damen Peak Video*, parts 1 and 2 — lost media
- [x] Where the webisodes actually survive: Hard Knox as deleted scenes and
      The Recruit / Going Postal / Nowhere Man as "Alternate Stories" on the S3
      Blu-ray, Dark Matters on the Reborn discs, Damen Peak on YouTube
- [x] A blurb on *Inside the Eclipse* #09 saying why it is not on archive.org
- [x] Credit **User:Iheartheroes** by name (in the footer)
- [ ] Actually diff our dates against their release-date list

## 3. Player and links

- [ ] Embed the comics that exist as individual PDFs on archive.org, keeping the
      title and blurb above them; some survive only as NBC.com PDFs on the
      Wayback Machine. **The addresses are already in hand:** every row of
      `build/data/gn_list.wiki` carries that issue's `nbc.com/Heroes/novels/
      downloads/Heroes_novel_NNN.pdf` and a Wayback `archive-url` for it, so
      the links can be read straight out of the cached wikitext rather than
      probed for
- [ ] Comics that are on neither are on a fan's Drive share — link it
- [ ] Archive links for the webisodes and comics generally

## 4. For Gabriel

- [ ] A checklist of the physical releases with the exact names they are sold
      under, so the buy links can be checked one by one

## Done

- [x] Internet Archive embeds (58 entries)
- [x] Detail popover, where-to-watch, where-to-buy
- [x] 235 title cards for episodes and graphic novels
- [x] The 2007–08 Writers Guild strike band
- [x] The Brazilian *Heroes: Vingança* edition link

## Dropped

- Amazon affiliate links — not doing it
- The Oscar 2027 site — deleted for good
- Fan-made material (DeviantArt posters and the like)
