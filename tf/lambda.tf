provider "aws" {
  region = var.aws_region
}

data "aws_s3_bucket" "existingbucket" {
  bucket = "fenix-notion-file-dump"
}

# read service user secret
data "aws_secretsmanager_secret" "db_secrets" {
  name = "fenix_mysql"
}

data "aws_secretsmanager_secret_version" "db_secrets_v" {
  secret_id = data.aws_secretsmanager_secret.db_secrets.id
}

resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = "packages/lambda_layer.zip"
  layer_name = "lambda_layer_one"
  compatible_runtimes = ["python3.10"]
}

resource "aws_lambda_function" "s3_to_mysql" {
  filename         = "lambda_function.zip"  # the filename of the ZIP file containing your code
  function_name    = "s3_to_mysql"     # the name of your Lambda function
  role             = aws_iam_role.lambda_role.arn  # the ARN of the IAM role your function uses
  handler          = "lambda_handler.lambda_handler"  # the name of the function to invoke in your code
  runtime          = "python3.10"  # the runtime environment for your function
  architectures = ["arm64"]
  source_code_hash = filebase64sha256("lambda_function.zip")  # the SHA-256 hash of your ZIP file
  layers = [aws_lambda_layer_version.lambda_layer.arn]
  tags = local.resource_tags
  environment {
    variables = {
      USERNAME = local.db_creds.username
      PASSWORD = local.db_creds.password
      HOST =local.db_creds.host
      DB = local.db_creds.dbInstanceIdentifier
    }
  }
}

# This block grants the S3 service permission to invoke the Lambda function. It specifies the following:
resource "aws_lambda_permission" "lambda_permission" {
  statement_id = "AllowExecutionFromS3Bucket"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_to_mysql.arn
  principal = "s3.amazonaws.com"
  source_arn = "arn:aws:s3:::fenix-notion-file-dump"
}

resource "aws_s3_bucket_notification" "s3_notition" {
  bucket = "fenix-notion-file-dump"

  lambda_function {
    lambda_function_arn = aws_lambda_function.s3_to_mysql.arn
    events = ["s3:ObjectCreated:*"]
    filter_prefix = "notiondata_"
    filter_suffix = ".csv"
  }
}
