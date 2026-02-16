import os
import json
import gspread
import pytz
import datetime
import requests 
from bs4 import BeautifulSoup 
from google.oauth2.service_account import Credentials

# log in with github secret key (for safety)
creds_json = json.loads(os.environ["GCP_CREDS"])
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_json, scopes=scope)
client = gspread.authorize(creds)

# Open google sheet
sheet = client.open("Olympic_Fantasy_Draft_2026").sheet1

def get_medal_data():
    url = "https://en.wikipedia.org/wiki/2026_Winter_Olympics_medal_table" # live data from wikipedia
    medal_stats = {}
    
    try:
        # asks wiki for page data 
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # grabs big main table on page
        table = soup.find('table', {'class': 'wikitable'})
        
        # convert country names to abbreviations for spreasheet cleanliness
        mapping = {
            "Norway": "NOR", "South Korea": "KOR", "Italy": "ITA", 
            "Netherlands": "NED", "United States": "USA", "Slovenia": "SLO",
            "Germany": "GER", "Austria": "AUT", "France": "FRA",
            "Japan": "JPN", "Canada": "CAN", "Sweden": "SWE", "Switzerland": "SUI", 
            "China": "CHN",
        }

        for row in table.find_all('tr')[1:]: # loop and grab every row but slice and skip row 1 at index 0
            cols = row.find_all(['th', 'td']) # grab all cells 
            if len(cols) < 5: continue # if row too short, skip 
            
            # clean up country name - get rid of stars and footnotes
            raw_name = cols[1].text.strip().replace('*', '').split('[')[0].strip()
            
            if raw_name in mapping: # if country in draft, save numbers
                code = mapping[raw_name]
                medal_stats[code] = {
                    "gold": int(cols[2].text.strip().replace(',', '')),
                    "silver": int(cols[3].text.strip().replace(',', '')),
                    "bronze": int(cols[4].text.strip().replace(',', ''))
                }
        return medal_stats

    except Exception as e: # if anything goes wrong with scrape
        print(f"Live Scraper Error: {e}") # print error 
        return {} # return empty data so code doesn't crash

def update_leaderboard(): #assigning countries to each person
    draft = {
        "AF": ["USA", "SLO"],
        "CM": ["NOR", "KOR"],
        "AS & SD": ["ITA", "NED"],
        "SD": ["SUI", "CHN"],
        "KT": ["GER", "AUT"],
        "ZG": ["FRA", "JPN"],
        "JC": ["CAN", "SWE"],
    }
    
    stats = get_medal_data() # pull live numbers 
    if not stats:
        print("Scraper failed to find data. Check URL or table structure.")
        return
    sheet.clear() # clear sheet for fresh numbers

    # Convert from UTC to EST
    utc_now = datetime.datetime.now(pytz.utc)
    est_tz = pytz.timezone("US/Eastern") 
    est_now = utc_now.astimezone(est_tz).strftime("%m/%d/%Y %I:%M %p")

    # add timestamp and column headers
    sheet.append_row([f"Last Updated: {est_now} EST"])
    sheet.append_row([]) 
    sheet.append_row(["Rank", "Name", "Total", "Gold", "Silver", "Bronze", "Gold Breakdown", "Silver Breakdown", "Bronze Breakdown"])

    final_list = [] # empty list holds final total scores
    for name, countries in draft.items(): # loop through each person in draft
        g, s, b = 0, 0, 0 # start count at 0 for each person
        g_details, s_details, b_details = [], [], [] # lists for holding country by country breakdown
        for c in countries: # check each country person picked
            m = stats.get(c, {"gold": 0, "silver": 0, "bronze": 0}) # get medals for country (0 if none)
            g += m['gold']; s += m['silver']; b += m['bronze'] # add medals to persons total
            g_details.append(f"{c}: {m['gold']}G") # creates breakdown style eg USA: 5G
            s_details.append(f"{c}: {m['silver']}S")
            b_details.append(f"{c}: {m['bronze']}B")

        total = g + s + b # add total medals per person
        # bundle everything into one list representing row on sheet. 
        final_list.append([name, total, g, s, b, " | ".join(g_details), " | ".join(s_details), " | ".join(b_details)]) # puts columns in order

    # Sort by total medals descending order
    final_list.sort(key=lambda x: x[1], reverse=True)

    # push each group to google sheet
    for idx, row in enumerate(final_list, start=1):
        sheet.append_row([idx] + row)
    print(f"Leaderboard updated LIVE at {est_now}")

if __name__ == "__main__": # Run
    update_leaderboard()
