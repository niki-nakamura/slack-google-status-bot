以下は、Slack用ボットの使い方や設定方法を記載したREADME.mdの例です。リポジトリ直下に配置してください。

---

```markdown
# Google Search Status Slack Bot

## 概要
本リポジトリは、Google Search Status ページからSEOアップデート（特に「Ranking」セクション）の情報を取得し、該当ステータス（例：「Running」など）が検出された場合にSlackへアラートを投稿するボットです。GitHub Actions を利用した定期実行により、最新の状態を自動で通知できます。

## フォルダ構成
```
404-error-handling-and-SEO-optimization
├─ .github
│   └─ workflows
│       └─ scheduled-announce.yml   # Slack 用定期実行ワークフロー
├─ scripts
│   └─ main_announce.py             # Slack 用アナウンススクリプト
│   └─ check_404.py                 # 404エラーなどのチェックスクリプト
│   └─ crawl_links.py               # リンククロール用スクリプト
├─ .gitignore
├─ README.md                        # このファイル
├─ flow.md                          # 処理の流れの説明書
└─ requirements.txt                 # Python依存パッケージ一覧
```

## 動作環境
- **Python バージョン:** 3.x
- **依存パッケージ:**  
  - requests  
  - beautifulsoup4  
  ※ これらは `requirements.txt` に記載されています。

## セットアップ

### 1. GitHub Secrets の設定
GitHub Actions で実行するため、リポジトリのSecretsに以下を追加してください:
- `SLACK_WEBHOOK_URL`: SlackのIncoming Webhook URL

### 2. ローカル実行環境の構築
1. リポジトリをクローン後、依存パッケージをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
2. 環境変数 `SLACK_WEBHOOK_URL` を設定してください。
   ```bash
   export SLACK_WEBHOOK_URL=<your_slack_webhook_url>
   ```
3. Slackボット用スクリプトを実行します。
   ```bash
   python scripts/main_announce.py
   ```

## GitHub Actions による自動実行
`.github/workflows/scheduled-announce.yml` により、毎日UTC 0時（日本時間午前9時）にSlackボットが実行されます。  
ワークフローの概要:
- **チェックアウト:** リポジトリのソースコードを取得
- **Pythonセットアップ:** 必要なPythonバージョンを設定
- **依存パッケージのインストール:** `requests` と `beautifulsoup4` をインストール
- **スクリプト実行:** `scripts/main_announce.py` を実行し、Slackにアナウンスを投稿

## 動作の概要
1. **情報取得:**  
   `main_announce.py` 内でGoogle Search Statusページから「Ranking」セクションの情報（Summary、Date、Duration、ステータスカラー）を抽出します。

2. **投稿判定:**  
   ステータスカラーが "#1E8E3E"（「Available」状態）の場合は投稿をスキップし、それ以外の場合はアラートを投稿します。

3. **Slack への投稿:**  
   取得した情報を元に、SlackのWebhook URLへ対してJSON形式のメッセージを送信します。

## カスタマイズ
- **メッセージ内容の変更:**  
  `scripts/main_announce.py` 内のメッセージフォーマットを編集することで、Slackでの表示内容をカスタマイズできます。

- **実行スケジュールの変更:**  
  GitHub Actions の `.github/workflows/scheduled-announce.yml` 内の `cron` 設定を変更することで、実行タイミングを調整できます。

## その他
- 404エラーやリンククロールなど、他の機能は `scripts/check_404.py` や `scripts/crawl_links.py` に実装されています。  
- 同様の手法で Teams 向けのボット（`scripts/main_announce_teams.py` など）も実装可能です。

---

このREADME.mdを参考に、Slackボットの運用およびカスタマイズを進めてください。
```

---

このREADME.mdは、Slack用ボットの概要、セットアップ手順、動作の流れ、カスタマイズ方法を包括的に説明しています。必要に応じて、環境固有の情報などを追加してください。
