from datetime import datetime

import plotly.express as px
import streamlit as st
from src.database import Database
from src.notion_helpers import load_config, load_notion_db, process_notion_db
from src.s3 import S3FileHandler
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.mention import mention

config, authenticator, database_id, client_token = load_config()

if st.session_state.get("authentication_status") is None:
    authenticator.login("Login")
    st.warning("Please enter your username and password")
elif not st.session_state["authentication_status"]:
    authenticator.login("Login")
    st.error("Username/password is incorrect", icon="🚨")
else:
    with st.sidebar:
        authenticator.logout("Logout")

    # Save latest notion data to s3
    with st.sidebar:
        if st.button("Save latest notion data to database"):
            # Load data from Notion database
            full_df = load_notion_db(database_id, client_token)
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            S3FileHandler(bucket_name="fenix-notion-file-dump").upload_df_to_s3(
                full_df, f"notiondata_{timestamp_str}.csv"
            )
            st.write(f"Notion data saved to s3 -> notiondata_{timestamp_str}.csv")

    with Database(db="fenixdatabase") as db:
        df = db.execute_query_to_dataframe("SELECT * FROM notion;")

    # filter out columns not for display
    _, ps = process_notion_db(df)
    ps.filter_columns(config.display_columns)
    ps.sort_columns(config.display_columns)

    # Display data and charts
    st.header("Welcome to Fenix's training app :dog:")
    filtered_df = dataframe_explorer(ps.df, case=False)
    st.dataframe(filtered_df, use_container_width=True)

    mention(
        label="Notion page",
        icon="notion",
        url="https://www.notion.so/adb7c02377da48e6b8ce50dc4dad8739?v=7b1ad8655ff74379bee0817d6b5eb0f6",
    )

    status_dict = config.status

    # Create tabs for different trainers
    with st.sidebar:
        tab_selected = st.radio(
            "Select trainer", ["All", "Kristia, Seth", "Kristia", "Seth"]
        )

    if tab_selected == "All":
        chart_df = filtered_df
    else:
        chart_df = filtered_df[filtered_df.Trainer == tab_selected]

    fig = px.scatter(
        chart_df,
        x="Date",
        y="Duration (min)",
        color="Status",
        color_discrete_map=status_dict,
    )
    fig.update_traces(marker=dict(size=12), selector=dict(mode="markers"))
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
