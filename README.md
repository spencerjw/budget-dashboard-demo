# 💰 Family Budget Dashboard

A beautiful, dark-themed family budget dashboard built with Streamlit and Plotly. Works out of the box with demo data, or connect your own financial data via CSV upload.

**[🚀 Live Demo](https://budget-dashboard-demo-ltc4jkyc8bajang468zh7v.streamlit.app/)** — Try it now with sample data

![Dashboard Preview](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)

## Features

- **📊 KPI Cards** — Spendable balance, credit card status, savings, income, investments
- **🍩 Spending Breakdown** — Interactive donut chart by category
- **🎯 Budget Health Gauge** — Visual budget health (green/yellow/red)
- **🔍 Category Drill-Down** — Click into any category to see sub-categories and individual transactions
- **📋 Fixed Expense Panels** — Expandable breakdowns of recurring bills
- **💳 Debt Tracking** — Progress bars for credit cards and loans
- **📅 Due Date Calendar** — Upcoming bills with paid/due soon/upcoming status
- **🧾 Transaction History** — Paginated transaction table
- **📆 Month Selector** — View current month, past months, or year-to-date
- **💾 Auto-Save** — Settings save automatically in your browser. Come back tomorrow, everything's still there.
- **🌙 Dark Theme** — Polished dark UI with glassmorphism effects

## 🆕 New to Budgeting?

Check out the **[Getting Started Guide](GETTING-STARTED.md)** — a step-by-step walkthrough from "I've never tracked money" to a working dashboard. No finance background needed. No coding.

---

## How to Use It

### Just Want to See the Demo?
Click the **[Live Demo](https://budget-dashboard-demo-ltc4jkyc8bajang468zh7v.streamlit.app/)** link. It loads with 6 months of realistic sample data. Nothing to install.

### Want to Track Your Own Budget?

**Everything is done through the sidebar — no code to edit.**

1. Open the [dashboard](https://budget-dashboard-demo-ltc4jkyc8bajang468zh7v.streamlit.app/)
2. Click the **>** arrow (top left) to open the sidebar
3. Switch from "Demo Data" to "Upload My CSV"
4. Fill in your income, bills, accounts, and due dates using the forms
5. Your settings **auto-save in your browser** — they'll be there next time you visit
6. Optionally upload a CSV from your bank to see your spending breakdown

That's it. No account to create, no software to install, no code to write.

---

## Uploading Your Transactions (CSV)

This powers the spending donut chart, category drill-down, and transaction history. It's optional — the dashboard works without it.

### How to Get Your CSV

1. **Log into your bank's website** (or credit card website)
2. **Go to your transaction history** (usually called "Activity" or "Transactions")
3. **Look for a "Download" or "Export" button** — choose **CSV** format
4. **In the dashboard sidebar**, click the file upload area and select your downloaded CSV

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

**Tip:** If you use a credit card for most purchases, download those transactions — that's where most of your spending data lives.

**Tip:** Most banks let you filter by date range. Download the current month, or the last 3 months if you want more history.

### What Format Does the CSV Need?

The dashboard auto-detects most bank formats. It looks for columns like:

- A **date** column (called "Date," "Transaction Date," "Posted Date," etc.)
- An **amount** column (called "Amount," "Debit," "Transaction Amount," etc.)
- A **description** column (called "Description," "Merchant," "Payee," "Name," etc.)
- A **category** column (optional — called "Category," "Type," etc.)

If your bank's CSV has these columns (most do), it'll work. You don't need to rename anything.

**Example of what a CSV looks like if you open it in Excel or Google Sheets:**

| Date | Amount | Description | Category |
|------|--------|-------------|----------|
| 2025-03-01 | -45.23 | H-E-B Grocery | Groceries |
| 2025-03-02 | -12.50 | Chipotle | Restaurants |
| 2025-03-03 | -35.00 | Shell Gas | Gas |
| 2025-03-07 | 3,200.00 | Direct Deposit | Income |

Negative = money you spent. Positive = money you received. If your bank shows all amounts as positive, the dashboard handles that automatically.

---

## Saving Your Settings

**Your settings save automatically.** When you fill in your income, bills, accounts, and due dates in the sidebar, they're stored in your browser. Close the tab, come back tomorrow — everything's still there.

**Switching devices?** (e.g., set it up on your laptop, want to use on your phone)
1. On the device that has your settings: open the sidebar → "Backup & Transfer" → "Download Backup"
2. On the new device: open the sidebar → "Backup & Transfer" → upload the file

**Clearing your browser data** (history, cookies, etc.) will erase your settings. Use the backup option if you do this regularly.

---

## Auto-Sync with Finta (Advanced — Optional)

> **This section is for people comfortable with Google accounts and spreadsheets.** Most people should stick with CSV upload — it's simpler and works great. Come back to this if you want the dashboard to update automatically without manual CSV uploads.

[Finta](https://www.finta.io/) is a service ($5.83/month) that connects to your bank accounts and automatically writes your transactions into a Google Sheet every day. Pair it with this dashboard and you never have to manually download CSVs again.

### What You'll Need

- A Google account (Gmail)
- A credit card for the Finta subscription ($5.83/month)
- About 30 minutes for the initial setup

### Step 1: Sign Up for Finta

1. Go to **[finta.io](https://www.finta.io/)** and click "Get Started"
2. Create an account with your email
3. Finta will ask you to connect your bank accounts. It uses **Plaid** to do this — the same secure service that Venmo, Cash App, and most financial apps use. Your bank login credentials go to Plaid, not to Finta.
4. Select which accounts you want to sync (checking, savings, credit cards — whatever you want to track)
5. Finta will ask you to connect a Google Sheet. Sign in with your Google account and give it permission.
6. Finta creates a Google Sheet in your Google Drive called something like "Finta - Transactions." **Leave this sheet alone** — Finta updates it automatically.

After setup, Finta syncs your transactions daily. You can see them in the Google Sheet anytime by going to [drive.google.com](https://drive.google.com) and opening the Finta sheet.

### Step 2: Create a Google Service Account (So the Dashboard Can Read Your Sheet)

The dashboard needs permission to read your Google Sheet. You do this by creating a "service account" — think of it as a read-only robot that can see your spreadsheet.

1. Go to **[console.cloud.google.com](https://console.cloud.google.com/)**
2. If you've never used Google Cloud before, it'll ask you to agree to terms. Do that. **You will not be charged** — this is all within the free tier.
3. At the top of the page, you'll see a project dropdown (might say "My First Project" or "Select a project"). Click it.
4. Click **"New Project"** in the top right of the popup
5. Name it anything — "Budget Dashboard" works fine. Click **"Create"**
6. Wait a few seconds for it to create, then make sure it's selected in the dropdown at the top

**Now enable the Google Sheets API:**

7. In the search bar at the top of Google Cloud Console, type **"Google Sheets API"** and press Enter
8. Click on **"Google Sheets API"** in the results
9. Click the big blue **"Enable"** button. Wait a few seconds.

**Now create the service account:**

10. In the search bar, type **"Service Accounts"** and click on **"Service Accounts"** under "IAM & Admin"
11. Click **"+ Create Service Account"** at the top
12. For "Service account name," type **"budget-reader"** (or anything you want)
13. Click **"Create and Continue"**
14. For "Role," you can skip this — just click **"Continue"**
15. Click **"Done"**

**Now get the key file:**

16. You'll see your new service account in the list. Click on it (click the email address).
17. Click the **"Keys"** tab at the top
18. Click **"Add Key"** → **"Create new key"**
19. Select **"JSON"** and click **"Create"**
20. A file will download to your computer. **This is your key file.** Keep it safe — anyone with this file can read your spreadsheet.

### Step 3: Share Your Sheet with the Service Account

1. Open the key file you just downloaded (it's a .json file). You can open it with any text editor (Notepad on Windows, TextEdit on Mac). Look for the line that says `"client_email":` — it'll be something like `budget-reader@budget-dashboard-12345.iam.gserviceaccount.com`. **Copy that whole email address.**
2. Go to **[drive.google.com](https://drive.google.com)** and open your Finta Google Sheet
3. Click the **"Share"** button (top right)
4. Paste the service account email address you copied
5. Make sure it's set to **"Viewer"** (not Editor — it only needs to read)
6. Uncheck "Notify people" (it's a robot, it doesn't have email)
7. Click **"Share"**

### Step 4: Connect It to the Dashboard

1. Open the dashboard and go to the sidebar
2. Switch to **"🔗 Google Sheets"** mode
3. You need your **Sheet ID** — this is the long random string in your Google Sheet's URL. For example, if your sheet URL is:
   `https://docs.google.com/spreadsheets/d/1ABC123xyz789/edit`
   Then your Sheet ID is: `1ABC123xyz789`
   Copy everything between `/d/` and `/edit`
4. Paste the Sheet ID into the dashboard
5. Upload the JSON key file you downloaded in Step 2
6. The dashboard should load your data. If it says "Connected," you're done!

### Troubleshooting Finta/Sheets Connection

**"Google Sheets error" or "Permission denied":**
- Make sure you shared the sheet with the service account email (Step 3). The email has to match exactly.
- Make sure the Google Sheets API is enabled (Step 2, item 9). Go back to console.cloud.google.com, search "Google Sheets API," and verify it says "Enabled."

**"Could not find date and amount columns":**
- Your Finta sheet may have different column names than expected. Open the sheet in Google Drive and check that it has columns for Date, Amount, and Description/Merchant.

**"No transactions loaded":**
- Finta may take up to 24 hours to sync after initial setup. Check the Google Sheet directly — if it's empty, wait for Finta to populate it.

**Some banks don't work with Finta:**
- Smaller credit unions and some regional banks aren't supported by Plaid (which Finta uses). If your bank isn't supported, use the CSV upload method instead.

---

## Deploy Your Own Private Copy

If you want your own dashboard URL (instead of using the shared demo), you can deploy a free copy:

1. Create free accounts at **[github.com](https://github.com)** and **[streamlit.io](https://streamlit.io)**
2. Go to the [dashboard repo](https://github.com/spencerjw/budget-dashboard-demo) and click **"Fork"** (top right)
3. Go to **[share.streamlit.io](https://share.streamlit.io)** and click **"New app"**
4. Select your fork, branch `main`, file `app.py`
5. Click **Deploy**

Your dashboard will be live at its own URL. Set it to **invite-only** in Settings → Sharing if you're entering real financial data (you should).

---

## FAQ

**Is my data stored on a server somewhere?**
No. Your settings save in your browser's local storage — they never leave your device. CSV uploads are processed in-memory and aren't saved anywhere. The Google Sheets connection is read-only.

**Can I use this on my phone?**
Yes. Open the URL in your phone's browser. The layout adjusts automatically.

**What if I clear my browser history/cookies?**
Your saved settings may be erased. Use the "Backup & Transfer" option in the sidebar to download a backup file first.

**Can I track multiple bank accounts?**
Yes. Download CSVs from each account and upload them one at a time, or use Finta to sync multiple accounts into one Google Sheet automatically.

**Does it work without uploading any CSV?**
Yes. You can enter your income, bills, accounts, and due dates in the sidebar and the dashboard shows your budget overview, debt progress, and due dates. The spending breakdown and transaction history need transaction data (CSV or Google Sheets).

---

## Templates

The `templates/` folder includes starter files if you want to see example formats:
- **`fixed-expenses-template.csv`** — Common recurring bills with examples and notes
- **`transactions-template.csv`** — Sample transaction data showing the expected CSV format
- **`accounts-template.csv`** — Account balances template (checking, savings, credit cards, loans)

## Tech Stack

- **[Streamlit](https://streamlit.io/)** — App framework
- **[Plotly](https://plotly.com/)** — Interactive charts
- **[Pandas](https://pandas.pydata.org/)** — Data handling

## License

MIT — Use it however you want.

---

Built with ☕ and Streamlit
