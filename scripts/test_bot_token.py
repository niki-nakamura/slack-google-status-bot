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

    # ステータスカラー(#1E8E3E 等) を取得する
    icon_div = duration_td.find("div", class_="ise88CpWulY__icon-container") if duration_td else None
    svg_tag = icon_div.find("svg") if icon_div else None
    fill_color = None
    if svg_tag:
        path_tag = svg_tag.find("path")
        if path_tag:
            fill_color = path_tag.get("fill")  # 例: "#1E8E3E"

    return summary_text, summary_link, date_text, duration_text, fill_color

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

    summary, link, date_, duration, fill_color = info

    fill_color = "#E37400"  # ここで強制的に「オレンジ」に設定

    # それ以外のカラーの場合 → @channel + デザイン付きでメッセージ投稿
    # Slackメッセージ本体
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
        "詳細はこちら"
        "「<https://docs.google.com/spreadsheets/d/1WXF39iuIYObQ1HP4aVauJfFcrkzJ6q4BYX7eln_5jI4/edit?gid=816217153#gid=816217153|"
        "GSSD Bot活用方法（Google Search Status Dashboard）>」"
    )

    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("SLACK_WEBHOOK_URL が設定されていません。")
        return

    # 投稿
    post_to_slack(slack_webhook_url, message)
    print("Slackに投稿しました。")

if __name__ == "__main__":
    main()
