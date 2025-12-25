# Referral Code Dashboard

A lightweight, static referral code dashboard automated with GitHub Actions.

## Features
- **Static HTML**: Ultra-fast and secure.
- **Automated**: Updates daily from Google Sheets via GitHub Actions.
- **Search & Filter**: Instant client-side search and category filtering.
- **Responsive**: Mobile-friendly design with Tailwind CSS.

## Setup Guide

### 1. Data Source (Google Sheets)
1. Create a Google Sheet with the following headers:
   `Service`, `Category`, `Description`, `Code`, `Link`
2. Fill in your data.
3. Click **File** > **Share** > **Publish to web**.
4. Select **Entire Document** (or specific sheet) and choose **Comma-separated values (.csv)**.
5. Click **Publish** and copy the generated link.

### 2. GitHub Configuration
1. Push this code to a new GitHub repository.
2. Go to **Settings** > **Secrets and variables** > **Actions**.
3. Create a **New repository secret** (or Variable for public sheets):
   - Name: `GOOGLE_SHEET_CSV_URL`
   - Value: (Paste your CSV link from Step 1)
   > Note: If you don't set this, the build will use `data_example.csv` by default.

### 3. Enable GitHub Pages
1. The workflow will automatically create/update a `gh-pages` branch after the first run.
2. Go to **Settings** > **Pages**.
3. Under **Source**, select `Deploy from a branch`.
4. Select `gh-pages` branch and `/ (root)` folder.
5. Click **Save**.
6. Your site will be live at `https://<your-username>.github.io/<repo-name>/`.

### Local Development
To run locally:
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the build script:
   ```bash
   python build.py
   ```
3. Open `index.html` in your browser.
