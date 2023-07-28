output "aws_instance_public_dns" {
  value = aws_alb.application_load_balancer.dns_name
}
