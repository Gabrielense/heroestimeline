# Roadmap

Working list for the next pass. Ticked items are done and pushed.

## 0c. The two that were only ever announced (Aug 2026)

- [x] **Blurbs for the three announcement rows that had none**: *Heroes:
      Origins* announced and cancelled, and *Heroes: Eclipsed* announced. Each
      carries the report it came from as its source — Variety's upfront wrap,
      John August's own post the day the plug was pulled, Deadline's break —
      and the Origins pair point at the Heroes Wiki page as well. The Misc.
      column is now 42 of 44
- [x] Both Origins rows say what the row cannot: the sheet's week is 29 Oct
      2007, the shelving was the 31st, five days before the strike
- [x] **Vercel Web Analytics**, the plain-HTML install: the queue shim and
      `<script defer src="/_vercel/insights/script.js">` before `</body>`. No
      package and no build step, which is the point — the platform serves the
      script once Web Analytics is enabled on the project, and it 404s
      harmlessly anywhere else
- [x] **A link preview worth pasting**: `assets/preview.jpg` is a photograph of
      the top of the page — lede, rail, and the first week of the timeline —
      taken by `build/og_card.py` rather than drawn to look like one, plus the
      absolute `og:image`, `og:url` and `twitter:card` tags WhatsApp and Reddit
      need. A poster was tried first and thrown away: it was a picture of
      numbers, and the page is better looking than any card about it

Still open from this pass:

- [ ] The *"two-hour Heroes event/movie"* pair, announced May 2010 and
      cancelled, are the last two Misc. rows with no blurb

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

## 0b. Dates, discs and the game that never was (Aug 2026)

- [x] **Where Heroes Wiki disagrees with the sheet, the wiki wins** and its page
      is linked from the panel. Three moved through `DATE_MOVES`: *Are You a
      Hero?* to 8 Jan 2007, Habbo's interactivity to 26 Jan 2009, *Gemini* to
      19 Jan 2016
- [x] *Inside Heroes* #1–#8 no longer share the announcement week: 21 and 28
      May, 11 and 18 June, 2, 9, 16 and 30 July 2007
- [x] **Every episode says which boxes carry it** — its own season set, the
      Blu-ray and Collector's Edition where there is one, and *The Complete
      Series*; the Reborn episodes get the event-series set and nothing else,
      since *The Complete Series* came out five years before it. `EP_DISCS` in
      index.html, one rule per season, and each name jumps to that release's week
- [x] *Heroes: The Video Game* — Ubisoft's cancelled adaptation, announced at
      Comic-Con on 26 July 2007 and dropped in Oct 2008. Blurb, concept art,
      wiki and Unseen64
- [x] The unaired pilot's blurb records the 72-minute Comic-Con 2006 screening
- [x] Seasons two and three stop wearing the season one box. `phys_cards.py`
      asked for a page that does not exist and search answered with season one;
      aliases added there, and the right art pinned in `manual_extras.json`

Still open:

- [x] *Nowhere Man*, Parts 2–4 turned up on VK and play in the panel. The `vk`
      field takes the id the way VK writes it, `-24928385_160292003`
- [x] **All 39 webisodes play in the panel.** *Dark Matters* #31–#36 close it
      out, from TNT Brasil's upload of the six — the only complete set on
      YouTube, English audio with Portuguese subtitles
- [ ] Spot-check the *Dark Matters* mapping: TNT's cuts run 5–11½ minutes each
      against about 2½ for the one English rip of Part 1 that exists, so they
      look padded with promo material. The order is TNT's own, Episódio 1–6
- [x] **All twelve magazine covers, and a blurb for each** (`build/magazine.py`).
      They were all showing one shared picture that was not even issue one's
      cover: the per-issue wiki pages are redirects to a single article whose
      infobox is a cast panel, and the real covers are files no article links.
      The *Heroes Reborn* magazine gets its cover and contents too
- [x] Cover art for the eleven the wiki has none of — the Collector's Edition,
      *The Complete Series*, the Season 1 Blu-ray, *Heroes Revealed*, the
      *Original Score*, both collected volumes, the Omnibus, *Vengeance* Vol. 1
      and the two *Heroes Reborn* paperbacks. `HR1x01` is all that is left in
      `phys_cards.json`'s `missing`
- [x] *Vengeance* #174–#178 and *Godsend* #179–#183 wear their own issue covers
      rather than the wiki's title-card art: they are the only novels that were
      printed as single issues
- [x] **All 26 radio-show editions carry their BBC broadcast date**, off
      bbc.co.uk/programmes rather than the wiki (`build/radio.py`), each linking
      its own BBC page. The wiki's "Saturday at 7.30pm" was wrong too: the BBC's
      own records say 6.30pm for series one and 6pm for series two
- [x] Series 2, Episode 5 stays as the BBC has it — 11 May 2008, out of sequence
      and the only one of the 26 with no time on its record. Decided; do not
      re-raise
- [ ] **Hunt for surviving video** — see `HUNTING.md`

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
