# -*- coding: utf-8 -*-
"""Work out exactly what has to go in one commit, and write it as a pathspec.

The invariant: every assets/ path the committed index.html references must be a
committed file. index.html and the images it newly points at therefore land
together or not at all -- a reference without its file is a hard 404 in
production, where the old archive URLs merely timed out and were hidden.

Matches images by SIGNATURE and by any image extension, not by ".jpg": auditing
this set by extension has produced a wrong answer twice, in both directions,
because nine of the cards are PNGs.

    py build/commit_plan.py            # report + write the pathspec file
    py build/commit_plan.py --tooling  # include the build scripts and data too
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, os.pardir))
OUT = os.path.join(HERE, "data", "commit_paths.txt")
IMG_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp")


def git(*a):
    return subprocess.run(["git", "-C", ROOT] + list(a),
                          capture_output=True, text=True, encoding="utf-8").stdout


def verify(ref):
    """The invariant, checked against a COMMIT rather than the working tree:
    every assets/ path the committed page asks for must be a committed file."""
    html = git("show", "%s:index.html" % ref)
    if not html:
        sys.exit("could not read index.html at %s" % ref)
    data = json.loads(re.search(r'id="extras-data">(.*?)</script>', html, re.S).group(1))
    asked = {v["img"] for g in data.values() if isinstance(g, dict)
             for v in g.values()
             if isinstance(v, dict) and str(v.get("img", "")).startswith("assets/")}
    tracked = {l.strip() for l in
               git("ls-tree", "-r", "--name-only", ref).splitlines()
               if l.startswith("assets/")}
    missing = sorted(asked - tracked)
    print("%s: page asks for %d local images, tree holds %d"
          % (ref, len(asked), len(tracked)))
    print("asked for but not committed: %d" % len(missing))
    for m in missing[:10]:
        print("   ", m)
    if missing:
        sys.exit("INVARIANT BROKEN - these 404 in production")
    print("invariant holds")


def main():
    for a in sys.argv[1:]:
        if a.startswith("--verify"):
            return verify(a.split("=", 1)[1] if "=" in a else "HEAD")

    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    data = json.loads(re.search(r'id="extras-data">(.*?)</script>', html, re.S).group(1))

    referenced = set()
    for group in data.values():
        if not isinstance(group, dict):
            continue
        for v in group.values():
            img = isinstance(v, dict) and v.get("img") or ""
            if img.startswith("assets/") and img.lower().endswith(IMG_EXT):
                referenced.add(img)

    tracked = {l.strip() for l in git("ls-files", "assets").splitlines() if l.strip()}
    on_disk = set()
    for base, _, files in os.walk(os.path.join(ROOT, "assets")):
        for f in files:
            rel = os.path.relpath(os.path.join(base, f), ROOT).replace(os.sep, "/")
            if rel.lower().endswith(IMG_EXT):
                on_disk.add(rel)

    absent = sorted(referenced - on_disk)
    need = sorted(referenced - tracked)
    unreferenced = sorted(on_disk - referenced)

    print("referenced by index.html : %d" % len(referenced))
    print("on disk                  : %d" % len(on_disk))
    print("already tracked          : %d" % len(tracked))
    print("referenced but MISSING   : %d %s" % (len(absent), "<-- BLOCKS THE COMMIT" if absent else ""))
    for a in absent[:10]:
        print("     ", a)
    print("must land with index.html: %d" % len(need))
    print("on disk, unreferenced    : %d (harmless, left untracked)" % len(unreferenced))
    for u in unreferenced:
        print("     ", u)

    if absent:
        sys.exit("refusing to write a pathspec that would 404 in production")

    paths = ["index.html"] + need
    if "--tooling" in sys.argv:
        paths += ["build/extras.py", "build/scrape_episodes.py", "build/fetch_cards.py",
                  "build/check_cards.py", "build/commit_plan.py",
                  "build/data/ep_wiki.json", "build/data/cards.json"]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(paths) + "\n")

    print("\nwrote %d paths -> %s" % (len(paths), os.path.relpath(OUT, ROOT)))

    # Prove the plan can actually run. A pathspec file that git rejects is a
    # check that looks thorough and isn't -- and `git commit --only` DOES reject
    # it, because --only resolves pathspecs against files git already knows and
    # every new image here is untracked. Hence the add first. --dry-run stages
    # nothing, so this is safe to do while reporting.
    dry = subprocess.run(
        ["git", "-C", ROOT, "add", "--dry-run",
         "--pathspec-from-file=" + os.path.relpath(OUT, ROOT).replace(os.sep, "/")],
        capture_output=True, text=True, encoding="utf-8")
    staged = len([l for l in dry.stdout.splitlines() if l.startswith("add ")])
    print("dry-run: git add reports %d paths, exit %d" % (staged, dry.returncode))
    if dry.returncode != 0 or staged != len(paths):
        print(dry.stderr.strip()[:400])
        sys.exit("plan is not executable as written - fix before committing")
    print("plan is executable")

    print("\ncommit with BOTH lines, in this order:")
    print("  git add --pathspec-from-file=build/data/commit_paths.txt")
    print('  git commit --only -m "MESSAGE" --pathspec-from-file=build/data/commit_paths.txt')
    print("\n  (the add is required: --only matches only paths git already knows,")
    print("   and the new images are untracked. The --only still protects anyone")
    print("   else's staged work, it just needs the add ahead of it.)")
    print("\nafterwards, confirm the invariant held:")
    print("  py build/commit_plan.py --verify=HEAD")


if __name__ == "__main__":
    main()
