# 2026 Winter Olympics: Automated Fantasy Leaderboard
A fully automated system that tracks live medal standings for the 2026 Winter Olympics and updates a fantasy draft leaderboard in Google Sheets with a Streamlit dashboard for viewing results.


## Overview
This project was built to automate the scoring for a Winter Olympics fantasy draft. Instead of manually updating medal counts, this pipeline scrapes the live medal standings from Wikipedia, aggregates totals for each participant's two drafted countries, ranks the results, and updates a shared Google Sheet every hour.
The goal was to build something simple, reliable, and hands-off once deployed.


## Project Architecture 

1.  **Extract:**
   Uses `BeautifulSoup4` and `requests` to pull and parse the live medal tables from Wikipedia. The script handles irregular table formatting and filters out non-data rows like headers and summary totals.
2.  **Transform:**
    * **Cleaning:** Country names are standardized and mapped to official 3-letter IOC abbreviations (e.g., "Norway" - "NOR") to ensure consistent joins.
    * **Aggregation:** Medal counts are matched to each participant's drafted countries and totaled, with a breakdown of Gold, Silver, and Bronze medals.
    * **Ranking:** The leaderboard is sorted in descending order based on total medal count, with medal type breakdown included for transparency. 
4.  **Load:** The processed results are pushed to Google Sheets using the `gspread` library and Google Cloud Service. 

## Stack & Skills
* **Language:** Python 3.14.3
* **Libraries:** `BeautifulSoup4`, `gspread`, `pytz`, `requests`
* **Automation:** Scheduled hourly runs Deployed via GitHub Actions ( `cron`)
* **Security:** Google Cloud credentials stored securely with GitHub Secrets.
* **Reliability:** Error handling inluded to manage network failures or changes in structure of source table.



