import streamlit as st
import datetime
import plotly.express as px
import pandas as pd
import re
from models import Expense, BudgetAnalyzer
from database import DatabaseManager

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Smart Student Expense Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM LOOK ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Global Font & Background */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }

    /* Hide Streamlit Native Branding */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.5) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Input Fields (Widgets) Styling for Premium Look */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div, 
    div[data-baseweb="number-input"] > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
        color: white;
    }
    div[data-baseweb="input"] > div:focus-within, 
    div[data-baseweb="select"] > div:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
    }

    /* Button Styling */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #38bdf8 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        padding: 10px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39);
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        color: white;
    }
    div.stButton > button:first-child:active {
        transform: translateY(0);
    }

    /* Metric Cards Glassmorphism */
    div[data-testid="stMetricValue"] {
        color: #38bdf8;
        font-weight: 800;
        font-size: 2.8rem;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .css-1r6slb0, .css-1y4p8pa, div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .css-1r6slb0:hover, .css-1y4p8pa:hover, div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Mobile Responsiveness & Container Spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px;
    }
    
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        /* Make fonts slightly smaller on mobile */
        div[data-testid="stMetricValue"] {
            font-size: 2.2rem;
        }
        h1 {
            font-size: 1.8rem !important;
        }
    }

    /* Mount Animations (Fill Up / Slide Up) */
    @keyframes fillUpFade {
        0% { opacity: 0; transform: translateY(60px) scale(0.95); }
        100% { opacity: 1; transform: translateY(0) scale(1.0); }
    }
    @keyframes barGrow {
        0% { transform: scaleY(0); transform-origin: bottom; opacity: 0; }
        100% { transform: scaleY(1); transform-origin: bottom; opacity: 1; }
    }

    /* Target the container wrapping charts to fade up */
    div[data-testid="stPlotlyChart"] {
        animation: fillUpFade 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    
    /* Target the metrics to slide in sequentially */
    div[data-testid="metric-container"] {
        animation: fillUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    
    /* Target the dataframes */
    div[data-testid="stDataFrame"] {
        animation: fillUpFade 1.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- INITIALIZATION ---
# Safe caching is hard with db engine, so we'll init each run. SQLAlchemy handles pooling.
db = DatabaseManager()

# --- AUTH LOGIC ---
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None

if st.session_state['user_id'] is None:
    # --- LOGIN & REGISTER PAGE ---
    st.title("🎓 Smart Tracking Portal")
    st.markdown("Please log in or register below to securely access your private dashboard.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                l_username = st.text_input("Username")
                l_password = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    user_id = db.verify_user(l_username, l_password)
                    if user_id:
                        st.session_state['user_id'] = user_id
                        st.session_state['username'] = l_username
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                        
        with tab2:
            with st.form("register_form"):
                r_username = st.text_input("Choose Username")
                r_password = st.text_input("Create Password", type="password")
                r_confirm = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Register", use_container_width=True):
                    if r_password != r_confirm:
                        st.error("Passwords do not match!")
                    elif len(r_password) < 8:
                        st.error("Security Risk: Password must be at least 8 characters long!")
                    elif not re.search(r"[A-Z]", r_password):
                        st.error("Security Risk: Password must contain at least one uppercase letter!")
                    elif not re.search(r"[a-z]", r_password):
                        st.error("Security Risk: Password must contain at least one lowercase letter!")
                    elif not re.search(r"[0-9]", r_password):
                        st.error("Security Risk: Password must contain at least one numeric digit!")
                    elif not r_username:
                        st.error("Username cannot be empty")
                    else:
                        success = db.create_user(r_username, r_password)
                        if success:
                            st.success("Account created! Please switch to the Login tab.")
                        else:
                            st.error("Username already exists. Please choose another.")
    
    # Stop execution here if not logged in
    st.stop()


# --- DASHBOARD LOGIC (When Logged In) ---
user_id = st.session_state['user_id']

def load_data(uid):
    expenses_list = db.get_all_expenses(uid)
    analyzer = BudgetAnalyzer(expenses_list)
    return expenses_list, analyzer

expenses_list, analyzer = load_data(user_id)

# --- EXPENSE CONTROLS ---
with st.expander("➕ Record New Expense", expanded=True):
    with st.form("expense_form", clear_on_submit=True):
        amt_val = st.session_state.get('parsed_amount', 1.0)
        desc_val = st.session_state.get('parsed_vendor', "")
        
        amount = st.number_input("Amount (Ksh)", min_value=1.0, value=amt_val, format="%f")
        date_input = st.date_input("Date", value=datetime.date.today())
        description = st.text_input("Description", value=desc_val, placeholder="e.g. Coffee at Campus")
        category = st.selectbox("Category", [
            "Food & Dining", "Transport", "Academics", 
            "Entertainment", "Rent", "Utilities", 
            "Photography & Tech Gear", "Logistics & Business", "Other"
        ])
        
        submitted = st.form_submit_button("Add Expense", use_container_width=True)
        if submitted:
            new_expense = Expense(
                user_id=user_id,
                amount=amount,
                date=date_input.strftime("%Y-%m-%d"),
                description=description,
                category=category
            )
            if 'parsed_amount' in st.session_state:
                del st.session_state['parsed_amount']
            if 'parsed_vendor' in st.session_state:
                del st.session_state['parsed_vendor']
            db.add_expense(new_expense)
            st.success(f"Added {category} expense of Ksh {amount:,.2f}")
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📱 M-Pesa Auto-Fill")
st.markdown("Paste your Safaricom message here to auto-fill the manual form above.")
with st.form("mpesa_form", clear_on_submit=True):
    col_sms, col_btn = st.columns([3, 1])
    with col_sms:
        sms_text = st.text_input("Paste SMS", placeholder="e.g. Ksh150.00 paid to VENDOR X on 10/10...", label_visibility="collapsed")
    with col_btn:
        submitted = st.form_submit_button("Parse SMS", use_container_width=True)
        
    if submitted:
        amount_match = re.search(r'Ksh\s*([\d,]+\.?\d*)', sms_text, re.IGNORECASE)
        vendor_match = re.search(r'(?:paid to|sent to)\s*(.*?)\s*on', sms_text, re.IGNORECASE)
        if amount_match:
            st.session_state['parsed_amount'] = float(amount_match.group(1).replace(',', ''))
        if vendor_match:
            st.session_state['parsed_vendor'] = vendor_match.group(1).strip()
        st.rerun()

dash_tab, funds_tab, settings_tab = st.tabs(["📊 Dashboard View", "💰 Sinking Funds & Goals", "⚙️ Account & Settings"])

with dash_tab:
    monthly_budget = st.session_state['monthly_budget']
    total_spent = analyzer.get_total_expenses()
    budget_used_pct = analyzer.get_budget_status_percentage(monthly_budget)
    projected_spend = analyzer.get_projected_spending()
    safe_daily = analyzer.get_safe_daily_limit(monthly_budget)

    # Budget Alerts
    if budget_used_pct >= 100:
        st.error(f"🚨 **Over Budget!** You have spent Ksh {total_spent:,.2f}, exceeding your budget of Ksh {monthly_budget:,.2f}.")
    elif budget_used_pct >= 80:
        st.warning(f"⚠️ **Warning!** You have spent {budget_used_pct:.1f}% of your budget. Slow down on spending!")
    elif projected_spend > monthly_budget:
        st.warning(f"🔥 **Burn Rate Alert:** At your current daily pace, you are projected to spend Ksh {projected_spend:,.2f} this month, crossing your limit!")
    elif total_spent > 0:
        st.success(f"✅ **On Track!** You've spent {budget_used_pct:.1f}% of your budget, and your burn rate is healthy.")

    # KPIs / Metrics
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, collimit, col4 = st.columns(5)
    with col1:
        st.metric(label="Total Expenses", value=f"Ksh {total_spent:,.0f}")
    with col2:
        remaining = max(0, monthly_budget - total_spent)
        st.metric(label="Remaining Budget", value=f"Ksh {remaining:,.0f}")
    with col3:
        st.metric(label="Burn Rate (Projected)", value=f"Ksh {projected_spend:,.0f}")
    with collimit:
        st.metric(label="Safe-to-Spend (Daily)", value=f"Ksh {safe_daily:,.0f}")
    with col4:
        st.metric(label="Budget Utilization", value=f"{budget_used_pct:.1f}%")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # Charts Section
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Spending by Category")
        df_cat = analyzer.get_expenses_by_category()
        if not df_cat.empty:
            fig_pie = px.pie(
                df_cat, 
                names='category', 
                values='amount', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses recorded yet. Add some to see the chart.")

    with col_chart2:
        st.subheader("Spending Over Time")
        df_time = analyzer.get_expenses_over_time()
        if not df_time.empty:
            fig_bar = px.bar(
                df_time, 
                x='date', 
                y='amount', 
                text_auto='.2s',
                color_discrete_sequence=['#38bdf8']
            )
            fig_bar.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                xaxis_title="Date",
                yaxis_title="Amount (Ksh)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No expenses recorded yet. Add some to see the chart.")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # Data Table Section
    st.subheader("Recent Expenses Data")
    if expenses_list:
        df_display = pd.DataFrame([vars(e) for e in expenses_list])
        # Drop internal data structure columns
        df_display = df_display.drop(columns=['id', 'user_id'])
        # Reorder columns
        df_display = df_display[['date', 'category', 'description', 'amount']]
        
        st.dataframe(
            df_display, 
            use_container_width=True,
            hide_index=True,
            column_config={
                "date": st.column_config.DateColumn("Date"),
                "category": st.column_config.TextColumn("Category"),
                "description": st.column_config.TextColumn("Description"),
                "amount": st.column_config.NumberColumn("Amount (Ksh)", format="Ksh %.2f")
            }
        )
    else:
        st.info("Your expense log is empty.")

with funds_tab:
    st.header("Sinking Funds & Goal Tracking")
    st.markdown("Set aside small amounts over time for large targets like Tuition or Camera Gear.")
    
    with st.expander("➕ Create New Goal", expanded=False):
        with st.form("new_goal_form", clear_on_submit=True):
            g_name = st.text_input("Goal Name", placeholder="e.g. Tuition, Camera Lens")
            g_target = st.number_input("Target Amount (Ksh)", min_value=1.0, step=500.0)
            if st.form_submit_button("Create Goal", use_container_width=True):
                from models import Goal
                db.add_goal(Goal(name=g_name, target_amount=g_target, current_amount=0.0, user_id=user_id))
                st.success("Goal created successfully!")
                st.rerun()
                
    st.markdown("<hr>", unsafe_allow_html=True)
    goals = db.get_all_goals(user_id)
    
    if not goals:
        st.info("No sinking funds yet! Start saving for your next target.")
    else:
        for g in goals:
            pct = min(1.0, g.current_amount / g.target_amount)
            st.markdown(f"#### {g.name}")
            st.markdown(f"**Ksh {g.current_amount:,.0f}** saved out of **Ksh {g.target_amount:,.0f}** ({pct*100:.1f}%)")
            st.progress(pct)
            
            with st.form(f"fund_{g.id}", clear_on_submit=True):
                col_amt, col_sub = st.columns([2, 1])
                with col_amt:
                    add_amt = st.number_input("Add Funds (Ksh)", min_value=1.0, step=100.0, key=f"amt_{g.id}", label_visibility="collapsed")
                with col_sub:
                    if st.form_submit_button("Contribute", use_container_width=True):
                        db.add_funds_to_goal(g.id, user_id, add_amt)
                        st.success(f"Added Ksh {add_amt} to {g.name}!")
                        st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

with settings_tab:
    st.header("⚙️ Budget Settings & Account")
    st.markdown("Manage your baseline tracking settings and active session.")
    
    with st.expander("Monthly Budget Control", expanded=True):
        if 'monthly_budget' not in st.session_state:
            st.session_state['monthly_budget'] = 15000.0
            
        budget_input = st.number_input("Monthly Budget (Ksh)", value=st.session_state['monthly_budget'], step=1000.0)
        if budget_input != st.session_state['monthly_budget']:
            st.session_state['monthly_budget'] = budget_input
            st.rerun()
            
    with st.expander("Authentication", expanded=True):
        st.markdown(f"**Logged in as:** `{st.session_state['username']}`")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state['user_id'] = None
            st.session_state['username'] = None
            st.rerun()
