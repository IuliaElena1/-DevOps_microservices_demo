output "aws_instance_dns" {
  value       = "http://${aws_instance.ec2_server.public_dns}:${80}"
  description = "Access your Nginx website using this URL"
}
