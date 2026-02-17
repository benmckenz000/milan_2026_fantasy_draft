import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from streamlit_autorefresh import st_autorefresh
import datetime
import altair as alt

# Set up page configuration
st.set_page_config(
    page_title="2026 Winter Olympics Fantasy Draft Tracker",
    layout="wide"
)

# set to auto-refresh every 5 minutes
st_autorefresh(interval=300_000, key="datarefresh")  # 300_000 ms = 5 min


# title and subtitle for page
st.title("Olympic Fantasy Draft Leaderboard")
st.markdown("### Benjamin McKenzie")


# authenticate google sheets w/ st.secrets
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

try:
    creds_json = json.loads(st.secrets["GCP_CREDS"])
    creds = Credentials.from_service_account_info(creds_json, scopes=scope)
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"Failed to authenticate Google Sheets: {e}")
    st.stop()

# pull data from google sheet
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
    # show timestamp for last update
    try:
        last_update_cell = sheet.acell('A1').value
        st.markdown(f"{last_update_cell}")
    except:
        st.markdown(f"**Last Checked:** {datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p')}")

    # make toggle for selecting ranking method on dashboard
    scoring_mode = st.selectbox(
        "Select Ranking Method",
        ["Total Medals", "Weighted Score (3-2-1)"]
    )

# make indv dataframes
df_chart_display = df.copy()

if scoring_mode == "Weighted Score (3-2-1)":
    # Create Score column
    df_chart_display["Score"] = (
        df_chart_display["Gold"]*3 +
        df_chart_display["Silver"]*2 +
        df_chart_display["Bronze"]*1
    )

    chart_col = "Score"
    df_chart_display = df_chart_display.sort_values(chart_col, ascending=False)
    df_table_display = df_chart_display.copy()

else:  # Total Medals
    chart_col = "Total Medals"
    df_chart_display = df_chart_display.sort_values(chart_col, ascending=False)

    # Only hide Score in this mode
    if "Score" in df_chart_display.columns:
        df_table_display = df_chart_display.drop(columns=["Score"])
    else:
        df_table_display = df_chart_display.copy()

    # display leaderboard as a table
    st.dataframe(df_table_display, use_container_width=True)

    # Display bar chart - left to right
    st.subheader(f"{chart_col} by Participant")
    df_chart = df_chart_display[["Name", chart_col]].sort_values(chart_col, ascending=False)

    chart = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X("Name", sort=None),
        y=chart_col,
        tooltip=["Name", chart_col]
    )

    st.altair_chart(chart, use_container_width=True)
