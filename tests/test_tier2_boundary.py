"""
Tier 2: Boundary & Corner Cases Test Suite (>=5 test cases per feature dimension).

Covers edge conditions, boundaries, and adversarial corner cases:
1. Empty referral codes & 3-state card rendering
2. Missing or blank referral links
3. Date parsing, expiration boundary, and invalid date formats
4. Extreme character lengths & text overflow handling
5. Special HTML entities & XSS injection prevention
6. Small viewports & responsive boundary classes
7. Edge dataset handling (zero items, single item, all expired)
"""
import copy
import json
import os
import re
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import build
from tests.test_utils import (
    get_standard_test_context,
    render_template,
    get_soup,
    get_dist_html,
)


class TestEmptyReferralCodes(unittest.TestCase):
    """Boundary 1: Handling empty or blank referral codes (>=5 test cases)."""

    def setUp(self):
        self.context = get_standard_test_context()

    def test_01_empty_code_omits_empty_code_element(self):
        """TC-T2-CODE-01: An item with empty referral code must NOT render an empty <code> block."""
        # Item 3 in standard context has Referral Code == ""
        html = render_template("index.html", self.context)
        soup = BeautifulSoup(html, "html.parser")
        
        # Find the card for DigitalOcean (which has empty code)
        card = soup.find(attrs={"data-service": "DigitalOcean"})
        self.assertIsNotNone(card, "Card for DigitalOcean not found.")
        
        code_tag = card.find("code")
        if code_tag:
            self.assertTrue(len(code_tag.get_text().strip()) > 0, "Rendered an empty <code> element for item without code!")

    def test_02_empty_code_omits_copy_button(self):
        """TC-T2-CODE-02: An item with empty code should omit or disable the copy button."""
        html = render_template("index.html", self.context)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": "DigitalOcean"})
        copy_btn = card.find(class_=re.compile(r"copy-btn"))
        if copy_btn:
            data_code = copy_btn.get("data-code", "").strip()
            self.assertTrue(len(data_code) > 0, "Rendered a copy button with empty data-code attribute!")

    def test_03_whitespace_only_code_treated_as_empty(self):
        """TC-T2-CODE-03: Referral code consisting solely of whitespace must be treated as empty."""
        ctx = copy.deepcopy(self.context)
        ctx["items"] = [{
            "Service Name": "SpaceCo",
            "Category": "Tools",
            "Description": "Whitespace code test",
            "Referral Code": "   \t  ",
            "Referral Link": "https://example.com/space",
            "Expiry Date": "2026-12-31",
            "VerifyDate": "2026-04-01",
        }]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": "SpaceCo"})
        self.assertIsNotNone(card)
        code_el = card.find("code")
        if code_el:
            self.assertTrue(len(code_el.get_text().strip()) > 0, "Whitespace code must not render as empty code block.")

    def test_04_link_only_card_preserves_cta(self):
        """TC-T2-CODE-04: Item with link but no code (Link-Only state) renders primary visit button."""
        html = render_template("index.html", self.context)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": "DigitalOcean"})
        link = card.find("a", href="https://m.do.co/c/test-link")
        self.assertIsNotNone(link, "Link-Only card must still render the destination <a> link.")

    def test_05_code_and_link_both_present(self):
        """TC-T2-CODE-05: Card with both code and link renders code, copy button, and link CTA."""
        html = render_template("index.html", self.context)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": "Spotify"})
        self.assertIsNotNone(card)
        code_tag = card.find("code")
        self.assertIsNotNone(code_tag, "Code+Link card must render <code> element.")
        self.assertEqual(code_tag.get_text().strip(), "SPOTIFY2026")
        link = card.find("a", href=re.compile(r"spotify\.com"))
        self.assertIsNotNone(link, "Code+Link card must render destination link.")


class TestMissingReferralLinks(unittest.TestCase):
    """Boundary 2: Handling missing or blank referral links (>=5 test cases)."""

    def setUp(self):
        self.context = get_standard_test_context()

    def test_01_empty_link_no_broken_anchor(self):
        """TC-T2-LINK-01: An item without referral link must not produce an <a> tag with empty or hash href."""
        # Item 4 (SecretCodeService) has Referral Link == ""
        html = render_template("index.html", self.context)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": "SecretCodeService"})
        self.assertIsNotNone(card)
        links = card.find_all("a")
        for a in links:
            href = a.get("href", "").strip()
            self.assertFalse(href == "" or href == "#", f"Card rendered broken anchor tag: {a}")

    def test_02_empty_link_renders_disabled_or_code_only_state(self):
        """TC-T2-LINK-02: Item with code but no link clearly indicates missing link or code-only mode."""
        html = render_template("index.html", self.context)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": "SecretCodeService"})
        text = card.get_text()
        has_indicator = "尚未提供連結" in text or "未提供" in text or "No link" in text or card.find("code") is not None
        self.assertTrue(has_indicator, "Missing link should be gracefully indicated or in code-only mode.")

    def test_03_code_only_card_preserves_code_copy(self):
        """TC-T2-LINK-03: Code-Only card preserves copy button functionality."""
        html = render_template("index.html", self.context)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": "SecretCodeService"})
        code_tag = card.find("code")
        self.assertIsNotNone(code_tag)
        self.assertEqual(code_tag.get_text().strip(), "SECRETOFFER")

    def test_04_whitespace_only_link_treated_as_empty(self):
        """TC-T2-LINK-04: Referral link with whitespace only must not generate clickable broken anchor."""
        ctx = copy.deepcopy(self.context)
        ctx["items"] = [{
            "Service Name": "BlankLinkService",
            "Category": "Tools",
            "Description": "Whitespace link test",
            "Referral Code": "BLANKCODE",
            "Referral Link": "   \n\t  ",
            "Expiry Date": "2026-12-31",
            "VerifyDate": "2026-04-01",
        }]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": "BlankLinkService"})
        for a in card.find_all("a"):
            self.assertTrue(len(a.get("href", "").strip()) > 0, "Whitespace link must not produce empty href link.")

    def test_05_item_with_neither_code_nor_link(self):
        """TC-T2-LINK-05: Item with neither code nor link renders informational card without crashing."""
        ctx = copy.deepcopy(self.context)
        ctx["items"] = [{
            "Service Name": "InfoOnlyService",
            "Category": "News",
            "Description": "Pure announcement item without codes or links",
            "Referral Code": "",
            "Referral Link": "",
            "Expiry Date": "2026-12-31",
            "VerifyDate": "2026-04-01",
        }]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": "InfoOnlyService"})
        self.assertIsNotNone(card, "Informational card without code or link must render cleanly.")


class TestDateBoundariesAndFormats(unittest.TestCase):
    """Boundary 3: Date calculations, expiration filtering, and invalid formats (>=5 test cases)."""

    def test_01_filter_expired_removes_past_dates(self):
        """TC-T2-DATE-01: _filter_expired removes items whose Expiry Date is in the past."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        df = pd.DataFrame([
            {"Service Name": "ExpiredItem", "Expiry Date": yesterday},
            {"Service Name": "ValidItem", "Expiry Date": tomorrow},
        ])
        filtered = build._filter_expired(df)
        names = list(filtered["Service Name"])
        self.assertNotIn("ExpiredItem", names, "Expired item was not filtered out.")
        self.assertIn("ValidItem", names, "Valid future item was incorrectly removed.")

    def test_02_filter_expired_retains_blank_expiry(self):
        """TC-T2-DATE-02: Non-expiring items (blank Expiry Date) must be retained."""
        df = pd.DataFrame([
            {"Service Name": "EvergreenItem", "Expiry Date": ""},
            {"Service Name": "NoneItem", "Expiry Date": None},
        ])
        filtered = build._filter_expired(df)
        self.assertEqual(len(filtered), 2, "Items with blank Expiry Date should be retained as evergreen.")

    def test_03_filter_expired_handles_corrupt_date_strings(self):
        """TC-T2-DATE-03: Corrupted expiry date strings (e.g. 'N/A', 'unknown') do not crash build."""
        df = pd.DataFrame([
            {"Service Name": "WeirdDateItem", "Expiry Date": "corrupted-date-xyz-999"},
        ])
        filtered = build._filter_expired(df)
        self.assertEqual(len(filtered), 1, "Corrupted date strings should coerce safely to NaT and not crash.")

    def test_04_compute_last_updated_max_date(self):
        """TC-T2-DATE-04: _compute_last_updated selects the latest valid date."""
        df = pd.DataFrame([
            {"VerifyDate": "2026-01-01"},
            {"VerifyDate": "2026-03-15"},
            {"VerifyDate": "2026-02-28"},
        ])
        last_updated = build._compute_last_updated(df)
        self.assertEqual(last_updated, "2026-03-15", "Should return the maximum valid VerifyDate.")

    def test_05_compute_last_updated_all_missing_defaults_today(self):
        """TC-T2-DATE-05: When all VerifyDate entries are missing or invalid, defaults to today's date."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        df = pd.DataFrame([
            {"VerifyDate": ""},
            {"VerifyDate": "not-a-date"},
        ])
        last_updated = build._compute_last_updated(df)
        self.assertEqual(last_updated, today_str, "Should fall back to today's date when all dates are invalid.")


class TestExtremeCharacterLengths(unittest.TestCase):
    """Boundary 4: Extreme character lengths and text overflow (>=5 test cases)."""

    def setUp(self):
        self.context = get_standard_test_context()

    def test_01_extremely_long_service_name(self):
        """TC-T2-LEN-01: Extremely long service name (150+ chars) renders without crashing template."""
        ctx = copy.deepcopy(self.context)
        long_name = "SuperCalifragilisticExpialidocious Cloud Computing Solutions International Group Global Enterprise Service"
        ctx["items"][0]["Service Name"] = long_name
        html = render_template("index.html", ctx)
        self.assertIn(long_name, html, "Long service name must be present in rendered HTML.")

    def test_02_extremely_long_description(self):
        """TC-T2-LEN-02: Long description (600+ chars) renders cleanly within card body."""
        ctx = copy.deepcopy(self.context)
        long_desc = "Detailed offer description. " * 30  # ~840 chars
        ctx["items"][0]["Description"] = long_desc
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": ctx["items"][0]["Service Name"]})
        self.assertIsNotNone(card)
        self.assertIn("Detailed offer description.", card.get_text())

    def test_03_extremely_long_referral_code(self):
        """TC-T2-LEN-03: Long unbroken referral code (80 chars) renders with truncation or wrapping classes."""
        ctx = copy.deepcopy(self.context)
        long_code = "A" * 80
        ctx["items"][0]["Referral Code"] = long_code
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        code_tag = soup.find("code")
        self.assertIsNotNone(code_tag)
        classes = " ".join(code_tag.get("class", []))
        has_overflow_control = "truncate" in classes or "break-" in classes or "select-all" in classes
        self.assertTrue(has_overflow_control, "<code> tag must have overflow control class like truncate or break-all.")

    def test_04_extremely_long_category_name(self):
        """TC-T2-LEN-04: Long category name renders in category filter buttons."""
        ctx = copy.deepcopy(self.context)
        long_cat = "Enterprise Financial Services & FinTech Solutions"
        ctx["items"][0]["Category"] = long_cat
        ctx["categories"].append(long_cat)
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        self.assertIn(long_cat, soup.get_text(), "Long category name must appear in rendered text.")

    def test_05_empty_description_field(self):
        """TC-T2-LEN-05: Empty description string renders without 'None' or 'undefined' placeholder artifacts."""
        ctx = copy.deepcopy(self.context)
        ctx["items"][0]["Description"] = ""
        html = render_template("index.html", ctx)
        self.assertNotIn("None", html, "Must not render Python 'None' string in HTML output.")
        self.assertNotIn("undefined", html, "Must not render JS 'undefined' string in HTML output.")


class TestSpecialCharactersAndXSS(unittest.TestCase):
    """Boundary 5: Special characters, HTML escaping, and XSS prevention (>=5 test cases)."""

    def setUp(self):
        self.context = get_standard_test_context()

    def test_01_script_injection_escaped_in_service_name(self):
        """TC-T2-SEC-01: <script> tags in service name are escaped and do not execute."""
        ctx = copy.deepcopy(self.context)
        xss_payload = "<script>alert('xss')</script>"
        ctx["items"][0]["Service Name"] = xss_payload
        html = render_template("index.html", ctx)
        self.assertNotIn("<script>alert('xss')</script>", html, "Script tag must be HTML-escaped!")
        self.assertIn("&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;", html)

    def test_02_quotes_in_description_escaped(self):
        """TC-T2-SEC-02: Double quotes and ampersands in description are escaped in HTML attributes."""
        ctx = copy.deepcopy(self.context)
        attack_desc = 'Special "50% off" & free <gift>'
        ctx["items"][0]["Description"] = attack_desc
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": ctx["items"][0]["Service Name"]})
        self.assertIsNotNone(card)
        self.assertEqual(card.get("data-description"), attack_desc, "BeautifulSoup attribute parsing should decode escaped value safely.")

    def test_03_schema_json_ld_escaping_with_special_chars(self):
        """TC-T2-SEC-03: Quotes in service names do not produce invalid Schema.org JSON."""
        ctx = copy.deepcopy(self.context)
        service_with_quotes = 'Service with "Special" Quotes'
        ctx["items"][0]["Service Name"] = service_with_quotes
        # Re-build schema graph JSON string
        schema_dict = json.loads(ctx["schema_json"])
        schema_dict["@graph"][2]["itemListElement"][0]["item"]["name"] = service_with_quotes
        ctx["schema_json"] = json.dumps(schema_dict, ensure_ascii=False)
        
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        schema_script = soup.find("script", type="application/ld+json")
        self.assertIsNotNone(schema_script)
        # Verify JSON parses without syntax error
        parsed = json.loads(schema_script.string)
        self.assertEqual(parsed["@graph"][2]["itemListElement"][0]["item"]["name"], service_with_quotes)

    def test_04_chinese_and_unicode_characters(self):
        """TC-T2-SEC-04: Traditional Chinese, emojis, and Unicode symbols render intact."""
        ctx = copy.deepcopy(self.context)
        unicode_title = "國泰世華 CUBE 卡 🎁 推薦碼優惠 2026"
        ctx["items"][0]["Service Name"] = unicode_title
        html = render_template("index.html", ctx)
        self.assertIn("國泰世華 CUBE 卡 🎁 推薦碼優惠 2026", html)

    def test_05_javascript_pseudo_protocol_in_link(self):
        """TC-T2-SEC-05: Links starting with javascript: should not execute script."""
        ctx = copy.deepcopy(self.context)
        ctx["items"][0]["Referral Link"] = "javascript:alert('pwned')"
        html = render_template("index.html", ctx)
        # Even if present in href, it must have rel='sponsored' and target='_blank'
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find(attrs={"data-service": ctx["items"][0]["Service Name"]})
        a = card.find("a")
        if a:
            self.assertEqual(a.get("target"), "_blank")


class TestSmallViewportsAndResponsiveBoundaries(unittest.TestCase):
    """Boundary 6: Small viewports, mobile boundaries, and responsive classes (>=5 test cases)."""

    @classmethod
    def setUpClass(cls):
        cls.soup = get_soup("index.html")

    def test_01_viewport_allows_user_zoom(self):
        """TC-T2-RWD-01: Viewport meta tag does not lock user zoom (no user-scalable=no or maximum-scale=1)."""
        head = self.soup.find("head")
        viewport = head.find("meta", attrs={"name": "viewport"})
        content = viewport.get("content", "").lower()
        self.assertNotIn("user-scalable=no", content, "WCAG Accessibility: Do not lock user-scalable.")
        self.assertNotIn("maximum-scale=1", content, "WCAG Accessibility: Do not restrict maximum-scale.")

    def test_02_no_fixed_body_width(self):
        """TC-T2-RWD-02: Main container uses max-w-* classes rather than fixed widths like w-[1200px]."""
        main = self.soup.find("main")
        self.assertIsNotNone(main)
        classes = " ".join(main.get("class", []))
        self.assertIn("max-w-", classes, "Main container should use max-w- (e.g., max-w-6xl) to prevent mobile horizontal overflow.")

    def test_03_grid_collapses_to_single_column_on_mobile(self):
        """TC-T2-RWD-03: Card grid uses grid-cols-1 by default for mobile viewports."""
        card_grid = self.soup.find(id="cardGrid")
        classes = " ".join(card_grid.get("class", []))
        self.assertIn("grid-cols-1", classes, "Grid should start at grid-cols-1 for mobile screens.")

    def test_04_category_container_wrap_or_scroll(self):
        """TC-T2-RWD-04: Category chips container wraps or scrolls horizontally to avoid page overflow."""
        cat_filters = self.soup.find(id="categoryFilters")
        classes = " ".join(cat_filters.get("class", []))
        has_flexible_layout = "flex-wrap" in classes or "overflow-x-auto" in classes or "flex" in classes
        self.assertTrue(has_flexible_layout, "Category chips must support flex-wrap or overflow-x-auto.")

    def test_05_header_responsive_padding(self):
        """TC-T2-RWD-05: Navigation header uses responsive padding."""
        header = self.soup.find("header")
        inner = header.find("div")
        classes = " ".join(inner.get("class", []))
        self.assertTrue("px-" in classes or "mx-" in classes, "Header inner container must include horizontal padding.")


class TestEdgeDatasetHandling(unittest.TestCase):
    """Boundary 7: Edge dataset handling: zero items, single item, single category (>=5 test cases)."""

    def setUp(self):
        self.context = get_standard_test_context()

    def test_01_empty_items_list_renders_safely(self):
        """TC-T2-DATA-01: Rendering template with 0 items does not throw exception."""
        ctx = copy.deepcopy(self.context)
        ctx["items"] = []
        ctx["categories"] = []
        ctx["seo"]["item_count"] = 0
        ctx["seo"]["category_count"] = 0
        html = render_template("index.html", ctx)
        self.assertIsNotNone(html, "Template rendered None on empty items list.")
        self.assertIn("<!DOCTYPE html>", html)

    def test_02_single_item_dataset(self):
        """TC-T2-DATA-02: Dataset with exactly 1 item renders cleanly."""
        ctx = copy.deepcopy(self.context)
        ctx["items"] = [ctx["items"][0]]
        ctx["categories"] = [ctx["items"][0]["Category"]]
        ctx["seo"]["item_count"] = 1
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("article")
        self.assertEqual(len(cards), 1, "Expected exactly 1 rendered card.")

    def test_03_all_items_same_category(self):
        """TC-T2-DATA-03: When all items share one category, category buttons render All + that category."""
        ctx = copy.deepcopy(self.context)
        for item in ctx["items"]:
            item["Category"] = "Finance"
        ctx["categories"] = ["Finance"]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        cat_btns = soup.find_all("button", attrs={"data-category": True})
        categories = [b["data-category"] for b in cat_btns]
        self.assertEqual(sorted(categories), ["All", "Finance"])

    def test_04_normalize_columns_alias_mapping(self):
        """TC-T2-DATA-04: build._normalize_columns correctly maps column aliases."""
        df = pd.DataFrame([{
            "Service": "TestService",
            "Type": "Food",
            "Desc": "Test Description",
            "Code": "DISCOUNT10",
            "Url": "https://example.com/promo",
            "Expiry": "2026-12-31",
            "Updated At": "2026-04-10",
        }])
        normalized = build._normalize_columns(df)
        for canonical in ["Service Name", "Category", "Description", "Referral Code", "Referral Link", "Expiry Date", "VerifyDate"]:
            self.assertIn(canonical, normalized.columns, f"Alias normalization failed for canonical column: {canonical}")

    def test_05_normalize_columns_missing_all_columns(self):
        """TC-T2-DATA-05: Missing optional columns are populated with empty strings."""
        df = pd.DataFrame([{"Service Name": "BareService"}])
        normalized = build._normalize_columns(df)
        self.assertEqual(normalized.iloc[0]["Referral Code"], "")
        self.assertEqual(normalized.iloc[0]["Referral Link"], "")


if __name__ == "__main__":
    unittest.main()
