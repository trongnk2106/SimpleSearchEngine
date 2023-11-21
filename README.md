# SimpleSearchEngine# Google Scholar Crawler and Author Ranking

## Introduction
This application utilizes FastAPI for the backend, Streamlit for the frontend, and MongoDB for data storage. It provides the capability to search and rank authors based on their publications from Google Scholar.

## Installation
1. Install the necessary Python libraries by running the command:
    ```bash
    pip install -r requirements.txt
    ```
2. Run the FastAPI backend:
    ```bash
    uvicorn main:app --reload
    ```
3. Run the Streamlit frontend:
    ```bash
    streamlit run frontend.py
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
- Data can be updated on demand or can be set to update automatically using scheduling tools, such as cron jobs on a Linux operating system.

## Requirements
- Python 3.8 and above
- MongoDB
- Libraries listed in `requirements.txt`

## Author
- Author's Name
- Contact: email@example.com

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
