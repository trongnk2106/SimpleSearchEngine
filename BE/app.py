from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
from rank_bm25 import BM25Okapi
import re
from time import sleep
from crawler import Crawler


app = FastAPI()

# collection = DB.get_instance().collection

# Hàm để thực hiện crawler trang Google Scholar với các tham số lọc
def google_scholar_crawler(query, year_filter=None, num_results=None):
    base_url = "https://scholar.google.com/scholar"
    params = {'q': query}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
  
    # Thêm các tham số lọc nếu được chọn
    if year_filter:
        params['as_ylo'] = year_filter
    if num_results:
        params['num'] = num_results

    response = requests.get(base_url, params=params, headers=headers)
    sleep(0.5)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        # Duyệt qua các kết quả tìm kiếm và lấy thông tin
        for result in soup.find_all('div', class_='gs_ri'):
            title = result.find('h3', class_='gs_rt').get_text()
            authors = result.find('div', class_='gs_a').get_text()
            abstract = result.find('div', class_='gs_rs')
            link = result.find('a')['href']

            # Lưu thông tin vào MongoDB
            article_data = {
                "title": title,
                "authors": authors,
                "abstract": abstract.get_text() if abstract else '',
                "link": link
            }
            # collection.update_one({"query": query}, {"$push": {"results": article_data}}, upsert=True)

            results.append({'title': title, 'author': authors, 'abstract': abstract.get_text() if abstract else '', 'link': link})

        return results
    else:
        return None



# Route để xử lý yêu cầu tìm kiếm và ranking sử dụng BM25
@app.get("/search/{query}", response_class=HTMLResponse)
async def search_and_rank(
    query: str,
    year_filter: str = Query(None, description="Năm"),
    num_results: int = Query(None, description="Số lượng kết quả tìm kiếm"),
    sort_by_cites: bool = Query(False, description="Sắp xếp theo số lần trích dẫn")
):
    # Gọi hàm crawler
    # results = google_scholar_crawler(query, year_filter, num_results)
    results = Crawler.handlecrawl(textinput = query, number_of_result=num_results)
    # print(result2)
    # print(results)

    if not results:
        return HTMLResponse(content="<p>Không thể kết nối đến Google Scholar.</p>")

    # Tính toán BM25 cho tất cả các documents
    contents = [result['abstract'] for result in results]
    tokenized_contents = [content.split() for content in contents]
    bm25 = BM25Okapi(tokenized_contents)

    # Tính toán điểm BM25 giữa query và các documents
    scores = bm25.get_scores(query.split())

    # Sắp xếp kết quả dựa trên điểm BM25
    ranked_results = [{'result': result, 'bm25_score': score} for result, score in zip(results, scores)]
    ranked_results = sorted(ranked_results, key=lambda x: x['bm25_score'], reverse=True)

    # Tạo HTML để hiển thị kết quả
    html_content = f"<h2>Kết quả tìm kiếm và ranking cho '{query}' (Thuật toán: BM25):</h2>"
    for idx, result in enumerate(ranked_results, start=1):
        html_content += f"<p><strong>{idx}. </strong>{result['result']['title']}<br>Tác giả: {result['result']['author']}<br>Link: <a href='{result['result']['link']}' target='_blank'>{result['result']['link']}</a><br>BM25 Score: {result['bm25_score']}</p>"
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)