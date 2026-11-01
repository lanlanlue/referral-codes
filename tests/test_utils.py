"""
Test utilities and helpers for E2E Test Suite.
Provides reliable access to build artifacts, DOM parsing, and template rendering.
"""
import io
import json
import os
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist"
TEMPLATES_DIR = ROOT_DIR / "templates"


def get_dist_file(filename: str) -> Path:
    """Return Path to a file in dist/."""
    return DIST_DIR / filename


def get_dist_html(filename: str = "index.html") -> str:
    """Read HTML file content from dist/."""
    path = DIST_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Artifact {filename} not found in {DIST_DIR}. Has build.py been executed?")
    return path.read_text(encoding="utf-8")


def get_soup(filename: str = "index.html") -> BeautifulSoup:
    """Parse HTML artifact from dist/ into BeautifulSoup."""
    html_content = get_dist_html(filename)
    return BeautifulSoup(html_content, "html.parser")


def get_sitemap_tree() -> ET.ElementTree:
    """Parse sitemap.xml from dist/."""
    sitemap_path = DIST_DIR / "sitemap.xml"
    if not sitemap_path.exists():
        raise FileNotFoundError(f"sitemap.xml not found in {DIST_DIR}")
    return ET.parse(sitemap_path)


def get_robots_content() -> str:
    """Read robots.txt from dist/."""
    robots_path = DIST_DIR / "robots.txt"
    if not robots_path.exists():
        raise FileNotFoundError(f"robots.txt not found in {DIST_DIR}")
    return robots_path.read_text(encoding="utf-8")


def get_schema_graph(filename: str = "index.html") -> dict:
    """Extract and parse Schema.org JSON-LD from dist HTML."""
    soup = get_soup(filename)
    script = soup.find("script", type="application/ld+json")
    if not script or not script.string:
        raise ValueError(f"No <script type='application/ld+json'> found in {filename}")
    return json.loads(script.string)


def get_standard_test_context() -> dict:
    """
    Produce a canonical mock context adhering strictly to Contract 1 in PROJECT.md.
    """
    items = [
        {
            "Service Name": "Spotify",
            "Category": "Music",
            "Description": "3 months free trial for new premium accounts",
            "Referral Code": "SPOTIFY2026",
            "Referral Link": "https://www.spotify.com/us/signup?code=SPOTIFY2026",
            "Expiry Date": "2026-12-31",
            "VerifyDate": "2026-04-15",
        },
        {
            "Service Name": "Uber Eats",
            "Category": "Food",
            "Description": "$15 off on first order over $30",
            "Referral Code": "EATS-2026",
            "Referral Link": "https://www.ubereats.com/invite/EATS-2026",
            "Expiry Date": "2026-12-31",
            "VerifyDate": "2026-04-14",
        },
        {
            "Service Name": "DigitalOcean",
            "Category": "Cloud",
            "Description": "$200 free credit valid for 60 days",
            "Referral Code": "",
            "Referral Link": "https://m.do.co/c/test-link",
            "Expiry Date": "2026-12-31",
            "VerifyDate": "2026-04-10",
        },
        {
            "Service Name": "SecretCodeService",
            "Category": "Tools",
            "Description": "Code only discount without affiliate link",
            "Referral Code": "SECRETOFFER",
            "Referral Link": "",
            "Expiry Date": "2026-12-31",
            "VerifyDate": "2026-04-01",
        },
    ]
    categories = sorted(list({item["Category"] for item in items}))
    category_counts = {cat: sum(1 for i in items if i["Category"] == cat) for cat in categories}
    site_url = "https://referral-codes.ointw.com"
    site_name = "推薦碼總覽"

    faqs = [
        {
            "@type": "Question",
            "name": "這些推薦碼如何整理？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "由人工整理並定期驗證有效性。",
            },
        },
        {
            "@type": "Question",
            "name": "使用推薦碼需要額外付費嗎？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "完全免費，享有專屬折扣或新戶禮。",
            },
        },
    ]

    schema_graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{site_url}/#website",
                "url": f"{site_url}/",
                "name": site_name,
                "inLanguage": "zh-TW",
            },
            {
                "@type": "CollectionPage",
                "@id": f"{site_url}/#page",
                "url": f"{site_url}/",
                "name": f"{site_name} | 精選優惠推薦碼 (2026 最新)",
                "isPartOf": {"@id": f"{site_url}/#website"},
            },
            {
                "@type": "ItemList",
                "@id": f"{site_url}/#item-list",
                "name": "Referral Code Directory",
                "numberOfItems": len(items),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": idx + 1,
                        "item": {
                            "@type": "Offer",
                            "name": item["Service Name"],
                            "description": item["Description"],
                            "url": item["Referral Link"],
                            "identifier": item["Referral Code"],
                            "category": item["Category"],
                        },
                    }
                    for idx, item in enumerate(items)
                ],
            },
            {
                "@type": "FAQPage",
                "@id": f"{site_url}/#faq",
                "mainEntity": faqs,
            },
        ],
    }

    return {
        "items": items,
        "categories": categories,
        "category_counts": category_counts,
        "current_year": 2026,
        "last_updated": "2026-04-15",
        "faqs": faqs,
        "schema_json": json.dumps(schema_graph, ensure_ascii=False),
        "site_url": site_url,
        "site_name": site_name,
        "adsense_client_id": "ca-pub-test-12345678",
        "seo": {
            "site_name": site_name,
            "title": f"{site_name} | 精選生活與金融優惠推薦碼 (2026 最新)",
            "description": f"整理 {len(items)} 筆經人工驗證之推薦碼與邀請連結，涵蓋 {len(categories)} 大分類。每日自動更新與過期排除。",
            "keywords": "推薦碼, 邀請碼, 優惠碼, 折扣碼, referral code, invite coupon",
            "canonical_url": f"{site_url}/",
            "og_image": f"{site_url}/banner.png",
            "last_updated": "2026-04-15",
            "item_count": len(items),
            "category_count": len(categories),
        },
    }


def render_template(template_name: str, context: dict) -> str:
    """Render a template directly with Jinja2 environment."""
    env = Environment(
        loader=FileSystemLoader(searchpath=str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    tpl = env.get_template(template_name)
    return tpl.render(context)
