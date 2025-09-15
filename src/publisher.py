import pathlib, json, yaml
from feedgen.feed import FeedGenerator

DOCS = pathlib.Path("docs")
ITEMS = DOCS / "items"

CONFIG = yaml.safe_load(pathlib.Path("config/site.yml").read_text(encoding="utf-8"))
SITE_TITLE = CONFIG.get("site_title","arXiv Abstracts (ja)")
SITE_DESC  = CONFIG.get("site_desc","arXiv abstractを日本語に翻訳")
SITE_URL   = CONFIG.get("site_url","")
LANG       = CONFIG.get("language","ja")
FEED_LIMIT = int(CONFIG.get("feed_limit",200))
INDEX_LIMIT = int(CONFIG.get("index_limit",120))

def load_items():
    items = []
    for p in ITEMS.glob("*.json"):
        if p.name.endswith(".raw.json"): continue
        items.append(json.loads(p.read_text(encoding="utf-8")))
    items.sort(key=lambda x: x.get("published",""), reverse=True)
    return items

def build_feed(items):
    fg = FeedGenerator()
    fg.title(SITE_TITLE)
    if SITE_URL:
        fg.link(href=f"{SITE_URL.rstrip('/')}/feed.xml", rel='self')
        fg.link(href=SITE_URL, rel='alternate')
    fg.description(SITE_DESC)
    fg.language(LANG)

    for it in items[:FEED_LIMIT]:
        fe = fg.add_entry()
        fe.id(it["id"])
        fe.title(it["title"])
        fe.link(href=it["url"])
        if it.get("published"): fe.published(it["published"])
        # RSS description は翻訳済みabstract（JA）を入れる
        desc = it.get("abstract_ja","").strip()
        fe.description(desc)
    fg.rss_file(str(DOCS/"feed.xml"))

def build_index_json(items):
    arr = []
    for it in items[:INDEX_LIMIT]:
        arr.append({
            "id": it["id"],
            "title": it["title"],
            "url": it["url"],
            "published": it.get("published",""),
            "abstract_ja": it.get("abstract_ja","")[:1000],
        })
    (ITEMS/"index.json").write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    DOCS.mkdir(parents=True, exist_ok=True)
    ITEMS.mkdir(parents=True, exist_ok=True)
    items = load_items()
    build_feed(items)
    build_index_json(items)

if __name__ == "__main__":
    main()

