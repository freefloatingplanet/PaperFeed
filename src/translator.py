import os, pathlib, json, html
from tenacity import retry, stop_after_attempt, wait_exponential
import requests

DOCS_ITEMS = pathlib.Path("docs/items")

GT_API_KEY = os.environ.get("GOOGLE_TRANSLATE_API_KEY")
GT_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"

if not GT_API_KEY:
    raise SystemExit("GOOGLE_TRANSLATE_API_KEY is not set. Add it to GitHub Secrets.")

def split_chunks(text: str, max_chars=4500):
    """
    Google Translate v2はqの長さに実質上限があります。
    安全サイドでUTF-8文字数4500で分割（英語abstract想定なので充分）。
    """
    text = text or ""
    if not text:
        return []
    # 行区切りを優先して自然に分割
    parts, buf = [], []
    current = 0
    for line in text.splitlines(True):  # keepends
        if current + len(line) > max_chars and buf:
            parts.append("".join(buf))
            buf, current = [line], len(line)
        else:
            buf.append(line); current += len(line)
    if buf:
        parts.append("".join(buf))
    return parts

@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=2, max=20))
def gtranslate_chunk(text: str, target="ja", source="en") -> str:
    """
    単一チャンクの翻訳。HTMLエスケープをデコードして素のテキストに戻す。
    """
    params = {"key": GT_API_KEY}
    data = {
        "q": text,
        "target": target,
        "source": source,
        "format": "text",  # 生テキスト
        # "model": "nmt"  # 明示不要。デフォルトでNMTにルーティングされます
    }
    r = requests.post(GT_ENDPOINT, params=params, data=data, timeout=60)
    if r.status_code >= 400:
        raise requests.HTTPError(f"Google Translate API error: {r.status_code} {r.text[:200]}")
    obj = r.json()
    translated = obj["data"]["translations"][0]["translatedText"]
    # APIはHTMLエスケープされた文字列を返すため、デコードしてから返す
    return html.unescape(translated)

def translate_text(text: str, target="ja", source="en") -> str:
    chunks = split_chunks(text, max_chars=4500)
    if not chunks:
        return "（abstractなし）"
    out = []
    for ch in chunks:
        out.append(gtranslate_chunk(ch, target=target, source=source))
    return "".join(out)

def main():
    raws = sorted(DOCS_ITEMS.glob("*.raw.json"))
    for rf in raws:
        out = rf.with_suffix(".json")
        if out.exists():
            continue
        item = json.loads(rf.read_text(encoding="utf-8"))
        abs_en = (item.get("abstract_en") or "").strip()
        try:
            abs_ja = translate_text(abs_en, target="ja", source="en") if abs_en else "（abstractなし）"
        except Exception as e:
            # 失敗時は英語のまま公開（ログはActions側に出る）
            abs_ja = "（翻訳に失敗したため英語abstractを表示）\n" + abs_en

        result = {
            "id": item["id"],
            "title": item["title"],
            "url": item["url"],
            "published": item.get("published",""),
            "abstract_en": abs_en,
            "abstract_ja": abs_ja,
        }
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
