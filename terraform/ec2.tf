
resource "aws_instance" "ec2_server" {
  key_name             = "myFirstKey"
  ami                  = nonsensitive(data.aws_ssm_parameter.amzn2_linux.value)
  iam_instance_profile = aws_iam_instance_profile.ecr_policy_attachment.name
  instance_type        = "t3.small"
  subnet_id            = aws_subnet.public_subnet1.id
  vpc_security_group_ids = [
    aws_security_group.ssh_sg.id,
    aws_security_group.number_inventory_sg.id,
    aws_security_group.port_order_sg.id,
    aws_security_group.kafka_ui_sg.id,
  ]
  user_data_replace_on_change = true
  associate_public_ip_address = true

  # todo: replace with Ansible in next steps
  user_data = <<EOF
#!/bin/bash

# 1. Install Docker, git and AWS CLI
sudo yum install -y docker git aws-cli
sudo systemctl enable --now docker
sudo usermod -a -G docker ec2-user

# 2. Install docker compose
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64" -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo curl -SL "https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64" -o /usr/local/lib/docker/cli-plugins/docker-buildx
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose /usr/local/lib/docker/cli-plugins/docker-buildx

# 3. Log in to AWS ECR (command from AWS -> ECR -> view push commands)
aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 385209919903.dkr.ecr.us-east-1.amazonaws.com

# 4. Read GitHub token from SSM Parameter Store (token is encrypted in AWS, never stored in code)
GITHUB_TOKEN=$(aws ssm get-parameter \
  --name "/devops/github_token" \
  --with-decryption \
  --region us-east-1 \
  --query "Parameter.Value" \
  --output text)

# 5. Clone using token embedded in URL — token stays in memory, never written to disk
git clone https://$GITHUB_TOKEN@github.com/IuliaElena1/-DevOps_microservices_demo /app

# 6. Start all services with docker compose
cd /app && sudo docker compose up --build -d
EOF
}
