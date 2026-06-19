"""
Netflix Content Insights Engine v1.0
Professional Enterprise Dashboard
Built with Streamlit, Plotly, Pandas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

# ══════════════════════════════════════════════════════════════════
#  GLOBAL CONFIGURATION & PAGE SETUP
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Netflix Insights",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS Injection ──

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

THEMES = {
    "dark": {
        "bg": "#141414", "card": "#000000", "card_hover": "#1A1A1A",
        "text": "#FFFFFF", "text_muted": "#B3B3B3", "border": "#333333",
        "accent": "#E50914", "shadow": "rgba(16, 24, 40, 0.2)",
        "glass": "rgba(0, 0, 0, 0.75)", "input_bg": "rgba(255, 255, 255, 0.05)",
        "input_border": "rgba(255, 255, 255, 0.15)", "btn_hover": "rgba(255, 255, 255, 0.1)",
        "overlay": "rgba(20, 20, 20, 0.6)", "tooltip": "#141414", "grid": "#333333",
        "bar_default": "#344054", "plotly_bg": "rgba(0,0,0,0)"
    },
    "light": {
        "bg": "#F9FAFB", "card": "#FFFFFF", "card_hover": "#F3F4F6",
        "text": "#111827", "text_muted": "#6B7280", "border": "#E5E7EB",
        "accent": "#E50914", "shadow": "rgba(0, 0, 0, 0.05)",
        "glass": "rgba(255, 255, 255, 0.85)", "input_bg": "#FFFFFF",
        "input_border": "#D1D5DB", "btn_hover": "rgba(0, 0, 0, 0.05)",
        "overlay": "rgba(255, 255, 255, 0.6)", "tooltip": "#FFFFFF", "grid": "#E5E7EB",
        "bar_default": "#9CA3AF", "plotly_bg": "rgba(255,255,255,0)"
    }
}

def get_custom_css(theme):
    t = THEMES[theme]
    css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --text-color: VAR_TEXT !important;
        --background-color: VAR_BG !important;
        --secondary-background-color: VAR_CARD !important;
        --primary-color: VAR_ACCENT !important;
    }

    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] { font-family: 'Inter', sans-serif; color: VAR_TEXT !important; background-color: VAR_BG !important; }
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] p, 
    [data-baseweb="checkbox"] label, [data-baseweb="radio"] label, div[data-baseweb="select"] * {
        color: VAR_TEXT !important;
    }
    .stApp { background-color: VAR_BG !important; }
    #MainMenu { visibility: hidden; } footer { visibility: hidden; }

    .top-bar { position: fixed; top: 0; left: 0; right: 0; height: 56px; background-color: VAR_BG; border-bottom: 1px solid VAR_BORDER; z-index: 999999; display: flex; align-items: center; padding: 0 32px; }
    .top-bar-brand { font-family: 'Inter', sans-serif; font-size: 1.1rem; font-weight: 700; color: VAR_ACCENT; letter-spacing: 0.5px; text-transform: uppercase; }
    .top-bar-spacer { flex-grow: 1; }
    .top-bar-stats { margin-left: 32px; display: flex; gap: 16px; font-size: 0.85rem; color: VAR_TEXT_MUTED; }
    .top-bar-stats strong { color: VAR_TEXT; font-weight: 600; }
    .top-bar-user { font-size: 0.85rem; color: VAR_TEXT_MUTED; font-weight: 500; display: flex; gap: 8px; align-items: center; }
    
    .block-container, div[data-testid="stAppViewBlockContainer"] { padding-top: 2.5rem !important; margin-top: 0rem !important; }
    .stApp > header { background: transparent !important; box-shadow: none !important; z-index: 9999999 !important; }

    .metric-card { background: VAR_CARD; border: 1px solid VAR_BORDER; border-radius: 8px; padding: 24px; text-align: left; transition: all 0.2s ease; box-shadow: 0 1px 2px VAR_SHADOW; height: 100%; }
    .metric-card:hover { border-color: VAR_CARD_HOVER; box-shadow: 0 4px 6px -1px VAR_SHADOW; }
    .metric-value { font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 600; color: VAR_TEXT; line-height: 1.2; margin-bottom: 4px; }
    .metric-label { font-size: 0.85rem; font-weight: 500; color: VAR_TEXT_MUTED; }
    .metric-subtext { font-size: 0.75rem; color: VAR_TEXT_MUTED; margin-top: 8px; font-weight: 400; }

    .section-header { font-family: 'Inter', sans-serif; font-size: 1.2rem; font-weight: 600; color: VAR_TEXT; padding-bottom: 12px; margin-top: 32px; margin-bottom: 24px; border-bottom: 1px solid VAR_BORDER; }

    [data-testid="stTabs"] [role="tablist"] { gap: 24px; }
    [data-testid="stTabs"] button[role="tab"] { height: 48px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; color: VAR_TEXT_MUTED !important; }
    [data-testid="stTabs"] button[role="tab"] * { color: VAR_TEXT_MUTED !important; }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] { background-color: transparent !important; border-bottom: 2px solid VAR_ACCENT !important; color: VAR_ACCENT !important; }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] * { color: VAR_ACCENT !important; font-weight: 600 !important; }

    [data-testid="stSidebar"] { top: 56px !important; height: calc(100vh - 56px) !important; background: VAR_CARD !important; border-right: 1px solid VAR_BORDER; }
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { top: 72px !important; left: 16px !important; z-index: 9999999 !important; background-color: VAR_BG !important; border: 1px solid VAR_BORDER !important; border-radius: 6px !important; box-shadow: 0 4px 6px VAR_SHADOW !important; }
    [data-testid="stSidebar"] .stButton > button { width: 100%; background-color: VAR_BG; border: 1px solid VAR_BORDER; color: VAR_TEXT; font-weight: 500; box-shadow: 0 1px 2px VAR_SHADOW; }
    [data-testid="stSidebar"] .stButton > button:hover { background-color: VAR_CARD_HOVER; border-color: VAR_BORDER; color: VAR_TEXT; }

    [data-testid="stStatusWidget"] { position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background-color: VAR_OVERLAY !important; z-index: 9999999 !important; display: flex !important; align-items: center !important; justify-content: center !important; backdrop-filter: blur(2px) !important; }
    [data-testid="stStatusWidget"] > div { background-color: VAR_CARD !important; padding: 20px 40px !important; border-radius: 12px !important; border: 1px solid VAR_BORDER !important; box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important; transform: scale(1.5); }

    .stDataFrame { border-radius: 8px; overflow: hidden; border: 1px solid VAR_BORDER; }

    .stDownloadButton > button { background: VAR_BG !important; color: VAR_TEXT !important; border: 1px solid VAR_BORDER !important; border-radius: 6px !important; padding: 10px 20px !important; font-weight: 500 !important; transition: all 0.2s ease !important; font-size: 0.85rem !important; box-shadow: 0 1px 2px VAR_SHADOW !important; }
    .stDownloadButton > button:hover { background: VAR_CARD !important; border-color: VAR_CARD_HOVER !important; color: VAR_TEXT !important; }

    .main-title-container { margin-bottom: 8px; }
    .main-title { font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 600; color: VAR_TEXT; line-height: 1.2; }
    .main-description { color: VAR_TEXT_MUTED; font-size: 1rem; margin-bottom: 32px; font-weight: 400; max-width: 800px; }

    [data-testid="stForm"] { background-color: VAR_GLASS !important; backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important; border: 1px solid VAR_INPUT_BORDER !important; border-radius: 20px !important; padding: 48px !important; max-width: 450px !important; margin: 0 auto !important; box-shadow: 0 24px 48px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1) !important; position: relative; z-index: 10; min-height: auto !important; }
    [data-testid="stForm"] label { display: block !important; font-size: 0.9rem !important; color: VAR_TEXT !important; font-weight: 500 !important; margin-bottom: 8px !important; text-transform: none !important; }
    [data-testid="stForm"] input { background-color: VAR_INPUT_BG !important; color: VAR_TEXT !important; border: 1px solid VAR_INPUT_BORDER !important; border-radius: 8px !important; padding: 14px 16px !important; font-size: 1rem !important; margin-bottom: 20px !important; transition: all 0.3s ease !important; }
    [data-testid="stForm"] input:hover { border-color: VAR_BORDER !important; }
    [data-testid="stForm"] input:focus { background-color: VAR_INPUT_BG !important; border-color: VAR_ACCENT !important; box-shadow: 0 0 0 1px VAR_ACCENT !important; }
    
    [data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"], [data-testid="stForm"] .stButton > button:not([data-testid="baseButton-secondaryFormSubmit"]):not([data-testid="baseButton-tertiaryFormSubmit"]) { background-color: VAR_ACCENT !important; color: white !important; border-radius: 50px !important; font-weight: 700 !important; padding: 12px 14px !important; margin-top: 16px !important; width: 100% !important; border: none !important; font-size: 1.05rem !important; transition: all 0.3s ease !important; box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important; }
    [data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"]:hover, [data-testid="stForm"] .stButton > button:not([data-testid="baseButton-secondaryFormSubmit"]):hover { background-color: #C11119 !important; transform: translateY(-2px) !important; box-shadow: 0 6px 12px rgba(229, 9, 20, 0.4) !important; }

    [data-testid="stForm"] button[data-testid="baseButton-secondaryFormSubmit"] { background-color: VAR_INPUT_BG !important; color: VAR_TEXT !important; border-radius: 50px !important; font-weight: 600 !important; padding: 12px 14px !important; margin-top: 16px !important; width: 100% !important; border: 1px solid VAR_INPUT_BORDER !important; font-size: 1.05rem !important; transition: all 0.3s ease !important; }
    [data-testid="stForm"] button[data-testid="baseButton-secondaryFormSubmit"]:hover { background-color: VAR_BTN_HOVER !important; border-color: VAR_BORDER !important; transform: translateY(-2px) !important; }
    
    [data-testid="stForm"] button[data-testid="baseButton-tertiaryFormSubmit"] { background: transparent !important; color: VAR_TEXT_MUTED !important; border: none !important; box-shadow: none !important; font-size: 0.9rem !important; font-weight: 500 !important; padding: 0 !important; margin-top: 16px !important; }
    [data-testid="stForm"] button[data-testid="baseButton-tertiaryFormSubmit"]:hover { color: VAR_TEXT !important; text-decoration: underline !important; background: transparent !important; transform: none !important; }
    
    button[data-testid="baseButton-tertiary"] { background: transparent !important; color: VAR_TEXT_MUTED !important; border: none !important; box-shadow: none !important; }
    button[data-testid="baseButton-tertiary"] * { color: VAR_TEXT_MUTED !important; }
    button[data-testid="baseButton-tertiary"] strong { color: VAR_TEXT !important; font-weight: 600 !important; }
    button[data-testid="baseButton-tertiary"]:hover * { color: VAR_TEXT !important; }
</style>
"""
    for k, v in t.items():
        css = css.replace(f"VAR_{k.upper()}", v)
    return css

st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════
#  MODULE 1: DATA LOADING & PREPROCESSING
# ══════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_and_preprocess_data():
    df = pd.read_csv("netflix_titles.csv")
    df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
    df["year_added"] = df["date_added"].dt.year.astype("Int64")
    df["duration_minutes"] = df["duration"].str.extract(r"(\d+)", expand=False).astype(float)
    df["primary_country"] = df["country"].str.split(",").str[0].str.strip()
    return df


# ══════════════════════════════════════════════════════════════════
#  MODULE 2: AUTHENTICATION GATEWAY
# ══════════════════════════════════════════════════════════════════

@st.dialog("Create a New Account")
def show_signup_dialog():
    st.markdown(f"<p style='color:{THEMES[st.session_state.theme]['text_muted']}; font-size:0.9rem;'>Register a new demo account.</p>", unsafe_allow_html=True)
    new_user = st.text_input("New Email", placeholder="e.g. elon@tesla.com")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Register", type="primary", use_container_width=True):
        if new_user and new_pass:
            st.session_state.demo_credentials[new_user] = new_pass
            st.success("Account created successfully! You can now close this and sign in.")
        else:
            st.error("Please fill in both fields.")

@st.dialog("Reset Password")
def show_forgot_dialog():
    st.markdown(f"<p style='color:{THEMES[st.session_state.theme]['text_muted']}; font-size:0.9rem;'>Reset your password for a demo account.</p>", unsafe_allow_html=True)
    reset_email = st.text_input("Account Email")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Reset Password", type="primary", use_container_width=True):
        if reset_email in st.session_state.demo_credentials:
            st.session_state.demo_credentials[reset_email] = new_pass
            st.success("Password reset successfully! You can now close this and sign in.")
        else:
            st.error("Account not found.")

def render_login_screen():
    st.markdown("""
        <style>
        .stApp {
            background-image: linear-gradient(to top, rgba(0,0,0,0.8) 0, rgba(0,0,0,0) 60%, rgba(0,0,0,0.8) 100%), url("https://assets.nflxext.com/ffe/siteui/vlv3/a73c4363-1dcd-4125-b746-8ed73c46646f/fe242f4b-1dda-4a5d-b054-9547d51ee939/US-en-20231016-popsignuptwoweeks-perspective_alpha_website_large.jpg");
            background-size: cover;
            background-position: center;
        }
        
        .top-bar { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        /* Netflix-Themed Blobs */
        .blob-1 {
            position: absolute;
            top: 15%;
            right: 20%;
            width: 350px;
            height: 350px;
            background: linear-gradient(135deg, #E50914 0%, #83050C 100%);
            border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
            z-index: 0;
            opacity: 0.6;
            filter: blur(16px);
        }
        .blob-2 {
            position: absolute;
            bottom: 15%;
            left: 15%;
            width: 250px;
            height: 200px;
            background: linear-gradient(135deg, #E50914 0%, #330000 100%);
            border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
            z-index: 0;
            opacity: 0.5;
            filter: blur(12px);
        }
        
        .login-header-container {
            text-align: center;
            position: relative;
            z-index: 10;
            margin-top: 6vh;
            margin-bottom: 24px;
        }
        
        .netflix-logo-center {
            width: 140px;
            margin-bottom: 16px;
        }
        
        .login-header-container h1 {
            font-size: 2.2rem;
            color: {THEMES[st.session_state.theme][\"text\"]};
            font-weight: 800;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        
        /* The Card */
        [data-testid="stForm"] {
            background-color: rgba(0, 0, 0, 0.75) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 20px !important;
            padding: 48px !important;
            max-width: 450px !important;
            margin: 0 auto !important;
            box-shadow: 0 24px 48px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1) !important;
            position: relative;
            z-index: 10;
            min-height: auto !important;
        }
        
        /* Labels */
        [data-testid="stForm"] label {
            display: block !important;
            font-size: 0.9rem !important;
            color: #E5E5E5 !important;
            font-weight: 500 !important;
            margin-bottom: 8px !important;
            text-transform: none !important;
        }
        
        /* Inputs */
        [data-testid="stForm"] input {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
            padding: 14px 16px !important;
            font-size: 1rem !important;
            margin-bottom: 20px !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stForm"] input:hover {
            border-color: rgba(255, 255, 255, 0.4) !important;
        }
        [data-testid="stForm"] input:focus {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-color: #E50914 !important;
            box-shadow: 0 0 0 1px #E50914 !important;
        }
        
        /* Pill Button (Primary) */
        [data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"],
        [data-testid="stForm"] .stButton > button:not([data-testid="baseButton-secondaryFormSubmit"]):not([data-testid="baseButton-tertiaryFormSubmit"]) {
            background-color: #E50914 !important;
            color: white !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
            padding: 12px 14px !important;
            margin-top: 16px !important;
            width: 100% !important;
            border: none !important;
            font-size: 1.05rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        }
        [data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"]:hover,
        [data-testid="stForm"] .stButton > button:not([data-testid="baseButton-secondaryFormSubmit"]):hover {
            background-color: #C11119 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(229, 9, 20, 0.4) !important;
        }

        /* Pill Button (Secondary / Demo) */
        [data-testid="stForm"] button[data-testid="baseButton-secondaryFormSubmit"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #E5E5E5 !important;
            border-radius: 50px !important;
            font-weight: 600 !important;
            padding: 12px 14px !important;
            margin-top: 16px !important;
            width: 100% !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            font-size: 1.05rem !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stForm"] button[data-testid="baseButton-secondaryFormSubmit"]:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #FFFFFF !important;
            border-color: rgba(255, 255, 255, 0.4) !important;
            transform: translateY(-2px) !important;
        }

        /* Pill Button (Tertiary / Links) */
        [data-testid="stForm"] button[data-testid="baseButton-tertiaryFormSubmit"] {
            background: transparent !important;
            color: #A3A3A3 !important;
            border: none !important;
            box-shadow: none !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            padding: 0 !important;
            margin-top: 16px !important;
        }
        [data-testid="stForm"] button[data-testid="baseButton-tertiaryFormSubmit"]:hover {
            color: #FFFFFF !important;
            text-decoration: underline !important;
            background: transparent !important;
            transform: none !important;
        }
        
        /* Bottom links */
        .login-links {
            display: flex;
            justify-content: space-between;
            margin-top: 24px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        .login-links a {
            color: #A3A3A3;
            text-decoration: none;
            transition: color 0.2s;
        }
        .login-links a:hover {
            color: {THEMES[st.session_state.theme][\"text\"]};
        }
        </style>
        
        <div class="blob-1"></div>
        <div class="blob-2"></div>
        
        <div class="login-header-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg" class="netflix-logo-center">
            <h1>Good to see you again</h1>
        </div>
    """, unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 1.8, 1])
    with col_center:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Your email", placeholder="e.g. admin")
            password = st.text_input("Your password", type="password", placeholder="Password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            with col_btn2:
                demo_submitted = st.form_submit_button("Instant Demo", type="secondary", use_container_width=True)
            
            st.markdown("""
                <div class="login-links" style="display: none;"></div>
            """, unsafe_allow_html=True)

            col_l1, col_l2 = st.columns(2)
            with col_l1:
                signup_submitted = st.form_submit_button("Don't have an account?", type="tertiary", use_container_width=True)
            with col_l2:
                forgot_submitted = st.form_submit_button("Forgot password?", type="tertiary", use_container_width=True)

            if signup_submitted:
                show_signup_dialog()
            
            if forgot_submitted:
                show_forgot_dialog()

            if demo_submitted:
                st.session_state["authenticated"] = True
                st.session_state["user"] = "admin"
                st.rerun()

            if submitted:
                if username in st.session_state.demo_credentials and st.session_state.demo_credentials[username] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = username
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use 'Instant Demo' or enter a valid account.")

def check_auth():
    return st.session_state.get("authenticated", False)


# ══════════════════════════════════════════════════════════════════
#  MODULE 3: SIDEBAR – FILTERS & SESSION CONTROLS
# ══════════════════════════════════════════════════════════════════

def render_sidebar(df: pd.DataFrame):
    with st.sidebar:
        st.markdown("""<img src="https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg" width="140" style="margin-bottom:16px;">""", unsafe_allow_html=True)
        st.caption(f"Logged in as {st.session_state.get('user', 'unknown')}")

        if st.button("Log Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.divider()
        st.markdown("#### Filter Controls")

        valid_years = df["release_year"].dropna().astype(int)
        min_year, max_year = int(valid_years.min()), int(valid_years.max())

        year_range = st.slider("Release Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year), step=1)
        selected_types = st.multiselect("Content Type", options=sorted(df["type"].dropna().unique()), default=sorted(df["type"].dropna().unique()))
        selected_ratings = st.multiselect("Maturity Rating", options=sorted(df["rating"].dropna().unique()), default=[])
        selected_countries = st.multiselect("Production Country", options=sorted(df["primary_country"].dropna().unique()), default=[])

        st.divider()
        st.markdown("#### Dataset Info")
        st.caption(f"Source: netflix_titles.csv")
        st.caption(f"Total Records: {len(df):,}")
        st.caption(f"Year Span: {min_year} – {max_year}")

    filtered = df[(df["release_year"] >= year_range[0]) & (df["release_year"] <= year_range[1])]
    if selected_types: filtered = filtered[filtered["type"].isin(selected_types)]
    if selected_ratings: filtered = filtered[filtered["rating"].isin(selected_ratings)]
    if selected_countries: filtered = filtered[filtered["primary_country"].isin(selected_countries)]
    return filtered


# ══════════════════════════════════════════════════════════════════
#  MODULE 4: EXECUTIVE METRIC CARDS
# ══════════════════════════════════════════════════════════════════

def chart_kpi_line(value, title, x_series, y_series):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_series, y=y_series, mode='lines+markers', marker=dict(size=6, color=THEMES[st.session_state.theme]["text"]), fill='tozeroy', line_color='#E50914', fillcolor='rgba(229, 9, 20, 0.1)', line=dict(width=3)))
    fig.update_layout(
        title=dict(text=f"<span style='font-size:14px;color:{THEMES[st.session_state.theme]['text_muted']};font-family:Inter'>{title}</span>", x=0.10, y=0.85),
        annotations=[dict(text=f"<b style='font-size:28px;color:{THEMES[st.session_state.theme]['text']};font-family:Inter'>{value}</b>", xref="paper", yref="paper", x=0.10, y=1.3, showarrow=False, xanchor="left", yanchor="top")],
        margin=dict(l=16, r=16, t=80, b=10),
        height=160,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        showlegend=False,
        clickmode="event+select"
    )
    return fig

def chart_kpi_bar(value, title, x_series, y_series):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x_series, y=y_series, marker_color='#E50914', opacity=0.8, marker_line_width=0))
    fig.update_layout(
        title=dict(text=f"<span style='font-size:14px;color:{THEMES[st.session_state.theme]['text_muted']};font-family:Inter'>{title}</span>", x=0.10, y=0.85),
        annotations=[dict(text=f"<b style='font-size:28px;color:{THEMES[st.session_state.theme]['text']};font-family:Inter'>{value}</b>", xref="paper", yref="paper", x=0.10, y=1.3, showarrow=False, xanchor="left", yanchor="top")],
        margin=dict(l=16, r=16, t=80, b=10),
        height=160,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        showlegend=False,
        bargap=0.2
    )
    return fig

def chart_kpi_donut(value, title, labels, values):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=values, text=labels, textposition='inside', insidetextfont=dict(color=THEMES[st.session_state.theme]["text"], size=14), marker_color=["#E50914", THEMES[st.session_state.theme]["border"]], marker_line_width=0))
    fig.update_layout(
        title=dict(text=f"<span style='font-size:14px;color:{THEMES[st.session_state.theme]['text_muted']};font-family:Inter'>{title}</span>", x=0.10, y=0.85),
        annotations=[dict(text=f"<b style='font-size:28px;color:{THEMES[st.session_state.theme]['text']};font-family:Inter'>{value}</b>", xref="paper", yref="paper", x=0.10, y=1.3, showarrow=False, xanchor="left", yanchor="top")],
        margin=dict(l=16, r=16, t=80, b=10),
        height=160,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True, range=[0, max(values) * 1.5 if len(values) > 0 else 1]),
        showlegend=False,
        clickmode="event+select"
    )
    return fig

def render_metric_cards(df: pd.DataFrame):
    total_titles = len(df)
    
    # Data for Card 1
    trend_df = df[df["year_added"] >= (df["year_added"].max() - 10)]
    trend_counts = trend_df.groupby("year_added").size().reset_index(name="counts")
    
    # Data for Card 2
    genres = df["listed_in"].str.split(", ").explode()
    top_genres_counts = genres.value_counts().head(12)
    top_genres_names = top_genres_counts.index
    total_genres = len(genres.unique())
    
    # Data for Card 3
    type_counts = df["type"].value_counts()
    pct_movies = (type_counts.get('Movie', 0) / total_titles * 100) if total_titles > 0 else 0
    
    fig1 = chart_kpi_line(f"{total_titles:,}", "Total Titles (10y Trend)", trend_counts["year_added"], trend_counts["counts"])
    fig2 = chart_kpi_bar(f"{total_genres}", "Unique Genres", top_genres_names[::-1], top_genres_counts.values[::-1])
    fig3 = chart_kpi_donut(f"{pct_movies:.0f}%", "Movie vs TV Show", type_counts.index, type_counts.values)

    cols = st.columns(3, gap="medium")
    with cols[0]:
        ev1 = st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False}, on_select="rerun", selection_mode="points")
        process_selection(ev1, "kpi_total", "year_added", extract_key="x")
    with cols[1]:
        ev2 = st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False}, on_select="rerun", selection_mode="points")
        process_selection(ev2, "kpi_genres", "listed_in", extract_key="x", match_type="contains")
    with cols[2]:
        ev3 = st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False}, on_select="rerun", selection_mode="points")
        process_selection(ev3, "kpi_split", "type", extract_key="x")


# ══════════════════════════════════════════════════════════════════
#  MODULE 5: PLOTLY VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════


def get_plotly_layout(theme):
    t = THEMES[theme]
    return dict(
        paper_bgcolor=t["plotly_bg"],
        plot_bgcolor=t["plotly_bg"],
        font=dict(family="Inter, sans-serif", color=t["text_muted"], size=12),
        margin=dict(l=20, r=20, t=50, b=20),
        hoverlabel=dict(bgcolor=t["card"], font_size=12, font_family="Inter, sans-serif", bordercolor=t["border"]),
    )


def chart_content_split(df: pd.DataFrame):
    type_counts = df["type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]
    fig = go.Figure(go.Bar(
        x=type_counts["Type"], y=type_counts["Count"],
        text=type_counts["Count"], textposition='auto',
        marker=dict(color=["#E50914", "#F04438"], line=dict(color=THEMES[st.session_state.theme]["bg"], width=2)),
    ))
    fig.update_layout(title=dict(text="Content Distribution", font=dict(size=14, color=THEMES[st.session_state.theme]["text"])), showlegend=False, height=350, clickmode="event+select", **get_plotly_layout(st.session_state.theme))
    return fig

def chart_year_ingestion(df: pd.DataFrame):
    yearly = df["year_added"].dropna().astype(int).value_counts().sort_index().reset_index()
    yearly.columns = ["Year", "Titles Added"]
    fig = go.Figure(go.Scatter(
        x=yearly["Year"], y=yearly["Titles Added"], mode="lines+markers",
        line=dict(color="#E50914", width=2, shape="spline"), marker=dict(size=6, color=THEMES[st.session_state.theme]["text"]), fill="tozeroy", fillcolor="rgba(217, 45, 32, 0.05)",
    ))
    fig.update_layout(title=dict(text="Year-over-Year Ingestion", font=dict(size=14, color=THEMES[st.session_state.theme]["text"])), xaxis=dict(gridcolor=THEMES[st.session_state.theme]["grid"], zeroline=False), yaxis=dict(gridcolor=THEMES[st.session_state.theme]["grid"], zeroline=False), height=350, clickmode="event+select", **get_plotly_layout(st.session_state.theme))
    return fig

def chart_top_genres(df: pd.DataFrame):
    genres = df["listed_in"].dropna().str.split(", ").explode()
    genre_counts = genres.value_counts().head(10).sort_values(ascending=True).reset_index()
    genre_counts.columns = ["Genre", "Titles"]
    fig = go.Figure(go.Bar(
        x=genre_counts["Titles"], y=genre_counts["Genre"], orientation="h",
        marker=dict(color=THEMES[st.session_state.theme]["bar_default"], line=dict(color=THEMES[st.session_state.theme]["bg"], width=0.5)),
    ))
    fig.update_layout(title=dict(text="Top 10 Genres", font=dict(size=14, color=THEMES[st.session_state.theme]["text"])), xaxis=dict(gridcolor=THEMES[st.session_state.theme]["grid"]), yaxis=dict(title=""), height=350, **get_plotly_layout(st.session_state.theme))
    return fig

def chart_rating_distribution(df: pd.DataFrame):
    rating_counts = df["rating"].dropna().value_counts().head(10).reset_index()
    rating_counts.columns = ["Rating", "Count"]
    fig = px.bar(rating_counts, x="Rating", y="Count", color_discrete_sequence=["#E50914"])
    fig.update_traces(marker_line_color=THEMES[st.session_state.theme]["bg"], marker_line_width=0.5)
    fig.update_layout(title=dict(text="Maturity Rating Distribution", font=dict(size=14, color=THEMES[st.session_state.theme]["text"])), xaxis=dict(title="", gridcolor="rgba(0,0,0,0)"), yaxis=dict(title="", gridcolor=THEMES[st.session_state.theme]["grid"]), bargap=0.2, height=350, **get_plotly_layout(st.session_state.theme))
    return fig

def chart_top_directors(df: pd.DataFrame):
    directors = df["director"].dropna().str.split(", ").explode()
    director_counts = directors.value_counts().head(10).sort_values(ascending=True).reset_index()
    director_counts.columns = ["Director", "Titles"]
    fig = go.Figure(go.Bar(
        x=director_counts["Titles"], y=director_counts["Director"], orientation="h",
        marker=dict(color=THEMES[st.session_state.theme]["bar_default"], line=dict(color=THEMES[st.session_state.theme]["bg"], width=0.5)),
    ))
    fig.update_layout(title=dict(text="Top 10 Directors", font=dict(size=14, color=THEMES[st.session_state.theme]["text"])), xaxis=dict(gridcolor=THEMES[st.session_state.theme]["grid"]), yaxis=dict(title=""), height=350, **get_plotly_layout(st.session_state.theme))
    return fig

def chart_runtime_distribution(df: pd.DataFrame):
    movies = df[(df["type"] == "Movie") & (df["duration_minutes"].notna())]
    fig = px.histogram(movies, x="duration_minutes", nbins=40, color_discrete_sequence=["#404040"])
    fig.update_traces(marker_line_color=THEMES[st.session_state.theme]["bg"], marker_line_width=0.5)
    fig.update_layout(title=dict(text="Movie Runtime Histogram", font=dict(size=14, color=THEMES[st.session_state.theme]["text"])), xaxis=dict(title="Duration (mins)", gridcolor=THEMES[st.session_state.theme]["grid"]), yaxis=dict(title="Frequency", gridcolor=THEMES[st.session_state.theme]["grid"]), bargap=0.06, height=350, clickmode="event+select", **get_plotly_layout(st.session_state.theme))
    return fig

# --- New Deep Dive Visualizations ---
def chart_top_countries_map(df: pd.DataFrame):
    country_counts = df["primary_country"].dropna().value_counts().reset_index()
    country_counts.columns = ["Country", "Titles"]
    fig = px.choropleth(
        country_counts, locations="Country", locationmode="country names", color="Titles",
        color_continuous_scale=[THEMES[st.session_state.theme]["bg"], "#F04438", "#7A271A"], labels={'Titles': 'Number of Titles'}
    )
    fig.update_layout(
        title=dict(text="Global Production Hubs", font=dict(size=14, color=THEMES[st.session_state.theme]["text"])),
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor=THEMES[st.session_state.theme]["border"], projection_type='equirectangular', bgcolor='rgba(0,0,0,0)'),
        height=400, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", clickmode="event+select"
    )
    return fig

def chart_top_cast(df: pd.DataFrame):
    cast_list = df["cast"].dropna().str.split(", ").explode()
    cast_counts = cast_list.value_counts().head(10).sort_values(ascending=True).reset_index()
    cast_counts.columns = ["Actor", "Titles"]
    fig = go.Figure(go.Bar(
        x=cast_counts["Titles"], y=cast_counts["Actor"], orientation="h",
        marker=dict(color="#E50914", line=dict(color=THEMES[st.session_state.theme]["bg"], width=0.5))
    ))
    fig.update_layout(title=dict(text="Top 10 Most Featured Actors", font=dict(size=14, color=THEMES[st.session_state.theme]["text"])), xaxis=dict(gridcolor=THEMES[st.session_state.theme]["grid"]), yaxis=dict(title=""), height=400, clickmode="event+select", **get_plotly_layout(st.session_state.theme))
    return fig

def chart_duration_scatter(df: pd.DataFrame):
    movies = df[(df["type"] == "Movie") & (df["duration_minutes"].notna()) & (df["release_year"] >= 1970)]
    avg_duration = movies.groupby("release_year")["duration_minutes"].mean().reset_index()
    
    fig = px.scatter(movies, x="release_year", y="duration_minutes", opacity=0.3, color_discrete_sequence=["#404040"])
    fig.add_trace(go.Scatter(x=avg_duration["release_year"], y=avg_duration["duration_minutes"], mode="lines+markers", marker=dict(size=6, color="#E50914"), line=dict(color="#E50914", width=3), name="Average Runtime"))
    fig.update_layout(title=dict(text="Movie Runtime Trends (Scatter + Average)", font=dict(size=14, color=THEMES[st.session_state.theme]["text"])), xaxis=dict(title="Release Year", gridcolor=THEMES[st.session_state.theme]["grid"]), yaxis=dict(title="Duration (mins)", gridcolor=THEMES[st.session_state.theme]["grid"]), height=400, clickmode="event+select", **get_plotly_layout(st.session_state.theme))
    return fig


# ══════════════════════════════════════════════════════════════════
#  MODULE 6: RECENT FEED & DATA EXPLORER
# ══════════════════════════════════════════════════════════════════

def render_recent_feed(df: pd.DataFrame):
    latest = df.sort_values("date_added", ascending=False).head(5)
    
    html = '<div style="display:flex; flex-direction:column; gap:16px;">'
    for _, row in latest.iterrows():
        date_str = row["date_added"].strftime("%B %d, %Y") if pd.notna(row["date_added"]) else "Unknown Date"
        desc = str(row["description"])[:140] + "..." if pd.notna(row["description"]) else ""
        html += f"""
<div style="border-left: 3px solid #E50914; padding-left: 16px;">
<div style="font-size: 0.75rem; color: {THEMES[st.session_state.theme]['text_muted']}; margin-bottom: 4px; font-weight: 500; text-transform: uppercase;">{date_str} &nbsp;&bull;&nbsp; {row['type']}</div>
<div style="font-size: 1.05rem; font-weight: 600; color: {THEMES[st.session_state.theme]['text']}; margin-bottom: 6px;">{row['title']} <span style="font-size:0.7rem; background:{THEMES[st.session_state.theme]['card']}; border:1px solid {THEMES[st.session_state.theme]['border']}; padding:2px 6px; border-radius:4px; margin-left:8px; color:{THEMES[st.session_state.theme]['text_muted']}; font-weight: 500;">{row['rating']}</span></div>
<div style="font-size: 0.85rem; color: {THEMES[st.session_state.theme]['text_muted']}; line-height: 1.5;">{desc}</div>
</div>
"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_catalog_explorer(df: pd.DataFrame):
    search_query = st.text_input("Search Titles, Directors, or Genres", placeholder="e.g. Sci-Fi, Christopher Nolan")
    if search_query:
        query_lower = search_query.lower()
        mask = (df["title"].str.lower().str.contains(query_lower, na=False) | df["director"].str.lower().str.contains(query_lower, na=False) | df["listed_in"].str.lower().str.contains(query_lower, na=False))
        search_results = df[mask]
    else:
        search_results = df

    display_cols = ["title", "type", "director", "country", "release_year", "rating", "duration", "listed_in"]
    display_df = search_results[[c for c in display_cols if c in search_results.columns]].reset_index(drop=True)

    st.caption(f"Showing {len(display_df):,} results")
    st.dataframe(display_df, use_container_width=True, height=500)

    csv_payload = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv_payload, file_name="netflix_export.csv", mime="text/csv", use_container_width=True)


# ══════════════════════════════════════════════════════════════════
#  MAIN APPLICATION ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def render_top_bar(df=None):
    if df is None:
        return
    
    total = len(df)
    movies = len(df[df["type"] == "Movie"])
    shows = len(df[df["type"] == "TV Show"])
    now = datetime.datetime.now().strftime("%H:%M UTC")
    user = st.session_state.get('user', '')
    user_status = f"User: {user}" if check_auth() else "Guest"
    
    st.markdown("""<img src="https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg" height="24" style="margin-bottom: 12px; margin-top: 12px;">""", unsafe_allow_html=True)
    
    c_theme, c1, c2, c3, c4 = st.columns([1.5, 2, 2, 2, 4])
    with c_theme:
        theme_icon = "🌞 Light Mode" if st.session_state.theme == "dark" else "🌙 Dark Mode"
        if st.button(theme_icon, use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
    with c1:
        if st.button(f"**{total:,}** Total", type="tertiary", use_container_width=True):
            st.session_state.popup_request = {"col": "type", "val": "", "match": "all"}
            st.session_state.popup_page = 0
    with c2:
        if st.button(f"**{movies:,}** Movies", type="tertiary", use_container_width=True):
            st.session_state.popup_request = {"col": "type", "val": "Movie", "match": "exact"}
            st.session_state.popup_page = 0
    with c3:
        if st.button(f"**{shows:,}** TV Shows", type="tertiary", use_container_width=True):
            st.session_state.popup_request = {"col": "type", "val": "TV Show", "match": "exact"}
            st.session_state.popup_page = 0
    with c4:
        st.markdown(f"<div style='text-align:right; color:#808080; padding-top:10px; font-size: 0.85rem;'>Last Sync: {now} | {user_status}</div>", unsafe_allow_html=True)


@st.dialog("Explore Data", width="large")
def show_data_popup(df, filter_col, filter_val, match_type="exact"):
    with st.spinner("Analyzing and retrieving data..."):
        if "page_size" not in st.session_state:
            st.session_state.page_size = 50
            
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.markdown(f"### Exploring: {filter_val if match_type != 'all' else 'All Content'}")
        with header_col2:
            st.session_state.page_size = st.selectbox("Items per page", options=[10, 50, 100, 500, 1000], index=[10, 50, 100, 500, 1000].index(st.session_state.page_size), label_visibility="collapsed")
            
        if match_type == "exact":
            display_df = df[df[filter_col].astype(str) == str(filter_val)]
        elif match_type == "contains":
            display_df = df[df[filter_col].astype(str).str.contains(str(filter_val), case=False, na=False)]
        elif match_type == "range":
            display_df = df[(df[filter_col] >= filter_val[0]) & (df[filter_col] <= filter_val[1])]
        elif match_type == "all":
            display_df = df
        
        PAGE_SIZE = st.session_state.page_size
        if "popup_page" not in st.session_state:
            st.session_state.popup_page = 0
            
        total_rows = len(display_df)
        total_pages = max(1, (total_rows + PAGE_SIZE - 1) // PAGE_SIZE)
        
        if st.session_state.popup_page >= total_pages:
            st.session_state.popup_page = 0
            
        start_idx = st.session_state.popup_page * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total_rows)
        
        st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_rows:,} matching titles")
        st.dataframe(display_df.iloc[start_idx:end_idx], use_container_width=True, height=400)
        
        col1, col2, col3, col4 = st.columns([1, 2, 1, 1.5])
        with col1:
            if st.button("⬅️ Previous", disabled=st.session_state.popup_page == 0, use_container_width=True):
                st.session_state.popup_page -= 1
        with col2:
            st.markdown(f"<div style='text-align: center; padding-top: 8px; color: {THEMES[st.session_state.theme]['text_muted']};'>Page {st.session_state.popup_page + 1} of {total_pages}</div>", unsafe_allow_html=True)
        with col3:
            if st.button("Next ➡️", disabled=st.session_state.popup_page >= total_pages - 1, use_container_width=True):
                st.session_state.popup_page += 1
        with col4:
            csv_payload = display_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Data", data=csv_payload, file_name=f"netflix_export_{filter_col}.csv", mime="text/csv", use_container_width=True)


def process_selection(event, chart_key, filter_col, extract_key="x", match_type="exact", is_range=False):
    if event and event.get("selection", {}).get("points"):
        pt = event["selection"]["points"][0]
        val = pt.get(extract_key)
        if val is None: val = pt.get("label", pt.get("x"))
        if is_range:
            val = float(pt.get("x", 0))
            if st.session_state.chart_selections.get(chart_key) != val:
                st.session_state.chart_selections[chart_key] = val
                st.session_state.popup_request = {"col": filter_col, "val": (val-5, val+5), "match": "range"}
                st.session_state.popup_page = 0
        else:
            if val is not None and st.session_state.chart_selections.get(chart_key) != str(val):
                st.session_state.chart_selections[chart_key] = str(val)
                st.session_state.popup_request = {"col": filter_col, "val": val, "match": match_type}
                st.session_state.popup_page = 0
    else:
        st.session_state.chart_selections[chart_key] = None

def main():
    if "demo_credentials" not in st.session_state:
        st.session_state.demo_credentials = {"admin": "admin123"}
    if "popup_request" not in st.session_state:
        st.session_state.popup_request = None
    if "chart_selections" not in st.session_state:
        st.session_state.chart_selections = {}

    if not check_auth():
        render_top_bar(None)
        render_login_screen()
        return

    df = load_and_preprocess_data()
    filtered_df = render_sidebar(df)
    render_top_bar(filtered_df)

    st.markdown(
        """
        <div class="main-title-container">
            <div class="main-title">Content Insights Engine</div>
        </div>
        <p class="main-description">
            Enterprise analytics dashboard. Adjust filters in the sidebar to explore streaming content trends.
        </p>
        """,
        unsafe_allow_html=True,
    )

    render_metric_cards(filtered_df)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABS IMPLEMENTATION ---
    tab1, tab2, tab3 = st.tabs(["Overview", "Content Deep Dive", "Data Explorer"])

    with tab1:
        st.markdown('<div class="section-header">High-Level Overview</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            ev1 = st.plotly_chart(chart_content_split(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev1, "tab1_split", "type", extract_key="x")
        with col2:
            ev2 = st.plotly_chart(chart_year_ingestion(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev2, "tab1_year", "year_added", extract_key="x")

        col3, col4 = st.columns(2, gap="large")
        with col3:
            ev3 = st.plotly_chart(chart_top_genres(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev3, "tab1_genres", "listed_in", extract_key="y", match_type="contains")
        with col4:
            ev4 = st.plotly_chart(chart_rating_distribution(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev4, "tab1_ratings", "rating", extract_key="x")
            
        ev5 = st.plotly_chart(chart_top_directors(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
        process_selection(ev5, "tab1_directors", "director", extract_key="y", match_type="contains")

    with tab2:
        st.markdown('<div class="section-header">Granular Analysis</div>', unsafe_allow_html=True)
        ev_m = st.plotly_chart(chart_top_countries_map(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
        process_selection(ev_m, "tab2_map", "primary_country", extract_key="location", match_type="contains")
        
        col_dd1, col_dd2 = st.columns(2, gap="large")
        with col_dd1:
            ev_c = st.plotly_chart(chart_top_cast(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev_c, "tab2_cast", "cast", extract_key="y", match_type="contains")
        with col_dd2:
            ev_d = st.plotly_chart(chart_duration_scatter(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev_d, "tab2_scatter", "release_year", extract_key="x")
            
        ev_r = st.plotly_chart(chart_runtime_distribution(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
        process_selection(ev_r, "tab2_histogram", "duration_minutes", is_range=True)

    with tab3:
        col_ex1, col_ex2 = st.columns([2, 1], gap="large")
        with col_ex1:
            st.markdown('<div class="section-header">Catalog Search & Export</div>', unsafe_allow_html=True)
            render_catalog_explorer(filtered_df)
        with col_ex2:
            st.markdown('<div class="section-header">Live Ingestion Feed</div>', unsafe_allow_html=True)
            render_recent_feed(filtered_df)

    st.markdown(
        f"""
        <div style="text-align: center; padding: 24px 0 12px; margin-top: 40px; border-top: 1px solid {THEMES[st.session_state.theme]['border']};">
            <span style="color: {THEMES[st.session_state.theme]['text_muted']}; font-size: 0.8rem;">
                Netflix Content Insights Engine &nbsp;|&nbsp; Enterprise Edition
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.popup_request:
        req = st.session_state.popup_request
        show_data_popup(filtered_df, req["col"], req["val"], req["match"])
        st.session_state.popup_request = None


if __name__ == "__main__":
    main()
