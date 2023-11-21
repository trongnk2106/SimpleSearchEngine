# SimpleSearchEngine# Google Scholar Crawler and Author Ranking

## Introduction
This application utilizes FastAPI for the backend, Streamlit for the frontend, and MongoDB for data storage. It provides the capability to search and rank authors based on their publications from Google Scholar.

## Demo:
[youtube](https://youtu.be/AWdssumpBrw) 

## Installation
1. Git clone this repository:
   ```
   git clone https://github.com/trongnk2106/SimpleSearchEngine.git
   ```
2. Docker Compose :
   ```
   docker compose up
   ```

## Backend (FastAPI)
- Module `crawler`: Contains functions essential for scraping data from Google Scholar using BeautifulSoup and storing it into MongoDB.
- Module `ranking`: Implements the ranking of authors based on a content-based algorithm with TF-IDF.

## Frontend (Streamlit)
- Module `frontend`: User interface using Streamlit for searching and viewing the ranking of authors.

## MongoDB
- Data from Google Scholar is stored in a collection within MongoDB.

## Usage
1. Run the application and access it through the browser at `http://localhost:8501`.
2. Use the interface to perform searches and view the ranking of authors.
3. Results will be displayed on the user interface.

## Data Updates
- Data can be updated on demand or can be set to update automatically using scheduling tools, such as cron jobs on a Linux operating system or Windows.

## Technical 
- Fastapi
- BeautifulSoup
- streamlit
- TF-IDF
- docker 

## Author
- Author's Trong
- Contact: trongntt2002@gmail.com

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
