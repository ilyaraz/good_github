output "website_bucket_name" {
  value = aws_s3_bucket.site.bucket
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.site.id
}

output "cloudfront_url" {
  value = "https://${aws_cloudfront_distribution.site.domain_name}"
}

output "website_url" {
  value = "https://${local.domain_name}"
}

output "publisher_policy_arn" {
  description = "Attach this policy to a role used for content-only deployments."
  value       = aws_iam_policy.publisher.arn
}

output "deployment" {
  description = "Export with terraform output -json deployment > infra/deployment.json from the repo root using -chdir=infra."
  value = {
    bucket          = aws_s3_bucket.site.bucket
    region          = "us-east-1"
    distribution_id = aws_cloudfront_distribution.site.id
    cloudfront_url  = "https://${aws_cloudfront_distribution.site.domain_name}"
    website_url     = "https://${local.domain_name}"
  }
}
