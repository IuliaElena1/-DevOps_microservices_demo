# Deploy the S3 bucket to store the state
cd ../s3_bucket_create

#----------------------------
# terraform formatting 
terraform fmt

# terraform validate
terraform validate

# Initialize and apply the S3 bucket
terraform init
terraform plan -out bucket.tfplan
terraform apply bucket.tfplan

#--------------------------

# Try out the state commands
cd ../globo_web_app

# Show the current state
terraform show

terraform show -json

# List out resources in the state
terraform state list

# Show a specific resource in the state
terraform state show aws_instance.nginx1

# Update the globo_web_app backend to use the S3 bucket
terraform init -backend-config="key=dev.tfstate"

# Run state show again to see the updated state
terraform state show aws_instance.nginx1

# Tear down the deployments to save costs
# Globo Web App first
terraform destroy -auto-approve

# Then the S3 bucket
cd ../s3_bucket_create
terraform destroy -auto-approve