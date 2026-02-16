# 2026 Winter Olympics: Automated Fantasy Leaderboard
**An end-to-end data pipeline that pulls live medal standings for the 2026 Winter Olympics and updates a real-time leaderboard in Google Sheets**


## Overview
This project automates the scoring and reporting for a 2026 Winter Olympics Fantasy Draft. This pipeline scrapes the real-time medal standings from Wikipedia, calculates each participant's total medal count across their two countries, ranks the leaderboard, and pushes the results to a live Google Sheet every hour.


## Project Architecture (ETL)
This project follows a classic **ETL** pattern:

1.  **Extract:** Uses `BeautifulSoup4` and `requests` to scrape live medal tables from Wikipedia. The script is designed to navigate HTML structures and identify relevant data rows while filtering out noise (headers, summary rows, and footnotes).
2.  **Transform:** * **Data Cleaning:** Raw country names are normalized and mapped to official 3-letter IOC abbreviations (e.g., "Norway" - "NOR").
    * **Aggregation:** Data is mapped to participant draft picks to calculate real-time totals, including granular breakdowns of Gold, Silver, and Bronze counts.
    * **Ranking:** Implements a sorting algorithm to rank the leaderboard in descending order based on total medal count.
3.  **Load:** Leverages the `gspread` library and **Google Cloud Service** to push cleaned data into the Google Sheets API.


## Stack & Skills
* **Language:** Python 3.14.3
* **Libraries:** `BeautifulSoup4`, `gspread`, `pytz`, `requests`
* **Automation:** Deployed via **GitHub Actions** using `cron` scheduling for hourly updates.
* **Security:** Manages Google Cloud credentials using **GitHub Secrets** to ensure environment variables aren't visible in the source code.
* **DevOps:** Includes robust error handling (`try-except` blocks) to ensure pipeline stability during network timeouts or source data fluctuations.



