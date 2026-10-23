# Good GitHub

Build a static reading guide from `clusters.md` and Markdown research reports.

Run from this directory with Python 3.10+ and [uv](https://docs.astral.sh/uv/):

```sh
uv run build_site.py
```

`uv` installs the pinned Markdown renderer automatically on the first run. Alternatively, use a regular Python environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 build_site.py
```

Open `dist/index.html` directly in a browser, or preview over HTTP:

```sh
python3 -m http.server 8000 --directory dist
```

Visit <http://localhost:8000>. Upload the entire `dist` folder to any static host. The content and cluster navigation use plain HTML and CSS and work without JavaScript. Every page also includes the asynchronous Google Analytics tag for measurement ID `G-SLF19PMTRF`, configured in the generator's shared page template. Reports retain their original GitHub and documentation links.

## Inputs and output

- `clusters.md`: `##` headings name clusters, with a bulleted or numbered list of categories below each heading. An optional `#` document title and blank lines are ignored. Leading numbers in cluster headings (such as `## 1. Databases and Search`) are removed from the displayed names. Cluster and category order follow this file.
- `repo-research/<category-slug>.md`: the report for each category. Slugs use lowercase words with punctuation replaced by hyphens. For example, `HTTP client libraries` maps to `http-client-libraries.md`.
- `site_assets/styles.css` and `site_assets/favicon.svg`: the shared stylesheet and site icon, copied into the generated site.
- `repo-metadata/<owner>/<repo>/metadata.json`: saved GitHub API responses. Repository links display `stargazers_count` after the link, for example `(1,234 ⭐)`. Counts are snapshots, read locally at build time; no browser or build-time API calls are needed. Both the listed directory name and canonical `html_url` are recognized, ignoring case. Repository links without saved metadata display `(stars unavailable)`; links to source files, issues, and other subpages remain unchanged.
- `dist/index.html`: an index of expandable clusters. Each cluster starts collapsed; click its name or focus it and press Enter/Space to reveal links to its category reports. Multiple clusters can stay open. This uses native HTML `<details>` elements and works without JavaScript.
- `dist/clusters/<cluster-slug>.html`: one overview page per cluster, listing its reports with a short description, repository count, and research date, plus links to the neighboring clusters. The homepage links each cluster panel to its overview.
- `dist/reports/<category-slug>.html`: full reports with section navigation, breadcrumbs, and links to the other reports in the same cluster, or a clearly marked pending page when the report is missing or empty.
- `dist/404.html`: the not-found page. It uses root-relative links because CloudFront serves it for any missing path.
- `dist/sitemap.xml`: the homepage, cluster pages, and reports with content, using absolute `https://goodgithub.com` URLs and `lastmod` dates. Pending pages are omitted.
- `dist/robots.txt`: allows crawling and advertises the sitemap.

## Search metadata

Every page has a canonical `https://goodgithub.com` URL, Open Graph and Twitter card tags, and schema.org JSON-LD: `WebSite` on the homepage, `CollectionPage` with breadcrumbs on cluster pages, and `Article`, `BreadcrumbList`, and an `ItemList` of the featured repositories on reports. Pending reports and `404.html` are marked `noindex`.

Report titles and descriptions are derived from the Markdown. The research date comes from the first `Research date: YYYY-MM-DD` line (bold dates are accepted) and becomes the article date and sitemap `lastmod`. Featured repositories are the H3 headings whose first link is a GitHub repository, such as `### 1. [owner/repo](https://github.com/owner/repo)`, in order and without duplicates. Their count goes into the title (`Time-series databases: 24 Open-Source Repos to Study`), and the first three names go into the meta description. A report without such headings falls back to a generic description and its plain category name as the title.

The Markdown renderer supports headings, links, emphasis, lists, code blocks, tables, and strikethrough. Embedded HTML is displayed as text. The first Markdown H1 is replaced with the category name from the list.

Example cluster input:

```markdown
# Category Clusters

## 1. Databases and Search

- Embedded relational databases
- Relational database servers

## 2. Networking and Communication

- HTTP client libraries
```

To use different inputs or a different output folder:

```sh
uv run build_site.py --clusters path/to/clusters.md --reports path/to/reports --metadata path/to/repo-metadata --output dist
```

Default paths are relative to the script, so the command also works from other directories. Explicit paths are relative to your current working directory. `clusters.md` is the source of both the cluster list and the category list. Reports not listed in a cluster are ignored. Duplicate cluster or category slugs, empty clusters, and malformed entries fail the build with an explanatory error.

Rerun the command after editing clusters, reports, or saved metadata. The metadata directory must contain valid repository snapshots with nonnegative integer star counts. It rebuilds the generated folder, including removing obsolete pages. The builder marks its output with `.good-github-site` and refuses to replace nonempty folders without this marker. Keep hand-written files outside the generated folder. Input or rendering errors leave an earlier build intact.

## Verification

```sh
uv run --with markdown-it-py==4.0.0 python -m unittest discover -s tests -v
```

## AWS deployment

The [Terraform infrastructure and deployment guide](infra/README.md) configure `goodgithub.com` and `www.goodgithub.com` with the private `ilyaraz-good-github` S3 bucket in `us-east-1`, CloudFront, Route 53, and ACM. Start with the foundation in `infra/bootstrap`, delegate DNS at Namecheap, then deploy the website configuration in `infra`.
