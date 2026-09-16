
output "ec2_public_ip" {
  description = "Public IP of the EC2 instance — use it for SSH and accessing services"
  value       = aws_instance.ec2_server.public_ip
}

output "service_urls" {
  description = "Service URLs — available ~5-10 min after instance starts (user_data runs in background)"
  value = {
    number_inventory = "http://${aws_instance.ec2_server.public_ip}:8000/docs"
    port_order       = "http://${aws_instance.ec2_server.public_ip}:8001/docs"
    kafka_ui         = "http://${aws_instance.ec2_server.public_ip}:8080"
    ssh              = "ssh -i ~/.ssh/myFirstKey.pem ec2-user@${aws_instance.ec2_server.public_ip}"
  }
}
