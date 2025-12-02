resource "aws_iam_role" "nitro_enclave_role" {
  name = "pd-nitro-enclave-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_policy" "nitro_enclave_policy" {
  name        = "pd-nitro-enclave-policy"
  description = "Least privilege policy for Nitro Enclave hosts"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowECRAuth"
        Effect = "Allow"
        Action = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Sid    = "AllowECRPull"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        # In a real deployment, restrict this to the specific repo ARN
        Resource = "*"
      },
      {
        Sid    = "AllowLogging"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:*:*:log-group:/aws/ec2/pd-nitro-*"
      },
      {
        Sid    = "AllowKMSDecrypt"
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        # Restrict to the specific key used for EIF encryption
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "ec2.${var.aws_region}.amazonaws.com"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "nitro_enclave_attach" {
  role       = aws_iam_role.nitro_enclave_role.name
  policy_arn = aws_iam_policy.nitro_enclave_policy.arn
}

resource "aws_iam_instance_profile" "nitro_enclave_profile" {
  name = "pd-nitro-enclave-profile"
  role = aws_iam_role.nitro_enclave_role.name
}
