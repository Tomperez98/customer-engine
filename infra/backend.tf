terraform {
  backend "s3" {
    bucket         = "tomp-aws-terraform-states"
    key            = "customer-engine/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "tomp-aws-terraform-states"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.3.7"
}


provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Terraform      = true
      CustomerEngine = true
    }

  }
}