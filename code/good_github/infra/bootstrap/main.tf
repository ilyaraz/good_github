terraform {
  required_version = ">= 1.11.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Project   = "good-github"
      ManagedBy = "Terraform"
    }
  }
}

resource "aws_s3_bucket" "state" {
  bucket        = "ilyaraz-good-github-tfstate"
  force_destroy = false

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_policy" "state" {
  bucket = aws_s3_bucket.state.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyInsecureTransport"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource  = [aws_s3_bucket.state.arn, "${aws_s3_bucket.state.arn}/*"]
      Condition = { Bool = { "aws:SecureTransport" = "false" } }
    }]
  })
}

resource "aws_route53_zone" "domain" {
  name    = "goodgithub.com"
  comment = "Good GitHub public DNS; registration remains at Namecheap until transferred"

  lifecycle {
    prevent_destroy = true
  }
}

output "domain_name" {
  value = trimsuffix(aws_route53_zone.domain.name, ".")
}

output "hosted_zone_id" {
  value = aws_route53_zone.domain.zone_id
}

output "name_servers" {
  description = "Set all of these under Namecheap > Manage > Nameservers > Custom DNS."
  value       = aws_route53_zone.domain.name_servers
}

output "state_bucket_name" {
  value = aws_s3_bucket.state.bucket
}
