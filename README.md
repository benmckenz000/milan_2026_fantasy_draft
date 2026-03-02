# 2026 Winter Olympics: Automated Fantasy Leaderboard

[View Live Leaderboard](https://milan2026fantasydraft-fzhufa7m5slxf7qfspmahk.streamlit.app/)

An ETL workflow that pulls live medal standings for the 2026 Winter Olympics, calculates fantasy scores and updates a Google Sheets leaderboard with a Streamlit dashboard for visualization.

## Overview

This project automates scoring for a Winter Olympics fantasy draft. Medal standings are scraped from Wikipedia, cleaned and matched to drafted countries, ranked under different scoring rules, and pushed to a shared Google Sheet.

A Streamlit app reads from the sheet and displays a live leaderboard that refreshes automatically. 

Once deployed, the system runs on a schedule without manual updates.

## Project Architecture 

### 1. Extract
- Uses `BeautifulSoup4` and `requests` to scrape the live medal table from Wikipedia.
- The parser isolates country rows and excludes headers and summary rows.
- Basic safeguards handle potential small changes in table structure. 
### 2. Transform
- Country names are standardized and mapped to IOC abbreviations.
- Medal counts are merged with participant draft picks.
- Two scoring methods:
  - Total Medals
  - Weighted Score (3-2-1)
- The leaderboard is sorted based on the selected scoring method.
- A timestamp is added to show the last successful update.

### 3. Load
- Authenticates using a Google Cloud service account.
- Writes results to Google Sheets via `gspread`.
- Credentials are stored securely using GitHub Secrets.
- Scheduled hourly with GitHub Actions (`cron`).
- Timezone automatically converts from UTC to EST.

## Streamlit Dashboard

The Streamlit app serves as the visualization layer:

- Authenticates to Google Sheets using `st.secrets`
- Auto-refreshes every 5 minutes
- Allows users to toggle between Total Medals and Weighted Score
- Displays:
  - An interactive leaderboard table
  - A bar chart built with Altair
- Includes error handling for authentication and data retrieval failures

The scraping script, scheduled job, and dashboard are separated, keeping data collection and visualization independent.

## Tech Stack

- Python 3.13  
- pandas  
- requests / BeautifulSoup4  
- gspread (Google Sheets API)  
- Streamlit + Altair  
- GitHub Actions (scheduled automation)

## Future Improvements

- Improve Streamlit column display logic so the Weighted Score column only appears on the weighted scoring view, while the total medals view shows medal breakdowns only.
- Add tie-breaking rules based on gold medal counts.
- Containerize for easier deployment.

---





