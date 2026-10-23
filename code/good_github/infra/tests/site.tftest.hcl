# These tests use fake resources and never call AWS or read real remote state.
mock_provider "aws" {
  override_during = plan

  mock_resource "aws_s3_bucket" {
    defaults = {
      arn                         = "arn:aws:s3:::ilyaraz-good-github"
      id                          = "ilyaraz-good-github"
      bucket_regional_domain_name = "ilyaraz-good-github.s3.us-east-1.amazonaws.com"
    }
  }

  mock_resource "aws_acm_certificate" {
    defaults = {
      arn = "arn:aws:acm:us-east-1:123456789012:certificate/00000000-0000-0000-0000-000000000001"
      domain_validation_options = [
        {
          domain_name           = "goodgithub.com"
          resource_record_name  = "_apex.goodgithub.com"
          resource_record_type  = "CNAME"
          resource_record_value = "_apex.acm-validations.aws."
        },
        {
          domain_name           = "www.goodgithub.com"
          resource_record_name  = "_www.www.goodgithub.com"
          resource_record_type  = "CNAME"
          resource_record_value = "_www.acm-validations.aws."
        }
      ]
    }
  }

  mock_resource "aws_cloudfront_distribution" {
    defaults = {
      id             = "EEXAMPLE123456"
      arn            = "arn:aws:cloudfront::123456789012:distribution/EEXAMPLE123456"
      domain_name    = "dexample.cloudfront.net"
      hosted_zone_id = "Z2FDTNDATAQYW2"
    }
  }
}

override_data {
  target = data.terraform_remote_state.foundation
  values = {
    outputs = {
      domain_name    = "goodgithub.com"
      hosted_zone_id = "ZEXAMPLE123456"
    }
  }
}

run "private_site_before_dns_cutover" {
  command = plan

  assert {
    condition     = aws_s3_bucket.site.bucket == "ilyaraz-good-github" && aws_s3_bucket.site.force_destroy == false
    error_message = "The website must use the requested bucket without destructive emptying."
  }

  assert {
    condition = (
      aws_s3_bucket_public_access_block.site.block_public_acls &&
      aws_s3_bucket_public_access_block.site.block_public_policy &&
      aws_s3_bucket_public_access_block.site.ignore_public_acls &&
      aws_s3_bucket_public_access_block.site.restrict_public_buckets &&
      aws_s3_bucket_ownership_controls.site.rule[0].object_ownership == "BucketOwnerEnforced"
    )
    error_message = "S3 must stay private and ACLs must be disabled."
  }

  assert {
    condition = (
      jsondecode(aws_s3_bucket_policy.site.policy).Statement[0].Principal.Service == "cloudfront.amazonaws.com" &&
      jsondecode(aws_s3_bucket_policy.site.policy).Statement[0].Action == "s3:GetObject" &&
      jsondecode(aws_s3_bucket_policy.site.policy).Statement[0].Condition.StringEquals["AWS:SourceArn"] == aws_cloudfront_distribution.site.arn &&
      jsondecode(aws_s3_bucket_policy.site.policy).Statement[1].Effect == "Deny"
    )
    error_message = "Only the designated CloudFront distribution gets public-serving read access."
  }

  assert {
    condition = (
      aws_cloudfront_origin_access_control.site.signing_behavior == "always" &&
      one(aws_cloudfront_distribution.site.origin).domain_name == aws_s3_bucket.site.bucket_regional_domain_name &&
      aws_cloudfront_distribution.site.default_cache_behavior[0].viewer_protocol_policy == "redirect-to-https" &&
      aws_cloudfront_distribution.site.default_root_object == "index.html" &&
      aws_cloudfront_cache_policy.site.min_ttl == 0
    )
    error_message = "The site must serve index.html over HTTPS through the authenticated S3 API origin."
  }

  assert {
    condition = (
      one(aws_cloudfront_distribution.site.default_cache_behavior[0].function_association).event_type == "viewer-request" &&
      aws_cloudfront_function.canonical_host.publish &&
      strcontains(aws_cloudfront_function.canonical_host.code, "\"www.goodgithub.com\"") &&
      strcontains(aws_cloudfront_function.canonical_host.code, "statusCode: 301") &&
      strcontains(aws_cloudfront_function.canonical_host.code, "\"https://goodgithub.com\" + request.uri")
    )
    error_message = "Requests for www.goodgithub.com must be permanently redirected to the apex host."
  }

  assert {
    condition = (
      length(aws_cloudfront_distribution.site.custom_error_response) == 2 &&
      alltrue([for response in aws_cloudfront_distribution.site.custom_error_response :
        response.response_code == 404 && response.response_page_path == "/404.html"])
    )
    error_message = "Missing pages must return the generated 404 page with a 404 status."
  }

  assert {
    condition = (
      contains(jsondecode(aws_iam_policy.publisher.policy).Statement[1].Resource, "arn:aws:s3:::ilyaraz-good-github/404.html") &&
      contains(jsondecode(aws_iam_policy.publisher.policy).Statement[1].Resource, "arn:aws:s3:::ilyaraz-good-github/clusters/*")
    )
    error_message = "The publisher must be able to upload the 404 page and cluster pages."
  }

  assert {
    condition = (
      aws_cloudfront_distribution.site.aliases == toset(["goodgithub.com", "www.goodgithub.com"]) &&
      aws_acm_certificate.site.validation_method == "DNS" &&
      length(aws_route53_record.certificate_validation) == 2 &&
      length(aws_route53_record.site_ipv4) == 0 &&
      length(aws_route53_record.site_ipv6) == 0
    )
    error_message = "Both domains must have certificate validation while public DNS waits for content."
  }

  assert {
    condition = (
      output.deployment.region == "us-east-1" &&
      output.deployment.bucket == "ilyaraz-good-github" &&
      output.deployment.website_url == "https://goodgithub.com"
    )
    error_message = "The publisher must receive the intended region, bucket, and domain."
  }
}

run "publish_both_hostnames" {
  command = plan
  variables {
    publish_dns = true
  }

  assert {
    condition = (
      length(aws_route53_record.site_ipv4) == 2 &&
      length(aws_route53_record.site_ipv6) == 2 &&
      alltrue([for record in aws_route53_record.site_ipv4 : record.alias[0].name == aws_cloudfront_distribution.site.domain_name]) &&
      alltrue([for record in aws_route53_record.site_ipv6 : record.alias[0].name == aws_cloudfront_distribution.site.domain_name])
    )
    error_message = "Apex and www must each get IPv4 and IPv6 aliases to CloudFront."
  }
}
