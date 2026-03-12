# 💰 Budget Dashboard

A dark-themed personal budget dashboard built with Streamlit and Plotly. Works out of the box with demo data, or enter your own finances -- everything stays in your browser.

**[🚀 Live Demo](https://budget-dashboard-demo-ltc4jkyc8bajang468zh7v.streamlit.app/)** — Try it now with sample data *(right-click → "Open in new tab" to keep this page open)*

![Dashboard Preview](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)

## Features

- **📊 KPI Cards** — Spendable balance, credit usage, savings, income, investments
- **🍩 Spending Breakdown** — Interactive donut chart by category
- **🎯 Budget Health Gauge** — Visual budget health (green/yellow/red)
- **🔍 Category Drill-Down** — Click any category to see sub-categories and transactions
- **📋 Fixed Expense Panels** — Expandable breakdowns of recurring bills
- **💳 Debt Tracking** — Progress bars for credit cards and loans with due dates
- **📅 Due Date Calendar** — Upcoming bills with paid/due soon/upcoming status
- **🧾 Transaction History** — Paginated transaction table
- **📆 Month Selector** — View current month, past months, or year-to-date
- **📄 Multi-CSV Upload** — Upload transactions from multiple bank accounts at once
- **💾 Auto-Save** — Settings save automatically in your browser via localStorage
- **🔒 Privacy First** — No accounts, no servers, no tracking. Data never leaves your browser.
- **🌙 Dark Theme** — Polished dark UI with glassmorphism effects

## 🆕 New to Budgeting?

Check out the **[Getting Started Guide](GETTING-STARTED.md)** — a step-by-step walkthrough from "I've never tracked money" to a working dashboard. No finance background needed. No coding.

---

## How to Use It

### Just Want to See the Demo?
Click the **[Live Demo](https://budget-dashboard-demo-ltc4jkyc8bajang468zh7v.streamlit.app/)** link. It loads with sample data for a fictional family. Nothing to install.

### Want to Track Your Own Budget?

**Everything is done through the sidebar — no code to edit.**

1. Open the [dashboard](https://budget-dashboard-demo-ltc4jkyc8bajang468zh7v.streamlit.app/)
2. Click the **>** arrow (top left) to open the sidebar
3. Click **💰 My Budget** to switch from demo mode
4. Fill in your income, bills, accounts, and due dates using the sidebar forms
5. Your settings **auto-save in your browser** — they'll be there next time you visit
6. Optionally upload CSVs from your bank(s) to see spending breakdowns

That's it. No account to create, no software to install, no code to write.

---

## Uploading Your Transactions (CSV)

This powers the spending donut chart, category drill-down, and transaction history. It's optional — the dashboard works without it for tracking bills, accounts, and due dates.

**You can upload multiple files at once** — one from each bank account or credit card.

### How to Get Your CSV

1. **Log into your bank's website** (or credit card website)
2. **Go to your transaction history** (usually called "Activity" or "Transactions")
3. **Look for a "Download" or "Export" button** — choose **CSV** format
4. **In the dashboard sidebar**, drop your CSV(s) into the upload area

**Where to find the download button at common banks:**

| Bank / Card | Where to Look |
|-------------|--------------|
| **Chase** | Log in → Activity → click the ⬇️ download icon at the top → choose CSV |
| **Bank of America** | Log in → Activity tab → "Download" link near the top right → CSV |
| **Wells Fargo** | Log in → Account Activity → "Download" button → Comma Delimited |
| **Capital One** | Log in → "View Transactions" → "Download Transactions" link → CSV |
| **Amex** | Log in → "Statements & Activity" → "Download your Transactions" → CSV |
| **USAA** | Log in → Transactions tab → "Export" button → CSV |
| **Discover** | Log in → "Recent Activity" → "Download" → CSV |
| **Citi** | Log in → "View Account Activity" → "Download" link → CSV |
| **Credit unions** | Look for "Export," "Download," or "Save Transactions" in your transaction history |

### What Format Does the CSV Need?

The dashboard auto-detects most bank formats. It looks for columns like:

- A **date** column (called "Date," "Transaction Date," "Posted Date," etc.)
- An **amount** column (called "Amount," "Debit," "Transaction Amount," etc.)
- A **description** column (called "Description," "Merchant," "Payee," "Name," etc.)
- A **category** column (optional — called "Category," "Type," etc.)

If your bank's CSV has these columns (most do), it'll work. You don't need to rename anything.

---

## Saving & Transferring Your Settings

**Settings save automatically** in your browser's localStorage. Close the tab, come back tomorrow — everything's still there.

**Moving to another device or your own private dashboard:**
1. In the sidebar, scroll to **🚀 Take It With You**
2. Click **⬇️ Download My Settings** to save a JSON file
3. On the new device, upload that file with **⬆️ Load Settings File**

**Clearing your browser data** (history, cookies, etc.) will erase your settings. Download a backup first if you do this regularly.

---

## Auto-Sync with Finta (Advanced — Optional)

> **This section is for people comfortable with Google accounts and spreadsheets.** Most people should stick with CSV upload — it's simpler and works great.

[Finta](https://www.finta.io/) ($5.83/month) connects to your bank accounts and automatically writes transactions into a Google Sheet daily. See the full setup instructions in the [Getting Started Guide](GETTING-STARTED.md#auto-sync-advanced--optional).

---

## Deploy Your Own Private Copy

If you want your own dashboard URL that nobody else can see:

1. Create free accounts at **[github.com](https://github.com)** and **[streamlit.io](https://streamlit.io)**
2. Go to the [dashboard repo](https://github.com/spencerjw/budget-dashboard-demo) and click **"Fork"** (top right)
3. Go to **[share.streamlit.io](https://share.streamlit.io)** and click **"New app"**
4. Select your fork, branch `main`, file `app.py`
5. Click **Deploy**

Set it to **invite-only** in Settings → Sharing if you're entering real financial data.

---

## FAQ

**Is my data stored on a server?**
No. Settings save in your browser's localStorage. CSV uploads are processed in-memory. Nothing is sent to any server.

**Can I use this on my phone?**
Yes. The layout adjusts automatically.

**Can I track multiple bank accounts?**
Yes. Upload CSVs from each account — the dashboard merges them automatically.

**Does it work without uploading any CSV?**
Yes. Enter your income, bills, accounts, and due dates in the sidebar. The spending breakdown and transaction history need transaction data, but everything else works.

---

## Templates

The `templates/` folder includes starter files:
- **`fixed-expenses-template.csv`** — Common recurring bills with examples
- **`transactions-template.csv`** — Sample transaction format
- **`accounts-template.csv`** — Account balances template

## Tech Stack

- **[Streamlit](https://streamlit.io/)** — App framework
- **[Plotly](https://plotly.com/)** — Interactive charts
- **[Pandas](https://pandas.pydata.org/)** — Data handling

## License

MIT — Use it however you want.
