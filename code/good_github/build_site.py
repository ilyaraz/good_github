#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py==4.0.0"]
# ///
"""Turn category clusters and Markdown reports into a portable static website."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unicodedata
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

try:
    from markdown_it import MarkdownIt
except ImportError:
    raise SystemExit(
        "Missing Markdown renderer. Run `uv run build_site.py` or install "
        "the dependencies with `python3 -m pip install -r requirements.txt`."
    ) from None


ROOT = Path(__file__).resolve().parent
MARKER = ".good-github-site"
MARKER_CONTENT = "good-github-static-site-v1\n"
SITE_URL = "https://goodgithub.com"
GOOGLE_ANALYTICS_ID = "G-SLF19PMTRF"


@dataclass
class Category:
    name: str
    slug: str
    content: str | None


@dataclass
class Cluster:
    name: str
    slug: str
    categories: list[Category]


def slugify(value: str) -> str:
    """Match the report filenames: lowercase words separated by hyphens."""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def read_clusters(clusters_path: Path, reports_dir: Path) -> list[Cluster]:
    if not reports_dir.is_dir():
        raise ValueError(f"Reports directory does not exist: {reports_dir}")
    clusters = []
    seen_clusters = {}
    seen_categories = {}
    for line_number, line in enumerate(clusters_path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = line.strip()
        if not line or re.match(r"^#\s", line):
            continue
        heading = re.fullmatch(r"##\s+(.+?)(?:\s+#+)?", line)
        if heading:
            name = re.sub(r"^\d+[.)]\s+", "", heading[1]).strip()
            slug = slugify(name)
            if not slug:
                raise ValueError(f"Cluster on line {line_number} has no usable name: {name!r}")
            if slug in seen_clusters:
                raise ValueError(f"Clusters {seen_clusters[slug]!r} and {name!r} have the same slug: {slug}")
            seen_clusters[slug] = name
            clusters.append(Cluster(name, slug, []))
            continue
        item = re.fullmatch(r"(?:[-*+]|\d+[.)])\s+(.+)", line)
        if not item:
            raise ValueError(f"Expected a ## cluster heading or category list item on line {line_number}: {line!r}")
        if not clusters:
            raise ValueError(f"Category on line {line_number} appears before a cluster heading.")
        name = item[1].strip()
        slug = slugify(name)
        if not slug:
            raise ValueError(f"Category on line {line_number} has no usable filename: {name!r}")
        if slug in seen_categories:
            raise ValueError(f"Categories {seen_categories[slug]!r} and {name!r} have the same filename: {slug}.md")
        seen_categories[slug] = name
        report = reports_dir / f"{slug}.md"
        content = report.read_text(encoding="utf-8-sig") if report.exists() else None
        clusters[-1].categories.append(Category(name, slug, content if content and content.strip() else None))
    if not clusters:
        raise ValueError(f"No clusters found in {clusters_path}")
    for cluster in clusters:
        if not cluster.categories:
            raise ValueError(f"Cluster {cluster.name!r} has no categories.")
    return clusters


def repository_key(url: str) -> str | None:
    """Normalize repository home links, excluding files, issues, and other subpages."""
    try:
        parsed = urlsplit(url)
        if (parsed.scheme.lower() not in {"http", "https"}
                or parsed.hostname not in {"github.com", "www.github.com"}
                or parsed.username or parsed.password or parsed.port is not None):
            return None
    except ValueError:
        return None
    path = unquote(parsed.path).strip("/").lower()
    if path.endswith(".git"):
        path = path[:-4]
    return path if re.fullmatch(r"[a-z0-9-]+/[a-z0-9_.-]+", path) else None


def read_repository_stars(metadata_dir: Path) -> dict[str, int]:
    """Read the saved API counts, indexed by both listed and canonical repo names."""
    files = sorted(metadata_dir.glob("*/*/metadata.json"))
    if not files:
        raise ValueError(f"No repository metadata.json files found in {metadata_dir}")
    stars = {}
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as error:
            raise ValueError(f"Invalid repository metadata in {path}: {error}") from error
        count = data.get("stargazers_count") if isinstance(data, dict) else None
        if type(count) is not int or count < 0:
            raise ValueError(f"Invalid stargazers_count in {path}: expected a nonnegative integer")
        canonical = repository_key(str(data.get("html_url", "")))
        listed = repository_key(f"https://github.com/{path.parent.parent.name}/{path.parent.name}")
        if canonical is None or listed is None:
            raise ValueError(f"Invalid repository URL or directory in {path}")
        for key in (listed, canonical):
            if key in stars and stars[key] != count:
                raise ValueError(f"Conflicting saved star counts for {key} in {path}")
            stars[key] = count
    return stars


def render_report(source: str, repository_stars: dict[str, int] | None = None) -> tuple[str, list[tuple[str, str]]]:
    # Disable embedded HTML; CommonMark links, lists, code, and emphasis still render.
    markdown = MarkdownIt("commonmark", {"html": False}).enable(["table", "strikethrough"])

    def close_link(renderer, tokens, index, options, env):
        result = renderer.renderToken(tokens, index, options, env)
        repository = tokens[index].meta.get("repository")
        if repository is not None and repository_stars is not None:
            count = repository_stars.get(repository)
            label = f"{count:,} ⭐" if count is not None else "stars unavailable"
            result += f' <span class="repo-stars">({label})</span>'
        return result

    markdown.add_render_rule("link_close", close_link)
    tokens = markdown.parse(source)
    # The page template supplies the title from the category list.
    if tokens and tokens[0].type == "heading_open" and tokens[0].tag == "h1":
        tokens = tokens[3:]
    sections = []
    used_ids = {"top", "main-content", "report-title"}
    for index, token in enumerate(tokens):
        if token.type not in {"heading_open", "heading_close"}:
            continue
        if token.tag == "h1":
            token.tag = "h2"
        if token.type != "heading_open":
            continue
        inline = tokens[index + 1]
        label = "".join(
            child.content for child in inline.children or []
            if child.type in {"text", "code_inline", "image"}
        )
        base = slugify(label) or "section"
        anchor = base
        suffix = 2
        while anchor in used_ids:
            anchor = f"{base}-{suffix}"
            suffix += 1
        used_ids.add(anchor)
        token.attrSet("id", anchor)
        if token.tag == "h2":
            sections.append((anchor, label))
    # Annotate actual links after deriving navigation labels and stable heading IDs.
    # Markdown code examples and escaped embedded HTML are not links.
    for token in tokens:
        repository = None
        for child in token.children or []:
            if child.type == "link_open":
                repository = repository_key(child.attrGet("href") or "")
            elif child.type == "link_close":
                if repository is not None:
                    child.meta["repository"] = repository
                repository = None
    return markdown.renderer.render(tokens, markdown.options, {}), sections


def page(title: str, description: str, body: str, *, report: bool = False) -> str:
    prefix = "../" if report else ""
    return f'''<!doctype html>
<html lang="en">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GOOGLE_ANALYTICS_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GOOGLE_ANALYTICS_ID}');
  </script>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="color-scheme" content="light">
  <title>{escape(title)} · Good GitHub</title>
  <link rel="stylesheet" href="{prefix}assets/styles.css">
</head>
<body id="top">
  <a class="skip-link" href="#main-content">Skip to content</a>
  <header class="site-header wrap">
    <a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true">G.</span>Good GitHub</a>
    <a class="header-link" href="{prefix}index.html#clusters">Browse clusters <span aria-hidden="true">↗</span></a>
  </header>
  {body}
  <footer class="site-footer wrap"><span>Good GitHub <span class="footer-dot">/</span> A field guide to software engineering</span><a href="#top">Back to top ↑</a></footer>
</body>
</html>
'''


def render_home(clusters: list[Cluster]) -> str:
    categories = [category for cluster in clusters for category in cluster.categories]
    available = sum(category.content is not None for category in categories)
    sections = []
    for number, cluster in enumerate(clusters, 1):
        links = []
        for category in cluster.categories:
            status = "Read report" if category.content is not None else "Report pending"
            state = "ready" if category.content is not None else "pending"
            links.append(f'''<li><a class="category-link {state}" href="reports/{category.slug}.html">
              <span class="category-name">{escape(category.name)}</span>
              <span class="category-status">{status}<span aria-hidden="true">↗</span></span>
            </a></li>''')
        count = len(cluster.categories)
        category_label = "category" if count == 1 else "categories"
        sections.append(f'''<details class="cluster" id="cluster-{cluster.slug}">
          <summary><span class="cluster-number" aria-hidden="true">{number:02d}</span>
            <span class="cluster-info"><span class="cluster-name">{escape(cluster.name)}</span><span class="cluster-meta">{count} {category_label}</span></span>
            <span class="cluster-toggle" aria-hidden="true"></span>
          </summary>
          <ul class="category-list">{"".join(links)}</ul>
        </details>''')
    pending = len(categories) - available
    report_status = f"{available} reports available" + (f" · {pending} pending" if pending else "")
    body = f'''<main id="main-content" class="wrap">
      <section class="hero" aria-labelledby="home-title">
        <div><p class="eyebrow">The software engineering reading room</p>
          <h1 id="home-title">A field guide to<br><em>code worth reading.</em></h1>
          <p class="hero-description">Explore software by the problems it solves. Each report connects GitHub repositories with the engineering ideas, implementation details, and design decisions worth studying.</p>
        </div>
        <dl class="site-stats"><div><dt>Clusters to explore</dt><dd>{len(clusters)}</dd></div><div><dt>Categories</dt><dd>{len(categories)}</dd></div></dl>
      </section>
      <section id="clusters" class="catalog" aria-labelledby="catalog-title">
        <div class="catalog-heading"><h2 id="catalog-title">Explore by cluster</h2><p>{report_status}</p></div>
        <p class="catalog-hint">Expand a cluster to browse its categories.</p>
        {"".join(sections)}
      </section>
    </main>'''
    return page("Explore the collection", "Explore software engineering clusters, categories, and reports with links to GitHub repositories.", body)


def render_category(category: Category, repository_stars: dict[str, int] | None = None) -> str:
    if category.content is None:
        article = '<div class="empty-state"><p class="eyebrow">Report pending</p><h2>This reading list is still taking shape.</h2><p>A report for this category is not available yet. Explore the other categories in the collection.</p><a class="text-link" href="../index.html#clusters">Browse all clusters →</a></div>'
        sections = []
    else:
        article, sections = render_report(category.content, repository_stars)
    contents = "".join(f'<li><a href="#{anchor}">{escape(label)}</a></li>' for anchor, label in sections)
    navigation = f'<nav aria-label="Report sections"><p class="eyebrow">In this report</p><ul>{contents}</ul></nav>' if sections else ''
    body = f'''<main id="main-content" class="wrap report-layout">
      <aside class="report-sidebar"><a class="back-link" href="../index.html#clusters">← All clusters</a>{navigation}</aside>
      <article class="report" aria-labelledby="report-title">
        <header class="report-header"><p class="eyebrow">Category report</p><h1 id="report-title">{escape(category.name)}</h1></header>
        <div class="prose">{article}</div>
        <div class="report-end"><span>Continue exploring</span><a href="../index.html#clusters">Back to the collection →</a></div>
      </article>
    </main>'''
    return page(category.name, f"Software engineering reading guide: {category.name}.", body, report=True)


def render_sitemap(categories: list[Category]) -> str:
    sitemap = ElementTree.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    urls = [f"{SITE_URL}/"] + [
        f"{SITE_URL}/reports/{category.slug}.html"
        for category in categories if category.content is not None
    ]
    for url in urls:
        entry = ElementTree.SubElement(sitemap, "url")
        ElementTree.SubElement(entry, "loc").text = url
    ElementTree.indent(sitemap, space="  ")
    return ElementTree.tostring(sitemap, encoding="utf-8", xml_declaration=True).decode("utf-8") + "\n"


def build(clusters_path: Path, reports_dir: Path, output_dir: Path,
          metadata_dir: Path = ROOT / "repo-metadata") -> tuple[int, int]:
    clusters_path = clusters_path.resolve()
    reports_dir = reports_dir.resolve()
    metadata_dir = metadata_dir.resolve()
    if output_dir.is_symlink():
        raise ValueError("The output directory must not be a symbolic link.")
    output_dir = output_dir.resolve()
    # Never replace inputs or the generator, even if a build marker was copied there.
    for source in (clusters_path, reports_dir, metadata_dir, Path(__file__).resolve(), ROOT / "site_assets"):
        if source == output_dir or output_dir in source.parents:
            raise ValueError(f"Output directory would overwrite an input: {source}")
    if any(source in output_dir.parents for source in (reports_dir, metadata_dir, ROOT / "site_assets")):
        raise ValueError("Output directory must be outside the input directories.")
    if output_dir.exists():
        if not output_dir.is_dir():
            raise ValueError(f"Output path is not a directory: {output_dir}")
        marker = output_dir / MARKER
        if any(output_dir.iterdir()) and (not marker.is_file() or marker.read_text() != MARKER_CONTENT):
            raise ValueError(f"Refusing to replace non-generated content in {output_dir}; choose an empty output directory.")
    clusters = read_clusters(clusters_path, reports_dir)
    repository_stars = read_repository_stars(metadata_dir)
    categories = [category for cluster in clusters for category in cluster.categories]
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    # Render everything before replacing an earlier build, so invalid inputs leave it intact.
    with tempfile.TemporaryDirectory(prefix=".good-github-build-", dir=output_dir.parent) as temporary:
        staging = Path(temporary) / "site"
        (staging / "reports").mkdir(parents=True)
        (staging / "assets").mkdir()
        shutil.copyfile(ROOT / "site_assets" / "styles.css", staging / "assets" / "styles.css")
        (staging / "index.html").write_text(render_home(clusters), encoding="utf-8")
        for category in categories:
            (staging / "reports" / f"{category.slug}.html").write_text(render_category(category, repository_stars), encoding="utf-8")
        (staging / "sitemap.xml").write_text(render_sitemap(categories), encoding="utf-8")
        (staging / "robots.txt").write_text(
            f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8",
        )
        (staging / MARKER).write_text(MARKER_CONTENT, encoding="utf-8")
        if output_dir.exists():
            shutil.rmtree(output_dir)
        staging.rename(output_dir)
    return len(categories), sum(category.content is not None for category in categories)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clusters", type=Path, default=ROOT / "clusters.md", help="Markdown cluster headings and category lists (default: clusters.md beside this script)")
    parser.add_argument("--reports", type=Path, default=ROOT / "repo-research", help="Directory of Markdown reports (default: repo-research beside this script)")
    parser.add_argument("--metadata", type=Path, default=ROOT / "repo-metadata", help="Saved GitHub metadata directory used for star counts (default: repo-metadata beside this script)")
    parser.add_argument("--output", type=Path, default=ROOT / "dist", help="Generated site directory (default: dist beside this script)")
    args = parser.parse_args()
    try:
        total, available = build(args.clusters, args.reports, args.output, args.metadata)
    except (OSError, ValueError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1
    print(f"Built {total} category pages: {available} reports, {total - available} pending.")
    print(f"Open {args.output.resolve() / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
