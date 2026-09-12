#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
from urllib.parse import urljoin


EXCLUDE_FILES = {
    "404.html",
    "search.html",
    "sitemap.xml",
}


def should_include(path: Path) -> bool:
    # Only HTML pages
    if path.suffix.lower() != ".html":
        return False

    # Exclude common non-content pages
    if path.name in EXCLUDE_FILES:
        return False

    # Exclude theme/plugin assets directories if they ever contain html (rare)
    parts = {p.lower() for p in path.parts}
    if "assets" in parts:
        return False

    return True


def is_redirect_stub(path: Path) -> bool:
    """True for the meta-refresh pages emitted by mkdocs-redirects.

    These live at the old URL of a moved page and exist only to forward
    visitors to its new home, so listing them in the sitemap would tell
    search engines the retired URLs are still canonical content.
    """
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:2048].lower()
    except OSError:
        return False
    return 'http-equiv="refresh"' in head or "http-equiv='refresh'" in head


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sitemap.xml from MkDocs site/ output.")
    parser.add_argument("--site-dir", required=True, help="Path to built site directory (e.g. site)")
    parser.add_argument("--site-url", required=True, help="Public site root URL (e.g. https://example.com/)")
    parser.add_argument("--output", default="sitemap.xml", help="Output filename inside site-dir (default: sitemap.xml)")
    args = parser.parse_args()

    site_dir = Path(args.site_dir).resolve()
    if not site_dir.is_dir():
        raise SystemExit(f"--site-dir does not exist or is not a directory: {site_dir}")

    site_url = args.site_url
    if not site_url.endswith("/"):
        site_url += "/"

    # Collect URLs
    html_files: list[Path] = []
    redirect_stubs = 0
    for p in site_dir.rglob("*.html"):
        rel = p.relative_to(site_dir)
        if not should_include(rel):
            continue
        if is_redirect_stub(p):
            redirect_stubs += 1
            continue
        html_files.append(rel)

    # Deterministic ordering
    html_files.sort(key=lambda p: str(p).lower())

    today = dt.date.today().isoformat()

    # Build sitemap XML (simple and valid)
    lines: list[str] = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for rel in html_files:
        # MkDocs output uses .../index.html for directories; canonical URL should be .../ (no index.html)
        rel_posix = rel.as_posix()
        if rel_posix.endswith("/index.html"):
            loc_path = rel_posix[: -len("index.html")]
        elif rel_posix == "index.html":
            loc_path = ""
        else:
            loc_path = rel_posix

        loc = urljoin(site_url, loc_path)
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append("  </url>")

    lines.append("</urlset>")
    xml = "\n".join(lines) + "\n"

    out_path = site_dir / args.output
    out_path.write_text(xml, encoding="utf-8")
    print(f"Wrote {out_path} ({len(html_files)} URLs, {redirect_stubs} redirect stubs skipped)")


if __name__ == "__main__":
    main()
