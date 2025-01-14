import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

def get_latest_ranking_info(url):
    # ダッシュボードを取得
    response = requests.get(url)
    response.raise_for_status()

    # パース
    soup = BeautifulSoup(response.text, "html.parser")

    # 「Ranking」と書かれた要素を取得
    ranking_span = soup.find("span", class_="nAlKgGlv8Vo__product-name", string="Ranking")
    if not ranking_span:
        return None

    # 次に出てくるテーブルを取得
    ranking_table = ranking_span.find_next("table", class_="ise88CpWulY__psd-table")
    if not ranking_table:
        return None

    # tbody -> 最初の <tr>
    first_row = ranking_table.find("tbody").find("tr")
    if not first_row:
        return None

    # Summary (タイトル)
    summary_td = first_row.find("td", class_="ise88CpWulY__summary")
    summary_text = summary_td.get_text(strip=True) if summary_td else None
    link_tag = summary_td.find("a") if summary_td else None
    summary_link = urllib.parse.urljoin(url, link_tag.get("href")) if link_tag else None

    # Date
    date_td = first_row.find("td", class_="ise88CpWulY__date")
    date_text = date_td.get_text(strip=True) if date_td else None

    # Duration
    duration_td = first_row.find("td", class_="ise88CpWulY__duration")
    duration_span = duration_td.find("span", class_="ise88CpWulY__duration-text") if duration_td else None
    duration_text = duration_span.get_text(strip=True) if duration_span else None

    return summary_text, summary_link, date_text, duration_text

def post_to_slack(webhook_url, message):
    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()

def main():
    URL = "https://status.search.google.com/summary"
    info = get_latest_ranking_info(URL)

    if not info:
        print("Ranking 情報が取得できませんでした。")
        return

    summary, link, date_, duration = info

    # Slackに投稿するメッセージを作成
    message = (
        f"*[Ranking 最新情報]*\n"
        f"• Summary : {summary}\n"
        f"• Link    : {link}\n"
        f"• Date    : {date_}\n"
        f"• Duration: {duration}"
    )

    # Secrets (環境変数) から Webhook URL を読み込み
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL が設定されていません。")
        return

    # 投稿
    post_to_slack(slack_webhook_url, message)
    print("Slackに投稿しました。")

if __name__ == "__main__":
    main()
