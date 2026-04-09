import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re
import os
import requests
import urllib.parse
from models import Expense, BudgetAnalyzer, Goal, InsightsEngine
from database import DatabaseManager

class OAuthManager:
    @staticmethod
    def get_google_auth_url():
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        if client_id:
            # Real OAuth flow URL
            redirect_uri = urllib.parse.quote("http://localhost:8501/")
            return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=email%20profile"
        return "?oauth_mock=google"

    @staticmethod
    def get_github_auth_url():
        client_id = os.environ.get("GITHUB_CLIENT_ID")
        if client_id:
            redirect_uri = urllib.parse.quote("http://localhost:8501/")
            return f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=user:email"
        return "?oauth_mock=github"

    @staticmethod
    def handle_callback(db: DatabaseManager):
        if 'oauth_handled' in st.session_state and st.session_state['oauth_handled']:
            return

        params = st.query_params
        if "oauth_mock" in params:
            provider = params["oauth_mock"]
            mock_email = f"demo_{provider}@student.edu"
            
            user_id = db.get_or_create_oauth_user(mock_email, provider)
            st.session_state['user_id'] = user_id
            st.session_state['username'] = mock_email
            st.session_state['oauth_handled'] = True
            
            st.toast(f"Simulating OAuth Login for {provider.capitalize()}! No Client ID found.", icon="🔑")
            st.query_params.clear()
            st.rerun()

        elif "code" in params:
            # Here you would:
            # 1. requests.post(token_url, data={code, client_id, client_secret})
            # 2. requests.get(user_info_url, headers={'Authorization': 'Bearer ...'})
            # 3. Handle actual db user creation with true email
            # We add a toast to indicate we caught the code and redirect
            st.toast("Caught real OAuth code, token exchange needed!", icon="🔄")
            st.query_params.clear()
            st.rerun()

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
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;800&family=Inter:wght@400;500;600;700&display=swap');

            :root {
                --bg-primary: #F3F4F6;
                --bg-white: #FFFFFF;
                --text-main: #111827;
                --text-muted: #6B7280;
                --brand-blue: #3B82F6;
                --brand-blue-hover: #2563EB;
                --border-color: #E5E7EB;
                --input-bg: #F9FAFB;
                
                --apple-bg: #F2F2F7;
                --apple-card: rgba(255, 255, 255, 0.35);
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
                background-color: var(--bg-primary);
            }
            [class*="css"] {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            }
            .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], 
            [data-baseweb="tab-panel"], div[role="tabpanel"], div[data-testid="stVerticalBlock"],
            div[data-testid="stHorizontalBlock"], div[data-testid="column"] {
                background-color: transparent !important;
                color: var(--text-main);
            }
            
            @keyframes mesh-float {
                0% { transform: translate(0px, 0px) scale(1); }
                33% { transform: translate(30px, -50px) scale(1.1); }
                66% { transform: translate(-20px, 20px) scale(0.9); }
                100% { transform: translate(0px, 0px) scale(1); }
            }

            .mesh-shape-1 {
                position: fixed; top: -10%; left: -10%; width: 50vw; height: 50vw;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, rgba(255,255,255,0) 70%);
                border-radius: 50%; filter: blur(60px); z-index: -10;
                animation: mesh-float 20s infinite alternate; pointer-events: none;
            }
            .mesh-shape-2 {
                position: fixed; bottom: -10%; right: -10%; width: 60vw; height: 60vw;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.05) 0%, rgba(255,255,255,0) 70%);
                border-radius: 50%; filter: blur(80px); z-index: -10;
                animation: mesh-float 25s infinite alternate-reverse; pointer-events: none;
            }
            
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}

            .hero-title {
                text-align: center;
                font-size: clamp(2.5rem, 6vw, 4rem);
                font-weight: 800;
                background: linear-gradient(180deg, #111827 0%, #4B5563 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
                letter-spacing: -1px;
            }
            .hero-subtitle {
                text-align: center;
                color: var(--text-muted);
                font-size: 1.2rem;
                font-weight: 400;
                margin-bottom: 3rem;
            }

            .auth-container {
                background-color: var(--bg-white);
                border-radius: 20px;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
                border: 1px solid var(--border-color);
                overflow: hidden;
            }
            
            .auth-marketing-col {
                padding: 40px;
                height: 100%;
                background: radial-gradient(120% 120% at 50% -20%, rgba(59, 130, 246, 0.1) 0%, transparent 100%);
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            .badge {
                display: inline-flex;
                align-items: center;
                padding: 6px 12px;
                background-color: rgba(59, 130, 246, 0.1);
                color: var(--brand-blue);
                border-radius: 9999px;
                font-size: 0.875rem;
                font-weight: 600;
                margin-bottom: 24px;
                width: max-content;
            }

            .marketing-title {
                font-size: 2.75rem;
                line-height: 1.2;
                font-weight: 700;
                color: var(--text-main);
                margin-bottom: 24px;
            }

            .marketing-title span {
                color: var(--brand-blue);
            }
            
            .feature-list {
                list-style: none;
                padding: 0;
                margin: 0 0 32px 0;
            }
            .feature-list li {
                display: flex;
                align-items: center;
                margin-bottom: 16px;
                color: var(--text-main);
                font-weight: 500;
            }
            .feature-icon {
                color: var(--brand-blue);
                background-color: #EFF6FF;
                width: 32px;
                height: 32px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                font-size: 14px;
            }

            .social-proof {
                display: flex;
                align-items: center;
                margin-top: 40px;
                padding-top: 32px;
                border-top: 1px solid var(--border-color);
            }
            .avatar-group {
                display: flex;
                margin-right: 16px;
            }
            .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: 2px solid #FFF;
                margin-left: -12px;
                background-color: #E5E7EB;
            }
            .avatar:first-child { margin-left: 0; }
            .proof-text {
                font-size: 0.875rem;
                color: var(--text-muted);
            }
            .proof-text strong {
                color: var(--text-main);
                font-weight: 600;
            }

            div[data-baseweb="input"] > div, 
            div[data-baseweb="select"] > div, 
            div[data-baseweb="number-input"] > div,
            textarea {
                background-color: var(--input-bg) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: 8px !important;
                color: var(--text-main) !important;
            }
            div[data-baseweb="input"] > div:focus-within, 
            div[data-baseweb="select"] > div:focus-within {
                border-color: var(--brand-blue) !important;
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
            }

            div.stButton > button:first-child {
                background: var(--bg-white);
                color: var(--text-main);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            div.stButton.primary-btn > button:first-child {
                background: var(--brand-blue);
                color: #FFFFFF;
                border: none;
                box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2);
                font-weight: 600;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            div.stButton > button:first-child:hover {
                background: var(--bg-primary);
                transform: translateY(-1px);
            }
            div.stButton.primary-btn > button:first-child:hover {
                background: var(--brand-blue-hover);
                color: #FFFFFF;
                transform: translateY(-2px);
                box-shadow: 0 6px 8px -1px rgba(59, 130, 246, 0.3);
            }

            .social-btn {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 10px 16px;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                background: var(--bg-white);
                color: var(--text-main);
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                text-decoration: none;
                font-size: 0.875rem;
                margin-top: 10px;
                width: 100%;
            }
            .social-btn:hover {
                background: var(--input-bg);
            }

            .stProgress > div > div > div > div {
                background-color: var(--brand-blue) !important;
                border-radius: 10px;
            }
            
            button[data-baseweb="tab"] {
                border-radius: 8px !important;
                padding: 8px 16px !important;
            }
            div[role="tablist"] {
                padding: 4px;
                background: var(--input-bg);
                border-radius: 10px;
                border: 1px solid var(--border-color);
                margin-bottom: 24px;
            }
            
            .metric-card {
                background-color: var(--bg-white);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); /* Modern Light Mode shadow */
            }
            .metric-title {
                color: var(--text-muted);
                font-size: 0.95rem;
                font-weight: 600;
                margin-bottom: 8px;
            }
            .metric-value {
                color: var(--brand-blue);
                font-size: 2.2rem;
                font-weight: 700;
            }
            .metric-safe { background: #F0FDF4; border-color: #DCFCE7; }
            .metric-safe .metric-value { color: #16A34A; }
            
            .metric-warn { background: #FEF2F2; border-color: #FEE2E2; }
            .metric-warn .metric-value { color: #DC2626; }
            
            .metric-empty .metric-value { color: var(--text-muted); }

            .empty-chart {
                background: var(--bg-white);
                border-radius: 16px;
                height: 250px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                border: 1px dashed var(--border-color);
            }

        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)
        st.markdown('''
            <div class="mesh-shape-1"></div>
            <div class="mesh-shape-2"></div>
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
        OAuthManager.handle_callback(self.db)
        
        if st.session_state['user_id'] is None:
            self.render_auth()
        else:
            self.render_main_app()

    def render_auth(self):
        st.markdown("<div style='margin-top: 4vh;'></div>", unsafe_allow_html=True)
        
        spacer_l, center_col, spacer_r = st.columns([1, 8, 1])
        
        with center_col:
            st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
            
            col_market, col_form = st.columns([1.2, 1])
            
            with col_market:
                st.markdown("""
<div class="auth-marketing-col">
<div class="badge">✨ New: AI Budgeting Insights v2.0</div>
<h1 class="marketing-title">Master Your <br><span>Student Finances</span><br> With Ease.</h1>

<ul class="feature-list">
<li><div class="feature-icon">📊</div> Real-time expense tracking & analytics</li>
<li><div class="feature-icon">🤖</div> Smart AI-driven budget recommendations</li>
<li><div class="feature-icon">🎯</div> Sinking funds for long-term goals</li>
</ul>

<div class="social-proof">
<div class="avatar-group">
<div class="avatar" style="background:#DBEAFE;"></div>
<div class="avatar" style="background:#BBF7D0;"></div>
<div class="avatar" style="background:#FEF08A;"></div>
</div>
<div class="proof-text">
Join <strong>10,000+</strong> students managing<br>their campus life effectively!
</div>
</div>
</div>
""", unsafe_allow_html=True)

            with col_form:
                st.markdown("<div style='padding: 40px;'>", unsafe_allow_html=True)
                st.markdown("<h2 style='font-size:2rem; font-weight:700; margin-bottom: 24px; color:var(--text-main);'>Welcome Back</h2>", unsafe_allow_html=True)
                
                tab_signin, tab_signup = st.tabs(["Sign In", "Create Account"])
                
                with tab_signin:
                    with st.form("login_form", clear_on_submit=False):
                        username = st.text_input("Email/Username", placeholder="e.g. alex@student.edu")
                        password = st.text_input("Password", type="password", placeholder="••••••••")
                        st.markdown("<div style='display:flex; justify-content:flex-end; margin-top:-10px; margin-bottom:16px;'><a href='#' style='font-size:0.875rem; color:var(--brand-blue); text-decoration:none;'>Forgot password?</a></div>", unsafe_allow_html=True)
                        
                        st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
                        sub = st.form_submit_button("Authenticate Account →", use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        if sub:
                            user_id = self.db.verify_user(username, password)
                            if user_id:
                                st.session_state['user_id'] = user_id
                                st.session_state['username'] = username
                                st.rerun()
                            else:
                                st.error("Invalid credentials.")
                                
                    st.markdown(f"""
<div style="text-align:center; margin:24px 0; position:relative;">
    <hr style="border:none; border-top:1px solid var(--border-color); margin:0;" />
    <span style="position:absolute; top:-10px; left:50%; transform:translateX(-50%); background:var(--bg-white); padding:0 10px; color:var(--text-muted); font-size:0.875rem;">Or continue with</span>
</div>
<a href="{OAuthManager.get_google_auth_url()}" class="social-btn" style="text-decoration:none;"><span style="margin-right:10px; display:flex; align-items:center;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="20px" height="20px"><path fill="#FFC107" d="M43.6 20.1H42V20H24v8h11.3C34.7 32.8 30 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.1 8 3.1l5.7-5.7C34.1 5.8 29.3 3.9 24 3.9 12.9 3.9 4 12.9 4 24s8.9 20.1 20 20.1c11.1 0 20-8.9 20-20.1 0-1.4-.2-2.7-.4-3.9z"/><path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 17.5 19 15.9 24 15.9c3.1 0 5.9 1.1 8 3.1l5.7-5.7C34.1 9.8 29.3 7.9 24 7.9c-7.7 0-14.4 4.3-17.7 10.8z"/><path fill="#4CAF50" d="M24 44.1c5.1 0 9.8-1.7 13.4-4.7l-6.2-5c-2.1 1.4-4.5 2.1-7.2 2.1-5 0-9.3-3.1-11.1-7.6l-6.6 5.1C9.6 39.8 16.3 44.1 24 44.1z"/><path fill="#1976D2" d="M43.6 20.1h-1.6V20H24v8h11.3c-.7 3.3-2.6 6-5.1 7.6l6.2 5c3.7-3.4 7.2-8.9 7.2-16.5 0-1.4-.2-2.7-.4-3.9z"/></svg></span> Continue with Google</a>
<a href="{OAuthManager.get_github_auth_url()}" class="social-btn" style="text-decoration:none;"><span style="margin-right:10px; display:flex; align-items:center;"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg></span> Continue with GitHub</a>
""", unsafe_allow_html=True)
                            
                with tab_signup:
                    with st.form("register_form", clear_on_submit=True):
                        new_user = st.text_input("Username", placeholder="Choose a username")
                        new_pass = st.text_input("Password", type="password", placeholder="Create a strong password")
                        conf_pass = st.text_input("Confirm Password", type="password", placeholder="Repeat your password")
                        
                        st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
                        sub_reg = st.form_submit_button("Create My Account →", use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        if sub_reg:
                            if new_pass == conf_pass and len(new_pass) >= 8:
                                if self.db.create_user(new_user, new_pass):
                                    st.success("Account created. You can now sign in.")
                                else:
                                    st.error("Username exists.")
                            else:
                                st.error("Invalid password criteria.")
                                
                st.markdown("</div>", unsafe_allow_html=True) # end padding
            
            st.markdown("</div>", unsafe_allow_html=True) # end auth-container

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
