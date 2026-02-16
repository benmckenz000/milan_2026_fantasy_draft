import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 1. Authorize using the GitHub Secret
creds_json = json.loads(os.environ["GCP_CREDS"])
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_json, scopes=scope)
client = gspread.authorize(creds)

# 2. Open  specific sheet
sheet = client.open("Olympic_Fantasy_Draft_2026").sheet1

def get_medal_data():
    # Feb 15, 2026 Standings
    return {
        "Norway": {"gold": 12, "silver": 7, "bronze": 8},
        "South Korea": {"gold": 1, "silver": 2, "bronze": 3},
        "Italy": {"gold": 8, "silver": 4, "bronze": 10},
        "Germany": {"gold": 4, "silver": 6, "bronze": 5},
        "USA": {"gold": 5, "silver": 8, "bronze": 4},
        "France": {"gold": 4, "silver": 7, "bronze": 4}
    }

def update_leaderboard():
    # Add your real participants and their picks here!
    draft = {
        "Group 1": ["Norway", "South Korea"],
        "PlaceHolder A": ["Italy", "Germany"],
        "PlaceHolder B": ["USA", "France"]
    }
    
    stats = get_medal_data()
    sheet.clear()
    sheet.append_row(["Rank", "Name", "Total", "Gold", "Silver", "Bronze", "Gold Breakdown", "Silver Breakdown", "Bronze Breakdown"])

    final_list = []
    for name, countries in draft.items():
        g, s, b = 0, 0, 0
        g_details, s_details, b_details = [],[],[]
        for c in countries:
            m = stats.get(c, {"gold": 0, "silver": 0, "bronze": 0})
            g += m['gold']; s += m['silver']; b += m['bronze']
            g_details.append(f"{c}: {m['gold']}G")
            s_details.append(f"{c}: {m['silver']}S")
            b_details.append(f"{c}: {m['bronze']}B")
            
        
        total = g + s + b
        final_list.append([name, total, g, s, b, " | ".join(g_details), "|" .join(s_details), "|" .join(b_details)])

    # Sort by total medals descending
    final_list.sort(key=lambda x: x[1], reverse=True)

    for idx, row in enumerate(final_list, start=1):
        sheet.append_row([idx] + row)
    print("Leaderboard updated")

if __name__ == "__main__":
    update_leaderboard()
