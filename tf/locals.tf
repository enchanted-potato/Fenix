locals {
  resource_tags = {
    app_code   = "fenix-app"
  }
}

locals {
  db_creds = jsondecode(
    data.aws_secretsmanager_secret_version.db_secrets_v.secret_string
  )
}
