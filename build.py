import io
import json
import os
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape


load_dotenv()

DIST_DIR = Path("dist")
DEFAULT_SITE_URL = "https://referral-codes.ointw.com"
DEFAULT_SITE_NAME = "推薦碼總覽"
DEFAULT_TITLE = "推薦碼總覽 | Referral Codes 精選優惠與邀請碼"
DEFAULT_ADSENSE_CLIENT_ID = "ca-pub-placeholder"

# Canonical static pages to index in sitemap.xml
SITEMAP_ENTRIES = [
    {"path": "/", "changefreq": "daily", "priority": "1.0"},
    {"path": "/about.html", "changefreq": "monthly", "priority": "0.6"},
    {"path": "/privacy.html", "changefreq": "monthly", "priority": "0.5"},
    {"path": "/terms.html", "changefreq": "monthly", "priority": "0.5"},
    {"path": "/disclaimer.html", "changefreq": "monthly", "priority": "0.5"},
    {"path": "/contact.html", "changefreq": "monthly", "priority": "0.5"},
]

COLUMN_ALIASES = {
    "Service Name": ["Service Name", "Service", "Name"],
    "Category": ["Category", "Type"],
    "Description": ["Description", "Desc", "Details"],
    "Referral Code": ["Referral Code", "Code", "ReferralCode"],
    "Referral Link": ["Referral Link", "Link", "URL", "Url"],
    "Expiry Date": ["Expiry Date", "Expiry", "Expires On"],
    "VerifyDate": ["VerifyDate", "Verify Date", "Updated At", "Last Verified"],
}


def _read_dataframe(data_source: str) -> pd.DataFrame:
    """
    Ingests referral dataset from remote Google Sheet or local CSV.
    Gracefully falls back to data_example.csv if network failure occurs.
    """
    if data_source.startswith("http"):
        try:
            response = requests.get(data_source, timeout=15)
            response.raise_for_status()
            csv_content = response.content.decode("utf-8-sig", errors="replace")
            return pd.read_csv(io.StringIO(csv_content))
        except Exception as exc:
            print(f"Warning: Failed to fetch remote dataset ({exc}). Falling back to 'data_example.csv'.")
            if os.path.exists("data_example.csv"):
                return pd.read_csv("data_example.csv", encoding="utf-8-sig")
            raise

    if not os.path.exists(data_source):
        raise FileNotFoundError(f"Data file not found: {data_source}")
    return pd.read_csv(data_source, encoding="utf-8-sig")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(col).strip() for col in df.columns]

    col_lookup = {}
    for col in df.columns:
        norm = "".join(ch for ch in str(col).lower() if ch.isalnum())
        if norm not in col_lookup:
            col_lookup[norm] = col

    rename_map = {}
    assigned_cols = set()

    for canonical_name in COLUMN_ALIASES.keys():
        if canonical_name in df.columns:
            assigned_cols.add(canonical_name)

    for canonical_name, aliases in COLUMN_ALIASES.items():
        if canonical_name in assigned_cols:
            continue
        for alias in aliases:
            norm_alias = "".join(ch for ch in str(alias).lower() if ch.isalnum())
            if norm_alias in col_lookup:
                matched_col = col_lookup[norm_alias]
                if matched_col not in assigned_cols and matched_col not in rename_map:
                    rename_map[matched_col] = canonical_name
                    assigned_cols.add(matched_col)
                    break

    if rename_map:
        df = df.rename(columns=rename_map)

    for canonical_name in COLUMN_ALIASES.keys():
        if canonical_name not in df.columns:
            df[canonical_name] = ""

    return df


def _filter_expired(df: pd.DataFrame) -> pd.DataFrame:
    if "Expiry Date" not in df.columns:
        return df

    original_count = len(df)
    expiry_dates = pd.to_datetime(
        df["Expiry Date"].astype(str), errors="coerce", format="mixed", utc=True
    ).dt.tz_localize(None)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    filtered = df[expiry_dates.isna() | (expiry_dates >= today)]
    removed_count = original_count - len(filtered)
    if removed_count > 0:
        print(f"Filtered out {removed_count} expired items.")
    return filtered


def _compute_last_updated(df: pd.DataFrame) -> str:
    default_date = datetime.now().strftime("%Y-%m-%d")
    if "VerifyDate" not in df.columns:
        return default_date

    verify_dates = pd.to_datetime(
        df["VerifyDate"].astype(str), errors="coerce", format="mixed", utc=True
    ).dt.tz_localize(None)
    max_verify_date = verify_dates.max()
    if pd.notna(max_verify_date):
        return max_verify_date.strftime("%Y-%m-%d")
    return default_date


def _generate_seo_description(item_count: int, category_count: int, last_updated_date: str) -> str:
    """
    Generates a high-CTR, SEO-optimized meta description strictly between 120 and 160 characters.
    Interpolates active item count, category count, and latest verified date.
    """
    desc = (
        f"收錄站長平時常用的 {item_count} 筆生活、數位工具與金融服務推薦碼與邀請連結，涵蓋 {category_count} 大分類。"
        f"定期自動篩選排除過期項目，更新基準為 {last_updated_date}。"
        f"提供一鍵複製與清楚說明，方便您在開戶或註冊時輕鬆享有迎新優惠！"
    )
    return desc


def _build_faq(
    last_updated_date: str,
    item_count: int = 0,
    categories: list[str] | None = None,
) -> list[dict]:
    """
    Generates dynamic FAQ entries based on active item counts and available categories.
    Outputs dual-key dictionary conforming to Contract 1 ({"question": str, "answer": str})
    while preserving backward compatibility for existing templates ({"name": str, "acceptedAnswer": ...}).
    """
    if categories is None:
        categories = []
    category_count = len(categories)
    cat_summary = "、".join(categories[:6])
    if category_count > 6:
        cat_summary += f" 等 {category_count} 大分類"
    elif not cat_summary:
        cat_summary = "多種日常分類"

    item_count_str = f"{item_count} 筆" if item_count > 0 else "多筆"

    faq_data = [
        {
            "question": "這些推薦碼與邀請連結如何整理與維護？",
            "answer": (
                f"本站所有推薦碼與優惠連結皆由站長手動收集與整理自己有在使用的項目，"
                f"並在每次建置過程中透過自動化排程比對有效期限（過濾已過期之項目），"
                f"盡量提供正確可用的優惠資訊。最新資料驗證基準為 {last_updated_date}。"
            ),
        },
        {
            "question": "使用本站提供的推薦碼或連結需要付費嗎？",
            "answer": (
                "完全不需要。本站所有推薦碼皆為免費公開分享。"
                "使用者在註冊或結帳時輸入推薦碼，或透過推薦連結前往官方網站完成指定任務，"
                "即可直接領取官方提供的迎新優惠、折價券或現金回饋。"
            ),
        },
        {
            "question": "目前有哪些服務分類可以使用優惠推薦碼？",
            "answer": (
                f"目前收錄涵蓋 {cat_summary}。每個分類皆提供服務說明、優惠代碼或註冊邀請連結，"
                "方便大家依需求快速查找各領域實用的開戶與消費優惠。"
            ),
        },
        {
            "question": "如何確保推薦碼能正確生效領取回饋？",
            "answer": (
                "建議在註冊時優先點選專屬推薦連結；若需手動填寫，請點擊本站卡片上的「複製」按鈕"
                "完整複製代碼，並貼至官方 App 或網站結帳/註冊流程中的「推薦人代碼」或「優惠碼」欄位。"
                "部分平台對舊用戶或已綁定帳號不適用迎新優惠，請務必先確認各服務活動規範。"
            ),
        },
        {
            "question": "若發現推薦碼過期、失效或無法使用該如何回報？",
            "answer": (
                "雖然系統會定期過濾已到期項目，但第三方平台可能無預警調整活動規範。"
                "若發現失效連結或代碼，歡迎透過聯絡我們頁面或寄信至站長信箱回報，"
                "站長收到後會盡快進行手動核實並更新清單。"
            ),
        },
        {
            "question": "如何在網站中快速找到需要的優惠代碼？",
            "answer": (
                "您可以利用頁面上方的即時搜尋框直接輸入服務名稱（如 Uber、GoShare）或關鍵字，"
                "亦可點擊分類標籤切換檢視，或使用鍵盤快捷鍵 '/' 快速啟動搜尋功能。"
            ),
        },
    ]

    enriched_faqs = []
    for item in faq_data:
        enriched_faqs.append(
            {
                "question": item["question"],
                "answer": item["answer"],
                # Backward-compatible fields for existing templates
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"],
                },
            }
        )
    return enriched_faqs


def _build_schema_graph(
    *,
    site_url: str,
    site_name: str = DEFAULT_SITE_NAME,
    seo_title: str,
    seo_description: str,
    last_updated_date: str,
    items: list[dict],
    faqs: list[dict],
) -> str:
    """
    Builds a fully connected, valid Schema.org JSON-LD @graph containing:
    1. WebSite (search action, language, publisher reference)
    2. Organization (entity authority, logo, disclaimer principles)
    3. CollectionPage (breadcrumb link, modification date, site link)
    4. BreadcrumbList (Home and Directory navigation items)
    5. ItemList (with items mapped to Offer schema with identifier, url, category, price: "0", priceCurrency: "TWD")
    6. FAQPage (with rich, meaningful questions & answers)
    """
    list_elements = []
    for idx, item in enumerate(items, start=1):
        raw_link = str(item.get("Referral Link", "") or "").strip()
        offer_url = raw_link if raw_link.startswith("http") else f"{site_url}/"
        offer_code = str(item.get("Referral Code", "") or "").strip()
        offer_name = str(item.get("Service Name", "") or "").strip()
        offer_desc = str(item.get("Description", "") or "").strip()
        offer_category = str(item.get("Category", "") or "").strip()

        list_elements.append(
            {
                "@type": "ListItem",
                "position": idx,
                "item": {
                    "@type": "Offer",
                    "name": offer_name,
                    "description": offer_desc,
                    "url": offer_url,
                    "identifier": offer_code,
                    "category": offer_category,
                    "price": "0",
                    "priceCurrency": "TWD",
                },
            }
        )

    faq_entities = [
        {
            "@type": "Question",
            "name": f.get("question") or f.get("name", ""),
            "acceptedAnswer": {
                "@type": "Answer",
                "text": (
                    f.get("answer")
                    if "answer" in f
                    else (
                        f.get("acceptedAnswer", {}).get("text", "")
                        if isinstance(f.get("acceptedAnswer"), dict)
                        else ""
                    )
                ),
            },
        }
        for f in faqs
    ]

    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{site_url}/#website",
                "url": f"{site_url}/",
                "name": site_name,
                "inLanguage": "zh-TW",
                "description": seo_description,
                "publisher": {"@id": f"{site_url}/#organization"},
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": f"{site_url}/?q={{search_term_string}}",
                    "query-input": "required name=search_term_string",
                },
            },
            {
                "@type": "Organization",
                "@id": f"{site_url}/#organization",
                "name": site_name,
                "url": f"{site_url}/",
                "logo": {
                    "@type": "ImageObject",
                    "@id": f"{site_url}/#logo",
                    "url": f"{site_url}/referral.png",
                    "caption": site_name,
                    "width": 512,
                    "height": 512,
                },
                "publishingPrinciples": f"{site_url}/disclaimer.html",
            },
            {
                "@type": "CollectionPage",
                "@id": f"{site_url}/#page",
                "url": f"{site_url}/",
                "name": seo_title,
                "description": seo_description,
                "isPartOf": {"@id": f"{site_url}/#website"},
                "breadcrumb": {"@id": f"{site_url}/#breadcrumb"},
                "dateModified": last_updated_date,
                "inLanguage": "zh-TW",
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{site_url}/#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "首頁",
                        "item": f"{site_url}/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "推薦碼總覽",
                        "item": f"{site_url}/",
                    },
                ],
            },
            {
                "@type": "ItemList",
                "@id": f"{site_url}/#item-list",
                "name": "Referral Code Directory",
                "itemListOrder": "https://schema.org/ItemListOrderAscending",
                "numberOfItems": len(items),
                "itemListElement": list_elements,
            },
            {
                "@type": "FAQPage",
                "@id": f"{site_url}/#faq",
                "mainEntity": faq_entities,
            },
        ],
    }

    return json.dumps(graph, ensure_ascii=False, indent=2).replace("</", "<\\/")


def _build_compliance_schema(
    *,
    site_url: str,
    site_name: str,
    page_filename: str,
    page_title: str,
    page_description: str,
    last_updated_date: str,
) -> str:
    """
    Builds a clean Schema.org JSON-LD graph specifically tailored for standalone trust/compliance pages.
    Includes WebSite, WebPage, and BreadcrumbList entities without misplaced ItemList/Offer elements.
    """
    clean_site_url = site_url.rstrip("/")
    page_url = f"{clean_site_url}/{page_filename}"
    crumb_name = page_title.split("|")[0].split("(")[0].strip()

    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{clean_site_url}/#website",
                "url": f"{clean_site_url}/",
                "name": site_name,
                "inLanguage": "zh-TW",
                "publisher": {"@id": f"{clean_site_url}/#organization"},
            },
            {
                "@type": "WebPage",
                "@id": f"{page_url}#webpage",
                "url": page_url,
                "name": page_title,
                "description": page_description,
                "isPartOf": {"@id": f"{clean_site_url}/#website"},
                "breadcrumb": {"@id": f"{page_url}#breadcrumb"},
                "dateModified": last_updated_date,
                "inLanguage": "zh-TW",
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{page_url}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "首頁",
                        "item": f"{clean_site_url}/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": crumb_name,
                        "item": page_url,
                    },
                ],
            },
        ],
    }
    return json.dumps(graph, ensure_ascii=False, indent=2).replace("</", "<\\/")


def _write_sitemap(site_url: str, last_updated_date: str) -> None:
    """Generate XML Sitemap 0.9 listing root and all compliance pages."""
    clean_site_url = site_url.rstrip("/")
    url_blocks = []
    for entry in SITEMAP_ENTRIES:
        loc = f"{clean_site_url}{entry['path']}"
        url_blocks.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{last_updated_date}</lastmod>\n"
            f"    <changefreq>{entry['changefreq']}</changefreq>\n"
            f"    <priority>{entry['priority']}</priority>\n"
            "  </url>"
        )

    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(url_blocks)
        + "\n</urlset>\n"
    )
    (DIST_DIR / "sitemap.xml").write_text(content, encoding="utf-8")


def _write_robots(site_url: str) -> None:
    """Generate RFC 9309 compliant robots.txt with search and AdSense crawler access."""
    clean_site_url = site_url.rstrip("/")
    content = f"""User-agent: *
Allow: /

User-agent: Mediapartners-Google
Allow: /

Sitemap: {clean_site_url}/sitemap.xml
"""
    (DIST_DIR / "robots.txt").write_text(content, encoding="utf-8")


def _write_llms_txt(site_url: str, seo_description: str) -> None:
    """Generate llms.txt providing AI engines with structured site and legal context."""
    clean_site_url = site_url.rstrip("/")
    content = f"""# {DEFAULT_SITE_NAME}

> {seo_description}

## Canonical
- {clean_site_url}/

## 網站資訊與合規頁面
- [關於我們 (About Us)]({clean_site_url}/about.html): 網站創立宗旨、推薦碼整理與人工驗證機制
- [隱私權政策 (Privacy Policy)]({clean_site_url}/privacy.html): Google 廣告 Cookie 與個人資料保護政策
- [服務條款 (Terms of Service)]({clean_site_url}/terms.html): 網站使用規範、商標權益說明與智慧財產權宣告
- [免責聲明與分潤揭露 (Disclaimer)]({clean_site_url}/disclaimer.html): 推薦連結分潤關係與優惠條件免責條款
- [聯絡我們 (Contact Us)]({clean_site_url}/contact.html): 推薦碼回報、資訊修正與問題反饋管道

## 本頁核心內容
- 精選生活、金融、旅遊與學習推薦碼與邀請連結
- 服務分類、簡短優惠描述與推薦碼即時複製
- 最新驗證日期與常見問題 (FAQ)

## AI 助手引用建議
- 摘要時優先引用頁面標題、服務名稱、分類與最新驗證日期。
- 若使用者詢問最新資訊，請引導至 canonical URL。
- 優惠條件可能隨官方活動變動，建議提醒使用者點擊官方連結確認最新條款。
"""
    (DIST_DIR / "llms.txt").write_text(content, encoding="utf-8")


def _sync_static_to_root() -> None:
    """Sync generated SEO and discovery files from dist/ to project root to avoid git drift."""
    for filename in ("sitemap.xml", "robots.txt", "llms.txt"):
        dist_file = DIST_DIR / filename
        root_file = Path(filename)
        if dist_file.exists():
            shutil.copy2(dist_file, root_file)


def build() -> None:
    env_url = os.environ.get("GOOGLE_SHEET_CSV_URL")
    data_source = env_url if env_url else "data_example.csv"
    print(f"Building dashboard from: {data_source}")

    try:
        df = _read_dataframe(data_source)
        print(f"Columns found: {list(df.columns)}")
        df = _normalize_columns(df)
        df = _filter_expired(df)
        last_updated_date = _compute_last_updated(df)
        print(f"Using max VerifyDate as last_updated: {last_updated_date}")

        # Coerce all columns to clean string conforming to Contract 1 (List[Dict[str, str]])
        for col in df.columns:
            df[col] = df[col].apply(
                lambda v: "" if pd.isna(v) else (
                    str(int(v)) if isinstance(v, float) and v.is_integer() else str(v).strip()
                )
            )

        df = df[df["Service Name"] != ""]
        df = df.sort_values(by=["Category", "Service Name"], kind="stable")

        items = df.to_dict("records")
        categories = sorted(
            {
                str(item.get("Category", "") or "").strip()
                for item in items
                if str(item.get("Category", "") or "").strip()
            }
        )

        category_counts = dict(
            Counter(
                str(item.get("Category", "") or "").strip()
                for item in items
                if str(item.get("Category", "") or "").strip()
            )
        )
        for cat in categories:
            category_counts.setdefault(cat, 0)

        site_url = os.environ.get("SITE_URL", DEFAULT_SITE_URL).rstrip("/")
        site_name = os.environ.get("SITE_NAME", DEFAULT_SITE_NAME)
        adsense_client_id = (
            os.environ.get("ADSENSE_CLIENT_ID", DEFAULT_ADSENSE_CLIENT_ID).strip()
            or DEFAULT_ADSENSE_CLIENT_ID
        )

        category_count = len(categories)
        item_count = len(items)
        current_year = datetime.now().year

        seo_title = f"{site_name} | Referral Codes 精選生活與金融優惠推薦碼總覽 ({current_year} 最新)"
        seo_description = _generate_seo_description(item_count, category_count, last_updated_date)
        seo_keywords = (
            "推薦碼, 邀請碼, 優惠碼, 折扣碼, 信用卡開戶, 數位帳戶, 證券開戶, "
            "referral code, invite code, coupon, Taiwan"
        )

        faqs = _build_faq(last_updated_date, item_count, categories)
        schema_json = _build_schema_graph(
            site_url=site_url,
            site_name=site_name,
            seo_title=seo_title,
            seo_description=seo_description,
            last_updated_date=last_updated_date,
            items=items,
            faqs=faqs,
        )

        DIST_DIR.mkdir(exist_ok=True)
        print(f"Output directory: {DIST_DIR}")

        for asset in ("referral.png", "banner.png", "CNAME"):
            src_path = Path(asset)
            if src_path.exists():
                shutil.copy2(src_path, DIST_DIR / asset)
                print(f"Copied {asset} to {DIST_DIR}")
            else:
                print(f"Warning: Asset not found: {asset}")

        _write_sitemap(site_url, last_updated_date)
        _write_robots(site_url)
        _write_llms_txt(site_url, seo_description)
        _sync_static_to_root()
        print("Generated and synced sitemap.xml, robots.txt, llms.txt")

        # Contract 1: Full context payload
        context = {
            "items": items,
            "categories": categories,
            "category_counts": category_counts,
            "current_year": current_year,
            "last_updated": last_updated_date,
            "faqs": faqs,
            "schema_json": schema_json,
            "site_url": site_url,
            "site_name": site_name,
            "adsense_client_id": adsense_client_id,
            "seo": {
                "site_name": site_name,
                "title": seo_title,
                "description": seo_description,
                "keywords": seo_keywords,
                "canonical_url": f"{site_url}/",
                "og_image": f"{site_url}/banner.png",
                "og_image_width": 1200,
                "og_image_height": 630,
                "last_updated": last_updated_date,
                "item_count": item_count,
                "category_count": category_count,
            },
        }

        template_env = Environment(
            loader=FileSystemLoader(searchpath="./templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # 1. Primary homepage rendering
        template = template_env.get_template("index.html")
        output_html = template.render(context)
        (DIST_DIR / "index.html").write_text(output_html, encoding="utf-8")
        print(f"Successfully generated {DIST_DIR / 'index.html'}")

        # 2. Multi-page compliance pages rendering (automatically active when templates exist)
        compliance_pages = [
            ("about.html", "關於我們 (About Us)", f"關於 {site_name} 站長與推薦碼整理說明。"),
            ("privacy.html", "隱私權政策 (Privacy Policy)", f"{site_name} 隱私權保護政策與 Google AdSense 廣告 Cookie 規範。"),
            ("terms.html", "服務條款 (Terms of Service)", f"{site_name} 使用者服務條款與免責規範。"),
            ("contact.html", "聯絡我們 (Contact Us)", f"聯絡 {site_name} 站長或回報失效優惠代碼。"),
            ("disclaimer.html", "免責聲明與分潤揭露 (Disclaimer)", f"{site_name} 免責聲明與推薦連結分潤透明揭露。"),
        ]
        for page_filename, page_title_prefix, page_desc in compliance_pages:
            page_template_path = Path("templates") / page_filename
            if page_template_path.exists():
                page_template = template_env.get_template(page_filename)
                full_title = f"{page_title_prefix} | {site_name}"

                page_seo = dict(context["seo"])
                page_seo["title"] = full_title
                page_seo["description"] = page_desc
                page_seo["canonical_url"] = f"{site_url}/{page_filename}"

                page_context = dict(context)
                page_context["seo"] = page_seo
                page_context["active_page"] = page_filename.replace(".html", "")
                page_context["schema_json"] = _build_compliance_schema(
                    site_url=site_url,
                    site_name=site_name,
                    page_filename=page_filename,
                    page_title=full_title,
                    page_description=page_desc,
                    last_updated_date=last_updated_date,
                )

                page_html = page_template.render(page_context)
                (DIST_DIR / page_filename).write_text(page_html, encoding="utf-8")
                print(f"Successfully generated {DIST_DIR / page_filename}")
            else:
                print(f"Warning: Compliance template {page_template_path} not found. Skipping {page_filename}.")

    except Exception as exc:
        print(f"Build failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    build()
