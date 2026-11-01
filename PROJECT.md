# Project: Modernized SEO & AdSense-Ready Recommendation Platform

## Architecture
- **Core Technology**: Static Site Generator via Python (`build.py`) with Jinja2 templates, rendering production HTML and assets into `dist/`.
- **Frontend Stack**: Modern semantic HTML5, Tailwind CSS v3 via CDN configured with refined typography and Zinc design tokens, vanilla JavaScript for client-side search, filtering, i18n (`zh-TW` / `en`), and dark mode persistence.
- **Data Flow**: `GOOGLE_SHEET_CSV_URL` or local `data_example.csv` -> Ingestion & Alias Normalization -> Expiration Filtering (`Expiry Date >= today`) -> Last Verification Calculation (`max(VerifyDate)`) -> Schema.org JSON-LD Graph Generation -> Multi-Page Jinja2 Rendering (`index.html`, `privacy.html`, `terms.html`, `about.html`, `contact.html`, `disclaimer.html`) -> Static XML/Text Generation (`sitemap.xml`, `robots.txt`, `llms.txt`) -> Asset Distribution (`dist/`).
- **SEO & Search Visibility**: Comprehensive standard meta tags, OpenGraph 1200x630 previews, Twitter Cards summary_large_image, Schema.org graph (`WebSite`, `Organization`, `CollectionPage`, `ItemList`, `BreadcrumbList`, `FAQPage`), XML Sitemap 0.9, and RFC 9309 robots.txt.
- **Google AdSense Architecture**: Dedicated legal trust pages (Privacy Policy, Terms of Service, About Us, Contact, Disclaimer with affiliate disclosure), anti-thin-content editorial layer, and 4 responsive zero-CLS ad container slots with policy-compliant spacing and "贊助廣告" labels.

## Feature Inventory
Every feature identified during the Survey phase is mapped below to its assigned milestone.

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Standard Meta Tags | Charset, viewport, optimized title, meta description (120-160 chars), keywords, canonical URL, hreflang, robots | M1 | Survey Spec Miner 3 |
| 2 | OpenGraph Metadata | `og:type`, `og:locale`, `og:site_name`, `og:title`, `og:description`, `og:url`, `og:image` with dimensions (1200x630) | M1 | Survey Spec Miner 3 |
| 3 | Twitter Cards | `twitter:card` (summary_large_image), `twitter:title`, `twitter:description`, `twitter:image`, `twitter:alt` | M1 | Survey Spec Miner 3 |
| 4 | Schema.org JSON-LD Graph | Multi-entity graph: `WebSite`, `Organization`, `CollectionPage`, `BreadcrumbList`, `ItemList` (with Offer elements), `FAQPage` | M1 | Survey Spec Miner 3 |
| 5 | XML Sitemap Generation | Protocol 0.9 `sitemap.xml` listing root and all compliance pages (`about.html`, `privacy.html`, `terms.html`, `contact.html`, `disclaimer.html`) with `<lastmod>` and `<changefreq>` | M1 | Survey Spec Miner 3 & Explorer 1 |
| 6 | Robots.txt Generation | RFC 9309 compliant `robots.txt` referencing `sitemap.xml` and specifying crawler access | M1 | Survey Spec Miner 3 & Explorer 1 |
| 7 | LLM Indexing Markdown | Maintenance of `llms.txt` with structured site summary for AI search engines | M1 | Survey Explorer 1 |
| 8 | Modern Design System & Tokens | Refined Zinc neutral scale, crisp borders, dark mode balance (no white glare), and semantic category tint badges | M2 | Survey Explorer 2 |
| 9 | Human-Crafted Editorial Hero | Clean typography hero with subtle ambient mesh/glow, trust pill badge (`[● 人工驗證 • 2026 最新推薦碼總覽]`), live statistics metrics bar, eliminating dated dark banner overlay | M2 | Survey Explorer 2 |
| 10 | Adaptive 3-State Card Components | Service initial avatars, conditional rendering for Code+Link, Code-Only, and Link-Only (fixing the empty code bug), hover micro-interactions, copy checkmark feedback | M2 | Survey Explorer 2 |
| 11 | Responsive Navigation & Mobile UI | Horizontal swipeable category chip bar with item counts (`生活 (12)`), sticky header with navigation anchors, responsive grid avoiding horizontal overflow | M2 | Survey Explorer 2 |
| 12 | Core Interactive Retention | Preserving 100% of live search with `/` shortcut, category filter, bilingual i18n (`zh-TW` / `en`), and dark/light theme switch | M2 | Survey Explorer 2 |
| 13 | Legal & Trust Compliance Pages | Standalone templates and rendered pages for Privacy Policy (Google cookie disclosures), Terms of Service, About Us, Contact, and Disclaimer | M3 | Survey Spec Miner 3 |
| 14 | Anti-Thin-Content Architecture | Editorial curation guidelines, coupon usage tutorial section, verification trust badges, and comprehensive FAQs to satisfy AdSense content depth | M3 | Survey Spec Miner 3 |
| 15 | AdSense Ad Container Architecture | 4 responsive zero-CLS reserved ad units (Header, In-feed, Pre-footer, Sidebar) with "贊助廣告" labels and safe distance from action buttons | M3 | Survey Spec Miner 3 & Explorer 2 |
| 16 | Link Attribution & Security | `rel="noopener noreferrer nofollow sponsored"` on all outbound affiliate and referral links | M3 | Survey Spec Miner 3 & Explorer 1 |
| 17 | Opaque-Box E2E Test Suite | Comprehensive 4-tier test suite verifying HTML tags, Schema JSON-LD, sitemap/robots, RWD classes, interactive attributes, and AdSense containers | E2E Testing Track / M4 | Survey Spec Miner 3 |
| 18 | Adversarial Coverage Hardening | White-box stress testing, corner cases, data variations, and regression prevention | M4 (Phase 2) | Dual Track Protocol |

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Build Pipeline & SEO Engine Core | Implement full SEO metadata, Schema.org JSON-LD graph, multi-URL sitemap.xml, robots.txt, and build pipeline enhancements in `build.py` | none | DONE (`build.py`, `dist/sitemap.xml`, `dist/robots.txt`, `dist/llms.txt`, root sync; 60/60 M1 tests pass) |
| M2 | Modern Human-Crafted UI/UX | Redesign `templates/index.html` with modern Zinc palette, editorial hero, adaptive 3-state cards, category badges, mobile horizontal chips, and fix empty code bug | none | DONE (`templates/index.html`; 106/106 tests passed in Tiers 1-3, Reviewers APPROVE, Challengers APPROVE, Auditor CLEAN) |
| M3 | Google AdSense Compliance & Trust Pages | Build trust pages (`privacy.html`, `terms.html`, `about.html`, `contact.html`, `disclaimer.html`), anti-thin-content guides, and 4 zero-CLS ad containers | M1, M2 | DONE (5 trust templates & pages generated in `dist/`, 4 zero-CLS ad containers, 116/116 tests pass, 5/5 Gate evaluations passed) |
| M4 | Final Milestone: 100% E2E Pass & Adversarial Hardening | Phase 1: Pass 100% E2E tests (Tiers 1-4). Phase 2: Tier 5 Adversarial Coverage Hardening | M1, M2, M3, TEST_READY.md | DONE (148/148 tests pass across all 5 tiers with 100% pass rate, both Challengers APPROVE, Forensic Auditor CLEAN) |

## Parallel Tracks
- **Implementation Track**: Executes M1, M2, M3, and M4 sequentially or concurrently where decoupled.
- **E2E Testing Track**: Dispatched in parallel at start. Designs opaque-box test infrastructure and Tiers 1-4 test cases according to requirements. Publishes `TEST_READY.md` upon completion.

## Code Layout
```
d:\Code\SP\Recommendation\
├── build.py                  # Static site builder & SEO engine (Pipeline & schema generation)
├── data_example.csv          # Local fallback dataset (10 records)
├── templates/
│   ├── index.html            # Primary responsive Jinja2 template
│   ├── partials/             # (Optional) shared modular partials (nav, footer, seo, cards)
│   ├── about.html            # About Us trust page template
│   ├── privacy.html          # Privacy Policy compliance page template
│   ├── terms.html            # Terms of Service page template
│   ├── contact.html          # Contact page template
│   └── disclaimer.html       # Disclaimer & affiliate disclosure template
├── dist/                     # Generated static production output
│   ├── index.html            # Rendered homepage
│   ├── about.html            # Rendered About page
│   ├── privacy.html          # Rendered Privacy Policy page
│   ├── terms.html            # Rendered Terms page
│   ├── contact.html          # Rendered Contact page
│   ├── disclaimer.html       # Rendered Disclaimer page
│   ├── sitemap.xml           # Multi-URL sitemap
│   ├── robots.txt            # Crawler access control
│   ├── llms.txt              # LLM context documentation
│   ├── banner.png            # Static brand asset
│   └── referral.png          # Favicon / icon asset
├── tests/                    # Independent E2E test suite (E2E Testing Track)
│   ├── test_runner.py        # Automated test executor & validator
│   ├── test_tier1_feature.py # Feature coverage tests
│   ├── test_tier2_boundary.py# Boundary and corner case tests
│   ├── test_tier3_interaction.py # Cross-feature combination tests
│   └── test_tier4_workload.py# Real-world workload tests
├── TEST_INFRA.md             # E2E test suite index & coverage matrix
├── TEST_READY.md             # Signal file when test suite is fully published
└── PROJECT.md                # Master project architecture & tracking
```

## Interface Contracts

### Contract 1: `build.py` ↔ Templates Context
The data context dictionary passed from `build.py` to `templates/` MUST adhere to:
```python
context = {
    "items": List[Dict[str, str]],          # Normalized referral records
    "categories": List[str],                # Unique sorted category names
    "category_counts": Dict[str, int],      # Item count per category
    "current_year": int,                    # e.g., 2026
    "last_updated": str,                    # Format: YYYY-MM-DD
    "faqs": List[Dict[str, str]],           # List of {"question": str, "answer": str}
    "schema_json": str,                     # Escaped valid JSON-LD string
    "site_url": str,                        # Canonical base URL
    "site_name": str,                       # Site display name
    "adsense_client_id": str,               # Google AdSense pub ID (from env or default)
    "seo": {
        "title": str,
        "description": str,
        "keywords": str,
        "canonical_url": str,
        "og_image": str,
        "last_updated": str,
        "item_count": int,
        "category_count": int
    }
}
```

### Contract 2: URL & Static File Layout
All URLs generated in `sitemap.xml`, canonical tags, and navigation anchors must resolve to:
- Homepage: `{site_url}/` (or `index.html`)
- About: `{site_url}/about.html`
- Privacy Policy: `{site_url}/privacy.html`
- Terms of Service: `{site_url}/terms.html`
- Contact: `{site_url}/contact.html`
- Disclaimer: `{site_url}/disclaimer.html`

### Contract 3: Ad Containers Layout & Zero CLS
All AdSense ad container elements must include:
- Container class: `adsense-container`
- Inline or class-based `min-height` reservation (e.g., `min-h-[90px]` for leaderboard, `min-h-[250px]` for cards)
- Dedicated label: `<div class="text-[10px] uppercase tracking-wider text-zinc-400">贊助廣告</div>`
- Isolation margin: `my-6` (minimum 20px spacing from interactive buttons)
