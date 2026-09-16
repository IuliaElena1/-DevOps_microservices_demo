
resource "aws_iam_role" "instance" {
  name               = "instance_role"
  path               = "/system/"
  assume_role_policy = data.aws_iam_policy_document.instance_assume_role_policy.json
}

# Allows EC2 to pull images from ECR
resource "aws_iam_role_policy_attachment" "ecr_policy_attachment" {
  role       = aws_iam_role.instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Allows EC2 to read the GitHub token stored in SSM Parameter Store
resource "aws_iam_role_policy" "ssm_read_policy" {
  name = "ssm_read_github_token"
  role = aws_iam_role.instance.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "kms:Decrypt"
        ]
        Resource = [
          "arn:aws:ssm:us-east-1:385209919903:parameter/devops/github_token",
          "arn:aws:kms:us-east-1:385209919903:key/*"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ecr_policy_attachment" {
  name = "ecr_policy_attachment"
  role = aws_iam_role.instance.name
}
