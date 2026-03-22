# Getting Started

## Demo Mode (No Setup)

1. Open the [live demo](https://budget-dashboard-demo-8nj84cznyyk33y7pacr4ug.streamlit.app/)
2. You'll see sample data for a fictional family (the "Anderson Family Budget")
3. Use the sidebar to switch between **Demo Test Data** and **Try with My Data**
4. In "Try with My Data" mode, enter your own income, bills, and accounts
5. Upload bank transaction CSVs for spending breakdowns (most banks offer CSV export under statements or transaction history — if yours doesn't, screenshot your transactions and ask ChatGPT, Claude, or Gemini to convert them into a CSV)
6. Toggle between **Daily Finances**, **Investments**, and **Groceries** views at the top
7. The Groceries tab shows sample grocery data with price tracking, category breakdowns, and actionable insights

The sidebar controls exist because the demo isn't connected to real bank accounts. In a real setup, everything syncs automatically and the sidebar goes away entirely.

## Production Mode (Your Real Data)

When you set up your own instance, the dashboard connects to your real bank accounts via Finta and runs on autopilot. No sidebar, no manual entry.

### What You'll Need

| Item | Cost | Purpose |
|------|------|---------|
| GitHub account | Free | Host your fork of the code |
| Finta.io account | $5.83/mo | Syncs bank data to Google Sheets via Plaid |
| Google Cloud service account | Free | Reads your Finta Google Sheet |
| Streamlit Cloud account | Free | Hosts your dashboard |

### Step 1: Fork the Repository

Fork [this repo](https://github.com/spencerjw/budget-dashboard-demo) on GitHub. This gives you your own copy to configure.

### Step 2: Set Up Finta

1. Sign up at [finta.io](https://finta.io)
2. Connect your bank accounts (checking, savings, credit cards, loans, investment accounts)
3. Finta creates a Google Sheet that auto-syncs daily with tabs for Accounts, Transactions, Holdings, Balance History, etc.

**About Plaid Security:** Finta uses Plaid to connect to your banks. Plaid is SOC 2 Type II certified, uses bank-level AES-256 encryption, and connects to 12,000+ financial institutions worldwide. It's the same technology behind apps like Venmo, Robinhood, and Coinbase. Your bank credentials are never stored by Finta or this dashboard -- Plaid handles authentication directly with your bank.

**Manual Accounts:** If your bank doesn't support Plaid (some credit unions block it), add a "Manual Accounts" tab to your Finta Google Sheet with columns: Account, Balance, Type, Last Updated. The dashboard reads these automatically.

### Step 3: Create Your Config

```bash
cp config.example.yaml config.yaml
```

Open `config.yaml` and fill in:

```yaml
# Your Finta Google Sheet ID (from the URL: docs.google.com/spreadsheets/d/THIS_PART/edit)
finta_sheet_id: "1ABC123..."

# For local development (Streamlit Cloud uses Secrets instead)
service_account_file: "service-account.json"

family_name: "My Family Budget"
monthly_income: 8000

fixed_expenses:
  Household:
    Electric: 200
    Internet: 80
    # Add all your recurring bills here
  Debt Payments:
    Mortgage: 2000
    Car Payment: 450

due_dates:
  Mortgage: [1, 2000]      # Due on the 1st, $2,000
  Car Payment: [15, 450]   # Due on the 15th, $450
  Credit Card: [22, 0]     # Due on the 22nd, variable amount
```

`config.yaml` is gitignored -- it never gets pushed to GitHub.

### Step 4: Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project (or use an existing one)
3. Enable the **Google Sheets API**
4. Create a **Service Account** (IAM > Service Accounts > Create)
5. Create a JSON key for the service account and download it
6. Open your Finta Google Sheet and share it with the service account email (the one that ends in `@...iam.gserviceaccount.com`). Read-only access is sufficient.

For local development, put the JSON file next to `app.py` and reference it in `config.yaml`.

### Step 5: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click "New app" and select your forked repo
3. Set the main file to `app.py`
4. Go to **Settings > Secrets** and add:

```toml
finta_sheet_id = "your-sheet-id"
family_name = "My Family Budget"
monthly_income = 8000

[gcp_service_account]
type = "service_account"
project_id = "your-project"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-sa@your-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"

[fixed_expenses]
[fixed_expenses.Household]
Electric = 200
Internet = 80

[fixed_expenses.Debt_Payments]
Mortgage = 2000

[due_dates]
[due_dates.Mortgage]
data = [1, 2000]
[due_dates.Car_Payment]
data = [15, 450]
```

5. Deploy. Your dashboard will auto-sync data from Finta every 15 minutes.

### Step 6: (Optional) 401(k) Fund Tracking

If your 401(k) is connected via Finta/Plaid, per-fund prices are often not available (Plaid provides share counts but not NAVs for employer retirement plans). To get estimated per-fund values:

Add a `fund_ticker_map` to your config:

```yaml
fund_ticker_map:
  "Vanguard Target Ret 2045": "VTIVX"
  "Fidelity Mid Cap Index Fund": "FSMDX"
```

The dashboard will look up public NAVs via Yahoo Finance and scale them proportionally to match your actual account balance. The percentages are accurate; dollar values are estimates based on public NAVs.

## Step 7: (Optional) Grocery Price Tracker

Track your grocery spending over time by connecting a Google Sheet with your order data.

### Setting Up Your Grocery Sheet

Create a Google Sheet with two tabs:

**Items tab** -- one row per line item from each grocery order:
| Column | Example | Description |
|--------|---------|-------------|
| `order_date` | 2026-01-03 | Date of the order |
| `store` | Walmart | Store name |
| `item_name_raw` | Great Value Frozen Broccoli Florets, 12 oz | Exact item name from receipt |
| `item_normalized` | frozen broccoli florets | Canonical name for matching across orders |
| `brand` | Great Value | Brand name (or empty) |
| `category` | Frozen | Produce, Meat, Dairy, Frozen, Snacks, Beverages, Pantry, Household, or Health/Beauty |
| `qty` | 3 | Quantity purchased |
| `size_value` | 12 | Numeric size |
| `size_unit` | oz | oz, lb, fl oz, count, each, pack |
| `line_total` | 3.48 | Total price for this line |
| `unit_price` | 1.16 | Price per unit (line_total / qty) |
| `price_per_oz` | 0.097 | Normalized price per oz (if applicable) |
| `price_per_lb` | 1.55 | Normalized price per lb (if applicable) |
| `weight_adjusted` | FALSE | TRUE if produce/meat with variable weight |
| `substitution` | FALSE | TRUE if store substituted the item |

**Orders tab** -- one row per weekly order:
| Column | Example |
|--------|---------|
| `order_date` | 2026-01-03 |
| `store` | Walmart |
| `subtotal` | 341.94 |
| `savings` | 22.45 |
| `tax` | 3.84 |
| `total` | 323.33 |
| `item_count` | 47 |

### Connecting to Your Dashboard

1. Share the Google Sheet with your service account email (same one used for Finta)
2. Add `grocery_sheet_id` to your Streamlit Secrets or `config.yaml`:
   ```toml
   grocery_sheet_id = "your-grocery-sheet-id-from-url"
   ```
3. The Groceries tab will show your real data with weekly spend trends, category breakdowns, repeat item tracking, price alerts, and auto-generated actionable insights.

**💡 AI Tip:** Don't type this data by hand. Most online grocery services (Walmart, Instacart, Amazon Fresh, H-E-B, etc.) let you view or export your order history. Screenshot it, save the page as a PDF, or copy the text, then feed it into an AI assistant like ChatGPT, Claude, or Google Gemini with a prompt like:

> "Extract every item from this grocery order into a CSV with columns: order_date, store, item_name_raw, item_normalized, brand, category, qty, size_value, size_unit, line_total, unit_price. Also extract the order total, subtotal, savings, and tax."

One prompt can turn months of receipts into a ready-to-import spreadsheet in minutes. You can paste the CSV directly into Google Sheets.

## What Changes in Production Mode

| Feature | Demo | Production |
|---------|------|------------|
| Sidebar | Full controls | Hidden |
| Data source | Fake data / manual CSV | Finta auto-sync |
| Bills & income | Enter in sidebar | From config.yaml |
| Investments | Sample data | Real holdings + NAV lookups |
| Groceries | Sample data (8 weeks) | Your real grocery orders from Google Sheet |
| Refresh | Manual | Every 15 minutes |
| Setup time | 0 minutes | ~15 minutes |

## Troubleshooting

**"Could not load Finta data"**: Check that your Google Sheet is shared with the service account email and that the sheet ID is correct.

**Missing transactions**: Finta syncs daily. New transactions may take up to 24 hours to appear.

**401(k) shows no fund values**: Add `fund_ticker_map` to your config. Without it, you'll see share counts but no dollar values per fund.

**Bank not supported by Plaid**: Some credit unions and smaller banks block Plaid connections. Add a "Manual Accounts" tab to your Finta Google Sheet as a workaround.
