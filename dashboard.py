import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from streamlit_autorefresh import st_autorefresh
import datetime

# -------------------
# Page Config
# -------------------
st.set_page_config(
    page_title="Olympic Fantasy Draft Tracker",
    layout="wide"
)

# -------------------
# Auto-refresh every 5 minutes
# -------------------
st_autorefresh(interval=300_000, key="datarefresh")  # 300_000 ms = 5 min

st.title("Olympic Fantasy Draft Leaderboard")

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
    st.error(f"Failed to authenticate Google Sheets: {e}")
    st.stop()

# -------------------
# Fetch Data from Google Sheet
# -------------------
try:
    sheet = client.open("Olympic_Fantasy_Draft_2026").sheet1
    data = sheet.get_all_records(head = 2)
except Exception as e:
    st.error(f"Failed to fetch data from Google Sheet: {e}")
    st.stop()

df = pd.DataFrame(data)

if df.empty:
    st.warning("No data found in the Google Sheet.")
else:
    # -------------------
    # Display Last Updated Timestamp
    # -------------------
    try:
        last_update_cell = sheet.acell('A1').value
        st.markdown(f"** {last_update_cell}**")
    except:
        st.markdown(f"**Last Checked:** {datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p')}")

    # -------------------
    # Select Ranking Method
    # -------------------
    scoring_mode = st.selectbox(
    "Select Ranking Method",
    ["Total Medals", "Weighted Score (3-2-1)"]
)

    # Compute weighted score if needed
    if scoring_mode == "Weighted Score (3-2-1)":
        if "Score" not in df.columns:
            df["Score"] = df["Gold"]*3 + df["Silver"]*2 + df["Bronze"]*1
        df_display = df.sort_values("Score", ascending=False)
        chart_col = "Score"
    else:
        df_display = df.sort_values("Total Medals", ascending=False)
        chart_col = "Total Medals"

# -------------------
# Display Leaderboard Table
# -------------------
    st.dataframe(df_display, use_container_width=True)

# -------------------
# Display Bar Chart dynamically
# -------------------
    st.subheader(f"{chart_col} by Player")
    df_chart = df_display.set_index("Name")  # already sorted descending
    st.bar_chart(df_chart[chart_col])
