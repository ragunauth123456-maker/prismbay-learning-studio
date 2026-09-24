from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "index.html", ROOT / "privacy.html", *sorted((ROOT / "guides").glob("*.html"))]
class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"): self.refs.append(a["href"])
        if tag == "link" and a.get("href"): self.refs.append(a["href"])

errors = []
for page in PAGES:
    body = page.read_text(encoding="utf-8")
    p = Links()
    p.feed(body)
    if not re.search(r'<meta name="description"', body): errors.append(f"{page.name}: description missing")
    for href in p.refs:
        parsed = urlsplit(href)
        if parsed.scheme or href.startswith(("#", "mailto:", "tel:")): continue
        target = (page.parent / unquote(parsed.path)).resolve()
        if target.is_dir() or parsed.path in (".", ".."): target = target / "index.html"
        if not target.is_file(): errors.append(f"{page.name}: broken local link {href}")
    print(f"PASS {page.relative_to(ROOT)}: {len(p.refs)} links")
if len(PAGES) != 5: errors.append("Expected homepage, privacy and three original guides")
if any(len(re.findall(r"\b[\w'-]+\b", p.read_text(encoding="utf-8"))) < 450 for p in PAGES[2:]):
    errors.append("One or more guides lack sufficient original reading material")
sitemap = ET.parse(ROOT / "sitemap.xml")
ns = {"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
locs = [el.text for el in sitemap.findall(".//s:loc", ns)]
if len(locs) != len(PAGES): errors.append("Sitemap does not list all five pages")
if "buy.stripe.com" not in (ROOT / "index.html").read_text(): errors.append("Stripe CTA missing")
if errors:
    print("\n".join("FAIL " + x for x in errors))
    raise SystemExit(1)
print(f"ALL PASS: {len(PAGES)} pages, sitemap, local links and Stripe CTA")
