import json
from omegaconf import OmegaConf
from src.secrets import AwsSecretsManager


class Config:
    def __init__(self, config_path: str = "app/config.yaml"):
        self.config = OmegaConf.merge(OmegaConf.load(config_path), OmegaConf.from_cli())

    def get_aws_secret(self, secret_name: str) -> json:
        secret = AwsSecretsManager(self.config.aws.region_name)
        return secret.get_secret(secret_name)

    def get_final_config(self):
        config = self.config.copy()
        for secret_name in config.aws.secrets_names:
            config.aws.secrets = self.get_aws_secret(secret_name)
        return config
