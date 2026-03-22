# Getting Started

This guide comes in two flavors. Pick the one that fits:

- 🐣 **[I'm New to This](#-complete-beginner-guide)** -- Never used GitHub, Google Cloud, or deployed a web app? Start here. Every click is explained.
- ⚡ **[Just Give Me the Steps](#-experienced-user-guide)** -- You know your way around GitHub, APIs, and config files. Here's the short version.

Throughout both guides, look for 💡 **AI Tips** -- places where tools like [ChatGPT](https://chat.openai.com), [Claude](https://claude.ai), [Google Gemini](https://gemini.google.com), or [Microsoft Copilot](https://copilot.microsoft.com) can do the tedious work for you. If you get stuck on ANY step, paste that section into an AI assistant and ask it to walk you through it. That's what they're for.

---

# 🐣 Complete Beginner Guide

No judgment. Everyone starts somewhere. This will take about 30-45 minutes, and you'll have a working personal finance dashboard at the end.

## What You're Building

A private website (only you can see it) that shows your bank balances, spending, bills, investments, and grocery costs -- all in one place, updated automatically. It looks like this: **[Live Demo](https://budget-dashboard-demo-8nj84cznyyk33y7pacr4ug.streamlit.app/)**

## What You'll Need

Before starting, make sure you have:
- A computer with a web browser (you're reading this, so ✅)
- An email address
- About 30-45 minutes of uninterrupted time

You'll create free accounts on a few services. Nothing costs money except Finta ($5.83/month), which connects to your bank.

## Step 1: Try the Demo First

Before setting anything up, see what you're building:

1. Open the **[Live Demo](https://budget-dashboard-demo-8nj84cznyyk33y7pacr4ug.streamlit.app/)**
2. Click around. You'll see sample data for a fictional family.
3. Try clicking the three buttons at the top: **💵 Daily Finances**, **📈 Investments**, and **🛒 Groceries**
4. This is exactly what yours will look like, but with YOUR real data.

## Step 2: Create a GitHub Account

GitHub is where the dashboard code lives. Think of it like a Google Drive for code.

1. Go to [github.com](https://github.com) and click **Sign up**
2. Use your email, create a password, and pick a username
3. Verify your email when they send you a confirmation
4. You now have a GitHub account ✅

## Step 3: Copy the Dashboard to Your Account

On GitHub, "forking" means making your own copy of someone else's project. You need your own copy so you can add your personal settings.

1. Make sure you're logged into GitHub
2. Go to this page: **[github.com/spencerjw/budget-dashboard-demo](https://github.com/spencerjw/budget-dashboard-demo)**
3. Click the green **Fork** button (top right area of the page)
4. On the next screen, just click **Create fork** (don't change anything)
5. Wait a few seconds. You now have your own copy ✅

You'll see the page looks the same, but the URL at the top now says `github.com/YOUR-USERNAME/budget-dashboard-demo` instead of `spencerjw`.

## Step 4: Create a Streamlit Account

Streamlit is the free service that runs your dashboard and gives you a private web address for it.

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **Continue with GitHub** (this connects it to the GitHub account you just made)
3. Authorize Streamlit to access your GitHub when it asks
4. You now have a Streamlit account ✅

## Step 5: Deploy Your Dashboard

"Deploying" means turning the code into a live website.

1. On Streamlit, click **Create app** (or **New app**)
2. You'll see a form. Fill it in:
   - **Repository**: Select `YOUR-USERNAME/budget-dashboard-demo`
   - **Branch**: `main` (should be selected already)
   - **Main file path**: `app.py`
3. Click **Deploy**
4. Wait 1-2 minutes while it builds

🎉 **Your dashboard is now live!** You'll get a URL like `your-app-name.streamlit.app`. Right now it shows demo data because we haven't connected your bank yet. That's the next part.

## Step 6: Connect Your Bank (Finta + Plaid)

This is what makes the dashboard show YOUR real financial data instead of sample data.

**What is Finta?** A small service ($5.83/month) that securely connects to your bank and copies your transaction data into a Google Sheet that you own. It uses **Plaid** (the same secure technology used by Venmo, Cash App, and Robinhood) to talk to your bank. Your bank login credentials are never stored by Finta or this dashboard.

1. Go to [finta.io](https://finta.io) and create an account
2. Click **Add Account** and search for your bank
3. Log in to your bank through Plaid's secure window (this is normal -- Plaid handles billions of dollars in connections)
4. Repeat for each bank account you want to track (checking, savings, credit cards, investments)
5. Finta will create a Google Sheet in your Google Drive. **Open that Google Sheet** and note the long ID in the URL:
   ```
   https://docs.google.com/spreadsheets/d/THIS_LONG_ID_HERE/edit
   ```
   Copy that ID. You'll need it in the next step.

💡 **AI Tip:** If you're nervous about connecting your bank through Plaid, that's understandable. Ask an AI assistant: *"Is Plaid safe to use for connecting my bank account? What security certifications does it have?"* It'll explain Plaid's SOC 2 Type II certification, bank-level encryption, and why major financial apps trust it.

## Step 7: Add Your Settings to the Dashboard

Now you need to tell your dashboard where to find your bank data and what your monthly bills are.

1. Go back to [share.streamlit.io](https://share.streamlit.io)
2. Find your app and click the **⋮** menu (three dots) → **Settings**
3. Click the **Secrets** tab
4. Paste the following (replacing the example values with yours):

```
finta_sheet_id = "paste-your-google-sheet-id-here"
family_name = "Your Family Budget"
monthly_income = 5000

[fixed_expenses]
[fixed_expenses.Housing]
Mortgage = 1500
Electric = 150
Internet = 80
Water = 50

[fixed_expenses.Transportation]
Car_Payment = 350
Car_Insurance = 120

[fixed_expenses.Subscriptions]
Netflix = 15
Spotify = 10
```

5. Click **Save**

💡 **AI Tip:** Not sure what your monthly bills are or how to organize them? Open your bank statement (or screenshot it) and paste it into ChatGPT or Claude with this prompt: *"Here are my recent bank transactions. Identify all the recurring monthly bills, organize them into categories, and format them in this exact format:"* then paste the template above. The AI will fill it in for you.

## Step 8: Set Up Google Sheets Access

Your dashboard needs permission to read the Google Sheet that Finta creates. This requires a "service account" -- think of it as a special email address that your dashboard uses to log into Google Sheets.

This is the most technical step. Take it slow.

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. If you've never used Google Cloud, it will ask you to agree to terms. Click **Agree and Continue**.
3. At the top of the page, click **Select a project** → **New Project**
4. Name it anything (like "My Budget Dashboard") and click **Create**
5. Wait for it to create, then make sure it's selected in the dropdown at the top

**Now enable the Google Sheets API:**

6. In the search bar at the top, type **"Google Sheets API"** and click the result
7. Click the blue **Enable** button
8. Wait for it to enable

**Now create the service account:**

9. In the left sidebar, click **IAM & Admin** → **Service Accounts**
10. Click **+ Create Service Account** at the top
11. Give it a name (like "budget-reader") and click **Create and Continue**
12. Skip the optional permissions steps -- just click **Done**
13. You'll see your new service account in the list. Click on it.
14. Go to the **Keys** tab
15. Click **Add Key** → **Create new key** → Select **JSON** → Click **Create**
16. A file will download to your computer. **This is important -- don't delete it!**

**Now share your Google Sheet with the service account:**

17. Open the JSON file you just downloaded in any text editor (Notepad works)
18. Find the line that says `"client_email":` and copy the email address (it looks like `budget-reader@your-project.iam.gserviceaccount.com`)
19. Open your Finta Google Sheet
20. Click **Share** (top right)
21. Paste that email address and click **Send** (Viewer access is fine)

**Finally, add the service account to your Streamlit secrets:**

22. Open the JSON file again
23. Go back to your Streamlit app **Settings** → **Secrets**
24. Add this section at the bottom of your existing secrets (copy the values from your JSON file):

```
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "copy-from-json"
private_key = "copy-the-entire-private-key-from-json"
client_email = "copy-from-json"
client_id = "copy-from-json"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

25. Click **Save**
26. Your app will restart automatically

💡 **AI Tip:** This step is the hardest. If you get stuck, take a screenshot of where you are and paste it into an AI assistant with: *"I'm trying to create a Google Cloud service account to read a Google Sheet. Here's where I am -- what do I do next?"* Or, open that downloaded JSON file and paste it into ChatGPT with: *"Convert this Google service account JSON file into Streamlit TOML secrets format."* It'll format it correctly.

## Step 9: Verify It Works

1. Go to your dashboard URL
2. You should see your real bank data instead of sample data
3. The sidebar should be gone -- it's now a clean, auto-updating dashboard

**If you still see sample data:** Wait 5 minutes and refresh. If it still doesn't work, check:
- Did you share the Google Sheet with the service account email?
- Is the `finta_sheet_id` correct in your secrets?
- Did you save the secrets after editing?

💡 **AI Tip:** If you see an error message, copy the entire error and paste it into an AI assistant: *"I deployed a Streamlit dashboard and I'm getting this error. My setup is: Finta Google Sheet connected to Streamlit via a Google service account."* It'll diagnose the problem 9 times out of 10.

## Step 10 (Optional): Add Grocery Tracking

Want to track your grocery spending too? See the [Grocery Price Tracker](#grocery-price-tracker) section in the README.

## You're Done! 🎉

Your dashboard will automatically update as Finta syncs new transactions from your bank (usually daily). Bookmark your dashboard URL and check it whenever you want.

---

# ⚡ Experienced User Guide

You know Git, YAML, and cloud consoles. Here's the fast track.

### Prerequisites
- GitHub account
- Google Cloud project with Sheets API enabled
- Service account with JSON key
- Finta.io account ($5.83/mo) with bank accounts connected
- Streamlit Cloud account (free)

### Setup (5 minutes)

```bash
# 1. Fork and clone
gh repo fork spencerjw/budget-dashboard-demo --clone

# 2. Configure
cp config.example.yaml config.yaml
# Edit config.yaml: finta_sheet_id, monthly_income, fixed_expenses, due_dates

# 3. Share Finta Google Sheet with your service account email (Viewer)

# 4. Deploy to Streamlit Cloud
# - Connect repo at share.streamlit.io
# - Add config + service account JSON to Secrets (TOML format)
# - Deploy
```

### Streamlit Secrets Format

```toml
finta_sheet_id = "your-sheet-id"
family_name = "Family Budget"
monthly_income = 8000

[gcp_service_account]
type = "service_account"
project_id = "your-project"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "sa@project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"

[fixed_expenses]
[fixed_expenses.Housing]
Mortgage = 2000
Electric = 200

[due_dates]
[due_dates.Mortgage]
data = [1, 2000]
```

### Optional: 401(k) Fund Tracking

Map your employer fund names to public tickers for NAV lookups:

```yaml
fund_ticker_map:
  "Vanguard Target Ret 2045": "VTIVX"
  "Fidelity Mid Cap Index Fund": "FSMDX"
```

💡 **AI Tip:** Paste your fund names into any AI tool to get ticker symbols.

### Optional: Grocery Price Tracker

1. Create a Google Sheet with `Items` and `Orders` tabs (schema in README)
2. Share with your service account
3. Add to secrets: `grocery_sheet_id = "your-sheet-id"`

💡 **AI Tip:** Feed your grocery order PDFs/screenshots into ChatGPT or Claude to extract structured CSV data. One prompt per order, paste into Google Sheets. See README for the full prompt template.

### Manual Accounts

Banks not on Plaid? Add a "Manual Accounts" tab to your Finta sheet:

| Account | Balance | Type | Last Updated |
|---------|---------|------|-------------|
| Credit Union Checking | 5200 | depository | 2026-03-15 |
| John Hancock 401(k) | 185000 | investment | 2026-03-15 |

---

## Troubleshooting

💡 **AI Tip:** Before searching forums, paste your error into an AI assistant with context about your setup. It'll diagnose config and permission issues faster than any search engine.

| Problem | Fix |
|---------|-----|
| Still seeing demo data | Check `finta_sheet_id` in secrets, verify sheet is shared with SA email |
| "Could not load Finta data" | Sheet ID wrong, or SA doesn't have access |
| Grocery tab shows demo data | Add `grocery_sheet_id` to secrets, share sheet with SA |
| 401(k) shows no fund values | Add `fund_ticker_map` to config |
| Missing recent transactions | Finta syncs daily -- new transactions take up to 24 hours |
| Bank not on Plaid | Use "Manual Accounts" tab in your Finta sheet |
| TOML format errors in secrets | Paste your YAML config into an AI tool: *"Convert to Streamlit TOML"* |
