resource "aws_acm_certificate" "site" {
  domain_name               = local.domain_name
  subject_alternative_names = ["www.${local.domain_name}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "certificate_validation" {
  # The instance keys are known before ACM has issued its validation tokens.
  for_each = local.site_domains
  zone_id  = local.hosted_zone_id
  name = one([
    for option in aws_acm_certificate.site.domain_validation_options : option.resource_record_name
    if option.domain_name == each.key
  ])
  type = "CNAME"
  ttl  = 60
  records = [one([
    for option in aws_acm_certificate.site.domain_validation_options : option.resource_record_value
    if option.domain_name == each.key
  ])]
}

resource "aws_acm_certificate_validation" "site" {
  certificate_arn         = aws_acm_certificate.site.arn
  validation_record_fqdns = [for record in aws_route53_record.certificate_validation : record.fqdn]
}
