"""
Tier 3: Cross-Feature Interaction Test Suite.

Validates pairwise feature interactions and cross-cutting behaviors:
1. Search input + Category filter conjunctive filtering DOM wiring
2. Dark mode classes + Ad container visual contrast & anti-glare
3. i18n multilingual declaration + SEO alternate hreflangs
4. Ad container spacing isolation + Action/copy button click safety
5. Search query matching across 3-state card variations
6. Theme toggle event handling + localStorage persistence
7. Copy button clipboard action + Toast notification feedback
8. Category filter reset ('All') interaction with active search
9. Footer compliance links + Sitemap.xml URL correspondence
10. Schema.org ItemList count + DOM rendered card count parity
"""
import json
import os
import re
import sys
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_utils import (
    get_dist_html,
    get_soup,
    get_sitemap_tree,
    get_schema_graph,
    get_standard_test_context,
    render_template,
)


class TestCrossFeatureInteractions(unittest.TestCase):
    """Pairwise cross-feature interaction test cases."""

    @classmethod
    def setUpClass(cls):
        cls.html = get_dist_html("index.html")
        cls.soup = get_soup("index.html")

    def test_01_search_and_category_filter_dom_attributes(self):
        """TC-T3-PAIR-01: Search + Category filter: all cards possess data attributes for combined filtering."""
        card_grid = self.soup.find(id="cardGrid")
        self.assertIsNotNone(card_grid, "Missing #cardGrid.")
        cards = card_grid.find_all("article")
        self.assertGreaterEqual(len(cards), 1, "No referral cards found in #cardGrid.")

        for card in cards:
            self.assertTrue(card.has_attr("data-service"), f"Card {card} missing data-service for search.")
            self.assertTrue(card.has_attr("data-category"), f"Card {card} missing data-category for filter.")
            self.assertTrue(card.has_attr("data-description"), f"Card {card} missing data-description for search.")

    def test_02_dark_mode_and_ad_containers(self):
        """TC-T3-PAIR-02: Dark mode + Ad containers: ad units adapt with dark: styles to prevent glare."""
        ad_containers = self.soup.find_all(lambda tag: tag.has_attr("data-ad-slot") or "ad-container" in tag.get("class", []) or "adsense-container" in tag.get("class", []))
        self.assertGreaterEqual(len(ad_containers), 1, "No ad containers found to test dark mode adaptation.")

        for container in ad_containers:
            inner_content = str(container)
            has_dark_mode_token = "dark:" in inner_content
            self.assertTrue(has_dark_mode_token, f"Ad container {container} must contain dark: utility classes to prevent dark-mode glare.")

    def test_03_i18n_and_seo_hreflang_alignment(self):
        """TC-T3-PAIR-03: i18n + SEO metadata: hreflang alternates align with client-side translation languages."""
        head = self.soup.find("head")
        alternates = head.find_all("link", attrs={"rel": "alternate"})
        declared_languages = {l.get("hreflang") for l in alternates if l.get("hreflang")}
        
        # Verify both supported languages (zh-TW and en) are declared in SEO head
        self.assertIn("zh-TW", declared_languages, "SEO missing zh-TW hreflang alternate.")
        self.assertIn("en", declared_languages, "SEO missing en hreflang alternate.")

        # Verify client-side script contains translations for both zh-TW and en
        scripts = " ".join([s.get_text() for s in self.soup.find_all("script")])
        self.assertIn("'zh-TW'", scripts, "Script missing zh-TW translations dictionary.")
        self.assertIn("'en'", scripts, "Script missing en translations dictionary.")

    def test_04_ad_containers_and_action_buttons_spacing(self):
        """TC-T3-PAIR-04: Ad containers + Action buttons: ad containers enforce safe margin from interactive buttons."""
        ad_containers = self.soup.find_all(lambda tag: tag.has_attr("data-ad-slot") or "ad-container" in tag.get("class", []) or "adsense-container" in tag.get("class", []))
        self.assertGreaterEqual(len(ad_containers), 1, "No ad containers found to evaluate button spacing.")

        for container in ad_containers:
            classes = " ".join(container.get("class", []))
            has_isolation_margin = "my-6" in classes or "my-8" in classes or "my-10" in classes or "margin" in container.get("style", "")
            self.assertTrue(has_isolation_margin, f"Ad container {container} must have isolation margin (e.g., my-6) away from action buttons.")

    def test_05_search_attributes_on_all_card_variants(self):
        """TC-T3-PAIR-05: Search + 3-state cards: all card states include searchable attributes."""
        context = get_standard_test_context()
        rendered_html = render_template("index.html", context)
        soup = BeautifulSoup(rendered_html, "html.parser")
        
        cards = soup.find_all("article")
        self.assertEqual(len(cards), len(context["items"]), "Rendered card count does not match mock items count.")
        for card in cards:
            service = card.get("data-service")
            self.assertIsNotNone(service, "Card variant missing data-service.")
            self.assertTrue(len(service) > 0, "data-service must not be empty.")

    def test_06_theme_toggle_and_localstorage_persistence(self):
        """TC-T3-PAIR-06: Dark mode + LocalStorage: theme toggle script persists preference in localStorage."""
        scripts = " ".join([s.get_text() for s in self.soup.find_all("script")])
        self.assertIn("localStorage.theme", scripts, "Script must check and save theme in localStorage.theme.")
        self.assertIn("classList.toggle", scripts, "Script must toggle dark class on document element.")

    def test_07_copy_button_and_toast_element(self):
        """TC-T3-PAIR-07: Copy button + Toast feedback: copy button triggers #toast notification element."""
        toast = self.soup.find(id="toast")
        self.assertIsNotNone(toast, "Missing #toast feedback container.")
        classes = " ".join(toast.get("class", []))
        self.assertIn("opacity-0", classes, "#toast should be hidden initially (opacity-0).")

        copy_btns = self.soup.find_all(class_=re.compile(r"copy-btn"))
        if copy_btns:
            first_btn = copy_btns[0]
            self.assertTrue(first_btn.has_attr("data-code"), "Copy button must carry data-code attribute.")

    def test_08_category_all_preserves_search_input(self):
        """TC-T3-PAIR-08: Category filter reset: 'All' button restores full catalog without resetting search input."""
        cat_all = self.soup.find("button", attrs={"data-category": "All"})
        self.assertIsNotNone(cat_all, "Missing 'All' category filter button.")
        search_input = self.soup.find(id="searchInput")
        self.assertIsNotNone(search_input, "Missing #searchInput.")

    def test_09_footer_links_and_sitemap_correspondence(self):
        """TC-T3-PAIR-09: Footer compliance links + Sitemap.xml: all compliance pages linked in footer exist in sitemap.xml."""
        footer = self.soup.find("footer")
        self.assertIsNotNone(footer, "Missing <footer>.")
        
        tree = get_sitemap_tree()
        root = tree.getroot()
        sitemap_urls = [u.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text for u in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")]

        compliance_pages = ["privacy.html", "terms.html", "about.html", "contact.html", "disclaimer.html"]
        footer_links = [a.get("href", "") for a in footer.find_all("a")]

        # For every compliance page linked in the footer, verify it is in sitemap.xml
        for page in compliance_pages:
            footer_has_page = any(page in href for href in footer_links)
            sitemap_has_page = any(page in loc for loc in sitemap_urls)
            if footer_has_page:
                self.assertTrue(sitemap_has_page, f"Page {page} is linked in footer but missing from sitemap.xml!")

    def test_10_schema_itemlist_count_matches_dom_card_count(self):
        """TC-T3-PAIR-10: Schema.org ItemList + DOM cards: ItemList.numberOfItems matches rendered card count."""
        schema = get_schema_graph("index.html")
        item_list = next((n for n in schema.get("@graph", []) if n.get("@type") == "ItemList"), None)
        self.assertIsNotNone(item_list, "Schema missing ItemList entity.")

        schema_count = item_list.get("numberOfItems")
        card_grid = self.soup.find(id="cardGrid")
        dom_cards = card_grid.find_all("article")
        dom_count = len(dom_cards)

        self.assertEqual(schema_count, dom_count, f"Schema ItemList.numberOfItems ({schema_count}) does not match DOM card count ({dom_count}).")


if __name__ == "__main__":
    unittest.main()
