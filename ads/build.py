#!/usr/bin/env python3
"""Build the ads section of basecodex.com from ads/catalogue.json.

    python3 ads/build.py

Writes ads/index.html (the library and the target apps), and for each target
app ads/<target>/manifest.json (what the app fetches) and ads/<target>/index.html.
Fails, writing nothing, if a video is missing or an app names an unknown ad.
Running it twice gives the same files.
"""
import hashlib
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://basecodex.com/ads"

cat = json.load(open(os.path.join(HERE, "catalogue.json")))
products = cat["products"]
library = {a["id"]: a for a in cat["library"]}

faults = []
for a in cat["library"]:
    path = os.path.join(HERE, "library", a["file"])
    if not os.path.exists(path):
        faults.append(f"library: {a['file']} is missing")
    else:
        a["bytes"] = os.path.getsize(path)
    if a["product"] not in products:
        faults.append(f"library: {a['id']} names unknown product {a['product']}")
for t in cat["targets"]:
    for entry in t["ads"]:
        if entry["ad"] not in library:
            faults.append(f"{t['id']}: unknown ad {entry['ad']}")
if faults:
    print("\n".join(faults))
    sys.exit(1)


def video_url(a):
    return f"{SITE}/library/{a['file']}"


def manifest(t):
    ads = []
    for entry in t["ads"]:
        a = library[entry["ad"]]
        p = products[a["product"]]
        ads.append({
            "id": a["id"],
            "product": p["name"],
            "title": a["title"],
            "video": {
                "url": video_url(a),
                "device": a["device"],
                "width": a["width"],
                "height": a["height"],
                "seconds": a["seconds"],
                "bytes": a["bytes"],
            },
            # The campaign token says which app and which ad sent an install
            # (App Store Connect, App Analytics, Campaigns).
            "tapUrl": f"{p['store']}?ct={t['id']}-{a['id']}",
            "weight": entry.get("weight", 1),
        })
    body = {"schema": 1, "app": {"id": t["id"], "name": t["name"], "bundleId": t["bundleId"]}, "ads": ads}
    # The version changes exactly when what the app should show changes, so an
    # app can keep its cached videos until it does.
    body["version"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]
    return body


STYLE = """
  :root { --edge:#04070f; --stage:#0a1630; --ink:#f2f4f8; --muted:#a7b0c2;
          --rule:rgba(255,255,255,.10); --accent:#4fc7bc; --blue:#8fb8ff; color-scheme:dark; }
  * { box-sizing:border-box; }
  html, body { background:var(--edge); }
  body { margin:0; color:var(--ink);
         font:16px/1.5 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
         -webkit-font-smoothing:antialiased; }
  .stage { width:min(100%, 760px); min-height:100vh; margin:0 auto; background:var(--stage);
           padding:28px 16px 40px; box-shadow:0 0 0 1px var(--rule), 0 0 80px rgba(0,0,0,.6); }
  h1 { font-size:32px; line-height:1.1; letter-spacing:-0.02em; margin:0 0 6px; }
  .lede { color:var(--muted); margin:0 0 8px; }
  section { padding-top:22px; margin-top:22px; border-top:1px solid var(--rule); }
  h2 { font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin:0 0 14px; }
  a { color:var(--blue); text-decoration:none; } a:hover { text-decoration:underline; }
  code { font:13px ui-monospace, SFMono-Regular, Menlo, monospace; color:var(--accent); word-break:break-all; }
  .ads { display:grid; grid-template-columns:repeat(auto-fill, minmax(200px, 1fr)); gap:18px; }
  .ad video { width:100%; aspect-ratio:1080/2348; background:#000; border-radius:14px; display:block; }
  .ad h3 { font-size:15px; margin:10px 0 2px; }
  .ad p { margin:0; font-size:13px; color:var(--muted); }
  .apps { list-style:none; padding:0; margin:0; }
  .apps li { padding:12px 0; border-bottom:1px solid var(--rule); }
  .apps li:last-child { border-bottom:0; }
  .apps p { margin:2px 0 0; font-size:14px; color:var(--muted); }
  .crumb { font-size:14px; margin:0 0 14px; }
"""


def page(title, body, crumb=""):
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex">
<title>{html.escape(title)}</title>
<link rel="icon" type="image/png" href="/favicon.png">
<style>{STYLE}</style>
</head>
<body>
<div class="stage">
{crumb}{body}
</div>
</body>
</html>
"""


def ad_card(a, extra=""):
    mb = a["bytes"] / 1_000_000
    return f"""  <div class="ad">
    <video src="{video_url(a)}" controls playsinline preload="metadata"></video>
    <h3>{html.escape(a['title'])}</h3>
    <p>{html.escape(products[a['product']]['name'])}, {a['device']}, {a['width']} x {a['height']}, {a['seconds']} s, {mb:.1f} MB</p>
    <p><a href="library/{a['file']}">library/{a['file']}</a>{extra}</p>
  </div>"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


# THE SECTION'S FRONT PAGE: the target apps, then the library.
apps = "\n".join(
    f"""  <li><a href="{t['id']}/">{html.escape(t['name'])}</a>
    <p>{html.escape(t['about'])} Shows {len(t['ads'])} ad{'s' if len(t['ads']) != 1 else ''}.
    Manifest: <code>{SITE}/{t['id']}/manifest.json</code></p></li>"""
    for t in cat["targets"])
cards = "\n".join(ad_card(a) for a in cat["library"])
write(os.path.join(HERE, "index.html"), page("BaseCodex house ads", f"""<h1>House ads</h1>
<p class="lede">Adverts for our own products, shown in our free apps. Every video lives once in the
library; each app has a manifest listing the ones it shows.</p>
<section>
<h2>Target apps</h2>
<ul class="apps">
{apps}
</ul>
</section>
<section>
<h2>Library</h2>
<div class="ads">
{cards}
</div>
</section>"""))

# EACH TARGET APP: its manifest and a page showing what it plays.
for t in cat["targets"]:
    m = manifest(t)
    write(os.path.join(HERE, t["id"], "manifest.json"), json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    cards = "\n".join(
        ad_card(library[e["ad"]], f"<br>Weight {e.get('weight', 1)}").replace('href="library/', 'href="../library/')
        for e in t["ads"])
    write(os.path.join(HERE, t["id"], "index.html"), page(f"{t['name']} house ads", f"""<h1>{html.escape(t['name'])}</h1>
<p class="lede">{html.escape(t['about'])} Bundle {html.escape(t['bundleId'])}.</p>
<p class="lede">Manifest: <a href="manifest.json"><code>{SITE}/{t['id']}/manifest.json</code></a> (version {m['version']})</p>
<section>
<h2>Ads it shows</h2>
<div class="ads">
{cards}
</div>
</section>""", crumb='<p class="crumb"><a href="../">House ads</a></p>\n'))

print(f"built ads: {len(cat['library'])} in the library, {len(cat['targets'])} target apps")
