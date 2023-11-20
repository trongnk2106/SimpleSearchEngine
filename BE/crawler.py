import requests, os, datetime, argparse
from bs4 import BeautifulSoup
# import matplotlib.pyplot as plt
import pandas as pd
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
    # def __init__(self, textinput, number_of_result , start_year = STARTYEAR, end_year = ENDYEAR):
        
        # self.textinput = textinput
        # self.number_of_result = number_of_result
        # self.start_year = start_year
        # self.end_year = end_year
        
        # self.links = []
        # self.title = []
        # self.citations = []
        # self.year = []
        # self.author = []
        # self.venue = []
        # self.publisher = []
        # self.rank = [0]
        
    
    @staticmethod
    def get_args():
       
        return Crawler.textinput, Crawler.number_of_result, Crawler.start_year, Crawler.end_year
        # return keyword, number_of_result , path, start_year, end_year
        


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

    def get_cities(self, content : str) -> int:
        out = 0
        for char in range(0, len(content)):
            if content[char: char +9 ] == "Cited by ":
                init = char + 9
                for end in range(init+1, init + 6):
                    if content[end] == '<':
                        break
                out = content[init:end]
        return int(out)

    def get_year(self, content:str) -> int:
        for char in range(0, len(content)):
            if content[char] == "-":
                out = content[char-5: char-1]
            
        if not out.isdigit():
            out = 0
        return int(out)

    def get_article_content(self, url):
        # Gửi yêu cầu HTTP để truy cập trang chi tiết của từng kết quả
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        # response = requests.get(url)
        try :
            
            if response.status_code == 200:
                article_soup = BeautifulSoup(response.text, 'html.parser')

                # Ví dụ: In nội dung của trang chi tiết
                article_content = article_soup.find('div', class_='c-article-body')  
                # print(f:\n{article_content.get_text() if article_content else 'N/A'}")
            # else:
            #     print(f"Không thể truy cập trang chi tiết. Mã trạng thái: {response.status_code}")

        except Exception as e:
            print(e)
            print("Error when get article content")
            return None

    @staticmethod
    def handlecrawl(textinput, number_of_result , start_year = STARTYEAR, end_year = ENDYEAR):
        
        # textinput, number_of_result , start_year, end_year

        if start_year :
            GSCHOLAR_MAIN_URL = GSCHOLAR_URL + STARTYEAR_URL.format(start_year)
        else :
            GSCHOLAR_MAIN_URL = GSCHOLAR_URL
        
        if end_year != now.year:
            GSCHOLAR_MAIN_URL = GSCHOLAR_URL + ENDYEAR_URL.format(end_year)
        
        session = requests.Session()
        
        
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
                    year=Crawler.get_year(div.find(div, {"class" : "gs_a"}).text)
                except : 
                    warnings.warn("Year not found")
                    year=0

                try:
                    author=div.find(div, {"class" : "gs_a"}).text
                except:
                    warnings.warn("Author not found")
                    author = "Not found"
                
                try : 
                    publisher=div.find(div, {"class" : "gs_a"}).text.split("-")[-1]
                
                except:
                    warnings.warn("Publisher not found")
                    publisher="Not found"
                    
                try :
                    venue=div.find(div, {"class" : "gs_a"}).text.split("-")[-2].split(",")[-1]
                except:
                    warnings.warn("Venue not found")
                    venue="Not found"
                try :
                    abstract = div.find('div', class_='gs_rs')
                except:
                    warnings.warn("Abstract not found")
                    abstract="Not found"
                
                data = {
                    "link" :links,
                    "title" : title,
                    "citations" : citations,
                    "year" : year,
                    "author" : author,
                    "venue" : venue,
                    "publisher" : publisher,
                    "abstract" : abstract.get_text() if abstract else ""
                    
                }
            collection.update_one({"query": textinput}, {"$push": {"results": data}}, upsert=True)
            result.append(data)
            sleep(0.5)
        return result


