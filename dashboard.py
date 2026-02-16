import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from streamlit_autorefresh import st_autorefresh
import datetime
import altair as alt

# -------------------
# Page Config
# -------------------
st.set_page_config(
    page_title="2026 Winter Olympics Fantasy Draft Tracker",
    layout="wide"
)

# -------------------
# Auto-refresh every 5 minutes
# -------------------
st_autorefresh(interval=300_000, key="datarefresh")  # 300_000 ms = 5 min

st.title("Olympic Fantasy Draft Leaderboard")
st.markdown("# Benjamin McKenzie")

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
    data = sheet.get_all_records(head=2)
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
        st.markdown(f"**Last Updated:** {last_update_cell}")
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
    df_table = df_display.copy()  # table shows all columns
else:  # Total Medals mode
    df_display = df.sort_values("Total Medals", ascending=False)
    chart_col = "Total Medals"
    # For table, drop the Score column if it exists
    df_table = df_display.drop(columns=["Score"]) if "Score" in df_display.columns else df_display.copy()

# Display table using df_table
    st.dataframe(df_table, use_container_width=True)

# -------------------
# Bar chart uses df_display so Score still works for Weighted Score mode
    st.subheader(f"{chart_col} by Participant")
    df_chart = df_display[["Name", chart_col]].sort_values(chart_col, ascending=False)

    chart = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X("Name", sort=None),
        y=chart_col,
        tooltip=["Name", chart_col]
)

    st.altair_chart(chart, use_container_width=True)


    # -------------------
    # Display Leaderboard Table
    # -------------------
    st.dataframe(df_display, use_container_width=True)

    # -------------------
    # Display Bar Chart dynamically (left→right descending)
    # -------------------
    st.subheader(f"{chart_col} by Person")
    df_chart = df_display[["Name", chart_col]].sort_values(chart_col, ascending=False)

    chart = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X("Name", sort=None),  # preserve descending order from DataFrame
        y=chart_col,
        tooltip=["Name", chart_col]
    )

    st.altair_chart(chart, use_container_width=True)
