import pandas as pd
import plotly.express as px
import streamlit as st
from src.features import ProcessDataFrame
from src.notion_import import NotionClient, PandasConverter, PandasLoader
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.mention import mention

from src.config import Config


config = Config()
config = config.get_final_config()

st.header("Welcome to Fenix's training app :dog:")

if st.button("Refresh data"):
    database_id = config.aws.secrets.NOTION_DATABASE_ID
    client = NotionClient(config.aws.secrets.NOTION_CLIENT_TOKEN)
    converter = PandasConverter()
    loader = PandasLoader(client, converter)
    df = loader.load_db(database_id)
    ps = ProcessDataFrame(df)
    df = ps.process_dataframe()

    filtered_df = dataframe_explorer(df, case=False)
    st.dataframe(filtered_df, use_container_width=True)

    mention(
        label="Notion page",
        icon="notion",
        url="https://www.notion.so/adb7c02377da48e6b8ce50dc4dad8739?v=7b1ad8655ff74379bee0817d6b5eb0f6",
    )

    status_dict = config.status

    tab1, tab2, tab3 = st.tabs(["K & S", "Kristia", "Seth"])
    with tab1:
        fig = px.scatter(
            filtered_df[filtered_df.Trainer == "Kristia, Seth"],
            x="Date",
            y="Duration (min)",
            color="Status",
            color_discrete_map=status_dict,
        )
        fig.update_traces(marker=dict(size=12), selector=dict(mode="markers"))
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    with tab2:
        fig = px.scatter(
            filtered_df[filtered_df.Trainer == "Kristia"],
            x="Date",
            y="Duration (min)",
            color="Status",
            color_discrete_map=status_dict,
        )
        fig.update_traces(marker=dict(size=12), selector=dict(mode="markers"))
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    with tab3:
        fig = px.scatter(
            filtered_df[filtered_df.Trainer == "Seth"],
            x="Date",
            y="Duration (min)",
            color="Status",
            color_discrete_map=status_dict,
        )
        fig.update_traces(marker=dict(size=12), selector=dict(mode="markers"))
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
