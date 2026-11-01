"""
Tier 4: Real-World Application Workloads Test Suite.

Validates end-to-end site build, production artifacts, and full compliance:
1. Execution of static site build pipeline (python build.py)
2. Production artifact integrity in dist/ (non-empty files)
3. Full DOM parsing and validation of dist/index.html
4. Standalone trust page generation (privacy, terms, about, contact, disclaimer)
5. Sitemap XML compliance against W3C/Google protocol 0.9 standards
6. Robots.txt compliance against RFC 9309
7. LLM indexing guide (llms.txt) Markdown structure
8. Complete Schema.org JSON-LD graph integrity
9. Static asset reference resolution (banner, favicon)
10. End-to-end dataset fidelity (all non-expired CSV records present)
"""
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import build

DIST_DIR = PROJECT_ROOT / "dist"
BUILD_SCRIPT = PROJECT_ROOT / "build.py"
DATA_CSV = PROJECT_ROOT / "data_example.csv"


class TestRealWorldWorkloads(unittest.TestCase):
    """Real-world end-to-end workload test cases."""

    def test_01_build_pipeline_execution(self):
        """TC-T4-LOAD-01: python build.py runs synchronously, returns 0, and produces output within 10s."""
        result = subprocess.run(
            [sys.executable, str(BUILD_SCRIPT)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"build.py exited with non-zero code {result.returncode}.\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}",
        )
        self.assertIn("Successfully generated", result.stdout, "build.py did not report successful generation.")

    def test_02_production_artifacts_exist_and_non_empty(self):
        """TC-T4-LOAD-02: Core production files in dist/ exist and are non-empty (>0 bytes)."""
        required_artifacts = [
            "index.html",
            "sitemap.xml",
            "robots.txt",
            "llms.txt",
            "banner.png",
            "referral.png",
        ]
        for filename in required_artifacts:
            path = DIST_DIR / filename
            self.assertTrue(path.exists(), f"Required artifact {filename} missing from dist/")
            size = path.stat().st_size
            self.assertGreater(size, 0, f"Artifact {filename} in dist/ is empty (0 bytes).")

    def test_03_index_html_dom_structure(self):
        """TC-T4-LOAD-03: Full DOM parsing of dist/index.html verifying semantic HTML5 layout."""
        index_path = DIST_DIR / "index.html"
        self.assertTrue(index_path.exists(), "dist/index.html does not exist.")
        content = index_path.read_text(encoding="utf-8")
        
        soup = BeautifulSoup(content, "html.parser")
        self.assertIsNotNone(soup.find("html"), "Missing <html> tag.")
        self.assertIsNotNone(soup.find("head"), "Missing <head> tag.")
        self.assertIsNotNone(soup.find("body"), "Missing <body> tag.")
        self.assertIsNotNone(soup.find("header"), "Missing semantic <header> tag.")
        self.assertIsNotNone(soup.find("main"), "Missing semantic <main> tag.")
        self.assertIsNotNone(soup.find("footer"), "Missing semantic <footer> tag.")

    def test_04_trust_pages_generation(self):
        """TC-T4-LOAD-04: Standalone trust pages (privacy, terms, about, contact, disclaimer) generated in dist/."""
        trust_pages = [
            "privacy.html",
            "terms.html",
            "about.html",
            "contact.html",
            "disclaimer.html",
        ]
        for page in trust_pages:
            path = DIST_DIR / page
            self.assertTrue(path.exists(), f"Trust page {page} missing from dist/.")
            content = path.read_text(encoding="utf-8")
            self.assertGreater(len(content), 100, f"Trust page {page} is too short or empty.")
            soup = BeautifulSoup(content, "html.parser")
            self.assertIsNotNone(soup.find("title"), f"Trust page {page} missing <title> tag.")
            self.assertIsNotNone(soup.find("footer"), f"Trust page {page} missing <footer> tag.")

    def test_05_sitemap_xml_strict_w3c_standards(self):
        """TC-T4-LOAD-05: Strict XML validation of dist/sitemap.xml against Protocol 0.9."""
        sitemap_path = DIST_DIR / "sitemap.xml"
        self.assertTrue(sitemap_path.exists())
        tree = ET.parse(sitemap_path)
        root = tree.getroot()

        self.assertIn("sitemaps.org/schemas/sitemap/0.9", root.tag)
        urls = root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        self.assertGreaterEqual(len(urls), 1, "Sitemap contains 0 URLs.")

        for idx, u in enumerate(urls):
            loc = u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            self.assertIsNotNone(loc, f"URL entry #{idx} missing <loc> element.")
            self.assertTrue(loc.text.startswith("https://"), f"URL {loc.text} must use HTTPS.")

            lastmod = u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
            if lastmod is not None:
                self.assertRegex(lastmod.text, r"^\d{4}-\d{2}-\d{2}$", f"Invalid date: {lastmod.text}")

    def test_06_robots_txt_rfc9309_strict_parsing(self):
        """TC-T4-LOAD-06: Strict validation of dist/robots.txt against RFC 9309 rules."""
        robots_path = DIST_DIR / "robots.txt"
        self.assertTrue(robots_path.exists())
        lines = [l.strip() for l in robots_path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]

        has_ua = False
        has_sitemap = False
        for line in lines:
            self.assertIn(":", line, f"Invalid robots.txt syntax (missing colon): '{line}'")
            field, val = [part.strip() for part in line.split(":", 1)]
            if field.lower() == "user-agent":
                has_ua = True
            elif field.lower() == "sitemap":
                has_sitemap = True
                self.assertTrue(val.startswith("https://"), f"Sitemap URL must be HTTPS: {val}")

        self.assertTrue(has_ua, "robots.txt must contain User-agent directive.")
        self.assertTrue(has_sitemap, "robots.txt must contain Sitemap directive.")

    def test_07_llms_txt_markdown_structure(self):
        """TC-T4-LOAD-07: dist/llms.txt conforms to structured markdown format for AI models."""
        llms_path = DIST_DIR / "llms.txt"
        self.assertTrue(llms_path.exists(), "dist/llms.txt does not exist.")
        content = llms_path.read_text(encoding="utf-8")

        self.assertTrue(content.startswith("#"), "llms.txt must start with a markdown H1 (#).")
        self.assertIn("Canonical", content, "llms.txt missing Canonical section.")
        self.assertIn("https://", content, "llms.txt must contain canonical HTTPS link.")

    def test_08_schema_json_ld_strict_graph_validation(self):
        """TC-T4-LOAD-08: Complete Schema.org JSON-LD graph integrity validation."""
        index_path = DIST_DIR / "index.html"
        soup = BeautifulSoup(index_path.read_text(encoding="utf-8"), "html.parser")
        script = soup.find("script", type="application/ld+json")
        self.assertIsNotNone(script, "Missing JSON-LD script.")
        
        data = json.loads(script.string)
        self.assertEqual(data.get("@context"), "https://schema.org")
        self.assertIn("@graph", data)
        graph = data["@graph"]

        types = {item.get("@type") for item in graph}
        self.assertIn("WebSite", types, "Schema missing WebSite entity.")
        self.assertTrue("CollectionPage" in types or "WebPage" in types, "Schema missing CollectionPage/WebPage.")
        self.assertIn("ItemList", types, "Schema missing ItemList entity.")
        self.assertIn("FAQPage", types, "Schema missing FAQPage entity.")

    def test_09_static_asset_references_resolve(self):
        """TC-T4-LOAD-09: All local images and icons referenced in index.html resolve to real files."""
        index_path = DIST_DIR / "index.html"
        soup = BeautifulSoup(index_path.read_text(encoding="utf-8"), "html.parser")

        # Check local image sources
        images = soup.find_all("img")
        for img in images:
            src = img.get("src", "")
            if not src.startswith("http") and not src.startswith("data:"):
                # Clean query strings if any
                src_clean = src.split("?")[0]
                asset_file = DIST_DIR / src_clean
                self.assertTrue(asset_file.exists(), f"Image src '{src}' referenced in HTML does not exist in dist/!")

        # Check favicon
        favicons = soup.find_all("link", rel=lambda r: r and "icon" in r)
        for fav in favicons:
            href = fav.get("href", "")
            if not href.startswith("http") and not href.startswith("data:"):
                href_clean = href.split("?")[0]
                asset_file = DIST_DIR / href_clean
                self.assertTrue(asset_file.exists(), f"Favicon href '{href}' does not exist in dist/!")

    def test_10_end_to_end_dataset_fidelity(self):
        """TC-T4-LOAD-010: Every non-expired record in the active data source is present in rendered index.html."""
        env_url = os.environ.get("GOOGLE_SHEET_CSV_URL")
        data_source = env_url if env_url else str(DATA_CSV)
        try:
            df = build._read_dataframe(data_source)
        except Exception:
            df = build._read_dataframe(str(DATA_CSV))

        df = build._normalize_columns(df)
        active_df = build._filter_expired(df)
        active_df = active_df[active_df["Service Name"].astype(str).str.strip() != ""]

        active_services = [s.strip() for s in active_df["Service Name"]]
        
        index_html = (DIST_DIR / "index.html").read_text(encoding="utf-8")
        soup = BeautifulSoup(index_html, "html.parser")
        rendered_services = [card.get("data-service", "").strip() for card in soup.find_all("article")]

        self.assertGreaterEqual(len(rendered_services), len(active_services), "Rendered card count less than active dataset count.")
        for service in active_services:
            self.assertIn(service, rendered_services, f"Active service '{service}' from dataset missing in rendered HTML cards!")


if __name__ == "__main__":
    unittest.main()
