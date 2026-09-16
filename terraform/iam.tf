
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

resource "aws_iam_instance_profile" "ecr_policy_attachment" {
  name = "ecr_policy_attachment"
  role = aws_iam_role.instance.name
}
