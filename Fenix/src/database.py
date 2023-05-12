import numpy as np
import pandas as pd
import pymysql
from src.config import Config


class Database:
    """
    Database class to connect to a MySQL database and execute queries.

    Example
    -------
    with Database() as db:
        db.list_tables()
        db.list_databases()
    """

    def __init__(
        self, host: str = None, user: str = None, password: str = None, db: str = None
    ):
        config = Config().get_final_config()
        self.host = host or config.aws.fenix_mysql.host
        self.user = user or config.aws.fenix_mysql.username
        self.password = password or config.aws.fenix_mysql.password
        self.db = db

    def __enter__(self):
        self.connection = pymysql.connect(
            host=self.host, user=self.user, password=self.password, db=self.db
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: dict = None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
            self.connection.commit()
            return result
        except Exception as e:
            print(f"Error executing query {query}: {e}")
            self.connection.rollback()
            return None

    def execute_query_to_dataframe(self, query: str, params: dict = None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                df = pd.read_sql(query, self.connection)
            self.connection.commit()
            return df
        except Exception as e:
            print(f"Error executing query {query}: {e}")
            self.connection.rollback()
            return None

    def list_databases(self):
        query = "SHOW DATABASES"
        result = self.execute_query(query)
        return [row[0] for row in result]

    def list_tables(self):
        query = "SHOW TABLES"
        result = self.execute_query(query)
        try:
            return [row[0] for row in result]
        except TypeError:
            return "No tables found"

    def create_table(self, table_name: str, columns: dict):
        columns_str = ", ".join([f"{name} {type}" for name, type in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.execute_query(query)

    def delete_table(self, table_name: str):
        query = f"DROP TABLE {table_name}"
        self.execute_query(query)

    def insert_df_to_table(self, df: pd.DataFrame, table_name: str):
        cleaned_df = self._clean_df_for_insert(df)
        columns = ",".join(cleaned_df.columns)
        values_placeholder = ",".join(["%s"] * len(cleaned_df.columns))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values_placeholder})"
        rows = [tuple(row) for row in cleaned_df.to_records(index=False)]
        with self.connection.cursor() as cursor:
            print(f"Inserting {len(cleaned_df)} rows into {table_name}..")
            cursor.executemany(query, rows)
            self.connection.commit()
            result = cursor.fetchall()
        return result

    def insert_dict_to_table(self, table_name: str, data: dict):
        columns = ",".join(list(data.keys()))
        values = ",".join(["%s"] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        # Convert dictionary values to tuple for parameterized query
        # Parameterized queries are safer, faster, and more efficient than using string formatting to include values
        # directly in SQL queries.
        params = tuple(data.values())
        self.execute_query(query, params)

    def _clean_df_for_insert(self, df):
        df = df.replace(r"^\s*$", np.nan, regex=True)
        df = df.where((pd.notnull(df)), None)
        return df

    def get_columns(self, table_name):
        query = f"SHOW COLUMNS FROM {table_name}"
        result = self.execute_query(query)
        return [row[0] for row in result]

    def _check_columns_equal(self, df, table_name):
        columns = self.get_columns(table_name)
        if not set(df.columns).issubset(set(columns)):
            raise ValueError(
                f"Columns in dataframe do not match columns in {table_name}"
            )
