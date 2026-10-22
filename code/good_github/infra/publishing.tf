# Attach this policy to an existing publishing role. The appropriate trust policy
# depends on the user's CI/account setup; no IAM users or access keys are created.
resource "aws_iam_policy" "publisher" {
  name        = "good-github-content-publisher"
  description = "Upload Good GitHub site content and refresh its CloudFront cache"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListSiteBucket"
        Effect   = "Allow"
        Action   = ["s3:ListBucket", "s3:GetBucketLocation"]
        Resource = aws_s3_bucket.site.arn
      },
      {
        Sid    = "UploadSiteContent"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject"]
        Resource = [
          "${aws_s3_bucket.site.arn}/index.html",
          "${aws_s3_bucket.site.arn}/sitemap.xml",
          "${aws_s3_bucket.site.arn}/robots.txt",
          "${aws_s3_bucket.site.arn}/assets/*",
          "${aws_s3_bucket.site.arn}/reports/*"
        ]
      },
      {
        Sid      = "RefreshSiteCache"
        Effect   = "Allow"
        Action   = ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"]
        Resource = aws_cloudfront_distribution.site.arn
      }
    ]
  })
}
