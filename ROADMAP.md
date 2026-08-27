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
- [x] **Heroes Evolutions** — blurb + picture for the rest; iStory chapters
      share one image
- [~] **Physical media** — 20 of the 32 have cover art. The twelve without are
      the ones Heroes Wiki has no page for: both graphic-novel omnibuses, the
      Vengeance hardcover, the Reborn eBook collections, the Reborn magazine,
      Heroes Revealed, the Collector's Edition, the Complete Series box, the
      Season 1 Blu-ray and the Original Score. Needs another source
- [~] **Heroes Reborn episodes** — three of the four filled. *Brave New World*
      (HR1x01) still has none
- [~] **Graphic novel subtitles** — only three are recorded anywhere a script
      can read: #25 Unknown Soldiers, #148 When Everything Changed, #166 1963,
      Part 1. Heroes Wiki does not carry the rest, so they need a human. The 22
      webisode subtitles are all in
- [x] **Unaired pilot** — its chapter title is *In His Own Image*; blurb and
      card now sit above the video
- [~] **HeroTruther** — the five videos are listed with dates and blurbs, and
      the channel link now points at a 2016 capture of the real one rather than
      the stranger who took the name. **Thumbnails from the VK mirror are still
      to do**
- [ ] **Disc extras** — every extra on S1–S4 and the Reborn set, each as its own
      entry in the week the discs came out, blurbs from dvdmg / highdefdigest.
      *The machinery is ready: write them into `build/data/additions.json` and
      their blurbs into `hand_extras.json`, then re-run sync.py and extras.py*
- [ ] **Audio commentaries** — per season, as individual entries, episodes named
      in the blurb. Same route as the disc extras
- [ ] **Cross-check** against User:Iheartheroes' release-date timeline, which is
      the best one on the wiki. There should be no differences

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
      Wayback Machine
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
