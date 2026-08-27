# Roadmap

Working list for the next pass. Ticked items are done and pushed.

## 0b. The Misc. split (Aug 2026)

- [x] The sixth column is **Behind the scenes**, not *Heroes Unmasked*, and the
      episodes read *Unmasked: Finale* so they can sit beside *Inside Heroes*
      and a commentary track without ambiguity
- [x] Misc. split four ways in `RECLASS`: making-of → behind the scenes,
      in-fiction artefacts → Evolutions, merchandise → physical releases, and
      the real world stays. The README has the table
- [x] Disc extras renamed `Season N Extras: …`, each with the High-Def Digest
      review it was written from as its source link, and each showing the cover
      of the set it is on
- [x] The five disc extras that are not disc releases — *Sword Saint*, the
      Drucker report, and the three "Alternate Stories" webisode series — are
      listed on the day they first appeared, with *Also found on* saying which
      set carries them. `disc_extras.json`'s `not_entries` records why
- [x] *Heroes Connections* dropped: disc navigation art, not a feature
- [x] **All 46 Heroes Unmasked episodes have a blurb**, from the one wiki
      article that carries them all (`build/unmasked.py`), each ending with its
      real BBC Two date. 13 have their intertitle; the rest show the series card
- [x] *Inside Heroes* listed out as its eight featurettes, each with its own
      picture off the wiki, plus *Heroes Character Profiles*, which launched the
      same day
- [x] Blurbs and pictures for Heroeswiki.com, the BBC radio show, *The Post
      Show*, the World Tour, Heroes All Access, the Heroes Reborn app,
      *Claire & the Cat*, the Drucker files, the two Topps sets, the Mezco
      figures and *Countdown to the Premiere*
- [x] The radio show and *The Post Show* carry one blurb across all 26 and all
      6 entries, through the `series` rules in `manual_extras.json`, rather than
      the same paragraph typed out thirty-two times
- [x] YouTube plays in the panel for the two things that never reached
      archive.org: the Super Bowl XLIII spot and the 2014 Olympics teaser
- [x] `hand_extras.json` and `additions.json` are now fully generated;
      `manual_extras.json` is the file to edit

Still open from this pass:

- [ ] *Inside Heroes* #1–#8 all sit in the week NBC announced them (21 May
      2007). They actually rolled out across that summer, one at a time, and no
      source found so far gives the individual dates
- [ ] *Inside the Eclipse* #01–#13 still have no blurb or picture of their own

## 0a. The videos come back (Aug 2026)

- [x] **No more *Between Eras*.** Volume 5 runs to the last thing it put out,
      the complete-series set of 16 Nov 2010; Heroes Reborn starts with the
      first, the Olympics teaser of 23 Feb 2014. `resolve_gaps()` in `sync.py`
      folds the sheet's near-black rows onto whichever side of that line they
      fall, so the era is gone from the data as well as the legend
- [x] **29 of the 39 webisodes play in the panel again**, from the copies
      collectors kept: `yt` for the 28 on YouTube, `dm` for *Nowhere Man,
      Part 1*, which is on Dailymotion. Every id checked with `build/yt.py`
      against its upload date and running time
- [x] *Damen Peak* is linked rather than described — parts 1 and 3 have their
      own uploads, and part 2 uses the 3:19 parts-1–2 video with the new `vn`
      caption saying so under the player. The *Also found on* line is gone
- [x] *Sword Saint* and *The Drucker Files* play too, off the season two set
- [x] Blurbs, cards and sources for **all the games**: *Are You a Hero?*,
      Habbo's interactivity, *Heroes Reborn: Enigma* and *Gemini: Heroes
      Reborn*. A source link on the Olympics teaser
- [x] `vn` — one line under the player for when the only surviving copy is not
      a clean single part

Still open:

- [ ] No copy has been found of *Hard Knox, Part 4* or *Nowhere Man*, Parts 2–4
      (its uploader posted only the first). They still point at the archive's
      1.4 GB webisode ZIP like the rest
- [ ] Three dates disagree with Heroes Wiki: Habbo's interactivity sits in the
      Volume 3 premiere week but the wiki's campaign runs 23 Jan – 9 Feb 2009,
      *Are You a Hero?* is 11 Dec 2006 here and 8 Jan 2007 there, and *Gemini*
      is 14 Jan 2016 here against a 19 Jan release. The sheet's dates were kept
- [ ] *Heroes: The Video Game* has a wiki page and no row anywhere here

## 0. Cleanup and corrections

- [x] Drop the "long out of print" line from the buy panel for good
- [x] Remove the footer "Where to find it" section — the panel says it now
- [x] `Global News Interactive` → `Global News Interactive / The Drucker Files`,
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
- [x] Stale README file list

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
      Blu-ray, Dark Matters on the Reborn discs
- [x] A blurb on *Inside the Eclipse* #09 saying why it is not on archive.org
- [x] Credit **User:Iheartheroes** by name (in the footer)
- [ ] Actually diff our dates against their release-date list

## 3. Player and links

- [x] **Read the issue** — all 173 numbered novels have NBC's own PDF on the
      Wayback Machine, found by `build/gn_pdfs.py`. The archive serves them as
      real files under its `id_` modifier and sets no `X-Frame-Options`, so the
      panel can frame one. It only does so when asked: the median issue is
      15.4 MB (largest 27.4) and one took 26 seconds to arrive, so the button
      says the size before you spend it. Title, card and blurb stay above.
      *Note for anyone extending this: ask CDX to filter by mimetype
      server-side. Filtering afterwards means paging through 17,000 captures
      of everything else in that directory, and a per-issue sweep of 366
      requests gets throttled to over an hour.*
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
