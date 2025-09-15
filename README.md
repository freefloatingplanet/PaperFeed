# PaperFeed
# arXiv Abstracts JA（DeepL翻訳） / GitHub Pages

arXivの複数フィードを集約し、**abstractのみ**を DeepL API Free で日本語に翻訳して RSS/ページ公開する仕組みです。LLM要約は使いません。

## セットアップ

1. リポジトリに本プロジェクトを配置
2. Settings → **Pages** → Branch: `main`, Folder: `/docs`
3. Settings → **Secrets and variables → Actions** で以下を登録
   - `DEEPL_API_KEY` : DeepL API Free のキー
   - `USER_AGENT`    : `YourAppName/1.0 (contact: your_email@example.com)`（任意）
4. `config/site.yml` の `site_url` を自サイトURLに変更
5. `config/feeds.yml` に arXiv の検索フィードURLを列挙
6. Actions タブ → `arXiv Abstracts JA (DeepL)` を **Run workflow** で初回実行
7. 公開URL：`https://<your-user>.github.io/<repo>/`

## ローカル実行（任意）
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GOOGLE_TRANSLATE_API_KEY=...
export USER_AGENT="YourAppName/1.0 (contact: your_email@example.com)"
python -m src.aggregator
python -m src.translator
python -m src.publisher
# docs/index.html をブラウザで開く

