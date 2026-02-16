import os
import json
import gspread
import pytz
import datetime
import requests 
from bs4 import BeautifulSoup 
from google.oauth2.service_account import Credentials

# 1. Authorize using the GitHub Secret
creds_json = json.loads(os.environ["GCP_CREDS"])
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_json, scopes=scope)
client = gspread.authorize(creds)

# Open google sheet
sheet = client.open("Olympic_Fantasy_Draft_2026").sheet1

def get_medal_data():
    """Pulls live 2026 medal counts from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/2026_Winter_Olympics_medal_table"
    medal_stats = {}
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main medal table
        table = soup.find('table', {'class': 'wikitable'})
        
        # Mapping names to your 3-letter abbreviations
        mapping = {
            "Norway": "NOR", "South Korea": "KOR", "Italy": "ITA", 
            "Netherlands": "NED", "United States": "USA", "Slovenia": "SLO",
            "Germany": "GER", "Austria": "AUT", "France": "FRA",
            "Japan": "JPN", "Canada": "CAN", "Sweden": "SWE"
        }

        for row in table.find_all('tr')[1:]:
            cols = row.find_all(['th', 'td'])
            if len(cols) < 5: continue
            
            # Extract and clean country name
            raw_name = cols[1].text.strip().replace('*', '').split('[')[0].strip()
            
            if raw_name in mapping:
                code = mapping[raw_name]
                medal_stats[code] = {
                    "gold": int(cols[2].text.strip().replace(',', '')),
                    "silver": int(cols[3].text.strip().replace(',', '')),
                    "bronze": int(cols[4].text.strip().replace(',', ''))
                }
        return medal_stats

    except Exception as e:
        print(f"Live Scraper Error: {e}")
        return {}

def update_leaderboard():
    draft = {
        "AF": ["USA", "SLO"],
        "CM": ["NOR", "KOR"],
        "AS & SD": ["ITA", "NED"],
        "KT": ["GER", "AUT"],
        "ZG": ["FRA", "JPN"],
        "JC": ["CAN", "SWE"],
    }
    
    stats = get_medal_data()
    if not stats:
        print("Scraper failed to find data. Check URL or table structure.")
        return

    sheet.clear()

    # Timezone conversion for EST
    utc_now = datetime.datetime.now(pytz.utc)
    est_tz = pytz.timezone('US/Eastern')
    est_now = utc_now.astimezone(est_tz).strftime("%Y-%m-%d %I:%M %p") 

    sheet.append_row([f"Last Updated (LIVE): {est_now} EST"])
    sheet.append_row([]) 
    sheet.append_row(["Rank", "Name", "Total", "Gold", "Silver", "Bronze", "Gold Breakdown", "Silver Breakdown", "Bronze Breakdown"])

    final_list = []
    for name, countries in draft.items():
        g, s, b = 0, 0, 0
        g_details, s_details, b_details = [], [], []
        for c in countries:
            m = stats.get(c, {"gold": 0, "silver": 0, "bronze": 0})
            g += m['gold']; s += m['silver']; b += m['bronze']
            g_details.append(f"{c}: {m['gold']}G")
            s_details.append(f"{c}: {m['silver']}S")
            b_details.append(f"{c}: {m['bronze']}B")
        
        total = g + s + b
        # Fixed the spacing on your join strings here
        final_list.append([name, total, g, s, b, " | ".join(g_details), " | ".join(s_details), " | ".join(b_details)])

    # Sort by total medals descending
    final_list.sort(key=lambda x: x[1], reverse=True)

    for idx, row in enumerate(final_list, start=1):
        sheet.append_row([idx] + row)
    print(f"Leaderboard updated LIVE at {est_now}")

if __name__ == "__main__":
    update_leaderboard()
