以下では、**リポジトリ構造の再定義**と、それに伴う**コードの修正例**、そして**対外向けREADME.md**のサンプルを提示します。現在の`slack-google-status-bot`リポジトリをより整理した形にするイメージです。必要に応じてパスやファイル名は調整してください。

---

# 1. 新しいリポジトリ構造の提案

```plaintext
slack-google-status-bot/
├── .github/
│   └── workflows/
│       ├── scheduled_announce.yml   # 定期実行・手動実行でmain_announce.pyを動かす
│       └── test_announce.yml        # テスト用ワークフロー (必要に応じて追加)
├── scripts/
│   ├── main_announce.py            # メインのSlack投稿スクリプト
│   ├── test_bot_token.py           # テスト用スクリプト（任意）
│   ├── fetch_html_debug.py         # デバッグ・調査用スクリプト（任意）
│   └── ...
├── requirements.txt                # Python依存パッケージの一覧
├── README.md                       # 対外向けドキュメント
└── ... (LICENSE等、必要に応じてファイルを追加)
```

- `scripts/` ディレクトリに主要なPythonスクリプトを集約し、`main_announce.py` は**Slack通知**を行うメインスクリプトとして配置します。
- `.github/workflows/` ディレクトリ内のYAMLファイルから `scripts/main_announce.py` を呼び出すように変更します。
- `requirements.txt` に必要なライブラリ（`requests`, `beautifulsoup4`など）を記載し、GitHub Actionsでは `pip install -r requirements.txt` で一括インストールするようにします。

---

# 2. コード修正例

## 2.1 GitHub Actionsワークフロー修正例

### `scheduled_announce.yml` （新構造版）
```yaml
name: ScheduledRankingAnnouncement

on:
  schedule:
    - cron: '0 23 * * *'  # 毎日UTC 23時、日本時間で午前8時に実行
  workflow_dispatch:      # 手動実行も可能にする

jobs:
  run_script:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run Slack announce script
        run: python scripts/main_announce.py
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```
- **変更点**  
  - `run: python main_announce.py` → `run: python scripts/main_announce.py`  
  - `pip install requests beautifulsoup4` → `pip install -r requirements.txt` に変更し、依存パッケージを一括管理します。

### （任意）`test_announce.yml`
テスト用ワークフローが必要な場合、同様に `scripts/test_bot_token.py` を呼び出す形に変更します。

---

## 2.2 `scripts/main_announce.py` （新構造版サンプル）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

def get_latest_ranking_info(url):
    """
    Google Search Status ダッシュボードから "Ranking" の最新情報を取得する関数。
    戻り値: (summary_text, summary_link, date_text, duration_text, fill_color) or None
    """
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # 「Ranking」という文字列をもつ要素を探す
    ranking_span = soup.find("span", class_="nAlKgGlv8Vo__product-name", string="Ranking")
    if not ranking_span:
        return None

    # 次に出てくるテーブル
    ranking_table = ranking_span.find_next("table", class_="ise88CpWulY__psd-table")
    if not ranking_table:
        return None

    first_row = ranking_table.find("tbody").find("tr")
    if not first_row:
        return None

    # Summary, Link
    summary_td = first_row.find("td", class_="ise88CpWulY__summary")
    summary_text = summary_td.get_text(strip=True) if summary_td else None
    link_tag = summary_td.find("a") if summary_td else None
    summary_link = urllib.parse.urljoin(url, link_tag.get("href")) if link_tag else None

    # Date
    date_td = first_row.find("td", class_="ise88CpWulY__date")
    date_text = date_td.get_text(strip=True) if date_td else None

    # Duration & fill_color
    duration_td = first_row.find("td", class_="ise88CpWulY__duration")
    duration_span = duration_td.find("span", class_="ise88CpWulY__duration-text") if duration_td else None
    duration_text = duration_span.get_text(strip=True) if duration_span else None

    icon_div = duration_td.find("div", class_="ise88CpWulY__icon-container") if duration_td else None
    svg_tag = icon_div.find("svg") if icon_div else None
    fill_color = None
    if svg_tag:
        path_tag = svg_tag.find("path")
        if path_tag:
            fill_color = path_tag.get("fill")

    return summary_text, summary_link, date_text, duration_text, fill_color


def post_to_slack(webhook_url, message):
    """Slackにシンプルなテキストメッセージを送信する"""
    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()


def main():
    URL = "https://status.search.google.com/summary"
    info = get_latest_ranking_info(URL)

    if not info:
        print("Ranking 情報が取得できませんでした。")
        return

    summary, link, date_, duration, fill_color = info

    # "Available" 状態(#1E8E3E) なら通知不要
    if fill_color == "#1E8E3E":
        print("現在のステータスは『Available』のため、Slackへのアナウンスは不要です。")
        return

    # Slackに投稿するメッセージ
    message = (
        "@channel\n"
        ":red_circle: *Google Search Status Update: Running*\n\n"
        "現在のSEOアップデート状況をお知らせします：\n"
        f"• Summary : {summary}\n"
        f"• Date : {date_}\n"
        f"• Duration: {duration}\n"
        f"• Link（詳細） : {link}\n\n"
        "アップデート中のアクション：\n"
        "①大規模改修・大量削除は控える\n"
        "②順位・被リンク・インデックス状況のモニタリングを強化\n"
        "③施策の優先度をつけて小さく検証 → 即フィードバック\n"
        "→変動幅が大きいページを早期にテコ入れすることで、"
        "アップデート期間中でも部分的に回復できるケースもある。\n\n"
        "詳細はこちら "
        "「<https://docs.google.com/spreadsheets/d/1WXF39iuIYObQ1HP4aVauJfFcrkzJ6q4BYX7eln_5jI4/edit?gid=816217153#gid=816217153|"
        "GSSD Bot活用方法（Google Search Status Dashboard）>」"
    )

    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL が設定されていません。")
        return

    post_to_slack(slack_webhook_url, message)
    print("Slackに投稿しました。")


if __name__ == "__main__":
    main()
```

- **変更点**  
  - ファイルを `scripts/` ディレクトリへ移動。
  - ワークフローの `run: python scripts/main_announce.py` に合わせた相対パスで呼び出せるように。
  - 依存パッケージはすべて `requirements.txt` に集約。

---

## 2.3 `requirements.txt` 例

```plaintext
requests>=2.0
beautifulsoup4>=4.0
```

- 必要に応じて `urllib3` や `lxml` などを追加してください。
- GitHub Actions側で `pip install -r requirements.txt` することで依存関係を一括インストールできます。

---

# 3. 対外用 README.md（サンプル）

```markdown
# slack-google-status-bot

Google Search Status ダッシュボードの「Ranking」状況を自動取得し、Slackへ通知するBotです。

## 機能概要
- **Google Search Status** (https://status.search.google.com/summary) をスクレイピングし、
  「Ranking」の最新ステータスを取得します。
- ステータスカラーが「#1E8E3E」(= Available) 以外の場合に、Slackへ状況を通知します。
- GitHub Actions でスケジュール実行（cron）または手動実行でき、運用コストを削減します。

## リポジトリ構成

```plaintext
slack-google-status-bot/
├── .github/
│   └── workflows/
│       ├── scheduled_announce.yml   # 定期実行・手動実行で main_announce.py を動かす
│       └── test_announce.yml        # テスト用ワークフロー (必要に応じて)
├── scripts/
│   ├── main_announce.py            # メインのSlack投稿スクリプト
│   ├── test_bot_token.py           # テスト用スクリプト (任意)
│   ├── fetch_html_debug.py         # HTMLを直接取得して確認するデバッグ用 (任意)
│   └── ...
├── requirements.txt                # Python依存パッケージの一覧
├── README.md                       # 本ファイル
└── ... (LICENSE等を必要に応じて追加)
```

## セットアップ手順

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com/niki-nakamura/slack-google-status-bot.git
   cd slack-google-status-bot
   ```

2. **Python依存パッケージをインストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **Slack Webhook URLを設定**
   - GitHubリポジトリの[Settings > Secrets and variables > Actions]にて `SLACK_WEBHOOK_URL` を追加してください。

4. **ローカルでの実行テスト** (オプション)
   ```bash
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx"
   python scripts/main_announce.py
   ```
   - ステータスが「Available」以外の場合にSlackへメッセージが投稿されます。

## GitHub Actionsワークフロー

- `.github/workflows/scheduled_announce.yml` で、毎日 UTC 23時（日本時間8時）に自動実行される設定になっています。
  ```yaml
  on:
    schedule:
      - cron: '0 23 * * *'
    workflow_dispatch:
  ```
- ステータスが更新されている場合のみ Slackへ投稿し、ステータスが「Available」(#1E8E3E) の場合は投稿をスキップします。

## カスタマイズ
- **実行タイミング変更**  
  `scheduled_announce.yml` の `cron` を編集してください。
- **スクレイピング対象URL変更**  
  `scripts/main_announce.py` 内の `URL = "https://status.search.google.com/summary"` を書き換えてください。
- **メッセージ文言変更**  
  `scripts/main_announce.py` の `message` 変数を編集してください。

## ライセンス
本リポジトリは MIT ライセンスの下で公開されています。詳細は[LICENSE](LICENSE)をご参照ください。

---

以上の手順で、GitHub Actionsを用いた定期監視とSlack通知が行えます。必要に応じてフォルダ名やスクリプト名などを調整してご利用ください。
```

---

## 4. まとめ

1. **新しいフォルダ構成**を定義し、`.github/workflows/` と `scripts/` などでコードを整理。  
2. **ワークフローYAML**で `run: python scripts/main_announce.py` に変更し、**requirements.txt** から一括インストールするよう修正。  
3. **対外向けREADME.md**を作成し、使い方・セットアップ・構造をわかりやすく説明。

これらにより、保守性と可読性が向上し、GitHub ActionsとSlack通知がスムーズに連携できるようになります。必要に応じて、テスト用ワークフローやその他のスクリプトを追加入力して運用してください。
