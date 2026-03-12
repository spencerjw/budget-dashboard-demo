# Getting Started: Your First Budget Dashboard

This guide walks you through setting up a personal budget dashboard from scratch. No finance degree required. If you can use a spreadsheet and pay a bill, you can do this.

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

## Before You Start: Gather Your Info

You need three things. Don't overthink this -- estimates are fine to start. You'll refine it over time.

### 1. Your Monthly Income (After Taxes)

This is your **take-home pay** -- the amount that actually hits your bank account, not your salary. If you get paid every two weeks, look at two recent paychecks and add them up. If your income varies (tips, freelance, hourly), use your average over the last 3 months.

- **Paycheck 1 (or only paycheck):** $________
- **Paycheck 2 (if paid biweekly):** $________
- **Side income (if any):** $________
- **Total monthly income:** $________

### 2. Your Fixed Monthly Expenses

These are bills that hit every month for roughly the same amount. Open the template file `templates/fixed-expenses-template.csv` -- it has common categories with examples.

**How to figure these out:**
- Log into your bank account and look at last month's transactions
- Find every recurring charge (rent, utilities, subscriptions, loan payments)
- Write down the name and amount

**Common ones people forget:**
- Subscriptions (streaming, gaming, apps, cloud storage)
- Insurance (car, renters, health if you pay separately)
- Minimum credit card payments
- Gym memberships they never use

Don't include things that change every month like groceries, gas, or eating out. Those are "variable spending" and the dashboard tracks them from your transaction history.

### 3. Your Accounts

What do you have and what do you owe? Open `templates/accounts-template.csv` for the format.

- **Checking account balance** -- what's in your main bank account right now
- **Savings account balance** -- if you have one
- **Credit card balance** -- what you currently owe (not the limit, the balance)
- **Credit card limit** -- the maximum you're allowed to charge
- **Loans** -- car loan, student loans, personal loans (what you still owe)
- **Retirement/investment accounts** -- 401(k), IRA, brokerage (ballpark is fine)

**If you're just starting out and have none of this:** That's totally normal. A checking account and maybe a credit card is plenty. You can add more as your financial life gets more complex.

---

## Step 1: Set Up Your Data

You have two options. Pick whichever sounds less annoying.

### Option A: Manual CSV (Free, 5 Minutes/Month)

This is the simplest approach. You download your transactions from your bank once a month (or whenever you want to check in) and upload them to the dashboard.

1. **Log into your bank's website or app**
2. **Go to your transaction history / activity**
3. **Look for "Download" or "Export" -- choose CSV format**
4. **Upload that file** in the dashboard sidebar under "📄 Upload CSV"

Most banks let you filter by date range. Download the current month's transactions.

**Where to find the export button:**
| Bank | Where to Look |
|------|--------------|
| Chase | Activity → ⬇️ Download icon → CSV |
| Bank of America | Activity → Download/Export |
| Wells Fargo | Activity → Download |
| Capital One | Transactions → Download Transactions |
| USAA | Transactions → Export |
| Credit Union | Varies -- look for "Export" or "Download" in transaction history |

**Credit cards too.** If you use a credit card for most purchases, download those transactions as well. That's where most of your spending data lives.

### Option B: Auto-Sync with Finta ($5.83/month)

This connects your bank accounts to a Google Sheet that updates automatically. Set it up once and your dashboard always has current data.

1. **Sign up at [finta.io](https://www.finta.io/)**
2. **Connect your bank accounts** through Plaid (the industry-standard secure connection -- same thing Venmo, Cash App, etc. use)
3. **Finta creates a Google Sheet** with your transactions, account balances, and categories
4. **In the dashboard sidebar**, select "🔗 Google Sheets" and paste your Sheet ID

This is the better long-term option if you want the dashboard to just work without manual effort. The $5.83/month is worth it if you'll actually use it.

**Note:** Some smaller banks and credit unions don't work with Plaid. Check Finta's supported institutions before signing up.

---

## Step 2: Customize Your Fixed Expenses

Open `app.py` in a text editor. Near the top, you'll see a section that looks like this:

```python
DEFAULT_FIXED_EXPENSES = {
    'Household': {
        'Austin Energy': 218,
        'T-Mobile Wireless': 195,
        # ... more items
    },
    'Auto & Insurance': {
        'Honda Accord Payment': 485,
        # ... more items
    },
}
```

Replace these with your actual bills. The format is: `'Bill Name': dollar_amount,`

**Example for someone just starting out:**
```python
DEFAULT_FIXED_EXPENSES = {
    'Household': {
        'Rent': 1200,
        'Electric': 95,
        'Internet': 65,
        'Cell Phone': 85,
        'Renters Insurance': 25,
        'Netflix': 16,
        'Spotify': 11,
    },
    'Auto & Insurance': {
        'Car Payment': 350,
        'Car Insurance': 150,
        'Gas (estimated)': 120,
    },
    'Debt': {
        'Student Loan': 280,
        'Credit Card Minimum': 50,
    },
}
```

Also update your income:
```python
DEFAULT_MONTHLY_INCOME = 3700  # Your take-home pay
```

And your name (or whatever you want the dashboard to say):
```python
DEFAULT_FAMILY_NAME = "My"  # Shows as "My Budget" at the top
```

---

## Step 3: Deploy It

### Run It On Your Computer (Easiest to Start)

```bash
# Install Python if you don't have it: https://python.org/downloads
# Then:
pip install -r requirements.txt
streamlit run app.py
```

This opens the dashboard in your browser at `localhost:8501`. It only runs while your terminal is open.

### Put It Online (Free with Streamlit Cloud)

This gives you a URL you can access from anywhere -- your phone, work, wherever.

1. **Create a free account** at [streamlit.io](https://streamlit.io/)
2. **Fork this repo** on GitHub (click the Fork button at the top of the repo page)
3. **On Streamlit Cloud**, click "New app"
4. **Select your fork**, branch `main`, file `app.py`
5. **Click Deploy**

Your dashboard will be live at a URL like `your-app-name.streamlit.app`

**Important:** If you customize the fixed expenses with your real numbers, set the app to **private** in Streamlit Cloud settings (Settings → Sharing → "Only specific people can view this app"). You don't want strangers seeing your finances.

---

## Step 4: Use It

Here's what to actually do with the dashboard once it's running.

### Weekly (2 minutes)
- Open the dashboard
- Look at "Spendable Left" -- that's your remaining budget for the month
- Glance at the spending breakdown donut -- anything surprising?
- If you're using CSV mode, upload fresh transactions from your bank

### Monthly (10 minutes)
- Check if any fixed expenses changed (new subscription, rate increase, paid off a loan)
- Update `app.py` if they did
- Look at the previous month's spending -- where did the money go?
- Compare to the month before that -- any trends?

### What the Numbers Mean

- **Spendable Left**: Money remaining after fixed bills and variable spending. If this is negative, you spent more than you made this month. That's a problem if it keeps happening.

- **Budget Health Gauge**: Green (under 75% of income used) = you're saving money. Yellow (75-95%) = tight but okay. Red (over 95%) = you're spending everything you make.

- **Credit Card Balance / Limit**: The percentage matters more than the dollar amount. Under 30% of your limit is healthy. Over 50% starts hurting your credit score. At the limit = stop using the card.

- **Category Breakdown**: The donut chart shows where your money goes. Most people are surprised by how much they spend on food (groceries + restaurants combined). That's normal -- food is expensive. But it's good to know.

---

## Budgeting Basics (The Short Version)

If you've never tracked money before, here's the framework in 60 seconds:

**The only rule that matters:** Spend less than you make. Every month. That's it.

**How to do it:**
1. **Know your income** (you figured this out above)
2. **Pay your fixed bills first** (rent, utilities, loans, insurance)
3. **What's left is your spending money** for everything else (food, gas, fun, shopping)
4. **If there's nothing left** after fixed bills, you have an income problem or an expense problem. Usually it's both.

**Three numbers to know:**
- **50/30/20 rule** (rough target, not gospel): 50% of income on needs (rent, bills, groceries), 30% on wants (eating out, entertainment, shopping), 20% saved or toward debt
- **Emergency fund target**: 3 months of expenses in savings. Start with $1,000 and build from there.
- **Credit card utilization**: Keep your balance under 30% of your limit. Pay it off monthly if you can.

**Common traps:**
- Subscriptions you forgot about (audit them every few months)
- Eating out vs. groceries (cooking at home is 3-5x cheaper per meal)
- "Small" purchases that add up ($5/day on coffee = $150/month)
- Lifestyle creep (making more money but spending all of it)

This dashboard makes all of this visible. You can't fix what you can't see.

---

## Troubleshooting

**"I don't have a computer to run this on"**
Use Streamlit Cloud. You only need a browser and a GitHub account (both free).

**"My bank's CSV format doesn't work"**
The parser handles most formats, but if your columns are unusual, rename them to match: `Date`, `Amount`, `Description`, `Category`. Open the CSV in Excel/Google Sheets, rename the header row, save, and re-upload.

**"I don't know my exact expenses"**
That's fine. Put your best estimate. The dashboard will show you your actual spending from transactions -- you'll dial in the fixed expense numbers over the first month or two.

**"I have irregular income (freelance, tips, gig work)"**
Use the average of your last 3 months. Update it quarterly. It won't be perfectly accurate for any given month, but the trend over time is what matters.

**"This is overwhelming"**
Start with just the CSV upload. Don't customize anything. Upload one month of bank transactions and look at where your money went. That alone is worth it. You can set up the rest later.

---

## Files in This Repo

| File | What It Is |
|------|-----------|
| `app.py` | The dashboard application. Customize your expenses and income here. |
| `requirements.txt` | Python packages needed to run the app. |
| `templates/fixed-expenses-template.csv` | Template for your recurring monthly bills. |
| `templates/transactions-template.csv` | Example transaction data showing the expected format. |
| `templates/accounts-template.csv` | Template for your account balances (checking, savings, debt, investments). |
| `GETTING-STARTED.md` | This guide. |
| `README.md` | Technical overview and feature list. |

---

## Questions?

Open an issue on GitHub or check the [Streamlit docs](https://docs.streamlit.io/) for deployment help.
