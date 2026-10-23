from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import unquote, urlsplit
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree

from build_site import (ROOT, Category, build, read_clusters, read_repository_stars, render_report,
                        mid_sentence, report_description, report_facts, repository_key)


class Links(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.hrefs = []
        self.ids = []
        self.headings = 0
        self.clusters = {}
        self.current_cluster = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "details" and attrs.get("class") == "cluster":
            self.current_cluster = attrs["id"]
            self.clusters[self.current_cluster] = {"open": "open" in attrs, "hrefs": []}
        if "href" in attrs:
            self.hrefs.append(attrs["href"])
            if self.current_cluster:
                self.clusters[self.current_cluster]["hrefs"].append(attrs["href"])
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "h1":
            self.headings += 1

    def handle_endtag(self, tag):
        if tag == "details":
            self.current_cluster = None


def structured_data(source):
    return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', source)[1])


class BuildSiteTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.clusters = self.root / "clusters.md"
        self.reports = self.root / "reports"
        self.reports.mkdir()
        self.output = self.root / "dist"
        self.metadata = self.root / "repo-metadata"
        self.snapshot = self.metadata / "curl/curl/metadata.json"
        self.snapshot.parent.mkdir(parents=True)
        self.snapshot.write_text(json.dumps({"html_url": "https://github.com/curl/curl", "stargazers_count": 12345}))
        self.clusters.write_text("# Category Clusters\n\n## 1. Networking\n\n- HTTP clients\n2. Empty report\n\n## 2. Other systems\n\n- Missing report\n", encoding="utf-8")
        (self.reports / "http-clients.md").write_text(
            "# HTTP clients\n\nIntro with **emphasis** and `code`.\n\n"
            "## Libraries\n\n### [curl/curl](https://github.com/curl/curl)\n\n"
            "- [Source](https://github.com/curl/curl/blob/master/README.md)\n",
            encoding="utf-8",
        )
        (self.reports / "empty-report.md").write_text(" \n", encoding="utf-8")

    def build(self, clusters, reports, output):
        return build(clusters, reports, output, self.metadata)

    def test_build_links_and_pending_reports(self):
        self.assertEqual(self.build(self.clusters, self.reports, self.output), (3, 1))
        home = Links((self.output / "index.html").read_text())
        self.assertEqual(home.clusters, {
            "cluster-networking": {"open": False, "hrefs": ["reports/http-clients.html", "reports/empty-report.html", "clusters/networking.html"]},
            "cluster-other-systems": {"open": False, "hrefs": ["reports/missing-report.html", "clusters/other-systems.html"]},
        })
        for slug in ("http-clients", "empty-report", "missing-report"):
            self.assertIn(f"reports/{slug}.html", home.hrefs)
        report = (self.output / "reports/http-clients.html").read_text()
        links = Links(report)
        self.assertEqual(links.headings, 1)
        self.assertIn("https://github.com/curl/curl", links.hrefs)
        self.assertIn("https://github.com/curl/curl/blob/master/README.md", links.hrefs)
        self.assertIn("#libraries", links.hrefs)
        self.assertIn("<strong>emphasis</strong>", report)
        self.assertIn("<code>code</code>", report)
        self.assertIn('href="https://github.com/curl/curl">curl/curl</a> <span class="repo-stars">(12,345 ⭐)</span>', report)
        self.assertEqual(report.count('class="repo-stars"'), 1)
        self.assertTrue((self.output / "assets/styles.css").is_file())
        self.assertTrue((self.output / "assets/favicon.svg").is_file())
        for slug in ("empty-report", "missing-report"):
            pending = (self.output / f"reports/{slug}.html").read_text()
            self.assertIn("Report pending", pending)
            self.assertIn('<meta name="robots" content="noindex">', pending)
        self.assertNotIn("noindex", report)
        self.assertIn('<link rel="canonical" href="https://goodgithub.com/reports/http-clients.html">', report)
        self.assertIn("<title>HTTP clients: 1 Open-Source Repo to Study · Good GitHub</title>", report)
        self.assertIn('href="../clusters/networking.html"', report)
        self.assertNotIn('href="../reports/empty-report.html"', report)
        graph = {item["@type"]: item for item in structured_data(report)["@graph"]}
        self.assertEqual(graph["ItemList"]["itemListElement"], [{"@type": "ListItem", "position": 1, "name": "curl/curl", "url": "https://github.com/curl/curl"}])
        self.assertEqual([item["name"] for item in graph["BreadcrumbList"]["itemListElement"]], ["Home", "Networking", "HTTP clients"])
        cluster = (self.output / "clusters/networking.html").read_text()
        self.assertEqual(Links(cluster).headings, 1)
        self.assertIn('href="../reports/http-clients.html"', cluster)
        self.assertNotIn('href="../reports/empty-report.html"', cluster)
        self.assertEqual(structured_data(cluster)["@graph"][0]["@type"], "CollectionPage")
        home_source = (self.output / "index.html").read_text()
        self.assertIn('<link rel="canonical" href="https://goodgithub.com/">', home_source)
        self.assertEqual(structured_data(home_source)["@type"], "WebSite")
        not_found = (self.output / "404.html").read_text()
        self.assertIn('<meta name="robots" content="noindex">', not_found)
        self.assertIn('href="/assets/styles.css"', not_found)
        self.assertNotIn("canonical", not_found)
        sitemap = ElementTree.parse(self.output / "sitemap.xml")
        urls = [element.text for element in sitemap.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(urls, [
            "https://goodgithub.com/",
            "https://goodgithub.com/clusters/networking.html",
            "https://goodgithub.com/reports/http-clients.html",
            "https://goodgithub.com/clusters/other-systems.html",
        ])
        robots = RobotFileParser()
        robots.parse((self.output / "robots.txt").read_text().splitlines())
        self.assertEqual(robots.site_maps(), ["https://goodgithub.com/sitemap.xml"])
        for agent in ("Googlebot", "OtherBot"):
            for url in urls:
                self.assertTrue(robots.can_fetch(agent, url))

    def test_rebuild_removes_obsolete_pages(self):
        self.build(self.clusters, self.reports, self.output)
        self.clusters.write_text("## Networking\n- HTTP clients\n")
        self.assertEqual(self.build(self.clusters, self.reports, self.output), (1, 1))
        self.assertFalse((self.output / "reports/missing-report.html").exists())
        (self.reports / "http-clients.md").write_text("")
        self.build(self.clusters, self.reports, self.output)
        sitemap = ElementTree.parse(self.output / "sitemap.xml")
        self.assertEqual([element.text for element in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")],
                         ["https://goodgithub.com/", "https://goodgithub.com/clusters/networking.html"])

    def test_invalid_input_preserves_previous_build(self):
        self.build(self.clusters, self.reports, self.output)
        original = (self.output / "index.html").read_bytes()
        self.clusters.write_text("## Networking\n- HTTP clients\n## Other\n- HTTP-clients\n")
        with self.assertRaisesRegex(ValueError, "same filename"):
            self.build(self.clusters, self.reports, self.output)
        self.assertEqual((self.output / "index.html").read_bytes(), original)

    def test_unmanaged_output_and_input_directories_are_protected(self):
        self.output.mkdir()
        keep = self.output / "keep.txt"
        keep.write_text("Do not overwrite")
        with self.assertRaisesRegex(ValueError, "non-generated"):
            self.build(self.clusters, self.reports, self.output)
        self.assertEqual(keep.read_text(), "Do not overwrite")
        for output in (self.root, self.reports, self.reports / "dist", self.metadata, self.metadata / "dist"):
            with self.subTest(output=output), self.assertRaises(ValueError):
                self.build(self.clusters, self.reports, output)
        symlink = self.root / "linked-output"
        symlink.symlink_to(self.output, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symbolic link"):
            self.build(self.clusters, self.reports, symlink)

    def test_markdown_navigation_and_escaping(self):
        html, sections = render_report(
            "# Title\n\n## Same *heading*\n\n## Same heading\n\n## Top\n\n"
            "<script>alert('unsafe')</script>\n\n[Unsafe](javascript:alert(1))\n\n"
            "| Name | Value |\n| --- | --- |\n| x | ~~y~~ |\n\n"
            "```python\nprint('<hello>')\n```\n"
        )
        self.assertEqual(sections, [("same-heading", "Same heading"), ("same-heading-2", "Same heading"), ("top-2", "Top")])
        self.assertNotIn("<script>", html)
        self.assertNotIn('href="javascript:', html)
        self.assertIn("<table>", html)
        self.assertIn("<s>y</s>", html)
        self.assertIn('class="language-python"', html)
        self.clusters.write_text('## C & D <cluster> "name"\n- A & B <systems> "guide"\n')
        self.build(self.clusters, self.reports, self.output)
        home = (self.output / "index.html").read_text()
        self.assertIn("A &amp; B &lt;systems&gt; &quot;guide&quot;", home)
        self.assertIn("C &amp; D &lt;cluster&gt; &quot;name&quot;", home)

    def test_cluster_and_category_order_follows_input(self):
        self.clusters.write_text("## 3. Zeta cluster\n- Zebra\n- Alpha\n## 1) Alpha cluster ##\n* Beta\n")
        clusters = read_clusters(self.clusters, self.reports)
        self.assertEqual([cluster.name for cluster in clusters], ["Zeta cluster", "Alpha cluster"])
        self.assertEqual([category.name for category in clusters[0].categories], ["Zebra", "Alpha"])
        self.build(self.clusters, self.reports, self.output)
        home = Links((self.output / "index.html").read_text())
        self.assertEqual(list(home.clusters), ["cluster-zeta-cluster", "cluster-alpha-cluster"])
        self.assertEqual(home.clusters["cluster-zeta-cluster"]["hrefs"], ["reports/zebra.html", "reports/alpha.html", "clusters/zeta-cluster.html"])

    def test_malformed_clusters_fail_with_useful_errors(self):
        cases = [
            ("- Orphan category\n", "before a cluster"),
            ("## Empty cluster\n", "has no categories"),
            ("## Cluster\nUnexpected prose\n", "Expected a ## cluster"),
            ("## Same name\n- First\n## Same-name\n- Second\n", "same slug"),
        ]
        for source, message in cases:
            with self.subTest(source=source):
                self.clusters.write_text(source)
                with self.assertRaisesRegex(ValueError, message):
                    read_clusters(self.clusters, self.reports)

    def test_empty_cluster_list_and_missing_reports_directory(self):
        self.clusters.write_text("# Empty\n\n")
        with self.assertRaisesRegex(ValueError, "No clusters"):
            read_clusters(self.clusters, self.reports)
        with self.assertRaisesRegex(ValueError, "Reports directory"):
            read_clusters(self.clusters, self.root / "absent")

    def test_repository_stars_in_headings_tables_references_and_autolinks(self):
        self.snapshot.write_text(json.dumps({"html_url": "https://github.com/New/Repo", "stargazers_count": 12345}))
        stars = read_repository_stars(self.metadata)
        self.assertEqual(stars, {"curl/curl": 12345, "new/repo": 12345})
        stars["zero/repo"] = 0
        html, sections = render_report(
            "## [**Repo**](https://github.com/New/Repo)\n\n"
            "| Repository |\n| --- |\n| [Old name](https://GitHub.com/CURL/CURL.git/?tab=readme-ov-file#readme) |\n\n"
            "- [Reference][repo]\n- <https://www.github.com/new/repo/>\n"
            "- [Zero](http://github.com/zero/repo)\n- [Unknown](https://github.com/unknown/repo)\n\n"
            "[repo]: https://github.com/new/repo\n\n"
            "[Source](https://github.com/new/repo/blob/main/README.md)\n\n"
            "[Issue](https://github.com/new/repo/issues/1)\n\n"
            "[Other site](https://example.com/new/repo)\n\n"
            "`[Code](https://github.com/new/repo)`\n\n"
            "```markdown\n[Example](https://github.com/new/repo)\n```\n",
            stars,
        )
        self.assertEqual(sections, [("repo", "Repo")])
        self.assertIn('<h2 id="repo"><a href="https://github.com/New/Repo"><strong>Repo</strong></a> <span', html)
        self.assertEqual(html.count('<span class="repo-stars">(12,345 ⭐)</span>'), 4)
        self.assertEqual(html.count('<span class="repo-stars">(0 ⭐)</span>'), 1)
        self.assertEqual(html.count('<span class="repo-stars">(stars unavailable)</span>'), 1)
        self.assertEqual(html.count('class="repo-stars"'), 6)
        for url in ("https://github.com/org", "https://github.com/org/repo/tree/main",
                    "https://github.com.evil.test/org/repo", "https://github.com@evil.test/org/repo",
                    "https://example.com/org/repo", "https://github.com:bad/org/repo"):
            with self.subTest(url=url):
                self.assertIsNone(repository_key(url))

    def test_report_facts_feed_titles_descriptions_and_sitemap(self):
        source = (
            "# Stores\n\nResearch date: **2026-10-09**.\n\n## Group\n\n"
            "### 1. [kurrent-io/KurrentDB](https://github.com/kurrent-io/KurrentDB)\n\n"
            "### 2. [**sierra-db/sierradb**](https://github.com/sierra-db/sierradb)\n\n"
            "### 3. [Duplicate](https://github.com/kurrent-io/kurrentdb/)\n\n"
            "### [Docs](https://example.com/docs)\n\n"
            "#### 4. [nested/repo](https://github.com/nested/repo)\n\n"
            "### 4. [umadb-io/umadb](https://github.com/umadb-io/umadb)\n"
        )
        research_date, repositories = report_facts(source)
        self.assertEqual(research_date, "2026-10-09")
        self.assertEqual([label for label, _ in repositories], ["kurrent-io/KurrentDB", "sierra-db/sierradb", "umadb-io/umadb"])
        self.assertEqual(report_facts("Research date: 2026-13-45\n")[0], None)
        category = Category("Append-only event stores", "append-only-event-stores", source, research_date, repositories)
        self.assertEqual(report_description(category),
                         "3 open-source append-only event stores worth studying, including KurrentDB, sierradb and umadb. "
                         "Design decisions, trade-offs and where to start reading the code.")
        self.assertTrue(report_description(Category("HTTP clients", "http-clients", "x")).startswith("A reading guide to open-source HTTP clients:"))
        self.assertEqual(mid_sentence("Databases and Search, WebAssembly, Fourier, TCP/IP, Computer-Aided"),
                         "databases and search, WebAssembly, Fourier, TCP/IP, computer-aided")
        generic = Category("Relational database servers", "relational-database-servers", "x", None,
                           [("postgres/postgres", "https://github.com/postgres/postgres"), ("MariaDB/server", "https://github.com/MariaDB/server")])
        self.assertIn("including postgres and MariaDB/server.", report_description(generic))
        (self.reports / "http-clients.md").write_text(source, encoding="utf-8")
        self.build(self.clusters, self.reports, self.output)
        sitemap = ElementTree.parse(self.output / "sitemap.xml")
        namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        modified = {entry.find(f"{namespace}loc").text: getattr(entry.find(f"{namespace}lastmod"), "text", None)
                    for entry in sitemap.findall(f"{namespace}url")}
        self.assertEqual(modified, {
            "https://goodgithub.com/": "2026-10-09",
            "https://goodgithub.com/clusters/networking.html": "2026-10-09",
            "https://goodgithub.com/reports/http-clients.html": "2026-10-09",
            "https://goodgithub.com/clusters/other-systems.html": None,
        })
        article = structured_data((self.output / "reports/http-clients.html").read_text())["@graph"][0]
        self.assertEqual((article["datePublished"], article["dateModified"]), ("2026-10-09", "2026-10-09"))

    def test_structured_data_cannot_close_its_script(self):
        self.clusters.write_text("## Networking\n- HTTP </script><b> clients\n")
        (self.reports / "http-script-b-clients.md").write_text("Intro\n")
        self.build(self.clusters, self.reports, self.output)
        report = (self.output / "reports/http-script-b-clients.html").read_text()
        self.assertEqual(report.count("</script>"), 3)
        self.assertEqual(structured_data(report)["@graph"][0]["headline"], "HTTP </script><b> clients")

    def test_invalid_metadata_preserves_previous_build(self):
        self.build(self.clusters, self.reports, self.output)
        original = (self.output / "reports/http-clients.html").read_bytes()
        for value in (None, -1, True, 1.5, "165"):
            with self.subTest(value=value):
                self.snapshot.write_text(json.dumps({"html_url": "https://github.com/curl/curl", "stargazers_count": value}))
                with self.assertRaisesRegex(ValueError, "stargazers_count"):
                    self.build(self.clusters, self.reports, self.output)
                self.assertEqual((self.output / "reports/http-clients.html").read_bytes(), original)
        self.snapshot.write_text("{")
        with self.assertRaisesRegex(ValueError, "Invalid repository metadata"):
            self.build(self.clusters, self.reports, self.output)
        self.snapshot.unlink()
        with self.assertRaisesRegex(ValueError, "No repository metadata"):
            self.build(self.clusters, self.reports, self.output)
        self.assertEqual((self.output / "reports/http-clients.html").read_bytes(), original)

    def test_actual_collection_has_no_broken_internal_links(self):
        clusters = read_clusters(ROOT / "clusters.md", ROOT / "repo-research")
        categories = [category for cluster in clusters for category in cluster.categories]
        build(ROOT / "clusters.md", ROOT / "repo-research", self.output)
        pages = {
            path: Links(path.read_text(encoding="utf-8"))
            for path in self.output.rglob("*.html")
        }
        self.assertEqual(len(pages), len(categories) + len(clusters) + 2)
        home = pages[self.output / "index.html"]
        self.assertEqual(len(home.clusters), len(clusters))
        for cluster in clusters:
            rendered = home.clusters[f"cluster-{cluster.slug}"]
            self.assertFalse(rendered["open"])
            self.assertEqual(rendered["hrefs"], [f"reports/{category.slug}.html" for category in cluster.categories] + [f"clusters/{cluster.slug}.html"])
        for path, page in pages.items():
            self.assertEqual(page.headings, 1, path)
            self.assertEqual(len(page.ids), len(set(page.ids)), path)
            for href in page.hrefs:
                url = urlsplit(href)
                if url.scheme or url.netloc:
                    continue
                base = self.output if url.path.startswith("/") else path.parent
                target = (base / unquote(url.path).lstrip("/")).resolve() if url.path else path
                self.assertTrue(target.exists(), f"{path.name}: {href}")
                if url.fragment:
                    self.assertIn(unquote(url.fragment), pages[target].ids, f"{path.name}: {href}")


if __name__ == "__main__":
    unittest.main()
