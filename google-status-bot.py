import requests
from bs4 import BeautifulSoup
import urllib.parse

def get_latest_ranking_info(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # class="nAlKgGlv8Vo__product-name" かつ "Ranking" の文字を持つ <span> を探す
    ranking_span = soup.find("span", class_="nAlKgGlv8Vo__product-name", string="Ranking")
    if not ranking_span:
        print("Ranking の要素が見つかりませんでした。")
        return None

    # 次に出てくる table (同じブロック内の <table class="ise88CpWulY__psd-table">)
    ranking_table = ranking_span.find_next("table", class_="ise88CpWulY__psd-table")
    if not ranking_table:
        print("Ranking テーブルが見つかりませんでした。")
        return None

    first_row = ranking_table.find("tbody").find("tr")
    if not first_row:
        print("Rankingテーブル内にデータがありません。")
        return None

    summary_td = first_row.find("td", class_="ise88CpWulY__summary")
    summary_text = summary_td.get_text(strip=True) if summary_td else None
    link_tag = summary_td.find("a") if summary_td else None
    summary_link = urllib.parse.urljoin(url, link_tag.get("href")) if link_tag else None

    date_td = first_row.find("td", class_="ise88CpWulY__date")
    date_text = date_td.get_text(strip=True) if date_td else None

    duration_td = first_row.find("td", class_="ise88CpWulY__duration")
    duration_span = duration_td.find("span", class_="ise88CpWulY__duration-text") if duration_td else None
    duration_text = duration_span.get_text(strip=True) if duration_span else None

    return summary_text, summary_link, date_text, duration_text

if __name__ == "__main__":
    URL = "https://status.search.google.com/summary"
    info = get_latest_ranking_info(URL)
    if info:
        summary, link, date_, duration = info
        print("[Ranking] 最新の情報")
        print("Summary :", summary)
        print("Link    :", link)
        print("Date    :", date_)
        print("Duration:", duration)
    else:
        print("情報を取得できませんでした。")
