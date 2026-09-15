# AWS Infrastructure Architecture

**!!!!!!!   INTERACTIVE DIAGRAM ***:** https://claude.ai/code/artifact/c7b6a8df-ef39-4727-af54-954f636509fc


Here is the technical diagram of your infrastructure, organized by connection levels:


                                [ INTERNET ]
                                     │
                                     │ (Ingress / Egress Traffic)
                                     ▼
                   ┌───────────────────────────────────┐
                   │   aws_internet_gateway.app        │
                   └─────────────────┬─────────────────┘
                                     │
                                     │ (Route 0.0.0.0/0)
                                     ▼
                   ┌───────────────────────────────────┐
                   │      aws_route_table.app          │
                   └─────────────────┬─────────────────┘
                                     │
                                     │ (aws_route_table_association)
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│ aws_vpc.app (10.0.0.0/16)                                              │
│                                                                        │
│   ┌──────────────────────────────────────────────────────────────────┐ │
│   │ aws_subnet.public_subnet1 (10.0.0.0/24 - us-east-1a)            │ │
│   │                                                                  │ │
│   │   SECURITY GROUPS (Virtual Firewall)                             │ │
│   │   ├── aws_security_group.ssh_sg ------------> Allows Port 22     │ │
│   │   ├── aws_security_group.number_inventory_sg -> Allows Port 8000 │ │
│   │   └── aws_security_group.port_order_sg -----> Allows Port 8001  │ │
│   │                                                                  │ │
│   │   ┌────────────────────────────────────────────────────────────┐ │ │
│   │   │ aws_instance.backend_sg (t3.micro, Amazon Linux 2)         │ │ │
│   │   │                                                            │ │ │
│   │   │  [IAM Instance Profile]                                    │ │ │
│   │   │   └── aws_iam_instance_profile.ecr_policy_attachment       │ │ │
│   │   │        └── aws_iam_role.instance                           │ │ │
│   │   │             └── AmazonEC2ContainerRegistryReadOnly Policy  │ │ │
│   │   │                                                            │ │ │
│   │   │  [user_data / Docker Runtime]                              │ │ │
│   │   │   1. Install Docker & AWS CLI via YUM                      │ │ │
│   │   │   2. ECR Authentication via IAM Role (No manual keys)      │ │ │
│   │   │   3. Backend Microservices Container (Ports 8000 & 8001)   │ │ │
│   │   └────────────────────────────────────────────────────────────┘ │ │
│   └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

## How each resource is connected in main.tf

### 1. Networking Level (VPC → Subnet → Internet)

- `aws_internet_gateway.app` attaches to `aws_vpc.app.id`
- `aws_subnet.public_subnet1` is created inside `aws_vpc.app.id`
- `aws_route_table.app` has a route (`0.0.0.0/0`) pointing to `aws_internet_gateway.app.id`
- `aws_route_table_association.app_subnet1` links the subnet to the route table — this converts the subnet from private to a **public subnet** with Internet access

### 2. Permissions Level (IAM → ECR Access)

- `data.aws_iam_policy_document.instance_assume_role_policy` grants `ec2.amazonaws.com` permission to assume a role
- `aws_iam_role.instance` uses that Trust Policy
- `aws_iam_role_policy_attachment.ecr_policy_attachment` attaches `AmazonEC2ContainerRegistryReadOnly` to the role
- `aws_iam_instance_profile.ecr_policy_attachment` wraps the IAM role into a profile that the EC2 instance can "wear"

### 3. Server Level (EC2 → Everything Assembled)

Your `aws_instance.backend_sg` instance connects all the pieces in the file:

- **Image:** `data.aws_ssm_parameter.amzn2_linux.value` provides the latest official Amazon Linux 2 AMI ID
- **Network:** `subnet_id = aws_subnet.public_subnet1.id` places the instance inside the public subnet
- **Security:** `vpc_security_group_ids` attaches all 3 Security Groups simultaneously (SSH :22, Inventory :8000, Port Order :8001)
- **Authentication:** `iam_instance_profile = aws_iam_instance_profile.ecr_policy_attachment.name` grants the server native access to AWS ECR
- **Boot Process:** `user_data` installs Docker, retrieves the ECR token using the attached IAM Role, and starts the application on both ports
