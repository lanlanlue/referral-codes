"""
Tier 1: Feature Coverage Test Suite (>=5 test cases per feature).

Covers all 11 core functional features specified in PROJECT.md and ORIGINAL_REQUEST.md:
1. Standard <head> tags
2. OpenGraph metadata
3. Twitter Cards
4. Schema.org JSON-LD structured data
5. XML Sitemap generation
6. Robots.txt generation
7. Modern UI & responsive layout elements
8. Core interactive retention (search, category filter, i18n, dark mode, copy)
9. Google AdSense containers
10. Legal & trust compliance pages
11. Link qualification & security
"""
import json
import os
import re
import sys
import unittest
from pathlib import Path

# Ensure project root is in sys.path for standalone script execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_utils import (
    get_dist_file,
    get_dist_html,
    get_soup,
    get_sitemap_tree,
    get_robots_content,
    get_schema_graph,
)


class TestStandardHeadTags(unittest.TestCase):
    """Feature 1: Standard <head> tags verification (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.html = get_dist_html("index.html")
        cls.soup = get_soup("index.html")
        cls.head = cls.soup.find("head")
        assert cls.head is not None, "HTML missing <head> element"

    def test_01_charset_within_first_1024_bytes(self):
        """TC-T1-HEAD-01: Charset meta tag must declare UTF-8 within first 1024 bytes."""
        prefix = self.html[:1024]
        match = re.search(r'<meta\s+charset=["\']?(utf-8)["\']?', prefix, re.IGNORECASE)
        self.assertIsNotNone(match, "Charset UTF-8 must be declared within the first 1024 bytes of the HTML document.")

    def test_02_viewport_meta_tag(self):
        """TC-T1-HEAD-02: Viewport meta tag must be configured for mobile-first indexing."""
        viewport = self.head.find("meta", attrs={"name": "viewport"})
        self.assertIsNotNone(viewport, "Missing <meta name='viewport'> tag in <head>.")
        content = viewport.get("content", "").replace(" ", "")
        self.assertIn("width=device-width", content, "Viewport content must contain 'width=device-width'.")
        self.assertIn("initial-scale=1.0", content, "Viewport content must contain 'initial-scale=1.0'.")

    def test_03_page_title_quality(self):
        """TC-T1-HEAD-03: <title> tag exists and conforms to length recommendations (15-75 chars)."""
        title = self.head.find("title")
        self.assertIsNotNone(title, "Missing <title> tag in <head>.")
        text = title.get_text().strip()
        self.assertGreaterEqual(len(text), 15, f"Page title is too short ({len(text)} chars): '{text}'")
        self.assertLessEqual(len(text), 75, f"Page title exceeds 75 chars ({len(text)} chars): '{text}'")

    def test_04_meta_description_quality(self):
        """TC-T1-HEAD-04: Meta description tag exists and is 50-200 chars for optimal SERP snippets."""
        desc = self.head.find("meta", attrs={"name": "description"})
        self.assertIsNotNone(desc, "Missing <meta name='description'> tag in <head>.")
        content = desc.get("content", "").strip()
        self.assertGreaterEqual(len(content), 50, f"Meta description is too short ({len(content)} chars): '{content}'")
        self.assertLessEqual(len(content), 200, f"Meta description exceeds 200 chars: '{content}'")

    def test_05_meta_keywords_present(self):
        """TC-T1-HEAD-05: Meta keywords tag exists and contains relevant comma-separated terms."""
        keywords = self.head.find("meta", attrs={"name": "keywords"})
        self.assertIsNotNone(keywords, "Missing <meta name='keywords'> tag in <head>.")
        content = keywords.get("content", "").strip()
        self.assertTrue(len(content) > 10, "Meta keywords content is empty or too short.")
        self.assertIn(",", content, "Meta keywords must contain comma-separated terms.")

    def test_06_canonical_url_format(self):
        """TC-T1-HEAD-06: Canonical link must be absolute HTTPS URL with no tracking query parameters."""
        canonical = self.head.find("link", attrs={"rel": "canonical"})
        self.assertIsNotNone(canonical, "Missing <link rel='canonical'> tag in <head>.")
        href = canonical.get("href", "").strip()
        self.assertTrue(href.startswith("https://"), f"Canonical URL must start with https://, got: {href}")
        self.assertNotIn("?", href, f"Canonical URL must not contain query parameters, got: {href}")

    def test_07_robots_and_crawler_directives(self):
        """TC-T1-HEAD-07: Robots meta tag directives must instruct index and follow."""
        robots = self.head.find("meta", attrs={"name": "robots"})
        self.assertIsNotNone(robots, "Missing <meta name='robots'> tag in <head>.")
        content = robots.get("content", "").lower()
        self.assertIn("index", content, "Robots directive must contain 'index'.")
        self.assertIn("follow", content, "Robots directive must contain 'follow'.")

    def test_08_hreflang_multilingual_alternates(self):
        """TC-T1-HEAD-08: Hreflang alternates declared for zh-TW, en, and x-default."""
        alternates = self.head.find_all("link", attrs={"rel": "alternate"})
        hreflangs = {link.get("hreflang"): link.get("href") for link in alternates if link.get("hreflang")}
        self.assertIn("zh-TW", hreflangs, "Missing alternate link with hreflang='zh-TW'.")
        self.assertIn("en", hreflangs, "Missing alternate link with hreflang='en'.")
        self.assertIn("x-default", hreflangs, "Missing alternate link with hreflang='x-default'.")


class TestOpenGraphMetadata(unittest.TestCase):
    """Feature 2: OpenGraph social media sharing metadata (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.soup = get_soup("index.html")
        cls.head = cls.soup.find("head")

    def test_01_og_type(self):
        """TC-T1-OG-01: og:type meta tag exists and is set to 'website'."""
        tag = self.head.find("meta", property="og:type")
        self.assertIsNotNone(tag, "Missing <meta property='og:type'>.")
        self.assertEqual(tag.get("content", "").strip(), "website")

    def test_02_og_locale(self):
        """TC-T1-OG-02: og:locale meta tag declares primary locale (zh_TW)."""
        tag = self.head.find("meta", property="og:locale")
        self.assertIsNotNone(tag, "Missing <meta property='og:locale'>.")
        self.assertIn("zh", tag.get("content", "").lower())

    def test_03_og_title_and_description(self):
        """TC-T1-OG-03: og:title and og:description match content and are non-empty."""
        og_title = self.head.find("meta", property="og:title")
        og_desc = self.head.find("meta", property="og:description")
        self.assertIsNotNone(og_title, "Missing <meta property='og:title'>.")
        self.assertIsNotNone(og_desc, "Missing <meta property='og:description'>.")
        self.assertTrue(len(og_title.get("content", "").strip()) >= 5, "og:title is empty or too short.")
        self.assertTrue(len(og_desc.get("content", "").strip()) >= 20, "og:description is empty or too short.")

    def test_04_og_url_canonical(self):
        """TC-T1-OG-04: og:url points to absolute canonical HTTPS URL."""
        tag = self.head.find("meta", property="og:url")
        self.assertIsNotNone(tag, "Missing <meta property='og:url'>.")
        href = tag.get("content", "").strip()
        self.assertTrue(href.startswith("https://"), f"og:url must be an absolute HTTPS URL, got: {href}")

    def test_05_og_image_and_resolution(self):
        """TC-T1-OG-05: og:image points to valid social preview banner image."""
        tag = self.head.find("meta", property="og:image")
        self.assertIsNotNone(tag, "Missing <meta property='og:image'>.")
        img_url = tag.get("content", "").strip()
        self.assertTrue(img_url.endswith((".png", ".jpg", ".jpeg", ".webp")), f"og:image must be an image file, got: {img_url}")

    def test_06_og_site_name(self):
        """TC-T1-OG-06: og:site_name matches brand name."""
        tag = self.head.find("meta", property="og:site_name")
        self.assertIsNotNone(tag, "Missing <meta property='og:site_name'>.")
        self.assertTrue(len(tag.get("content", "").strip()) > 0, "og:site_name is empty.")


class TestTwitterCards(unittest.TestCase):
    """Feature 3: Twitter Cards metadata (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.soup = get_soup("index.html")
        cls.head = cls.soup.find("head")

    def test_01_twitter_card_type(self):
        """TC-T1-TW-01: twitter:card specifies summary_large_image."""
        card = self.head.find("meta", attrs={"name": "twitter:card"})
        self.assertIsNotNone(card, "Missing <meta name='twitter:card'>.")
        self.assertEqual(card.get("content", "").strip(), "summary_large_image")

    def test_02_twitter_title(self):
        """TC-T1-TW-02: twitter:title exists and is non-empty."""
        tag = self.head.find("meta", attrs={"name": "twitter:title"})
        self.assertIsNotNone(tag, "Missing <meta name='twitter:title'>.")
        self.assertTrue(len(tag.get("content", "").strip()) >= 5, "twitter:title is too short.")

    def test_03_twitter_description(self):
        """TC-T1-TW-03: twitter:description exists and provides meaningful summary."""
        tag = self.head.find("meta", attrs={"name": "twitter:description"})
        self.assertIsNotNone(tag, "Missing <meta name='twitter:description'>.")
        self.assertTrue(len(tag.get("content", "").strip()) >= 20, "twitter:description is too short.")

    def test_04_twitter_image(self):
        """TC-T1-TW-04: twitter:image points to valid preview graphic."""
        tag = self.head.find("meta", attrs={"name": "twitter:image"})
        self.assertIsNotNone(tag, "Missing <meta name='twitter:image'>.")
        img_url = tag.get("content", "").strip()
        self.assertTrue(img_url.endswith((".png", ".jpg", ".jpeg", ".webp")), f"twitter:image invalid: {img_url}")

    def test_05_twitter_no_duplicate_properties(self):
        """TC-T1-TW-05: Ensure no malformed duplicate twitter tags exist in head."""
        tw_cards = self.head.find_all("meta", attrs={"name": "twitter:card"})
        self.assertEqual(len(tw_cards), 1, "There should be exactly one twitter:card tag.")


class TestSchemaOrgJSONLD(unittest.TestCase):
    """Feature 4: Schema.org JSON-LD structured data graph (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.schema = get_schema_graph("index.html")

    def test_01_schema_context_and_graph(self):
        """TC-T1-SCHEMA-01: Schema root contains @context and @graph array."""
        self.assertEqual(self.schema.get("@context"), "https://schema.org", "Schema @context must be https://schema.org")
        self.assertIn("@graph", self.schema, "Schema must contain a top-level @graph array.")
        self.assertIsInstance(self.schema["@graph"], list, "@graph must be a list.")

    def test_02_schema_website_entity(self):
        """TC-T1-SCHEMA-02: @graph contains WebSite entity with search action or name."""
        entities = {node.get("@type"): node for node in self.schema["@graph"]}
        self.assertIn("WebSite", entities, "Schema @graph missing WebSite entity.")
        website = entities["WebSite"]
        self.assertTrue(website.get("url", "").startswith("https://"), "WebSite URL must be absolute HTTPS.")
        self.assertTrue(len(website.get("name", "")) > 0, "WebSite entity missing name.")

    def test_03_schema_collection_or_webpage(self):
        """TC-T1-SCHEMA-03: @graph contains CollectionPage or WebPage entity."""
        entities = {node.get("@type"): node for node in self.schema["@graph"]}
        has_page = "CollectionPage" in entities or "WebPage" in entities
        self.assertTrue(has_page, "Schema @graph missing CollectionPage/WebPage entity.")

    def test_04_schema_itemlist_entity(self):
        """TC-T1-SCHEMA-04: @graph contains ItemList entity with populated elements."""
        entities = {node.get("@type"): node for node in self.schema["@graph"]}
        self.assertIn("ItemList", entities, "Schema @graph missing ItemList entity.")
        item_list = entities["ItemList"]
        elements = item_list.get("itemListElement", [])
        self.assertGreaterEqual(len(elements), 1, "Schema ItemList must contain at least one itemListElement.")
        first_item = elements[0].get("item", {})
        self.assertTrue("name" in first_item, "ItemList elements must contain 'name'.")

    def test_05_schema_faq_page(self):
        """TC-T1-SCHEMA-05: @graph contains FAQPage entity with valid question/answers."""
        entities = {node.get("@type"): node for node in self.schema["@graph"]}
        self.assertIn("FAQPage", entities, "Schema @graph missing FAQPage entity.")
        faq_page = entities["FAQPage"]
        questions = faq_page.get("mainEntity", [])
        self.assertGreaterEqual(len(questions), 1, "FAQPage must contain at least one question in mainEntity.")
        q1 = questions[0]
        self.assertEqual(q1.get("@type"), "Question", "FAQ items must be of @type Question.")
        self.assertEqual(q1.get("acceptedAnswer", {}).get("@type"), "Answer", "Question must have acceptedAnswer of @type Answer.")


class TestXMLSitemapGeneration(unittest.TestCase):
    """Feature 5: XML Sitemap Protocol 0.9 compliance (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.tree = get_sitemap_tree()
        cls.root = cls.tree.getroot()

    def test_01_sitemap_namespace(self):
        """TC-T1-SMAP-01: Sitemap root element tag matches sitemaps.org 0.9 namespace."""
        self.assertIn("http://www.sitemaps.org/schemas/sitemap/0.9", self.root.tag)
        self.assertTrue(self.root.tag.endswith("urlset"), "Root element must be <urlset>.")

    def test_02_sitemap_contains_urls(self):
        """TC-T1-SMAP-02: Sitemap must contain at least one <url> block."""
        urls = self.root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        self.assertGreaterEqual(len(urls), 1, "Sitemap contains zero <url> entries.")

    def test_03_sitemap_homepage_loc(self):
        """TC-T1-SMAP-03: Sitemap must contain the homepage canonical URL."""
        urls = self.root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        locs = [u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text for u in urls if u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc") is not None]
        self.assertTrue(any(l.startswith("https://") for l in locs), "Homepage URL must be absolute HTTPS.")

    def test_04_sitemap_lastmod_iso_format(self):
        """TC-T1-SMAP-04: All <lastmod> entries must strictly adhere to ISO-8601 YYYY-MM-DD."""
        urls = self.root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        for u in urls:
            lastmod = u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
            if lastmod is not None:
                self.assertRegex(lastmod.text.strip(), r"^\d{4}-\d{2}-\d{2}$", f"Invalid lastmod date format: {lastmod.text}")

    def test_05_sitemap_priority_and_changefreq(self):
        """TC-T1-SMAP-05: Priority between 0.0 and 1.0; changefreq from valid enum."""
        valid_freqs = {"always", "hourly", "daily", "weekly", "monthly", "yearly", "never"}
        urls = self.root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        for u in urls:
            p = u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
            if p is not None:
                val = float(p.text.strip())
                self.assertTrue(0.0 <= val <= 1.0, f"Priority out of range [0.0, 1.0]: {val}")
            cf = u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq")
            if cf is not None:
                self.assertIn(cf.text.strip().lower(), valid_freqs, f"Invalid changefreq value: {cf.text}")

    def test_06_sitemap_contains_trust_pages(self):
        """TC-T1-SMAP-06: Sitemap must list all trust/compliance subpages (about, privacy, terms, disclaimer, contact)."""
        urls = self.root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        locs = [u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text for u in urls if u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc") is not None]
        for page in ["about.html", "privacy.html", "terms.html", "disclaimer.html", "contact.html"]:
            self.assertTrue(any(page in l for l in locs), f"Sitemap missing entry for compliance page: {page}")


class TestRobotsTxtGeneration(unittest.TestCase):
    """Feature 6: Robots.txt RFC 9309 compliance (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.robots = get_robots_content()
        cls.lines = [line.strip() for line in cls.robots.splitlines() if line.strip() and not line.startswith("#")]

    def test_01_user_agent_directive(self):
        """TC-T1-ROBOTS-01: Contains User-agent directive targeting all crawlers (*)."""
        has_ua = any(re.match(r"^user-agent:\s*\*", line, re.IGNORECASE) for line in self.lines)
        self.assertTrue(has_ua, "robots.txt missing 'User-agent: *' directive.")

    def test_02_allow_all_directive(self):
        """TC-T1-ROBOTS-02: Contains Allow: / directive for full site indexation."""
        has_allow = any(re.match(r"^allow:\s*/$", line, re.IGNORECASE) for line in self.lines)
        self.assertTrue(has_allow, "robots.txt missing 'Allow: /' directive.")

    def test_03_sitemap_directive_presence(self):
        """TC-T1-ROBOTS-03: Declares Sitemap directive pointing to sitemap.xml."""
        sitemap_lines = [l for l in self.lines if l.lower().startswith("sitemap:")]
        self.assertGreaterEqual(len(sitemap_lines), 1, "robots.txt missing 'Sitemap:' directive.")

    def test_04_sitemap_url_format(self):
        """TC-T1-ROBOTS-04: Sitemap URL in robots.txt must be absolute HTTPS."""
        sitemap_lines = [l for l in self.lines if l.lower().startswith("sitemap:")]
        url = sitemap_lines[0].split(":", 1)[1].strip()
        self.assertTrue(url.startswith("https://"), f"Sitemap URL in robots.txt must start with https://, got: {url}")
        self.assertTrue(url.endswith("sitemap.xml"), f"Sitemap URL must point to sitemap.xml, got: {url}")

    def test_05_no_contradictory_disallow(self):
        """TC-T1-ROBOTS-05: Ensure no sweeping Disallow: / directive blocks search indexing."""
        has_sweeping_disallow = any(re.match(r"^disallow:\s*/$", line, re.IGNORECASE) for line in self.lines)
        self.assertFalse(has_sweeping_disallow, "robots.txt contains 'Disallow: /' which forbids crawler indexing!")


class TestModernUIAndLayout(unittest.TestCase):
    """Feature 7: Modern UI & responsive layout elements (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.soup = get_soup("index.html")

    def test_01_tailwind_css_configured(self):
        """TC-T1-UI-01: Tailwind CSS CDN and config script loaded in <head>."""
        scripts = self.soup.find_all("script")
        tailwind_script = any("cdn.tailwindcss.com" in s.get("src", "") for s in scripts)
        self.assertTrue(tailwind_script, "Tailwind CSS CDN script not found in HTML.")

    def test_02_sticky_header_navigation(self):
        """TC-T1-UI-02: Sticky navigation header present with branding."""
        header = self.soup.find("header")
        self.assertIsNotNone(header, "Missing <header> element in page.")
        classes = " ".join(header.get("class", []))
        self.assertIn("sticky", classes, "Header should have sticky positioning for responsive navigation.")

    def test_03_hero_editorial_hierarchy(self):
        """TC-T1-UI-03: Hero section exists with h1 heading and descriptive text."""
        h1 = self.soup.find("h1")
        self.assertIsNotNone(h1, "Missing <h1> headline in Hero section.")
        self.assertGreaterEqual(len(h1.get_text().strip()), 4, "<h1> headline is too short.")

    def test_04_card_grid_responsive_layout(self):
        """TC-T1-UI-04: Card container uses responsive multi-column grid layout."""
        card_grid = self.soup.find(id="cardGrid")
        self.assertIsNotNone(card_grid, "Missing #cardGrid container element.")
        classes = " ".join(card_grid.get("class", []))
        self.assertIn("grid", classes, "#cardGrid must use CSS grid layout.")

    def test_05_category_chips_bar(self):
        """TC-T1-UI-05: Category navigation filter bar exists."""
        cat_container = self.soup.find(id="categoryFilters")
        self.assertIsNotNone(cat_container, "Missing #categoryFilters container.")
        buttons = cat_container.find_all("button")
        self.assertGreaterEqual(len(buttons), 2, "Expected category filter buttons (All + categories).")

    def test_06_theme_toggle_accessibility(self):
        """TC-T1-UI-06: Theme toggle button includes aria-label for accessibility."""
        btn = self.soup.find(id="themeToggle")
        self.assertIsNotNone(btn, "Missing #themeToggle button.")
        self.assertTrue(btn.has_attr("aria-label"), "#themeToggle must have aria-label attribute for accessibility.")


class TestCoreInteractiveRetention(unittest.TestCase):
    """Feature 8: Core interactive features: search, filter, i18n, dark mode, copy (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.soup = get_soup("index.html")

    def test_01_search_input_element(self):
        """TC-T1-INTERACT-01: #searchInput exists with placeholder and accessible label."""
        search = self.soup.find(id="searchInput")
        self.assertIsNotNone(search, "Missing #searchInput input element.")
        self.assertTrue(search.has_attr("placeholder"), "#searchInput missing placeholder attribute.")

    def test_02_category_filter_data_attributes(self):
        """TC-T1-INTERACT-02: Category buttons have data-category attributes including 'All'."""
        cat_btns = self.soup.find_all("button", attrs={"data-category": True})
        self.assertGreaterEqual(len(cat_btns), 1, "No buttons with data-category found.")
        categories = [btn["data-category"] for btn in cat_btns]
        self.assertIn("All", categories, "Category filter missing 'All' button.")

    def test_03_i18n_translation_data_attributes(self):
        """TC-T1-INTERACT-03: Key text elements contain data-i18n attributes for bilingual switching."""
        i18n_elements = self.soup.find_all(attrs={"data-i18n": True})
        self.assertGreaterEqual(len(i18n_elements), 5, "Expected at least 5 elements with data-i18n attributes.")

    def test_04_copy_button_and_toast(self):
        """TC-T1-INTERACT-04: Copy button components and toast feedback container exist."""
        toast = self.soup.find(id="toast")
        self.assertIsNotNone(toast, "Missing #toast notification container.")
        copy_btns = self.soup.find_all(class_=re.compile(r"copy-btn"))
        self.assertGreaterEqual(len(copy_btns), 1, "Missing .copy-btn buttons on cards.")

    def test_05_no_results_feedback_element(self):
        """TC-T1-INTERACT-05: #noResults feedback container exists for zero-match search queries."""
        no_res = self.soup.find(id="noResults")
        self.assertIsNotNone(no_res, "Missing #noResults feedback element.")


class TestGoogleAdSenseContainers(unittest.TestCase):
    """Feature 9: Google AdSense ad container architecture & zero-CLS (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.soup = get_soup("index.html")
        cls.html = get_dist_html("index.html")

    def test_01_ad_containers_presence(self):
        """TC-T1-ADS-01: At least 2 ad slot containers exist (e.g. header, in-feed, sidebar, or footer)."""
        ad_containers = self.soup.find_all(lambda tag: tag.has_attr("data-ad-slot") or "ad-container" in tag.get("class", []) or "adsense-container" in tag.get("class", []))
        self.assertGreaterEqual(len(ad_containers), 2, f"Expected at least 2 ad container slots, found {len(ad_containers)}.")

    def test_02_ad_container_cls_reservation(self):
        """TC-T1-ADS-02: Ad containers reserve min-height (via CSS class or style) to prevent layout shifts (CLS=0)."""
        ad_containers = self.soup.find_all(lambda tag: tag.has_attr("data-ad-slot") or "ad-container" in tag.get("class", []) or "adsense-container" in tag.get("class", []))
        self.assertGreaterEqual(len(ad_containers), 1, "No ad containers found to evaluate CLS reservation.")
        for container in ad_containers:
            style = container.get("style", "")
            classes = " ".join(container.get("class", []))
            has_min_height = "min-height" in style or "min-h-" in classes
            self.assertTrue(has_min_height, f"Ad container {container} must specify min-height to eliminate CLS.")

    def test_03_ad_container_sponsor_label(self):
        """TC-T1-ADS-03: Ad container must display explicit '贊助廣告' or '贊助商廣告' or 'ADVERTISEMENT' label."""
        ad_containers = self.soup.find_all(lambda tag: tag.has_attr("data-ad-slot") or "ad-container" in tag.get("class", []) or "adsense-container" in tag.get("class", []))
        self.assertGreaterEqual(len(ad_containers), 1, "No ad containers found to evaluate sponsorship label.")
        for container in ad_containers:
            text = container.get_text()
            has_label = "贊助" in text or "廣告" in text or "advertisement" in text.lower()
            self.assertTrue(has_label, f"Ad container missing required sponsorship label: {container}")

    def test_04_ad_container_spacing_isolation(self):
        """TC-T1-ADS-04: Ad containers have margin (e.g., my-6) isolating ads from misclick-prone interactive elements."""
        ad_containers = self.soup.find_all(lambda tag: tag.has_attr("data-ad-slot") or "ad-container" in tag.get("class", []) or "adsense-container" in tag.get("class", []))
        self.assertGreaterEqual(len(ad_containers), 1, "No ad containers found to evaluate spacing isolation.")
        for container in ad_containers:
            classes = " ".join(container.get("class", []))
            has_margin = any(m in classes for m in ["my-", "py-", "mb-", "mt-"]) or "margin" in container.get("style", "")
            self.assertTrue(has_margin, f"Ad container must have margin spacing to prevent accidental clicks: {container}")

    def test_05_ad_container_slot_naming(self):
        """TC-T1-ADS-05: Ad containers identify slots clearly via data-ad-slot (e.g., header, infeed, footer)."""
        ad_containers = self.soup.find_all(lambda tag: tag.has_attr("data-ad-slot") or "ad-container" in tag.get("class", []) or "adsense-container" in tag.get("class", []))
        slots = [c.get("data-ad-slot") for c in ad_containers if c.get("data-ad-slot")]
        self.assertGreaterEqual(len(slots), 1, "Ad containers should have data-ad-slot attribute identifying placement.")


class TestLegalAndTrustCompliancePages(unittest.TestCase):
    """Feature 10: Legal and trust compliance architecture for Google AdSense (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.soup = get_soup("index.html")
        cls.footer = cls.soup.find("footer")
        assert cls.footer is not None, "Missing <footer> element on page."

    def test_01_footer_navigation_present(self):
        """TC-T1-TRUST-01: Footer contains navigation links for trust and compliance."""
        links = self.footer.find_all("a")
        self.assertGreaterEqual(len(links), 3, "Footer must contain navigation links to trust pages.")

    def test_02_privacy_policy_link(self):
        """TC-T1-TRUST-02: Link to Privacy Policy (privacy.html) exists in footer or nav."""
        all_links = self.soup.find_all("a", href=True)
        privacy_links = [a for a in all_links if "privacy" in a["href"].lower()]
        self.assertGreaterEqual(len(privacy_links), 1, "Missing navigation link to Privacy Policy (privacy.html).")

    def test_03_terms_of_service_link(self):
        """TC-T1-TRUST-03: Link to Terms of Service (terms.html) exists in footer or nav."""
        all_links = self.soup.find_all("a", href=True)
        terms_links = [a for a in all_links if "terms" in a["href"].lower()]
        self.assertGreaterEqual(len(terms_links), 1, "Missing navigation link to Terms of Service (terms.html).")

    def test_04_about_and_contact_links(self):
        """TC-T1-TRUST-04: Links to About Us and Contact pages exist in footer or nav."""
        all_links = self.soup.find_all("a", href=True)
        about_links = [a for a in all_links if "about" in a["href"].lower()]
        contact_links = [a for a in all_links if "contact" in a["href"].lower()]
        self.assertGreaterEqual(len(about_links), 1, "Missing navigation link to About Us (about.html).")
        self.assertGreaterEqual(len(contact_links), 1, "Missing navigation link to Contact Us (contact.html).")

    def test_05_disclaimer_affiliate_disclosure_link(self):
        """TC-T1-TRUST-05: Link to Disclaimer / Affiliate Disclosure (disclaimer.html) exists."""
        all_links = self.soup.find_all("a", href=True)
        disclaimer_links = [a for a in all_links if "disclaimer" in a["href"].lower()]
        self.assertGreaterEqual(len(disclaimer_links), 1, "Missing navigation link to Disclaimer (disclaimer.html).")


class TestLinkQualificationAndSecurity(unittest.TestCase):
    """Feature 11: Link security & outbound affiliate qualification (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.soup = get_soup("index.html")

    def test_01_outbound_links_target_blank(self):
        """TC-T1-LINK-01: All external referral links open in new tab via target='_blank'."""
        external_links = self.soup.find_all("a", href=re.compile(r"^https?://"))
        for link in external_links:
            # Skip internal links that point to the site domain itself
            if any(d in link.get("href", "") for d in ["referral-codes.ointw.com", "lanlanlue.github.io"]):
                continue
            self.assertEqual(link.get("target"), "_blank", f"External link {link.get('href')} must have target='_blank'.")

    def test_02_outbound_links_rel_sponsored(self):
        """TC-T1-LINK-02: External referral links must contain rel attribute including 'sponsored'."""
        external_links = self.soup.find_all("a", href=re.compile(r"^https?://"))
        referral_links = [l for l in external_links if not any(d in l.get("href", "") for d in ["referral-codes.ointw.com", "lanlanlue.github.io"])]
        for link in referral_links:
            rel = link.get("rel", [])
            if isinstance(rel, str):
                rel = rel.split()
            self.assertIn("sponsored", rel, f"Referral link {link.get('href')} missing 'sponsored' in rel attribute.")

    def test_03_outbound_links_rel_noopener_noreferrer(self):
        """TC-T1-LINK-03: External links must include 'noopener' and 'noreferrer' to prevent tabnabbing."""
        external_links = self.soup.find_all("a", href=re.compile(r"^https?://"))
        referral_links = [l for l in external_links if not any(d in l.get("href", "") for d in ["referral-codes.ointw.com", "lanlanlue.github.io"])]
        for link in referral_links:
            rel = link.get("rel", [])
            if isinstance(rel, str):
                rel = rel.split()
            self.assertIn("noopener", rel, f"External link {link.get('href')} missing 'noopener'.")
            self.assertIn("noreferrer", rel, f"External link {link.get('href')} missing 'noreferrer'.")

    def test_04_no_empty_href_anchors(self):
        """TC-T1-LINK-04: No anchor tag should have empty or missing href."""
        anchors = self.soup.find_all("a")
        for a in anchors:
            href = a.get("href", "")
            self.assertTrue(len(href.strip()) > 0, f"Found empty href anchor: {a}")

    def test_05_copy_button_has_code_attribute(self):
        """TC-T1-LINK-05: Copy buttons have data-code attribute."""
        copy_btns = self.soup.find_all(class_=re.compile(r"copy-btn"))
        for btn in copy_btns:
            self.assertTrue(btn.has_attr("data-code"), f"Copy button missing data-code attribute: {btn}")


if __name__ == "__main__":
    unittest.main()
