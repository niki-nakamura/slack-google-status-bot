import requests

url = "https://status.search.google.com/summary"
response = requests.get(url)
html = response.text

print(html)  # 実際のHTMLがどうなっているかを出力

from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
all_h2 = soup.find_all("h2")

for i, h2 in enumerate(all_h2, 1):
    print(f"[{i}] {h2.get_text(strip=True)}")

def fetch_latest_ranking_status():
    url = "https://status.search.google.com/summary"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    
    # デバッグ: h2タグのテキストを全部出してみる
    all_h2 = soup.find_all("h2")
    for h2 in all_h2:
        print("Found h2 text:", repr(h2.get_text(strip=True)))
    
    # 1) "Ranking" の文字列が含まれていればそれをセクションの起点とする
    ranking_section = None
    for h2 in all_h2:
        h2_text = h2.get_text(strip=True)
        if "Ranking" in h2_text:  # 完全一致ではなく部分一致
            # h2を含む親要素などから該当のセクションを取得する
            ranking_section = h2.find_parent("div", class_="product-group")
            # もし親要素のクラスが異なるなら要調整
            break

    if not ranking_section:
        print("Could not find Ranking section.")
        return None

    # 2) Ranking セクション内のテーブル行を探す
    table_rows = ranking_section.find_all("tr")
    if not table_rows:
        print("No table rows found in Ranking section.")
        return None
    
    # デバッグ: 先頭2行のtdを出してみる
    for i, tr in enumerate(table_rows[:2], 1):
        tds = tr.find_all("td")
        print(f"[Row {i}]", [td.get_text(strip=True) for td in tds])
    
    # 3) 実データが何行目にあるかを確認して取り出す
    #    例えば 0行目がヘッダ (Summary / Date / Duration) で、1行目〜が実データ、という場合
    latest_row = table_rows[1] if len(table_rows) > 1 else None
    if not latest_row:
        return None

    cols = latest_row.find_all("td")
    if len(cols) < 3:
        return None

    summary = cols[0].get_text(strip=True)
    date = cols[1].get_text(strip=True)
    duration = cols[2].get_text(strip=True)

    return {
        "summary": summary,
        "date": date,
        "duration": duration
    }
