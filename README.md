# 💰 Family Budget Dashboard

A dark-themed personal finance dashboard built with Streamlit and Plotly. Works as a live demo with sample data, or connect your real bank accounts for a fully automated personal dashboard.

**🚀 [Live Demo](https://budget-dashboard-demo-8nj84cznyyk33y7pacr4ug.streamlit.app/)** -- Try it now with sample data

## Built for the AI Era

This dashboard is designed to work hand-in-hand with AI tools. You don't need to be a developer or a spreadsheet wizard to get your financial data organized. Throughout this guide, you'll see 💡 **AI Tips** showing where tools like [ChatGPT](https://chat.openai.com), [Claude](https://claude.ai), [Google Gemini](https://gemini.google.com), or [Microsoft Copilot](https://copilot.microsoft.com) can do the heavy lifting for you -- turning messy bank statements into clean CSVs, extracting grocery receipts into structured data, or helping you categorize months of transactions in seconds.

If you've never used AI for personal finance tasks, this is a great place to start. The data prep that used to take hours now takes minutes.

## Two Modes, One Codebase

### Demo Mode (Default)
Open the app and explore immediately. No setup required.
- Sidebar with **Demo Test Data** (sample family) or **Try with My Data** (manual entry)
- Upload bank transaction CSVs for spending analysis
- Customize bills, due dates, accounts, and income in the sidebar
- Toggle between **Daily Finances**, **Long-Term Investments**, and **Grocery Price Tracker** views
- Everything stays in your browser. No accounts, no servers, no tracking.

### Production Mode (Your Real Data)
Fork the repo, add your config, and get a fully automated dashboard synced to your real bank accounts.
- Connects to **Finta.io** for automatic bank/brokerage syncing via Plaid
- No sidebar. No manual entry. Data refreshes automatically.
- Fixed expenses, due dates, and income loaded from a simple `config.yaml`
- Investment holdings with real-time NAV lookups for 401(k) funds
- **Grocery Price Tracker** with your own store order data via Google Sheets
- Same dark theme and features as the demo, powered by real data

## Features

### 💵 Daily Finances
- **KPI Cards** -- Spendable balance, credit usage, savings, income, investments
- **Spending Donut** -- Interactive breakdown by category with drill-down
- **Budget Health Gauge** -- Visual green/yellow/red budget status
- **Category Drill-Down** -- Click any category for sub-categories and transactions
- **Fixed Expense Panels** -- Expandable breakdowns of recurring bills
- **Credit & Debt Tracking** -- Progress bars for cards and loans with due dates
- **Upcoming Due Dates** -- Next 14 days shown by default, expandable for all bills (with dollar amounts)
- **Transaction History** -- Paginated table with merchant, category, and amount
- **Month Selector** -- Current month, past months, or year-to-date

### 📈 Investments
- **Portfolio Total** -- Aggregate value across all connected accounts
- **Account Cards** -- Balance, subtype, and source for each investment account
- **Holdings Drill-Down** -- Expand any account to see individual holdings, quantities, and values
- **Allocation Donut** -- Visual portfolio allocation breakdown
- **Balance History Snapshot** -- Track changes with timestamps
- **401(k) NAV Lookups** -- Real-time fund pricing via Yahoo Finance with ticker mapping

### 🛒 Grocery Price Tracker
- **Weekly Spend Trend** -- Line chart of order totals with savings overlay
- **Category Breakdown** -- Stacked bar chart by week (Produce, Meat, Dairy, Frozen, Snacks, Beverages, Pantry, Household, Health/Beauty)
- **Repeat Item Tracker** -- Top 25 most-purchased items with avg vs last price, trend indicators, and sparkline price history
- **Price Alerts** -- Flags items with >10% deviation from their running average (red = up, green = down)
- **Actionable Insights** -- Auto-generated data-driven findings: monthly spend estimate, top categories, price increases/drops, savings rate analysis, and smart recommendations

### General
- **Mobile Responsive** -- Works on phone screens
- **Dark Theme** -- Easy on the eyes, looks great on any device
- **Demo Mode** -- Explore with sample data, no setup required

## Quick Start (Production)

Setup takes about 15 minutes. If any step feels unfamiliar, paste these instructions into an AI assistant and ask it to walk you through it -- that's what they're for.

### 1. Fork this repo
Click **Fork** on GitHub. Clone your fork locally.

💡 **AI Tip:** New to GitHub? Ask an AI assistant: *"Walk me through forking a GitHub repo and cloning it to my computer."* It'll give you step-by-step instructions for your operating system.

### 2. Set up Finta.io
- Create an account at [finta.io](https://finta.io) ($5.83/mo)
- Connect your bank accounts (checking, savings, credit cards, loans, brokerages)
- Finta syncs to a Google Sheet automatically

Finta uses **Plaid** under the hood -- the same secure bank connection layer trusted by Chase, Vanguard, and thousands of financial institutions. Plaid is SOC 2 Type II certified and connects to 12,000+ institutions.

### 3. Create your config
```bash
cp config.example.yaml config.yaml
```
Edit `config.yaml` with your:
- Finta Google Sheet ID (from the sheet URL)
- Monthly income
- Fixed expenses (organized by category)
- Bill due dates with amounts
- (Optional) 401(k) fund ticker mappings for NAV lookups

`config.yaml` is gitignored -- your financial details never touch GitHub.

💡 **AI Tip:** Not sure how to organize your fixed expenses or what counts as a "fixed" vs "variable" expense? Paste your last 3 months of bank statements into ChatGPT or Claude and ask: *"Identify my recurring monthly bills and categorize them. Format them as YAML like this: [paste the config.example.yaml format]."* It'll build your config for you.

### 4. Set up Google Service Account
- Create a service account in Google Cloud Console
- Download the JSON key
- Share your Finta Google Sheet with the service account email (read-only)
- Reference the key file in `config.yaml` (local) or add it to Streamlit Secrets (cloud)

💡 **AI Tip:** Google Cloud Console can be intimidating if you haven't used it before. Ask an AI assistant: *"Walk me through creating a Google Cloud service account with Sheets API access, step by step with screenshots descriptions."* It'll guide you through every click.

### 5. Deploy to Streamlit Cloud
- Connect your forked repo at [share.streamlit.io](https://share.streamlit.io)
- Add your config as **Streamlit Secrets** (Settings > Secrets):
  - Paste your `config.yaml` contents
  - Add `[gcp_service_account]` section with your service account JSON
- Deploy. Your dashboard auto-syncs with Finta every 15 minutes.

💡 **AI Tip:** Streamlit Secrets use TOML format, which is slightly different from YAML. If you're having trouble converting your config, paste your `config.yaml` into an AI tool and ask: *"Convert this YAML to Streamlit TOML secrets format."*

## Configuration Reference

See [`config.example.yaml`](config.example.yaml) for a complete template with comments.

| Setting | Required | Description |
|---------|----------|-------------|
| `finta_sheet_id` | Yes | Your Finta Google Sheet ID |
| `service_account_file` | Local only | Path to Google service account JSON |
| `family_name` | No | Dashboard title (default: "Family Budget") |
| `monthly_income` | Yes | Combined monthly take-home pay |
| `fixed_expenses` | Yes | Recurring bills organized by category |
| `due_dates` | No | Bill names with [day, amount] pairs |
| `ploc_limit` | No | Line of credit limit (enables PLOC tracking) |
| `fund_ticker_map` | No | 401(k) fund-to-ticker mappings for NAV lookups |
| `grocery_sheet_id` | No | Google Sheet ID for grocery price tracking data |

## Grocery Price Tracker Setup

The Grocery Price Tracker works with any Google Sheet containing your grocery order data. In demo mode, it displays sample data automatically.

### For Production Mode

1. Create a Google Sheet with two tabs:
   - **Items** -- Columns: `order_date`, `store`, `item_name_raw`, `item_normalized`, `brand`, `category`, `qty`, `size_value`, `size_unit`, `line_total`, `unit_price`, `price_per_oz`, `price_per_lb`, `weight_adjusted`, `substitution`
   - **Orders** -- Columns: `order_date`, `store`, `subtotal`, `savings`, `tax`, `total`, `item_count`
2. Share the sheet with your Google service account email (the same one used for Finta)
3. Add `grocery_sheet_id` to your `config.yaml` or Streamlit Secrets:
   ```yaml
   grocery_sheet_id: "your-grocery-sheet-id"
   ```

The dashboard reads the sheet on each page load and auto-generates insights including price trend analysis, category breakdowns, and actionable recommendations.

💡 **AI Tip:** Don't build your grocery sheet by hand. Most online grocery services (Walmart, Instacart, Amazon Fresh, H-E-B, Kroger, etc.) let you export or screenshot your order history. Feed those exports, PDFs, or screenshots into an AI tool and ask it to extract the items into a CSV matching the schema above. One prompt can turn months of receipts into structured data in minutes. Example prompt:

> *"Here's my Walmart order history. Extract every item into a CSV with columns: order_date, store, item_name_raw, item_normalized, brand, category, qty, size_value, size_unit, line_total, unit_price. Normalize the item names (lowercase, no brand, no size info). Categorize each item as Produce, Meat, Dairy, Frozen, Snacks, Beverages, Pantry, Household, or Health/Beauty. Also create a separate summary CSV with: order_date, store, subtotal, savings, tax, total, item_count."*

## Security

- **Demo mode**: Everything stays in your browser via `localStorage`. No server, no cookies, no tracking.
- **Production mode**: Your financial data lives in your Finta Google Sheet (your Google account). The dashboard reads it read-only via a service account. No data is stored in the app code.
- **Config**: `config.yaml` and service account keys are gitignored. On Streamlit Cloud, use encrypted Secrets.
- **Plaid**: SOC 2 Type II certified, bank-level encryption, used by major financial apps worldwide.

## Troubleshooting

Having issues? Before digging through docs, try pasting the error message into an AI assistant with context like *"I'm setting up a Streamlit dashboard that connects to Google Sheets via a service account. I'm getting this error: [error]."* AI tools are excellent at diagnosing config issues, permission errors, and deployment problems.

Common issues:

- **"Could not load Finta data"** -- Check that your Google Sheet is shared with the service account email and that the sheet ID is correct.
- **Missing transactions** -- Finta syncs daily. New transactions may take up to 24 hours to appear.
- **Grocery tab shows demo data in production** -- Make sure `grocery_sheet_id` is set in your secrets and the sheet is shared with the service account.
- **401(k) shows no fund values** -- Add `fund_ticker_map` to your config. Without it, you'll see share counts but no dollar values per fund.

## Tech Stack

- [Streamlit](https://streamlit.io) -- App framework
- [Plotly](https://plotly.com) -- Charts and visualizations
- [Finta.io](https://finta.io) -- Bank data sync (production mode)
- [Plaid](https://plaid.com) -- Secure bank connections (via Finta)
- [yfinance](https://github.com/ranaroussi/yfinance) -- Fund NAV lookups (production mode)

## License

MIT
