# milan_2026_fantasy_draft
Olympic Fantasy Draft - Live Medal Tracker
An automated leaderboard that pulls live medal data from the 2026 Winter Olympics and updates a shared Google Sheet every hour.

Overview
Six players each drafted two countries ahead of the 2026 Milan-Cortina Winter Olympics. This pipeline scrapes the real-time medal standings from Wikipedia, calculates each player's total medal count across their two countries, ranks the leaderboard, and pushes the results to a live Google Sheet.
Live leaderboard updates automatically every hour during the Games.

Workflow
1 - Scrape: requests and BeautifulSoup pulls current medal table from Wikipedia's 2026 Winter Olympics page
2 - Parse: Country names cleaned and assigned 3-letter IOC abbreviations. Gold, silver, and bronze counts pulled for each country
3 - Score: Each player's medal totals summed and ranked in descending order 
4 - Export: gspread clears and rewrites Google Sheet with updated rankings, medal breakdown per country, and a timestamp
