# Family Budget Dashboard (Demo)

A Streamlit-based family budget dashboard with randomly generated sample data. No API keys or external services required.

## Features

- **KPI Cards** — Spendable balance, credit card status, savings, income, bills, investments
- **Spending Breakdown** — Interactive donut chart by category
- **Budget Health Gauge** — Visual indicator of budget utilization
- **Category Drill-Down** — Click into any spending category to see sub-categories and individual transactions
- **Fixed Expense Breakdown** — Expandable panels for recurring bills
- **Credit & Debt Tracking** — Progress bars for credit cards and loans
- **Due Date Calendar** — Upcoming bill due dates with status
- **Transaction History** — Paginated table of recent transactions
- **Month Selector** — View current month, past months, or YTD

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Point to this repo, `app.py` as entrypoint
4. Deploy — no secrets needed

## Tech Stack

- **Streamlit** — App framework
- **Plotly** — Charts (donut, gauge)
- **Pandas** — Data handling
- All data is generated at runtime with seeded randomness for consistency.

## Customization

Edit the constants at the top of `app.py` to change:
- `FAMILY_NAME` — Dashboard title
- `MONTHLY_INCOME` — Household income
- `FIXED_EXPENSES` — Recurring bills
- `MERCHANT_POOLS` — Transaction merchants
- `SPEND_RANGES` / `CATEGORY_FREQ` — Spending patterns
