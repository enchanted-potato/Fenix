import numpy as np
import altair as alt
import pandas as pd
import streamlit as st
import plotly.express as px
# from notion_client import Client

from src.notion_import import NotionClient, PandasLoader, PandasConverter
from src.features import ProcessDataFrame

pd.set_option('display.max_columns', 24)

database_id = "adb7c02377da48e6b8ce50dc4dad8739"
client = NotionClient("secret_NWpuizQRvbX2embEawThKZd9bw7uaXypUqoaebH6fgC")
converter = PandasConverter()
loader = PandasLoader(client, converter)
df = loader.load_db(database_id)

ps = ProcessDataFrame(df)
df = ps.process_dataframe()

st.header('Welcome to Fenix\'s training app :dog:')

filter_value = st.selectbox('Select a filter value', list(df['Status'].unique()) + ["No filter"], index=3)

if filter_value!= "No filter":
    filtered_data = df[df['Status'] == filter_value]
else:
    filtered_data = df

# display the filtered data
st.write(filtered_data)

status_dict = {
    "Aced it": "green",
    "Okay": "blue",
    "Struggled": "red"
}

fig = px.scatter(df,
                  x="Date",
                  y="Duration (min)",
                  color="Status",
                 color_discrete_map=status_dict,
                 # text="Trazadone"
                 )
fig.update_traces(marker=dict(size=12),
                  selector=dict(mode='markers'))

tab1, tab2, tab3 = st.tabs(["K & S", "Kristia", "Seth"])
with tab1:
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
with tab2:
    # Use the native Plotly theme.
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
with tab3:
    # Use the native Plotly theme.
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
