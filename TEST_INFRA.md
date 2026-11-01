# Test Infrastructure Specification: E2E Test Suite

## Overview
This document specifies the opaque-box, requirement-driven E2E test infrastructure for the **Modernized SEO & AdSense-Ready Recommendation Platform**. The suite validates that static build artifacts, template rendering, responsive UI components, search/filter interactions, SEO tags, Schema.org graphs, and Google AdSense compliance policies conform strictly to requirements without reliance on white-box internals.

## 4-Tier Test Architecture

```
tests/
├── __init__.py               # Package marker
├── test_utils.py             # Artifact loaders, DOM helpers, mock contexts
├── test_runner.py            # Master test executor & reporter
├── test_tier1_feature.py     # Tier 1: Feature Coverage (>=5 tests / feature)
├── test_tier2_boundary.py    # Tier 2: Boundary & Corner Cases (>=5 tests / dim)
├── test_tier3_interaction.py # Tier 3: Cross-Feature Interactions (pairwise)
└── test_tier4_workload.py    # Tier 4: Real-World Application Workloads
```

---

### Tier 1: Feature Coverage (`tests/test_tier1_feature.py`)
Validates baseline functional requirements across 11 core architectural features:
1. **Standard `<head>` Tags**: Charset (first 1024 bytes), viewport (mobile-first), title (15-75 chars), meta description (50-200 chars), meta keywords, canonical URL (absolute HTTPS, no query params), robots directives (`index, follow`), hreflang (`zh-TW`, `en`, `x-default`).
2. **OpenGraph Metadata**: `og:type` (website), `og:locale` (zh_TW), `og:title`, `og:description`, `og:url` (canonical), `og:image` (preview banner), `og:site_name`.
3. **Twitter Cards**: `twitter:card` (summary_large_image), `twitter:title`, `twitter:description`, `twitter:image`.
4. **Schema.org JSON-LD Graph**: Top-level `@graph`, `WebSite`, `CollectionPage` / `WebPage`, `ItemList` with offers, `FAQPage` with questions and accepted answers.
5. **XML Sitemap Generation**: Namespace `sitemaps.org/schemas/sitemap/0.9`, canonical homepage `<loc>`, trust pages (`about.html`, `privacy.html`, `terms.html`, `disclaimer.html`, `contact.html`), ISO-8601 `<lastmod>` (`YYYY-MM-DD`), valid priority and changefreq.
6. **Robots.txt Generation**: `User-agent: *`, `Allow: /`, `Sitemap:` reference pointing to HTTPS `sitemap.xml`, RFC 9309 compliance.
7. **Modern UI & Responsive Layout**: Tailwind CDN script loaded, sticky `<header>`, hero typography hierarchy, CSS grid `#cardGrid`, category chips `#categoryFilters`, theme toggle `#themeToggle`.
8. **Core Interactive Retention**: `#searchInput`, category buttons with `data-category`, bilingual attributes `data-i18n`, copy buttons `.copy-btn` and `#toast`, `#noResults` state.
9. **Google AdSense Containers**: Minimum 2 ad containers, reserved `min-height` (zero-CLS), explicit "贊助廣告" / "ADVERTISEMENT" label, isolation margins (`my-6`).
10. **Legal & Trust Pages**: Navigation links to Privacy Policy (`privacy.html`), Terms of Service (`terms.html`), About Us (`about.html`), Contact (`contact.html`), Disclaimer (`disclaimer.html`).
11. **Link Qualifications & Security**: External links target `_blank`, `rel="noopener noreferrer nofollow sponsored"`, no empty `href=""`.

**Count**: 61 test cases.

---

### Tier 2: Boundary & Corner Cases (`tests/test_tier2_boundary.py`)
Validates edge conditions, input anomalies, and defensive rendering:
1. **Empty Referral Codes**: Items without code omit empty `<code>` element; omit or disable copy button; whitespace code treated as empty; preserves link-only CTA.
2. **Missing / Blank Referral Links**: Items without link omit broken `<a>` tags; displays disabled notice or clean code-only mode; whitespace link stripped; handles items with neither code nor link.
3. **Date Boundaries & Invalid Formats**: Past expiry dates filtered out; evergreen/empty expiry retained; corrupted date strings coerced without crashing; `VerifyDate` computes maximum valid date; defaults to today when all missing.
4. **Extreme Character Lengths**: 150+ char service names; 600+ char descriptions; 80+ char unbroken codes with `truncate`/`break-all`; long category names; empty descriptions.
5. **Special Characters & XSS Prevention**: `<script>` injection escaped in DOM; quotes and ampersands escaped; Schema.org JSON intact with special chars; Traditional Chinese and Unicode preserved; JavaScript pseudo-protocol links neutralized.
6. **Small Viewports & Responsive Boundaries**: Viewport allows user zoom (WCAG); main containers use `max-w-` without rigid width overflow; single-column on mobile (`grid-cols-1`); category chips wrap or scroll.
7. **Edge Dataset Handling**: Empty items list renders without exception; single item dataset; all items in same category; column alias normalization; missing optional columns defaulted.

**Count**: 35 test cases.

---

### Tier 3: Cross-Feature Interactions (`tests/test_tier3_interaction.py`)
Validates pairwise cross-cutting integrations:
1. **Search + Category Filter**: All DOM cards contain `data-service`, `data-category`, `data-description`.
2. **Dark Mode + Ad Containers**: Ad containers adapt via `dark:` styles to prevent visual glare.
3. **i18n + SEO Hreflang Alignment**: Alternate hreflang tags match client-side translations dictionary (`zh-TW`, `en`).
4. **Ad Containers + Action Buttons Spacing**: Ad containers enforce isolation margin (`my-6`) from interactive copy/link buttons.
5. **Search + 3-State Cards**: All card variants (Code+Link, Code-Only, Link-Only) contain searchable attributes.
6. **Theme Toggle + LocalStorage**: Theme switch logic persists choice in `localStorage.theme`.
7. **Copy Button + Toast Feedback**: Copy button triggers `#toast` container; initial state is `opacity-0`.
8. **Category Filter Reset**: "All" button resets filter while preserving search input.
9. **Footer Links + Sitemap Correspondence**: All compliance pages linked in footer are present in `sitemap.xml`.
10. **Schema Graph + DOM Parity**: Schema `ItemList.numberOfItems` equals total cards rendered in DOM.

**Count**: 10 test cases.

---

### Tier 4: Real-World Application Workloads (`tests/test_tier4_workload.py`)
Validates production static build integrity and external specifications:
1. **Build Pipeline Execution**: `python build.py` executes synchronously under 10s with exit code 0.
2. **Production Artifacts**: `dist/index.html`, `dist/sitemap.xml`, `dist/robots.txt`, `dist/llms.txt`, `dist/banner.png`, `dist/referral.png` exist and are non-empty.
3. **Full HTML5 DOM Structure**: Complete parsing of `dist/index.html` with semantic tags (`header`, `main`, `footer`).
4. **Standalone Trust Pages**: `privacy.html`, `terms.html`, `about.html`, `contact.html`, `disclaimer.html` generated in `dist/`.
5. **Sitemap Protocol 0.9 W3C Standards**: XML schema validation, HTTPS loc, ISO lastmod dates, valid priority and changefreq.
6. **Robots.txt RFC 9309**: Strict line-by-line validation, User-agent, Allow, HTTPS Sitemap reference.
7. **LLM Indexing Guide (`llms.txt`)**: Markdown structure, canonical URL, and AI model extraction guidelines.
8. **Complete Schema.org Graph Validation**: Validates `WebSite`, `CollectionPage`, `ItemList`, `FAQPage`.
9. **Static Asset Resolution**: All `<img>` src and `<link rel="icon">` resolve to real files in `dist/`.
10. **End-to-End Dataset Fidelity**: Every active record from the dataset is present in rendered HTML cards.

**Count**: 10 test cases.

---

## Test Execution Commands

### Run Full E2E Test Suite
```bash
python tests/test_runner.py
```

### Run Specific Tier
```bash
python tests/test_runner.py --tier 1    # Tier 1: Feature Coverage
python tests/test_runner.py --tier 2    # Tier 2: Boundary & Corner Cases
python tests/test_runner.py --tier 3    # Tier 3: Cross-Feature Interactions
python tests/test_runner.py --tier 4    # Tier 4: Real-World Workloads
```

### Run Individual Test Modules (via unittest)
```bash
python tests/test_tier1_feature.py
python tests/test_tier2_boundary.py
python tests/test_tier3_interaction.py
python tests/test_tier4_workload.py
```

### Run with Diagnostic Summary (CI/CD Pipeline)
```bash
python tests/test_runner.py --summary --exit-zero
```

---

## Authoritative Output Sources
1. **Technical SEO Standards**: Google Search Central Guidelines (Title, Meta Description, Canonical URL, Robots meta, Hreflang).
2. **Schema.org Vocabulary**: Schema.org 2026 specs for `WebSite`, `CollectionPage`, `ItemList`, `Offer`, `FAQPage`, `BreadcrumbList`.
3. **Google AdSense Program Policies**: Publisher Policies on Privacy Policy cookie disclosures, low-value thin content mitigation, zero layout shift (CLS = 0), and accidental click prevention (20px+ isolation).
4. **RFC 9309**: Robots Exclusion Protocol standard for crawler directives and sitemap declaration.
5. **Sitemaps.org Protocol 0.9**: W3C standard for multi-URL XML sitemaps.
6. **Interface Contracts 1-3**: Documented in `PROJECT.md`.
