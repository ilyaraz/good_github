provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Project   = "good-github"
      ManagedBy = "Terraform"
    }
  }
}

# DNS is created separately so Namecheap can be delegated before ACM waits
# for validation. Read the foundation's state only after its backend migration.
data "terraform_remote_state" "foundation" {
  backend = "s3"
  config = {
    bucket = "ilyaraz-good-github-tfstate"
    key    = "foundation/terraform.tfstate"
    region = "us-east-1"
  }
}

locals {
  domain_name    = data.terraform_remote_state.foundation.outputs.domain_name
  hosted_zone_id = data.terraform_remote_state.foundation.outputs.hosted_zone_id
  site_domains   = toset([local.domain_name, "www.${local.domain_name}"])
  bucket_name    = "ilyaraz-good-github"
  origin_id      = "good-github-s3"
}

variable "publish_dns" {
  description = "Publish apex and www DNS aliases after the first content upload has been verified."
  type        = bool
  default     = false
}
