import pandas as pd
import pymysql


class Database:
    """
    Database class to connect to a MySQL database and execute queries.
    """

    def __init__(
        self, host: str = None, user: str = None, password: str = None, db: str = None
    ):
        self.host = host
        self.user = user
        self.password = password
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

    def _clean_df_for_insert(self, df):
        df = df.replace(r"^\s*$", None, regex=True)
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
