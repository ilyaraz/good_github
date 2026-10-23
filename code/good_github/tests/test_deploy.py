import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import call, patch

from infra import deploy


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config = self.root / "deployment.json"
        self.settings = {
            "bucket": "ilyaraz-good-github",
            "region": "us-east-1",
            "distribution_id": "EEXAMPLE123456",
            "cloudfront_url": "https://dexample.cloudfront.net",
            "website_url": "https://goodgithub.com",
        }
        self.config.write_text(json.dumps(self.settings))
        for filename in ("index.html", "404.html", "assets/styles.css", "assets/favicon.svg", "reports/example.html",
                         "clusters/example.html", "sitemap.xml", "robots.txt", ".good-github-site"):
            path = self.root / "dist" / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("example")

    def test_publish_uploads_dependencies_before_homepage_then_invalidates(self):
        def fake_run(*args, **kwargs):
            return "IEXAMPLE123" if "create-invalidation" in args else None

        with patch.object(deploy, "ROOT", self.root), \
             patch.object(deploy.sys, "argv", ["deploy.py", "--config", str(self.config)]), \
             patch.object(deploy, "run", side_effect=fake_run) as run, \
             patch.object(deploy, "verify") as verify, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(deploy.main(), 0)

        commands = [entry.args for entry in run.call_args_list]
        self.assertEqual(commands[0][0], "uv")
        self.assertIn("unittest", commands[0])
        self.assertEqual(commands[1], ("uv", "run", "build_site.py"))
        uploads = [command for command in commands if "cp" in command]
        expected = (
            ("assets/favicon.svg", "image/svg+xml"),
            ("assets/styles.css", "text/css; charset=utf-8"),
            ("reports", "text/html; charset=utf-8"),
            ("clusters", "text/html; charset=utf-8"),
            ("404.html", "text/html; charset=utf-8"),
            ("sitemap.xml", "application/xml; charset=utf-8"),
            ("robots.txt", "text/plain; charset=utf-8"),
            ("index.html", "text/html; charset=utf-8"),
        )
        self.assertEqual(len(uploads), len(expected))
        for command, (filename, content_type) in zip(uploads, expected):
            self.assertIn(self.root / "dist" / filename, command)
            self.assertIn("us-east-1", command)
            self.assertIn(deploy.CACHE_CONTROL, command)
            self.assertEqual(command[command.index("--content-type") + 1], content_type)
        self.assertFalse(any(".good-github-site" in str(argument) for command in commands for argument in command))
        self.assertFalse(any("--delete" in command for command in commands))
        self.assertGreater(next(i for i, command in enumerate(commands) if "create-invalidation" in command), commands.index(uploads[-1]))
        self.assertIn("invalidation-completed", commands[-1])
        self.assertIn("IEXAMPLE123", commands[-1])
        verify.assert_called_once_with(self.settings["cloudfront_url"], "reports/example.html")

    def test_unknown_asset_type_stops_before_upload(self):
        (self.root / "dist/assets/logo.png").write_text("example")
        with patch.object(deploy, "ROOT", self.root), \
             patch.object(deploy.sys, "argv", ["deploy.py", "--config", str(self.config)]), \
             patch.object(deploy, "run") as run, \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(deploy.main(), 1)
        self.assertIn("logo.png", errors.getvalue())
        self.assertFalse(any("cp" in entry.args for entry in run.call_args_list))

    def test_wrong_target_stops_before_build_or_aws_commands(self):
        self.settings["bucket"] = "another-bucket"
        self.config.write_text(json.dumps(self.settings))
        with patch.object(deploy.sys, "argv", ["deploy.py", "--config", str(self.config)]), \
             patch.object(deploy, "run") as run, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(deploy.main(), 1)
        run.assert_not_called()

    def test_domain_verification_is_explicit(self):
        with patch.object(deploy, "ROOT", self.root), \
             patch.object(deploy.sys, "argv", ["deploy.py", "--config", str(self.config), "--verify-domain"]), \
             patch.object(deploy, "run", return_value="IEXAMPLE123"), \
             patch.object(deploy, "verify") as verify, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(deploy.main(), 0)
        self.assertEqual(verify.call_args_list, [
            call(self.settings["cloudfront_url"], "reports/example.html"),
            call(self.settings["website_url"], "reports/example.html"),
        ])


if __name__ == "__main__":
    unittest.main()
