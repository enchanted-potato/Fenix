import os
import boto3
import pandas as pd
from io import StringIO

from lambda_helper import Database

username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
host = os.environ.get("HOST")
database = os.environ.get("DB")


def get_max_db_date(table):
    with Database(user=username, password=password, host=host, db=database) as db:
        return db.execute_query(f"SELECT MAX(Datetime) FROM {table};")[0][0]


def lambda_handler(event, context):
    print("Bucket name:", event["Records"][0]["s3"]["bucket"]["name"])
    print(
        "File name:", event["Records"][0]["s3"]["object"]["key"]
    )  # get the bucket and object key from the S3 event

    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    s3_object_key = event["Records"][0]["s3"]["object"]["key"]

    # create an S3 client
    s3_client = boto3.client("s3")

    # read the CSV file from S3
    s3_response = s3_client.get_object(Bucket=s3_bucket, Key=s3_object_key)
    data = s3_response["Body"].read().decode("utf-8")

    # convert the CSV data to a Pandas DataFrame
    df = pd.read_csv(StringIO(data))

    # get the max date in the database
    date = get_max_db_date("notion")
    print("Max db date:", date)

    # filter the s3 rows greater than the max date
    if date:
        print(f"Max s3 date: {max(df.Datetime)}")
        df = df[df.Datetime > date]

    # insert new rows in database
    with Database(user=username, password=password, host=host, db=database) as db:
        result = db.insert_df_to_table(df, "notion")

    return result
