# -*- coding: utf-8 -*-
"""Shoot assets/preview.jpg -- the picture Reddit, WhatsApp, Discord and the
rest show when somebody pastes the link.

It is the page itself, not a poster made to look like it: Chrome loads
index.html off a local server and photographs the top of it, so the card shows
the lede and the first weeks of the timeline exactly as a reader would find
them. Nothing to keep in sync, because there is nothing typed twice.

Shot at 1600x840 and 2x, then scaled to 1200x630, which is the size every
scraper agrees on -- the wider viewport fits more of the timeline in, and
scaling down from twice the pixels is what keeps the small type readable.
JPEG rather than PNG because WhatsApp will not fetch a large preview; keep the
file well under 300 KB.

    py build/og_card.py

Needs Pillow and Chrome or Edge. Re-run it whenever the top of the page
changes, and commit the picture: og:image has to be an absolute URL on the
deploy, so the file has to be in the repo.
"""
import os, shutil, socket, subprocess, sys, tempfile, time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, os.pardir))
OUT = os.path.join(ROOT, "assets", "preview.jpg")

W, H = 1200, 630                 # what the scrapers want
SHOT_W, SHOT_H = 1800, 945       # same 40:21, but more of the page in frame
SCALE = 2                        # shoot at twice the pixels, then come down

BROWSERS = [
    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
    r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
    r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe",
    r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
]


def browser():
    for path in BROWSERS:
        path = os.path.expandvars(path)
        if os.path.exists(path):
            return path
    found = shutil.which("chrome") or shutil.which("chromium")
    if found:
        return found
    sys.exit("no Chrome or Edge found -- this needs one to photograph the page")


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def serve(port):
    """The page has to come off http, not file://. Two things break otherwise:
    the Google Fonts request, and the where-to-watch lookup, which would sit
    there failing while the shutter is open."""
    p = subprocess.Popen([sys.executable, "-m", "http.server", str(port),
                          "-b", "127.0.0.1", "-d", ROOT],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try:
            socket.create_connection(("127.0.0.1", port), .2).close()
            return p
        except OSError:
            time.sleep(.1)
    p.kill()
    sys.exit("the local server never came up")


def shoot(exe, url, path):
    """--virtual-time-budget is the wait: it lets the page's own timers run to
    completion before the shutter, which is what the render and the fonts need.
    A throwaway profile keeps this off whatever Chrome the reader has open."""
    profile = tempfile.mkdtemp(prefix="og-card-")
    try:
        r = subprocess.run(
            [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--no-first-run", "--no-default-browser-check",
             "--user-data-dir=" + profile,
             "--force-device-scale-factor=%d" % SCALE,
             "--window-size=%d,%d" % (SHOT_W, SHOT_H),
             "--virtual-time-budget=10000",
             "--screenshot=" + path, url],
            capture_output=True, text=True, timeout=120)
        if not os.path.exists(path):
            print(r.stderr.strip()[-600:])
            sys.exit("Chrome took no picture")
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def main():
    exe = browser()
    port = free_port()
    server = serve(port)
    raw = os.path.join(tempfile.gettempdir(), "heroes-preview-raw.png")
    try:
        shoot(exe, "http://127.0.0.1:%d/index.html" % port, raw)
    finally:
        server.terminate()

    img = Image.open(raw).convert("RGB")
    print("shot %dx%d with %s" % (img.width, img.height, os.path.basename(exe)))
    # Chrome honours the scale factor in the window size, so the picture comes
    # back at SHOT * SCALE. Crop to the exact 40:21 before scaling, in case a
    # future Chrome rounds it differently.
    want = W / float(H)
    if abs(img.width / float(img.height) - want) > .001:
        h = int(img.width / want + .5)
        img = img.crop((0, 0, img.width, min(h, img.height)))
    img = img.resize((W, H), Image.LANCZOS)

    img.save(OUT, "JPEG", quality=88, optimize=True, progressive=True)
    kb = os.path.getsize(OUT) / 1024.0
    print("%dx%d, %.0f KB -> %s" % (W, H, kb, os.path.relpath(OUT, ROOT)))
    if kb > 290:
        print("  over 290 KB -- WhatsApp may skip it; drop the JPEG quality")


if __name__ == "__main__":
    main()
