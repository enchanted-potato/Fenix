import pandas as pd
import plotly.express as px
import streamlit as st
from src.features import ProcessDataFrame
from src.notion_import import NotionClient, PandasConverter, PandasLoader
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.mention import mention

pd.set_option("display.max_columns", 24)

database_id = "adb7c02377da48e6b8ce50dc4dad8739"
client = NotionClient("secret_NWpuizQRvbX2embEawThKZd9bw7uaXypUqoaebH6fgC")
converter = PandasConverter()
loader = PandasLoader(client, converter)
df = loader.load_db(database_id)

ps = ProcessDataFrame(df)
df = ps.process_dataframe()

st.header("Welcome to Fenix's training app :dog:")

filtered_df = dataframe_explorer(df, case=False)
st.dataframe(filtered_df, use_container_width=True)

mention(
    label="Notion page",
    icon="notion",  # Notion is also featured!
    url="https://www.notion.so/adb7c02377da48e6b8ce50dc4dad8739?v=7b1ad8655ff74379bee0817d6b5eb0f6",
)

status_dict = {"Aced it": "green", "Okay": "blue", "Struggled": "red"}

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
