# S3 Bucket — bucket name includes AWS account ID to guarantee global uniqueness
# terraform {
#   backend "s3" {
#     bucket         = "devops-tfstate-385209919903"
#     key            = "stage1/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "terraform-locks"
#   }
# }

resource "aws_s3_bucket" "terraform_state" {
  bucket        = "devops-tfstate-385209919903"
  force_destroy = true
}

# DynamoDB table used as a distributed lock — prevents simultaneous terraform applies
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
