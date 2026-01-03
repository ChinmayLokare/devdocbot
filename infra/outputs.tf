output "demo_table_arn" {
  description = "The ARN of the demo table"
  value       = aws_dynamodb_table.demo_table.arn
}

output "deployment_status" {
  value = "Infrastructure as Code (IaC) Demo Deployed Successfully"
}