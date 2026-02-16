import streamlit as st
import json
from google.oauth2.service_account import Credentials
import gspread

scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# Use st.secrets
creds_json = json.loads(st.secrets["GCP_CREDS"])
creds = Credentials.from_service_account_info(creds_json, scopes=scope)
client = gspread.authorize(creds)


st.set_page_config(
    page_title="Olympic Fantasy Tracker",
    layout="wide"
)

st_autorefresh(interval=300000, key="datarefresh")
st.title("Olympic Fantasy Draft Leaderboard")

# streamlit secret authentification
creds_json = json.loads(os.environ["GCP_CREDS"])
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(creds_json, scopes=scope)
client = gspread.authorize(creds)

# pull data from google sheet
sheet = client.open("Olympic_Fantasy_Draft_2026").sheet1
data = sheet.get_all_records()

df = pd.DataFrame(data)

if df.empty:
    st.warning("No data found.")
else:
    # create toggle for switching between total medlas vs weighted score
    scoring_mode = st.selectbox(
        "Select Ranking Method",
        ["Total Medals", "Weighted Score (3-2-1)"]
    )

    if scoring_mode == "Weighted Score (3-2-1)":
        df = df.sort_values("Score", ascending=False)
    else:
        df = df.sort_values("Total Medals", ascending=False)

    st.dataframe(df, use_container_width=True)

    # Visual
    st.subheader("Medals by Person")
    st.bar_chart(df.set_index("Name")["Total Medals"])

# Autorefresh
st.caption("Auto-refreshes every 5 minutes")
st.experimental_rerun
