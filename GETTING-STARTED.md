# Getting Started: Your First Budget Dashboard

No finance degree required. No coding. If you can fill out a form and pay a bill, you can do this.

---

## What This Dashboard Does

It shows you, in one place:
- **How much money you have left to spend** this month (after bills)
- **Where your money is going** (groceries, eating out, gas, etc.)
- **Whether you're on track** or overspending
- **What bills are coming up** and when they're due
- **How much debt you have** and how fast you're paying it down

It's not going to manage your money for you -- it just makes it visible. Visibility is the first step to not being broke.

---

## Quick Start (5 Minutes)

### Step 1: Open the Dashboard

**Option A -- Use it online (easiest):**
Open the [live demo](https://budget-dashboard-demo-ltc4jkyc8bajang468zh7v.streamlit.app/) in your browser *(right-click → "Open in new tab" to keep this page open)*. Works on your phone too.

**Option B -- Run it yourself:**
If you want your own private copy, see "Deploy Your Own Copy" at the bottom of this guide.

### Step 2: Open the Sidebar

Click the **>** arrow in the top-left corner to open the sidebar. This is where you set everything up.

### Step 3: Switch to My Budget

At the top of the sidebar, click the **💰 My Budget** button. The demo data goes away and you'll see your own settings.

You'll see a privacy note: 🔒 **Your data never leaves your browser.** No accounts, no servers, no tracking.

### Step 4: Enter Your Info

Fill in these sections in the sidebar:

#### 🏠 My Info
- **Dashboard Name:** Your last name, "My Budget," whatever you want at the top
- **Monthly Take-Home Pay:** The amount that actually hits your bank account after taxes. Not your salary -- your actual deposit. If you get paid every two weeks, add up two recent paychecks.

#### 📋 Monthly Bills
Recurring charges that hit every month for roughly the same amount. Tap each category to expand it.

**To add a bill:** Click **➕ Add a bill** inside any category, type the name and amount, then click **✅ Save**.

**To delete a bill:** Click the 🗑️ button next to it.

**To add a new category:** Use the **➕ Add a new category** section below the existing ones.

**To delete a category:** Open it and scroll to the bottom -- there's a delete button. If it has bills in it, you'll get a confirmation warning.

**Start with the big ones:**
- Rent or mortgage
- Car payment
- Insurance (car, renters)
- Utilities (electric, water, internet, phone)
- Loan payments

**Then the small ones people forget:**
- Streaming services (Netflix, Spotify, YouTube, Disney+)
- Gym membership
- Cloud storage (iCloud, Google One)
- App subscriptions

**How to find these:** Log into your bank account and look at last month's transactions. Find every charge that shows up every month.

**Don't include** things that change every month like groceries, gas, or eating out. The dashboard tracks those separately from your transaction data.

#### 💰 Accounts & Balances
Tap each account to expand it and enter your current balance. Check your bank app for the numbers.

**Cash & Savings:**
- Checking account -- what's in your main bank account right now
- Savings account -- even if it's $50, put it in
- Investments -- 401(k), IRA, brokerage. Ballpark is fine. $0 if you don't have any.

**Credit Cards & Loans:**
- Balance owed -- what you currently owe
- Credit limit (cards) or original loan amount (loans)
- Payment due date -- day of the month it's due (shows up in the Upcoming Bills section)

Click the ➕ expanders to add new accounts.

#### 📅 Bill Due Dates
This is for bills that **aren't** credit cards or loans (those due dates are set in the accounts section above). Enter the day of the month each is due -- e.g. rent on the 1st, electric on the 15th. Shows up in the Upcoming Bills section of your dashboard.

### Step 5: Save Your Settings

Click **💾 Save Changes** in the sidebar. Your settings are stored automatically in your browser -- they'll be there next time you visit.

**Want to use on another device?** Scroll to **🚀 Take It With You** at the bottom of the sidebar. Download your settings, deploy your own free copy, and upload them there.

### Step 6: Upload Your Transactions (Optional but Recommended)

This powers the spending donut chart, category drill-down, and transaction history.

1. **Log into your bank's website or app**
2. **Go to your transaction history**
3. **Look for "Download" or "Export" -- choose CSV format**
4. **Drop the file(s)** into the upload area at the top of the sidebar

**You can upload multiple files at once** -- one from each bank account or credit card.

| Bank | Where to Find It |
|------|-----------------|
| Chase | Activity → ⬇️ Download → CSV |
| Bank of America | Activity → Download/Export |
| Wells Fargo | Activity → Download |
| Capital One | Transactions → Download Transactions |
| USAA | Transactions → Export |
| Credit unions | Look for "Export" or "Download" in transaction history |

**Do this for credit cards too.** If you use a credit card for most purchases, those transactions are where most of your spending data lives.

**Don't have transactions yet?** That's fine. The dashboard still works with just your bills and accounts. Add transactions later when you're ready.

---

## Using the Dashboard

### What to Check Weekly (2 minutes)

1. Open the dashboard
2. Look at **"Spendable Left"** -- that's your remaining budget for the month after bills
3. Glance at the **spending donut** -- anything surprising?
4. Upload fresh transactions from your bank if you're tracking spending

### What to Check Monthly (10 minutes)

1. Did any bills change? (New subscription, rate increase, paid off a loan?) Update them.
2. Look at last month's spending. Where did the money go?
3. Update your account balances.

### What the Numbers Mean

**Spendable Left:** Money remaining after fixed bills and your spending so far. If this is negative, you spent more than you made.

**Budget Health Gauge:**
- 🟢 Green (under 75%) = You're saving money. Nice.
- 🟡 Yellow (75-95%) = Tight but okay.
- 🔴 Red (over 95%) = You're spending everything you make. Time to look at where it's going.

**Credit Card Balance/Limit:**
- Under 30% = healthy
- Over 50% = starting to hurt your credit score
- At the limit = stop using the card and pay it down

---

## Budgeting Basics (60 Seconds)

If nobody ever taught you this, here it is:

**The only rule:** Spend less than you make. Every month.

**The 50/30/20 guideline** (not a law, just a target):
- 50% on needs (rent, bills, groceries, transportation)
- 30% on wants (eating out, entertainment, shopping)
- 20% saved or toward extra debt payments

**Three things to do first:**
1. **Build a $1,000 emergency cushion.** Before anything else.
2. **Pay at least the minimum on all debts.** Missing payments destroys your credit score.
3. **Keep credit card usage under 30% of your limit.**

**Traps that get everyone:**
- Subscriptions you forgot about (audit every few months)
- Eating out vs. cooking ($15 takeout vs. $4 home-cooked)
- "Small" daily purchases ($5/day = $150/month = $1,800/year)
- Lifestyle creep (making more but spending all of it)

This dashboard makes all of this visible. You can't fix what you can't see.

---

## Deploy Your Own Copy (Free)

### The Simple Way (Streamlit Cloud -- Free)

1. **Create accounts** at [github.com](https://github.com/) and [streamlit.io](https://streamlit.io/) (both free)
2. **Go to the [dashboard repo](https://github.com/spencerjw/budget-dashboard-demo)**
3. **Click "Fork"** (top right) -- this creates your own copy
4. **Go to [share.streamlit.io](https://share.streamlit.io)**
5. **Click "New app"**
6. **Select your fork**, branch `main`, file `app.py`
7. **Click Deploy**

Set it to **invite-only** in Settings → Sharing if you're entering real financial data.

### On Your Own Computer

```bash
# Install Python: https://python.org/downloads
git clone https://github.com/spencerjw/budget-dashboard-demo.git
cd budget-dashboard-demo
pip install -r requirements.txt
streamlit run app.py
```

Opens in your browser at `localhost:8501`. Only runs while the terminal is open.

---

## Auto-Sync (Advanced -- Optional)

Everything above — the sidebar inputs, CSV uploads, manual balance entry — is the **demo experience**. It works, but it's manual. The real experience is fully automated.

**[Finta](https://www.finta.io/)** ($5.83/month) connects your bank accounts, credit cards, and brokerages to a Google Sheet and syncs transactions automatically. Finta uses **[Plaid](https://plaid.com/)** to connect to your accounts — the same secure bank-connection infrastructure behind Chase, Vanguard, Venmo, and thousands of other financial apps. Plaid is SOC 2 Type II certified, connects to 12,000+ financial institutions, and never stores your bank login credentials.

**What changes with Finta connected:**
- Transactions sync daily — no more downloading and uploading CSVs
- Account balances stay current automatically
- The sidebar simplifies to just viewing controls — no manual data entry
- You get accurate spending data without remembering to export anything

**Setup takes about 10 minutes.** You create a Finta account, connect your bank(s) through Plaid's secure flow, point Finta at a Google Sheet, and configure the dashboard to read from it. After that, the dashboard just works. See the [README](README.md#demo-vs-real-setup) for more.

---

## FAQ

**"Is my data stored anywhere?"**
Your settings are saved in your browser's localStorage -- they'll be there when you come back. CSV uploads are processed in-memory and never stored. Nothing is sent to any server.

**"How do I move my settings to another device?"**
In the sidebar, scroll to **🚀 Take It With You**. Click **⬇️ Download My Settings** to save a JSON file. On the new device, use **⬆️ Load Settings File** to upload it.

**"Can I use this on my phone?"**
Yes. The layout adjusts automatically.

**"I don't know my exact expenses."**
Put your best guess. You'll get more accurate over the first month or two.

**"My income changes every month (tips, freelance, gig work)."**
Use the average of your last 3 months. Update it quarterly.

**"This is overwhelming."**
Start small. Just enter your income and bills. Skip the transactions, skip the accounts. See what "Spendable Left" says. That one number is worth the whole setup.
