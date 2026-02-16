import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from streamlit_autorefresh import st_autorefresh
import datetime

# -------------------
# Streamlit Page Config
# -------------------
st.set_page_config(
    page_title="Olympic Fantasy Draft Tracker",
    page_icon="🥇",
    layout="wide"
)

# -------------------
# Auto-refresh every 5 minutes
# -------------------
st_autorefresh(interval=300000, key="datarefresh")

# -------------------
# Title
# -------------------
st.title("🥇 Olympic Fantasy Draft Leaderboard")

# -------------------
# Google Sheets Authentication via st.secrets
# -------------------
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

try:
    creds_json = json.loads(st.secrets["GCP_CREDS"])
    creds = Credentials.from_service_account_info(creds_json, scopes=scope)
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"Google Sheets Authentication Failed: {e}")
    st.stop()

# -------------------
# Pull Data from Sheet
# -------------------
try:
    sheet = client.open("Olympic_Fantasy_Draft_2026").sheet1
    data = sheet.get_all_records()
except Exception as e:
    st.error(f"Failed to fetch data from Google Sheet: {e}")
    st.stop()

df = pd.DataFrame(data)

if df.empty:
    st.warning("No data found in Google Sheet.")
else:
    # -------------------
    # Last Updated Timestamp
    # -------------------
    # Assume first row in sheet is last updated, if you include a timestamp
    try:
        last_update_cell = sheet.acell('A1').value
        st.markdown(f"**Last Updated:** {last_update_cell}")
    except:
        # fallback to current time
        st.markdown(f"**Last Checked:** {datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p')}")
    
    # -------------------
    # Toggle: Total Medals vs Weighted Score
    # -------------------
    scoring_mode = st.selectbox(
        "Select Ranking Method",
        ["Total Medals", "Weighted Score (3-2-1)"]
    )

    if scoring_mode == "Weighted Score (3-2-1)":
        if "Score" not in df.columns:
            # Calculate weighted score if missing
            df["Score"] = df["Gold"]*3 + df["Silver"]*2 + df["Bronze"]*1
        df = df.sort_values("Score", ascending=False)
    else:
        df = df.sort_values("Total Medals", ascending=False)

    # -------------------
    # Display Table
    # -------------------
    st.dataframe(df, use_container_width=True)

    # -------------------
    # Visual: Bar chart
    # -------------------
    st.subheader("Total Medals by Person")
    st.bar_chart(df.set_index("Name")["Total Medals"])
