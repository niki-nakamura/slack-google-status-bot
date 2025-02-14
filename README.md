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
