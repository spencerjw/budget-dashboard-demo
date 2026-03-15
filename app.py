import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

APP_VERSION = "1.0.0"
from streamlit_local_storage import LocalStorage
import pandas as pd
import random
import json
import time
import io
import yaml
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import math

# ========================
# CONFIG LOADING
# ========================

def load_config():
    """Load config from Streamlit secrets or config.yaml."""
    # Check Streamlit secrets first
    try:
        if hasattr(st, 'secrets') and 'finta_sheet_id' in st.secrets:
            cfg = dict(st.secrets)
            # Convert secrets to proper types
            return cfg
    except Exception:
        pass
    # Check config.yaml
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path) as f:
            return yaml.safe_load(f)
    return None

_APP_CONFIG = load_config()
IS_PRODUCTION = _APP_CONFIG is not None


# ========================
# DEMO DATA GENERATOR
# ========================
random.seed(42)

MERCHANT_POOLS = {
    'Groceries': ['H-E-B', 'Whole Foods', 'Costco', 'Trader Joes', 'Sprouts', 'Central Market', 'Walmart Grocery'],
    'Restaurants': ['Chilis', 'Torchys Tacos', 'Chipotle', 'Whataburger', 'Panera Bread', 'Olive Garden', 'Five Guys', 'Mod Pizza'],
    'Gas & Auto': ['Shell', 'Exxon', 'Buc-ees', 'Valvoline', 'Discount Tire', 'AutoZone'],
    'Shopping': ['Amazon', 'Target', 'Home Depot', 'Lowes', 'Best Buy', 'Kohls', 'TJ Maxx'],
    'Health & Fitness': ['CVS Pharmacy', 'Walgreens', 'Planet Fitness', 'Urgent Care'],
    'Entertainment': ['AMC Theatres', 'TopGolf', 'Dave & Busters', 'Alamo Drafthouse'],
    'Kids & Family': ['Academy Sports', 'Great Clips', 'YMCA', 'Party City'],
    'Home & Garden': ['Home Depot', 'Lowes', 'Wayfair', 'Ace Hardware'],
    'Travel': ['Southwest Airlines', 'Marriott', 'Uber', 'Lyft'],
    'Personal Care': ['Great Clips', 'Ulta Beauty', 'Sport Clips'],
}
CATEGORY_GROUPS = {
    'Groceries': 'Food & Drink', 'Restaurants': 'Food & Drink',
    'Gas & Auto': 'Transportation', 'Shopping': 'Shopping',
    'Health & Fitness': 'Health', 'Entertainment': 'Entertainment',
    'Kids & Family': 'Family', 'Home & Garden': 'Home',
    'Travel': 'Travel', 'Personal Care': 'Personal',
}
SPEND_RANGES = {
    'Groceries': (35, 220), 'Restaurants': (12, 85), 'Gas & Auto': (25, 75),
    'Shopping': (15, 250), 'Health & Fitness': (15, 120), 'Entertainment': (20, 100),
    'Kids & Family': (15, 90), 'Home & Garden': (20, 180), 'Travel': (50, 400),
    'Personal Care': (15, 65),
}
CATEGORY_FREQ = {
    'Groceries': 8, 'Restaurants': 10, 'Gas & Auto': 4, 'Shopping': 5,
    'Health & Fitness': 2, 'Entertainment': 3, 'Kids & Family': 3,
    'Home & Garden': 2, 'Travel': 1, 'Personal Care': 2,
}

DEMO_FIXED_EXPENSES = {
    'Household': {
        'Rent / Mortgage': 1200, 'Electric': 120, 'Water': 45,
        'Internet': 65, 'Cell Phone': 85, 'Renters Insurance': 25,
        'Netflix': 16, 'Spotify': 11,
    },
    'Auto & Insurance': {
        'Car Payment': 350, 'Car Insurance': 150,
    },
    'Debt Payments': {
        'Student Loans': 280, 'Credit Card Minimum': 50,
    },
}

DEMO_ACCOUNTS = [
    {'name': 'Checking Account', 'type': 'checking', 'balance': 2450, 'limit': 0},
    {'name': 'Savings Account', 'type': 'savings', 'balance': 8500, 'limit': 0},
    {'name': 'Credit Card', 'type': 'credit', 'balance': 3200, 'limit': 10000},
    {'name': 'Car Loan', 'type': 'loan', 'balance': 14500, 'limit': 22000},
    {'name': 'Retirement 401(k)', 'type': 'investment', 'balance': 12000, 'limit': 0},
]

# ========================
# DEMO INVESTMENT DATA
# ========================
DEMO_INVESTMENT_ACCOUNTS = [
    {'name': 'Vanguard Brokerage', 'subtype': 'brokerage', 'balance': 47832.50},
    {'name': 'Fidelity 401(k)', 'subtype': '401k', 'balance': 128450.75},
    {'name': 'E*TRADE Roth IRA', 'subtype': 'roth', 'balance': 34215.30},
    {'name': 'Schwab Taxable', 'subtype': 'brokerage', 'balance': 21890.00},
]

def _gen_holdings():
    """Generate fake but realistic holdings for demo investment accounts."""
    rng = random.Random(42)
    holdings_map = {
        'Vanguard Brokerage': [
            {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'quantity': 85.0, 'price': 248.50, 'gain_loss': 18.4},
            {'symbol': 'VXUS', 'name': 'Vanguard Total Intl Stock ETF', 'quantity': 120.0, 'price': 58.30, 'gain_loss': -2.1},
            {'symbol': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'quantity': 60.0, 'price': 72.15, 'gain_loss': 1.8},
            {'symbol': 'AAPL', 'name': 'Apple Inc', 'quantity': 25.0, 'price': 189.25, 'gain_loss': 42.6},
        ],
        'Fidelity 401(k)': [
            {'symbol': 'FXAIX', 'name': 'Fidelity 500 Index Fund', 'quantity': 310.0, 'price': 198.40, 'gain_loss': 24.3},
            {'symbol': 'FSPSX', 'name': 'Fidelity Intl Index Fund', 'quantity': 180.0, 'price': 48.20, 'gain_loss': -1.5},
            {'symbol': 'FXNAX', 'name': 'Fidelity US Bond Index Fund', 'quantity': 450.0, 'price': 10.85, 'gain_loss': 2.9},
            {'symbol': 'FSSNX', 'name': 'Fidelity Small Cap Index Fund', 'quantity': 200.0, 'price': 28.65, 'gain_loss': 8.7},
            {'symbol': 'FPADX', 'name': 'Fidelity Balanced Fund', 'quantity': 150.0, 'price': 29.10, 'gain_loss': 11.2},
            {'symbol': 'FSMAX', 'name': 'Fidelity Ext Market Index Fund', 'quantity': 275.0, 'price': 82.50, 'gain_loss': 6.4},
        ],
        'E*TRADE Roth IRA': [
            {'symbol': 'MSFT', 'name': 'Microsoft Corp', 'quantity': 30.0, 'price': 415.80, 'gain_loss': 35.2},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc', 'quantity': 45.0, 'price': 175.40, 'gain_loss': 22.8},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc', 'quantity': 20.0, 'price': 185.60, 'gain_loss': 28.9},
            {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'quantity': 15.0, 'price': 248.50, 'gain_loss': 14.1},
        ],
        'Schwab Taxable': [
            {'symbol': 'SCHD', 'name': 'Schwab US Dividend Equity ETF', 'quantity': 100.0, 'price': 78.90, 'gain_loss': 9.3},
            {'symbol': 'SCHX', 'name': 'Schwab US Large-Cap ETF', 'quantity': 85.0, 'price': 58.20, 'gain_loss': 15.7},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corp', 'quantity': 12.0, 'price': 485.30, 'gain_loss': 112.5},
        ],
    }
    # Compute value for each holding and scale to match account balance
    for acct in DEMO_INVESTMENT_ACCOUNTS:
        acct_name = acct['name']
        h_list = holdings_map.get(acct_name, [])
        raw_total = sum(h['quantity'] * h['price'] for h in h_list)
        scale = acct['balance'] / raw_total if raw_total > 0 else 1
        for h in h_list:
            h['value'] = round(h['quantity'] * h['price'] * scale, 2)
        holdings_map[acct_name] = h_list
    return holdings_map

DEMO_HOLDINGS = _gen_holdings()

DEMO_DUE_DATES = {
    'Rent / Mortgage': (1, 2200), 'Student Loans': (8, 485), 'Car Payment': (15, 520),
    'Credit Card': (22, 0), 'Car Insurance': (28, 165),
}


def generate_transactions(year, month):
    from calendar import monthrange
    _, days_in_month = monthrange(year, month)
    now = datetime.now()
    max_day = now.day if (year == now.year and month == now.month) else days_in_month
    transactions = []
    for category, freq in CATEGORY_FREQ.items():
        count = max(1, freq + random.randint(-2, 2))
        min_amt, max_amt = SPEND_RANGES[category]
        merchants = MERCHANT_POOLS[category]
        group = CATEGORY_GROUPS[category]
        for _ in range(count):
            day = random.randint(1, max_day)
            transactions.append({
                'Date': date(year, month, day).strftime('%Y-%m-%d'),
                'Merchant': random.choice(merchants),
                'Category Name': category,
                'Category Group': group,
                'Amount': f"-{round(random.uniform(min_amt, max_amt), 2)}",
            })
    return pd.DataFrame(transactions)


def generate_months_of_data(num_months=6):
    now = datetime.now()
    all_tx = []
    for i in range(num_months):
        dt = now - timedelta(days=30 * i)
        old_state = random.getstate()
        random.seed(42 + i * 17)
        all_tx.append(generate_transactions(dt.year, dt.month))
        random.setstate(old_state)
    return pd.concat(all_tx, ignore_index=True)


# ========================
# CSV PARSER
# ========================
def parse_csv_transactions(uploaded_file):
    try:
        raw = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        return None
    if raw.empty:
        st.error("CSV file is empty.")
        return None
    
    cols_lower = {c: c.strip().lower().replace(' ', '_') for c in raw.columns}
    raw = raw.rename(columns=cols_lower)
    cols = list(raw.columns)
    
    date_col = next((c for c in cols if any(k in c for k in ['date', 'posted', 'transaction_date'])), None)
    amount_col = next((c for c in cols if any(k in c for k in ['amount', 'debit', 'transaction_amount'])), None)
    merchant_col = next((c for c in cols if any(k in c for k in ['merchant', 'description', 'payee', 'name', 'memo', 'summary', 'original_description'])), None)
    cat_col = next((c for c in cols if any(k in c for k in ['category', 'category_name', 'type'])), None)
    cat_group_col = next((c for c in cols if 'group' in c and 'category' in c), None)
    
    if not date_col or not amount_col:
        st.error(f"Could not find date and amount columns. Found: {', '.join(cols)}")
        return None
    
    def clean_amount(val):
        if pd.isna(val): return 0.0
        s = str(val).replace(',', '').replace('$', '').strip()
        if s.startswith('(') and s.endswith(')'): s = '-' + s[1:-1]
        try: return float(s)
        except ValueError: return 0.0
    
    result = pd.DataFrame()
    result['Date'] = pd.to_datetime(raw[date_col], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')
    result['Amount'] = raw[amount_col].apply(clean_amount)
    
    non_zero = result['Amount'][result['Amount'] != 0]
    if len(non_zero) > 0 and (non_zero > 0).mean() > 0.7:
        result['Amount'] = -result['Amount'].abs()
    result['Amount'] = result['Amount'].apply(str)
    
    result['Merchant'] = raw[merchant_col].fillna('Unknown').astype(str) if merchant_col else 'Unknown'
    result['Category Name'] = raw[cat_col].fillna('Uncategorized').astype(str) if cat_col else 'Uncategorized'
    result['Category Group'] = raw[cat_group_col].fillna(result['Category Name']).astype(str) if cat_group_col else result['Category Name']
    
    result = result.dropna(subset=['Date'])
    result = result[result['Date'] != 'NaT']
    return result


# ========================
# LOCAL STORAGE (Browser Persistence)
# ========================
LOCAL_STORAGE_KEY = "budget_dashboard_config"

def get_local_storage():
    """Get LocalStorage instance."""
    return LocalStorage()

def get_default_config():
    return {
        'family_name': 'My Budget',
        'monthly_income': 3700,
        'fixed_expenses': {
            'Household': {'Rent / Mortgage': 1200, 'Electric': 120, 'Internet': 65, 'Cell Phone': 85},
            'Auto & Insurance': {'Car Payment': 350, 'Car Insurance': 150},
            'Debt Payments': {},
            'Subscriptions': {},
        },
        'accounts': [
            {'name': 'Checking Account', 'type': 'checking', 'balance': 0, 'limit': 0},
            {'name': 'Savings Account', 'type': 'savings', 'balance': 0, 'limit': 0},
        ],
        'due_dates': {},
    }


def init_session_config(local_storage):
    """Initialize session state, loading from browser localStorage if available."""
    if 'config_loaded' not in st.session_state:
        st.session_state['config_loaded'] = True
        # Try to load from browser localStorage
        saved = local_storage.getItem(LOCAL_STORAGE_KEY)
        if saved and isinstance(saved, dict) and 'monthly_income' in saved:
            st.session_state['config'] = saved
            st.session_state['config_source'] = 'saved'
        elif saved and isinstance(saved, str):
            try:
                parsed = json.loads(saved)
                if 'monthly_income' in parsed:
                    st.session_state['config'] = parsed
                    st.session_state['config_source'] = 'saved'
                else:
                    st.session_state['config'] = get_default_config()
                    st.session_state['config_source'] = 'default'
            except:
                st.session_state['config'] = get_default_config()
                st.session_state['config_source'] = 'default'
        else:
            st.session_state['config'] = get_default_config()
            st.session_state['config_source'] = 'default'


def save_config(local_storage, config):
    """Save config to browser localStorage."""
    local_storage.setItem(LOCAL_STORAGE_KEY, config)


# ========================
# HELPERS
# ========================
def parse_amount(val):
    if not val: return 0.0
    try: return float(str(val).replace(',', '').replace('$', '').strip())
    except (ValueError, TypeError): return 0.0


def get_filtered_spending(tx_df, period='current'):
    if tx_df.empty: return pd.DataFrame(), 0
    now = datetime.now()
    tx_df = tx_df.copy()
    tx_df['parsed_date'] = pd.to_datetime(tx_df['Date'], format='mixed', errors='coerce')
    tx_df['parsed_amount'] = tx_df['Amount'].apply(parse_amount)
    
    if period == 'ytd':
        mask = (tx_df['parsed_date'].dt.year == now.year) & (tx_df['parsed_amount'] < 0)
    elif period == 'current':
        mask = (tx_df['parsed_date'].dt.month == now.month) & (tx_df['parsed_date'].dt.year == now.year) & (tx_df['parsed_amount'] < 0)
    else:
        try:
            y, m = int(period[:4]), int(period[5:7])
            mask = (tx_df['parsed_date'].dt.month == m) & (tx_df['parsed_date'].dt.year == y) & (tx_df['parsed_amount'] < 0)
        except:
            mask = tx_df['parsed_amount'] < 0
    
    filtered = tx_df[mask].copy()
    filtered['spend'] = filtered['parsed_amount'].abs()
    for col in ['Category Group', 'Category Name']:
        if col in filtered.columns:
            filtered[col] = filtered[col].replace({'#N/A': 'Uncategorized', '': 'Uncategorized', 'nan': 'Uncategorized'}).fillna('Uncategorized')
    return filtered, filtered['spend'].sum()


def get_available_months(tx_df):
    if tx_df.empty: return []
    tx_df = tx_df.copy()
    tx_df['parsed_date'] = pd.to_datetime(tx_df['Date'], format='mixed', errors='coerce')
    months = tx_df['parsed_date'].dropna().dt.to_period('M').unique()
    return sorted([str(m) for m in months], reverse=True)


def render_kpi(label, value, color, prefix="$", sub=""):
    formatted = f"-${abs(value):,.0f}" if (prefix == "$" and value < 0) else (f"${value:,.0f}" if prefix == "$" else (f"{value:.0f}%" if prefix == "%" else f"{value:,.0f}"))
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value {color}">{formatted}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)


def render_progress(name, balance, limit):
    pct = (balance / limit * 100) if limit > 0 else 0
    color = '#fb7185' if pct > 70 else ('#fbbf24' if pct > 40 else '#34d399')
    st.markdown(f'''<div class="progress-container"><div class="progress-header"><span class="progress-name">{name}</span><span class="progress-stats" style="color:{color}">${balance:,.0f} / ${limit:,.0f} &nbsp; ({pct:.0f}%)</span></div><div class="progress-bar-track"><div class="progress-bar-fill" style="width:{min(pct,100)}%; background: linear-gradient(90deg, {color}, {color}88);"></div></div></div>''', unsafe_allow_html=True)


def make_donut(spending_df):
    if spending_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="<b>No transactions yet</b><br><br>Upload a bank CSV or switch to<br>Demo Test Data to see spending",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color='#94a3b8'),
            align='center'
        )
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380,
            margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig
    by_group = spending_df.groupby('Category Group')['spend'].sum().reset_index().sort_values('spend', ascending=False)
    by_group = by_group[by_group['spend'] > 0]
    colors = ['#60a5fa', '#34d399', '#fbbf24', '#fb7185', '#a78bfa', '#fb923c', '#2dd4bf', '#f472b6', '#818cf8', '#94a3b8', '#22d3ee', '#84cc16']
    fig = go.Figure(data=[go.Pie(labels=by_group['Category Group'], values=by_group['spend'], hole=0.6,
        marker=dict(colors=colors[:len(by_group)], line=dict(color='rgba(10,14,26,0.8)', width=3)),
        textinfo='percent', textfont=dict(size=12, color='#e2e8f0', family='Inter'),
        hovertemplate='<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>',
        pull=[0.015]*len(by_group), direction='clockwise', sort=True)])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'), height=380, margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(font=dict(size=11, color='#94a3b8', family='Inter'), bgcolor='rgba(0,0,0,0)', orientation='v', yanchor='middle', y=0.5, itemclick=False, itemdoubleclick=False), showlegend=True)
    return fig


def make_budget_gauge(used_pct):
    display_pct = min(used_pct, 120)
    bar_color = '#34d399' if used_pct <= 60 else ('#fbbf24' if used_pct <= 85 else '#fb7185')
    fig = go.Figure(go.Indicator(mode="gauge+number", value=display_pct,
        number={'suffix': '%', 'font': {'size': 42, 'color': bar_color, 'family': 'Inter'}},
        gauge={'axis': {'range': [0, 120], 'tickwidth': 0, 'tickcolor': 'rgba(0,0,0,0)', 'tickfont': {'color': 'rgba(0,0,0,0)'}},
            'bar': {'color': bar_color, 'thickness': 0.3}, 'bgcolor': 'rgba(255,255,255,0.04)', 'borderwidth': 0,
            'steps': [{'range': [0, 60], 'color': 'rgba(52,211,153,0.1)'}, {'range': [60, 85], 'color': 'rgba(251,191,36,0.1)'}, {'range': [85, 120], 'color': 'rgba(251,113,133,0.1)'}]}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'), height=200, margin=dict(l=30, r=30, t=30, b=0))
    return fig


# ========================
# FINTA / PRODUCTION DATA
# ========================

def get_credentials():
    """Get Google credentials from Streamlit secrets or local file."""
    try:
        # Streamlit Cloud: read from secrets
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            info = dict(st.secrets["gcp_service_account"])
            return service_account.Credentials.from_service_account_info(
                info,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
    except Exception:
        pass

    # Local: read from file
    sa_path = _APP_CONFIG.get('service_account_file', 'service-account.json') if _APP_CONFIG else 'service-account.json'
    return service_account.Credentials.from_service_account_file(
        sa_path,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )


@st.cache_data(ttl=900)  # 15 minutes
def load_finta_data():
    """Load all data from Finta Google Sheet."""
    try:
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        sheet_id = _APP_CONFIG['finta_sheet_id']

        sheets_to_load = ['Accounts', 'Transactions', 'Balance History', 'Categories']
        data = {}

        for sheet_name in sheets_to_load:
            # Retry up to 3 times on transient errors
            for attempt in range(3):
                try:
                    result = service.spreadsheets().values().get(
                        spreadsheetId=sheet_id,
                        range=f"'{sheet_name}'!A1:Z5000"
                    ).execute()
                    break
                except Exception as api_err:
                    if attempt < 2 and ('503' in str(api_err) or '429' in str(api_err) or 'unavailable' in str(api_err).lower()):
                        time.sleep(2 ** attempt)  # 1s, 2s backoff
                        continue
                    raise

            values = result.get('values', [])
            if len(values) > 1:
                header = values[0]
                rows = [r for r in values[1:] if r and r[0] != '---']
                rows = [r + [''] * (len(header) - len(r)) for r in rows]
                data[sheet_name] = pd.DataFrame(rows, columns=header)
            else:
                data[sheet_name] = pd.DataFrame()

        # Load Holdings and Securities tabs (investment positions)
        for extra_tab in ['Holdings', 'Securities']:
            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=sheet_id,
                    range=f"'{extra_tab}'!A1:P500"
                ).execute()
                values = result.get('values', [])
                if len(values) > 1:
                    header = values[0]
                    rows = [r for r in values[1:] if r and r[0] != '---' and r[0] != '']
                    rows = [r + [''] * (len(header) - len(r)) for r in rows]
                    data[extra_tab] = pd.DataFrame(rows, columns=header)
                else:
                    data[extra_tab] = pd.DataFrame()
            except Exception:
                data[extra_tab] = pd.DataFrame()

        # Load Manual Accounts tab
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range="'Manual Accounts'!A1:D100"
            ).execute()
            values = result.get('values', [])
            if len(values) > 1:
                header = values[0]
                rows = [r + [''] * (len(header) - len(r)) for r in values[1:] if r]
                data['Manual Accounts'] = pd.DataFrame(rows, columns=header)
            else:
                data['Manual Accounts'] = pd.DataFrame()
        except Exception:
            data['Manual Accounts'] = pd.DataFrame()

        return data
    except Exception as e:
        st.error("⚠️ Google Sheets is temporarily unavailable. Refresh in a minute.")
        return None


# 401(k) fund ticker mappings for NAV-based proportional allocation
FUND_TICKER_MAP = _APP_CONFIG.get('fund_ticker_map', {}) if _APP_CONFIG else {}


@st.cache_data(ttl=3600)
def get_fund_navs():
    """Look up current NAVs for 401(k) fund ticker mappings. Cached 1 hour."""
    try:
        import yfinance as yf
        navs = {}
        for fund_name, ticker in FUND_TICKER_MAP.items():
            try:
                info = yf.Ticker(ticker).info
                price = info.get('previousClose') or info.get('navPrice') or info.get('regularMarketPrice')
                if price and price > 0:
                    navs[fund_name] = price
            except Exception:
                pass
        return navs
    except ImportError:
        return {}


def parse_finta_amount(val):
    """Parse Finta amount string (e.g. '$1,847.00') to float."""
    if not val:
        return 0.0
    try:
        return float(str(val).replace(',', '').replace('$', '').strip())
    except (ValueError, TypeError):
        return 0.0


def get_manual_balances(manual_df):
    """Extract balances from the Manual Accounts tab."""
    manual = {}
    if manual_df is None or manual_df.empty:
        return manual
    for _, row in manual_df.iterrows():
        name = str(row.get('Account', '')).strip()
        bal = parse_finta_amount(row.get('Balance', 0))
        updated = str(row.get('Last Updated', ''))
        acct_type = str(row.get('Type', '')).strip().lower()
        manual[name] = {'balance': bal, 'type': acct_type, 'last_updated': updated}
    return manual


def get_account_balances(accounts_df):
    """Extract current balances from Accounts sheet."""
    balances = {}
    if accounts_df.empty:
        return balances

    for _, row in accounts_df.iterrows():
        name = str(row.get('Name', ''))
        bal = parse_finta_amount(row.get('Current Balance', 0))
        limit = parse_finta_amount(row.get('Account Limit', 0))
        acct_type = str(row.get('Account Type', ''))
        subtype = str(row.get('Account Subtype', ''))

        if 'Bonvoy' in name:
            balances['bonvoy'] = {'balance': bal, 'limit': limit, 'name': 'Bonvoy Visa'}
        elif 'Savings' in name and 'Wells' in name:
            balances['savings'] = {'balance': bal, 'name': 'Wells Fargo Savings'}
        elif 'Tesla' in name and 'Loan' in name:
            balances['tesla_loan'] = {'balance': bal, 'name': 'Tesla Loan'}
        elif acct_type == 'investment':
            if 'investments' not in balances:
                balances['investments'] = {'balance': 0, 'accounts': []}
            balances['investments']['balance'] += bal
            balances['investments']['accounts'].append({'name': name, 'balance': bal})

    return balances


# ========================
# PAGE CONFIG + CSS
# ========================
_page_title = _APP_CONFIG.get('family_name', 'Budget Dashboard') if IS_PRODUCTION else 'Budget Dashboard'
st.set_page_config(page_title=_page_title, page_icon="💰", layout="wide",
                   initial_sidebar_state='collapsed' if IS_PRODUCTION else 'expanded')

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp { background: linear-gradient(160deg, #0a0e1a 0%, #111827 40%, #0f172a 100%); color: #e2e8f0; font-family: 'Inter', sans-serif; }
    #MainMenu, footer {visibility: hidden;}
    [data-testid="stHeader"] { background: rgba(10,14,26,0.95) !important; }
    .block-container { padding-top: 3.5rem !important; max-width: 1200px; }
    .kpi-card { background: linear-gradient(145deg, rgba(30,41,59,0.8) 0%, rgba(15,23,42,0.9) 100%); border-radius: 20px; padding: 28px 20px; text-align: center; box-shadow: 0 4px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.06); backdrop-filter: blur(10px); margin-bottom: 12px; transition: transform 0.2s ease; }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; color: #64748b; }
    .kpi-value { font-size: 38px; font-weight: 800; line-height: 1; margin-bottom: 6px; }
    .kpi-sub { font-size: 11px; color: #64748b; line-height: 1.3; }
    .green { color: #34d399; } .red { color: #fb7185; } .blue { color: #60a5fa; }
    .yellow { color: #fbbf24; } .orange { color: #fb923c; } .purple { color: #a78bfa; } .teal { color: #2dd4bf; }
    .section-header { font-size: 13px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #64748b; margin: 36px 0 16px 0; padding-bottom: 10px; border-bottom: 1px solid rgba(71,85,105,0.3); }
    .progress-container { background: rgba(15,23,42,0.6); border-radius: 14px; padding: 18px 22px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.04); }
    .progress-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
    .progress-name { font-size: 14px; font-weight: 600; color: #cbd5e1; }
    .progress-stats { font-size: 13px; font-weight: 600; }
    .progress-bar-track { background: rgba(255,255,255,0.06); border-radius: 6px; height: 10px; overflow: hidden; }
    .progress-bar-fill { height: 100%; border-radius: 6px; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
    .dashboard-title { text-align: center; font-size: 22px; font-weight: 800; letter-spacing: 3px; color: #94a3b8; margin: 8px 0 2px 0; text-transform: uppercase; }
    .dashboard-subtitle { text-align: center; font-size: 12px; color: #64748b; margin-bottom: 28px; letter-spacing: 1px; }
    .demo-badge { text-align: center; margin-bottom: 8px; }
    .demo-badge span { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #000; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 4px 16px; border-radius: 20px; }
    .csv-badge { text-align: center; margin-bottom: 8px; }
    .csv-badge span { background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); color: #fff; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 4px 16px; border-radius: 20px; }
    .custom-badge { text-align: center; margin-bottom: 8px; }
    .custom-badge span { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); color: #000; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 4px 16px; border-radius: 20px; }
    .due-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; border-radius: 10px; margin-bottom: 6px; font-size: 13px; background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.03); }
    .due-name { color: #94a3b8; font-weight: 500; } .due-date { font-weight: 600; }
    .tx-table { width: 100%; border-collapse: separate; border-spacing: 0 4px; }
    .tx-table th { text-align: left; font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 1.5px; padding: 8px 12px; }
    .tx-table td { padding: 10px 12px; font-size: 13px; color: #cbd5e1; background: rgba(15,23,42,0.4); }
    .tx-table tr td:first-child { border-radius: 8px 0 0 8px; } .tx-table tr td:last-child { border-radius: 0 8px 8px 0; }
    .streamlit-expanderHeader, .streamlit-expanderHeader p, [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; font-size: 13px !important; }
    [data-testid="stExpander"] summary p { margin: 0 !important; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
    .stTextInput div[data-testid="InputInstructions"] { display: none !important; }
    [data-testid="stToast"] { left: 1rem !important; right: auto !important; background: rgba(30,41,59,0.95) !important; border: 1px solid rgba(52,211,153,0.3) !important; border-radius: 12px !important; backdrop-filter: blur(10px) !important; }
    [data-testid="stToast"] div { color: #e2e8f0 !important; }
    @keyframes slideDown {
        from { opacity: 0; max-height: 0; transform: translateY(-10px); }
        to { opacity: 1; max-height: 2000px; transform: translateY(0); }
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(96,165,250,0.2) 0%, rgba(96,165,250,0.1) 100%) !important;
        border: 1px solid rgba(96,165,250,0.4) !important;
        color: #60a5fa !important;
    }
    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: #64748b !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.06) !important;
        color: #94a3b8 !important;
    }
    .holdings-panel {
        background: linear-gradient(145deg, rgba(30,41,59,0.6) 0%, rgba(15,23,42,0.8) 100%);
        border-radius: 16px; padding: 20px 24px; margin: 0 0 16px 0;
        border: 1px solid rgba(96,165,250,0.2);
        animation: slideDown 0.35s ease-out forwards; overflow: hidden;
    }
    .holding-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 14px;
    }
    .holding-detail { font-size: 11px; color: #64748b; margin-top: 2px; }
    .holding-val { color: #e2e8f0; font-weight: 700; }
    @media (max-width: 768px) { .kpi-value { font-size: 28px; } .kpi-label { font-size: 10px; letter-spacing: 1.5px; } .block-container { padding: 0.5rem; } }
</style>
""", unsafe_allow_html=True)


# ========================
# INIT
# ========================
localS = get_local_storage()
init_session_config(localS)


# ========================
# SIDEBAR (demo mode only)
# ========================
if not IS_PRODUCTION:
 with st.sidebar:
    if st.session_state.get("view_mode") == "investments":
        st.markdown("### 📈 Investments View")
        st.info("The investments view is not customizable in this demo. Switch back to **💵 Daily Finances** to configure your budget.")
        st.caption("Investment accounts, holdings, and allocation shown here use sample data to demonstrate the feature.")

if not IS_PRODUCTION:
    is_my_budget = st.session_state.get('mode', 'demo') == 'budget'
else:
    is_my_budget = False

if not IS_PRODUCTION and st.session_state.get("view_mode") != "investments":
 with st.sidebar:
    # === STATUS MESSAGES ===
    if st.session_state.get('reset_success'):
        st.session_state['reset_success'] = False
        st.session_state['show_reset_banner'] = True
    
    # === MODE ===
    if 'mode' not in st.session_state:
        st.session_state['mode'] = 'demo'
    
    col_demo, col_budget = st.columns(2)
    with col_demo:
        demo_type = "primary" if st.session_state['mode'] == 'demo' else "secondary"
        if st.button("🎲 Demo Test Data", use_container_width=True, type=demo_type):
            st.session_state['mode'] = 'demo'
            st.rerun()
    with col_budget:
        budget_type = "primary" if st.session_state['mode'] == 'budget' else "secondary"
        if st.button("💰 Try with My Data", use_container_width=True, type=budget_type):
            st.session_state['mode'] = 'budget'
            st.rerun()
    
    is_my_budget = st.session_state['mode'] == 'budget'
    cfg = st.session_state['config']
    
    if not is_my_budget:
        st.info("👀 Viewing sample data for a fictional family. Switch to **💰 Try with My Data** to build your own.")
        st.caption("The sidebar controls below exist because this is a demo without real bank connections. In a real setup, you connect your accounts through [Finta](https://www.finta.io/), which uses [Plaid](https://plaid.com/) — the same secure bank-connection layer trusted by Chase, Vanguard, and major financial institutions worldwide — to sync transactions automatically. No manual entry needed.")
    else:
        st.markdown("🔒 **Your data never leaves your browser.** No accounts, no servers, no tracking. Everything you enter stays on this device only.")
        
        # === CSV UPLOAD ===
        st.markdown("### 📄 Upload Transactions")
        st.caption("Drop CSVs from your bank(s). Multiple OK. [How?](https://github.com/spencerjw/budget-dashboard-demo/blob/main/GETTING-STARTED.md#step-6-upload-your-transactions-optional-but-recommended)")
        uploaded_files = st.file_uploader("CSV files", type=['csv'], key="csv_upload",
            accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file{'s' if len(uploaded_files) > 1 else ''} loaded")
        
        st.markdown("---")
        
        # === BASIC INFO ===
        st.markdown("### 🏠 My Info")
        cfg['family_name'] = st.text_input("Dashboard Name", value=cfg['family_name'])
        cfg['monthly_income'] = st.number_input("Monthly Take-Home Pay ($)", value=cfg['monthly_income'],
            step=100, min_value=0)
        
        st.markdown("---")
    
    if is_my_budget:
        # === FIXED EXPENSES ===
        st.markdown("### 📋 Monthly Bills")
        st.caption("Recurring bills. Not groceries or eating out. [What goes here?](https://github.com/spencerjw/budget-dashboard-demo/blob/main/GETTING-STARTED.md#-monthly-bills)")
        
        expense_categories = list(cfg['fixed_expenses'].keys())
        
        # Track which expander to keep open
        if 'open_expense_cat' not in st.session_state:
            st.session_state['open_expense_cat'] = None
        
        for cat_name in expense_categories:
            is_open = st.session_state.get('open_expense_cat') == cat_name
            with st.expander(f"**{cat_name}** (${sum(cfg['fixed_expenses'][cat_name].values()):,.0f}/mo)", expanded=is_open):
                items = cfg['fixed_expenses'][cat_name]
                updated_items = {}
                
                for item_name, amount in list(items.items()):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        new_name = st.text_input("Name", value=item_name, key=f"exp_name_{cat_name}_{item_name}", label_visibility="collapsed")
                    with col2:
                        new_amount = st.number_input("$", value=amount, step=5, min_value=0, key=f"exp_amt_{cat_name}_{item_name}", label_visibility="collapsed")
                    with col3:
                        delete = st.button("🗑️", key=f"exp_del_{cat_name}_{item_name}")
                    
                    if delete:
                        cfg['fixed_expenses'][cat_name] = {k: v for k, v in items.items() if k != item_name}
                        st.session_state['open_expense_cat'] = cat_name
                        st.rerun()
                    elif new_name.strip():
                        updated_items[new_name.strip()] = new_amount
                
                # Add new bill
                show_add_key = f"show_add_{cat_name}"
                if show_add_key not in st.session_state:
                    st.session_state[show_add_key] = False
                
                if st.session_state[show_add_key]:
                    st.markdown("---")
                    nc1, nc2 = st.columns([3, 2])
                    with nc1:
                        new_bill_name = st.text_input("Bill name", key=f"new_name_{cat_name}", placeholder="e.g. Netflix", label_visibility="collapsed")
                    with nc2:
                        new_bill_amount = st.number_input("Amount", value=0, step=5, min_value=0, key=f"new_amt_{cat_name}", label_visibility="collapsed")
                    
                    sc1, sc2 = st.columns(2)
                    with sc1:
                        if st.button("✅ Save", key=f"save_bill_{cat_name}", use_container_width=True):
                            if new_bill_name.strip() and new_bill_amount > 0:
                                updated_items[new_bill_name.strip()] = new_bill_amount
                                cfg['fixed_expenses'][cat_name] = updated_items
                                st.session_state[show_add_key] = False
                                st.session_state['open_expense_cat'] = cat_name
                                st.rerun()
                    with sc2:
                        if st.button("Cancel", key=f"cancel_bill_{cat_name}", use_container_width=True):
                            st.session_state[show_add_key] = False
                            st.session_state['open_expense_cat'] = cat_name
                            st.rerun()
                else:
                    if st.button("➕ Add a bill", key=f"add_{cat_name}", use_container_width=True):
                        st.session_state[show_add_key] = True
                        st.session_state['open_expense_cat'] = cat_name
                        st.rerun()
                
                st.markdown("---")
                confirm_del_key = f"confirm_del_cat_{cat_name}"
                if confirm_del_key not in st.session_state:
                    st.session_state[confirm_del_key] = False
                
                if not st.session_state[confirm_del_key]:
                    if st.button(f"🗑️ Delete {cat_name}", key=f"del_cat_{cat_name}", use_container_width=True):
                        if updated_items:
                            st.session_state[confirm_del_key] = True
                            st.session_state['open_expense_cat'] = cat_name
                            st.rerun()
                        else:
                            del cfg['fixed_expenses'][cat_name]
                            st.session_state['open_expense_cat'] = None
                            st.rerun()
                else:
                    bill_count = len(updated_items)
                    st.warning(f"⚠️ This will delete **{cat_name}** and its **{bill_count} bill{'s' if bill_count != 1 else ''}**.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete all", key=f"yes_del_cat_{cat_name}", use_container_width=True, type="primary"):
                            del cfg['fixed_expenses'][cat_name]
                            st.session_state[confirm_del_key] = False
                            st.session_state['open_expense_cat'] = None
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"no_del_cat_{cat_name}", use_container_width=True):
                            st.session_state[confirm_del_key] = False
                            st.session_state['open_expense_cat'] = cat_name
                            st.rerun()
                
                cfg['fixed_expenses'][cat_name] = updated_items
        
        with st.expander("➕ Add a new category"):
            new_cat = st.text_input("Category name", placeholder="e.g. Medical, Childcare")
            if st.button("Create Category") and new_cat.strip():
                if new_cat.strip() not in cfg['fixed_expenses']:
                    cfg['fixed_expenses'][new_cat.strip()] = {}
                    st.rerun()
        
        st.markdown("---")
        
        # === ACCOUNTS ===
        st.markdown("### 💰 Accounts & Balances")
        st.caption("Tap each account to enter your current balance. Check your bank app for the numbers. [Help](https://github.com/spencerjw/budget-dashboard-demo/blob/main/GETTING-STARTED.md#-accounts--balances)")
        
        updated_accounts = []
        
        cash_accounts = [a for a in cfg['accounts'] if a['type'] in ('checking', 'savings', 'investment')]
        debt_accounts = [a for a in cfg['accounts'] if a['type'] in ('credit', 'loan')]
        
        st.markdown("#### 🏦 Cash & Savings")
        st.caption("👆 Tap to expand and enter your balance.")
        
        for i, acct in enumerate(cash_accounts):
            with st.expander(f"**{acct['name']}** — ${acct['balance']:,.0f}"):
                a_name = st.text_input("Account Name", value=acct['name'], key=f"cash_name_{i}")
                a_type = st.selectbox("Account Type", ['checking', 'savings', 'investment'],
                    index=['checking', 'savings', 'investment'].index(acct['type']),
                    format_func=lambda x: {'checking': '🔵 Checking', 'savings': '🟢 Savings', 'investment': '📈 Investment / Retirement'}[x],
                    key=f"cash_type_{i}")
                a_balance = st.number_input("Current Balance ($)", value=acct['balance'], step=100, key=f"cash_bal_{i}")
                
                delete_acct = st.button("🗑️ Remove", key=f"cash_del_{i}")
                if not delete_acct:
                    updated_accounts.append({'name': a_name, 'type': a_type, 'balance': a_balance, 'limit': 0})
        
        with st.expander("➕ Add a cash / savings account"):
            na_name = st.text_input("Account name", placeholder="e.g. Ally Savings", key="new_cash_name")
            na_type = st.selectbox("Type", ['checking', 'savings', 'investment'],
                format_func=lambda x: {'checking': '🔵 Checking', 'savings': '🟢 Savings', 'investment': '📈 Investment / Retirement'}[x],
                key="new_cash_type")
            na_balance = st.number_input("Current Balance ($)", value=0, step=100, key="new_cash_bal")
            if st.button("Add Account", key="add_cash") and na_name.strip():
                updated_accounts.append({'name': na_name.strip(), 'type': na_type, 'balance': na_balance, 'limit': 0})
                st.rerun()
        
        st.markdown("#### 💳 Credit Cards & Loans")
        st.caption("👆 Tap to expand. Enter balance owed, limit, and due date.")
        
        for i, acct in enumerate(debt_accounts):
            pct = f" ({acct['balance']/acct['limit']*100:.0f}%)" if acct['limit'] > 0 else ""
            with st.expander(f"**{acct['name']}** — ${acct['balance']:,.0f}{pct}"):
                a_name = st.text_input("Account Name", value=acct['name'], key=f"debt_name_{i}")
                a_type = st.selectbox("Account Type", ['credit', 'loan'],
                    index=['credit', 'loan'].index(acct['type']),
                    format_func=lambda x: {'credit': '💳 Credit Card', 'loan': '🏦 Loan (car, student, personal, etc.)'}[x],
                    key=f"debt_type_{i}")
                a_balance = st.number_input("Current Balance Owed ($)", value=acct['balance'], step=100, min_value=0, key=f"debt_bal_{i}")
                
                if a_type == 'credit':
                    a_limit = st.number_input("Credit Limit ($)", value=acct['limit'], step=100, min_value=0, key=f"debt_lim_{i}")
                else:
                    a_limit = st.number_input("Original Loan Amount ($)", value=acct['limit'], step=100, min_value=0, key=f"debt_lim_{i}")
                
                a_due_day = st.number_input("Payment Due Date (day of month)", value=acct.get('due_day', 0),
                    min_value=0, max_value=31, step=1, key=f"debt_due_{i}")
                
                delete_acct = st.button("🗑️ Remove", key=f"debt_del_{i}")
                if not delete_acct:
                    updated_accounts.append({'name': a_name, 'type': a_type, 'balance': a_balance, 'limit': a_limit, 'due_day': a_due_day})
        
        with st.expander("➕ Add a credit card or loan"):
            nd_name = st.text_input("Account name", placeholder="e.g. Chase Visa, Car Loan", key="new_debt_name")
            nd_type = st.selectbox("Type", ['credit', 'loan'],
                format_func=lambda x: {'credit': '💳 Credit Card', 'loan': '🏦 Loan'}[x],
                key="new_debt_type")
            nd_balance = st.number_input("Balance Owed ($)", value=0, step=100, min_value=0, key="new_debt_bal")
            if nd_type == 'credit':
                nd_limit = st.number_input("Credit Limit ($)", value=0, step=100, min_value=0, key="new_debt_lim")
            else:
                nd_limit = st.number_input("Original Loan Amount ($)", value=0, step=100, min_value=0, key="new_debt_lim")
            nd_due = st.number_input("Payment Due Date (day of month)", value=0, min_value=0, max_value=31, step=1, key="new_debt_due")
            if st.button("Add Account", key="add_debt") and nd_name.strip():
                updated_accounts.append({'name': nd_name.strip(), 'type': nd_type, 'balance': nd_balance, 'limit': nd_limit, 'due_day': nd_due})
                st.rerun()
        
        cfg['accounts'] = updated_accounts
        
        st.markdown("---")
        
        # === DUE DATES ===
        st.markdown("### 📅 Bill Due Dates")
        st.caption("Add bills that aren't credit cards or loans (those due dates are set above). Enter the day of the month each is due -- e.g. rent on the 1st, electric on the 15th. Shows up in the Upcoming Bills section of your dashboard.")
        
        updated_dues = {}
        for bill_name, val in list(cfg['due_dates'].items()):
            day, amount = (val, 0) if isinstance(val, int) else val
            c1, c2, c3, c4 = st.columns([3, 1.5, 1, 0.5])
            with c1:
                st.markdown(f"<span style='color:#94a3b8;font-size:13px;'>{bill_name}</span>", unsafe_allow_html=True)
            with c2:
                new_amt = st.number_input("$", value=amount, step=5, min_value=0, key=f"due_amt_{bill_name}", label_visibility="collapsed")
            with c3:
                new_day = st.number_input("Day", value=day, min_value=1, max_value=31, key=f"due_{bill_name}", label_visibility="collapsed")
            with c4:
                del_due = st.button("🗑️", key=f"due_del_{bill_name}")
            if del_due:
                cfg['due_dates'] = {k: v for k, v in cfg['due_dates'].items() if k != bill_name}
                st.rerun()
            else:
                updated_dues[bill_name] = (new_day, new_amt)
        
        st.caption("Add a new bill due date:")
        nc1, nc2, nc3 = st.columns([3, 1.5, 1])
        with nc1:
            new_due_name = st.text_input("Bill name", key="new_due_name", placeholder="e.g. Rent", label_visibility="collapsed")
        with nc2:
            new_due_amt = st.number_input("$", value=0, step=5, min_value=0, key="new_due_amt", label_visibility="collapsed")
        with nc3:
            new_due_day = st.number_input("Day", value=1, min_value=1, max_value=31, key="new_due_day", label_visibility="collapsed")
        if st.button("➕ Add Due Date", key="add_due_btn", use_container_width=True):
            if new_due_name.strip():
                updated_dues[new_due_name.strip()] = (new_due_day, new_due_amt)
        
        cfg['due_dates'] = updated_dues
        
        st.markdown("---")
        
        # === SAVE BUTTON ===
        save_clicked = st.button("💾 Save Changes", use_container_width=True, type="primary")
        
        save_config(localS, cfg)
        
        if save_clicked:
            st.session_state['config_source'] = 'saved'
            st.success("✅ Saved! Your settings are stored in this browser.")
        elif st.session_state.get('config_source') == 'saved':
            st.caption("✅ Settings saved in this browser")
        
        st.markdown("")
        st.markdown("")
        
        # === TAKE IT WITH YOU ===
        st.markdown("### 🚀 Take It With You")
        st.caption("Ready for your own private dashboard? Download your settings, deploy your own free copy, and upload them there. [Step-by-step guide](https://github.com/spencerjw/budget-dashboard-demo/blob/main/GETTING-STARTED.md#deploy-your-own-copy-free)")
        
        config_json = json.dumps(cfg, indent=2)
        st.download_button("⬇️ Download My Settings", config_json, file_name="budget-settings.json",
            mime="application/json", use_container_width=True)
        
        uploaded_config = st.file_uploader("⬆️ Load Settings File", type=['json'],
            label_visibility="collapsed")
        if uploaded_config:
            try:
                loaded = json.loads(uploaded_config.read().decode('utf-8'))
                if 'monthly_income' in loaded and 'fixed_expenses' in loaded:
                    st.session_state['config'] = loaded
                    save_config(localS, loaded)
                    st.success("✅ Settings loaded and saved!")
                    st.rerun()
                else:
                    st.error("Invalid settings file.")
            except:
                st.error("Could not read settings file.")
        
        st.markdown("")
        
        if 'confirm_reset' not in st.session_state:
            st.session_state['confirm_reset'] = False
        
        if not st.session_state['confirm_reset']:
            if st.button("🗑️ Reset Everything", use_container_width=True):
                st.session_state['confirm_reset'] = True
                st.rerun()
        else:
            st.warning("⚠️ **Are you sure?** All your data will be lost. Download your settings first if you want to keep them.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes, delete everything", use_container_width=True, type="primary"):
                    localS.deleteAll()
                    st.session_state['config'] = get_default_config()
                    st.session_state['config_source'] = 'default'
                    st.session_state['confirm_reset'] = False
                    st.session_state['reset_success'] = True
                    st.rerun()
            with col_no:
                if st.button("Cancel", use_container_width=True):
                    st.session_state['confirm_reset'] = False
                    st.rerun()
            



# ========================
# LOAD DATA (demo mode only)
# ========================
if IS_PRODUCTION:
    cfg = {}
    transactions = None
    is_demo = False
    FIXED_EXPENSES = {}
    ACCOUNTS = []
    DUE_DATES = {}
    FAMILY_NAME = ''
    MONTHLY_INCOME = 0
    badge_class = ''
    badge_text = ''
else:
    cfg = st.session_state['config']
    transactions = None
    is_demo = False

if not IS_PRODUCTION and not is_my_budget:
    transactions = generate_months_of_data(6)
    is_demo = True
    FIXED_EXPENSES = DEMO_FIXED_EXPENSES
    ACCOUNTS = DEMO_ACCOUNTS
    DUE_DATES = DEMO_DUE_DATES
    FAMILY_NAME = "Anderson Family Budget"
    MONTHLY_INCOME = 9200
    badge_class = "demo-badge"
    badge_text = "⚡ Demo Mode — Sample Data"
elif not IS_PRODUCTION:
    is_demo = False
    FIXED_EXPENSES = cfg['fixed_expenses']
    ACCOUNTS = cfg['accounts']
    FAMILY_NAME = cfg['family_name']
    MONTHLY_INCOME = cfg['monthly_income']
    
    # Build due dates: manual entries + auto from debt accounts with due_day set
    DUE_DATES = dict(cfg.get('due_dates', {}))
    for acct in ACCOUNTS:
        if acct.get('type') in ('credit', 'loan') and acct.get('due_day', 0) > 0:
            DUE_DATES[acct['name']] = acct['due_day']
    badge_class = "custom-badge"
    badge_text = "💰 Try with My Data"
    
    # CSV upload was placed at top of sidebar - now handle the data
    csv_files = st.session_state.get('csv_upload', [])
    if csv_files:
        all_dfs = []
        for f in csv_files:
            parsed = parse_csv_transactions(f)
            if parsed is not None and not parsed.empty:
                all_dfs.append(parsed)
        if all_dfs:
            transactions = pd.concat(all_dfs, ignore_index=True)
            badge_class = "csv-badge"
            badge_text = f"📄 Your Data ({len(csv_files)} file{'s' if len(csv_files) > 1 else ''})"
        else:
            transactions = pd.DataFrame(columns=['Date', 'Amount', 'Merchant', 'Category Name', 'Category Group'])
    else:
        transactions = pd.DataFrame(columns=['Date', 'Amount', 'Merchant', 'Category Name', 'Category Group'])


# ========================
# ACCOUNT HELPERS
# ========================
def get_account_by_type(accounts, acct_type):
    """Get first account of a given type."""
    if isinstance(accounts, list):
        for a in accounts:
            if a.get('type') == acct_type:
                return a
    return None

def get_total_by_type(accounts, acct_type):
    """Sum balances for all accounts of a type."""
    if isinstance(accounts, list):
        return sum(a.get('balance', 0) for a in accounts if a.get('type') == acct_type)
    return 0

def get_credit_accounts(accounts):
    if isinstance(accounts, list):
        return [a for a in accounts if a.get('type') in ('credit', 'loan')]
    return []


# ========================
# INVESTMENTS VIEW
# ========================
def render_investments_view():
    """Render the Long-Term Investments view with demo data."""
    investment_accounts = list(DEMO_INVESTMENT_ACCOUNTS)
    holdings_by_account = DEMO_HOLDINGS
    total_investments = sum(a['balance'] for a in investment_accounts)

    # Total Portfolio KPI
    st.markdown(f"""
    <div style="background:linear-gradient(145deg, rgba(16,185,129,0.15) 0%, rgba(15,23,42,0.9) 100%);
                border:1px solid rgba(16,185,129,0.3);border-radius:20px;padding:32px;text-align:center;margin-bottom:24px;">
        <div style="font-size:13px;font-weight:600;color:#10b981;text-transform:uppercase;letter-spacing:2px;">Total Portfolio Value</div>
        <div style="font-size:48px;font-weight:800;color:#e2e8f0;margin:8px 0;">${total_investments:,.2f}</div>
        <div style="font-size:13px;color:#64748b;">{len(investment_accounts)} accounts</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📈 Investment Accounts</div>', unsafe_allow_html=True)

    investment_accounts.sort(key=lambda a: -a['balance'])

    subtype_labels = {
        'brokerage': '📊 Brokerage', 'roth': '🏦 Roth IRA',
        'sep ira': '🏦 SEP IRA', '401k': '🏢 401(k)',
    }

    if "expanded_acct" not in st.session_state:
        st.session_state["expanded_acct"] = None

    for i in range(0, len(investment_accounts), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j >= len(investment_accounts):
                continue
            acct = investment_accounts[i + j]
            subtype_label = subtype_labels.get(acct['subtype'], acct['subtype'].title())
            acct_holdings = holdings_by_account.get(acct['name'], [])
            holding_count = len(acct_holdings)
            acct_bal = acct['balance']
            is_expanded = st.session_state["expanded_acct"] == acct['name']
            arrow = "▼" if is_expanded else "▶"

            with col:
                st.markdown(f"""
                <div style="background:linear-gradient(145deg, rgba(30,41,59,0.8) 0%, rgba(15,23,42,0.9) 100%);
                            border:1px solid rgba(96,165,250,{'0.3' if is_expanded else '0.15'});border-radius:14px;padding:14px 18px;margin-bottom:4px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:1px;">{subtype_label}</span>
                            <span style="color:#64748b;margin:0 6px;">·</span>
                            <span style="font-size:14px;font-weight:700;color:#e2e8f0;">{acct['name']}</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:22px;font-weight:800;color:#60a5fa;">${acct_bal:,.2f}</span>
                            <span style="font-size:11px;color:#64748b;margin-left:8px;">{holding_count} holdings</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if holding_count > 0:
                    if st.button(f"{arrow} {'Hide' if is_expanded else 'View'} Holdings", key=f"expand_{acct['name']}", use_container_width=True):
                        if is_expanded:
                            st.session_state["expanded_acct"] = None
                        else:
                            st.session_state["expanded_acct"] = acct['name']
                        st.rerun()

        # Render holdings below the row for whichever account in this row is expanded
        for j in range(2):
            if i + j >= len(investment_accounts):
                continue
            acct = investment_accounts[i + j]
            if st.session_state["expanded_acct"] != acct['name']:
                continue

            acct_holdings = holdings_by_account.get(acct['name'], [])
            acct_bal = acct['balance']
            if not acct_holdings:
                continue

            sorted_holdings = sorted(acct_holdings, key=lambda h: -h['value'])

            for h in sorted_holdings:
                gl_num = h['gain_loss']
                gl_color = '#34d399' if gl_num >= 0 else '#fb7185'
                gl_display = f"{gl_num:+.2f}%"

                title = f"<span style=\"color:#60a5fa;font-weight:700;\">{h['symbol']}</span> <span style=\"color:#64748b;\">- {h['name'][:45]}</span>"

                val_display = f"${h['value']:,.2f}"
                pct_of_acct = (h['value'] / acct_bal * 100) if acct_bal > 0 else 0
                detail = f"{h['quantity']:,.2f} shares @ ${h['price']:,.2f}"
                pct_display = f"<span style=\"color:{gl_color};font-size:12px;font-weight:600;\">{gl_display}</span> <span style=\"color:#64748b;font-size:11px;\">| {pct_of_acct:.1f}%</span>"

                st.markdown(f'<div class="holding-row"><div style="flex:1;"><div>{title}</div><div class="holding-detail">{detail}</div></div><div style="text-align:right;"><div class="holding-val">{val_display}</div>{pct_display}</div></div>', unsafe_allow_html=True)

    # Allocation donut chart
    st.markdown('<div class="section-header">🎯 Allocation</div>', unsafe_allow_html=True)

    by_type = {}
    for acct in investment_accounts:
        if acct['subtype'] == 'brokerage':
            group = 'Brokerage'
        elif acct['subtype'] in ('roth', 'sep ira'):
            group = 'Retirement (IRA)'
        elif acct['subtype'] == '401k':
            group = 'Retirement (401k)'
        else:
            group = 'Other'
        by_type[group] = by_type.get(group, 0) + acct['balance']

    color_map = {'Brokerage': '#60a5fa', 'Retirement (IRA)': '#34d399', 'Retirement (401k)': '#a78bfa', 'Other': '#fbbf24'}
    chart_colors = [color_map.get(k, '#64748b') for k in by_type.keys()]

    fig = go.Figure(data=[go.Pie(
        labels=list(by_type.keys()),
        values=list(by_type.values()),
        hole=0.6,
        marker=dict(
            colors=chart_colors,
            line=dict(color='rgba(10,14,26,0.8)', width=3)
        ),
        textinfo='percent',
        textfont=dict(size=12, color='#e2e8f0', family='Inter'),
        hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>',
        pull=[0.015] * len(by_type),
        direction='clockwise',
        sort=True,
    )])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            font=dict(size=11, color='#94a3b8', family='Inter'),
            bgcolor='rgba(0,0,0,0)',
            orientation='v',
            yanchor='middle',
            y=0.5,
            itemclick=False,
            itemdoubleclick=False,
        ),
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ========================
    # BALANCE HISTORY SNAPSHOT
    # ========================
    st.markdown('<div class="section-header">📋 Balance History Snapshot</div>', unsafe_allow_html=True)

    random.seed(42)
    history_data = [
        ("Vanguard Brokerage", 45200, 47850),
        ("Fidelity 401(k)", 182400, 189750),
        ("E*TRADE Roth IRA", 31800, 34200),
        ("Schwab Taxable", 22100, 23650),
    ]

    for acct_name, prev_bal, current_bal in history_data:
        change = current_bal - prev_bal
        change_pct = (change / prev_bal * 100) if prev_bal > 0 else 0
        arrow = "↑" if change >= 0 else "↓"
        change_color = "#34d399" if change >= 0 else "#fb7185"

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;
                    border-bottom:1px solid rgba(255,255,255,0.04);font-size:14px;">
            <span style="color:#cbd5e1;">{acct_name}</span>
            <span style="color:{change_color};font-weight:600;">
                {arrow} ${abs(change):,.2f} ({change_pct:+.1f}%)
            </span>
        </div>
        """, unsafe_allow_html=True)


# ========================
# PRODUCTION INVESTMENTS VIEW
# ========================
def render_production_investments_view(data, manual):
    """Render the Long-Term Investments view with real Finta data."""
    DUE_DATES = _APP_CONFIG.get('due_dates', {})
    # Convert [day, amount] lists to tuples
    DUE_DATES = {k: tuple(v) if isinstance(v, list) else v for k, v in DUE_DATES.items()}
    FIXED_EXPENSES = _APP_CONFIG.get('fixed_expenses', {})

    accounts = data.get('Accounts', pd.DataFrame())
    holdings = data.get('Holdings', pd.DataFrame())
    balance_history = data.get('Balance History', pd.DataFrame())

    # Gather investment accounts from Finta
    investment_accounts = []
    if not accounts.empty:
        for _, row in accounts.iterrows():
            if str(row.get('Account Type', '')) == 'investment':
                name = str(row.get('Name', ''))
                bal = parse_finta_amount(row.get('Current Balance', 0))
                subtype = str(row.get('Account Subtype', ''))
                investment_accounts.append({
                    'name': name, 'balance': bal, 'subtype': subtype,
                    'source': 'Finta/Plaid'
                })

    # Add manual investment accounts (e.g., John Hancock 401k)
    for acct_name, acct_data in manual.items():
        if acct_data.get('type') == 'investment':
            investment_accounts.append({
                'name': acct_name, 'balance': acct_data['balance'],
                'subtype': 'manual', 'source': f"Manual (updated {acct_data.get('last_updated', 'N/A')})"
            })

    total_investments = sum(a['balance'] for a in investment_accounts)

    # Build holdings lookup by account name
    holdings_by_account = {}
    if not holdings.empty:
        for _, row in holdings.iterrows():
            acct_name = str(row.get('Account', ''))
            symbol = str(row.get('Symbol', '')).strip()
            sec_name = str(row.get('Security Name', '')).strip()
            qty = parse_finta_amount(row.get('Quantity', 0))
            value = parse_finta_amount(row.get('Total Value', 0))
            gain_loss = str(row.get('Gain / Loss', '')).strip()
            sec_type = str(row.get('Security Type', '')).strip()
            close_price = parse_finta_amount(row.get('Security Close Price', 0))

            if acct_name not in holdings_by_account:
                holdings_by_account[acct_name] = []

            display_name = symbol if symbol and symbol != 'CUR:USD' else sec_name
            if not display_name:
                display_name = sec_name or symbol

            holdings_by_account[acct_name].append({
                'symbol': symbol, 'name': sec_name, 'display': display_name,
                'quantity': qty, 'value': value, 'gain_loss': gain_loss,
                'type': sec_type, 'price': close_price
            })

    # Total Portfolio KPI
    st.markdown(f"""
    <div style="background:linear-gradient(145deg, rgba(16,185,129,0.15) 0%, rgba(15,23,42,0.9) 100%);
                border:1px solid rgba(16,185,129,0.3);border-radius:20px;padding:32px;text-align:center;margin-bottom:24px;">
        <div style="font-size:13px;font-weight:600;color:#10b981;text-transform:uppercase;letter-spacing:2px;">Total Portfolio Value</div>
        <div style="font-size:48px;font-weight:800;color:#e2e8f0;margin:8px 0;">${total_investments:,.2f}</div>
        <div style="font-size:13px;color:#64748b;">{len(investment_accounts)} accounts across {len(set(a['source'] for a in investment_accounts))} sources</div>
    </div>
    """, unsafe_allow_html=True)

    # Account cards
    st.markdown('<div class="section-header">📈 Investment Accounts</div>', unsafe_allow_html=True)

    investment_accounts.sort(key=lambda a: -a['balance'])

    subtype_labels = {
        'brokerage': '📊 Brokerage', 'roth': '🏦 Roth IRA',
        'sep ira': '🏦 SEP IRA', '401k': '🏢 401(k)',
        'manual': '✏️ Manual Entry'
    }

    if "expanded_acct" not in st.session_state:
        st.session_state["expanded_acct"] = None

    for i in range(0, len(investment_accounts), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j >= len(investment_accounts):
                continue
            acct = investment_accounts[i + j]
            subtype_label = subtype_labels.get(acct['subtype'], acct['subtype'].title())
            acct_holdings = holdings_by_account.get(acct['name'], [])
            holding_count = len([h for h in acct_holdings if h['symbol'] != 'CUR:USD'])
            acct_bal = acct['balance']
            is_expanded = st.session_state["expanded_acct"] == acct['name']
            arrow = "▼" if is_expanded else "▶"

            with col:
                st.markdown(f"""
                <div style="background:linear-gradient(145deg, rgba(30,41,59,0.8) 0%, rgba(15,23,42,0.9) 100%);
                            border:1px solid rgba(96,165,250,{'0.3' if is_expanded else '0.15'});border-radius:14px;padding:14px 18px;margin-bottom:4px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:1px;">{subtype_label}</span>
                            <span style="color:#64748b;margin:0 6px;">·</span>
                            <span style="font-size:14px;font-weight:700;color:#e2e8f0;">{acct['name']}</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:22px;font-weight:800;color:#60a5fa;">${acct_bal:,.2f}</span>
                            <span style="font-size:11px;color:#64748b;margin-left:8px;">{holding_count} holdings</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if holding_count > 0:
                    if st.button(f"{arrow} {'Hide' if is_expanded else 'View'} Holdings", key=f"expand_{acct['name']}", use_container_width=True):
                        if is_expanded:
                            st.session_state["expanded_acct"] = None
                        else:
                            st.session_state["expanded_acct"] = acct['name']
                        st.rerun()

        # Render holdings below the row for whichever account in this row is expanded
        for j in range(2):
            if i + j >= len(investment_accounts):
                continue
            acct = investment_accounts[i + j]
            if st.session_state["expanded_acct"] != acct['name']:
                continue

            acct_holdings = holdings_by_account.get(acct['name'], [])
            acct_bal = acct['balance']
            if not acct_holdings:
                continue

            # Calculate proportional values for 401k (NAV lookup + scaling)
            has_values = any(h['value'] > 0 for h in acct_holdings if h['symbol'] != 'Loan')
            if not has_values and acct_bal > 0:
                navs = get_fund_navs()
                raw_values = {}
                loan_value = 0
                for h in acct_holdings:
                    if h['symbol'] == 'Loan' or h['name'] == 'Loan':
                        # John Hancock loan: quantity IS the dollar value
                        loan_value = h['quantity']
                        h['_calc_value'] = loan_value
                        continue
                    nav = navs.get(h['name'], 0)
                    raw_values[h['name']] = (nav * h['quantity']) if nav > 0 else h['quantity']
                raw_total = sum(raw_values.values())
                invested = acct_bal - loan_value
                for h in acct_holdings:
                    if h['symbol'] == 'Loan' or h['name'] == 'Loan':
                        continue
                    raw = raw_values.get(h['name'], 0)
                    if raw_total > 0:
                        h['_calc_value'] = invested * (raw / raw_total)
                        h['_calc_pct'] = (raw / raw_total) * 100

            sorted_holdings = sorted(acct_holdings, key=lambda h: -(h.get('_calc_value', 0) or h['value'] or h['quantity']))

            for h in sorted_holdings:
                if h['symbol'] == 'CUR:USD' and h['value'] < 1:
                    continue

                gl_color, gl_display = '#64748b', ''
                gl_text = h['gain_loss']
                if gl_text:
                    try:
                        gl_num = float(gl_text.replace('%', ''))
                        gl_color = '#34d399' if gl_num >= 0 else '#fb7185'
                        gl_display = f"{gl_num:+.2f}%"
                    except (ValueError, TypeError):
                        pass

                is_loan = h['symbol'] == 'Loan' or h['name'] == 'Loan'
                if is_loan:
                    title = "<span style='color:#fbbf24;font-weight:600;'>📋 401(k) Loan</span>"
                elif h['symbol'] and h['symbol'] not in ('CUR:USD', 'Loan', '') and h['symbol'] != h['name']:
                    title = f"<span style='color:#60a5fa;font-weight:700;'>{h['symbol']}</span> <span style='color:#64748b;'>- {h['name'][:45]}</span>"
                else:
                    mapped = FUND_TICKER_MAP.get(h['name'], '')
                    if mapped:
                        title = f"<span style='color:#60a5fa;font-weight:700;'>{mapped}</span> <span style='color:#64748b;'>- {h['name'][:45]}</span>"
                    else:
                        title = f"<span style='color:#cbd5e1;font-weight:600;'>{h['name'][:55]}</span>"

                calc_val = h.get('_calc_value', 0)
                calc_pct = h.get('_calc_pct', 0)

                if is_loan:
                    val_display = f"${h['quantity']:,.2f}"
                    pct_display = "<span style='color:#fbbf24;font-size:12px;'>Outstanding balance</span>"
                    detail = ""
                elif calc_val > 0 and h['value'] == 0:
                    val_display = f"${calc_val:,.2f}"
                    pct_display = f"<span style='color:#94a3b8;font-size:12px;'>{calc_pct:.1f}% of account</span>"
                    detail = f"{h['quantity']:,.2f} shares (est. value)"
                elif h['value'] > 0:
                    val_display = f"${h['value']:,.2f}"
                    pct_of_acct = (h['value'] / acct_bal * 100) if acct_bal > 0 else 0
                    detail = f"{h['quantity']:,.2f} shares"
                    if h['price'] > 0:
                        detail += f" @ ${h['price']:,.2f}"
                    if gl_display:
                        pct_display = f"<span style='color:{gl_color};font-size:12px;font-weight:600;'>{gl_display}</span> <span style='color:#64748b;font-size:11px;'>| {pct_of_acct:.1f}%</span>"
                    else:
                        pct_display = f"<span style='color:#94a3b8;font-size:12px;'>{pct_of_acct:.1f}% of account</span>"
                else:
                    val_display, pct_display = "", ""
                    detail = f"{h['quantity']:,.2f} shares"

                st.markdown(f'<div class="holding-row"><div style="flex:1;"><div>{title}</div><div class="holding-detail">{detail}</div></div><div style="text-align:right;"><div class="holding-val">{val_display}</div>{pct_display}</div></div>', unsafe_allow_html=True)

            if not has_values:
                st.markdown('<div style="font-size:11px;color:#64748b;text-align:center;margin-top:8px;">💡 Values estimated from fund NAVs scaled to account total. Percentages are accurate.</div>', unsafe_allow_html=True)

    # Allocation breakdown by account subtype
    st.markdown('<div class="section-header">🎯 Allocation</div>', unsafe_allow_html=True)

    by_type = {}
    for acct in investment_accounts:
        st_key = acct['subtype']
        if st_key in ('brokerage',):
            group = 'Brokerage'
        elif st_key in ('roth', 'sep ira'):
            group = 'Retirement (IRA)'
        elif st_key in ('401k',):
            group = 'Retirement (401k)'
        else:
            group = 'Other'
        by_type[group] = by_type.get(group, 0) + acct['balance']

    color_map = {'Brokerage': '#60a5fa', 'Retirement (IRA)': '#34d399', 'Retirement (401k)': '#a78bfa', 'Other': '#fbbf24'}
    chart_colors = [color_map.get(k, '#64748b') for k in by_type.keys()]

    fig = go.Figure(data=[go.Pie(
        labels=list(by_type.keys()), values=list(by_type.values()), hole=0.6,
        marker=dict(colors=chart_colors, line=dict(color='rgba(10,14,26,0.8)', width=3)),
        textinfo='percent', textfont=dict(size=12, color='#e2e8f0', family='Inter'),
        hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>',
        pull=[0.015] * len(by_type), direction='clockwise', sort=True,
    )])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'), height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(font=dict(size=11, color='#94a3b8', family='Inter'), bgcolor='rgba(0,0,0,0)',
                    orientation='v', yanchor='middle', y=0.5, itemclick=False, itemdoubleclick=False),
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Balance History
    if not balance_history.empty and 'Account Type' in balance_history.columns:
        inv_history = balance_history[balance_history['Account Type'] == 'investment'].copy()
        if not inv_history.empty and 'Balance' in inv_history.columns:
            inv_history['bal'] = inv_history['Balance'].apply(parse_finta_amount)
            st.markdown('<div class="section-header">📋 Balance History Snapshot</div>', unsafe_allow_html=True)
            by_acct = inv_history.groupby('Account')['bal'].last().sort_values(ascending=False)
            for acct_name, bal in by_acct.items():
                current = next((a['balance'] for a in investment_accounts if a['name'] == acct_name), bal)
                change = current - bal
                change_pct = (change / bal * 100) if bal > 0 else 0
                arrow = "↑" if change >= 0 else "↓"
                change_color = "#34d399" if change >= 0 else "#fb7185"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;
                            border-bottom:1px solid rgba(255,255,255,0.04);font-size:14px;">
                    <span style="color:#cbd5e1;">{acct_name}</span>
                    <span style="color:{change_color};font-weight:600;">
                        {arrow} ${abs(change):,.2f} ({change_pct:+.1f}%)
                    </span>
                </div>
                """, unsafe_allow_html=True)

    # Manual accounts note
    manual_inv = [a for a in investment_accounts if a['source'].startswith('Manual')]
    if manual_inv:
        names = ", ".join(a['name'] for a in manual_inv)
        st.markdown(f"""
        <div style="text-align:center;margin-top:24px;padding:12px;background:rgba(251,191,36,0.08);
                    border:1px solid rgba(251,191,36,0.2);border-radius:12px;font-size:12px;color:#fbbf24;">
            ✏️ Manual accounts ({names}) - update balances in the "Manual Accounts" tab of your Finta Google Sheet
        </div>
        """, unsafe_allow_html=True)


# ========================
# PRODUCTION DASHBOARD
# ========================
def run_production(config):
    """Full production dashboard powered by Finta data."""
    data = load_finta_data()
    if data is None:
        return

    accounts_df = data.get('Accounts', pd.DataFrame())
    transactions = data.get('Transactions', pd.DataFrame())
    manual = get_manual_balances(data.get('Manual Accounts', pd.DataFrame()))
    balances = get_account_balances(accounts_df)

    # Config values
    FIXED_EXPENSES = config.get('fixed_expenses', {})
    DUE_DATES = config.get('due_dates', {})
    # Convert [day, amount] lists to tuples
    DUE_DATES = {k: tuple(v) if isinstance(v, list) else v for k, v in DUE_DATES.items()}
    MONTHLY_INCOME = config.get('monthly_income', 0)
    PLOC_LIMIT = config.get('ploc_limit', 0)
    PLOC_APR = config.get('ploc_apr', 0)
    family_name = config.get('family_name', 'Family Budget')

    # Title
    st.markdown(f'<div class="dashboard-title">💰 {family_name}</div>', unsafe_allow_html=True)

    # View toggle
    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "daily"

    toggle_col1, tc_daily, tc_invest, toggle_col4 = st.columns([2, 1, 1, 2])
    with tc_daily:
        if st.button("💵 Daily Finances", key="btn_daily", use_container_width=True,
                      type="primary" if st.session_state["view_mode"] == "daily" else "secondary"):
            st.session_state["view_mode"] = "daily"
            st.rerun()
    with tc_invest:
        if st.button("📈 Investments", key="btn_invest", use_container_width=True,
                      type="primary" if st.session_state["view_mode"] == "investments" else "secondary"):
            st.session_state["view_mode"] = "investments"
            st.rerun()

    if st.session_state["view_mode"] == "investments":
        render_production_investments_view(data, manual)
        st.markdown(f'<div style="text-align:center;margin-top:48px;padding:20px;color:#475569;font-size:11px;letter-spacing:1px;">{family_name.upper()} &nbsp;•&nbsp; Data synced via Finta &nbsp;&bull;&nbsp; v{APP_VERSION}</div>', unsafe_allow_html=True)
        return

    # Period selector
    available_months = get_available_months(transactions) if not transactions.empty else []
    now = datetime.now()
    current_label = now.strftime("%B %Y")

    period_options = [f"📅 {current_label} (Current)"]
    period_keys = ['current']
    for m in available_months:
        y, mo = int(m[:4]), int(m[5:7])
        if y == now.year and mo == now.month:
            continue
        from calendar import month_name
        period_options.append(f"{month_name[mo]} {y}")
        period_keys.append(m)
    period_options.append("📊 Year to Date (YTD)")
    period_keys.append('ytd')

    sel_col1, sel_col2, sel_col3 = st.columns([1, 2, 1])
    with sel_col2:
        selected_idx = st.selectbox("View Period", range(len(period_options)),
            format_func=lambda i: period_options[i], index=0, label_visibility="collapsed")

    selected_period = period_keys[selected_idx]
    is_ytd = selected_period == 'ytd'

    if is_ytd:
        subtitle_text = f"{now.year} Year to Date &nbsp;•&nbsp; Auto-synced via Finta"
    elif selected_period == 'current':
        subtitle_text = f"{current_label} &nbsp;•&nbsp; Auto-synced via Finta"
    else:
        y, mo = int(selected_period[:4]), int(selected_period[5:7])
        from calendar import month_name
        subtitle_text = f"{month_name[mo]} {y} &nbsp;•&nbsp; Auto-synced via Finta"
    st.markdown(f'<div class="dashboard-subtitle">{subtitle_text}</div>', unsafe_allow_html=True)

    # Spending
    monthly_tx, monthly_total = get_filtered_spending(transactions, selected_period) if not transactions.empty else (pd.DataFrame(), 0)

    months_elapsed = now.month if is_ytd else 1
    income_for_period = MONTHLY_INCOME * months_elapsed
    total_fixed_monthly = sum(sum(cat.values()) for cat in FIXED_EXPENSES.values())
    total_fixed = total_fixed_monthly * months_elapsed
    spendable = income_for_period - total_fixed - monthly_total

    # Account balances
    bonvoy_bal = balances.get('bonvoy', {}).get('balance', 0)
    bonvoy_limit = balances.get('bonvoy', {}).get('limit', 0)
    savings_bal = balances.get('savings', {}).get('balance', 0)

    # Manual accounts for cash totals
    ssfcu_checking = manual.get('SSFCU Checking', {}).get('balance', 0)
    ssfcu_savings = manual.get('SSFCU Savings', {}).get('balance', 0)
    total_cash = savings_bal + ssfcu_checking + ssfcu_savings

    # Investment total
    inv_total = balances.get('investments', {}).get('balance', 0)
    for acct_name, acct_data in manual.items():
        if acct_data.get('type') == 'investment':
            inv_total += acct_data['balance']

    budget_used_pct = ((total_fixed + monthly_total) / income_for_period * 100) if income_for_period > 0 else 0

    # === KPI ROW 1 ===
    c1, c2, c3 = st.columns(3)
    with c1:
        color = "green" if spendable > 200 else ("yellow" if spendable > 0 else "red")
        render_kpi("Spendable Left", spendable, color,
                   sub=f"${income_for_period:,.0f} income − ${total_fixed:,.0f} fixed − ${monthly_total:,.0f} spent")
    with c2:
        if bonvoy_limit > 0:
            pct = bonvoy_bal / bonvoy_limit * 100
            color = "red" if pct > 70 else ("yellow" if pct > 40 else "green")
            render_kpi("Bonvoy Balance", bonvoy_bal, color,
                       sub=f"{pct:.0f}% of ${bonvoy_limit:,.0f} limit")
        else:
            render_kpi("Credit Used", bonvoy_bal, "green" if bonvoy_bal == 0 else "yellow")
    with c3:
        cash_parts = []
        if savings_bal > 0:
            cash_parts.append("Wells Fargo")
        if ssfcu_checking > 0 or ssfcu_savings > 0:
            cash_parts.append("SSFCU")
        render_kpi("Cash + Savings", total_cash, "blue",
                   sub=" + ".join(cash_parts) if cash_parts else "All accounts")

    # === KPI ROW 2 ===
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Monthly Income", income_for_period, "teal",
                   sub=f"{'(' + str(months_elapsed) + ' months)' if is_ytd else 'Take-home pay'}")
    with c2:
        render_kpi("Fixed Bills", total_fixed, "orange",
                   sub=f"{sum(len(v) for v in FIXED_EXPENSES.values())} recurring items{' x ' + str(months_elapsed) + ' months' if is_ytd else ''}")
    with c3:
        render_kpi("Spent (Variable)", monthly_total, "purple" if monthly_total > 0 else "green",
                   sub=f"{len(monthly_tx)} transactions")
    with c4:
        render_kpi("Investments", inv_total, "green", sub="All accounts")

    # === DONUT + GAUGE ===
    st.markdown('<div class="section-header">📊 Spending Breakdown & Budget Health</div>', unsafe_allow_html=True)
    col_donut, col_gauge = st.columns([3, 2])
    with col_donut:
        st.plotly_chart(make_donut(monthly_tx), width='stretch', config={'displayModeBar': False})
    with col_gauge:
        st.plotly_chart(make_budget_gauge(budget_used_pct), width='stretch', config={'displayModeBar': False})
        if budget_used_pct < 75:
            st.markdown('<p style="text-align:center;color:#34d399;font-size:14px;font-weight:600;">✅ On track</p>', unsafe_allow_html=True)
        elif budget_used_pct < 95:
            st.markdown('<p style="text-align:center;color:#fbbf24;font-size:14px;font-weight:600;">⚠️ Watch spending</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="text-align:center;color:#fb7185;font-size:14px;font-weight:600;">🚨 Over budget</p>', unsafe_allow_html=True)

    # === CATEGORY DRILL-DOWN ===
    if not monthly_tx.empty and 'Category Group' in monthly_tx.columns:
        by_group = monthly_tx.groupby('Category Group')['spend'].sum().sort_values(ascending=False)
        cat_options = ['Select a category to drill down...'] + [f"{cat} (${amt:,.2f})" for cat, amt in by_group.items() if amt > 0]
        cat_keys = [None] + [cat for cat, amt in by_group.items() if amt > 0]
        if "drill_gen" not in st.session_state:
            st.session_state["drill_gen"] = 0
        dc1, dc2, dc3 = st.columns([1, 2, 1])
        with dc2:
            sel_cat_idx = st.selectbox("Drill down", range(len(cat_options)), format_func=lambda i: cat_options[i],
                index=0, label_visibility="collapsed", key=f"cat_drill_{st.session_state['drill_gen']}")
        selected_category = cat_keys[sel_cat_idx] if sel_cat_idx > 0 else None

        if selected_category:
            cat_tx = monthly_tx[monthly_tx['Category Group'] == selected_category].copy()
            cat_total, cat_count = cat_tx['spend'].sum(), len(cat_tx)
            st.markdown(f'<div style="background:linear-gradient(145deg, rgba(30,41,59,0.6) 0%, rgba(15,23,42,0.8) 100%);border-radius:16px;padding:20px 24px;margin:8px 0 16px 0;border:1px solid rgba(96,165,250,0.2);"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;"><span style="font-size:16px;font-weight:700;color:#60a5fa;">🔍 {selected_category}</span><span style="font-size:14px;color:#94a3b8;">{cat_count} transactions &nbsp;•&nbsp; ${cat_total:,.2f}</span></div>', unsafe_allow_html=True)
            if 'Category Name' in cat_tx.columns:
                by_sub = cat_tx.groupby('Category Name')['spend'].agg(['sum', 'count']).reset_index().sort_values('sum', ascending=False)
                for _, sub in by_sub.iterrows():
                    pct = (sub['sum'] / cat_total * 100) if cat_total > 0 else 0
                    st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;font-size:13px;"><span style="color:#cbd5e1;">{sub["Category Name"]} <span style="color:#475569;">({int(sub["count"])})</span></span><span style="color:#e2e8f0;font-weight:600;">${sub["sum"]:,.2f} <span style="color:#475569;font-weight:400;">({pct:.0f}%)</span></span></div><div style="background:rgba(255,255,255,0.06);border-radius:3px;height:4px;margin-bottom:4px;"><div style="width:{max(pct,2)}%;height:100%;background:#60a5fa;border-radius:3px;"></div></div>', unsafe_allow_html=True)
            st.markdown('<div style="margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);"><div style="font-size:11px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Transactions</div>', unsafe_allow_html=True)
            for _, tx in cat_tx.sort_values('parsed_date', ascending=False).iterrows():
                st.markdown(f'<div style="display:flex;justify-content:space-between;padding:4px 0;font-size:13px;"><span style="color:#64748b;min-width:50px;">{tx["parsed_date"].strftime("%b %d")}</span><span style="color:#94a3b8;flex:1;padding:0 12px;">{str(tx.get("Merchant",""))[:35]}</span><span style="color:#fb7185;font-weight:600;">${tx["spend"]:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
            if st.button("✕ Close Details", key="close_drill"):
                st.session_state["drill_gen"] += 1
                st.rerun()

    # === FIXED EXPENSES ===
    if FIXED_EXPENSES:
        st.markdown('<div style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1.5px;margin:12px 0 8px 0;">Fixed Expenses</div>', unsafe_allow_html=True)
        non_empty = {k: v for k, v in FIXED_EXPENSES.items() if v}
        if non_empty:
            exp_cols = st.columns(min(len(non_empty), 4))
            for i, (cat_name, items) in enumerate(non_empty.items()):
                cat_total = sum(items.values())
                with exp_cols[i % len(exp_cols)]:
                    with st.expander(f"**{cat_name}** — ${cat_total:,.0f}/mo"):
                        for item_name, amount in sorted(items.items(), key=lambda x: -x[1]):
                            pct_of_cat = max((amount / cat_total * 100) if cat_total > 0 else 0, 2)
                            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;font-size:13px;"><span style="color:#94a3b8;">{item_name}</span><span style="color:#e2e8f0;font-weight:600;">${amount:,.0f}</span></div><div style="background:rgba(255,255,255,0.06);border-radius:3px;height:4px;margin-bottom:6px;"><div style="width:{pct_of_cat}%;height:100%;background:#60a5fa;border-radius:3px;"></div></div>', unsafe_allow_html=True)

    # === CREDIT & DEBT ===
    st.markdown('<div class="section-header">💳 Credit & Debt</div>', unsafe_allow_html=True)
    if bonvoy_limit > 0:
        render_progress(balances.get('bonvoy', {}).get('name', 'Bonvoy Visa'), bonvoy_bal, bonvoy_limit)

    # PLOC
    if PLOC_LIMIT > 0:
        ploc_data = manual.get('SSFCU PLOC', {})
        ploc_bal = ploc_data.get('balance', 0)
        ploc_label = "PLOC (SSFCU)"
        if ploc_data.get('last_updated'):
            ploc_label += f" - updated {ploc_data['last_updated']}"
        render_progress(ploc_label, ploc_bal, PLOC_LIMIT)

    # Tesla loan
    tesla_bal = balances.get('tesla_loan', {}).get('balance', 0)
    if tesla_bal > 0:
        render_progress("Tesla Auto Loan", tesla_bal, 22000)

    # === DUE DATES ===
    if DUE_DATES:
        st.markdown('<div class="section-header">📅 Upcoming Due Dates</div>', unsafe_allow_html=True)
        today = datetime.now().day
        dues_sorted = sorted(DUE_DATES.items(), key=lambda x: x[1] if isinstance(x[1], int) else x[1][0])

        all_dues = []
        for name, val in dues_sorted:
            day, amount = (val, 0) if isinstance(val, int) else val
            if day < today:
                all_dues.append((name, day, amount, "✅ Paid", "#34d399"))
            elif day - today <= 5:
                all_dues.append((name, day, amount, "⚡ Due Soon", "#fbbf24"))
            else:
                all_dues.append((name, day, amount, f"In {day - today} days", "#64748b"))

        # Sort: unpaid first by day, then paid at bottom
        all_dues.sort(key=lambda x: (x[3].startswith('✅'), x[1]))

        INITIAL_SHOW = 12
        first_batch = all_dues[:INITIAL_SHOW]
        overflow = all_dues[INITIAL_SHOW:]

        def render_due_rows(items):
            c1, c2 = st.columns(2)
            mid = len(items) // 2
            for i, (n, d, a, s, clr) in enumerate(items):
                col = c1 if i <= mid else c2
                amt_html = f'<span style="color:#e2e8f0;font-weight:600;font-size:13px;min-width:70px;text-align:right;display:inline-block;margin-right:16px;">${a:,.0f}</span>' if a > 0 else '<span style="min-width:70px;display:inline-block;margin-right:16px;"></span>'
                with col:
                    st.markdown(f'<div class="due-row"><span class="due-name" style="flex:1;">{n}</span>{amt_html}<span class="due-date" style="color:{clr};min-width:120px;text-align:right;">{d}th — {s}</span></div>', unsafe_allow_html=True)

        render_due_rows(first_batch)

        if overflow:
            if "show_all_dues" not in st.session_state:
                st.session_state["show_all_dues"] = False
            if st.session_state["show_all_dues"]:
                render_due_rows(overflow)
                if st.button("Show Less", key="due_less"):
                    st.session_state["show_all_dues"] = False
                    st.rerun()
            else:
                if st.button(f"Show {len(overflow)} More", key="due_more"):
                    st.session_state["show_all_dues"] = True
                    st.rerun()

    # === RECENT TRANSACTIONS ===
    if not monthly_tx.empty:
        st.markdown('<div class="section-header">🧾 Recent Transactions</div>', unsafe_allow_html=True)
        PAGE_SIZE = 15
        all_tx = monthly_tx.sort_values('parsed_date', ascending=False)
        total_tx = len(all_tx)
        if "tx_show_count" not in st.session_state:
            st.session_state["tx_show_count"] = PAGE_SIZE
        show_count = min(st.session_state["tx_show_count"], total_tx)
        visible_tx = all_tx.head(show_count)
        table_html = '<table class="tx-table"><thead><tr><th>Date</th><th>Merchant</th><th>Category</th><th>Amount</th></tr></thead><tbody>'
        for _, row in visible_tx.iterrows():
            table_html += f'<tr><td>{row["parsed_date"].strftime("%b %d")}</td><td>{str(row.get("Merchant",""))[:30]}</td><td>{str(row.get("Category Group",""))}</td><td style="color:#fb7185;font-weight:600;">-${row["spend"]:,.2f}</td></tr>'
        table_html += '</tbody></table>'
        st.markdown(table_html, unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:center;color:#64748b;font-size:12px;margin-top:8px;">Showing {show_count} of {total_tx} transactions</p>', unsafe_allow_html=True)
        if show_count < total_tx:
            if st.button(f"Show More ({min(PAGE_SIZE, total_tx - show_count)} more)", key="more_tx"):
                st.session_state["tx_show_count"] = show_count + PAGE_SIZE
                st.rerun()
        if show_count > PAGE_SIZE:
            if st.button("Show Less", key="less_tx"):
                st.session_state["tx_show_count"] = PAGE_SIZE
                st.rerun()
    else:
        st.markdown('<p style="color:#64748b;text-align:center;">No transactions this month yet.</p>', unsafe_allow_html=True)

    # === FOOTER ===
    st.markdown(f'<div style="text-align:center;margin-top:48px;padding:20px;color:#475569;font-size:11px;letter-spacing:1px;">{family_name.upper()} &nbsp;•&nbsp; Data synced via Finta &nbsp;&bull;&nbsp; v{APP_VERSION}</div>', unsafe_allow_html=True)


# ========================
# MAIN DASHBOARD
# ========================
def main():
    if IS_PRODUCTION:
        run_production(_APP_CONFIG)
        return

    # Show reset confirmation banner
    if st.session_state.get('show_reset_banner'):
        st.markdown('<div style="background:rgba(52,211,153,0.15);border:1px solid rgba(52,211,153,0.4);border-radius:10px;padding:12px 16px;margin-bottom:16px;color:#34d399;font-weight:600;font-size:14px;text-align:center;">✅ All settings have been reset to defaults.</div>', unsafe_allow_html=True)
        st.session_state['show_reset_banner'] = False
    
    st.markdown(f'<div class="{badge_class}"><span>{badge_text}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dashboard-title">💰 {FAMILY_NAME}</div>', unsafe_allow_html=True)
    
    # Period selector
    available_months = get_available_months(transactions) if transactions is not None and not transactions.empty else []
    now = datetime.now()
    current_label = now.strftime("%B %Y")
    
    period_options = [f"📅 {current_label} (Current)"]
    period_keys = ['current']
    for m in available_months:
        y, mo = int(m[:4]), int(m[5:7])
        if y == now.year and mo == now.month: continue
        from calendar import month_name
        period_options.append(f"{month_name[mo]} {y}")
        period_keys.append(m)
    period_options.append("📊 Year to Date (YTD)")
    period_keys.append('ytd')
    
    # ========================
    # VIEW TOGGLE (pill style) - above date selector
    # ========================
    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "daily"

    toggle_col1, tc_daily, tc_invest, toggle_col4 = st.columns([2, 1, 1, 2])
    with tc_daily:
        if st.button(
            "💵 Daily Finances",
            key="btn_daily",
            use_container_width=True,
            type="primary" if st.session_state["view_mode"] == "daily" else "secondary"
        ):
            st.session_state["view_mode"] = "daily"
            st.rerun()
    with tc_invest:
        if st.button(
            "📈 Investments",
            key="btn_invest",
            use_container_width=True,
            type="primary" if st.session_state["view_mode"] == "investments" else "secondary"
        ):
            st.session_state["view_mode"] = "investments"
            st.rerun()

    if st.session_state["view_mode"] == "investments":
        render_investments_view()
        st.markdown(f'<div style="text-align:center;margin-top:48px;padding:20px;color:#475569;font-size:11px;letter-spacing:1px;">FAMILY BUDGET DASHBOARD &nbsp;•&nbsp; Built with Streamlit + Plotly &nbsp;&bull;&nbsp; v{APP_VERSION}</div>', unsafe_allow_html=True)
        return

    # Date selector (daily finances only)
    sel_col1, sel_col2, sel_col3 = st.columns([1, 2, 1])
    with sel_col2:
        selected_idx = st.selectbox("View Period", range(len(period_options)),
            format_func=lambda i: period_options[i], index=0, label_visibility="collapsed")
    
    selected_period = period_keys[selected_idx]
    is_ytd = selected_period == 'ytd'
    
    source_label = "Sample Data" if is_demo else "Your Data"
    if is_ytd: subtitle_text = f"{now.year} Year to Date &nbsp;•&nbsp; {source_label}"
    elif selected_period == 'current': subtitle_text = f"{current_label} &nbsp;•&nbsp; {source_label}"
    else:
        y, mo = int(selected_period[:4]), int(selected_period[5:7])
        from calendar import month_name
        subtitle_text = f"{month_name[mo]} {y} &nbsp;•&nbsp; {source_label}"
    st.markdown(f'<div class="dashboard-subtitle">{subtitle_text}</div>', unsafe_allow_html=True)

    monthly_tx, monthly_total = get_filtered_spending(transactions, selected_period) if transactions is not None and not transactions.empty else (pd.DataFrame(), 0)
    
    months_elapsed = now.month if is_ytd else 1
    income_for_period = MONTHLY_INCOME * months_elapsed
    total_fixed_monthly = sum(sum(cat.values()) for cat in FIXED_EXPENSES.values()) if isinstance(FIXED_EXPENSES, dict) else 0
    total_fixed = total_fixed_monthly * months_elapsed
    spendable = income_for_period - total_fixed - monthly_total
    budget_used_pct = ((total_fixed + monthly_total) / income_for_period * 100) if income_for_period > 0 else 0
    
    # Account summaries
    savings_bal = get_total_by_type(ACCOUNTS, 'savings')
    checking_bal = get_total_by_type(ACCOUNTS, 'checking')
    investment_bal = get_total_by_type(ACCOUNTS, 'investment')
    cash_total = savings_bal + checking_bal
    credit_accounts = get_credit_accounts(ACCOUNTS)
    primary_credit = credit_accounts[0] if credit_accounts else None
    
    # === ROW 1: BIG KPIs ===
    c1, c2, c3 = st.columns(3)
    with c1:
        color = "green" if spendable > 200 else ("yellow" if spendable > 0 else "red")
        render_kpi("Spendable Left", spendable, color,
            sub=f"${income_for_period:,.0f} income - ${total_fixed:,.0f} fixed - ${monthly_total:,.0f} spent")
    with c2:
        if primary_credit:
            cc_bal = primary_credit['balance']
            cc_lim = primary_credit['limit']
            pct = (cc_bal / cc_lim * 100) if cc_lim > 0 else 0
            color = "red" if pct > 70 else ("yellow" if pct > 40 else "green")
            render_kpi(primary_credit['name'], cc_bal, color,
                sub=f"{pct:.0f}% of ${cc_lim:,.0f} limit" if cc_lim > 0 else "")
        else:
            render_kpi("Credit Card", 0, "green", sub="No credit accounts set up")
    with c3:
        render_kpi("Cash + Savings", cash_total, "blue", sub="Checking + Savings")
    
    # === ROW 2: SECONDARY KPIs ===
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Income", income_for_period, "teal",
            sub=f"Monthly take-home{' (' + str(months_elapsed) + ' months)' if is_ytd else ''}")
    with c2:
        render_kpi("Fixed Bills", total_fixed, "orange",
            sub=f"{sum(len(v) for v in FIXED_EXPENSES.values()) if isinstance(FIXED_EXPENSES, dict) else 0} recurring items")
    with c3:
        render_kpi("Spent (Variable)", monthly_total, "purple" if monthly_total > 0 else "green",
            sub=f"{len(monthly_tx)} transactions")
    with c4:
        render_kpi("Investments", investment_bal, "green", sub="Retirement & Brokerage")
    
    # === DONUT + GAUGE ===
    st.markdown('<div class="section-header">📊 Spending Breakdown & Budget Health</div>', unsafe_allow_html=True)
    col_donut, col_gauge = st.columns([3, 2])
    with col_donut:
        st.plotly_chart(make_donut(monthly_tx), width='stretch', config={'displayModeBar': False})
    with col_gauge:
        st.plotly_chart(make_budget_gauge(budget_used_pct), width='stretch', config={'displayModeBar': False})
        if budget_used_pct < 75:
            st.markdown('<p style="text-align:center;color:#34d399;font-size:14px;font-weight:600;">✅ On track</p>', unsafe_allow_html=True)
        elif budget_used_pct < 95:
            st.markdown('<p style="text-align:center;color:#fbbf24;font-size:14px;font-weight:600;">⚠️ Watch spending</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="text-align:center;color:#fb7185;font-size:14px;font-weight:600;">🚨 Over budget</p>', unsafe_allow_html=True)
    
    # === CATEGORY DRILL-DOWN ===
    if not monthly_tx.empty and 'Category Group' in monthly_tx.columns:
        by_group = monthly_tx.groupby('Category Group')['spend'].sum().sort_values(ascending=False)
        cat_options = ['Select a category to drill down...'] + [f"{cat} (${amt:,.2f})" for cat, amt in by_group.items() if amt > 0]
        cat_keys = [None] + [cat for cat, amt in by_group.items() if amt > 0]
        if "drill_gen" not in st.session_state: st.session_state["drill_gen"] = 0
        dc1, dc2, dc3 = st.columns([1, 2, 1])
        with dc2:
            sel_cat_idx = st.selectbox("Drill down", range(len(cat_options)), format_func=lambda i: cat_options[i],
                index=0, label_visibility="collapsed", key=f"cat_drill_{st.session_state['drill_gen']}")
        selected_category = cat_keys[sel_cat_idx] if sel_cat_idx > 0 else None
        
        if selected_category:
            cat_tx = monthly_tx[monthly_tx['Category Group'] == selected_category].copy()
            cat_total, cat_count = cat_tx['spend'].sum(), len(cat_tx)
            st.markdown(f'<div style="background:linear-gradient(145deg, rgba(30,41,59,0.6) 0%, rgba(15,23,42,0.8) 100%);border-radius:16px;padding:20px 24px;margin:8px 0 16px 0;border:1px solid rgba(96,165,250,0.2);"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;"><span style="font-size:16px;font-weight:700;color:#60a5fa;">🔍 {selected_category}</span><span style="font-size:14px;color:#94a3b8;">{cat_count} transactions &nbsp;•&nbsp; ${cat_total:,.2f}</span></div>', unsafe_allow_html=True)
            if 'Category Name' in cat_tx.columns:
                by_sub = cat_tx.groupby('Category Name')['spend'].agg(['sum', 'count']).reset_index().sort_values('sum', ascending=False)
                for _, sub in by_sub.iterrows():
                    pct = (sub['sum'] / cat_total * 100) if cat_total > 0 else 0
                    st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;font-size:13px;"><span style="color:#cbd5e1;">{sub["Category Name"]} <span style="color:#475569;">({int(sub["count"])})</span></span><span style="color:#e2e8f0;font-weight:600;">${sub["sum"]:,.2f} <span style="color:#475569;font-weight:400;">({pct:.0f}%)</span></span></div><div style="background:rgba(255,255,255,0.06);border-radius:3px;height:4px;margin-bottom:4px;"><div style="width:{max(pct,2)}%;height:100%;background:#60a5fa;border-radius:3px;"></div></div>', unsafe_allow_html=True)
            st.markdown('<div style="margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);"><div style="font-size:11px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Transactions</div>', unsafe_allow_html=True)
            for _, tx in cat_tx.sort_values('parsed_date', ascending=False).iterrows():
                st.markdown(f'<div style="display:flex;justify-content:space-between;padding:4px 0;font-size:13px;"><span style="color:#64748b;min-width:50px;">{tx["parsed_date"].strftime("%b %d")}</span><span style="color:#94a3b8;flex:1;padding:0 12px;">{str(tx.get("Merchant",""))[:35]}</span><span style="color:#fb7185;font-weight:600;">${tx["spend"]:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
            if st.button("✕ Close", key="close_drill"):
                st.session_state["drill_gen"] += 1
                st.rerun()
    
    # === FIXED EXPENSES ===
    if isinstance(FIXED_EXPENSES, dict) and FIXED_EXPENSES:
        st.markdown('<div style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1.5px;margin:12px 0 8px 0;">Fixed Expenses</div>', unsafe_allow_html=True)
        non_empty = {k: v for k, v in FIXED_EXPENSES.items() if v}
        if non_empty:
            exp_cols = st.columns(min(len(non_empty), 4))
            for i, (cat_name, items) in enumerate(non_empty.items()):
                cat_total = sum(items.values())
                with exp_cols[i % len(exp_cols)]:
                    with st.expander(f"**{cat_name}** — ${cat_total:,.0f}/mo"):
                        for item_name, amount in sorted(items.items(), key=lambda x: -x[1]):
                            pct_of_cat = max((amount / cat_total * 100) if cat_total > 0 else 0, 2)
                            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;font-size:13px;"><span style="color:#94a3b8;">{item_name}</span><span style="color:#e2e8f0;font-weight:600;">${amount:,.0f}</span></div><div style="background:rgba(255,255,255,0.06);border-radius:3px;height:4px;margin-bottom:6px;"><div style="width:{pct_of_cat}%;height:100%;background:#60a5fa;border-radius:3px;"></div></div>', unsafe_allow_html=True)
    
    # === DEBT PROGRESS ===
    if credit_accounts:
        st.markdown('<div class="section-header">💳 Credit & Debt</div>', unsafe_allow_html=True)
        for acct in credit_accounts:
            if acct['limit'] > 0:
                render_progress(acct['name'], acct['balance'], acct['limit'])
    
    # === DUE DATES ===
    if DUE_DATES:
        st.markdown('<div class="section-header">📅 Upcoming Due Dates</div>', unsafe_allow_html=True)
        today = datetime.now().day
        dues_sorted = sorted(DUE_DATES.items(), key=lambda x: x[1] if isinstance(x[1], int) else x[1][0])
        
        all_dues = []
        for name, val in dues_sorted:
            day, amount = (val, 0) if isinstance(val, int) else val
            if day < today:
                all_dues.append((name, day, amount, "✅ Paid", "#34d399"))
            elif day - today <= 5:
                all_dues.append((name, day, amount, "⚡ Due Soon", "#fbbf24"))
            else:
                all_dues.append((name, day, amount, f"In {day - today} days", "#475569"))
        
        all_dues.sort(key=lambda x: (x[3].startswith('✅'), x[1]))
        
        INITIAL_SHOW = 12
        first_batch = all_dues[:INITIAL_SHOW]
        overflow = all_dues[INITIAL_SHOW:]
        
        def render_due_rows(items):
            c1, c2 = st.columns(2)
            mid = len(items) // 2
            for i, (n, d, a, s, clr) in enumerate(items):
                col = c1 if i <= mid else c2
                amt_html = f'<span style="color:#e2e8f0;font-weight:600;font-size:13px;min-width:70px;text-align:right;display:inline-block;margin-right:16px;">${a:,.0f}</span>' if a > 0 else '<span style="min-width:70px;display:inline-block;margin-right:16px;"></span>'
                with col:
                    st.markdown(f'<div class="due-row"><span class="due-name" style="flex:1;">{n}</span>{amt_html}<span class="due-date" style="color:{clr};min-width:120px;text-align:right;">{d}th — {s}</span></div>', unsafe_allow_html=True)
        
        render_due_rows(first_batch)
        
        if overflow:
            if "show_all_dues" not in st.session_state:
                st.session_state["show_all_dues"] = False
            if st.session_state["show_all_dues"]:
                render_due_rows(overflow)
                if st.button("Show Less", key="due_less"):
                    st.session_state["show_all_dues"] = False
                    st.rerun()
            else:
                if st.button(f"Show {len(overflow)} More", key="due_more"):
                    st.session_state["show_all_dues"] = True
                    st.rerun()
    
    # === RECENT TRANSACTIONS ===
    if not monthly_tx.empty:
        st.markdown('<div class="section-header">🧾 Recent Transactions</div>', unsafe_allow_html=True)
        PAGE_SIZE = 15
        all_tx = monthly_tx.sort_values('parsed_date', ascending=False)
        total_tx = len(all_tx)
        if "tx_show_count" not in st.session_state: st.session_state["tx_show_count"] = PAGE_SIZE
        show_count = min(st.session_state["tx_show_count"], total_tx)
        visible_tx = all_tx.head(show_count)
        table_html = '<table class="tx-table"><thead><tr><th>Date</th><th>Merchant</th><th>Category</th><th>Amount</th></tr></thead><tbody>'
        for _, row in visible_tx.iterrows():
            table_html += f'<tr><td>{row["parsed_date"].strftime("%b %d")}</td><td>{str(row.get("Merchant",""))[:30]}</td><td>{str(row.get("Category Group",""))}</td><td style="color:#fb7185;font-weight:600;">-${row["spend"]:,.2f}</td></tr>'
        table_html += '</tbody></table>'
        st.markdown(table_html, unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:center;color:#475569;font-size:12px;margin-top:8px;">Showing {show_count} of {total_tx}</p>', unsafe_allow_html=True)
        if show_count < total_tx:
            if st.button(f"Show More ({min(PAGE_SIZE, total_tx - show_count)} more)", key="more_tx"):
                st.session_state["tx_show_count"] = show_count + PAGE_SIZE
                st.rerun()
        if show_count > PAGE_SIZE:
            if st.button("Show Less", key="less_tx"):
                st.session_state["tx_show_count"] = PAGE_SIZE
                st.rerun()
    
    # === FOOTER ===
    st.markdown(f'<div style="text-align:center;margin-top:48px;padding:20px;color:#475569;font-size:11px;letter-spacing:1px;">FAMILY BUDGET DASHBOARD &nbsp;•&nbsp; Built with Streamlit + Plotly &nbsp;&bull;&nbsp; v{APP_VERSION}</div>', unsafe_allow_html=True)
    



if __name__ == '__main__':
    main()
