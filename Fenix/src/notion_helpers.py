import streamlit as st
from src.authenticate import Authenticate
from src.config import Config
from src.features import ProcessDataFrame
from src.notion_import import NotionClient, PandasConverter, PandasLoader
from src.users import Users


@st.cache_resource
def load_config():
    config = Config().get_final_config()
    authenticator = Authenticate(credentials=Users.get_user_list())
    _database_id = config.aws.notion_client.NOTION_DATABASE_ID
    client_token = config.aws.notion_client.NOTION_CLIENT_TOKEN
    return config, authenticator, _database_id, client_token


@st.cache_data
def load_notion_db(_database_id, client_token):
    client = NotionClient(client_token)
    converter = PandasConverter()
    loader = PandasLoader(client, converter)
    df = loader.load_db(_database_id)
    return df


@st.cache_data
def process_notion_db(df):
    ps = ProcessDataFrame(df)
    full_df = ps.process_dataframe()
    return full_df, ps
