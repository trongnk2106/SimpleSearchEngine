from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
from rank_bm25 import BM25Okapi
import re
from time import sleep
from crawler import Crawler
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = FastAPI()
tok = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', ':', '?']
stop_words = set(stopwords.words('english'))
stop_words.update(tok)
vectorizer = TfidfVectorizer()

def preprocessing(input_string):

    '''
        This module is preprocessing input string with remove stopword
        Args:
            input_string: string
        Returns:
            result_string: string
    '''
    
    words = word_tokenize(input_string)

    filtered_words = [word for word in words if word.lower() not in stop_words]


    result_string = ' '.join(filtered_words)

    return result_string


def content_base(data, query):
    
    '''
        This module is ranking author by content base with tfidf
        Args:
            data: list
            query: string
        Returns:
            recommended_authors: list
    '''

    author_ranking = []
    for dt in data:
        for d in dt:
            author_ranking.append(d)
    
    for i in author_ranking:
        i["title_paper"] = preprocessing(' '.join(i["title_paper"]))
    
    documents = [entry['title_paper'] for entry in author_ranking]
    
    #vectorize documents
    tfidf_matrix = vectorizer.fit_transform(documents)
    # vectorize query
    query_vector = vectorizer.transform([preprocessing(query)])
    # calculate similarity between query and documents
    query_similarity = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # scale total ref to 0-1    
    summ_ref = sum([int(ref['total_ref']) for ref in author_ranking])
    
    for i in range(len(author_ranking)):
        author_ranking[i]['total_ref'] = float(author_ranking[i]['total_ref']) / summ_ref
    # ranking
    for i in range(len(author_ranking)):
        author_ranking[i]['query_similarity'] = query_similarity[i]
        # calculate total score with weight for query similarity, total ref, h_index, i_10_index
        author_ranking[i]['total_score'] = float(author_ranking[i]['h_index']) + 0.5 * float(author_ranking[i]['i_10_index']) + 0.001 * float(author_ranking[i]['total_ref']) + 0.6 * float(author_ranking[i]['query_similarity'])

    # sort list author by total score
    recommended_authors = sorted(author_ranking, key=lambda x: x['total_score'], reverse=True)
 
    return recommended_authors




#route for search, ranking author by contentbase with tfidf
@app.get("/search/{query}", response_class=HTMLResponse)
async def search_and_rank(
    query: str,
    year_filter: str = Query(None, description="Year"),
    num_results: int = Query(None, description="Number of results"),
    sort_by_cites: bool = Query(False, description="Sort by citations")
):
    
    results = Crawler.handlecrawl(textinput = query, number_of_result=num_results)
    

    if not results:
        return HTMLResponse(content="<p>Not Connected Gooogle Scholar.</p>")
    try:
        #get list author
        authorlist = [result['list_author'] for result in results]
        
        #out ranking author
        ranking_author = content_base(authorlist, query)
        
        authorname = [name['author_name'] for name in ranking_author]
        
        #get list paper
        ranked_results = []
        for name_ in authorname:
            for result in results:
                listauthor = result['list_author']
                for aut in listauthor:
                    if aut['author_name'] == name_:
                        if result not in ranked_results:
                            ranked_results.append(result)
                    
        #format html content to display
        html_content = f"<h4>List researcher in that field:</h4>"
        for idex, item in enumerate(ranking_author[1:]):
            html_content += f" <p><strong>{idex}. </strong><a href= '{item['author_url']}' target='_blank'/> <br> Researcher : {item['author_name']}</a> </p>"
        html_content +=  f"<h4>List of papers related to the search topic:</h4>"
        # for idx, result in enumerate(ranked_results, start=1):
        print(ranked_results)
        for idx, result in enumerate(ranked_results, start=1):
            html_content += f"<p><strong>{idx}. </strong>{result['title']}<br>Author: {result['author']}<br>Link: <a href='{result['link_paper']}' target='_blank'>{result['link_paper']}</a></p>"
        
        return HTMLResponse(content=html_content)
    except:
        return HTMLResponse(content="<p>Not Connected Gooogle Scholar.</p>")

#router for update database
@app.get("/update")
async def update_database():
    Crawler.update_database()
    return {"message": "Update database successfully!"}

