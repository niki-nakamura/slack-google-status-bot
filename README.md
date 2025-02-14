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
