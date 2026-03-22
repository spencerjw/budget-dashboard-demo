# Getting Started

Every section of this guide where you need to prepare data or configure something has a 💡 **AI Tip** showing how tools like [ChatGPT](https://chat.openai.com), [Claude](https://claude.ai), [Google Gemini](https://gemini.google.com), or [Microsoft Copilot](https://copilot.microsoft.com) can speed up the process. If you get stuck at any point, paste the relevant section of this guide into an AI assistant and ask for help -- that's what they're built for.

## Demo Mode (No Setup)

1. Open the [live demo](https://budget-dashboard-demo-8nj84cznyyk33y7pacr4ug.streamlit.app/)
2. You'll see sample data for a fictional family (the "Anderson Family Budget")
3. Use the sidebar to switch between **Demo Test Data** and **Try with My Data**
4. In "Try with My Data" mode, enter your own income, bills, and accounts
5. Upload bank transaction CSVs for spending breakdowns
6. Toggle between **Daily Finances**, **Investments**, and **Groceries** views at the top
7. The Groceries tab shows sample grocery data with price tracking, category breakdowns, and actionable insights

💡 **AI Tip:** Most banks offer CSV export under statements or transaction history. If yours doesn't, screenshot your transactions or save them as a PDF and ask an AI tool: *"Convert these bank transactions into a CSV with columns: Date, Amount, Merchant, Category."* It'll parse the image or text and give you a clean file to upload.

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

💡 **AI Tip:** Never used GitHub? Ask an AI assistant: *"Walk me through forking a GitHub repo and cloning it to my computer step by step."* It'll give you instructions specific to your operating system.

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

💡 **AI Tip:** Not sure how to organize your expenses or what counts as "fixed" vs "variable"? Paste your last few months of bank statements (or a screenshot of your recurring charges) into an AI tool and ask: *"Identify my recurring monthly bills and organize them into categories. Format them as YAML like this:"* then paste the config.example.yaml structure. It'll build your config section for you, properly formatted and categorized.

### Step 4: Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project (or use an existing one)
3. Enable the **Google Sheets API**
4. Create a **Service Account** (IAM > Service Accounts > Create)
5. Create a JSON key for the service account and download it
6. Open your Finta Google Sheet and share it with the service account email (the one that ends in `@...iam.gserviceaccount.com`). Read-only access is sufficient.

For local development, put the JSON file next to `app.py` and reference it in `config.yaml`.

💡 **AI Tip:** Google Cloud Console can be overwhelming if you've never used it. Ask an AI assistant: *"Walk me through creating a Google Cloud project, enabling the Sheets API, and creating a service account with a JSON key. Step by step for a beginner."* It'll guide you through every screen.

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

💡 **AI Tip:** Streamlit Secrets use TOML format, which looks different from YAML. If you're having trouble converting, paste your `config.yaml` into an AI tool and ask: *"Convert this YAML config into Streamlit TOML secrets format, including the fixed_expenses and due_dates sections."*

### Step 6: (Optional) 401(k) Fund Tracking

If your 401(k) is connected via Finta/Plaid, per-fund prices are often not available (Plaid provides share counts but not NAVs for employer retirement plans). To get estimated per-fund values:

Add a `fund_ticker_map` to your config:

```yaml
fund_ticker_map:
  "Vanguard Target Ret 2045": "VTIVX"
  "Fidelity Mid Cap Index Fund": "FSMDX"
```

The dashboard will look up public NAVs via Yahoo Finance and scale them proportionally to match your actual account balance. The percentages are accurate; dollar values are estimates based on public NAVs.

💡 **AI Tip:** Not sure what ticker symbol maps to your 401(k) funds? Paste your fund names into an AI tool and ask: *"What are the public ticker symbols for these retirement funds?"* Most employer 401(k) funds have publicly traded equivalents.

### Step 7: (Optional) Grocery Price Tracker

Track your grocery spending over time by connecting a Google Sheet with your order data.

#### Where to Get Your Data

Most online grocery services keep your full order history:
- **Walmart** -- Account > Purchase History (can view/export each order)
- **Instacart** -- Your Orders page shows itemized receipts
- **Amazon Fresh** -- Order history in your Amazon account
- **H-E-B** -- Order history in the H-E-B app or website
- **Kroger/Ralph's/Fred Meyer** -- Purchase history in your Kroger account
- **Costco** -- Warehouse receipts + Instacart for delivery orders

You can screenshot these, save as PDF, or copy the text.

💡 **AI Tip:** This is where AI saves you the most time. Take your order history (screenshots, PDFs, copied text, email receipts -- whatever you have) and feed it into ChatGPT, Claude, or Gemini with this prompt:

> *"Here's my grocery order from [store]. Extract every item into a CSV with these columns: order_date, store, item_name_raw, item_normalized, brand, category, qty, size_value, size_unit, line_total, unit_price. For item_normalized, use lowercase with no brand or size info (e.g., 'frozen broccoli florets'). For category, use one of: Produce, Meat, Dairy, Frozen, Snacks, Beverages, Pantry, Household, Health/Beauty. Also give me a summary row with: order_date, store, subtotal, savings, tax, total, item_count."*

One prompt per order. Paste the CSV output into your Google Sheet. If you have months of orders, batch several into one prompt -- most AI tools can handle 10+ receipts at once.

#### Setting Up Your Grocery Sheet

Create a Google Sheet with two tabs:

**Items tab** -- one row per line item from each grocery order:

| Column | Example | Description |
|--------|---------|-------------|
| `order_date` | 2026-01-03 | Date of the order |
| `store` | Walmart | Store name |
| `item_name_raw` | Great Value Frozen Broccoli Florets, 12 oz | Exact item name from receipt |
| `item_normalized` | frozen broccoli florets | Canonical name for matching across orders |
| `brand` | Great Value | Brand name (or empty) |
| `category` | Frozen | One of: Produce, Meat, Dairy, Frozen, Snacks, Beverages, Pantry, Household, Health/Beauty |
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

💡 **AI Tip:** Don't want to set up the sheet structure manually? Ask an AI tool: *"Create a Google Sheets template with two tabs matching this schema: [paste the tables above]. Give me the column headers I should put in row 1 of each tab."* Or even simpler -- paste your first grocery receipt and ask it to give you the complete sheet with headers and data already filled in.

#### Connecting to Your Dashboard

1. Share the Google Sheet with your service account email (same one used for Finta)
2. Add `grocery_sheet_id` to your Streamlit Secrets or `config.yaml`:
   ```toml
   grocery_sheet_id = "your-grocery-sheet-id-from-url"
   ```
3. The Groceries tab will show your real data with weekly spend trends, category breakdowns, repeat item tracking, price alerts, and auto-generated actionable insights.

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

💡 **AI Tip:** Before digging through forums, paste your error message into an AI assistant with context like: *"I'm setting up a Streamlit budget dashboard that connects to Google Sheets. I'm getting this error: [paste error]."* AI tools are excellent at diagnosing config issues, permission problems, and deployment errors.

**"Could not load Finta data"**: Check that your Google Sheet is shared with the service account email and that the sheet ID is correct.

**Missing transactions**: Finta syncs daily. New transactions may take up to 24 hours to appear.

**Grocery tab shows demo data in production**: Make sure `grocery_sheet_id` is set in your secrets and the sheet is shared with the service account.

**401(k) shows no fund values**: Add `fund_ticker_map` to your config. Without it, you'll see share counts but no dollar values per fund.

**Bank not supported by Plaid**: Some credit unions and smaller banks block Plaid connections. Add a "Manual Accounts" tab to your Finta Google Sheet as a workaround.
