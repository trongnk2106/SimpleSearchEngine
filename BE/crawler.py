import requests, os, datetime, argparse
from bs4 import BeautifulSoup
# import matplotlib.pyplot as plt

from time import sleep
import warnings
import os
import sys
from database import DB 

collection = DB.get_instance().collection


# Default Parameters
KEYWORD = 'Machine Learning' # Default argument if command line is empty
NRESULTS = 100 # Fetch 100 articles
CSVPATH = os.getcwd() # Current folder as default path
SAVECSV = True
SORTBY = 'Citations'
PLOT_RESULTS = False
STARTYEAR = None
now = datetime.datetime.now()
ENDYEAR = now.year # Current year
DEBUG=False # debug mode
MAX_CSV_FNAME = 255
if sys.version[0]=="3": raw_input=input


# Websession Parameters
GSCHOLAR_URL = 'https://scholar.google.com/scholar?start={}&q={}&hl=en&as_sdt=0,5'
YEAR_RANGE = '' #&as_ylo={start_year}&as_yhi={end_year}'
STARTYEAR_URL = '&as_ylo={}'
ENDYEAR_URL = '&as_yhi={}'
ROBOT_KW=['unusual traffic from your computer network', 'not a robot']
ABSTRACT = ["core-container", "c-article-section__content", "article open abstract", 'html-p','abstract']

class Crawler:

    def setup_driver(self):
        try : 
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.common.exceptions import StalementReferenceException
        except Exception as e:
            print(e)
            print("Please install selenium and chromedriver")
        print("Setting up driver...")
        chrome_options = Options()
        chrome_options.add_argument("disable-infobars")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        return driver
        

    def get_element(self, driver, xpath, attemps=5, _count=0):
        try : 
            element = driver.find_element_by_xpath(xpath)
            return element
        except Exception as e:
            if _count< attemps:
                sleep(1)
                self.get_element(driver, xpath, attemps=attemps, _count=_count+1)
            else : 
                print("Element not found")


    def get_content_with_selenium(self, url):
        if 'driver' not in globals():
            global driver
            driver = self.setup_driver()
        
        driver.get(url)
        
        crsl = self.get_element(driver, "/html/body")
        c = crsl.get_attribute('innerHTML')
        
        if any(kw in crsl.text for kw in ROBOT_KW):
            raw_input("Solve captcha manually and press enter here to continue...")
            el = self.get_element(driver, "/html/body")
            c = el.get_attribute('innerHTML')


        return c.encode('utf-8')

    def get_cities(content):
        '''
        Args:
            content : str , parse html content
        return:
            int : number of cities
        '''
      
        out = 0
        for char in range(0, len(content)):
            if content[char: char +9 ] == "Cited by ":
                init = char + 9
                for end in range(init+1, init + 6):
                    if content[end] == '<':
                        break
                out = content[init:end]
        return int(out)

    def get_year(content):
        
        '''
            Args:
                content : str , parse html content
            return:
                year : int , year of article
        '''
        # print(content)
        for char in range(0, len(content)):
            if content[char] == "-":
                out = content[char-5: char-1]
            
        if not out.isdigit():
            out = 0
        return int(out)

    def get_article_content(self, url : setup_driver) -> str:
        
        '''
            Args: 
                url : str , url of article
            Return:
                str : content of article
        '''
       #http request
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
    
        try :
            
            if response.status_code == 200:
                article_soup = BeautifulSoup(response.text, 'html.parser')
                # get article content
                article_content = article_soup.find('div', class_='c-article-body')  
                # print(f:\n{article_content.get_text() if article_content else 'N/A'}")
            # else:
            #     print(f"Không thể truy cập trang chi tiết. Mã trạng thái: {response.status_code}")

        except Exception as e:
            print(e)
            print("Error when get article content")
            return None
        


    def check_exist(query:str):
        '''
            Args:
                query : str , query keyword
            Return:
                bool : True if query exist in database
        '''

        res = collection.find_one({"query": query})
        if res:
            return res
        return None  
    
    def get_titlepaper():
        pass
    
    def get_hindex(url_link):
        res = []
        list_url_authors = url_link.find_all('a')
  
        for url_lk in list_url_authors:
            url = url_lk.get('href')
            if not url.startswith('https:'):
                author_url = f'https://scholar.google.com{url}'
                # print(author_url)
            # request
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(author_url, headers=headers)
            # print(author_url)
            try :
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    author_name = soup.find('div', id='gsc_prf_in').get_text()
                    rows = soup.find_all('tr')
                    h_index = rows[2].find_all('td')[1].get_text()
                    i_10_index = rows[3].find_all('td')[1].get_text()
                    total_ref = rows[1].find_all('td')[1].get_text()
                    
                    table = soup.find('tbody', id='gsc_a_b').find_all('tr', class_="gsc_a_tr")
                    title_paper = []
                    for tb in table:
                        title_paper.append(tb.find('td', class_='gsc_a_t').find('a').get_text())
                    data = {
                        "author_name": author_name,
                        "h_index": h_index,
                        "i_10_index": i_10_index,
                        "total_ref": total_ref,
                        "title_paper": title_paper,
                        "author_url": author_url
                    }
                res.append(data)
               
                    # return h_index
                    # print(author_name)
            except Exception as e:
                pass
            
        return res

    @staticmethod
    def handlecrawl(textinput, number_of_result , start_year = STARTYEAR, end_year = ENDYEAR, isudpate = False, list_update = []):
        
        '''
        Args: 
            textinput : str , query keyword
            number_of_result : int , number of result
            start_year : int , start year
            end_year : int , end year
            isudpate : bool , update database
            list_update : list , list of query keyword
        Return:
            list : list of result content information of article by query keyword
        '''

        if start_year :
            GSCHOLAR_MAIN_URL = GSCHOLAR_URL + STARTYEAR_URL.format(start_year)
        else :
            GSCHOLAR_MAIN_URL = GSCHOLAR_URL
        
        if end_year != now.year:
            GSCHOLAR_MAIN_URL = GSCHOLAR_URL + ENDYEAR_URL.format(end_year)
        
        session = requests.Session()
        res_check_exist = None
        
        if isudpate:
            for query_ in list_update:
                for i in range(0, number_of_result, 10):
                
                    url = GSCHOLAR_MAIN_URL.format(str(i), query_.replace(' ', '+'))
                    
                    page = session.get(url)
                    
                    c = page.content
                
                    if any(kw in c.decode("ISO-8859-1") for kw in ROBOT_KW):
                        print('Robot check!')
                        try :
                            c = Crawler.get_content_with_selenium(url)
                        except Exception as e:
                            print(e)
                            
                    soup = BeautifulSoup(c, 'html.parser', from_encoding='utf-8')
                    
                    divs = soup.findAll("div", {"class" : "gs_or"})
                    
                    for div in divs:
                        try :
                            links=div.find('h3').find('a')['href']
                        except :
                            links="Look manually at: " + url
                            
                        try :
                            title=div.find('h3').find('a').text
                        except:
                            title="Not found title"
                        
                        try:
                            citations=Crawler.get_cities(str(div.format_string))
                        except:
                            warnings.warn("Citation not found")
                            citations=0
                            
                        try :
                            year=Crawler.get_year(div.find('div', class_='gs_a').get_text())
                        except : 
                            warnings.warn("Year not found")
                            year=0

                        try:
                            author=div.find('div', class_='gs_a').get_text()
                        except:
                            warnings.warn("Author not found")
                            author = "Not found"
                        
                        try : 
                            publisher=div.find('div', class_='gs_a').get_text().split("-")[-1]
                        
                        except:
                            warnings.warn("Publisher not found")
                            publisher="Not found"
                            
                        try :
                            venue=div.find('div', class_='gs_a').get_text()[-2].split(",")[-1]
                        except:
                            warnings.warn("Venue not found")
                            venue="Not found"
                        try :
                            abstract = div.find('div', class_='gs_rs')
                        except:
                            warnings.warn("Abstract not found")
                            abstract="Not found"
                        
                        try : 
                            # print(Crawler.get_hindex(div.find('div', class_='gs_a').find_all('a')['href']))
                            res_listauthor = Crawler.get_hindex(div.find('div', class_='gs_a'))
                        except:
                            res_listauthor= []
                        data = {
                            "link_paper" :links,
                            "title" : title,
                            "citations" : citations,
                            "year" : year,
                            "author" : author,
                            "venue" : venue,
                            "publisher" : publisher,
                            "abstract" : abstract.get_text() if abstract else "",
                            "list_author" : res_listauthor
                        }
                        collection.update_one({"query": query_}, {"$push": {"results": data}}, upsert=True)
            
            return "Update sucessfully"
            
        if not isudpate :
            res_check_exist = Crawler.check_exist(textinput)
        if res_check_exist:
            return res_check_exist['results']
        else:
            rank = [0]
            result = []
            for i in range(0, number_of_result, 10):
                
                url = GSCHOLAR_MAIN_URL.format(str(i), textinput.replace(' ', '+'))
                
                page = session.get(url)
                
                c = page.content
            
                if any(kw in c.decode("ISO-8859-1") for kw in ROBOT_KW):
                    print('Robot check!')
                    try :
                        c = Crawler.get_content_with_selenium(url)
                    except Exception as e:
                        print(e)
                        
                soup = BeautifulSoup(c, 'html.parser', from_encoding='utf-8')
                
                divs = soup.findAll("div", {"class" : "gs_or"})
                
                for div in divs:
                    try :
                        links=div.find('h3').find('a')['href']
                    except :
                        links="Look manually at: " + url
                        
                    try :
                        title=div.find('h3').find('a').text
                    except:
                        title="Not found title"
                    
                    try:
                        citations=Crawler.get_cities(str(div.format_string))
                    except:
                        warnings.warn("Citation not found")
                        citations=0
                        
                    try :
                        year=Crawler.get_year(div.find('div', class_='gs_a').get_text())
                    except : 
                        warnings.warn("Year not found")
                        year=0

                    try:
                        author=div.find('div', class_='gs_a').get_text()
                    except:
                        warnings.warn("Author not found")
                        author = "Not found"
                    
                    try : 
                        publisher=div.find('div', class_='gs_a').get_text().split("-")[-1]
                    
                    except:
                        warnings.warn("Publisher not found")
                        publisher="Not found"
                        
                    try :
                        venue=div.find('div', class_='gs_a').get_text()[-2].split(",")[-1]
                    except:
                        warnings.warn("Venue not found")
                        venue="Not found"
                    try :
                        abstract = div.find('div', class_='gs_rs')
                    except:
                        warnings.warn("Abstract not found")
                        abstract="Not found"
                    
                    try : 
                        # print(Crawler.get_hindex(div.find('div', class_='gs_a').find_all('a')['href']))
                        res_listauthor = Crawler.get_hindex(div.find('div', class_='gs_a'))
                    except:
                        res_listauthor= []
                    data = {
                        "link_paper" :links,
                        "title" : title,
                        "citations" : citations,
                        "year" : year,
                        "author" : author,
                        "venue" : venue,
                        "publisher" : publisher,
                        "abstract" : abstract.get_text() if abstract else "",
                        "list_author" : res_listauthor
                    }
                    collection.update_one({"query": textinput}, {"$push": {"results": data}}, upsert=True)
                    result.append(data)
                sleep(0.5)
            return result
        
    

    @staticmethod
    def update_database():
        #get query on database
        list_query = collection.find()
        list_query = [query['query'] for query in list_query]
        Crawler.handlecrawl( number_of_result= 50, isudpate=True, list_update=list_query)
        