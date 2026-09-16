# 1. VPC
resource "aws_vpc" "app" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
}

# 2. Internet Gateway
resource "aws_internet_gateway" "app" {
  vpc_id = aws_vpc.app.id
}

# 3. Subnet
resource "aws_subnet" "public_subnet1" {
  cidr_block              = "10.0.0.0/24"
  vpc_id                  = aws_vpc.app.id
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
}

## ROUTING ##

resource "aws_route_table" "app" {
  vpc_id = aws_vpc.app.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.app.id
  }
}

resource "aws_route_table_association" "app_subnet1" {
  subnet_id      = aws_subnet.public_subnet1.id
  route_table_id = aws_route_table.app.id
}
