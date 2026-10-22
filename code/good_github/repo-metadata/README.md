# Website repository metadata

This directory contains the saved GitHub repository responses used by the website generator to display star counts:

```text
repo-metadata/
  OWNER/
    REPO/
      metadata.json
```

`build_site.py` reads every `OWNER/REPO/metadata.json` file. Each must contain a valid repository `html_url` and a nonnegative integer `stargazers_count`. The generator recognizes both the directory's owner/repository name and the canonical repository URL, ignoring case.

Star counts are local snapshots. Building or browsing the website does not fetch GitHub API data. Repository links without a matching snapshot display `(stars unavailable)`.

Update the saved snapshots and rebuild the website to refresh displayed counts. Collection scripts, logs, language snapshots, and fetch records are not part of the website source.
