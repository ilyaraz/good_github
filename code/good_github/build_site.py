#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py==4.0.0"]
# ///
"""Turn category clusters and Markdown reports into a portable static website."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date
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
SITE_NAME = "Good GitHub"
HOME_TITLE = "Good GitHub: Open-Source Codebases Worth Reading, by Topic"
RESEARCH_DATE = re.compile(r"^Research date:\s*\**(\d{4}-\d{2}-\d{2})\b", re.M)
# Report entries are H3 headings such as "### 1. [owner/repo](https://github.com/owner/repo)".
REPOSITORY_HEADING = re.compile(r"^###\s+(?:\d+[.)]\s+)?[^\n\[]*\[([^\]\n]+)\]\(([^)\s]+)\)", re.M)


@dataclass
class Category:
    name: str
    slug: str
    content: str | None
    research_date: str | None = None
    repositories: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class Cluster:
    name: str
    slug: str
    categories: list[Category]


def slugify(value: str) -> str:
    """Match the report filenames: lowercase words separated by hyphens."""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


PROPER_NOUNS = {"Fourier", "Unicode"}
# Repository names that say little without their owner, such as MariaDB/server.
GENERIC_REPOSITORY_NAMES = {"app", "core", "engine", "lib", "main", "plot", "runtime", "sdk", "server", "src", "text", "view"}


def mid_sentence(value: str) -> str:
    """Lowercase capitalized words for use mid-sentence, keeping acronyms such as "HTTP" and "WebAssembly"."""
    return re.sub(r"\b[A-Z][a-z]+\b", lambda word: word[0] if word[0] in PROPER_NOUNS else word[0].lower(), value)


def report_facts(content: str) -> tuple[str | None, list[tuple[str, str]]]:
    """Find the research date and the featured repositories (label, URL) in a report."""
    match = RESEARCH_DATE.search(content)
    research_date = None
    if match:
        try:
            research_date = date.fromisoformat(match[1]).isoformat()
        except ValueError:
            pass
    repositories = []
    seen = set()
    for label, url in REPOSITORY_HEADING.findall(content):
        key = repository_key(url)
        if key is not None and key not in seen:
            seen.add(key)
            repositories.append((re.sub(r"[*`]", "", label).strip() or key, url))
    return research_date, repositories


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
        category = Category(name, slug, content if content and content.strip() else None)
        if category.content is not None:
            category.research_date, category.repositories = report_facts(category.content)
        clusters[-1].categories.append(category)
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
    used_ids = {"top", "main-content", "report-title", "related-title"}
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


def json_ld(data: dict) -> str:
    # Escape "<" so report text can never close the script element.
    source = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{source}</script>'


def page(title: str, description: str, body: str, *, prefix: str = "", path: str | None = None,
         page_type: str = "website", structured_data: dict | None = None, indexable: bool = True) -> str:
    """Wrap a page body. `path` is the canonical URL path; pages without one are not shared or indexed."""
    head = [f'<meta name="description" content="{escape(description, quote=True)}">']
    if not indexable:
        head.append('<meta name="robots" content="noindex">')
    if path is not None:
        url = escape(f"{SITE_URL}/{path}", quote=True)
        head += [
            f'<link rel="canonical" href="{url}">',
            f'<meta property="og:site_name" content="{SITE_NAME}">',
            f'<meta property="og:type" content="{page_type}">',
            f'<meta property="og:title" content="{escape(title, quote=True)}">',
            f'<meta property="og:description" content="{escape(description, quote=True)}">',
            f'<meta property="og:url" content="{url}">',
            '<meta name="twitter:card" content="summary">',
        ]
    if structured_data is not None:
        head.append(json_ld(structured_data))
    head_tags = "\n  ".join(head)
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
  <title>{escape(title)}</title>
  {head_tags}
  <meta name="color-scheme" content="light">
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
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


def publisher() -> dict:
    return {"@type": "Organization", "name": SITE_NAME, "url": f"{SITE_URL}/"}


def breadcrumbs(trail: list[tuple[str, str | None]], prefix: str) -> tuple[str, dict]:
    """Render a visible breadcrumb trail and its schema.org equivalent; the last item is the current page."""
    items = []
    schema = []
    for position, (name, path) in enumerate(trail, 1):
        if position == len(trail):
            items.append(f'<li aria-current="page">{escape(name)}</li>')
        else:
            items.append(f'<li><a href="{prefix}{path or "index.html"}">{escape(name)}</a></li>')
        schema.append({"@type": "ListItem", "position": position, "name": name, "item": f"{SITE_URL}/{path or ''}"})
    html = f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'
    return html, {"@type": "BreadcrumbList", "itemListElement": schema}


def report_title(category: Category) -> str:
    count = len(category.repositories)
    noun = "Repo" if count == 1 else "Repos"
    return f"{category.name}: {count} Open-Source {noun} to Study" if count else category.name


def report_description(category: Category) -> str:
    topic = mid_sentence(category.name)
    if not category.repositories:
        return f"A reading guide to open-source {topic}: the design decisions worth studying and where to start reading the code."
    names = [label if label.split("/")[-1].lower() in GENERIC_REPOSITORY_NAMES else label.split("/")[-1]
             for label, _ in category.repositories[:3]]
    listed = ", ".join(names[:-1]) + f" and {names[-1]}" if len(names) > 1 else names[0]
    return (f"{len(category.repositories)} open-source {topic} worth studying, including {listed}. "
            "Design decisions, trade-offs and where to start reading the code.")


def cluster_description(cluster: Cluster) -> str:
    ready = [category for category in cluster.categories if category.content is not None]
    examples = ", ".join(mid_sentence(category.name) for category in ready[:3])
    noun = "guide" if len(ready) == 1 else "guides"
    return (f"{len(ready)} reading {noun} to open-source {mid_sentence(cluster.name)} on GitHub"
            + (f", covering {examples} and more." if examples else "."))


def report_link(category: Category, prefix: str) -> str:
    status = "Read report" if category.content is not None else "Report pending"
    state = "ready" if category.content is not None else "pending"
    return f'''<li><a class="category-link {state}" href="{prefix}reports/{category.slug}.html">
              <span class="category-name">{escape(category.name)}</span>
              <span class="category-status">{status}<span aria-hidden="true">↗</span></span>
            </a></li>'''


def render_home(clusters: list[Cluster]) -> str:
    categories = [category for cluster in clusters for category in cluster.categories]
    available = sum(category.content is not None for category in categories)
    sections = []
    for number, cluster in enumerate(clusters, 1):
        links = [report_link(category, "") for category in cluster.categories]
        count = len(cluster.categories)
        category_label = "category" if count == 1 else "categories"
        sections.append(f'''<details class="cluster" id="cluster-{cluster.slug}">
          <summary><span class="cluster-number" aria-hidden="true">{number:02d}</span>
            <span class="cluster-info"><span class="cluster-name">{escape(cluster.name)}</span><span class="cluster-meta">{count} {category_label}</span></span>
            <span class="cluster-toggle" aria-hidden="true"></span>
          </summary>
          <ul class="category-list">{"".join(links)}</ul>
          <p class="cluster-more"><a href="clusters/{cluster.slug}.html">Overview of {escape(cluster.name)} →</a></p>
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
    description = (f"A field guide to code worth reading: {available} reading guides that pick open-source GitHub "
                   "repositories by the problem they solve and explain the design decisions worth studying.")
    structured_data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": f"{SITE_URL}/",
        "description": description,
        "publisher": publisher(),
    }
    return page(HOME_TITLE, description, body, path="", structured_data=structured_data)


def render_cluster(cluster: Cluster, number: int, clusters: list[Cluster]) -> str:
    path = f"clusters/{cluster.slug}.html"
    trail, breadcrumb_schema = breadcrumbs([("Home", None), (cluster.name, path)], "../")
    items = []
    for category in cluster.categories:
        if category.content is None:
            continue
        details = [f"{len(category.repositories)} repositories"] if category.repositories else []
        if category.research_date:
            details.append(f'Researched <time datetime="{category.research_date}">{category.research_date}</time>')
        meta = f'<p class="report-item-meta">{" · ".join(details)}</p>' if details else ""
        items.append(f'''<li class="report-item"><h2><a href="../reports/{category.slug}.html">{escape(category.name)}</a></h2>
          <p>{escape(report_description(category))}</p>{meta}</li>''')
    if not items:
        items.append('<li class="report-item"><p>Reports for this cluster are still taking shape.</p></li>')
    pager = []
    if number > 1:
        pager.append(f'<a href="{clusters[number - 2].slug}.html">← {escape(clusters[number - 2].name)}</a>')
    if number < len(clusters):
        pager.append(f'<a href="{clusters[number].slug}.html">{escape(clusters[number].name)} →</a>')
    description = cluster_description(cluster)
    body = f'''<main id="main-content" class="wrap cluster-page">
      <header class="cluster-header">{trail}
        <p class="eyebrow">Cluster {number:02d} of {len(clusters):02d}</p>
        <h1 id="cluster-title">{escape(cluster.name)}</h1>
        <p class="hero-description">{escape(description)} Each report selects repositories worth studying and explains the engineering ideas and design decisions behind them.</p>
      </header>
      <ul class="report-list">{"".join(items)}</ul>
      <nav class="report-end" aria-label="Other clusters">{"".join(pager)}</nav>
    </main>'''
    structured_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": cluster.name,
                "description": description,
                "url": f"{SITE_URL}/{path}",
                "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": f"{SITE_URL}/"},
                "hasPart": [
                    {"@type": "Article", "headline": category.name, "url": f"{SITE_URL}/reports/{category.slug}.html"}
                    for category in cluster.categories if category.content is not None
                ],
            },
            breadcrumb_schema,
        ],
    }
    return page(f"{cluster.name}: Open-Source Codebases to Study · {SITE_NAME}", description, body,
                prefix="../", path=path, structured_data=structured_data)


def render_category(category: Category, cluster: Cluster, repository_stars: dict[str, int] | None = None) -> str:
    path = f"reports/{category.slug}.html"
    cluster_path = f"clusters/{cluster.slug}.html"
    trail, breadcrumb_schema = breadcrumbs([("Home", None), (cluster.name, cluster_path), (category.name, path)], "../")
    if category.content is None:
        article = '<div class="empty-state"><p class="eyebrow">Report pending</p><h2>This reading list is still taking shape.</h2><p>A report for this category is not available yet. Explore the other categories in the collection.</p><a class="text-link" href="../index.html#clusters">Browse all clusters →</a></div>'
        sections = []
    else:
        article, sections = render_report(category.content, repository_stars)
    contents = "".join(f'<li><a href="#{anchor}">{escape(label)}</a></li>' for anchor, label in sections)
    navigation = f'<nav aria-label="Report sections"><p class="eyebrow">In this report</p><ul>{contents}</ul></nav>' if sections else ''
    related = [report_link(other, "../") for other in cluster.categories if other is not category and other.content is not None]
    related_section = f'''<section class="related" aria-labelledby="related-title">
          <h2 id="related-title">More in {escape(cluster.name)}</h2>
          <ul class="category-list">{"".join(related)}</ul>
        </section>''' if related else ""
    body = f'''<main id="main-content" class="wrap report-layout">
      <aside class="report-sidebar"><a class="back-link" href="../{cluster_path}">← {escape(cluster.name)}</a>{navigation}</aside>
      <article class="report" aria-labelledby="report-title">
        <header class="report-header">{trail}<p class="eyebrow">Category report</p><h1 id="report-title">{escape(category.name)}</h1></header>
        <div class="prose">{article}</div>
        {related_section}
        <div class="report-end"><span>Continue exploring</span><a href="../index.html#clusters">Back to the collection →</a></div>
      </article>
    </main>'''
    if category.content is None:
        return page(f"{category.name} · {SITE_NAME}", f"A reading guide to open-source {mid_sentence(category.name)} is in progress.",
                    body, prefix="../", path=path, indexable=False)
    description = report_description(category)
    article_schema = {
        "@type": "Article",
        "headline": category.name,
        "description": description,
        "url": f"{SITE_URL}/{path}",
        "mainEntityOfPage": f"{SITE_URL}/{path}",
        "author": publisher(),
        "publisher": publisher(),
        "articleSection": cluster.name,
    }
    if category.research_date:
        article_schema["datePublished"] = article_schema["dateModified"] = category.research_date
    graph = [article_schema, breadcrumb_schema]
    if category.repositories:
        graph.append({
            "@type": "ItemList",
            "name": f"{category.name}: repositories to study",
            "numberOfItems": len(category.repositories),
            "itemListElement": [
                {"@type": "ListItem", "position": position, "name": label, "url": url}
                for position, (label, url) in enumerate(category.repositories, 1)
            ],
        })
    return page(f"{report_title(category)} · {SITE_NAME}", description, body, prefix="../", path=path,
                page_type="article", structured_data={"@context": "https://schema.org", "@graph": graph})


def render_not_found() -> str:
    # Served for any missing path, so asset and page links are root-relative.
    body = '''<main id="main-content" class="wrap not-found">
      <div class="empty-state"><p class="eyebrow">Page not found</p><h1>This page is not in the collection.</h1>
        <p>The link may be mistyped, or the report may have moved. Browse the clusters to find what you were looking for.</p>
        <a class="text-link" href="/index.html#clusters">Browse all clusters →</a></div>
    </main>'''
    return page(f"Page not found · {SITE_NAME}", "This page is not in the Good GitHub collection.", body,
                prefix="/", indexable=False)


def render_sitemap(clusters: list[Cluster]) -> str:
    sitemap = ElementTree.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    entries = []
    for cluster in clusters:
        ready = [category for category in cluster.categories if category.content is not None]
        dates = [category.research_date for category in ready if category.research_date]
        entries.append((f"{SITE_URL}/clusters/{cluster.slug}.html", max(dates, default=None)))
        entries += [(f"{SITE_URL}/reports/{category.slug}.html", category.research_date) for category in ready]
    newest = max((modified for _, modified in entries if modified), default=None)
    for url, modified in [(f"{SITE_URL}/", newest)] + entries:
        entry = ElementTree.SubElement(sitemap, "url")
        ElementTree.SubElement(entry, "loc").text = url
        if modified:
            ElementTree.SubElement(entry, "lastmod").text = modified
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
        (staging / "clusters").mkdir()
        (staging / "assets").mkdir()
        for asset in ("styles.css", "favicon.svg"):
            shutil.copyfile(ROOT / "site_assets" / asset, staging / "assets" / asset)
        (staging / "index.html").write_text(render_home(clusters), encoding="utf-8")
        (staging / "404.html").write_text(render_not_found(), encoding="utf-8")
        for number, cluster in enumerate(clusters, 1):
            (staging / "clusters" / f"{cluster.slug}.html").write_text(render_cluster(cluster, number, clusters), encoding="utf-8")
            for category in cluster.categories:
                (staging / "reports" / f"{category.slug}.html").write_text(render_category(category, cluster, repository_stars), encoding="utf-8")
        (staging / "sitemap.xml").write_text(render_sitemap(clusters), encoding="utf-8")
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
