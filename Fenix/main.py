import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from src.database import Database
from src.notion_helpers import load_config, load_notion_db, process_notion_db
from src.s3 import S3FileHandler
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.mention import mention

os.environ["AWS_PROFILE"] = "enchanted-potato"
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
    st.header("Welcome to Fenix's training Fenix :dog:")
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

# # query the database and get the max date
# def get_max_db_date(db, table):
#     with Database(db=db) as db:
#         return db.execute_query(f"SELECT MAX(Datetime) FROM {table};")[0][0]
#
# # get the latest s3 file
# from src.s3 import S3FileHandler
# s3_handler = S3FileHandler("fenix-notion-file-dump")
# df = s3_handler.load_csv_from_s3("notiondata_2023-05-06 10:18:54.csv")
# # filter the rows greater than the max date
# def filter_df(df, date):
#     return df[df.Datetime>date]
# # insert the rows into the table
# with Database(db="fenixdatabase") as db:
#     db.insert_df_to_table(df, "notion")
#
# # get the latest s3 file
# import os
# from src.database import Database
# import pandas as pd
# os.environ['AWS_PROFILE'] = 'enchanted-potato'
#
# s3_handler.list_files()
# df = s3_handler.load_csv_from_s3("notiondata_2023-05-06 10:18:54.csv")
#
# # create a table in mysql
# df = df[df.Datetime>"2023-04-20"]
# df.Datetime.max()
# import numpy as np
#
# # insert the data into mysql
# with Database(db="fenixdatabase") as db:
#     print(db.list_databases())
#
#     db.create_table("notion",
#                     {
#                         "Datetime": "VARCHAR(255)",
#                         "Duration": "VARCHAR(255)",
#                         "Status": "VARCHAR(255)",
#                         "Trainer": "VARCHAR(255)",
#                         "Tired": "VARCHAR(255)",
#                         "Weather": "VARCHAR(255)",
#                         "Trazadone": "VARCHAR(255)",
#                         "Recording": "VARCHAR(255)",
#                     }
#                 )
#     db.insert_df_to_table(df, "notion")
#     r = pd.DataFrame(db.execute_query("SELECT * FROM notion;"))
#     dataframe = pd.DataFrame(r, columns=[t[0] for t in r])
#
# #1. Click save data to database from web app
# #2. Read data from notion in the app, process it and load to s3
# #3. Lambda function triggered and read data from s3 and insert into mysql
# #3. Read data from mysql in the web app
#
# import pymysql
# from src.config import Config
# config = Config().get_final_config()
# conn = pymysql.connect(
# 		host=config.aws.fenix_mysql.host,
# 		user=config.aws.fenix_mysql.username,
# 		password=config.aws.fenix_mysql.password,
#         db = "fenixdatabase",
# 	)
#
# with conn.cursor() as cur:
#     fields = list(df)
#     insert_stmt = '''INSERT INTO {table} ({cols}) VALUES ({placeholders})'''.format(
#         table="notion",
#         cols=','.join(fields),
#         placeholders=','.join(['%s'] * len(fields)),
#     )
#     df = df.replace(r'^\s*$', pd.np.nan, regex=True)
#     df = df.where((pd.notnull(df)), None)
#     print(df.head())
#     values = [tuple(x) for x in df[fields].values]
#     print("Inserting with {} rows into {}..".format(len(df), "notion"))
#     cur.executemany(query=insert_stmt, args=values)
#     conn.commit()
#
#
# query = "SELECT * FROM notion;"
# with conn.cursor() as cursor:
#     cursor.execute(query)
#     result = cursor.fetchall()
#     print([row[0] for row in result])
#
# df = pd.read_sql("SELECT * FROM notion;", conn)
#
#
#
#
# fields = list(df)
# if sorted(fields) != sorted(db_cols):
#     print(list(df), db_cols, sep="\n")
#     raise ValueError("DataFrame column names don't match")
#
# update = duplicates.lower().strip() == 'update'
# insert_stmt = '''INSERT{ignore} INTO {table} ({cols}) VALUES ({placeholders})'''.format(
#     table=table,
#     cols=','.join(fields),
#     placeholders=','.join(['%s'] * len(fields)),
#     ignore=' IGNORE' if not update else ''
# )
#
# if update:
#     update_string = ', '.join(['{f}=VALUES({f})'.format(f=f) for f in fields])
#     duplicates_postfix = ''' ON DUPLICATE KEY UPDATE {update_string}'''.format(update_string=update_string)
#     insert_stmt += duplicates_postfix
#
# # print(insert_stmt)
# df = df.replace(r'^\s*$', pd.np.nan, regex=True)
# df = df.where((pd.notnull(df)), None)
# print(df.head())
# values = [tuple(x) for x in df[fields].values]
# print("Inserting with '{}' {} rows into {}..".format(duplicates, len(df), table))
# cur.executemany(sql=insert_stmt, args=values)
#
# duplicates='update'
# update = duplicates.lower().strip()=='update'
#
# def insert_pandas(self, df, table, duplicates='update'):
#     with self.connection.cursor() as cursor:
#         cursor.execute('''select column_name from INFORMATION_SCHEMA.COLUMNS
#             where concat(table_schema, ".", table_name) = "{}"'''.format(table))
#         db_cols = [c[0] for c in cursor.fetchall()]
#         print(db_cols)
#
#         fields = list(df)
#         if sorted(fields) != sorted(db_cols):
#             print(list(df), db_cols, sep="\n")
#             raise ValueError("DataFrame column names don't match")
#
#         update = duplicates.lower().strip() == 'update'
#         insert_stmt = '''INSERT{ignore} INTO {table} ({cols}) VALUES ({placeholders})'''.format(
#             table=table,
#             cols=','.join(fields),
#             placeholders=','.join(['%s'] * len(fields)),
#             ignore=' IGNORE' if not update else ''
#         )
#
#         if update:
#             update_string = ', '.join(['{f}=VALUES({f})'.format(f=f) for f in fields])
#             duplicates_postfix = ''' ON DUPLICATE KEY UPDATE {update_string}'''.format(update_string=update_string)
#             insert_stmt += duplicates_postfix
#
#         # print(insert_stmt)
#         df = df.replace(r'^\s*$', pd.np.nan, regex=True)
#         df = df.where((pd.notnull(df)), None)
#         print(df.head())
#         values = [tuple(x) for x in df[fields].values]
#         print("Inserting with '{}' {} rows into {}..".format(duplicates, len(df), table))
#         cursor.executemany(sql=insert_stmt, args=values)
