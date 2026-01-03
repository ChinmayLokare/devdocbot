# This is a Demonstration Resource to prove IaC capability.
# In a full production migration, all manual resources (Lambda, API Gateway)
# would be imported into this state file.

resource "aws_dynamodb_table" "demo_table" {
  name           = "devdocbot-terraform-demo"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "demo_id"

  attribute {
    name = "demo_id"
    type = "S"
  }

  tags = {
    Name        = "Terraform-Demo"
    Project     = var.project_name
    Description = "Created via Terraform to demonstrate IaC skills"
  }
}