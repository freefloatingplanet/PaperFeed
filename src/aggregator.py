import pathlib, json, feedparser
from dateutil import parser as dtp
from bs4 import BeautifulSoup
from src.utils import ensure_dirs, load_json, save_json, extract_arxiv_id

DATA = pathlib.Path("data")
DOCS_ITEMS = pathlib.Path("docs/items")
SEEN = DATA / "seen.json"
CFG_FEEDS = pathlib.Path("config/feeds.yml")

ensure_dirs(DATA, DOCS_ITEMS)

def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "lxml")
    for tag in soup.find_all(["script","style"]): tag.decompose()
    return soup.get_text("\n").strip()

def main():
    import yaml
    seen = set(load_json(SEEN, []))
    feeds = yaml.safe_load(CFG_FEEDS.read_text(encoding="utf-8"))
    new_items = []

    for url in feeds["feeds"]:
        fp = feedparser.parse(url)
        for e in fp.entries:
            link = e.get("link") or e.get("id") or ""
            aid = extract_arxiv_id(link or e.get("title",""))
            if not aid: continue
            if aid in seen: continue

            title = (e.get("title") or "").strip()
            abstr_html = (e.get("summary") or "").strip()
            abstr = html_to_text(abstr_html)
            pub = (e.get("published") or e.get("updated") or "").strip()
            published_iso = dtp.parse(pub).isoformat() if pub else ""

            new_items.append({
                "id": aid,
                "title": title,
                "url": link or f"https://arxiv.org/abs/{aid}",
                "published": published_iso,
                "abstract_en": abstr
            })

    for it in new_items:
        (DOCS_ITEMS / f"{it['id']}.raw.json").write_text(json.dumps(it, ensure_ascii=False), encoding="utf-8")
        seen.add(it["id"])

    save_json(SEEN, sorted(seen))

if __name__ == "__main__":
    main()

