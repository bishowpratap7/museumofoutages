#!/usr/bin/env python3
"""Museum of Outages scanner: watches the public status pages of GitHub,
Cloudflare, npm and Vercel for recent incidents (the Emergency Room),
writes data/feed.json, bakes the ER list + exhibit ItemList into
index.html, regenerates feed.xml and sitemap.xml. On failure it keeps
the previous data rather than blanking the museum."""
import json, os, re, subprocess, sys
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
SITE = "https://bishowpratap7.github.io/museumofoutages/"
PROVIDERS = [
    ("GitHub", "https://www.githubstatus.com"),
    ("Cloudflare", "https://www.cloudflarestatus.com"),
    ("npm", "https://status.npmjs.org"),
    ("Vercel", "https://www.vercel-status.com"),
]
EXHIBITS = [
    ("Knight Capital: The 45-Minute Fortune (2012)", "#"),
    ("Cloudflare: One Rule to Slow Them All (2019)", "#"),
    ("CrowdStrike: The Day the World Blue-Screened (2024)", "#"),
    ("Fastly: The Customer Who Broke the Web by Using It Correctly (2021)", "https://www.fastly.com/blog/summary-of-june-8-outage"),
    ("Facebook: The Day the Internet's Biggest House Lost Its Own Address (2021)", "#"),
    ("AWS: The Automation That Congested Its Own Cloud (2021)", "#"),
    ("AWS S3: The Four-Hour Typo (2017)", "#"),
    ("Dyn: The Webcam Army (2016)", "#"),
    ("British Airways: The Power Cable Incident (2017)", "#"),
    ("OVHcloud: The Night the Cloud Caught Fire (2021)", "#"),
    ("GitHub: Forty-Three Seconds, Twenty-Four Hours (2018)", "https://blog.github.com/2018-10-30-oct21-post-incident-analysis/"),
]

def fetch(url, timeout=25):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        out = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-A", UA, url],
                             capture_output=True, text=True)
        if out.returncode == 0 and out.stdout:
            return out.stdout
        raise

def esc(t):
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def main():
    cutoff = datetime.now(timezone.utc) - timedelta(days=14)
    incidents = []
    for name, base in PROVIDERS:
        try:
            data = json.loads(fetch(base + "/api/v2/incidents.json"))
            for inc in data.get("incidents", []):
                created = inc.get("created_at", "")
                try:
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                except Exception:
                    continue
                if dt < cutoff:
                    continue
                incidents.append({
                    "provider": name,
                    "title": inc.get("name", "Incident"),
                    "status": inc.get("status", ""),
                    "impact": inc.get("impact", ""),
                    "url": inc.get("shortlink") or base,
                    "date": dt.strftime("%b %d, %H:%M UTC"),
                    "_dt": dt.isoformat(),
                })
            print(f"{name}: ok")
        except Exception as e:
            print(f"{name}: FAILED {e}", file=sys.stderr)
    incidents.sort(key=lambda i: i["_dt"], reverse=True)
    for i in incidents:
        i.pop("_dt", None)
    incidents = incidents[:12]
    prev_path = os.path.join(ROOT, "data", "feed.json")
    if not incidents and os.path.exists(prev_path):
        try:
            prev = json.load(open(prev_path))
            if prev.get("incidents"):
                incidents = prev["incidents"]
                print("no fresh incidents; kept previous ER board")
        except Exception:
            pass
    out = {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
           "incidents": incidents}
    with open(prev_path, "w") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    bake(out)
    return 0

def bake(out):
    ipath = os.path.join(ROOT, "index.html")
    html = open(ipath).read()
    if out["incidents"]:
        lines = ['<div class="er">']
        for i in out["incidents"]:
            imp = f" · impact: {esc(i['impact'])}" if i.get("impact") and i["impact"] != "none" else ""
            lines.append(f"<div class=\"item\"><a href=\"{esc(i['url'])}\">{esc(i['title'])}</a>"
                         f"<div class=\"m\">{esc(i['provider'])} · status: {esc(i['status'])} · {esc(i['date'])}{imp}</div></div>")
        lines.append("</div>")
        block = "\n".join(lines)
    else:
        block = "<p>All quiet on the status pages — the Emergency Room is empty.</p>"
    ld = {"@context": "https://schema.org", "@type": "ItemList",
          "name": "Exhibits in the Museum of Outages",
          "itemListElement": [{"@type": "ListItem", "position": n + 1, "name": t,
                               **({"url": u} if u != "#" else {})}
                              for n, (t, u) in enumerate(EXHIBITS)]}
    ld_html = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False) + "\n</script>"
    new = re.sub(r"<!--ER:START-->.*?<!--ER:END-->",
                 "<!--ER:START-->\n" + block + "\n<!--ER:END-->", html, flags=re.S)
    new = re.sub(r"<!--ITEMLIST:START-->.*?<!--ITEMLIST:END-->",
                 "<!--ITEMLIST:START-->\n" + ld_html + "\n<!--ITEMLIST:END-->", new, flags=re.S)
    if new != html:
        open(ipath, "w").write(new)
        feed = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
                f"<title>Museum of Outages</title><link>{SITE}</link>"
                "<description>Famous outages, preserved. Plus recent incidents on the major status pages.</description>\n")
        for i in out["incidents"][:8]:
            feed += (f"<item><title>{esc(i['title'])} ({esc(i['provider'])})</title>"
                     f"<link>{esc(i['url'])}</link><guid>{esc(i['url'])}</guid>"
                     f"<pubDate>{out['generated_at']}</pubDate></item>\n")
        feed += "</channel></rss>"
        open(os.path.join(ROOT, "feed.xml"), "w").write(feed)
        sm = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
              f"<url><loc>{SITE}</loc><lastmod>{out['generated_at']}</lastmod>"
              "<changefreq>daily</changefreq><priority>1.0</priority></url></urlset>")
        open(os.path.join(ROOT, "sitemap.xml"), "w").write(sm)
        print("baked: changed")
    else:
        print("baked: unchanged")

if __name__ == "__main__":
    sys.exit(main())
