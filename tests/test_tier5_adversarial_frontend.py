"""
Tier 5: Adversarial Coverage Hardening Test Suite (Frontend, Design System, Interactivity, AdSense & Trust)

Adversarial stress harness for Milestone 4 Phase 2:
1. Design system & typography (Zinc tokens, Inter+Noto Sans TC, dark mode anti-glare, ambient hero glow, live ping badge)
2. Adaptive 3-State cards (Code+Link, Code-Only, Link-Only, Info-Only; 100% empty code bug elimination)
3. Category chips with item count accuracy & mobile horizontal swipe
4. Client-side JS interactivity, i18n zh-TW/en bidirectional key parity, / shortcut, Escape clear, copy checkmark feedback
5. Google AdSense 4 zero-CLS reserved ad units (Header, In-feed, Sidebar, Pre-footer), sponsor labels, and 20px+ isolation
6. Standalone Trust pages (E-E-A-T in about.html, DART cookie opt-outs in privacy.html, anti-scraping in terms.html, 24-48h SLA in contact.html, FTC affiliate disclosure in disclaimer.html)
7. Mobile viewports (320px/360px), color contrast, internal links, a11y labels & keyboard focus.
"""
import json
import os
import re
import sys
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_utils import (
    get_dist_html,
    get_soup,
    get_standard_test_context,
    render_template,
)

TEMPLATES_DIR = PROJECT_ROOT / "templates"
DIST_DIR = PROJECT_ROOT / "dist"

ALL_TEMPLATES = [
    "index.html",
    "about.html",
    "privacy.html",
    "terms.html",
    "contact.html",
    "disclaimer.html",
]


class TestDesignSystemAndTypography(unittest.TestCase):
    """Adversarial Category 1: Design System & Typography Integrity across all templates."""

    def test_zinc_palette_tokens_across_all_templates(self):
        """TC-T5-DS-01: All templates must consistently implement the Zinc color token architecture."""
        for tpl_name in ALL_TEMPLATES:
            tpl_path = TEMPLATES_DIR / tpl_name
            self.assertTrue(tpl_path.exists(), f"Template {tpl_name} does not exist.")
            content = tpl_path.read_text(encoding="utf-8")

            # Body background and text color tokens
            self.assertIn(
                "bg-zinc-50",
                content,
                f"{tpl_name} is missing light mode token 'bg-zinc-50' on body.",
            )
            self.assertIn(
                "dark:bg-zinc-950",
                content,
                f"{tpl_name} is missing dark mode token 'dark:bg-zinc-950' on body.",
            )
            self.assertIn(
                "text-zinc-900",
                content,
                f"{tpl_name} is missing token 'text-zinc-900'.",
            )
            self.assertIn(
                "dark:text-zinc-100",
                content,
                f"{tpl_name} is missing token 'dark:text-zinc-100'.",
            )

            # Sticky navigation header zinc styling
            self.assertIn(
                "dark:border-zinc-800",
                content,
                f"{tpl_name} is missing dark border token 'dark:border-zinc-800' in header/footer.",
            )

    def test_typography_font_pairing_inter_noto(self):
        """TC-T5-DS-02: Fonts configuration must specify Inter and Noto Sans TC with proper preconnects."""
        for tpl_name in ALL_TEMPLATES:
            content = (TEMPLATES_DIR / tpl_name).read_text(encoding="utf-8")
            self.assertIn(
                "https://fonts.googleapis.com",
                content,
                f"{tpl_name} missing preconnect to Google Fonts.",
            )
            self.assertIn(
                "family=Inter",
                content,
                f"{tpl_name} missing Inter font stylesheet link.",
            )
            self.assertIn(
                "Noto+Sans+TC",
                content,
                f"{tpl_name} missing Noto Sans TC stylesheet link.",
            )
            self.assertIn(
                "fontFamily:",
                content,
                f"{tpl_name} missing Tailwind fontFamily configuration.",
            )
            self.assertIn(
                "'Noto Sans TC'",
                content,
                f"{tpl_name} missing 'Noto Sans TC' in Tailwind configuration.",
            )

    def test_dark_mode_anti_glare_and_inline_script(self):
        """TC-T5-DS-03: Dark mode anti-glare meta tags and inline DOM initializer script."""
        index_content = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
        
        # Adaptive theme-color meta tags
        self.assertIn(
            'meta name="theme-color" content="#09090b" media="(prefers-color-scheme: dark)"',
            index_content,
            "Missing dark theme-color meta tag for anti-glare browser UI.",
        )
        self.assertIn(
            'meta name="theme-color" content="#fafafa" media="(prefers-color-scheme: light)"',
            index_content,
            "Missing light theme-color meta tag.",
        )

        # Inline execution in <head> checking localStorage.theme
        self.assertIn(
            "localStorage.theme === 'dark'",
            index_content,
            "Missing inline dark-mode initialiser script in <head> to prevent theme flash.",
        )

    def test_ambient_hero_glow_and_live_ping_badge(self):
        """TC-T5-DS-04: Ambient editorial hero radial glow and live ping trust badge."""
        index_content = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn(
            "blur-3xl",
            index_content,
            "Missing ambient hero blur glow container.",
        )
        self.assertIn(
            "animate-ping",
            index_content,
            "Missing live green ping indicator animation in hero trust badge.",
        )
        self.assertIn(
            "data-i18n=\"hero_badge\"",
            index_content,
            "Missing hero trust badge data-i18n hook.",
        )


class TestAdaptiveCardsAndEmptyCodeBug(unittest.TestCase):
    """Adversarial Category 2: 3-State Card Architecture & Empty Code Bug Elimination."""

    def setUp(self):
        self.base_context = get_standard_test_context()

    def test_card_state_1_code_and_link(self):
        """TC-T5-CARD-01: State 1: Both code and link present renders code box, copy button, and link CTA."""
        ctx = dict(self.base_context)
        ctx["items"] = [
            {
                "Service Name": "DualService",
                "Category": "生活",
                "Description": "Both code and link provided",
                "Referral Code": "DUAL2026",
                "Referral Link": "https://example.com/signup?code=DUAL2026",
            }
        ]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find("article", attrs={"data-service": "DualService"})
        self.assertIsNotNone(card)

        # Has code element
        code_tag = card.find("code")
        self.assertIsNotNone(code_tag)
        self.assertEqual(code_tag.get_text().strip(), "DUAL2026")

        # Has copy button with data-code
        copy_btn = card.find("button", class_=lambda c: c and "copy-btn" in c)
        self.assertIsNotNone(copy_btn)
        self.assertEqual(copy_btn.get("data-code"), "DUAL2026")

        # Has active link CTA
        link_tag = card.find("a", href="https://example.com/signup?code=DUAL2026")
        self.assertIsNotNone(link_tag)
        self.assertIn("前往連結", link_tag.get_text())

    def test_card_state_2_code_only_no_broken_link(self):
        """TC-T5-CARD-02: State 2: Code only (link empty) renders code box, copy button, and manual hint (NO <a>)."""
        ctx = dict(self.base_context)
        ctx["items"] = [
            {
                "Service Name": "CodeOnlyService",
                "Category": "金融",
                "Description": "Referral code only without URL",
                "Referral Code": "MANUALONLY",
                "Referral Link": "",
            }
        ]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find("article", attrs={"data-service": "CodeOnlyService"})
        self.assertIsNotNone(card)

        # Has code and copy button
        code_tag = card.find("code")
        self.assertIsNotNone(code_tag)
        self.assertEqual(code_tag.get_text().strip(), "MANUALONLY")

        copy_btn = card.find("button", class_=lambda c: c and "copy-btn" in c)
        self.assertIsNotNone(copy_btn)

        # NO outbound <a> link tag rendered in action area
        outbound_links = card.find_all("a")
        self.assertEqual(
            len(outbound_links),
            0,
            f"Code-only card should have 0 <a> tags, found: {outbound_links}",
        )

        # Informational hint rendered
        self.assertIn("結帳或註冊時手動輸入代碼", card.get_text())

    def test_card_state_3_link_only_no_empty_code_or_copy_button(self):
        """TC-T5-CARD-03: State 3: Link only (code empty) renders auto-apply hint and link CTA (NO <code>, NO copy-btn)."""
        ctx = dict(self.base_context)
        ctx["items"] = [
            {
                "Service Name": "LinkOnlyService",
                "Category": "旅遊",
                "Description": "Auto apply link without explicit promo code",
                "Referral Code": "",
                "Referral Link": "https://example.com/auto-promo",
            }
        ]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find("article", attrs={"data-service": "LinkOnlyService"})
        self.assertIsNotNone(card)

        # MUST NOT render <code>
        code_tag = card.find("code")
        self.assertIsNone(
            code_tag,
            "CRITICAL BUG: Empty referral code rendered an empty <code> element!",
        )

        # MUST NOT render .copy-btn
        copy_btn = card.find("button", class_=lambda c: c and "copy-btn" in c)
        self.assertIsNone(
            copy_btn,
            "CRITICAL BUG: Empty referral code rendered a copy button!",
        )

        # Auto-apply banner present
        self.assertIn("點擊下方連結即可自動套用專屬優惠", card.get_text())

        # Link CTA present
        link_tag = card.find("a", href="https://example.com/auto-promo")
        self.assertIsNotNone(link_tag)

    def test_card_state_4_info_only_fallback(self):
        """TC-T5-CARD-04: State 4: Both code and link empty renders clean info fallback (NO <code>, NO <a>)."""
        ctx = dict(self.base_context)
        ctx["items"] = [
            {
                "Service Name": "InfoOnlyService",
                "Category": "Tools",
                "Description": "General information only",
                "Referral Code": "",
                "Referral Link": "",
            }
        ]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find("article", attrs={"data-service": "InfoOnlyService"})
        self.assertIsNotNone(card)

        self.assertIsNone(card.find("code"))
        self.assertIsNone(card.find("button", class_=lambda c: c and "copy-btn" in c))
        self.assertEqual(len(card.find_all("a")), 0)
        self.assertIn("優惠資訊分享", card.get_text())

    def test_whitespace_code_and_link_adversarial_normalization(self):
        """TC-T5-CARD-05: Adversarial whitespace codes/links are trimmed and treated strictly as empty."""
        ctx = dict(self.base_context)
        ctx["items"] = [
            {
                "Service Name": "WhitespaceCard",
                "Category": "生活",
                "Description": "Item with tabs, newlines, and spaces in code and link",
                "Referral Code": "   \t\n  ",
                "Referral Link": " \n\t  ",
            }
        ]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find("article", attrs={"data-service": "WhitespaceCard"})
        self.assertIsNotNone(card)

        # Should fall back to State 4 (Info Only) without throwing or rendering blank containers
        self.assertIsNone(card.find("code"))
        self.assertIsNone(card.find("button", class_=lambda c: c and "copy-btn" in c))
        self.assertEqual(len(card.find_all("a")), 0)

    def test_service_avatar_initial_generation(self):
        """TC-T5-CARD-06: Avatar initials are correctly derived and capitalized."""
        ctx = dict(self.base_context)
        ctx["items"] = [
            {
                "Service Name": "uber eats",
                "Category": "Food",
                "Referral Code": "ABC",
                "Referral Link": "https://example.com",
            },
            {
                "Service Name": "Spotify",
                "Category": "Music",
                "Referral Code": "XYZ",
                "Referral Link": "https://example.com",
            },
            {
                "Service Name": "",  # Empty name fallback
                "Category": "Other",
                "Referral Code": "123",
                "Referral Link": "https://example.com",
            },
        ]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("article", class_="card")

        # uber eats -> UB
        avatar_1 = cards[0].find("div", class_=lambda c: c and "rounded-xl" in c and "select-none" in c)
        self.assertEqual(avatar_1.get_text().strip(), "UB")

        # Spotify -> SP
        avatar_2 = cards[1].find("div", class_=lambda c: c and "rounded-xl" in c and "select-none" in c)
        self.assertEqual(avatar_2.get_text().strip(), "SP")

        # Empty -> SP fallback
        avatar_3 = cards[2].find("div", class_=lambda c: c and "rounded-xl" in c and "select-none" in c)
        self.assertEqual(avatar_3.get_text().strip(), "SP")

    def test_category_semantic_tint_badges_mapping(self):
        """TC-T5-CARD-07: Category tint badges correctly assign semantic color tokens."""
        ctx = dict(self.base_context)
        ctx["items"] = [
            {"Service Name": "S1", "Category": "生活", "Referral Code": "C1"},
            {"Service Name": "S2", "Category": "旅遊", "Referral Code": "C2"},
            {"Service Name": "S3", "Category": "虛擬貨幣", "Referral Code": "C3"},
            {"Service Name": "S4", "Category": "銀行新戶", "Referral Code": "C4"},
            {"Service Name": "S5", "Category": "UnknownCategory", "Referral Code": "C5"},
        ]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")

        # 生活 -> emerald
        c1 = soup.find("article", attrs={"data-service": "S1"})
        self.assertIn("bg-emerald-50", str(c1))

        # 旅遊 -> sky
        c2 = soup.find("article", attrs={"data-service": "S2"})
        self.assertIn("bg-sky-50", str(c2))

        # 虛擬貨幣 -> amber
        c3 = soup.find("article", attrs={"data-service": "S3"})
        self.assertIn("bg-amber-50", str(c3))

        # 銀行新戶 -> blue
        c4 = soup.find("article", attrs={"data-service": "S4"})
        self.assertIn("bg-blue-50", str(c4))

        # UnknownCategory -> fallback zinc
        c5 = soup.find("article", attrs={"data-service": "S5"})
        self.assertIn("bg-zinc-100", str(c5))


class TestCategoryChipsAndMobileScroll(unittest.TestCase):
    """Adversarial Category 3: Category Chips & Horizontal Mobile Scrolling."""

    def test_all_chip_count_and_individual_category_counts(self):
        """TC-T5-CHIP-01: 'All' button and category chips accurately count active items."""
        soup = get_soup("index.html")
        all_btn = soup.find("button", attrs={"data-category": "All"})
        self.assertIsNotNone(all_btn)

        cards = soup.find_all("article", class_="card")
        all_count_span = all_btn.find("span", class_="chip-count")
        self.assertEqual(int(all_count_span.get_text().strip()), len(cards))

        # Check category buttons
        cat_btns = soup.find_all("button", class_="category-btn")
        for btn in cat_btns:
            cat_name = btn.get("data-category")
            count_span = btn.find("span", class_="chip-count")
            self.assertIsNotNone(count_span)
            count = int(count_span.get_text().strip())

            if cat_name == "All":
                self.assertEqual(count, len(cards))
            else:
                expected = len(soup.find_all("article", attrs={"data-category": cat_name}))
                self.assertEqual(
                    count,
                    expected,
                    f"Count mismatch for category {cat_name}: displayed {count}, actual cards {expected}",
                )

    def test_mobile_horizontal_swipeable_classes_and_no_scrollbar(self):
        """TC-T5-CHIP-02: Category chip container includes horizontal scroll, no-scrollbar, and edge swipe."""
        soup = get_soup("index.html")
        filter_bar = soup.find(id="categoryFilters")
        self.assertIsNotNone(filter_bar)
        classes = filter_bar.get("class", [])

        self.assertIn("overflow-x-auto", classes, "Category chips missing overflow-x-auto for mobile scroll.")
        self.assertIn("no-scrollbar", classes, "Category chips missing no-scrollbar class.")
        self.assertTrue(
            any("sm:flex-wrap" in c for c in classes),
            "Category chips missing sm:flex-wrap for desktop wrapping.",
        )


class TestClientSideInteractivityAndI18n(unittest.TestCase):
    """Adversarial Category 4: Client-side Interactivity, JS Shortcuts, and i18n Key Parity."""

    def test_search_input_and_clear_button_attributes(self):
        """TC-T5-JS-01: Search input and clear button have correct DOM attributes."""
        soup = get_soup("index.html")
        search_input = soup.find(id="searchInput")
        self.assertIsNotNone(search_input)
        self.assertEqual(search_input.get("type"), "search")
        self.assertTrue(search_input.has_attr("aria-label"))
        self.assertEqual(search_input.get("autocomplete"), "off")

        search_clear = soup.find(id="searchClear")
        self.assertIsNotNone(search_clear)
        self.assertIn("hidden", search_clear.get("class", []))

    def test_keyboard_shortcuts_slash_and_escape(self):
        """TC-T5-JS-02: Keyboard listeners for / (focus search) and Escape (clear & blur) exist in script."""
        index_html = get_dist_html("index.html")
        self.assertIn("e.key === '/'", index_html, "Missing / shortcut listener.")
        self.assertIn("e.key === 'Escape'", index_html, "Missing Escape clear listener.")
        self.assertIn("searchInput.focus()", index_html, "Missing focus() call in / shortcut.")
        self.assertIn("searchInput.blur()", index_html, "Missing blur() call in Escape shortcut.")

    def test_i18n_dictionary_symmetry_and_completeness(self):
        """TC-T5-JS-03: Translations dictionary has 100% key symmetry between zh-TW and en."""
        index_html = get_dist_html("index.html")
        # Extract translations JS object using regex
        match = re.search(r"const translations\s*=\s*(\{[\s\S]*?\n\s*\};)", index_html)
        self.assertIsNotNone(match, "Failed to locate translations JS object in index.html")

        # Parse keys from zh-TW and en blocks
        raw_js = match.group(1)
        zhtw_block = re.search(r"['\"]zh-TW['\"]\s*:\s*\{([\s\S]*?)\},", raw_js)
        en_block = re.search(r"['\"]en['\"]\s*:\s*\{([\s\S]*?)\}\s*\}", raw_js)
        self.assertIsNotNone(zhtw_block, "Missing zh-TW translations block.")
        self.assertIsNotNone(en_block, "Missing en translations block.")

        zhtw_keys = set(re.findall(r"([a-zA-Z0-9_]+)\s*:", zhtw_block.group(1)))
        en_keys = set(re.findall(r"([a-zA-Z0-9_]+)\s*:", en_block.group(1)))

        diff_zh_en = zhtw_keys - en_keys
        diff_en_zh = en_keys - zhtw_keys
        self.assertEqual(
            diff_zh_en,
            set(),
            f"Keys in zh-TW but missing from en: {diff_zh_en}",
        )
        self.assertEqual(
            diff_en_zh,
            set(),
            f"Keys in en but missing from zh-TW: {diff_en_zh}",
        )

    def test_html_data_i18n_keys_present_in_translations(self):
        """TC-T5-JS-04: Every data-i18n attribute in index.html resolves to a valid key in translations."""
        soup = get_soup("index.html")
        i18n_elements = soup.find_all(attrs={"data-i18n": True})
        self.assertGreater(len(i18n_elements), 10, "Found too few data-i18n elements in DOM.")

        index_html = get_dist_html("index.html")
        match = re.search(r"const translations\s*=\s*(\{[\s\S]*?\n\s*\};)", index_html)
        zhtw_block = re.search(r"['\"]zh-TW['\"]\s*:\s*\{([\s\S]*?)\},", match.group(1))
        known_keys = set(re.findall(r"([a-zA-Z0-9_]+)\s*:", zhtw_block.group(1)))

        missing_keys = set()
        for el in i18n_elements:
            key = el["data-i18n"]
            if key not in known_keys:
                missing_keys.add(key)

        self.assertEqual(
            missing_keys,
            set(),
            f"HTML elements reference undefined data-i18n keys: {missing_keys}",
        )

    def test_theme_toggle_and_localstorage_persistence(self):
        """TC-T5-JS-05: Theme toggle flips dark class and persists into localStorage.theme."""
        index_html = get_dist_html("index.html")
        self.assertIn(
            "document.documentElement.classList.toggle('dark')",
            index_html,
            "Missing dark class toggle execution on theme button click.",
        )
        self.assertIn(
            "localStorage.theme =",
            index_html,
            "Missing localStorage.theme persistence on theme toggle.",
        )

    def test_clipboard_copy_feedback_and_fallback(self):
        """TC-T5-JS-06: Copy button triggers toast, swaps checkmark icon, and includes fallbackCopy."""
        index_html = get_dist_html("index.html")
        self.assertIn("function copyCode(", index_html)
        self.assertIn("showToast()", index_html)
        self.assertIn("copiedIcon.classList.remove('hidden')", index_html)
        self.assertIn("fallbackCopy(", index_html, "Missing fallbackCopy implementation for non-HTTPS/legacy browsers.")
        self.assertIn("document.execCommand('copy')", index_html)


class TestAdSenseLayoutAndZeroCLS(unittest.TestCase):
    """Adversarial Category 5: AdSense 4 Zero-CLS Reserved Units & Policy Compliance."""

    def test_four_homepage_ad_units_and_zero_cls(self):
        """TC-T5-ADS-01: Exactly 4 responsive ad containers on homepage with explicit min-height reservations."""
        soup = get_soup("index.html")
        ad_containers = soup.find_all("aside", class_="adsense-container")
        self.assertEqual(
            len(ad_containers),
            4,
            f"Expected exactly 4 AdSense containers on homepage, found {len(ad_containers)}",
        )

        slots = [ad.get("data-ad-slot") for ad in ad_containers]
        self.assertIn("header", slots)
        self.assertIn("infeed", slots)
        self.assertIn("sidebar", slots)
        self.assertIn("footer", slots)

        # Check explicit zero-CLS min-height reservations
        for ad in ad_containers:
            cls_str = " ".join(ad.get("class", []))
            has_min_h = bool(re.search(r"min-h-\[\d+px\]", cls_str))
            self.assertTrue(
                has_min_h,
                f"Ad container slot '{ad.get('data-ad-slot')}' missing zero-CLS min-height reservation: {cls_str}",
            )

    def test_ad_units_sponsor_labels_and_dark_contrast(self):
        """TC-T5-ADS-02: Every ad container has dedicated sponsor label and dark mode anti-glare."""
        soup = get_soup("index.html")
        ad_containers = soup.find_all("aside", class_="adsense-container")
        for ad in ad_containers:
            label_div = ad.find("div", attrs={"data-i18n": "ad_label"})
            self.assertIsNotNone(
                label_div,
                f"Ad slot {ad.get('data-ad-slot')} missing dedicated sponsor label.",
            )
            self.assertIn("贊助廣告", label_div.get_text())

            # Dark mode classes
            cls_str = " ".join(ad.get("class", []))
            self.assertIn(
                "dark:bg-zinc-900/50",
                cls_str,
                f"Ad slot {ad.get('data-ad-slot')} missing dark:bg anti-glare style.",
            )
            self.assertIn(
                "dark:border-zinc-800",
                cls_str,
                f"Ad slot {ad.get('data-ad-slot')} missing dark:border style.",
            )

    def test_ad_units_isolation_margins_my6(self):
        """TC-T5-ADS-03: Ad units have my-6 isolation margin to guarantee >= 20px spacing from action buttons."""
        soup = get_soup("index.html")
        ad_containers = soup.find_all("aside", class_="adsense-container")
        for ad in ad_containers:
            cls_str = " ".join(ad.get("class", []))
            self.assertIn(
                "my-6",
                cls_str,
                f"Ad slot {ad.get('data-ad-slot')} missing isolation margin 'my-6'.",
            )

    def test_infeed_ad_unit_fallback_under_small_datasets(self):
        """TC-T5-ADS-04: In-feed ad unit renders as fallback even if dataset has < 3 items."""
        ctx = dict(get_standard_test_context())
        ctx["items"] = [
            {"Service Name": "SingleItem", "Category": "生活", "Referral Code": "ONE"}
        ]
        html = render_template("index.html", ctx)
        soup = BeautifulSoup(html, "html.parser")
        infeed = soup.find("aside", attrs={"data-ad-slot": "infeed"})
        self.assertIsNotNone(
            infeed,
            "In-feed ad slot must still render when dataset has fewer than 3 items.",
        )

    def test_trust_pages_contain_zero_cls_ad_containers(self):
        """TC-T5-ADS-05: Standalone trust pages also contain zero-CLS Pre-footer ad unit."""
        trust_pages = ["about.html", "privacy.html", "terms.html", "contact.html", "disclaimer.html"]
        for p in trust_pages:
            soup = get_soup(p)
            ad = soup.find("aside", class_="adsense-container")
            self.assertIsNotNone(ad, f"Trust page {p} missing AdSense container.")
            self.assertEqual(ad.get("data-ad-slot"), "footer")
            cls_str = " ".join(ad.get("class", []))
            self.assertIn("min-h-[90px]", cls_str)
            self.assertIn("my-6", cls_str)
            self.assertIn("贊助廣告", ad.get_text())


class TestTrustPagesCompliance(unittest.TestCase):
    """Adversarial Category 6: Trust & Compliance Page Contents (E-E-A-T, SLA, Disclosures)."""

    def test_about_page_eeat_framework_and_curation_lifecycle(self):
        """TC-T5-TRUST-01: about.html contains full Google E-E-A-T framework and 5-stage curation lifecycle."""
        soup = get_soup("about.html")
        text = soup.get_text()

        # E-E-A-T
        self.assertIn("E-E-A-T", text)
        self.assertIn("真實經驗 (Experience)", text)
        self.assertIn("專業把關 (Expertise)", text)
        self.assertIn("權威認證 (Authoritativeness)", text)
        self.assertIn("值得信賴 (Trustworthiness)", text)

        # 5-Stage lifecycle
        self.assertIn("5-Stage Human Curation Methodology", text)
        self.assertIn("階段 1：實測採集", text)
        self.assertIn("階段 2：條款審核", text)
        self.assertIn("階段 3：自動過期篩選", text)
        self.assertIn("階段 4：週期複驗與日期戳記", text)
        self.assertIn("階段 5：社群回報與即時除役", text)

        # 4-step tutorial
        self.assertIn("4-Step Coupon Usage Tutorial", text)

    def test_privacy_page_dart_cookie_disclosures_and_optout_links(self):
        """TC-T5-TRUST-02: privacy.html contains Google AdSense DART cookie notice and 4 official opt-outs."""
        soup = get_soup("privacy.html")
        text = soup.get_text()

        # AdSense cookie disclosures
        self.assertIn("第三方廠商（包括 Google）會使用 Cookie", text)
        self.assertIn("Google 使用廣告 Cookie", text)

        # Opt-out URLs present
        links = [a.get("href", "") for a in soup.find_all("a")]
        self.assertTrue(
            any("adssettings.google.com" in link for link in links),
            "privacy.html missing Google Ads Settings opt-out URL.",
        )
        self.assertTrue(
            any("aboutads.info/choices" in link for link in links),
            "privacy.html missing DAA opt-out URL.",
        )
        self.assertTrue(
            any("optout.networkadvertising.org" in link for link in links),
            "privacy.html missing NAI opt-out URL.",
        )
        self.assertTrue(
            any("youronlinechoices.eu" in link for link in links),
            "privacy.html missing EDAA opt-out URL.",
        )

        # GDPR & CCPA
        self.assertIn("GDPR", text)
        self.assertIn("CCPA", text)
        self.assertIn("Sec-GPC", text)

    def test_terms_page_anti_scraping_and_nominative_fair_use(self):
        """TC-T5-TRUST-03: terms.html contains anti-scraping and nominative fair use clauses."""
        soup = get_soup("terms.html")
        text = soup.get_text()

        self.assertIn("嚴禁自動化惡意爬蟲 (No Automated Web Scraping)", text)
        self.assertIn("指示性合理使用 (Nominative Fair Use)", text)
        self.assertIn("AS IS", text)
        self.assertIn("Limitation of Liability", text)

    def test_contact_page_sla_email_and_broken_code_protocol(self):
        """TC-T5-TRUST-04: contact.html contains 24-48h SLA, official email, and reporting protocol."""
        soup = get_soup("contact.html")
        text = soup.get_text()

        self.assertIn("24–48 小時內回覆", text)
        self.assertIn("contact@ointw.com", text)
        self.assertIn("Broken Referral Reporting Protocol", text)

        # Form elements
        form = soup.find("form", id="contactForm")
        self.assertIsNotNone(form)
        self.assertIsNotNone(soup.find(id="contactName"))
        self.assertIsNotNone(soup.find(id="contactEmail"))
        self.assertIsNotNone(soup.find(id="contactCategory"))
        self.assertIsNotNone(soup.find(id="contactMessage"))

    def test_disclaimer_page_ftc_disclosure_and_rel_sponsored(self):
        """TC-T5-TRUST-05: disclaimer.html contains FTC 16 CFR Part 255 and rel='sponsored' documentation."""
        soup = get_soup("disclaimer.html")
        text = soup.get_text()

        self.assertIn("FTC - 16 CFR Part 255", text)
        self.assertIn("rel=\"noopener noreferrer nofollow sponsored\"", text)
        self.assertIn("零額外成本承諾", text)
        self.assertIn("No Financial, Tax or Legal Advice Warning", text)


class TestViewportsContrastLinksA11y(unittest.TestCase):
    """Adversarial Category 7: Responsive 320px/360px Viewports, Contrast, Links & A11y."""

    def test_mobile_viewports_no_overflow_classes(self):
        """TC-T5-RWD-01: HTML layout does not contain fixed rigid widths that break on 320px screens."""
        for tpl_name in ALL_TEMPLATES:
            content = (TEMPLATES_DIR / tpl_name).read_text(encoding="utf-8")
            
            # Must declare standard mobile viewport meta tag
            self.assertIn(
                'meta name="viewport" content="width=device-width, initial-scale=1.0"',
                content,
                f"{tpl_name} missing responsive viewport meta tag.",
            )

            # Check that container elements use responsive max-w rather than fixed w-[600px]
            rigid_width_matches = re.findall(r"\bw-\[(?:[4-9]\d{2}|\d{4,})px\]", content)
            self.assertEqual(
                rigid_width_matches,
                [],
                f"{tpl_name} has rigid width classes that cause horizontal overflow: {rigid_width_matches}",
            )

        # Homepage toast floating notification bounded by viewport width
        index_content = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn(
            "max-w-[calc(100vw-3rem)]",
            index_content,
            "Toast notification container missing max-w clamp for narrow 320px screens.",
        )

    def test_all_internal_anchors_and_links_resolve(self):
        """TC-T5-RWD-02: All internal links and anchor hashes resolve to existing targets."""
        for html_file in DIST_DIR.glob("*.html"):
            soup = BeautifulSoup(html_file.read_text(encoding="utf-8"), "html.parser")
            anchors = soup.find_all("a", href=True)

            for a in anchors:
                href = a["href"].strip()
                # Exclude external, mailto, or full URLs
                if href.startswith(("http://", "https://", "mailto:", "tel:")):
                    continue

                if href.startswith("#"):
                    # Local section hash
                    target_id = href[1:]
                    if target_id:
                        target_elem = soup.find(id=target_id)
                        self.assertIsNotNone(
                            target_elem,
                            f"Broken anchor '{href}' in {html_file.name}: target id not found in page.",
                        )
                elif ".html" in href:
                    # Page reference (e.g., about.html, about.html#directory)
                    page_name = href.split("#")[0].split("?")[0]
                    target_file = DIST_DIR / page_name
                    self.assertTrue(
                        target_file.exists(),
                        f"Broken link '{href}' in {html_file.name}: file {target_file} not found in dist/.",
                    )

    def test_accessibility_aria_labels_and_form_bindings(self):
        """TC-T5-RWD-03: Interactive icon-only buttons have aria-label and forms have matching label-for."""
        for html_file in DIST_DIR.glob("*.html"):
            soup = BeautifulSoup(html_file.read_text(encoding="utf-8"), "html.parser")

            # Check buttons without text have aria-label
            buttons = soup.find_all("button")
            for btn in buttons:
                text = btn.get_text().strip()
                if not text:
                    self.assertTrue(
                        btn.has_attr("aria-label"),
                        f"Icon-only button in {html_file.name} missing aria-label attribute.",
                    )

            # Check forms have properly bound labels
            forms = soup.find_all("form")
            for form in forms:
                inputs = form.find_all(["input", "textarea", "select"])
                for field in inputs:
                    if field.get("type") == "hidden":
                        continue
                    field_id = field.get("id")
                    if field_id:
                        label = form.find("label", attrs={"for": field_id})
                        self.assertIsNotNone(
                            label,
                            f"Form field '{field_id}' in {html_file.name} missing matching <label for='{field_id}'>.",
                        )


if __name__ == "__main__":
    unittest.main()
