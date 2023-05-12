import io
import os

import boto3
import botocore
import pandas as pd


class S3FileHandler:
    """
    Class to handle uploading, downloading, listing and deleting files from S3 bucket.
    """

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client("s3")

    def upload_df_to_s3(self, df: pd.DataFrame, key: str):
        """Uploads a pandas dataframe to S3 as a CSV file"""
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        self.s3_client.put_object(
            Body=csv_buffer.getvalue(), Bucket=self.bucket_name, Key=key
        )
        print(f"Dataframe uploaded to s3://{self.bucket_name}/{key}")

    def load_csv_from_s3(self, key: str) -> pd.DataFrame:
        s3 = boto3.client("s3")
        response = s3.get_object(Bucket=self.bucket_name, Key=key)
        body = response["Body"]
        csv_string = body.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(csv_string))
        return df

    def upload_local_file(self, file_path: str, object_key: str = None) -> bool:
        if object_key is None:
            object_key = os.path.basename(file_path)
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_key)
        except botocore.exceptions.ClientError as e:
            print(f"Error uploading file {file_path}: {e}")
            return False
        return True

    def download_file(self, object_key: str, local_path: str = None) -> bool:
        if local_path is None:
            local_path = os.path.basename(object_key)
        try:
            self.s3_client.download_file(self.bucket_name, object_key, local_path)
        except botocore.exceptions.ClientError as e:
            print(f"Error downloading file {object_key}: {e}")
            return False
        return True

    def list_files(self) -> list:
        files = []
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        for obj in response.get("Contents", []):
            files.append(obj["Key"])
        return files

    def delete_file(self, object_key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
        except botocore.exceptions.ClientError as e:
            print(f"Error deleting file {object_key}: {e}")
            return False
        return True
