import json

import boto3
from botocore.exceptions import ClientError


class AwsSecretsManager:
    def __init__(self, region_name):
        self.region_name = region_name

        session = boto3.session.Session()
        self.client_session = session.client(
            service_name="secretsmanager", region_name=self.region_name
        )

    def get_secret(self, secret_name):
        try:
            get_secret_value_response = self.client_session.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            raise e

        # Decrypts secret using the associated KMS key.
        secret = get_secret_value_response["SecretString"]

        return json.loads(secret)
