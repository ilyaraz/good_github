# Keep this TXT record for ongoing Google Search Console ownership verification.
resource "aws_route53_record" "google_site_verification" {
  zone_id = local.hosted_zone_id
  name    = local.domain_name
  type    = "TXT"
  ttl     = 300
  records = ["google-site-verification=iXa2c1albFZNP7VWMTp9ToXX8hkz1PHkLcs2N1V9_KI"]
}

# Keep the first deployment accessible at its CloudFront URL while content is
# uploaded. Enable publish_dns in terraform.tfvars when that deployment is ready.
resource "aws_route53_record" "site_ipv4" {
  for_each = var.publish_dns ? local.site_domains : toset([])
  zone_id  = local.hosted_zone_id
  name     = each.value
  type     = "A"

  alias {
    name                   = aws_cloudfront_distribution.site.domain_name
    zone_id                = aws_cloudfront_distribution.site.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "site_ipv6" {
  for_each = var.publish_dns ? local.site_domains : toset([])
  zone_id  = local.hosted_zone_id
  name     = each.value
  type     = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.site.domain_name
    zone_id                = aws_cloudfront_distribution.site.hosted_zone_id
    evaluate_target_health = false
  }
}
