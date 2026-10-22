# AWS hosting for goodgithub.com

This directory defines a private S3 origin, CloudFront, Route 53 DNS, an ACM certificate, and a scoped content-publishing IAM policy. Both `goodgithub.com` and `www.goodgithub.com` serve the site. All regional resources use **us-east-1**; CloudFront and Route 53 DNS are global.

| Configuration | Resources |
| --- | --- |
| `bootstrap/` | The `ilyaraz-good-github-tfstate` state bucket and `goodgithub.com` public hosted zone |
| This directory | The `ilyaraz-good-github` website bucket, CloudFront/OAC, certificate/validation, optional DNS aliases, and publishing policy |

The foundation is separate because its nameservers must be configured at Namecheap before ACM can validate the certificate. Creating a hosted zone does not transfer the domain registration. Namecheap remains the registrar until a separate transfer is completed.

## Prerequisites

- Terraform **1.11 or newer**, below 2.0. The S3 backend uses native `use_lockfile` locking, and the tests use mocks during planning. Terraform 1.5.7 is too old for this configuration.
- AWS CLI v2, Python 3.10+, and `uv` for content deployments.
- An authenticated AWS profile with permission to create the resources above, including IAM policies. Use the same AWS account for both Terraform configurations.
- Access to change nameservers for `goodgithub.com` at Namecheap.

Run the commands below from the repository root. Use your own profile name:

```sh
export AWS_PROFILE=your-profile
aws sts get-caller-identity
```

Both bucket names must be available globally. If they already exist in your account, import them and their configuration resources into the corresponding state rather than creating replacements. If a Route 53 hosted zone for `goodgithub.com` already exists, import that zone into `aws_route53_zone.domain` in `bootstrap` before applying, so the deployment uses one authoritative zone.

## 1. Create the foundation once

For the first deployment only, bootstrap starts with local state because its state bucket does not exist yet:

```sh
terraform -chdir=infra/bootstrap init
terraform -chdir=infra/bootstrap plan -out=foundation.tfplan
terraform -chdir=infra/bootstrap apply foundation.tfplan
terraform -chdir=infra/bootstrap output name_servers
```

The state bucket has versioning, default encryption, disabled ACLs, blocked public access, and an HTTPS-only bucket policy. The state bucket and hosted zone have `prevent_destroy` protection.

Move the foundation state into its new S3 backend immediately after the first apply:

```sh
cp infra/bootstrap/backend.tf.example infra/bootstrap/backend.tf
terraform -chdir=infra/bootstrap init -migrate-state
```

Accept Terraform's prompt to copy the existing local state. Preserve the local backup until migration succeeds. The site configuration reads the hosted-zone ID and domain from `foundation/terraform.tfstate`; its own state is stored separately at `site/terraform.tfstate` in the same bucket.

For a later checkout or a second machine, copy `backend.tf.example` to `backend.tf` **before** running `terraform init`; connect to the existing remote state instead of repeating a local-state bootstrap. State files, plan files, local settings, and the generated backend file are ignored by Git. Commit both `.terraform.lock.hcl` files.

## 2. Delegate DNS from Namecheap once

Before changing nameservers, copy any existing website, email, and verification records into the new Route 53 zone. If DNSSEC is enabled, handle the existing DS records as part of the DNS migration before changing nameservers.

In Namecheap, open **Domain List → goodgithub.com → Manage → Nameservers → Custom DNS**. Enter every nameserver from the foundation output and save. Keep this Route 53 hosted zone throughout any later registrar transfer.

Verify that public DNS now delegates to those nameservers:

```sh
dig NS goodgithub.com +short
```

Wait for delegation to propagate before the next step; otherwise Terraform's ACM validation resource will wait and can time out. A new domain's registration transfer restriction does not prevent this DNS delegation or hosting the website on AWS.

## 3. Create the website infrastructure

```sh
cp infra/terraform.tfvars.example infra/terraform.tfvars
terraform -chdir=infra init
terraform -chdir=infra plan -out=site.tfplan
terraform -chdir=infra apply site.tfplan
terraform -chdir=infra output -json deployment > infra/deployment.json
```

The initial `publish_dns = false` setting creates the certificate validation records but does not publish apex/www website aliases. ACM requests a certificate in `us-east-1` and validates both hostnames through Route 53. Keep its CNAME records for automatic certificate renewal.

The S3 bucket is private and uses its regional API endpoint, with CloudFront signing every origin request through OAC. S3 website hosting and public-read ACLs are not enabled. CloudFront redirects HTTP to HTTPS, serves `index.html` at `/`, and supports the generator's existing `/reports/<slug>.html` URLs. Both custom hostnames serve the same content; no www-to-apex redirect is configured.

## 4. Upload and verify the first build

```sh
python3 infra/deploy.py
```

The helper reads the exported deployment configuration, runs the generator tests, rebuilds `dist`, uploads assets, reports, and crawler files, uploads the homepage last, invalidates CloudFront, and checks the homepage, stylesheet, one report, sitemap, and robots file through the CloudFront hostname. It uploads only `assets/`, `reports/`, `sitemap.xml`, `robots.txt`, and `index.html`; `.good-github-site` is not uploaded.

All uploaded files use `Cache-Control: public,max-age=0,s-maxage=3600,must-revalidate`. Browsers revalidate while CloudFront can cache for an hour. Old report objects are retained so cached links continue working; removal is a separate cleanup operation. Object versioning is enabled for recovery, and both buckets reject automatic destruction.

The sitemap is regenerated from the current collection and lists `https://goodgithub.com/` plus reports with content. Pending reports are omitted. `robots.txt` allows crawling and points to `https://goodgithub.com/sitemap.xml`. After deployment, submit that URL in Google Search Console's Sitemaps page; later content deployments keep the sitemap updated automatically. The publishing policy grants access to both files, so apply the Terraform policy update before first uploading them with a content-only role.

The helper uses the AWS CLI's normal credentials, including `AWS_PROFILE`. For a content-only publishing role, attach the IAM policy identified by `terraform output publisher_policy_arn` to an existing role with the appropriate trust configuration. The exported `deployment.json` contains identifiers and public URLs, not credentials, so this publishing role does not need permission to read Terraform state. Terraform administration requires broader permissions than content publishing.

## 5. Publish the custom domain

Change `publish_dns` to `true` in `infra/terraform.tfvars`, then run:

```sh
terraform -chdir=infra plan -out=site.tfplan
terraform -chdir=infra apply site.tfplan
curl -I https://goodgithub.com/
curl -I https://www.goodgithub.com/
curl -I http://goodgithub.com/
```

Terraform creates A and AAAA aliases for both hostnames. The HTTPS requests should return 200 and HTTP should redirect to HTTPS after DNS propagation. Keep `publish_dns = true` in the configuration for subsequent applies; setting it back to false removes those four aliases.

## Subsequent content updates

```sh
python3 infra/deploy.py --verify-domain
```

Content changes do not require `terraform apply`. Re-export `deployment.json` after infrastructure changes that alter the distribution or its identifiers. For infrastructure changes, run `terraform plan` and apply the saved plan. For CI, use short-lived credentials from an IAM role and serialize deployments. A saved Terraform plan can be applied without interactive confirmation using the commands above.

To roll back content, restore an earlier source/build version, upload its files, and invalidate CloudFront again. S3 retains prior object versions as an additional recovery option. Do not delete certificate validation records during a registrar transfer.

## Optional later registration transfer

Transfer `goodgithub.com` from Namecheap separately after it is eligible, keeping the nameservers from this foundation. This configuration does not attempt to register your existing domain again or initiate a transfer with missing authorization/contact details. After transfer, domain settings can be adopted with `aws_route53domains_registered_domain` in the foundation. The hosting configuration needs no change.

## Local validation without AWS access

Run in a fresh checkout with Terraform 1.11+:

```sh
terraform fmt -check -recursive infra
terraform -chdir=infra/bootstrap init -backend=false
terraform -chdir=infra/bootstrap validate
terraform -chdir=infra/bootstrap test
terraform -chdir=infra init -backend=false
terraform -chdir=infra validate
terraform -chdir=infra test
python3 -m py_compile infra/deploy.py
```

The Terraform tests mock the AWS provider and override the foundation-state lookup. They check bucket privacy, restricted CloudFront access, certificate/domain coverage, caching, and the DNS publishing switch without creating AWS resources. Provider downloads still require internet access. These checks do not establish bucket-name availability, AWS permissions, or DNS ownership; the real plan/apply checks those in your account.

## References

- [Terraform S3 backend and state locking](https://developer.hashicorp.com/terraform/language/backend/s3)
- [CloudFront origin access control for private S3 buckets](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- [CloudFront certificate requirements](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html)
- [Namecheap nameserver configuration](https://www.namecheap.com/support/knowledgebase/article.aspx/767/10/how-to-change-dns-for-a-domain/)
- [AWS domain transfer procedure](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-transfer-to-route-53.html)
