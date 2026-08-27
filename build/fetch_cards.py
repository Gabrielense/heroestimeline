# -*- coding: utf-8 -*-
"""Download the title cards once so the site serves them itself.

Hot-linking the Wayback Machine failed roughly half of all image requests and
took 10-20s when it did answer -- it is an archive, not a CDN. These are small
identifying thumbnails (a few KB each, ~270px wide), fetched once and committed.

The archive drops connections often, so this is resumable: already-downloaded
files are skipped, and re-running picks up whatever failed last time. Run it
until it reports 0 outstanding.

    py build/fetch_cards.py            # fetch anything still missing
    py build/fetch_cards.py --report   # just say what's outstanding
"""
import json, os, re, sys, time, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import season4
from naming import slug

try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CARDS = os.path.join(HERE, os.pardir, "assets", "cards")
MANIFEST = os.path.join(DATA, "cards.json")
UA = {"User-Agent": "Mozilla/5.0"}


def wanted():
    """(local name, remote url) for every card we know about"""
    out = []
    gn = os.path.join(DATA, "gn_wiki.json")
    if os.path.exists(gn):
        for k, v in json.load(open(gn, encoding="utf-8")).get("found", {}).items():
            if v.get("card"):
                out.append(("gn-%s" % k, v["card"]))
    # the issues Wikipedia's list never covered, filled in from Heroes Wiki
    extra = os.path.join(DATA, "gn_extra.json")
    if os.path.exists(extra):
        for k, v in json.load(open(extra, encoding="utf-8")).get("found", {}).items():
            if v.get("card"):
                out.append(("gn-%s" % k, v["card"]))
    ep = os.path.join(DATA, "ep_wiki.json")
    if os.path.exists(ep):
        # ep_wiki.json is keyed the way the sheet numbers season four, which is
        # one too high from Ink onwards. Shift before naming the files, or the
        # cards land under codes the page will never ask for.
        found = season4.remap_keys(
            json.load(open(ep, encoding="utf-8")).get("found", {}))
        for k, v in found.items():
            if v.get("card"):
                out.append(("ep-%s" % k, v["card"]))
    # The webisode and Evolutions art comes off a fan-run mirror rather than the
    # Wayback Machine. Hot-linking someone's hobby server for every page view is
    # rude at best and dead at worst, so those get copied down too. The key is
    # the code as the timeline spells it, slashes and all -- flatten it.
    web = os.path.join(DATA, "web_wiki.json")
    if os.path.exists(web):
        for k, v in json.load(open(web, encoding="utf-8")).get("found", {}).items():
            if v.get("img"):
                out.append(("web-%s" % k, v["img"]))
    # one picture per iStory volume, stored under each chapter's own code so a
    # volume that later gets its own art per chapter needs no other change
    ist = os.path.join(DATA, "istory.json")
    if os.path.exists(ist):
        for k, v in json.load(open(ist, encoding="utf-8")).items():
            if v.get("img", "").startswith("http"):
                out.append(("istory-%s" % slug(k), v["img"]))
    art = os.path.join(DATA, "phys_cards.json")
    if os.path.exists(art):
        blob = json.load(open(art, encoding="utf-8"))
        for k, v in (blob.get("phys") or {}).items():
            if v.get("img"):
                out.append(("phys-%s" % slug(k), v["img"]))
        for k, v in (blob.get("reborn_eps") or {}).items():
            if v.get("img"):
                out.append(("ep-%s" % k, v["img"]))
    evo = os.path.join(DATA, "evo_site_wiki.json")
    if os.path.exists(evo):
        blob = json.load(open(evo, encoding="utf-8"))
        for group, prefix in (("site", "site"), ("evo", "evo")):
            for k, v in (blob.get(group) or {}).items():
                if v.get("img"):
                    out.append(("%s-%s" % (prefix, slug(k)), v["img"]))
        if blob.get("istory_img"):
            out.append(("istory", blob["istory_img"]))
    return out


def ext_of(url):
    m = re.search(r"\.(jpg|jpeg|png)(?:$|\?)", url, re.I)
    return "." + (m.group(1).lower() if m else "jpg")


# The archive starts returning 429 after a few dozen rapid requests. Backing off
# inside a retry is not enough on its own -- there has to be a gap between
# successful fetches too, or the run simply earns a rate limit and then burns
# through the rest of the queue failing.
PAUSE = 2.5          # between requests
COOLDOWN = 45        # after a 429, before trying anything again


def grab(url, dest, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                body = r.read()
            if len(body) < 200 or not r.headers.get("Content-Type", "").startswith("image/"):
                return False, "not an image"
            open(dest, "wb").write(body)
            return True, len(body)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = COOLDOWN * (i + 1)
                try:
                    wait = max(wait, int(e.headers.get("Retry-After", 0)))
                except (TypeError, ValueError):
                    pass
                print("      rate limited, waiting %ds" % wait)
                time.sleep(wait)
                continue
            if i == tries - 1:
                return False, "HTTP %s" % e.code
            time.sleep(3 + 4 * i)
        except Exception as e:
            if i == tries - 1:
                return False, str(e)[:60]
            time.sleep(3 + 4 * i)
    return False, "gave up"


def main():
    os.makedirs(CARDS, exist_ok=True)
    todo = wanted()
    manifest = {}
    if os.path.exists(MANIFEST):
        manifest = json.load(open(MANIFEST, encoding="utf-8"))

    missing = [(n, u) for n, u in todo
               if not os.path.exists(os.path.join(CARDS, n + ext_of(u)))]
    print("known cards: %d | already local: %d | outstanding: %d"
          % (len(todo), len(todo) - len(missing), len(missing)))
    if "--report" in sys.argv:
        # still rewrite the manifest, so an interrupted run's downloads are
        # usable without having to finish the whole queue first
        for name, url in todo:
            if os.path.exists(os.path.join(CARDS, name + ext_of(url))):
                manifest[name] = "assets/cards/" + name + ext_of(url)
        json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1, sort_keys=True)
        print("manifest lists %d local cards" % len(manifest))
        return

    # Long runs get killed part-way through, so cap the batch and let the
    # caller loop. The manifest is rewritten every time, which keeps whatever
    # landed usable even if the process dies mid-queue.
    limit = None
    for a in sys.argv:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
    if limit:
        missing = missing[:limit]
        print("this batch: %d" % len(missing))

    ok = fail = 0
    for i, (name, url) in enumerate(missing, 1):
        fn = name + ext_of(url)
        got, info = grab(url, os.path.join(CARDS, fn))
        if got:
            ok += 1
            manifest[name] = "assets/cards/" + fn
            print("  %3d/%d ok   %-10s %6d bytes" % (i, len(missing), name, info))
        else:
            fail += 1
            print("  %3d/%d FAIL %-10s %s" % (i, len(missing), name, info))
        time.sleep(PAUSE)

    # anything already on disk counts, whether or not we fetched it this run
    for name, url in todo:
        fn = name + ext_of(url)
        if os.path.exists(os.path.join(CARDS, fn)):
            manifest[name] = "assets/cards/" + fn
    json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, sort_keys=True)

    still = len(todo) - len(manifest)
    total = sum(os.path.getsize(os.path.join(CARDS, f)) for f in os.listdir(CARDS))
    print("\nfetched %d, failed %d | %d/%d cards local (%.1f MB) | %d still outstanding"
          % (ok, fail, len(manifest), len(todo), total / 1e6, still))
    if still:
        print("re-run to retry the rest -- the archive drops connections at random")


if __name__ == "__main__":
    main()
