# 💰 Family Budget Dashboard

A beautiful, dark-themed family budget dashboard built with Streamlit and Plotly. Works out of the box with demo data, or connect your own financial data via CSV upload or Google Sheets.

**[🚀 Live Demo](https://budget-dashboard-demo.streamlit.app)** — Try it now with sample data

![Dashboard Preview](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)

## Features

- **📊 KPI Cards** — Spendable balance, credit card status, savings, income, investments
- **🍩 Spending Breakdown** — Interactive donut chart by category
- **🎯 Budget Health Gauge** — Visual indicator of budget utilization (green/yellow/red)
- **🔍 Category Drill-Down** — Click into any category to see sub-categories and individual transactions
- **📋 Fixed Expense Panels** — Expandable breakdowns of recurring bills
- **💳 Debt Tracking** — Progress bars for credit cards and loans
- **📅 Due Date Calendar** — Upcoming bills with paid/due soon/upcoming status
- **🧾 Transaction History** — Paginated, sortable transaction table
- **📆 Month Selector** — View current month, past months, or year-to-date
- **🌙 Dark Theme** — Polished dark UI with glassmorphism effects

## Three Ways to Use It

### 1. 🎲 Demo Mode (Default)
Just run it. Six months of realistic fake transactions are generated automatically. Great for showcasing what the dashboard looks like.

### 2. 📄 CSV Upload
Drag and drop a CSV export from your bank, credit card, Mint, YNAB, or any financial tool. The parser auto-detects common column formats.

### 3. 🔗 Google Sheets (Auto-Sync)
Connect to a Google Sheet for always-up-to-date data. Works great with [Finta](https://www.finta.io/) (auto-syncs bank accounts to Google Sheets) or any spreadsheet with transaction data.

---

## Quick Start

### Run Locally
```bash
git clone https://github.com/spencerjw/budget-dashboard-demo.git
cd budget-dashboard-demo
pip install -r requirements.txt
streamlit run app.py
```

### Deploy to Streamlit Cloud (Free)
1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select your fork, set `app.py` as entrypoint
4. Click **Deploy** — no secrets needed for demo mode

---

## Connecting Your Own Data

### Option A: CSV Upload (Easiest)

Export transactions from your bank or financial tool and upload directly in the app sidebar.

**Supported formats:**
| Source | How to Export |
|--------|-------------|
| **Chase** | Activity → Download → CSV |
| **Amex** | Statements → Download → CSV |
| **Bank of America** | Activity → Export/Download |
| **Mint** | Transactions → Export → CSV |
| **YNAB** | All Accounts → Export → CSV |
| **Any bank** | Look for "Download" or "Export" in transaction history |

**Required CSV columns** (names are flexible, parser auto-detects):
- **Date** — Transaction date (`Date`, `Transaction Date`, `Posted Date`, etc.)
- **Amount** — Dollar amount (`Amount`, `Debit`, `Transaction Amount`, etc.)
- **Description** *(optional but recommended)* — Merchant name (`Description`, `Merchant`, `Payee`, `Name`, etc.)
- **Category** *(optional)* — Spending category (`Category`, `Category Name`, `Type`, etc.)

Example CSV:
```csv
Date,Amount,Description,Category
2025-03-01,-45.23,H-E-B Grocery,Groceries
2025-03-02,-12.50,Chipotle Mexican Grill,Restaurants
2025-03-03,-35.00,Shell Gas Station,Gas & Auto
2025-03-05,-89.99,Amazon.com,Shopping
2025-03-07,3200.00,Direct Deposit Payroll,Income
```

> **Note:** Negative amounts = spending, positive = income/credits. If your bank exports all amounts as positive, the parser handles that automatically.

### Option B: Google Sheets (Auto-Sync with Finta)

This is the most powerful setup — your dashboard updates automatically as transactions come in.

#### Step 1: Set Up Finta ($5.83/month)
1. Sign up at [finta.io](https://www.finta.io/)
2. Connect your bank accounts via Plaid
3. Finta creates a Google Sheet and auto-syncs transactions daily

#### Step 2: Create a Google Cloud Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable the **Google Sheets API**
4. Go to **IAM & Admin → Service Accounts** → Create Service Account
5. Create a JSON key and download it
6. **Share your Finta Google Sheet** with the service account email (read-only is fine)

#### Step 3: Configure the Dashboard

**For local development:**
```bash
# In the sidebar, select "Google Sheets" mode
# Paste your Sheet ID and upload the JSON key file
```

**For Streamlit Cloud deployment:**

Create `.streamlit/secrets.toml` (don't commit this!):
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-sa@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

Or paste the same values into Streamlit Cloud's Secrets management UI.

#### Expected Google Sheet Format

The dashboard expects sheets named `Transactions` (and optionally `Accounts`) with these columns:

**Transactions sheet:**
| Column | Description |
|--------|------------|
| Date | Transaction date |
| Amount | Dollar amount (negative = spending) |
| Merchant or Summary | Transaction description |
| Category Name | Sub-category (e.g., "Groceries") |
| Category Group | Parent category (e.g., "Food & Drink") |

**Accounts sheet** *(optional, for balance cards):*
| Column | Description |
|--------|------------|
| Name | Account name |
| Current Balance | Current balance |
| Account Limit | Credit limit (for credit cards) |
| Account Type | "credit", "depository", "investment", etc. |

> Finta generates this format automatically. If using a custom sheet, match these column names.

---

## Customization

Edit the constants at the top of `app.py` (or use the sidebar):

```python
DEFAULT_FAMILY_NAME = "Anderson"     # Dashboard title
DEFAULT_MONTHLY_INCOME = 9200        # Combined household income

DEFAULT_FIXED_EXPENSES = {           # Your recurring monthly bills
    'Household': {
        'Electric': 218,
        'Internet': 65,
        # ... add your bills
    },
    'Debt Payments': {
        'Mortgage': 2890,
        # ... add your debts
    },
}
```

### Adding More Account Cards
To add real account balances (from Google Sheets), modify the `get_account_balances()` function to match your account names.

### Changing Categories
The demo data uses predefined categories. When using CSV or Google Sheets, categories come from your data. The donut chart and drill-down adapt automatically.

---

## Tech Stack

- **[Streamlit](https://streamlit.io/)** — App framework
- **[Plotly](https://plotly.com/)** — Interactive charts (donut, gauge)
- **[Pandas](https://pandas.pydata.org/)** — Data handling
- **[Google Sheets API](https://developers.google.com/sheets/api)** *(optional)* — Live data connection

## Requirements

```
streamlit>=1.30.0
plotly>=5.18.0
pandas>=2.0.0
google-api-python-client>=2.100.0  # Only for Google Sheets mode
google-auth>=2.23.0                # Only for Google Sheets mode
```

---

## FAQ

**Q: Is my data stored anywhere?**
A: No. CSV uploads are processed in-memory and never saved. Google Sheets connections are read-only. Nothing is logged or transmitted.

**Q: Can I use this without Finta?**
A: Absolutely. CSV upload works with any bank export. You can also connect any Google Sheet — Finta is just one way to automate the data pipeline.

**Q: Does it work on mobile?**
A: Yes. The layout is responsive and works on phones and tablets.

**Q: Can I add more charts / features?**
A: Fork it and go wild. The codebase is a single `app.py` file — easy to modify.

---

## License

MIT — Use it however you want.

---

Built with ☕ and Streamlit
