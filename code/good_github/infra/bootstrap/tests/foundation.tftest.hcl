mock_provider "aws" {
  override_during = plan
}

run "private_versioned_state_and_public_dns" {
  command = plan

  assert {
    condition = (
      aws_s3_bucket.state.bucket == "ilyaraz-good-github-tfstate" &&
      aws_s3_bucket.state.force_destroy == false &&
      aws_s3_bucket_versioning.state.versioning_configuration[0].status == "Enabled" &&
      aws_s3_bucket_public_access_block.state.block_public_policy &&
      aws_s3_bucket_public_access_block.state.restrict_public_buckets
    )
    error_message = "Terraform state must have a separate private, versioned bucket."
  }

  assert {
    condition     = output.domain_name == "goodgithub.com" && aws_route53_zone.domain.name == "goodgithub.com"
    error_message = "The foundation must create DNS for the existing Namecheap domain."
  }
}
