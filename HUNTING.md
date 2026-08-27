# Hunting for what is missing

A working list for the searches that need a person, not a script — mostly
judging whether a given upload really is the thing it claims to be. Written so
you can pick it up cold: what is missing, where copies have actually turned up
before, the exact search strings, and what to do with a hit.

**When you find one:** note the id and run

```bash
py build/yt.py <id>
```

It prints the upload date, the running time and the title. Then put it in
`build/data/manual_extras.json` — `blurbs.web` keyed by the webisode code,
`blurbs.bts`/`blurbs.evo`/`blurbs.misc` keyed by the exact title — as
`"yt": "<id>"`, or `"dm": "<id>"` for Dailymotion. Add a `"vn"` line if the copy
is not a clean single part ("Parts 1 and 2 went out together…"). Then:

```bash
py build/make_additions.py
py build/extras.py
```

Nothing is rehosted; the page embeds from youtube-nocookie or Dailymotion.

---

## What has already worked

Four sources have produced every hit so far. Try them first, in this order.

| Source | What it gave | Why it works |
| --- | --- | --- |
| **Rewatch Podcast** (YouTube) | Slow Burn 7–10, Damen Peak 1–2 and 3, and *Parts 1–N* compilations of Going Postal, The Recruit, Hard Knox | A 2024–25 archivist re-uploading the webisodes in order, with the release dates in the descriptions. The single most productive channel found. |
| **Alexus2319** (YouTube) | Damen Peak, both 30-second parts, uploaded Jan 2016 | Contemporary uploads, still using NBC's own titles |
| **ChM** uploads (YouTube) | Hard Knox 1–4, titled `Heroes Webisode 04 Hard Knox 2008 Ch 0N <subtitle> ChM` | Rigid naming: swap the chapter number and you find the next part |
| **heroes-spain** (Dailymotion) | Nowhere Man Part 1 | Exhausted — the account has four videos in total and no more Heroes |

Two patterns are worth knowing:

- **Search by subtitle, not by part number.** "The Main Man Now" found Hard Knox
  Part 4 when "Hard Knox Part 4" did not. Every webisode's subtitle is in its
  panel on the site, and in `build/data/web_wiki.json`.
- **Compilations count.** Several series survive only as one video of several
  parts. That is fine — use it, and add a `vn` line saying where the part
  starts.

---

## Still missing, in the order worth trying

### 1. Nowhere Man, Parts 2–4 (2009) — the only webisode gap left

The one series with no full copy anywhere. Subtitles: **Statement of
Character**, **Pulling the Strings**, **A New Beginning**. It is on the season
three Blu-ray under *Alternate Stories*, so a disc rip is plausible.

Already run and empty: YouTube for the titles and the subtitles; Dailymotion
search for "Nowhere Man" and "Heroes Nowhere Man Webisode Chapter"; the
heroes-spain account in full; Rewatch Podcast's channel.

Left to try:

- `Nowhere Man Parts 1-4 - Heroes Webisodes` — Rewatch Podcast's exact naming
  for Going Postal. If they get to it, this is the title it will have
- `Heroes Webisode 1N Nowhere Man Ch 0N` — the ChM naming, webisodes 18–20
- `heroes alternate stories nowhere man doyle`
- Non-English: `heroes webisodio nowhere man`, `heroes webisode nowhere man
  vostfr`, `heroes webisode nowhere man legendado`. The Recruit survives as a
  French fansub and Destiny as a Portuguese one, so this is not a long shot
- Vimeo and Bilibili, which no search here has touched yet
- archive.org full-text search for `Nowhere Man Doyle heroes webisode` — the
  1.4 GB `heroes-webisodes` ZIP has them, but nothing streams per file. If
  someone has uploaded them as separate items, they would be playable

### 2. *Inside Heroes* #1–#8 (2007) — eight NBC featurettes, no copy at all

Visual Effects, The Score, Wardrobe, Stunts, Makeup, Craft Services, The
Artwork, Production Design. Plus *Heroes Webisode Behind the Story* (2008).
Blurbs and pictures are done; there is no video.

- `Inside Heroes visual effects Stargate Digital Kolpack` — the featurettes name
  their interviewees, and those names are in each blurb on the site
- `heroes nbc digital inside heroes featurette 2007`
- Wayback: `web.archive.org/web/2007*/nbc.com/Heroes/video/*` — NBC's own player
  pages. Flash video, so probably not playable, but the Wayback Machine did keep
  some `.flv` files
- The season one and two discs carry a lot of this material under other names;
  compare the disc-extra lists on High-Def Digest against these eight titles
  before hunting further, in case they are already on the site as disc extras

### 3. *The Post Show* (G4, 2007) — six episodes, believed lost

Blair Butler and Kevin Pereira, Saturdays at 11pm, 3 Nov – 8 Dec 2007. G4
archived none of it.

- `G4 Post Show Heroes Blair Butler Kevin Pereira`
- `Attack of the Show Heroes Post Show 2007`
- G4 fan-preservation projects: there are people archiving G4TV's whole run —
  search `g4tv archive 2007` on archive.org and Reddit's r/G4TV
- Stickam segments were user webcams, so unlikely, but the show's own promos
  may survive on NBC/G4 promo reels

### 4. *Heroes: The Official Radio Show* (BBC Radio 7, 2006–07) — 26 episodes

Jon Holmes and Xanthe Fuller, Saturdays 7.30pm. Radio 7 kept nothing.

- `BBC Radio 7 Heroes Official Radio Show Jon Holmes` on archive.org and on
  Internet Archive's `oldtimeradio` collections
- BBC Genome (`genome.ch.bbc.co.uk`) is Radio Times listings, so it will confirm
  the transmission dates even where no recording exists — worth it for the dates
  alone, since the site currently files these beside the episode each covers
- Off-air recordings from radio hobbyists: `radio 7 offair recording 2007 heroes`
- Jon Holmes' own site and podcast feed

### 5. *Making of the Damen Peak Video*, Parts 1–2 (2015–16)

Posted during the Reborn campaign, lost with the channel that hosted it. NBC's
own page for it is captured in the wiki's external links —
`nbc.com/heroes-reborn/video/making-of-the-damen-peak-video/2939543` — so try the
Wayback Machine on that URL before searching anywhere else.

### 6. The four lost HeroTruther videos (2015)

*Woman Pushes Truck with One Hand*, *мотоцикл чудо (Motorcycle Miracle)*, and
two more. The original channel was deleted and someone else later took the name.
*4th of July Fail* survives because a viewer re-uploaded it, so the others may
too.

- Search the Russian title directly: `мотоцикл чудо HeroTruther`
- `hero truther evo video 2015 reupload`
- The campaign was on Twitter and Tumblr as well; a Wayback capture of
  `twitter.com/HeroTruther` may embed the videos

### 7. Disc extras — 26 featurettes across the four season sets

These are not lost, only unlinked: they are on discs you can buy, and the panels
already say which set. Uploads exist for a lot of it. Low priority, but the
easiest wins per hour: search the exact featurette title plus `heroes dvd
featurette`, e.g. `The Super Power of Heroes featurette Tim Gilbert`.

### 8. *Heroes: Countdown to the Premiere* (2008)

NBC's own hour before the Volume Three premiere. Worth one search:
`Heroes Countdown to the Premiere 2008 NBC special Masi Oka`.

---

## Not video: cover art still missing

`build/data/phys_cards.json` lists these under `missing` — the wiki has no
picture for them, and Amazon is deliberately not used because those URLs rot and
block hot-linking:

Season One Collector's Edition · *The Complete Series* box · the Season 1
Blu-ray · *Heroes Revealed* · *Original Score from the Television Series* ·
*Heroes, Volume 1* and *Volume 2* · the Omnibus · *Vengeance* Vol. 1 · both
*Heroes Reborn* paperback collections.

Best sources, in order: the publisher's own page (Titan, Del Rey), Discogs for
the two soundtracks, Blu-ray.com and DVDActive for the boxes, and the Wayback
Machine on the 2007–10 NBC store. Once you have a URL, add it to
`manual_extras.json` under `blurbs.phys` as `"img"`, then run
`py build/fetch_cards.py` to copy it down.

**The magazine covers are done** — all twelve, plus the *Heroes Reborn* one, by
`build/magazine.py`. They were hiding in the wiki's file namespace under names
no article links to, which is worth remembering: if the wiki seems not to have a
picture, search the `File:` namespace directly before giving up.
