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
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ─── Root Theme Overrides ─── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #FFFFFF;
    }
    
    .stApp {
        background-color: #141414 !important;
    }

    /* ─── Hide default Streamlit chrome ─── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* ─── Top Bar ─── */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 56px;
        background-color: #141414;
        border-bottom: 1px solid #333333;
        z-index: 999999;
        display: flex;
        align-items: center;
        padding: 0 32px;
    }
    .top-bar-brand {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #E50914;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .top-bar-spacer {
        flex-grow: 1;
    }
    .top-bar-stats {
        margin-left: 32px;
        display: flex;
        gap: 16px;
        font-size: 0.85rem;
        color: #B3B3B3;
    }
    .top-bar-stats strong {
        color: #FFFFFF;
        font-weight: 600;
    }
    .top-bar-user {
        font-size: 0.85rem;
        color: #B3B3B3;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Push content down to account for top bar */
    .block-container {
        padding-top: 5rem !important;
    }
    .stApp > header {
        background: transparent !important;
        box-shadow: none !important;
        z-index: 9999999 !important;
    }

    /* ─── Metric Cards ─── */
    .metric-card {
        background: #141414;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 24px;
        text-align: left;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
        height: 100%;
    }
    
    .metric-card:hover {
        border-color: #404040;
        box-shadow: 0 4px 6px -1px rgba(16, 24, 40, 0.05), 0 2px 4px -1px rgba(16, 24, 40, 0.03);
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 600;
        color: #FFFFFF;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    
    .metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #808080;
    }
    
    .metric-subtext {
        font-size: 0.75rem;
        color: #404040;
        margin-top: 8px;
        font-weight: 400;
    }

    /* ─── Section Headers ─── */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #FFFFFF;
        padding-bottom: 12px;
        margin-top: 32px;
        margin-bottom: 24px;
        border-bottom: 1px solid #333333;
    }

    /* ─── Streamlit Tabs Styling ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        border-bottom: 2px solid #E50914 !important;
        color: #E50914 !important;
    }

    /* ─── Login Card ─── */
    .login-container {
        max-width: 400px;
        margin: 8vh auto;
        background: #141414;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 40px;
        box-shadow: 0 4px 6px -1px rgba(16, 24, 40, 0.05), 0 2px 4px -1px rgba(16, 24, 40, 0.03);
    }
    .login-title {
        text-align: left;
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 8px;
    }
    .login-subtitle {
        text-align: left;
        font-size: 0.9rem;
        color: #B3B3B3;
        margin-bottom: 32px;
        font-weight: 400;
    }
    .login-hint {
        text-align: left;
        font-size: 0.8rem;
        color: #808080;
        margin-top: 24px;
        padding: 16px;
        background: #000000;
        border-radius: 6px;
        border: 1px solid #333333;
    }
    .login-hint code {
        color: #E50914;
        background: #FEF3F2;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    [data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }

    /* ─── Sidebar Polish ─── */
    [data-testid="stSidebar"] {
        top: 56px !important;
        height: calc(100vh - 56px) !important;
        background: #000000 !important;
        border-right: 1px solid #333333;
    }
    /* Ensure the collapse/expand button is clearly visible below the top bar */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        top: 72px !important;
        left: 16px !important;
        z-index: 9999999 !important;
        background-color: #141414 !important;
        border: 1px solid #404040 !important;
        border-radius: 6px !important;
        box-shadow: 0 4px 6px rgba(16, 24, 40, 0.1) !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background-color: #141414;
        border: 1px solid #404040;
        color: #344054;
        font-weight: 500;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #F9FAFB;
        border-color: #404040;
        color: #FFFFFF;
    }

    /* ─── Dataframe ─── */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #333333;
    }

    /* ─── Download Button ─── */
    .stDownloadButton > button {
        background: #141414 !important;
        color: #344054 !important;
        border: 1px solid #404040 !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        font-size: 0.85rem !important;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05) !important;
    }
    .stDownloadButton > button:hover {
        background: #F9FAFB !important;
        color: #FFFFFF !important;
    }

    /* ─── Main Title ─── */
    .main-title-container {
        margin-bottom: 8px;
    }
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 600;
        color: #FFFFFF;
        line-height: 1.2;
    }
    .main-description {
        color: #B3B3B3;
        font-size: 1rem;
        margin-bottom: 32px;
        font-weight: 400;
        max-width: 800px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


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

DEMO_CREDENTIALS = {"admin": "admin123"}

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
            color: #FFFFFF;
            font-weight: 800;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        
        /* The Card */
        [data-testid="stForm"] {
            background-color: rgba(0, 0, 0, 0.85) !important;
            border: 1px solid #333333 !important;
            border-radius: 16px !important;
            padding: 48px !important;
            max-width: 450px !important;
            margin: 0 auto !important;
            box-shadow: 0 24px 48px rgba(0,0,0,0.6) !important;
            position: relative;
            z-index: 10;
            min-height: auto !important;
        }
        
        /* Labels */
        [data-testid="stForm"] label {
            display: block !important;
            font-size: 0.9rem !important;
            color: #B3B3B3 !important;
            font-weight: 500 !important;
            margin-bottom: 6px !important;
            text-transform: none !important;
        }
        
        /* Inputs */
        [data-testid="stForm"] input {
            background-color: #333333 !important;
            color: #FFFFFF !important;
            border: 1px solid #404040 !important;
            border-radius: 8px !important;
            padding: 14px 16px !important;
            font-size: 1rem !important;
            margin-bottom: 16px !important;
        }
        [data-testid="stForm"] input:focus {
            border-color: #E50914 !important;
            box-shadow: 0 0 0 1px #E50914 !important;
        }
        
        /* Pill Button */
        [data-testid="stForm"] .stButton > button {
            background-color: #E50914 !important;
            color: white !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
            padding: 14px !important;
            margin-top: 16px !important;
            width: 100% !important;
            border: none !important;
            font-size: 1.05rem !important;
            transition: background-color 0.2s;
        }
        [data-testid="stForm"] .stButton > button:hover {
            background-color: #C11119 !important;
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
            color: #B3B3B3;
            text-decoration: none;
            transition: color 0.2s;
        }
        .login-links a:hover {
            color: #FFFFFF;
            text-decoration: underline;
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
            username = st.text_input("Your email", placeholder="e.g. elon@tesla.com")
            password = st.text_input("Your password", type="password", placeholder="Password")
            submitted = st.form_submit_button("Sign In")
            
            st.markdown("""
                <div class="login-links">
                    <a href="#">Don't have an account?</a>
                    <a href="#">Forgot password?</a>
                </div>
            """, unsafe_allow_html=True)

            if submitted:
                if username in DEMO_CREDENTIALS and DEMO_CREDENTIALS[username] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = username
                    st.rerun()
                else:
                    st.error("Invalid credentials. Try admin / admin123")

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
    fig.add_trace(go.Scatter(x=x_series, y=y_series, mode='lines+markers', marker=dict(size=6, color="#FFFFFF"), fill='tozeroy', line_color='#E50914', fillcolor='rgba(229, 9, 20, 0.1)', line=dict(width=3)))
    fig.update_layout(
        title=dict(text=f"<span style='font-size:14px;color:#B3B3B3;font-family:Inter'>{title}</span>", x=0.10, y=0.85),
        annotations=[dict(text=f"<b style='font-size:28px;color:#FFFFFF;font-family:Inter'>{value}</b>", xref="paper", yref="paper", x=0.10, y=1.3, showarrow=False, xanchor="left", yanchor="top")],
        margin=dict(l=16, r=16, t=80, b=10),
        height=160,
        paper_bgcolor="#1A1A1A",
        plot_bgcolor="#1A1A1A",
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
        title=dict(text=f"<span style='font-size:14px;color:#B3B3B3;font-family:Inter'>{title}</span>", x=0.10, y=0.85),
        annotations=[dict(text=f"<b style='font-size:28px;color:#FFFFFF;font-family:Inter'>{value}</b>", xref="paper", yref="paper", x=0.10, y=1.3, showarrow=False, xanchor="left", yanchor="top")],
        margin=dict(l=16, r=16, t=80, b=10),
        height=160,
        paper_bgcolor="#1A1A1A",
        plot_bgcolor="#1A1A1A",
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        showlegend=False,
        bargap=0.2
    )
    return fig

def chart_kpi_donut(value, title, labels, values):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=values, text=labels, textposition='inside', insidetextfont=dict(color="#FFFFFF", size=14), marker_color=["#E50914", "#333333"], marker_line_width=0))
    fig.update_layout(
        title=dict(text=f"<span style='font-size:14px;color:#B3B3B3;font-family:Inter'>{title}</span>", x=0.10, y=0.85),
        annotations=[dict(text=f"<b style='font-size:28px;color:#FFFFFF;font-family:Inter'>{value}</b>", xref="paper", yref="paper", x=0.10, y=1.3, showarrow=False, xanchor="left", yanchor="top")],
        margin=dict(l=16, r=16, t=80, b=10),
        height=160,
        paper_bgcolor="#1A1A1A",
        plot_bgcolor="#1A1A1A",
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
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

PLOTLY_LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#B3B3B3", size=12),
    margin=dict(l=20, r=20, t=50, b=20),
    hoverlabel=dict(bgcolor="#141414", font_size=12, font_family="Inter, sans-serif", bordercolor="#333333"),
)

def chart_content_split(df: pd.DataFrame):
    type_counts = df["type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]
    fig = go.Figure(go.Bar(
        x=type_counts["Type"], y=type_counts["Count"],
        text=type_counts["Count"], textposition='auto',
        marker=dict(color=["#E50914", "#F04438"], line=dict(color="#141414", width=2)),
    ))
    fig.update_layout(title=dict(text="Content Distribution", font=dict(size=14, color="#FFFFFF")), showlegend=False, height=350, clickmode="event+select", **PLOTLY_LAYOUT_DEFAULTS)
    return fig

def chart_year_ingestion(df: pd.DataFrame):
    yearly = df["year_added"].dropna().astype(int).value_counts().sort_index().reset_index()
    yearly.columns = ["Year", "Titles Added"]
    fig = go.Figure(go.Scatter(
        x=yearly["Year"], y=yearly["Titles Added"], mode="lines+markers",
        line=dict(color="#E50914", width=2, shape="spline"), marker=dict(size=6, color="#FFFFFF"), fill="tozeroy", fillcolor="rgba(217, 45, 32, 0.05)",
    ))
    fig.update_layout(title=dict(text="Year-over-Year Ingestion", font=dict(size=14, color="#FFFFFF")), xaxis=dict(gridcolor="#333333", zeroline=False), yaxis=dict(gridcolor="#333333", zeroline=False), height=350, clickmode="event+select", **PLOTLY_LAYOUT_DEFAULTS)
    return fig

def chart_top_genres(df: pd.DataFrame):
    genres = df["listed_in"].dropna().str.split(", ").explode()
    genre_counts = genres.value_counts().head(10).sort_values(ascending=True).reset_index()
    genre_counts.columns = ["Genre", "Titles"]
    fig = go.Figure(go.Bar(
        x=genre_counts["Titles"], y=genre_counts["Genre"], orientation="h",
        marker=dict(color="#344054", line=dict(color="#141414", width=0.5)),
    ))
    fig.update_layout(title=dict(text="Top 10 Genres", font=dict(size=14, color="#FFFFFF")), xaxis=dict(gridcolor="#333333"), yaxis=dict(title=""), height=350, **PLOTLY_LAYOUT_DEFAULTS)
    return fig

def chart_rating_distribution(df: pd.DataFrame):
    rating_counts = df["rating"].dropna().value_counts().head(10).reset_index()
    rating_counts.columns = ["Rating", "Count"]
    fig = px.bar(rating_counts, x="Rating", y="Count", color_discrete_sequence=["#E50914"])
    fig.update_traces(marker_line_color="#141414", marker_line_width=0.5)
    fig.update_layout(title=dict(text="Maturity Rating Distribution", font=dict(size=14, color="#FFFFFF")), xaxis=dict(title="", gridcolor="rgba(0,0,0,0)"), yaxis=dict(title="", gridcolor="#333333"), bargap=0.2, height=350, **PLOTLY_LAYOUT_DEFAULTS)
    return fig

def chart_top_directors(df: pd.DataFrame):
    directors = df["director"].dropna().str.split(", ").explode()
    director_counts = directors.value_counts().head(10).sort_values(ascending=True).reset_index()
    director_counts.columns = ["Director", "Titles"]
    fig = go.Figure(go.Bar(
        x=director_counts["Titles"], y=director_counts["Director"], orientation="h",
        marker=dict(color="#808080", line=dict(color="#141414", width=0.5)),
    ))
    fig.update_layout(title=dict(text="Top 10 Directors", font=dict(size=14, color="#FFFFFF")), xaxis=dict(gridcolor="#333333"), yaxis=dict(title=""), height=350, **PLOTLY_LAYOUT_DEFAULTS)
    return fig

def chart_runtime_distribution(df: pd.DataFrame):
    movies = df[(df["type"] == "Movie") & (df["duration_minutes"].notna())]
    fig = px.histogram(movies, x="duration_minutes", nbins=40, color_discrete_sequence=["#404040"])
    fig.update_traces(marker_line_color="#141414", marker_line_width=0.5)
    fig.update_layout(title=dict(text="Movie Runtime Histogram", font=dict(size=14, color="#FFFFFF")), xaxis=dict(title="Duration (mins)", gridcolor="#333333"), yaxis=dict(title="Frequency", gridcolor="#333333"), bargap=0.06, height=350, clickmode="event+select", **PLOTLY_LAYOUT_DEFAULTS)
    return fig

# --- New Deep Dive Visualizations ---
def chart_top_countries_map(df: pd.DataFrame):
    country_counts = df["primary_country"].dropna().value_counts().reset_index()
    country_counts.columns = ["Country", "Titles"]
    fig = px.choropleth(
        country_counts, locations="Country", locationmode="country names", color="Titles",
        color_continuous_scale=["#000000", "#F04438", "#7A271A"], labels={'Titles': 'Number of Titles'}
    )
    fig.update_layout(
        title=dict(text="Global Production Hubs", font=dict(size=14, color="#FFFFFF")),
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#333333", projection_type='equirectangular', bgcolor='rgba(0,0,0,0)'),
        height=400, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", clickmode="event+select"
    )
    return fig

def chart_top_cast(df: pd.DataFrame):
    cast_list = df["cast"].dropna().str.split(", ").explode()
    cast_counts = cast_list.value_counts().head(10).sort_values(ascending=True).reset_index()
    cast_counts.columns = ["Actor", "Titles"]
    fig = go.Figure(go.Bar(
        x=cast_counts["Titles"], y=cast_counts["Actor"], orientation="h",
        marker=dict(color="#E50914", line=dict(color="#141414", width=0.5))
    ))
    fig.update_layout(title=dict(text="Top 10 Most Featured Actors", font=dict(size=14, color="#FFFFFF")), xaxis=dict(gridcolor="#333333"), yaxis=dict(title=""), height=400, clickmode="event+select", **PLOTLY_LAYOUT_DEFAULTS)
    return fig

def chart_duration_scatter(df: pd.DataFrame):
    movies = df[(df["type"] == "Movie") & (df["duration_minutes"].notna()) & (df["release_year"] >= 1970)]
    avg_duration = movies.groupby("release_year")["duration_minutes"].mean().reset_index()
    
    fig = px.scatter(movies, x="release_year", y="duration_minutes", opacity=0.3, color_discrete_sequence=["#404040"])
    fig.add_trace(go.Scatter(x=avg_duration["release_year"], y=avg_duration["duration_minutes"], mode="lines+markers", marker=dict(size=6, color="#E50914"), line=dict(color="#E50914", width=3), name="Average Runtime"))
    fig.update_layout(title=dict(text="Movie Runtime Trends (Scatter + Average)", font=dict(size=14, color="#FFFFFF")), xaxis=dict(title="Release Year", gridcolor="#333333"), yaxis=dict(title="Duration (mins)", gridcolor="#333333"), height=400, clickmode="event+select", **PLOTLY_LAYOUT_DEFAULTS)
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
<div style="font-size: 0.75rem; color: #808080; margin-bottom: 4px; font-weight: 500; text-transform: uppercase;">{date_str} &nbsp;&bull;&nbsp; {row['type']}</div>
<div style="font-size: 1.05rem; font-weight: 600; color: #FFFFFF; margin-bottom: 6px;">{row['title']} <span style="font-size:0.7rem; background:#000000; border:1px solid #333333; padding:2px 6px; border-radius:4px; margin-left:8px; color:#B3B3B3; font-weight: 500;">{row['rating']}</span></div>
<div style="font-size: 0.85rem; color: #B3B3B3; line-height: 1.5;">{desc}</div>
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
    
    c1, c2, c3, c4 = st.columns([2, 2, 2, 4])
    with c1:
        if st.button(f"**{total:,}** Total", type="tertiary", use_container_width=True):
            show_data_popup(df, "type", "", "all")
    with c2:
        if st.button(f"**{movies:,}** Movies", type="tertiary", use_container_width=True):
            show_data_popup(df, "type", "Movie", "exact")
    with c3:
        if st.button(f"**{shows:,}** TV Shows", type="tertiary", use_container_width=True):
            show_data_popup(df, "type", "TV Show", "exact")
    with c4:
        st.markdown(f"<div style='text-align:right; color:#808080; padding-top:10px; font-size: 0.85rem;'>Last Sync: {now} | {user_status}</div>", unsafe_allow_html=True)


@st.dialog("Explore Data", width="large")
def show_data_popup(df, filter_col, filter_val, match_type="exact"):
    st.markdown(f"### Exploring: {filter_val if match_type != 'all' else 'All Content'}")
    if match_type == "exact":
        display_df = df[df[filter_col].astype(str) == str(filter_val)]
    elif match_type == "contains":
        display_df = df[df[filter_col].astype(str).str.contains(str(filter_val), case=False, na=False)]
    elif match_type == "range":
        display_df = df[(df[filter_col] >= filter_val[0]) & (df[filter_col] <= filter_val[1])]
    elif match_type == "all":
        display_df = df
    
    st.caption(f"Showing {len(display_df):,} matching titles")
    st.dataframe(display_df, use_container_width=True, height=400)


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
        else:
            if val is not None and st.session_state.chart_selections.get(chart_key) != str(val):
                st.session_state.chart_selections[chart_key] = str(val)
                st.session_state.popup_request = {"col": filter_col, "val": val, "match": match_type}
    else:
        st.session_state.chart_selections[chart_key] = None

def main():
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
        """
        <div style="text-align: center; padding: 24px 0 12px; margin-top: 40px; border-top: 1px solid #333333;">
            <span style="color: #808080; font-size: 0.8rem;">
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
