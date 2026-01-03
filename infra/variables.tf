variable "aws_region" {
  description = "AWS Region to deploy resources"
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Project Name Tag"
  type        = string
  default     = "DevDocBot-Portfolio-Demo"
}