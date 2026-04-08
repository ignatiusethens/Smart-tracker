import streamlit as st
import datetime
import plotly.express as px
import pandas as pd
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

    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background-color: #0f172a; /* Slate 900 */
        color: #f8fafc;
    }
    
    h1, h2, h3 {
        color: #e2e8f0;
    }

    [data-testid="stSidebar"] {
        background-color: #1e293b; /* Slate 800 */
        border-right: 1px solid #334155;
    }

    div[data-testid="stMetricValue"] {
        color: #38bdf8; /* Light blue */
        font-weight: 800;
        font-size: 2.5rem;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 600;
    }

    .css-1r6slb0, .css-1y4p8pa { /* Metric container styling */
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .css-1r6slb0:hover, .css-1y4p8pa:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
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
                    elif len(r_password) < 4:
                        st.error("Password must be at least 4 characters long.")
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

# --- SIDEBAR: INPUT FORM ---
with st.sidebar:
    st.title(f"🎓 {st.session_state['username']}'s Wallet")
    
    with st.form("expense_form", clear_on_submit=True):
        amount = st.number_input("Amount ($)", min_value=0.01, format="%f")
        date_input = st.date_input("Date", value=datetime.date.today())
        description = st.text_input("Description", placeholder="e.g. Coffee at Campus")
        category = st.selectbox("Category", [
            "Food & Dining", "Transport", "Academics", 
            "Entertainment", "Rent", "Utilities", "Other"
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
            db.add_expense(new_expense)
            st.success(f"Added {category} expense of ${amount:.2f}")
            st.rerun()
            
    st.divider()
    st.subheader("💰 Budget Settings")
    if 'monthly_budget' not in st.session_state:
        st.session_state['monthly_budget'] = 1000.0
        
    budget_input = st.number_input("Monthly Budget ($)", value=st.session_state['monthly_budget'], step=50.0)
    if budget_input != st.session_state['monthly_budget']:
        st.session_state['monthly_budget'] = budget_input
        st.rerun()
        
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state['user_id'] = None
        st.session_state['username'] = None
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("Smart Student Expense Tracker")
st.markdown("Monitor your personal finances and prevent overspending. 🚀")

monthly_budget = st.session_state['monthly_budget']
total_spent = analyzer.get_total_expenses()
budget_used_pct = analyzer.get_budget_status_percentage(monthly_budget)

# Budget Alerts
if budget_used_pct >= 100:
    st.error(f"🚨 **Over Budget!** You have spent ${total_spent:.2f}, exceeding your budget of ${monthly_budget:.2f}.")
elif budget_used_pct >= 80:
    st.warning(f"⚠️ **Warning!** You have spent {budget_used_pct:.1f}% of your budget. Slow down on spending!")
elif total_spent > 0:
    st.success(f"✅ **On Track!** You've spent {budget_used_pct:.1f}% of your budget. Keep it up!")

# KPIs / Metrics
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Expenses", value=f"${total_spent:,.2f}")
with col2:
    remaining = max(0, monthly_budget - total_spent)
    st.metric(label="Remaining Budget", value=f"${remaining:,.2f}")
with col3:
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
            yaxis_title="Amount ($)"
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
            "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f")
        }
    )
else:
    st.info("Your expense log is empty.")
