import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re
from models import Expense, BudgetAnalyzer, Goal, InsightsEngine
from database import DatabaseManager

class ThemeManager:
    @staticmethod
    def apply_theme():
        st.set_page_config(
            page_title="Expense Tracker | Pro",
            page_icon="",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        custom_css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;800&display=swap');

            :root {
                --apple-bg: #F2F2F7;
                --apple-card: rgba(255, 255, 255, 0.65);
                --apple-text: #1C1C1E;
                --apple-text-muted: #8E8E93;
                --apple-placeholder: #86868B;
                --sf-blue: #007AFF;
                --sf-blue-dark: #0071E3;
                --sf-mint: #34C759;
                --sf-red: #FF3B30;
                --sf-yellow: #FFCC00;
                --apple-border: rgba(0,0,0,0.08);
            }

            html, body {
                background-color: var(--apple-bg);
            }
            [class*="css"] {
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
            }
            .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                background-color: transparent !important;
                color: var(--apple-text);
            }
            
            @keyframes mesh-float {
                0% { transform: translate(0px, 0px) scale(1); }
                33% { transform: translate(30px, -50px) scale(1.1); }
                66% { transform: translate(-20px, 20px) scale(0.9); }
                100% { transform: translate(0px, 0px) scale(1); }
            }

            .mesh-shape-1 {
                position: fixed; top: -10%; left: -10%; width: 50vw; height: 50vw;
                background: radial-gradient(circle, rgba(0, 122, 255, 0.25) 0%, rgba(255,255,255,0) 70%);
                border-radius: 50%; filter: blur(60px); z-index: -10;
                animation: mesh-float 20s infinite alternate; pointer-events: none;
            }
            .mesh-shape-2 {
                position: fixed; bottom: -10%; right: -10%; width: 60vw; height: 60vw;
                background: radial-gradient(circle, rgba(52, 199, 89, 0.20) 0%, rgba(255,255,255,0) 70%);
                border-radius: 50%; filter: blur(80px); z-index: -10;
                animation: mesh-float 25s infinite alternate-reverse; pointer-events: none;
            }
            .mesh-shape-3 {
                position: fixed; top: 20%; right: 20%; width: 40vw; height: 40vw;
                background: radial-gradient(circle, rgba(255, 204, 0, 0.18) 0%, rgba(255,255,255,0) 70%);
                border-radius: 50%; filter: blur(70px); z-index: -10;
                animation: mesh-float 22s infinite alternate; pointer-events: none;
            }
            
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}

            .hero-title {
                text-align: center;
                font-size: clamp(2.5rem, 6vw, 4rem);
                font-weight: 800;
                background: linear-gradient(180deg, #000000 0%, #8E8E93 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
                letter-spacing: -1px;
            }
            .hero-subtitle {
                text-align: center;
                color: var(--apple-text-muted);
                font-size: 1.2rem;
                font-weight: 400;
                margin-bottom: 3rem;
            }

            div[data-baseweb="input"] > div, 
            div[data-baseweb="select"] > div, 
            div[data-baseweb="number-input"] > div,
            textarea {
                background-color: rgba(29, 29, 31, 0.05) !important;
                border: 1px solid var(--apple-border) !important;
                border-radius: 12px !important;
                color: var(--apple-text) !important;
            }
            div[data-baseweb="input"] > div:focus-within, 
            div[data-baseweb="select"] > div:focus-within {
                border-color: var(--sf-blue) !important;
                box-shadow: 0 0 0 2px rgba(10, 132, 255, 0.2) !important;
            }

            div.stButton > button:first-child {
                background: rgba(255, 255, 255, 0.7);
                color: var(--apple-text);
                border: 1px solid var(--apple-border);
                border-radius: 14px;
                font-weight: 500;
                transition: all 0.3s ease;
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
            }
            div.stButton.primary-btn > button:first-child {
                background: var(--sf-blue);
                color: #FFFFFF;
                border: none;
                box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3);
                font-weight: 600;
            }
            div.stButton > button:first-child:hover {
                background: rgba(0, 0, 0, 0.1);
                transform: translateY(-1px);
            }
            div.stButton.primary-btn > button:first-child:hover {
                background: #0A84FF;
                color: #FFFFFF;
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
            }

            .stProgress > div > div > div > div {
                background-color: var(--sf-yellow) !important;
                box-shadow: 0 0 12px rgba(255, 214, 10, 0.5);
                border-radius: 10px;
            }
            
            button[data-baseweb="tab"] {
                border-radius: 8px !important;
                padding: 10px 20px !important;
            }
            
            .metric-card {
                background-color: var(--apple-card);
                border: 1px solid rgba(255,255,255,0.4);
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.05); /* Refined Apple Light Mode floating shadow */
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
            }
            .metric-title {
                color: var(--apple-text-muted);
                font-size: 0.95rem;
                font-weight: 600;
                margin-bottom: 8px;
            }
            .metric-value {
                color: var(--sf-blue-dark);
                font-size: 2.2rem;
                font-weight: 700;
            }
            .metric-safe { background: rgba(52,199,89,0.05); border-color: rgba(52,199,89,0.1); }
            .metric-safe .metric-value { color: var(--sf-mint); }
            
            .metric-warn { background: rgba(255,59,48,0.05); border-color: rgba(255,59,48,0.1); }
            .metric-warn .metric-value { color: var(--sf-red); }
            
            .metric-empty .metric-value { color: var(--apple-placeholder); }

            .empty-chart {
                background: var(--apple-card);
                border-radius: 16px;
                height: 250px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                border: 1px dashed var(--apple-placeholder);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
            }

        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)
        st.markdown('''
            <div class="mesh-shape-1"></div>
            <div class="mesh-shape-2"></div>
            <div class="mesh-shape-3"></div>
        ''', unsafe_allow_html=True)

class UIComponents:
    @staticmethod
    def render_hero(show_cta=True, show_subtitle=True):
        st.markdown(f'''
            <div style="padding: 4rem 0 2rem 0;">
                <div class="hero-title" style="font-size: clamp(2rem, 5vw, 3rem);">SMART STUDENT EXPENSE TRACKER</div>
                {'<div class="hero-subtitle" style="margin-top: 1rem; max-width: 700px; margin-left: auto; margin-right: auto; line-height: 1.5;">Stop wondering where your money went. Transform financial anxiety into complete confidence with a frictionless system designed to do the heavy lifting for you. Spend guilt-free, effortlessly build better habits, and finally feel in total control of your finances.</div>' if show_subtitle else ''}
            </div>
        ''', unsafe_allow_html=True)
        # Visual Anchor
        if show_cta:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.markdown('<div class="stButton primary-btn"><button><a href="#input-center" style="color:#FFFFFF; text-decoration:none;">Start Tracking</a></button></div>', unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)

    @staticmethod
    def render_empty_state(text="No data available"):
        st.markdown(f'''
            <div class="empty-chart">
                <div style="font-size: 2rem; color: #333;">✨</div>
                <div style="color: #666; font-weight: 500; margin-top: 10px;">{text}</div>
            </div>
        ''', unsafe_allow_html=True)

class ExpenseTrackerApp:
    def __init__(self):
        self.db = DatabaseManager()
        self.init_session_state()

    def init_session_state(self):
        if 'user_id' not in st.session_state:
            st.session_state['user_id'] = None
        if 'username' not in st.session_state:
            st.session_state['username'] = None
        if 'monthly_budget' not in st.session_state:
            st.session_state['monthly_budget'] = 15000.0

    def run(self):
        ThemeManager.apply_theme()
        
        if st.session_state['user_id'] is None:
            self.render_auth()
        else:
            self.render_main_app()

    def render_auth(self):
        UIComponents.render_hero(show_cta=False)
        st.markdown("<div style='text-align:center; color:#86868B; margin-bottom: 2rem;'>Secure Access Portal</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            tab1, tab2 = st.tabs(["Sign In", "Create Account"])
            
            with tab1:
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
                    sub = st.form_submit_button("Authenticate", use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    if sub:
                        user_id = self.db.verify_user(username, password)
                        if user_id:
                            st.session_state['user_id'] = user_id
                            st.session_state['username'] = username
                            st.rerun()
                        else:
                            st.error("Invalid credentials.")
                            
            with tab2:
                with st.form("register_form"):
                    new_user = st.text_input("Username")
                    new_pass = st.text_input("Password", type="password")
                    conf_pass = st.text_input("Confirm Password", type="password")
                    st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
                    sub_reg = st.form_submit_button("Register", use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    if sub_reg:
                        if new_pass == conf_pass and len(new_pass) >= 8:
                            if self.db.create_user(new_user, new_pass):
                                st.success("Account created. You can now sign in.")
                            else:
                                st.error("Username exists.")
                        else:
                            st.error("Invalid password criteria.")

    def render_main_app(self):
        user_id = st.session_state['user_id']
        expenses = self.db.get_all_expenses(user_id)
        analyzer = BudgetAnalyzer(expenses)
        
        # Hero
        UIComponents.render_hero(show_cta=True, show_subtitle=False)

        # Overview Tabs
        d_tab, g_tab, s_tab = st.tabs(["Overview", "Goals", "Settings"])
        
        with d_tab:
            budget = st.session_state['monthly_budget']
            spent = analyzer.get_total_expenses()
            safe = analyzer.get_safe_daily_limit(budget)
            burn = analyzer.get_projected_spending()
            pct = analyzer.get_budget_status_percentage(budget)
            
            # --- 1. TOP SECTION (At a Glance) ---
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            def metric_card(title, val, type_cls=""):
                return f"""<div class='metric-card {type_cls}'>
                    <div class='metric-title'>{title}</div>
                    <div class='metric-value'>{val}</div>
                </div>"""
                
            with col1: st.markdown(metric_card("Total Expenses (So Far)", f"Ksh {spent:,.0f}"), unsafe_allow_html=True)
            with col2: 
                rem = max(0, budget - spent)
                st.markdown(metric_card("Remaining Budget", f"Ksh {rem:,.0f}"), unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- 2. MIDDLE SECTION (Insights & Recommendations) ---
            st.markdown("### Financial Clarity")
            insights = InsightsEngine(analyzer, budget)
            st.info(insights.get_financial_translation(), icon="💡")
            
            rec = insights.get_actionable_recommendation()
            if rec['type'] == 'danger':
                st.error(rec['msg'], icon="🛑")
            elif rec['type'] == 'warning':
                st.warning(rec['msg'], icon="⚠️")
            else:
                st.success(rec['msg'], icon="✅")
                
            st.markdown("<br><hr style='border-color: rgba(0,0,0,0.05);'><br>", unsafe_allow_html=True)
            
            # --- 3. BOTTOM SECTION (Action Center / Logging) ---
            st.markdown("<div id='input-center'></div>", unsafe_allow_html=True)
            st.markdown("### Quick Log Center")
            tab_manual, tab_mpesa = st.tabs(["Manual Entry", "M-Pesa SMS Auto-fill"])
            
            with tab_mpesa:
                with st.form("mpesa_form"):
                    st.markdown("<div style='color: #86868B; margin-bottom:10px;'>Paste Safaricom SMS for intelligent parsing</div>", unsafe_allow_html=True)
                    sms_text = st.text_area("SMS Content", placeholder="Ksh 150.00 paid to KHALID KHALID on...", label_visibility="collapsed", height=100)
                    st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
                    sub_sms = st.form_submit_button("Extract & Autofill", use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    if sub_sms:
                        amount_match = re.search(r'Ksh\s*([\d,]+\.?\d*)', sms_text, re.IGNORECASE)
                        vendor_match = re.search(r'(?:paid to|sent to)\s*(.*?)\s*on', sms_text, re.IGNORECASE)
                        if amount_match:
                            st.session_state['parsed_amount'] = float(amount_match.group(1).replace(',', ''))
                        if vendor_match:
                            st.session_state['parsed_vendor'] = vendor_match.group(1).strip()
                        st.success("Extracted! Check Manual Entry tab to confirm.")
                        
            with tab_manual:
                with st.form("manual_form", clear_on_submit=True):
                    amt_val = st.session_state.get('parsed_amount', 0.0)
                    desc_val = st.session_state.get('parsed_vendor', "")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        amount = st.number_input("Amount (Ksh)", min_value=0.0, value=amt_val)
                        category = st.selectbox("Category", ["Food & Dining", "Transport", "Academics", "Entertainment", "Rent", "Utilities", "Other"])
                    with col_b:
                        date_val = st.date_input("Date", value=datetime.date.today())
                        description = st.text_input("Entity / Description", value=desc_val)
                    
                    st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
                    if st.form_submit_button("Record Transaction", use_container_width=True):
                        if amount > 0:
                            self.db.add_expense(Expense(user_id=user_id, amount=amount, date=date_val.strftime("%Y-%m-%d"), description=description, category=category))
                            if 'parsed_amount' in st.session_state: del st.session_state['parsed_amount']
                            if 'parsed_vendor' in st.session_state: del st.session_state['parsed_vendor']
                            st.success("Transaction recorded.")
                            st.rerun()
                        else:
                            st.error("Amount must be greater than 0.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
            st.markdown("<br><hr style='border-color: rgba(0,0,0,0.05);'><br>", unsafe_allow_html=True)
            
            # --- 4. ADVANCED CHARTS & GRAPHS ---
            col_srd, col_util = st.columns(2)
            with col_srd: st.markdown(metric_card("Safe-to-Spend (Daily)", f"Ksh {safe:,.0f}", "metric-safe"), unsafe_allow_html=True)
            with col_util: 
                util_cls = "metric-empty" if pct == 0 else ("metric-warn" if pct>=80 else "")
                st.markdown(metric_card("Utilization", f"{pct:.1f}%", util_cls), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div style='color:#8E8E93; margin-bottom:10px;'>Category Distribution</div>", unsafe_allow_html=True)
                df_cat = analyzer.get_expenses_by_category()
                if not df_cat.empty:
                    fig = px.pie(df_cat, names='category', values='amount', hole=0.7, 
                                 color_discrete_sequence=['#007AFF', '#00C7BE', '#5856D6', '#FF9500', '#FF3B30'])
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, b=0, l=0, r=0), font_color="#000000")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    UIComponents.render_empty_state("No transactions yet")
            with c2:
                st.markdown("<div style='color:#8E8E93; margin-bottom:10px;'>Expenditure Flow</div>", unsafe_allow_html=True)
                df_time = analyzer.get_expenses_over_time()
                if not df_time.empty:
                    fig = go.Figure(go.Scatter(x=df_time['date'], y=df_time['amount'], mode='lines+markers', line=dict(color='#007AFF', width=3), fill='tozeroy', fillcolor='rgba(0, 122, 255, 0.1)'))
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, b=0, l=0, r=0), font_color="#000000", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    UIComponents.render_empty_state("No timeline data")
                    
        with g_tab:
            st.markdown("### Sinking Funds")
            with st.expander("Create Goal"):
                with st.form("goal_form"):
                    g_name = st.text_input("Target Name")
                    g_amt = st.number_input("Target Amount", min_value=0.0)
                    if st.form_submit_button("Initialize Goal"):
                        self.db.add_goal(Goal(name=g_name, target_amount=g_amt, current_amount=0.0, user_id=user_id))
                        st.rerun()
            
            goals = self.db.get_all_goals(user_id)
            if not goals:
                UIComponents.render_empty_state("No active goals")
            else:
                for g in goals:
                    st.markdown(f"<span style='color:#1D1D1F; font-weight:600;'>{g.name}</span>", unsafe_allow_html=True)
                    p = min(1.0, g.current_amount / g.target_amount) if g.target_amount > 0 else 0
                    st.markdown(f"<span style='color:#3A3A3C; font-size:0.9rem;'>{p*100:.1f}% — Ksh {g.current_amount:,.0f} of {g.target_amount:,.0f}</span>", unsafe_allow_html=True)
                    st.progress(p)
                    
                    with st.form(f"fund_{g.id}"):
                        c1, c2 = st.columns([3, 1])
                        with c1: add = st.number_input("Add Funds", min_value=0.0, key=f"f_{g.id}", label_visibility="collapsed")
                        with c2: 
                            if st.form_submit_button("Fund"):
                                self.db.add_funds_to_goal(g.id, user_id, add)
                                st.rerun()
                                
        with s_tab:
            st.markdown("### Preferences")
            b_input = st.number_input("Basline Monthly Budget (Ksh)", value=st.session_state['monthly_budget'])
            if b_input != st.session_state['monthly_budget']:
                st.session_state['monthly_budget'] = b_input
                st.rerun()
                
            if st.button("End Session"):
                st.session_state['user_id'] = None
                st.rerun()

if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.run()
