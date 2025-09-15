import os, json, time, re, logging, requests
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

USER_AGENT = os.environ.get("USER_AGENT", "ArxivAbstractsJA/1.0 (contact: you@example.com)")
HEADERS = {"User-Agent": USER_AGENT}

def ensure_dirs(*paths):
    import pathlib
    for p in paths:
        pathlib.Path(p).mkdir(parents=True, exist_ok=True)

def load_json(path: str, default):
    import pathlib
    p = pathlib.Path(path)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return default

def save_json(path: str, obj):
    import pathlib
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def extract_arxiv_id(url_or_text: str) -> Optional[str]:
    s = (url_or_text or "").strip().rstrip("/")
    m = re.search(r"(\d{4}\.\d{4,5})(?:v\d+)?$", s)
    if m: return m.group(1)
    m = re.search(r"([a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?$", s, re.IGNORECASE)
    if m: return m.group(1)
    return None

@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=1, max=20))
def http_get(url: str, timeout=60) -> requests.Response:
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    if r.status_code >= 400:
        raise requests.HTTPError(f"GET {url} -> {r.status_code}")
    return r

def polite_sleep(sec=1.2): time.sleep(sec)

