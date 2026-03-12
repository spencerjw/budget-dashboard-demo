import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from streamlit_local_storage import LocalStorage
import pandas as pd
import random
import json
import time
import io

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

DEMO_DUE_DATES = {
    'Rent / Mortgage': 1, 'Student Loans': 8, 'Car Payment': 15,
    'Credit Card': 22, 'Car Insurance': 28,
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
        fig.add_annotation(text="No transactions yet", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color='#64748b'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(l=0, r=0, t=0, b=0))
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
# PAGE CONFIG + CSS
# ========================
st.set_page_config(page_title="Family Budget Dashboard", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

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
    [data-testid="stToast"] { left: 1rem !important; right: auto !important; background: rgba(30,41,59,0.95) !important; border: 1px solid rgba(52,211,153,0.3) !important; border-radius: 12px !important; backdrop-filter: blur(10px) !important; }
    [data-testid="stToast"] div { color: #e2e8f0 !important; }
    @media (max-width: 768px) { .kpi-value { font-size: 28px; } .kpi-label { font-size: 10px; letter-spacing: 1.5px; } .block-container { padding: 0.5rem; } }
</style>
""", unsafe_allow_html=True)


# ========================
# INIT
# ========================
localS = get_local_storage()
init_session_config(localS)


# ========================
# SIDEBAR
# ========================
with st.sidebar:
    st.markdown("## ⚙️ Setup")
    
    # === STATUS MESSAGES ===
    if st.session_state.get('reset_success'):
        st.session_state['reset_success'] = False
        st.session_state['show_reset_banner'] = True
    
    # === MODE ===
    data_mode = st.radio("Mode", ["🎲 Demo", "💰 My Budget"], index=0)
    is_my_budget = data_mode == "💰 My Budget"
    
    if not is_my_budget:
        st.caption("You're viewing a fake family's budget with sample transactions. Switch to **My Budget** to enter your own.")
    
    # === CSV UPLOAD (top of sidebar in My Budget mode) ===
    if is_my_budget:
        st.markdown("---")
        st.markdown("### 📄 Upload Transactions")
        st.caption("Export CSVs from your bank(s) and drop them here. Multiple files OK. [How do I get a CSV?](https://github.com/spencerjw/budget-dashboard-demo/blob/main/GETTING-STARTED.md#step-6-upload-your-transactions-optional-but-recommended)")
        uploaded_files = st.file_uploader("CSV files", type=['csv'], key="csv_upload",
            accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file{'s' if len(uploaded_files) > 1 else ''} loaded")
    
    st.markdown("---")
    
    # === BASIC INFO ===
    cfg = st.session_state['config']
    
    if is_my_budget:
        st.markdown("### 🏠 My Info")
        cfg['family_name'] = st.text_input("Dashboard Name", value=cfg['family_name'])
        cfg['monthly_income'] = st.number_input("Monthly Take-Home Pay ($)", value=cfg['monthly_income'],
            step=100, min_value=0, help="After taxes. The amount that hits your bank account.")
    
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
                        delete = st.button("🗑️", key=f"exp_del_{cat_name}_{item_name}", help="Remove this bill")
                    
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
                a_name = st.text_input("Account Name", value=acct['name'], key=f"cash_name_{i}",
                    help="Whatever you call this account. e.g. 'Chase Checking' or 'Ally Savings'")
                a_type = st.selectbox("Account Type", ['checking', 'savings', 'investment'],
                    index=['checking', 'savings', 'investment'].index(acct['type']),
                    format_func=lambda x: {'checking': '🔵 Checking', 'savings': '🟢 Savings', 'investment': '📈 Investment / Retirement'}[x],
                    key=f"cash_type_{i}")
                a_balance = st.number_input("Current Balance ($)", value=acct['balance'], step=100, key=f"cash_bal_{i}",
                    help="What your account shows right now.")
                
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
                a_name = st.text_input("Account Name", value=acct['name'], key=f"debt_name_{i}",
                    help="e.g. 'Chase Visa', 'Car Loan', 'Student Loans'")
                a_type = st.selectbox("Account Type", ['credit', 'loan'],
                    index=['credit', 'loan'].index(acct['type']),
                    format_func=lambda x: {'credit': '💳 Credit Card', 'loan': '🏦 Loan (car, student, personal, etc.)'}[x],
                    key=f"debt_type_{i}")
                a_balance = st.number_input("Current Balance Owed ($)", value=acct['balance'], step=100, min_value=0, key=f"debt_bal_{i}",
                    help="What you currently owe.")
                
                if a_type == 'credit':
                    a_limit = st.number_input("Credit Limit ($)", value=acct['limit'], step=100, min_value=0, key=f"debt_lim_{i}",
                        help="The maximum you're allowed to charge.")
                else:
                    a_limit = st.number_input("Original Loan Amount ($)", value=acct['limit'], step=100, min_value=0, key=f"debt_lim_{i}",
                        help="How much you originally borrowed.")
                
                a_due_day = st.number_input("Payment Due Date (day of month)", value=acct.get('due_day', 0),
                    min_value=0, max_value=31, step=1, key=f"debt_due_{i}",
                    help="Day of the month payment is due. 0 = no due date.")
                
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
            nd_due = st.number_input("Payment Due Date (day of month)", value=0, min_value=0, max_value=31, step=1, key="new_debt_due",
                help="0 = no due date.")
            if st.button("Add Account", key="add_debt") and nd_name.strip():
                updated_accounts.append({'name': nd_name.strip(), 'type': nd_type, 'balance': nd_balance, 'limit': nd_limit, 'due_day': nd_due})
                st.rerun()
        
        cfg['accounts'] = updated_accounts
        
        st.markdown("---")
        
        # === DUE DATES ===
        st.markdown("### 📅 Bill Due Dates")
        st.caption("Add bills that aren't credit cards or loans (those due dates are set above). Enter the day of the month each is due -- e.g. rent on the 1st, electric on the 15th. Shows up in the Upcoming Bills section of your dashboard.")
        
        updated_dues = {}
        for bill_name, day in list(cfg['due_dates'].items()):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"<span style='color:#94a3b8;font-size:13px;'>{bill_name}</span>", unsafe_allow_html=True)
            with c2:
                new_day = st.number_input("Day", value=day, min_value=1, max_value=31, key=f"due_{bill_name}", label_visibility="collapsed")
            with c3:
                del_due = st.button("🗑️", key=f"due_del_{bill_name}")
            if not del_due:
                updated_dues[bill_name] = new_day
        
        st.caption("Add a due date:")
        nc1, nc2 = st.columns([3, 1])
        with nc1:
            new_due_name = st.text_input("Bill name", key="new_due_name", placeholder="e.g. Rent", label_visibility="collapsed")
        with nc2:
            new_due_day = st.number_input("Day", value=1, min_value=1, max_value=31, key="new_due_day", label_visibility="collapsed")
        
        if new_due_name.strip():
            updated_dues[new_due_name.strip()] = new_due_day
        
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
            mime="application/json", use_container_width=True,
            help="Save a backup file you can load on another device or your own dashboard.")
        
        uploaded_config = st.file_uploader("⬆️ Load Settings File", type=['json'],
            help="Upload a previously saved budget-settings.json file.", label_visibility="collapsed")
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
# LOAD DATA
# ========================
cfg = st.session_state['config']
transactions = None
is_demo = False

if data_mode == "🎲 Demo":
    transactions = generate_months_of_data(6)
    is_demo = True
    FIXED_EXPENSES = DEMO_FIXED_EXPENSES
    ACCOUNTS = DEMO_ACCOUNTS
    DUE_DATES = DEMO_DUE_DATES
    FAMILY_NAME = "Anderson Family Budget"
    MONTHLY_INCOME = 9200
    badge_class = "demo-badge"
    badge_text = "⚡ Demo Mode — Sample Data"
else:
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
    badge_text = "💰 My Budget"
    
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
# MAIN DASHBOARD
# ========================
def main():
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
        dues_sorted = sorted(DUE_DATES.items(), key=lambda x: x[1])
        col1, col2 = st.columns(2)
        mid = len(dues_sorted) // 2
        for i, (name, day) in enumerate(dues_sorted):
            col = col1 if i <= mid else col2
            if day < today: status, color = "✅ Paid", "#34d399"
            elif day - today <= 5: status, color = "⚡ Due Soon", "#fbbf24"
            else: status, color = f"In {day - today} days", "#475569"
            with col:
                st.markdown(f'<div class="due-row"><span class="due-name">{name}</span><span class="due-date" style="color:{color}">{day}th — {status}</span></div>', unsafe_allow_html=True)
    
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
    st.markdown(f'<div style="text-align:center;margin-top:48px;padding:20px;color:#1e293b;font-size:11px;letter-spacing:1px;">FAMILY BUDGET DASHBOARD &nbsp;•&nbsp; Built with Streamlit + Plotly</div>', unsafe_allow_html=True)
    



if __name__ == '__main__':
    main()
