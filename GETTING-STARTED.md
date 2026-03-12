# Getting Started: Your First Budget Dashboard

This guide walks you through setting up a personal budget dashboard from scratch. No finance degree required. No coding. If you can fill out a form and pay a bill, you can do this.

---

## What This Dashboard Does

It shows you, in one place:
- **How much money you have left to spend** this month (after bills)
- **Where your money is going** (groceries, eating out, gas, etc.)
- **Whether you're on track** or overspending
- **What bills are coming up** and when they're due
- **How much debt you have** and how fast you're paying it down

That's it. It's not going to manage your money for you -- it just makes it visible. Visibility is the first step to not being broke.

---

## Quick Start (5 Minutes)

### Step 1: Open the Dashboard

**Option A -- Use it online (easiest):**
Open the [live demo](https://budget-dashboard-demo-ltc4jkyc8bajang468zh7v.streamlit.app/) in your browser. It works on your phone too.

**Option B -- Run it yourself:**
If you want your own private copy, see "Deploy Your Own Copy" at the bottom of this guide.

### Step 2: Open the Sidebar

Click the **>** arrow in the top-left corner to open the sidebar. This is where you set everything up. No code to edit -- it's all forms and buttons.

### Step 3: Switch from Demo to Your Data

At the top of the sidebar, change the data source from **"🎲 Demo Data"** to **"📄 Upload My CSV"**. The demo data disappears and you'll see your own settings.

### Step 4: Enter Your Info

Fill in these sections in the sidebar:

#### 🏠 My Info
- **Dashboard Name:** Your last name, "My Budget," whatever you want at the top
- **Monthly Take-Home Pay:** The amount that actually hits your bank account after taxes. Not your salary -- your actual deposit. If you get paid every two weeks, add up two recent paychecks.

#### 📋 Monthly Bills
These are recurring charges that hit every month for roughly the same amount. Click each category to expand it and add your bills.

**Start with the big ones:**
- Rent or mortgage
- Car payment
- Insurance (car, renters)
- Utilities (electric, water, internet, phone)
- Loan payments (student loans, credit cards)

**Then the small ones people forget:**
- Streaming services (Netflix, Spotify, YouTube, Disney+, etc.)
- Gym membership
- Cloud storage (iCloud, Google One)
- App subscriptions
- Anything that auto-charges your card monthly

**How to find these:** Log into your bank account and look at last month's transactions. Find every charge that shows up every month. Write down the name and amount.

**Don't include** things that change every month like groceries, gas, or eating out. The dashboard tracks those separately from your transaction data.

You can create new categories with the "➕ Add a new category" section if the defaults don't fit.

#### 💰 Accounts & Balances
What you have and what you owe.

- **Checking account** -- what's in your main bank account right now
- **Savings account** -- if you have one (even if it's $50, put it in)
- **Credit card** -- what you currently owe (the balance, not the limit). Set the limit too.
- **Loans** -- car loan, student loans, personal loans. Put what you still owe as the balance, and what you originally borrowed as the limit.
- **Investments** -- 401(k), IRA, brokerage. Ballpark is fine. $0 if you don't have any -- that's normal when starting out.

Click "➕ Add an account" to add each one.

#### 📅 Bill Due Dates
Add your bills and what day of the month they're due. The dashboard will show you which ones are coming up, which are due soon, and which are already paid for the month.

### Step 5: Save Your Settings

**Important:** The dashboard doesn't save your settings automatically (your data stays private -- nothing is stored on any server).

Click **"⬇️ Download My Settings"** in the sidebar to save a `budget-settings.json` file to your computer. Next time you visit, upload that file to load everything back.

### Step 6: Upload Your Transactions (Optional but Recommended)

This is what makes the spending breakdown, donut chart, and transaction history work.

1. **Log into your bank's website or app**
2. **Go to your transaction history**
3. **Look for "Download" or "Export" -- choose CSV format**
4. **Upload that file** in the sidebar

| Bank | Where to Find It |
|------|-----------------|
| Chase | Activity → ⬇️ Download → CSV |
| Bank of America | Activity → Download/Export |
| Wells Fargo | Activity → Download |
| Capital One | Transactions → Download Transactions |
| USAA | Transactions → Export |
| Credit unions | Look for "Export" or "Download" in transaction history |

**Do this for credit cards too.** If you use a credit card for most purchases (which is smart for building credit), export those transactions. That's where most of your spending data lives.

**Don't have transactions yet?** That's fine. The dashboard still works with just your bills and accounts entered in the sidebar. Add transactions later when you're ready.

---

## Using the Dashboard

### What to Check Weekly (2 minutes)

1. Open the dashboard
2. Look at **"Spendable Left"** -- that's your remaining budget for the month after bills
3. Glance at the **spending donut** -- anything surprising?
4. Upload fresh transactions from your bank if you're tracking spending

### What to Check Monthly (10 minutes)

1. Did any bills change? (New subscription, rate increase, paid off a loan?) Update them in the sidebar.
2. Look at last month's spending. Where did the money go?
3. Download your updated settings file to keep them saved.

### What the Numbers Mean

**Spendable Left:** Money remaining after fixed bills and your spending so far. If this is negative, you spent more than you made. That's a problem if it keeps happening.

**Budget Health Gauge:**
- 🟢 Green (under 75%) = You're saving money. Nice.
- 🟡 Yellow (75-95%) = Tight but okay. Don't go nuts.
- 🔴 Red (over 95%) = You're spending everything you make. Time to look at where it's going.

**Credit Card Balance/Limit:** The percentage matters more than the dollar amount.
- Under 30% of your limit = healthy
- Over 50% = starting to hurt your credit score
- At the limit = stop using the card and pay it down

**Category Breakdown (Donut):** Shows where your money goes. Most people are surprised by food (groceries + restaurants combined). That's normal -- food is expensive. But it's good to know.

---

## Budgeting Basics (60 Seconds)

If nobody ever taught you this, here it is:

**The only rule:** Spend less than you make. Every month. That's it.

**How:**
1. Know your income (you entered this above)
2. Pay your fixed bills first (rent, utilities, loans, insurance)
3. What's left is your spending money for everything else
4. If there's nothing left after bills, you either need to earn more or cut something

**The 50/30/20 guideline** (not a law, just a target):
- 50% on needs (rent, bills, groceries, transportation)
- 30% on wants (eating out, entertainment, shopping)
- 20% saved or toward extra debt payments

**Three things to do first:**
1. **Build a $1,000 emergency cushion.** Before anything else. This keeps a flat tire from becoming a crisis.
2. **Pay at least the minimum on all debts.** Missing payments destroys your credit score and costs you more in the long run.
3. **Keep credit card usage under 30% of your limit.** Using credit is fine. Maxing it out is not.

**Traps that get everyone:**
- Subscriptions you forgot about (audit every few months)
- Eating out vs. cooking ($15 takeout vs. $4 home-cooked -- 3-5x difference per meal)
- "Small" daily purchases ($5/day on coffee = $150/month = $1,800/year)
- Lifestyle creep (making more money but spending all of it -- your future self needs some of that)

This dashboard makes all of this visible. You can't fix what you can't see.

---

## Deploy Your Own Copy (Free)

If you want your own private dashboard URL that nobody else can see:

### The Simple Way (Streamlit Cloud -- Free)

1. **Create accounts** at [github.com](https://github.com/) and [streamlit.io](https://streamlit.io/) (both free)
2. **Go to the [dashboard repo](https://github.com/spencerjw/budget-dashboard-demo)**
3. **Click "Fork"** (top right) -- this creates your own copy
4. **Go to [share.streamlit.io](https://share.streamlit.io)**
5. **Click "New app"**
6. **Select your fork**, branch `main`, file `app.py`
7. **Click Deploy**

Your dashboard will be live at a private URL. Set it to **invite-only** in Settings → Sharing if you're entering real financial data.

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

If you want the dashboard to always have current data without manual CSV uploads, you can connect it to [Finta](https://www.finta.io/) ($5.83/month). Finta syncs your bank accounts to a Google Sheet automatically. See the [README](README.md) for setup instructions.

Most people don't need this. Monthly CSV uploads work fine.

---

## FAQ

**"Is my data stored anywhere?"**
No. Everything runs in your browser session. When you close the tab, it's gone. That's why you download the settings file -- it's the only copy.

**"Can I use this on my phone?"**
Yes. The dashboard is responsive. Open the Streamlit URL in your phone's browser.

**"I don't know my exact expenses."**
Put your best guess. The dashboard will show you your actual spending from transactions. You'll get more accurate over the first month or two.

**"My income changes every month (tips, freelance, gig work)."**
Use the average of your last 3 months. Update it quarterly. The trend over time matters more than any single month being perfect.

**"This is overwhelming."**
Start small. Just enter your income and bills. Skip the transactions, skip the accounts. See what "Spendable Left" says. That one number is worth the whole setup.
