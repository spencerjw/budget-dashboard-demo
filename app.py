import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import pandas as pd
import random
import math
import json
import os
import io

# ========================
# DEMO DATA GENERATOR
# ========================
random.seed(42)

DEFAULT_FAMILY_NAME = "Anderson"
DEFAULT_MONTHLY_INCOME = 9200

DEFAULT_FIXED_EXPENSES = {
    'Household': {
        'Austin Energy': 218, 'T-Mobile Wireless': 195, 'CleanPro Maids': 150,
        'Republic Waste': 89, 'Culligan Water': 52, 'Orkin Pest Control': 55,
        'Chewy.com': 62, 'AT&T Fiber': 65, 'Lawn Pros': 120,
        'Netflix': 16, 'Spotify Family': 17, 'YouTube Premium': 14,
        'ADT Security': 45, 'Apple One': 20, 'Mealime App': 5,
    },
    'Auto & Insurance': {
        'Honda Accord Payment': 485, 'Toyota RAV4 Lease': 390,
        'Progressive Auto': 210, 'Term Life Policy': 38,
    },
    'Debt Payments': {
        'Mortgage': 2890, 'Renovation Loan': 315,
        'Student Loans': 280,
    },
    'Subscriptions & Small': {
        'Adobe Creative': 55, 'iCloud+': 3, 'HELOC Interest (est.)': 22,
    },
}

DEFAULT_CREDIT_CARD_BALANCE = random.randint(3200, 8500)
DEFAULT_CREDIT_CARD_LIMIT = 25000
DEFAULT_HELOC_BALANCE = random.randint(4000, 9000)
DEFAULT_HELOC_LIMIT = 15000
DEFAULT_SAVINGS_BALANCE = random.randint(8000, 18000)
DEFAULT_AUTO_LOAN_BALANCE = random.randint(12000, 19000)
DEFAULT_INVESTMENT_BALANCE = random.randint(45000, 120000)

DEFAULT_DUE_DATES = {
    'Mortgage': 1, 'Student Loans': 8, 'Renovation Loan': 12,
    'Chase Visa': 15, 'HELOC': 22, 'Honda Accord': 25,
    'Apple Card': 28,
}

# Merchant pools for demo data generation
MERCHANT_POOLS = {
    'Groceries': ['H-E-B', 'Whole Foods', 'Costco', 'Trader Joes', 'Sprouts', 'Central Market', 'Walmart Grocery'],
    'Restaurants': ['Chilis', 'Torchys Tacos', 'Chipotle', 'Whataburger', 'Panera Bread', 'Olive Garden', 'Pho King', 'Five Guys', 'Mod Pizza'],
    'Gas & Auto': ['Shell', 'Exxon', 'Buc-ees', 'Valvoline', 'Discount Tire', 'AutoZone'],
    'Shopping': ['Amazon', 'Target', 'Home Depot', 'Lowes', 'Best Buy', 'Kohls', 'TJ Maxx', 'Hobby Lobby'],
    'Health & Fitness': ['CVS Pharmacy', 'Walgreens', 'Planet Fitness', 'Urgent Care Co-Pay', 'Dr. Smith DDS'],
    'Entertainment': ['AMC Theatres', 'TopGolf', 'Dave & Busters', 'Alamo Drafthouse', 'Pinballz Arcade', 'Book People'],
    'Kids & Family': ['Academy Sports', 'Kumon Learning', 'Great Clips', 'YMCA', 'Party City', 'Scholastic'],
    'Home & Garden': ['Home Depot', 'Lowes', 'Bed Bath Beyond', 'Pottery Barn', 'Wayfair', 'Ace Hardware'],
    'Travel': ['Southwest Airlines', 'Marriott Hotel', 'Uber', 'Lyft', 'Enterprise Rent-A-Car'],
    'Personal Care': ['Great Clips', 'Ulta Beauty', 'Bath & Body Works', 'Sport Clips'],
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
            dt = date(year, month, day)
            transactions.append({
                'Date': dt.strftime('%Y-%m-%d'),
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
        df = generate_transactions(dt.year, dt.month)
        random.setstate(old_state)
        all_tx.append(df)
    return pd.concat(all_tx, ignore_index=True)


# ========================
# CSV PARSING
# ========================
def parse_csv_transactions(uploaded_file):
    """Parse uploaded CSV into standardized transaction DataFrame.
    
    Supports common formats: Mint, YNAB, bank exports, Finta, generic.
    Expects at minimum: a date column, an amount column, and ideally a description/merchant column.
    """
    try:
        raw = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        return None
    
    if raw.empty:
        st.error("CSV file is empty.")
        return None
    
    # Normalize column names
    cols_lower = {c: c.strip().lower().replace(' ', '_') for c in raw.columns}
    raw = raw.rename(columns=cols_lower)
    cols = list(raw.columns)
    
    # --- Date column ---
    date_candidates = [c for c in cols if any(k in c for k in ['date', 'posted', 'transaction_date'])]
    date_col = date_candidates[0] if date_candidates else None
    
    # --- Amount column ---
    amount_candidates = [c for c in cols if any(k in c for k in ['amount', 'debit', 'transaction_amount'])]
    amount_col = amount_candidates[0] if amount_candidates else None
    
    # --- Merchant / Description ---
    merchant_candidates = [c for c in cols if any(k in c for k in ['merchant', 'description', 'payee', 'name', 'memo', 'summary', 'original_description'])]
    merchant_col = merchant_candidates[0] if merchant_candidates else None
    
    # --- Category ---
    cat_candidates = [c for c in cols if any(k in c for k in ['category', 'category_name', 'category_group', 'type'])]
    cat_col = cat_candidates[0] if cat_candidates else None
    cat_group_candidates = [c for c in cols if 'group' in c and 'category' in c]
    cat_group_col = cat_group_candidates[0] if cat_group_candidates else None
    
    if not date_col or not amount_col:
        st.error(f"Could not identify required columns. Found: {', '.join(cols)}. Need at least a date and amount column.")
        return None
    
    # Build standardized DataFrame
    result = pd.DataFrame()
    result['Date'] = pd.to_datetime(raw[date_col], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')
    
    # Parse amounts -- handle various formats
    def clean_amount(val):
        if pd.isna(val):
            return 0.0
        s = str(val).replace(',', '').replace('$', '').strip()
        if s.startswith('(') and s.endswith(')'):
            s = '-' + s[1:-1]
        try:
            return float(s)
        except ValueError:
            return 0.0
    
    result['Amount'] = raw[amount_col].apply(clean_amount)
    
    # If there's a separate "credit" column, some exports split debits/credits
    credit_candidates = [c for c in cols if 'credit' in c and c != amount_col]
    if credit_candidates:
        credit_col = credit_candidates[0]
        credits = raw[credit_col].apply(clean_amount)
        # Merge: debits are negative, credits are positive
        result['Amount'] = result['Amount'].where(result['Amount'] != 0, credits)
    
    # Ensure spending is negative (convention)
    # If most amounts are positive and they look like expenses, flip sign
    non_zero = result['Amount'][result['Amount'] != 0]
    if len(non_zero) > 0 and (non_zero > 0).mean() > 0.7:
        result['Amount'] = -result['Amount'].abs()
    
    result['Amount'] = result['Amount'].apply(lambda x: str(x))
    result['Merchant'] = raw[merchant_col].fillna('Unknown').astype(str) if merchant_col else 'Unknown'
    result['Category Name'] = raw[cat_col].fillna('Uncategorized').astype(str) if cat_col else 'Uncategorized'
    result['Category Group'] = raw[cat_group_col].fillna(result['Category Name']).astype(str) if cat_group_col else result['Category Name']
    
    # Drop rows with invalid dates
    result = result.dropna(subset=['Date'])
    result = result[result['Date'] != 'NaT']
    
    return result


# ========================
# GOOGLE SHEETS LOADER (for real data mode)
# ========================
def load_google_sheets_data(sheet_id, credentials_json):
    """Load transaction data from a Google Sheet (Finta format)."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        import time
        
        creds_dict = json.loads(credentials_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        service = build('sheets', 'v4', credentials=creds)
        
        sheets_to_load = ['Accounts', 'Transactions', 'Balance History']
        data = {}
        
        for sheet_name in sheets_to_load:
            for attempt in range(3):
                try:
                    result = service.spreadsheets().values().get(
                        spreadsheetId=sheet_id,
                        range=f"'{sheet_name}'!A1:Z5000"
                    ).execute()
                    break
                except Exception as api_err:
                    if attempt < 2 and ('503' in str(api_err) or '429' in str(api_err)):
                        time.sleep(2 ** attempt)
                        continue
                    raise
            
            values = result.get('values', [])
            if len(values) > 1:
                header = values[0]
                rows = [r + [''] * (len(header) - len(r)) for r in values[1:] if r and r[0] != '---']
                data[sheet_name] = pd.DataFrame(rows, columns=header)
            else:
                data[sheet_name] = pd.DataFrame()
        
        return data
    except ImportError:
        st.error("Google API libraries not installed. Run: `pip install google-api-python-client google-auth`")
        return None
    except Exception as e:
        st.error(f"Google Sheets error: {e}")
        return None


# ========================
# HELPERS
# ========================
def parse_amount(val):
    if not val:
        return 0.0
    try:
        return float(str(val).replace(',', '').replace('$', '').strip())
    except (ValueError, TypeError):
        return 0.0


def get_filtered_spending(tx_df, period='current'):
    if tx_df.empty:
        return pd.DataFrame(), 0
    
    now = datetime.now()
    tx_df = tx_df.copy()
    tx_df['parsed_date'] = pd.to_datetime(tx_df['Date'], format='mixed', errors='coerce')
    tx_df['parsed_amount'] = tx_df['Amount'].apply(parse_amount)
    
    if period == 'ytd':
        mask = (tx_df['parsed_date'].dt.year == now.year) & (tx_df['parsed_amount'] < 0)
    elif period == 'current':
        mask = (
            (tx_df['parsed_date'].dt.month == now.month) &
            (tx_df['parsed_date'].dt.year == now.year) &
            (tx_df['parsed_amount'] < 0)
        )
    else:
        try:
            y, m = int(period[:4]), int(period[5:7])
            mask = (
                (tx_df['parsed_date'].dt.month == m) &
                (tx_df['parsed_date'].dt.year == y) &
                (tx_df['parsed_amount'] < 0)
            )
        except:
            mask = tx_df['parsed_amount'] < 0
    
    filtered = tx_df[mask].copy()
    filtered['spend'] = filtered['parsed_amount'].abs()
    
    for col in ['Category Group', 'Category Name']:
        if col in filtered.columns:
            filtered[col] = filtered[col].replace({'#N/A': 'Uncategorized', '': 'Uncategorized', 'nan': 'Uncategorized'})
            filtered[col] = filtered[col].fillna('Uncategorized')
    
    return filtered, filtered['spend'].sum()


def get_available_months(tx_df):
    if tx_df.empty:
        return []
    tx_df = tx_df.copy()
    tx_df['parsed_date'] = pd.to_datetime(tx_df['Date'], format='mixed', errors='coerce')
    months = tx_df['parsed_date'].dropna().dt.to_period('M').unique()
    return sorted([str(m) for m in months], reverse=True)


def render_kpi(label, value, color, prefix="$", sub=""):
    if prefix == "$":
        formatted = f"-${abs(value):,.0f}" if value < 0 else f"${value:,.0f}"
    elif prefix == "%":
        formatted = f"{value:.0f}%"
    else:
        formatted = f"{value:,.0f}"
    
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {color}">{formatted}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def render_progress(name, balance, limit):
    pct = (balance / limit * 100) if limit > 0 else 0
    if pct > 70:
        color = text_color = '#fb7185'
    elif pct > 40:
        color = text_color = '#fbbf24'
    else:
        color = text_color = '#34d399'
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-header">
            <span class="progress-name">{name}</span>
            <span class="progress-stats" style="color:{text_color}">${balance:,.0f} / ${limit:,.0f} &nbsp; ({pct:.0f}%)</span>
        </div>
        <div class="progress-bar-track">
            <div class="progress-bar-fill" style="width:{min(pct,100)}%; background: linear-gradient(90deg, {color}, {color}88);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def make_donut(spending_df):
    if spending_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No transactions yet", x=0.5, y=0.5, showarrow=False,
                           font=dict(size=16, color='#475569'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          height=380, margin=dict(l=0, r=0, t=0, b=0))
        return fig
    
    by_group = spending_df.groupby('Category Group')['spend'].sum().reset_index()
    by_group = by_group.sort_values('spend', ascending=False)
    by_group = by_group[by_group['spend'] > 0]
    
    colors = ['#60a5fa', '#34d399', '#fbbf24', '#fb7185', '#a78bfa',
              '#fb923c', '#2dd4bf', '#f472b6', '#818cf8', '#94a3b8',
              '#22d3ee', '#84cc16']
    
    fig = go.Figure(data=[go.Pie(
        labels=by_group['Category Group'], values=by_group['spend'], hole=0.6,
        marker=dict(colors=colors[:len(by_group)], line=dict(color='rgba(10,14,26,0.8)', width=3)),
        textinfo='percent', textfont=dict(size=12, color='#e2e8f0', family='Inter'),
        hovertemplate='<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>',
        pull=[0.015] * len(by_group), direction='clockwise', sort=True,
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'), height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(font=dict(size=11, color='#94a3b8', family='Inter'),
                    bgcolor='rgba(0,0,0,0)', orientation='v', yanchor='middle', y=0.5,
                    itemclick=False, itemdoubleclick=False),
        showlegend=True,
    )
    return fig


def make_budget_gauge(used_pct):
    display_pct = min(used_pct, 120)
    bar_color = '#34d399' if used_pct <= 60 else ('#fbbf24' if used_pct <= 85 else '#fb7185')
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=display_pct,
        number={'suffix': '%', 'font': {'size': 42, 'color': bar_color, 'family': 'Inter'}},
        gauge={
            'axis': {'range': [0, 120], 'tickwidth': 0, 'tickcolor': 'rgba(0,0,0,0)',
                     'tickfont': {'color': 'rgba(0,0,0,0)'}},
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': 'rgba(255,255,255,0.04)', 'borderwidth': 0,
            'steps': [
                {'range': [0, 60], 'color': 'rgba(52,211,153,0.1)'},
                {'range': [60, 85], 'color': 'rgba(251,191,36,0.1)'},
                {'range': [85, 120], 'color': 'rgba(251,113,133,0.1)'},
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'), height=200,
        margin=dict(l=30, r=30, t=30, b=0),
    )
    return fig


# ========================
# PAGE CONFIG + CSS
# ========================
st.set_page_config(page_title="Family Budget Dashboard", page_icon="💰", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background: linear-gradient(160deg, #0a0e1a 0%, #111827 40%, #0f172a 100%);
        color: #e2e8f0; font-family: 'Inter', sans-serif;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .block-container { padding-top: 1.5rem; max-width: 1200px; }

    .kpi-card {
        background: linear-gradient(145deg, rgba(30,41,59,0.8) 0%, rgba(15,23,42,0.9) 100%);
        border-radius: 20px; padding: 28px 20px; text-align: center;
        box-shadow: 0 4px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.06); backdrop-filter: blur(10px);
        margin-bottom: 12px; transition: transform 0.2s ease;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; color: #64748b; }
    .kpi-value { font-size: 38px; font-weight: 800; line-height: 1; margin-bottom: 6px; }
    .kpi-sub { font-size: 11px; color: #475569; line-height: 1.3; }
    
    .green { color: #34d399; } .red { color: #fb7185; } .blue { color: #60a5fa; }
    .yellow { color: #fbbf24; } .orange { color: #fb923c; } .purple { color: #a78bfa; }
    .teal { color: #2dd4bf; }
    
    .section-header {
        font-size: 13px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase;
        color: #475569; margin: 36px 0 16px 0; padding-bottom: 10px;
        border-bottom: 1px solid rgba(71,85,105,0.3);
    }
    .progress-container {
        background: rgba(15,23,42,0.6); border-radius: 14px; padding: 18px 22px;
        margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.04);
    }
    .progress-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
    .progress-name { font-size: 14px; font-weight: 600; color: #cbd5e1; }
    .progress-stats { font-size: 13px; font-weight: 600; }
    .progress-bar-track { background: rgba(255,255,255,0.06); border-radius: 6px; height: 10px; overflow: hidden; }
    .progress-bar-fill { height: 100%; border-radius: 6px; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
    
    .dashboard-title {
        text-align: center; font-size: 22px; font-weight: 800; letter-spacing: 3px;
        color: #94a3b8; margin: 8px 0 2px 0; text-transform: uppercase;
    }
    .dashboard-subtitle { text-align: center; font-size: 12px; color: #334155; margin-bottom: 28px; letter-spacing: 1px; }
    .demo-badge { text-align: center; margin-bottom: 8px; }
    .demo-badge span {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #000; font-size: 11px; font-weight: 700; letter-spacing: 2px;
        text-transform: uppercase; padding: 4px 16px; border-radius: 20px;
    }
    .csv-badge { text-align: center; margin-bottom: 8px; }
    .csv-badge span {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        color: #fff; font-size: 11px; font-weight: 700; letter-spacing: 2px;
        text-transform: uppercase; padding: 4px 16px; border-radius: 20px;
    }
    .live-badge { text-align: center; margin-bottom: 8px; }
    .live-badge span {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
        color: #000; font-size: 11px; font-weight: 700; letter-spacing: 2px;
        text-transform: uppercase; padding: 4px 16px; border-radius: 20px;
    }
    
    .due-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 16px; border-radius: 10px; margin-bottom: 6px;
        font-size: 13px; background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.03);
    }
    .due-name { color: #94a3b8; font-weight: 500; }
    .due-date { font-weight: 600; }
    
    .tx-table { width: 100%; border-collapse: separate; border-spacing: 0 4px; }
    .tx-table th {
        text-align: left; font-size: 11px; font-weight: 700; color: #475569;
        text-transform: uppercase; letter-spacing: 1.5px; padding: 8px 12px;
    }
    .tx-table td { padding: 10px 12px; font-size: 13px; color: #cbd5e1; background: rgba(15,23,42,0.4); }
    .tx-table tr td:first-child { border-radius: 8px 0 0 8px; }
    .tx-table tr td:last-child { border-radius: 0 8px 8px 0; }
    
    .streamlit-expanderHeader, .streamlit-expanderHeader p,
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {
        white-space: nowrap !important; overflow: hidden !important;
        text-overflow: ellipsis !important; font-size: 13px !important;
    }
    [data-testid="stExpander"] summary p { margin: 0 !important; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h3 { color: #94a3b8; }
    
    @media (max-width: 768px) {
        .kpi-value { font-size: 28px; }
        .kpi-label { font-size: 10px; letter-spacing: 1.5px; }
        .block-container { padding: 0.5rem; }
    }
</style>
""", unsafe_allow_html=True)


# ========================
# SIDEBAR: DATA SOURCE
# ========================
with st.sidebar:
    st.markdown("### ⚙️ Data Source")
    
    data_mode = st.radio(
        "Choose how to load data:",
        ["🎲 Demo Data", "📄 Upload CSV", "🔗 Google Sheets"],
        index=0,
        help="Demo mode shows realistic sample data. CSV mode lets you upload your own bank export. Google Sheets connects to Finta or similar auto-sync services."
    )
    
    st.markdown("---")
    
    # Settings that apply to all modes
    st.markdown("### 🏠 Dashboard Settings")
    family_name = st.text_input("Family / Dashboard Name", value=DEFAULT_FAMILY_NAME)
    monthly_income = st.number_input("Monthly Income ($)", value=DEFAULT_MONTHLY_INCOME, step=100, min_value=0)
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px;color:#475569;line-height:1.6;">
        <strong>📄 CSV Format</strong><br>
        Upload any bank/card export with columns for date, amount, and description.
        Supports Mint, YNAB, Chase, Amex, and most bank CSV exports.<br><br>
        <strong>🔗 Google Sheets</strong><br>
        Connect to Finta or any Google Sheet with transaction data.
        Requires a service account JSON key.
    </div>
    """, unsafe_allow_html=True)

# ========================
# LOAD DATA BASED ON MODE
# ========================
transactions = None
is_demo = False
is_csv = False
badge_class = "demo-badge"
badge_text = "⚡ Demo Mode - Sample Data"

if data_mode == "🎲 Demo Data":
    transactions = generate_months_of_data(6)
    is_demo = True
    badge_class = "demo-badge"
    badge_text = "⚡ Demo Mode - Sample Data"

elif data_mode == "📄 Upload CSV":
    is_csv = True
    badge_class = "csv-badge"
    badge_text = "📄 Your Data - CSV Upload"
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload transaction CSV",
        type=['csv'],
        help="Export transactions from your bank, credit card, Mint, YNAB, etc."
    )
    
    if uploaded_file:
        transactions = parse_csv_transactions(uploaded_file)
        if transactions is not None:
            st.sidebar.success(f"✅ Loaded {len(transactions)} transactions")
    else:
        st.sidebar.info("👆 Upload a CSV to get started")
        # Show sample format
        with st.sidebar.expander("📋 Sample CSV format"):
            st.code("""Date,Amount,Description,Category
2025-03-01,-45.23,H-E-B Grocery,Groceries
2025-03-02,-12.50,Chipotle,Restaurants
2025-03-03,-35.00,Shell Gas,Gas & Auto
2025-03-05,-89.99,Amazon,Shopping""", language="csv")

elif data_mode == "🔗 Google Sheets":
    badge_class = "live-badge"
    badge_text = "🔗 Live Data - Google Sheets"
    
    sheet_id = st.sidebar.text_input(
        "Google Sheet ID",
        help="The long ID from the sheet URL: docs.google.com/spreadsheets/d/{THIS_PART}/edit"
    )
    
    creds_method = st.sidebar.radio(
        "Credentials source",
        ["Streamlit Secrets", "Upload JSON key"],
        help="Use Streamlit Secrets for deployed apps, or upload a service account JSON key for local testing."
    )
    
    credentials_json = None
    
    if creds_method == "Upload JSON key":
        creds_file = st.sidebar.file_uploader("Service account JSON", type=['json'])
        if creds_file:
            credentials_json = creds_file.read().decode('utf-8')
    elif creds_method == "Streamlit Secrets":
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            credentials_json = json.dumps(dict(st.secrets["gcp_service_account"]))
        else:
            st.sidebar.warning("No secrets configured. Add `gcp_service_account` to `.streamlit/secrets.toml`")
    
    if sheet_id and credentials_json:
        with st.spinner("Loading from Google Sheets..."):
            sheets_data = load_google_sheets_data(sheet_id, credentials_json)
            if sheets_data and 'Transactions' in sheets_data:
                transactions = sheets_data['Transactions']
                st.sidebar.success(f"✅ Connected! {len(transactions)} rows loaded")
    elif sheet_id:
        st.sidebar.info("👆 Provide credentials to connect")
    else:
        st.sidebar.info("👆 Enter your Google Sheet ID")


# ========================
# CONFIG
# ========================
FAMILY_NAME = family_name
MONTHLY_INCOME = monthly_income
FIXED_EXPENSES = DEFAULT_FIXED_EXPENSES
DUE_DATES = DEFAULT_DUE_DATES

# Account balances (demo defaults; would come from Sheets in live mode)
CREDIT_CARD_BALANCE = DEFAULT_CREDIT_CARD_BALANCE
CREDIT_CARD_LIMIT = DEFAULT_CREDIT_CARD_LIMIT
HELOC_BALANCE = DEFAULT_HELOC_BALANCE
HELOC_LIMIT = DEFAULT_HELOC_LIMIT
SAVINGS_BALANCE = DEFAULT_SAVINGS_BALANCE
AUTO_LOAN_BALANCE = DEFAULT_AUTO_LOAN_BALANCE
INVESTMENT_BALANCE = DEFAULT_INVESTMENT_BALANCE


# ========================
# MAIN DASHBOARD
# ========================
def main():
    st.markdown(f'<div class="{badge_class}"><span>{badge_text}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dashboard-title">💰 {FAMILY_NAME} Family Budget</div>', unsafe_allow_html=True)
    
    if transactions is None or transactions.empty:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#64748b;">
            <div style="font-size:48px;margin-bottom:16px;">📊</div>
            <div style="font-size:18px;font-weight:600;color:#94a3b8;margin-bottom:8px;">No Data Loaded</div>
            <div style="font-size:14px;">Use the sidebar to select a data source: demo data, CSV upload, or Google Sheets.</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Period selector
    available_months = get_available_months(transactions)
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
                                     format_func=lambda i: period_options[i], index=0,
                                     label_visibility="collapsed")
    
    selected_period = period_keys[selected_idx]
    is_ytd = selected_period == 'ytd'
    
    source_label = "Sample Data" if is_demo else ("CSV Upload" if is_csv else "Google Sheets")
    if is_ytd:
        subtitle_text = f"{now.year} Year to Date &nbsp;•&nbsp; {source_label}"
    elif selected_period == 'current':
        subtitle_text = f"{current_label} &nbsp;•&nbsp; {source_label}"
    else:
        y, mo = int(selected_period[:4]), int(selected_period[5:7])
        from calendar import month_name
        subtitle_text = f"{month_name[mo]} {y} &nbsp;•&nbsp; {source_label}"
    
    st.markdown(f'<div class="dashboard-subtitle">{subtitle_text}</div>', unsafe_allow_html=True)
    
    monthly_tx, monthly_total = get_filtered_spending(transactions, selected_period)
    
    months_elapsed = now.month if is_ytd else 1
    income_for_period = MONTHLY_INCOME * months_elapsed
    
    total_fixed_monthly = sum(sum(cat.values()) for cat in FIXED_EXPENSES.values())
    total_fixed = total_fixed_monthly * months_elapsed
    spendable = income_for_period - total_fixed - monthly_total
    
    budget_used_pct = ((total_fixed + monthly_total) / income_for_period * 100) if income_for_period > 0 else 0
    
    # ========================
    # ROW 1: BIG KPIs
    # ========================
    c1, c2, c3 = st.columns(3)
    with c1:
        color = "green" if spendable > 200 else ("yellow" if spendable > 0 else "red")
        render_kpi("Spendable Left", spendable, color,
                   sub=f"${income_for_period:,.0f} income - ${total_fixed:,.0f} fixed - ${monthly_total:,.0f} spent")
    with c2:
        color = "red" if CREDIT_CARD_BALANCE > CREDIT_CARD_LIMIT * 0.7 else ("yellow" if CREDIT_CARD_BALANCE > CREDIT_CARD_LIMIT * 0.4 else "green")
        render_kpi("Credit Card", CREDIT_CARD_BALANCE, color,
                   sub=f"{(CREDIT_CARD_BALANCE/CREDIT_CARD_LIMIT*100):.0f}% of ${CREDIT_CARD_LIMIT:,.0f} limit")
    with c3:
        render_kpi("Cash + Savings", SAVINGS_BALANCE, "blue", sub="Savings Account")
    
    # ========================
    # ROW 2: SECONDARY KPIs
    # ========================
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Income", income_for_period, "teal",
                   sub=f"Combined household{' (' + str(months_elapsed) + ' months)' if is_ytd else ''}")
    with c2:
        render_kpi("Fixed Bills", total_fixed, "orange",
                   sub=f"{sum(len(v) for v in FIXED_EXPENSES.values())} recurring items{' x ' + str(months_elapsed) + ' months' if is_ytd else ''}")
    with c3:
        render_kpi("Spent (Variable)", monthly_total, "purple" if monthly_total > 0 else "green",
                   sub=f"{len(monthly_tx)} transactions")
    with c4:
        render_kpi("Investments", INVESTMENT_BALANCE, "green", sub="Retirement & Brokerage")
    
    # ========================
    # DONUT + GAUGE
    # ========================
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
    
    # ========================
    # CATEGORY DRILL-DOWN
    # ========================
    if not monthly_tx.empty and 'Category Group' in monthly_tx.columns:
        by_group = monthly_tx.groupby('Category Group')['spend'].sum().sort_values(ascending=False)
        cat_options = ['Select a category to drill down...'] + [
            f"{cat} (${amt:,.2f})" for cat, amt in by_group.items() if amt > 0
        ]
        cat_keys = [None] + [cat for cat, amt in by_group.items() if amt > 0]
        
        if "drill_gen" not in st.session_state:
            st.session_state["drill_gen"] = 0
        
        drill_col1, drill_col2, drill_col3 = st.columns([1, 2, 1])
        with drill_col2:
            selected_cat_idx = st.selectbox("Drill down", range(len(cat_options)),
                                             format_func=lambda i: cat_options[i], index=0,
                                             label_visibility="collapsed",
                                             key=f"cat_drill_{st.session_state['drill_gen']}")
        
        selected_category = cat_keys[selected_cat_idx] if selected_cat_idx > 0 else None
        
        if selected_category:
            cat_tx = monthly_tx[monthly_tx['Category Group'] == selected_category].copy()
            cat_total = cat_tx['spend'].sum()
            cat_count = len(cat_tx)
            
            st.markdown(f"""
            <div style="background:linear-gradient(145deg, rgba(30,41,59,0.6) 0%, rgba(15,23,42,0.8) 100%);
                        border-radius:16px;padding:20px 24px;margin:8px 0 16px 0;
                        border:1px solid rgba(96,165,250,0.2);">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                    <span style="font-size:16px;font-weight:700;color:#60a5fa;">🔍 {selected_category}</span>
                    <span style="font-size:14px;color:#94a3b8;">{cat_count} transactions &nbsp;•&nbsp; ${cat_total:,.2f}</span>
                </div>
            """, unsafe_allow_html=True)
            
            if 'Category Name' in cat_tx.columns:
                by_sub = cat_tx.groupby('Category Name')['spend'].agg(['sum', 'count']).reset_index()
                by_sub = by_sub.sort_values('sum', ascending=False)
                for _, sub in by_sub.iterrows():
                    pct = (sub['sum'] / cat_total * 100) if cat_total > 0 else 0
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;font-size:13px;">
                        <span style="color:#cbd5e1;">{sub['Category Name']} <span style="color:#475569;">({int(sub['count'])})</span></span>
                        <span style="color:#e2e8f0;font-weight:600;">${sub['sum']:,.2f} <span style="color:#475569;font-weight:400;">({pct:.0f}%)</span></span>
                    </div>
                    <div style="background:rgba(255,255,255,0.06);border-radius:3px;height:4px;margin-bottom:4px;">
                        <div style="width:{max(pct,2)}%;height:100%;background:#60a5fa;border-radius:3px;"></div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('<div style="margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:11px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Transactions</div>', unsafe_allow_html=True)
            
            for _, tx in cat_tx.sort_values('parsed_date', ascending=False).iterrows():
                dt = tx['parsed_date'].strftime('%b %d')
                merchant = str(tx.get('Merchant', ''))[:35]
                amt = tx['spend']
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;padding:4px 0;font-size:13px;">
                    <span style="color:#64748b;min-width:50px;">{dt}</span>
                    <span style="color:#94a3b8;flex:1;padding:0 12px;">{merchant}</span>
                    <span style="color:#fb7185;font-weight:600;">${amt:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            if st.button("✕ Close Details", key="close_drill"):
                st.session_state["drill_gen"] += 1
                st.rerun()
    
    # ========================
    # FIXED EXPENSE BREAKDOWN
    # ========================
    st.markdown('<div style="font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1.5px;margin:12px 0 8px 0;">Fixed Expenses</div>', unsafe_allow_html=True)
    
    exp_cols = st.columns(len(FIXED_EXPENSES))
    for i, (cat_name, items) in enumerate(FIXED_EXPENSES.items()):
        cat_total = sum(items.values())
        with exp_cols[i]:
            with st.expander(f"**{cat_name}** — ${cat_total:,.0f}/mo"):
                for item_name, amount in sorted(items.items(), key=lambda x: -x[1]):
                    pct_of_cat = (amount / cat_total * 100) if cat_total > 0 else 0
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;font-size:13px;">
                        <span style="color:#94a3b8;">{item_name}</span>
                        <span style="color:#e2e8f0;font-weight:600;">${amount:,.0f}</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.06);border-radius:3px;height:4px;margin-bottom:6px;">
                        <div style="width:{max(pct_of_cat,2)}%;height:100%;background:#60a5fa;border-radius:3px;"></div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # ========================
    # DEBT PROGRESS
    # ========================
    st.markdown('<div class="section-header">💳 Credit & Debt</div>', unsafe_allow_html=True)
    render_progress("Credit Card", CREDIT_CARD_BALANCE, CREDIT_CARD_LIMIT)
    render_progress("HELOC (Credit Union)", HELOC_BALANCE, HELOC_LIMIT)
    render_progress("Auto Loan", AUTO_LOAN_BALANCE, 28000)
    
    # ========================
    # DUE DATES
    # ========================
    st.markdown('<div class="section-header">📅 Upcoming Due Dates</div>', unsafe_allow_html=True)
    
    today = datetime.now().day
    dues_sorted = sorted(DUE_DATES.items(), key=lambda x: x[1])
    col1, col2 = st.columns(2)
    mid = len(dues_sorted) // 2
    
    for i, (name, day) in enumerate(dues_sorted):
        col = col1 if i <= mid else col2
        if day < today:
            status, color = "✅ Paid", "#34d399"
        elif day - today <= 5:
            status, color = "⚡ Due Soon", "#fbbf24"
        else:
            status, color = f"In {day - today} days", "#475569"
        
        with col:
            st.markdown(f"""
            <div class="due-row">
                <span class="due-name">{name}</span>
                <span class="due-date" style="color:{color}">{day}th — {status}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # ========================
    # RECENT TRANSACTIONS
    # ========================
    st.markdown('<div class="section-header">🧾 Recent Transactions</div>', unsafe_allow_html=True)
    
    if not monthly_tx.empty:
        PAGE_SIZE = 15
        all_tx = monthly_tx.sort_values('parsed_date', ascending=False)
        total_tx = len(all_tx)
        
        if "tx_show_count" not in st.session_state:
            st.session_state["tx_show_count"] = PAGE_SIZE
        
        show_count = min(st.session_state["tx_show_count"], total_tx)
        visible_tx = all_tx.head(show_count)
        
        table_html = '<table class="tx-table"><thead><tr><th>Date</th><th>Merchant</th><th>Category</th><th>Amount</th></tr></thead><tbody>'
        for _, row in visible_tx.iterrows():
            dt = row['parsed_date'].strftime('%b %d')
            merchant = str(row.get('Merchant', ''))[:30]
            cat = str(row.get('Category Group', ''))
            amt = row['spend']
            table_html += f'<tr><td>{dt}</td><td>{merchant}</td><td>{cat}</td>'
            table_html += f'<td style="color:#fb7185;font-weight:600;">-${amt:,.2f}</td></tr>'
        table_html += '</tbody></table>'
        st.markdown(table_html, unsafe_allow_html=True)
        
        st.markdown(f'<p style="text-align:center;color:#475569;font-size:12px;margin-top:8px;">Showing {show_count} of {total_tx} transactions</p>', unsafe_allow_html=True)
        
        if show_count < total_tx:
            if st.button(f"Show More ({min(PAGE_SIZE, total_tx - show_count)} more)", key="show_more_tx"):
                st.session_state["tx_show_count"] = show_count + PAGE_SIZE
                st.rerun()
        if show_count > PAGE_SIZE:
            if st.button("Show Less", key="show_less_tx"):
                st.session_state["tx_show_count"] = PAGE_SIZE
                st.rerun()
    else:
        st.markdown('<p style="color:#475569;text-align:center;">No transactions for this period.</p>', unsafe_allow_html=True)
    
    # ========================
    # FOOTER
    # ========================
    st.markdown(f"""
    <div style="text-align:center;margin-top:48px;padding:20px;color:#1e293b;font-size:11px;letter-spacing:1px;">
        FAMILY BUDGET DASHBOARD &nbsp;•&nbsp; Built with Streamlit + Plotly
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
