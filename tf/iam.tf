resource "aws_iam_role" "lambda_role" {
  name = "lambdaassumerole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "AllowLambdaFunctions"
        Effect = "Allow"
        Action = [
          "lambda:*"
        ]
        Resource = "*"
      }
    ]
  })
}
resource "aws_iam_policy" "s3_access_policy" {
  name        = "s3-access-policy"
  description = "Policy to grant S3 access to Lambda function"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::fenix-notion-file-dump/*",
          "arn:aws:s3:::fenix-notion-file-dump"
        ]
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "lambda_policy_attachment" {
  name = "basic_execution_for_lambda"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  roles = [aws_iam_role.lambda_role.name]
}

resource "aws_iam_role_policy_attachment" "s3_access_attachment" {
  policy_arn = aws_iam_policy.s3_access_policy.arn
  role       = aws_iam_role.lambda_role.name
}


##### ECS TASK EXECUTION ROLE
resource "aws_iam_role" "ecsTaskExecutionRole" {
  name               = "ecsTaskExecutionRole"
  assume_role_policy = "${data.aws_iam_policy_document.assume_role_policy.json}"
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
  role       = "${aws_iam_role.ecsTaskExecutionRole.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

##### ECS TASK ROLE

resource "aws_iam_role" "task_role" {
  name = "example-task-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "task_policy" {
  name        = "example-task-policy"
  description = "Policy to allow access to Secrets Manager, S3, and RDS"

  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Sid       = "SecretsManagerAccess"
        Effect    = "Allow"
        Action    = [
          "secretsmanager:GetSecretValue"
        ]
        Resource  = [
          "arn:aws:secretsmanager:eu-north-1:647301530191:secret:notion_client-q1ItUh",
          "arn:aws:secretsmanager:eu-north-1:647301530191:secret:fenix_mysql-FvroL6"
        ]
      },
      {
        Sid       = "S3Access"
        Effect    = "Allow"
        Action    = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource  = [
          "arn:aws:s3:::fenix-notion-file-dump/*",
        ]
      },
      {
        Sid       = "RDSAccess"
        Effect    = "Allow"
        Action    = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds-data:ExecuteStatement",
        ]
        Resource  = [
          "arn:aws:rds:eu-north-1:647301530191:db:fenix-database"
        ]
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "task_policy_attachment" {
  policy_arn = aws_iam_policy.task_policy.arn
  role       = aws_iam_role.task_role.name
}
