## EBS VOLUME ##

# Extra persistent disk attached to EC2 — survives instance stop/start
resource "aws_ebs_volume" "Devopsprojvolume" {
  availability_zone = "us-east-1a"
  size              = 2
  type              = "gp3"
}

# /dev/xvdf is the AWS convention for the first additional disk (after root /dev/xvda)
resource "aws_volume_attachment" "ebs_attach" {
  device_name = "/dev/xvdf"
  volume_id   = aws_ebs_volume.Devopsprojvolume.id
  instance_id = aws_instance.ec2_server.id
}
