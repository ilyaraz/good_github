#!/usr/bin/env python3
"""Build and publish site content using the deployment output from Terraform."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent.parent
CACHE_CONTROL = "public,max-age=0,s-maxage=3600,must-revalidate"
ROOT_FILES = (
    ("sitemap.xml", "application/xml; charset=utf-8"),
    ("robots.txt", "text/plain; charset=utf-8"),
    ("index.html", "text/html; charset=utf-8"),
)


def run(*args, capture=False):
    print("+ " + " ".join(str(arg) for arg in args), flush=True)
    result = subprocess.run(
        [str(arg) for arg in args], cwd=ROOT, check=True,
        text=True, stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout.strip() if capture else None


def load_config(path):
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Deployment configuration must be a JSON object exported by Terraform.")
    if config.get("bucket") != "ilyaraz-good-github" or config.get("region") != "us-east-1":
        raise ValueError("Deployment configuration must target ilyaraz-good-github in us-east-1.")
    if not isinstance(config.get("distribution_id"), str) or not config["distribution_id"].isalnum():
        raise ValueError("Deployment configuration needs a CloudFront distribution ID.")
    for key in ("cloudfront_url", "website_url"):
        url = urlsplit(config.get(key, ""))
        if url.scheme != "https" or not url.hostname or url.username or url.password or url.path or url.query or url.fragment:
            raise ValueError(f"Invalid HTTPS base URL in deployment configuration: {key}")
    return config


def verify(base_url, report_path):
    for path, expected_type in (
        ("/", "text/html"),
        ("/assets/styles.css", "text/css"),
        ("/" + report_path, "text/html"),
        ("/sitemap.xml", "application/xml"),
        ("/robots.txt", "text/plain"),
    ):
        url = base_url + path
        with urlopen(url, timeout=30) as response:
            if response.status != 200 or response.headers.get_content_type() != expected_type:
                raise ValueError(f"Unexpected HTTP status or content type at {url}")
        print(f"Verified {url}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("deployment.json"))
    parser.add_argument("--verify-domain", action="store_true", help="Also check goodgithub.com after its DNS aliases have been published.")
    args = parser.parse_args()

    try:
        # Read the explicit export first: a publishing role need not read Terraform state.
        config = load_config(args.config)
        run("uv", "run", "--with", "markdown-it-py==4.0.0", "python", "-m", "unittest", "discover", "-s", "tests", "-v")
        run("uv", "run", "build_site.py")
        dist = ROOT / "dist"
        reports = sorted((dist / "reports").glob("*.html"))
        required_files = [filename for filename, _ in ROOT_FILES] + ["assets/styles.css"]
        if not reports or not all((dist / filename).is_file() for filename in required_files):
            raise ValueError("Build did not produce the expected HTML, CSS, sitemap.xml, and robots.txt files.")

        aws = ["aws", "--region", config["region"], "--no-cli-pager"]
        destination = f"s3://{config['bucket']}"
        # Re-upload these small files to update both content and cache metadata.
        # Do not delete old report URLs while browsers might still have older links.
        for directory, content_type in (("assets", "text/css; charset=utf-8"), ("reports", "text/html; charset=utf-8")):
            run(*aws, "s3", "cp", dist / directory, f"{destination}/{directory}/",
                "--recursive", "--no-follow-symlinks", "--only-show-errors",
                "--content-type", content_type, "--cache-control", CACHE_CONTROL)
        for filename, content_type in ROOT_FILES:
            run(*aws, "s3", "cp", dist / filename, f"{destination}/{filename}",
                "--only-show-errors", "--content-type", content_type, "--cache-control", CACHE_CONTROL)
        invalidation_id = run(*aws, "cloudfront", "create-invalidation",
                              "--distribution-id", config["distribution_id"], "--paths", "/*",
                              "--query", "Invalidation.Id", "--output", "text", capture=True)
        run(*aws, "cloudfront", "wait", "invalidation-completed",
            "--distribution-id", config["distribution_id"], "--id", invalidation_id)
        report_path = reports[0].relative_to(dist).as_posix()
        verify(config["cloudfront_url"], report_path)
        if args.verify_domain:
            verify(config["website_url"], report_path)
    except (OSError, ValueError, URLError, subprocess.CalledProcessError) as error:
        print(f"Deployment failed: {error}", file=sys.stderr)
        return 1
    print(f"Published to {config['cloudfront_url']}; custom domain: {config['website_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
