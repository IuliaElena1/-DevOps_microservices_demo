
# TO DO : Move harcoded values to variables.tf - but for the moment i will keep like this for better understanding + split in different files: providers,
# data, security etc

##################################################################################
# PROVIDERS
##################################################################################

provider "aws" {
  region = "us-east-1"
}



##################################################################################
# DATA
##################################################################################

# Dynamically fetch the latest AMI ID-Amazon machin ID from AWS SSM to avoid hardcoding,
# as AWS frequently updates image IDs with new security patches.
# run command : aws ssm get-parameters-by-path --path "/aws/service/ami-amazon-linux-latest" --region us-east-1 -> to see all parameteres from public SSM parameteres 
#--------------------------------------------------------------------------------
data "aws_ssm_parameter" "amzn2_linux" {
  name = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"
}

data "aws_iam_policy_document" "instance_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

##################################################################################
# RESOURCES
##################################################################################

## NETWORKING ##
# 1. VPC
resource "aws_vpc" "app" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
}
#-------------------------------------------------------------------------------------

# 2. Gateway
resource "aws_internet_gateway" "app" {
  vpc_id = aws_vpc.app.id
}
#-------------------------------------------------------------------------------------

# 3. Subnet
resource "aws_subnet" "public_subnet1" {
  cidr_block              = "10.0.0.0/24"
  vpc_id                  = aws_vpc.app.id
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
}
#-------------------------------------------------------------------------------------


## ROUTING ##
resource "aws_route_table" "app" {
  vpc_id = aws_vpc.app.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.app.id
  }
}
#-------------------------------------------------------------------------------------

resource "aws_route_table_association" "app_subnet1" {
  subnet_id      = aws_subnet.public_subnet1.id
  route_table_id = aws_route_table.app.id
}



## SECURITY GROUPS ##

# 1. SHH 
resource "aws_security_group" "ssh_sg" {
  name   = "ssh_sg"
  vpc_id = aws_vpc.app.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
#-------------------------------------------------------------------------------------

# 2. Number inventory
resource "aws_security_group" "number_inventory_sg" {
  name   = "number_inventory_sg"
  vpc_id = aws_vpc.app.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
#-------------------------------------------------------------------------------------

# 3. Port order
resource "aws_security_group" "port_order_sg" {
  name   = "port_order_sg"
  vpc_id = aws_vpc.app.id

  ingress {
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 4. Kafka UI
resource "aws_security_group" "kafka_ui_sg" {
  name   = "kafka_ui_sg"
  vpc_id = aws_vpc.app.id

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

## IAM ##
resource "aws_iam_role" "instance" {
  name               = "instance_role"
  path               = "/system/"
  assume_role_policy = data.aws_iam_policy_document.instance_assume_role_policy.json
}

resource "aws_iam_role_policy_attachment" "ecr_policy_attachment" {
  role       = aws_iam_role.instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "ecr_policy_attachment" {
  name = "ecr_policy_attachment"
  role = aws_iam_role.instance.name
}

## BACKEND ##

# terraform {
#   backend "s3" {
#     bucket         = "my-tf-state-bucket-12345"
#     key            = "stage1/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "terraform-locks"
#   }
# }

# Resursa pentru S3 Bucket
resource "aws_s3_bucket" "terraform_state" {
  bucket        = "my-tf-state-bucket-12345" # Numele trebuie să fie unic global
  force_destroy = true
}

# Resursa pentru DynamoDB Lock
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

# EBS Volume
resource "aws_ebs_volume" "Devopsprojvolume" {
  availability_zone = "us-east-1a"
  size              = 2
  type              = "gp3"
}

resource "aws_volume_attachment" "ebs_attach" {
  device_name = "/dev/xvdf"
  volume_id   = aws_ebs_volume.Devopsprojvolume.id
  instance_id = aws_instance.ec2_server.id
}

## INSTANCES ##

resource "aws_instance" "ec2_server" {
  key_name                    = "myFirstKey"
  ami                         = nonsensitive(data.aws_ssm_parameter.amzn2_linux.value)
  iam_instance_profile        = aws_iam_instance_profile.ecr_policy_attachment.name
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public_subnet1.id
  vpc_security_group_ids      = [aws_security_group.ssh_sg.id, aws_security_group.number_inventory_sg.id, aws_security_group.port_order_sg.id, aws_security_group.kafka_ui_sg.id]
  user_data_replace_on_change = true
  associate_public_ip_address = true
  user_data                   = <<EOF
#! /bin/bash
# 1. Installs required software: Uses the yum package manager to download and install Docker  and AWS CLI
sudo yum install -y docker aws-cli
sudo systemctl enable --now docker

# 2. # Downloads the latest docker-compose executable and grants it execution permissions
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Log in to AWS ECR registry -> the command is copied from my perssonal AWS ->  ECR -> my repository -> "view push commands"
aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 385209919903.dkr.ecr.us-east-1.amazonaws.com
EOF
}