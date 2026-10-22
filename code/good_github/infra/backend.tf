terraform {
  backend "s3" {
    bucket       = "ilyaraz-good-github-tfstate"
    key          = "site/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
