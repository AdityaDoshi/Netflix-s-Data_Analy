import sqlite3
def hex_to_rgba(hex_color, alpha=0.1):
    hex_color = hex_color.lstrip('#')
    return f'rgba({int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}, {alpha})'



import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ══════════════════════════════════════════════════════════════════
#  GLOBAL CONFIGURATION & PAGE SETUP
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Netflix Insights",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS Injection ──

css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body { overflow-x: hidden !important; max-width: 100vw !important; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--text-color); }
    .stApp { background-color: var(--background-color) !important; overflow-x: hidden !important; }
    footer { visibility: hidden; }

    
    .block-container, div[data-testid="stAppViewBlockContainer"] { padding-top: 2.5rem !important; margin-top: 0rem !important; }
    .stApp > header { background: transparent !important; box-shadow: none !important; z-index: 9999999 !important; }

    .metric-card { background: var(--secondary-background-color); border: 1px solid var(--border-color, rgba(128,128,128,0.2)); border-radius: 8px; padding: 24px; text-align: left; transition: all 0.2s ease; box-shadow: 0 1px 2px rgba(0,0,0,0.1); height: 100%; }
    .metric-card:hover { border-color: var(--primary-color); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .metric-value { font-family: 'Bebas Neue', sans-serif; font-size: 3.2rem; font-weight: normal; color: var(--text-color); line-height: 1; letter-spacing: 1px; margin-bottom: 16px; text-shadow: 0px 2px 4px rgba(0,0,0,0.2); }
    .metric-label { font-size: 0.85rem; font-weight: 500; color: var(--text-color); opacity: 0.7; }
    .metric-subtext { font-size: 0.75rem; color: var(--text-color); opacity: 0.7; margin-top: 8px; font-weight: 400; }

    .section-header { font-family: 'Inter', sans-serif; font-size: 1.3rem; font-weight: 600; color: var(--text-color); padding-bottom: 12px; margin-top: 56px; margin-bottom: 32px; border-bottom: 1px solid var(--border-color, rgba(128,128,128,0.2)); letter-spacing: 0.5px; }

    [role="tablist"], [data-testid="stTabList"] { gap: 24px; }
    [data-testid="stTab"], [data-baseweb="tab"], button[role="tab"] { height: 48px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; color: var(--text-color) !important; opacity: 0.7; }
    [data-testid="stTab"] *, [data-baseweb="tab"] *, button[role="tab"] * { color: inherit !important; }
    [data-testid="stTab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"], button[role="tab"][aria-selected="true"] { background-color: transparent !important; border-bottom: 2px solid var(--primary-color) !important; color: var(--primary-color) !important; opacity: 1; }
    [data-testid="stTab"][aria-selected="true"] *, [data-baseweb="tab"][aria-selected="true"] *, button[role="tab"][aria-selected="true"] * { color: inherit !important; font-weight: 600 !important; }

    [data-testid="stSidebar"] { background: var(--secondary-background-color) !important; border-right: 1px solid var(--border-color, rgba(128,128,128,0.2)); }
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { z-index: 9999999 !important; background-color: var(--background-color) !important; border: 1px solid var(--border-color, rgba(128,128,128,0.2)) !important; border-radius: 6px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; }
    [data-testid="stSidebar"] .stButton > button { width: 100%; background-color: var(--background-color); border: 1px solid var(--border-color, rgba(128,128,128,0.2)); color: var(--text-color); font-weight: 500; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] .stButton > button:hover { background-color: var(--secondary-background-color); border-color: var(--primary-color); color: var(--text-color); }

    [data-testid="stStatusWidget"] { position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; background-color: rgba(128,128,128,0.2) !important; z-index: 9999999 !important; display: flex !important; align-items: center !important; justify-content: center !important; backdrop-filter: blur(2px) !important; }
    [data-testid="stStatusWidget"] > div { background-color: var(--secondary-background-color) !important; padding: 20px 40px !important; border-radius: 12px !important; border: 1px solid var(--border-color, rgba(128,128,128,0.2)) !important; box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important; transform: scale(1.5); }

    .stDataFrame { border-radius: 8px; overflow: hidden; border: 1px solid var(--border-color, rgba(128,128,128,0.2)); }

    .stDownloadButton > button { background: var(--background-color) !important; color: var(--text-color) !important; border: 1px solid var(--border-color, rgba(128,128,128,0.2)) !important; border-radius: 6px !important; padding: 10px 20px !important; font-weight: 500 !important; transition: all 0.2s ease !important; font-size: 0.85rem !important; box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important; }
    .stDownloadButton > button:hover { background: var(--secondary-background-color) !important; border-color: var(--primary-color) !important; color: var(--text-color) !important; }

    .main-title-container { margin-bottom: 8px; }
    .main-title { font-family: 'Bebas Neue', sans-serif; font-size: 4rem; font-weight: normal; letter-spacing: 2px; color: var(--primary-color); line-height: 1; text-transform: uppercase; text-shadow: none; }
    .main-description { color: var(--text-color); opacity: 0.7; font-size: 1rem; margin-bottom: 32px; font-weight: 400; max-width: 800px; }

    @media (max-width: 768px) {
        .main-title { font-size: 1.6rem !important; }
        .main-description { font-size: 0.9rem !important; }
        .metric-value { font-size: 1.8rem !important; }
        .metric-card { padding: 16px !important; }
        [role="tablist"], [data-testid="stTabList"] { gap: 8px !important; flex-wrap: wrap !important; }
        [data-testid="stTab"], [data-baseweb="tab"], button[role="tab"] { height: auto !important; padding-top: 8px !important; padding-bottom: 8px !important; font-size: 0.9rem !important; }
        .block-container, div[data-testid="stAppViewBlockContainer"] { padding-top: 4rem !important; }

    }

    /* Premium Refinements */
    
    /* Background animated glow */
    .stApp::before {{
        content: "";
        position: fixed;
        top: -10%; left: -10%; width: 120%; height: 120%;
        background-image: radial-gradient(circle at 20% 30%, var(--primary-color) 0%, transparent 20%),
                          radial-gradient(circle at 80% 70%, var(--primary-color) 0%, transparent 20%);
        opacity: 0.05;
        z-index: -1;
        pointer-events: none;
        animation: subtlePulse 8s infinite alternate;
    }}

    @keyframes subtlePulse {{
        0% {{ transform: scale(1); opacity: 0.03; }}
        100% {{ transform: scale(1.05); opacity: 0.08; }}
    }}

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-right: 1px solid var(--border-color, rgba(255, 255, 255, 0.05)) !important;
    }}
    
    /* Glowing active tabs */
    [data-testid="stTab"][aria-selected="true"] {{
        border-bottom: 3px solid var(--primary-color) !important;
        filter: drop-shadow(0 4px 6px var(--primary-color));
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateY(-2px);
    }}
    [data-testid="stTab"] {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    [data-testid="stTab"]:hover {{
        transform: translateY(-2px);
        color: var(--primary-color) !important;
    }}

    /* Static Title */
    .main-title {{
        position: relative;
        display: inline-block;
    }}

    /* Glassmorphism for containers and charts */
    .stDataFrame {{
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.05));
    }}

    /* Smooth Chart interactions */
    .js-plotly-plot .plotly .nsewdrag {{
        cursor: pointer;
    }}


    /* Glassmorphism for bordered containers (Cards) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{
        background: rgba(255, 255, 255, 0.06) !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }}

    /* Soften Buttons (Glassmorphic) */
    .stButton > button {{
        border-radius: 20px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    
    .stButton > button:hover {{
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px);
    }}

    /* SIMKL UI OVERHAUL */
    .simkl-card {{ position: relative; margin-bottom: 4px; }}
    .simkl-poster {{
        width: 100%; aspect-ratio: 2/3; border-radius: 8px; position: relative;
        overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.6); transition: transform 0.2s ease, box-shadow 0.2s ease;
        background-color: #1a1a1a;
    }}
    .simkl-poster:hover {{ transform: scale(1.04); box-shadow: 0 8px 20px rgba(0,0,0,0.8); z-index: 10; }}
    
    .simkl-badge {{
        position: absolute; background: rgba(0,0,0,0.85); color: white;
        padding: 4px 6px; font-size: 0.7rem; font-weight: 800; border-radius: 4px; z-index: 2;
        letter-spacing: 0.5px;
    }}
    .badge-top-right {{ top: 6px; right: 6px; border: 1px solid #444; color: #f5c518; }}
    .badge-top-left {{ top: 6px; left: 6px; background: #e50914; }}

    .simkl-overlay {{
        position: absolute; bottom: 0; left: 0; right: 0; top: 0;
        background: rgba(15,15,15,0.9); display: flex; flex-direction: column;
        justify-content: center; align-items: center; opacity: 0; transition: opacity 0.2s ease;
        padding: 8px; text-align: center; border-radius: 8px;
    }}
    .simkl-poster:hover .simkl-overlay {{ opacity: 1; backdrop-filter: blur(2px); }}
    
    .simkl-genres {{ color: #aaa; font-size: 0.75rem; margin-bottom: 8px; font-weight: 500; line-height: 1.4; }}
    .simkl-duration {{ color: #fff; font-size: 0.85rem; font-weight: 700; border-top: 1px solid #333; padding-top: 8px; width: 80%; }}
    
    .simkl-title {{
        font-weight: 700; font-size: 0.9rem; margin-top: 8px; margin-bottom: 4px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff;
    }}
    .simkl-btn-container {{ margin-top: 4px; }}

</style>
"""



LANG = {
    "English": {
        "language_selector": "Language", "logged_in_as": "Logged in as", "ui_theme": "UI Theme", "log_out": "Log Out",
        "filter_controls": "Filter Controls", "release_year": "Release Year Range", "content_type": "Content Type",
        "movie": "Movie", "tv_show": "TV Show", "maturity_rating": "Maturity Rating", "choose_options": "Choose options",
        "production_country": "Production Country", "main_title": "Content Insights Engine",
        "main_desc": "Enterprise analytics dashboard. Adjust filters in the sidebar to explore streaming content trends.",
        "tab_overview": "Overview", "tab_deep_dive": "Content Deep Dive", "tab_data": "Data Explorer",
        "tab_ai": "🤖 AI Recommender", "tab_cast_network": "🎭 Cast Network",
        "ai_desc": "Describe what you want to watch in natural language, and our AI will find the best matches based on plot descriptions!",
        "ai_search_prompt": "🔍 Search query...", "ai_search_placeholder": "e.g., A spooky detective movie with a twist ending",
        "ai_no_match": "No matches found. Try describing it differently!",
        "header_trend": "Content Release Trend", "header_dist": "Content Distribution", "header_ratings": "Ratings & Directors",
        "header_granular": "Granular Analysis", "download_csv": "Download CSV", "header_trend": "Content Release Trend (10 Years)", "header_dist": "Distribution & Genres", "header_ratings": "Ratings & Directors", "header_granular": "Granular Analysis", "dataset_info": "Dataset Info", "source": "Source", "total_records": "Total Records", "year_span": "Year Span", "view_mode_label": "View Mode", "grid_mode": "Grid", "csv_mode": "CSV", "btn_cast": "🎭 Cast", "btn_trailer": "▶ Trailer", "watch_netflix": "▶ Watch on Netflix", "btn_netflix": "Netflix", "btn_where": "Where?", "title_search_netflix": "Search on Netflix", "title_find_justwatch": "Find on JustWatch",
        "metric_total": "Total Content", "metric_movies": "Total Movies", "metric_shows": "Total TV Shows",
        "metric_directors": "Total Directors", "metric_cast": "Unique Cast", "metric_countries": "Countries",
        "metric_genres": "Unique Genres", "metric_type": "Content Type",
        "chart_distribution": "Content Distribution", "chart_yoy": "Year-over-Year Ingestion", "chart_genres": "Top 10 Genres",
        "chart_rating": "Maturity Rating Distribution", "chart_directors": "Top 10 Directors", "chart_map": "Global Content Map",
        "chart_title_release_trend": "Content Release Trend (10 Years)", "chart_title_split": "Content Type Split",
        "chart_title_genres": "Top 10 Genres by Volume", "chart_title_rating": "Maturity Rating Distribution",
        "chart_title_directors": "Top 10 Directors by Volume", "chart_title_map": "Global Content Production Heatmap",
        "chart_title_actors": "Top 10 Most Featured Actors", "chart_title_scatter": "Movie Runtime Trends (Scatter + Average)",
        "chart_title_histogram": "Movie Runtime Histogram", "axis_frequency": "Frequency", "legend_avg_runtime": "Average Runtime",
        "titles": "Titles", "year": "Year", "count": "Count", "rating": "Rating", "actor": "Actor", "duration_minutes": "Duration (min)",
        "cat_search_prompt": "Search Titles, Directors, or Genres", "cat_search_placeholder": "e.g. Sci-Fi, Christopher Nolan",
        "cat_showing_results": "Showing {0:,} results", "cat_header": "Catalog Search & Export",
        "feed_header": "Live Ingestion Feed", "feed_unknown": "Unknown Date",
        "col_title": "Title", "col_type": "Type", "col_director": "Director", "col_country": "Country",
        "col_year": "Release Year", "col_rating": "Rating", "col_duration": "Duration", "col_genres": "Genres",
        "cast_search_prompt": "Search for an actor...", "cast_search_btn": "Search Actor", "cast_back": "Go Back",
        "cast_total_titles": "Total Titles", "cast_filmography": "Filmography", "cast_costars": "Frequent Co-Stars",
        "cast_no_costars": "No co-stars found.",
        "dataset_info": "Dataset Information", "total_records": "Total Records",
        "cast_go_back": "Go Back", "cast_search_placeholder": "e.g., Leonardo DiCaprio", "director": "Director", "genre": "Genre", "items_per_page": "Items per page", "year_added": "Year Added"
    },
    "Gujarati": {
        "language_selector": "ભાષા", "logged_in_as": "લૉગ ઇન થયેલ છે", "ui_theme": "UI થીમ", "log_out": "લૉગ આઉટ",
        "filter_controls": "ફિલ્ટર નિયંત્રણો", "release_year": "પ્રકાશન વર્ષ શ્રેણી", "content_type": "સામગ્રી પ્રકાર",
        "movie": "ચલચિત્ર", "tv_show": "ટીવી શો", "maturity_rating": "પરિપક્વતા રેટિંગ", "choose_options": "વિકલ્પો પસંદ કરો",
        "production_country": "ઉત્પાદન દેશ", "main_title": "કન્ટેન્ટ ઇનસાઇટ્સ એન્જિન",
        "main_desc": "એન્ટરપ્રાઇઝ એનાલિટિક્સ ડેશબોર્ડ. સ્ટ્રીમિંગ સામગ્રી વલણોનું અન્વેષણ કરવા માટે સાઇડબારમાં ફિલ્ટર્સને સમાયોજિત કરો.",
        "tab_overview": "ઝાંખી", "tab_deep_dive": "ડીપ ડાઇવ", "tab_data": "ડેટા એક્સપ્લોરર",
        "tab_ai": "🤖 AI ભલામણકર્તા", "tab_cast_network": "🎭 કાસ્ટ નેટવર્ક",
        "ai_desc": "તમે કુદરતી ભાષામાં શું જોવા માંગો છો તેનું વર્ણન કરો, અને અમારું AI પ્લોટ વર્ણનોના આધારે શ્રેષ્ઠ મેચ શોધશે!",
        "ai_search_prompt": "🔍 શોધ ક્વેરી...", "ai_search_placeholder": "દા.ત., ટ્વિસ્ટ એન્ડિંગ સાથેની ડરામણી ડિટેક્ટીવ ફિલ્મ",
        "ai_no_match": "કોઈ મેળ મળ્યો નથી. તેનું અલગ રીતે વર્ણન કરવાનો પ્રયાસ કરો!",
        "header_trend": "સામગ્રી પ્રકાશન વલણ", "header_dist": "સામગ્રી વિતરણ", "header_ratings": "રેટિંગ્સ અને ડિરેક્ટર્સ",
        "header_granular": "દાણાદાર વિશ્લેષણ", "download_csv": "CSV ડાઉનલોડ કરો",
        "metric_total": "કુલ સામગ્રી", "metric_movies": "કુલ ચલચિત્રો", "metric_shows": "કુલ ટીવી શો",
        "metric_directors": "કુલ દિગ્દર્શકો", "metric_cast": "અનન્ય કાસ્ટ", "metric_countries": "દેશો",
        "metric_genres": "અનન્ય શૈલીઓ", "metric_type": "સામગ્રી પ્રકાર",
        "chart_distribution": "સામગ્રી વિતરણ", "chart_yoy": "વર્ષ-દર-વર્ષ ઇન્જેશન", "chart_genres": "ટોચની 10 શૈલીઓ",
        "chart_rating": "પરિપક્વતા રેટિંગ વિતરણ", "chart_directors": "ટોચના 10 દિગ્દર્શકો", "chart_map": "વૈશ્વિક સામગ્રી નકશો",
        "chart_title_release_trend": "સામગ્રી પ્રકાશન વલણ (10 વર્ષ)", "chart_title_split": "સામગ્રી પ્રકાર વિભાજન",
        "chart_title_genres": "વોલ્યુમ દ્વારા ટોચની 10 શૈલીઓ", "chart_title_rating": "પરિપક્વતા રેટિંગ વિતરણ",
        "chart_title_directors": "વોલ્યુમ દ્વારા ટોચના 10 દિગ્દર્શકો", "chart_title_map": "વૈશ્વિક સામગ્રી ઉત્પાદન હીટમેપ",
        "chart_title_actors": "ટોચના 10 સૌથી વધુ દર્શાવવામાં આવેલ કલાકારો", "chart_title_scatter": "મૂવી રનટાઇમ વલણો (સ્કેટર + એવરેજ)",
        "chart_title_histogram": "મૂવી રનટાઇમ હિસ્ટોગ્રામ", "axis_frequency": "આવર્તન", "legend_avg_runtime": "સરેરાશ રનટાઇમ",
        "titles": "શીર્ષકો", "year": "વર્ષ", "count": "ગણતરી", "rating": "રેટિંગ", "actor": "અભિનેતા", "duration_minutes": "સમયગાળો (મિનિટ)",
        "cat_search_prompt": "શીર્ષકો, દિગ્દર્શકો અથવા શૈલીઓ શોધો", "cat_search_placeholder": "દા.ત. સાય-ફાઇ, ક્રિસ્ટોફર નોલાન",
        "cat_showing_results": "{0:,} પરિણામો બતાવી રહ્યાં છીએ", "cat_header": "કેટલોગ શોધ અને નિકાસ",
        "feed_header": "લાઇવ ઇન્જેશન ફીડ", "feed_unknown": "અજ્ઞાત તારીખ",
        "col_title": "શીર્ષક", "col_type": "પ્રકાર", "col_director": "દિગ્દર્શક", "col_country": "દેશ",
        "col_year": "પ્રકાશન વર્ષ", "col_rating": "રેટિંગ", "col_duration": "સમયગાળો", "col_genres": "શૈલીઓ",
        "cast_search_prompt": "અભિનેતા માટે શોધો...", "cast_search_btn": "અભિનેતા શોધો", "cast_back": "પાછા જાઓ",
        "cast_total_titles": "કુલ શીર્ષકો", "cast_filmography": "ફિલ્મોગ્રાફી", "cast_costars": "વારંવાર સહ-કલાકારો",
        "cast_no_costars": "કોઈ સહ-કલાકારો મળ્યા નથી.",
        "dataset_info": "ડેટાસેટ માહિતી", "total_records": "કુલ રેકોર્ડ્સ",
        "cast_go_back": "પાછા જાઓ", "cast_search_placeholder": "દા.ત., લિયોનાર્ડો ડી કેપ્રિયો", "director": "દિગ્દર્શક", "genre": "શૈલી", "items_per_page": "પૃષ્ઠ દીઠ આઇટમ્સ", "year_added": "વર્ષ ઉમેરાયું"
    },
    "Hindi": {
        "language_selector": "भाषा", "logged_in_as": "लॉग इन किया है", "ui_theme": "यूआई थीम", "log_out": "लॉग आउट",
        "filter_controls": "फ़िल्टर नियंत्रण", "release_year": "रिलीज़ वर्ष सीमा", "content_type": "सामग्री प्रकार",
        "movie": "फ़िल्म", "tv_show": "टीवी शो", "maturity_rating": "परिपक्वता रेटिंग", "choose_options": "विकल्प चुनें",
        "production_country": "उत्पादन देश", "main_title": "कंटेंट इनसाइट्स इंजन",
        "main_desc": "एंटरप्राइज़ एनालिटिक्स डैशबोर्ड। स्ट्रीमिंग सामग्री रुझानों का पता लगाने के लिए साइडबार में फ़िल्टर समायोजित करें।",
        "tab_overview": "अवलोकन", "tab_deep_dive": "डीप डाइव", "tab_data": "डेटा एक्सप्लोरर",
        "tab_ai": "🤖 एआई अनुशंसाकर्ता", "tab_cast_network": "🎭 कास्ट नेटवर्क",
        "ai_desc": "वर्णन करें कि आप प्राकृतिक भाषा में क्या देखना चाहते हैं, और हमारा एआई कथानक विवरण के आधार पर सर्वोत्तम मिलान ढूंढेगा!",
        "ai_search_prompt": "🔍 खोज क्वेरी...", "ai_search_placeholder": "उदा., ट्विस्ट एंडिंग के साथ एक डरावनी जासूसी फिल्म",
        "ai_no_match": "कोई मेल नहीं मिला। इसका अलग तरह से वर्णन करने का प्रयास करें!",
        "header_trend": "सामग्री रिलीज़ रुझान", "header_dist": "सामग्री वितरण", "header_ratings": "रेटिंग और निर्देशक",
        "header_granular": "दानेदार विश्लेषण", "download_csv": "CSV डाउनलोड करें",
        "metric_total": "कुल सामग्री", "metric_movies": "कुल फ़िल्में", "metric_shows": "कुल टीवी शो",
        "metric_directors": "कुल निर्देशक", "metric_cast": "अद्वितीय कास्ट", "metric_countries": "देश",
        "metric_genres": "अद्वितीय शैलियां", "metric_type": "सामग्री का प्रकार",
        "chart_distribution": "सामग्री वितरण", "chart_yoy": "वर्ष-दर-वर्ष इंजेशन", "chart_genres": "शीर्ष 10 शैलियाँ",
        "chart_rating": "परिपक्वता रेटिंग वितरण", "chart_directors": "शीर्ष 10 निर्देशक", "chart_map": "वैश्विक सामग्री मानचित्र",
        "chart_title_release_trend": "सामग्री रिलीज़ रुझान (10 वर्ष)", "chart_title_split": "सामग्री प्रकार विभाजन",
        "chart_title_genres": "मात्रा के आधार पर शीर्ष 10 शैलियाँ", "chart_title_rating": "परिपक्वता रेटिंग वितरण",
        "chart_title_directors": "मात्रा के आधार पर शीर्ष 10 निर्देशक", "chart_title_map": "वैश्विक सामग्री उत्पादन हीटमैप",
        "chart_title_actors": "शीर्ष 10 सबसे अधिक प्रदर्शित अभिनेता", "chart_title_scatter": "मूवी रनटाइम रुझान (स्कैटर + औसत)",
        "chart_title_histogram": "मूवी रनटाइम हिस्टोग्राम", "axis_frequency": "आवृत्ति", "legend_avg_runtime": "औसत रनटाइम",
        "titles": "शीर्षक", "year": "वर्ष", "count": "गिनती", "rating": "रेटिंग", "actor": "अभिनेता", "duration_minutes": "अवधि (मिनट)",
        "cat_search_prompt": "शीर्षक, निर्देशक या शैलियां खोजें", "cat_search_placeholder": "उदा. साई-फाई, क्रिस्टोफर नोलन",
        "cat_showing_results": "{0:,} परिणाम दिखा रहे हैं", "cat_header": "कैटलॉग खोज और निर्यात",
        "feed_header": "लाइव इंजेशन फ़ीड", "feed_unknown": "अज्ञात तिथि",
        "col_title": "शीर्षक", "col_type": "प्रकार", "col_director": "निर्देशक", "col_country": "देश",
        "col_year": "रिलीज़ वर्ष", "col_rating": "रेटिंग", "col_duration": "अवधि", "col_genres": "शैलियां",
        "cast_search_prompt": "किसी अभिनेता को खोजें...", "cast_search_btn": "अभिनेता खोजें", "cast_back": "वापस जाएं",
        "cast_total_titles": "कुल शीर्षक", "cast_filmography": "फिल्मोग्राफी", "cast_costars": "लगातार सह-कलाकार",
        "cast_no_costars": "कोई सह-कलाकार नहीं मिला।",
        "dataset_info": "डेटासेट जानकारी", "total_records": "कुल रिकॉर्ड",
        "cast_go_back": "वापस जाएं", "cast_search_placeholder": "उदा., लियोनार्डो डिकैप्रियो", "director": "निर्देशक", "genre": "शैली", "items_per_page": "प्रति पृष्ठ आइटम", "year_added": "वर्ष जोड़ा गया"
    },
    "Spanish": {
        "language_selector": "Idioma", "logged_in_as": "Conectado como", "ui_theme": "Tema de UI", "log_out": "Cerrar sesión",
        "filter_controls": "Controles de Filtro", "release_year": "Rango de Año de Lanzamiento", "content_type": "Tipo de Contenido",
        "movie": "Película", "tv_show": "Programa de TV", "maturity_rating": "Clasificación por Madurez", "choose_options": "Elige opciones",
        "production_country": "País de Producción", "main_title": "Motor de Insights de Contenido",
        "main_desc": "Panel de análisis empresarial. Ajusta los filtros en la barra lateral para explorar las tendencias de contenido de transmisión.",
        "tab_overview": "Visión general", "tab_deep_dive": "Análisis Profundo", "tab_data": "Explorador de Datos",
        "tab_ai": "🤖 Recomendador AI", "tab_cast_network": "🎭 Red de Reparto",
        "ai_desc": "¡Describe lo que quieres ver en lenguaje natural y nuestra IA encontrará las mejores coincidencias según las descripciones de la trama!",
        "ai_search_prompt": "🔍 Consulta de búsqueda...", "ai_search_placeholder": "ej., Una película de detectives espeluznante con un final inesperado",
        "ai_no_match": "No se encontraron coincidencias. ¡Intenta describirlo de manera diferente!",
        "header_trend": "Tendencia de Lanzamiento de Contenido", "header_dist": "Distribución de Contenido", "header_ratings": "Clasificaciones y Directores",
        "header_granular": "Análisis Granular", "download_csv": "Descargar CSV", "header_trend": "Tendencia de lanzamientos (10 Años)", "header_dist": "Distribución y Géneros", "header_ratings": "Calificaciones y Directores", "header_granular": "Análisis Granular", "dataset_info": "Info del Dataset", "source": "Fuente", "total_records": "Registros Totales", "year_span": "Lapso de Años", "view_mode_label": "Modo de vista", "grid_mode": "Cuadrícula", "csv_mode": "CSV", "btn_cast": "🎭 Reparto", "btn_trailer": "▶ Tráiler", "watch_netflix": "▶ Ver en Netflix", "btn_netflix": "Netflix", "btn_where": "¿Dónde?", "title_search_netflix": "Buscar en Netflix", "title_find_justwatch": "Buscar en JustWatch",
        "metric_total": "Contenido Total", "metric_movies": "Películas Totales", "metric_shows": "Programas de TV Totales",
        "metric_directors": "Directores Totales", "metric_cast": "Elenco Único", "metric_countries": "Países",
        "metric_genres": "Géneros Únicos", "metric_type": "Tipo de Contenido",
        "chart_distribution": "Distribución de Contenido", "chart_yoy": "Ingestión Año tras Año", "chart_genres": "Top 10 Géneros",
        "chart_rating": "Distribución de Clasificación por Madurez", "chart_directors": "Top 10 Directores", "chart_map": "Mapa de Contenido Global",
        "chart_title_release_trend": "Tendencia de Lanzamiento de Contenido (10 Años)", "chart_title_split": "División por Tipo de Contenido",
        "chart_title_genres": "Top 10 Géneros por Volumen", "chart_title_rating": "Distribución de Clasificación por Madurez",
        "chart_title_directors": "Top 10 Directores por Volumen", "chart_title_map": "Mapa de Calor Global de Producción de Contenido",
        "chart_title_actors": "Top 10 Actores Más Destacados", "chart_title_scatter": "Tendencias de Duración de Películas (Dispersión + Promedio)",
        "chart_title_histogram": "Histograma de Duración de Películas", "axis_frequency": "Frecuencia", "legend_avg_runtime": "Duración Promedio",
        "titles": "Títulos", "year": "Año", "count": "Recuento", "rating": "Clasificación", "actor": "Actor", "duration_minutes": "Duración (min)",
        "cat_search_prompt": "Buscar Títulos, Directores o Géneros", "cat_search_placeholder": "ej. Ciencia Ficción, Christopher Nolan",
        "cat_showing_results": "Mostrando {0:,} resultados", "cat_header": "Búsqueda y Exportación",
        "feed_header": "Feed de Ingestión en Vivo", "feed_unknown": "Fecha Desconocida",
        "col_title": "Título", "col_type": "Tipo", "col_director": "Director", "col_country": "País",
        "col_year": "Año de Lanzamiento", "col_rating": "Clasificación", "col_duration": "Duración", "col_genres": "Géneros",
        "cast_search_prompt": "Buscar un actor...", "cast_search_btn": "Buscar Actor", "cast_back": "Regresar",
        "cast_total_titles": "Títulos Totales", "cast_filmography": "Filmografía", "cast_costars": "Coprotagonistas Frecuentes",
        "cast_no_costars": "No se encontraron coprotagonistas.",
        "dataset_info": "Información del Conjunto de Datos", "total_records": "Registros Totales",
        "cast_go_back": "Regresar", "cast_search_placeholder": "ej., Leonardo DiCaprio", "director": "Director", "genre": "Género", "items_per_page": "Artículos por página", "year_added": "Año Agregado"
    }
}

if "lang" not in st.session_state:
    st.session_state.lang = "English"

T = LANG[st.session_state.lang]


THEMES = {
    "Netflix Dark (Default)": {"bg_color": "#141414", "sec_bg_color": "#000000", "text_color": "#FFFFFF", "border_color": "rgba(255,255,255,0.1)", "primary_color": "#E50914", "base": "dark"},
    "Netflix Light": {"bg_color": "#F9FAFB", "sec_bg_color": "#FFFFFF", "text_color": "#111827", "border_color": "rgba(0,0,0,0.1)", "primary_color": "#E50914", "base": "light"},
    "Sunset Orange": {"bg_color": "#FFFBF0", "sec_bg_color": "#FFFFFF", "text_color": "#431407", "border_color": "rgba(0,0,0,0.1)", "primary_color": "#F97316", "base": "light"},
    "Neon Pink": {"bg_color": "#FDF2F8", "sec_bg_color": "#FFFFFF", "text_color": "#831843", "border_color": "rgba(236,72,153,0.3)", "primary_color": "#DB2777", "base": "light"}
}

if "theme" not in st.session_state:
    st.session_state.theme = "Netflix Dark (Default)"

current_theme = THEMES.get(st.session_state.theme, THEMES["Netflix Dark (Default)"])
bg_color = current_theme["bg_color"]
sec_bg_color = current_theme["sec_bg_color"]
text_color = current_theme["text_color"]
border_color = current_theme["border_color"]
theme_primary = current_theme["primary_color"]

def get_netflix_logo_svg(height="40px", style=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" height="{height}" style="{style}" viewBox="0 0 1024 276.742"><path d="M140.803 258.904c-15.404 2.705-31.079 3.516-47.294 5.676l-49.458-144.856v151.073c-15.404 1.621-29.457 3.783-44.051 5.945v-276.742h41.08l56.212 157.021v-157.021h43.511v258.904zm85.131-157.558c16.757 0 42.431-.811 57.835-.811v43.24c-19.189 0-41.619 0-57.835.811v64.322c25.405-1.621 50.809-3.785 76.482-4.596v41.617l-119.724 9.461v-255.39h119.724v43.241h-76.482v58.105zm237.284-58.104h-44.862v198.908c-14.594 0-29.188 0-43.239.539v-199.447h-44.862v-43.242h132.965l-.002 43.242zm70.266 55.132h59.187v43.24h-59.187v98.104h-42.433v-239.718h120.808v43.241h-78.375v55.133zm148.641 103.507c24.594.539 49.456 2.434 73.51 3.783v42.701c-38.646-2.434-77.293-4.863-116.75-5.676v-242.689h43.24v201.881zm109.994 49.457c13.783.812 28.377 1.623 42.43 3.242v-254.58h-42.43v251.338zm231.881-251.338l-54.863 131.615 54.863 145.127c-16.217-2.162-32.432-5.135-48.648-7.838l-31.078-79.994-31.617 73.51c-15.678-2.705-30.812-3.516-46.484-5.678l55.672-126.75-50.269-129.992h46.482l28.377 72.699 30.27-72.699h47.295z" fill="{theme_primary}"/></svg>'''


root_css = f"""
<style>
:root {{
    --background-color: {bg_color};
    --secondary-background-color: {sec_bg_color};
    --text-color: {text_color};
    --border-color: {border_color};
    --primary-color: {theme_primary};
}}

    /* Premium Refinements */
    
    /* Background animated glow */
    .stApp::before {{
        content: "";
        position: fixed;
        top: -10%; left: -10%; width: 120%; height: 120%;
        background-image: radial-gradient(circle at 20% 30%, var(--primary-color) 0%, transparent 20%),
                          radial-gradient(circle at 80% 70%, var(--primary-color) 0%, transparent 20%);
        opacity: 0.05;
        z-index: -1;
        pointer-events: none;
        animation: subtlePulse 8s infinite alternate;
    }}

    @keyframes subtlePulse {{
        0% {{ transform: scale(1); opacity: 0.03; }}
        100% {{ transform: scale(1.05); opacity: 0.08; }}
    }}

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-right: 1px solid var(--border-color, rgba(255, 255, 255, 0.05)) !important;
    }}
    
    /* Glowing active tabs */
    [data-testid="stTab"][aria-selected="true"] {{
        border-bottom: 3px solid var(--primary-color) !important;
        filter: drop-shadow(0 4px 6px var(--primary-color));
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateY(-2px);
    }}
    [data-testid="stTab"] {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    [data-testid="stTab"]:hover {{
        transform: translateY(-2px);
        color: var(--primary-color) !important;
    }}

    /* Static Title */
    .main-title {{
        position: relative;
        display: inline-block;
    }}

    /* Glassmorphism for containers and charts */
    .stDataFrame {{
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.05));
    }}

    /* Smooth Chart interactions */
    .js-plotly-plot .plotly .nsewdrag {{
        cursor: pointer;
    }}


    /* Glassmorphism for bordered containers (Cards) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{
        background: rgba(255, 255, 255, 0.06) !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }}

    /* Soften Buttons (Glassmorphic) */
    .stButton > button {{
        border-radius: 20px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    
    .stButton > button:hover {{
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px);
    }}

    /* SIMKL UI OVERHAUL */
    .simkl-card {{ position: relative; margin-bottom: 4px; }}
    .simkl-poster {{
        width: 100%; aspect-ratio: 2/3; border-radius: 8px; position: relative;
        overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.6); transition: transform 0.2s ease, box-shadow 0.2s ease;
        background-color: #1a1a1a;
    }}
    .simkl-poster:hover {{ transform: scale(1.04); box-shadow: 0 8px 20px rgba(0,0,0,0.8); z-index: 10; }}
    
    .simkl-badge {{
        position: absolute; background: rgba(0,0,0,0.85); color: white;
        padding: 4px 6px; font-size: 0.7rem; font-weight: 800; border-radius: 4px; z-index: 2;
        letter-spacing: 0.5px;
    }}
    .badge-top-right {{ top: 6px; right: 6px; border: 1px solid #444; color: #f5c518; }}
    .badge-top-left {{ top: 6px; left: 6px; background: #e50914; }}

    .simkl-overlay {{
        position: absolute; bottom: 0; left: 0; right: 0; top: 0;
        background: rgba(15,15,15,0.9); display: flex; flex-direction: column;
        justify-content: center; align-items: center; opacity: 0; transition: opacity 0.2s ease;
        padding: 8px; text-align: center; border-radius: 8px;
    }}
    .simkl-poster:hover .simkl-overlay {{ opacity: 1; backdrop-filter: blur(2px); }}
    
    .simkl-genres {{ color: #aaa; font-size: 0.75rem; margin-bottom: 8px; font-weight: 500; line-height: 1.4; }}
    .simkl-duration {{ color: #fff; font-size: 0.85rem; font-weight: 700; border-top: 1px solid #333; padding-top: 8px; width: 80%; }}
    
    .simkl-title {{
        font-weight: 700; font-size: 0.9rem; margin-top: 8px; margin-bottom: 4px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff;
    }}
    .simkl-btn-container {{ margin-top: 4px; }}

</style>
"""
st.markdown(root_css + css, unsafe_allow_html=True)

import os
def update_theme_config(theme_name):
    config_path = ".streamlit/config.toml"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    t = THEMES.get(theme_name, THEMES["Netflix Dark (Default)"])
    config_str = f"""[theme]
base="{t['base']}"
primaryColor="{t['primary_color']}"
backgroundColor="{t['bg_color']}"
secondaryBackgroundColor="{t['sec_bg_color']}"
textColor="{t['text_color']}"
font="sans serif"
"""
    try:
        with open(config_path, "r") as f:
            if f.read() == config_str: return
    except: pass
    with open(config_path, "w") as f: f.write(config_str)

update_theme_config(st.session_state.theme)







# ══════════════════════════════════════════════════════════════════
#  MODULE 1: DATA LOADING & PREPROCESSING
# ══════════════════════════════════════════════════════════════════

import os
@st.cache_resource
def get_db_connection(_force_reconnect=2):
    # Ensure we use the absolute path relative to app.py to avoid working directory issues on Streamlit Cloud
    db_path = os.path.join(os.path.dirname(__file__), "netflix.db")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}. Ensure netflix.db is pushed to GitHub.")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    
    # Guarantee tables exist on Streamlit Cloud even if git pull failed to update the db file
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            show_id TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(show_id) REFERENCES titles(show_id),
            UNIQUE(user_id, show_id)
        )
    ''')
    
    # Ensure default admin exists
    import hashlib
    admin_hash = hashlib.sha256(b"admin123").hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", admin_hash))
    except sqlite3.IntegrityError:
        pass
        
    conn.commit()
    return conn

@st.cache_data(show_spinner=False)
def load_user_watchlist():
    if "user_id" in st.session_state:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT show_id FROM watchlists WHERE user_id = ?", (st.session_state["user_id"],))
        st.session_state["watchlist"] = set(row[0] for row in cursor.fetchall())
    else:
        st.session_state["watchlist"] = set()

def toggle_watchlist(show_id):
    if "user_id" not in st.session_state:
        st.error("Please login to save to your watchlist.")
        return
        
    if "watchlist" not in st.session_state:
        load_user_watchlist()
        
    user_id = st.session_state["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    
    watchlist = st.session_state.get("watchlist", set())
    if show_id in watchlist:
        cursor.execute("DELETE FROM watchlists WHERE user_id = ? AND show_id = ?", (user_id, show_id))
        watchlist.discard(show_id)
        st.session_state["watchlist"] = watchlist
        st.toast(f"Removed from My List.")
    else:
        cursor.execute("INSERT INTO watchlists (user_id, show_id) VALUES (?, ?)", (user_id, show_id))
        watchlist.add(show_id)
        st.session_state["watchlist"] = watchlist
        st.toast(f"Added to My List!")
    conn.commit()

def load_and_preprocess_data(_cache_buster=2):
    conn = get_db_connection()
    # Load data from the new SQLite database instead of CSV
    df = pd.read_sql("SELECT * FROM titles", conn)
    
    # Minimal type casting (SQLite stores dates as strings)
    df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
    df["year_added"] = df["date_added"].dt.year.astype("Int64")
    
    # Restore 'cast' and 'genres' column names so downstream Pandas charts don't crash
    if 'cast_original' in df.columns:
        df.rename(columns={'cast_original': 'cast', 'genres_original': 'genres'}, inplace=True)
        
    return df


# ══════════════════════════════════════════════════════════════════
#  MODULE 2: AUTHENTICATION GATEWAY
# ══════════════════════════════════════════════════════════════════

@st.dialog("Create a New Account")
def show_signup_dialog():
    st.markdown(f"<p style='color:gray; font-size:0.9rem;'>Register a new account.</p>", unsafe_allow_html=True)
    new_user = st.text_input("New Username", placeholder="e.g. elon")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Register", type="primary", use_container_width=True):
        if new_user and new_pass:
            import hashlib
            conn = get_db_connection()
            cursor = conn.cursor()
            pwd_hash = hashlib.sha256(new_pass.encode()).hexdigest()
            try:
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (new_user, pwd_hash))
                conn.commit()
                st.success("Account created successfully! You can now close this and sign in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists. Please choose another.")
        else:
            st.error("Please fill in both fields.")

@st.dialog("Reset Password")
def show_forgot_dialog():
    st.markdown(f"<p style='color:gray; font-size:0.9rem;'>Reset your password for a demo account.</p>", unsafe_allow_html=True)
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
        
        
        
        
        
        
        
        

        
        @keyframes floatBlob1 {
            0% { transform: translate(0, 0) scale(1) rotate(0deg); }
            33% { transform: translate(30px, -50px) scale(1.1) rotate(45deg); }
            66% { transform: translate(-20px, 20px) scale(0.9) rotate(-45deg); }
            100% { transform: translate(0, 0) scale(1) rotate(0deg); }
        }
        @keyframes floatBlob2 {
            0% { transform: translate(0, 0) scale(1) rotate(0deg); }
            33% { transform: translate(-40px, 30px) scale(1.2) rotate(-30deg); }
            66% { transform: translate(20px, -40px) scale(0.8) rotate(30deg); }
            100% { transform: translate(0, 0) scale(1) rotate(0deg); }
        }

        /* Netflix-Themed Blobs */
        .blob-1 {
            position: absolute;
            top: 10%;
            right: 15%;
            width: 400px;
            height: 400px;
            background: linear-gradient(135deg, var(--primary-color) 0%, #83050C 100%);
            border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
            z-index: 0;
            opacity: 0.5;
            filter: blur(25px);
            animation: floatBlob1 15s ease-in-out infinite;
        }
        .blob-2 {
            position: absolute;
            bottom: 10%;
            left: 10%;
            width: 300px;
            height: 300px;
            background: linear-gradient(135deg, var(--primary-color) 0%, #4a0000 100%);
            border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
            z-index: 0;
            opacity: 0.4;
            filter: blur(20px);
            animation: floatBlob2 18s ease-in-out infinite reverse;
        }
        
        @keyframes loginFadeIn {
            from { opacity: 0; transform: translateY(40px) scale(0.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
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
            font-size: 1.8rem;
            background: linear-gradient(to right, #ffffff, #a3a3a3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            letter-spacing: -0.5px;
        }

        
        
        /* The Card */
        [data-testid="stForm"] {
            animation: loginFadeIn 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
            background-color: rgba(10, 10, 10, 0.6) !important;
            backdrop-filter: blur(30px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 24px !important;
            padding: 48px !important;
            max-width: 450px !important;
            margin: 0 auto !important;
            box-shadow: 0 30px 60px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.05) !important;
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
            background-color: rgba(0, 0, 0, 0.35) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 12px !important;
            padding: 16px 18px !important;
            font-size: 1.05rem !important;
            margin-bottom: 24px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
        }
        [data-testid="stForm"] input:hover {
            border-color: rgba(255, 255, 255, 0.3) !important;
            background-color: rgba(0, 0, 0, 0.5) !important;
        }
        [data-testid="stForm"] input:focus {
            background-color: rgba(0, 0, 0, 0.6) !important;
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 15px rgba(229,9,20, 0.25), inset 0 2px 4px rgba(0,0,0,0.2) !important;
        }

        
        
        @keyframes shimmerBtn {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        /* Pill Button (Primary) */
        [data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"],
        [data-testid="stForm"] .stButton > button:not([data-testid="baseButton-secondaryFormSubmit"]):not([data-testid="baseButton-tertiaryFormSubmit"]) {
            background: linear-gradient(90deg, var(--primary-color) 0%, #ff4b53 50%, var(--primary-color) 100%) !important;
            background-size: 200% auto !important;
            animation: shimmerBtn 3s infinite linear !important;
            color: white !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
            padding: 14px 16px !important;
            margin-top: 16px !important;
            width: 100% !important;
            border: none !important;
            font-size: 1.1rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 6px 20px rgba(229,9,20,0.4) !important;
        }
        [data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"]:hover,
        [data-testid="stForm"] .stButton > button:not([data-testid="baseButton-secondaryFormSubmit"]):hover {
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 10px 25px rgba(229, 9, 20, 0.6) !important;
        }


        
        /* Pill Button (Secondary / Demo) */
        [data-testid="stForm"] button[data-testid="baseButton-secondaryFormSubmit"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #E5E5E5 !important;
            border-radius: 50px !important;
            font-weight: 600 !important;
            padding: 14px 16px !important;
            margin-top: 16px !important;
            width: 100% !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            font-size: 1.1rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            backdrop-filter: blur(5px) !important;
        }
        [data-testid="stForm"] button[data-testid="baseButton-secondaryFormSubmit"]:hover {
            background-color: rgba(255, 255, 255, 0.15) !important;
            color: #FFFFFF !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;
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
            color: var(--text-color);
            text-decoration: underline;
        }

        @media (max-width: 768px) {
            .blob-1 { width: 200px !important; height: 200px !important; right: -50px !important; top: -50px !important; opacity: 0.4 !important; filter: blur(12px) !important; }
            .blob-2 { width: 150px !important; height: 150px !important; left: -20px !important; bottom: 0px !important; opacity: 0.3 !important; filter: blur(10px) !important; }
            
        .login-header-container h1 {
            font-size: 1.8rem;
            background: linear-gradient(to right, #ffffff, #a3a3a3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            letter-spacing: -0.5px;
        }

            [data-testid="stForm"] { padding: 24px !important; width: 90% !important; margin-top: 24px !important; }
        }
        
    @media (max-width: 768px) {
        .main-title { font-size: 1.6rem !important; }
        .main-description { font-size: 0.9rem !important; }
        .metric-value { font-size: 1.8rem !important; }
        .metric-card { padding: 16px !important; }
        [role="tablist"], [data-testid="stTabList"] { gap: 8px !important; flex-wrap: wrap !important; }
        [data-testid="stTab"], [data-baseweb="tab"], button[role="tab"] { height: auto !important; padding-top: 8px !important; padding-bottom: 8px !important; font-size: 0.9rem !important; }
        .block-container, div[data-testid="stAppViewBlockContainer"] { padding-top: 4rem !important; }

    }

    /* Premium Refinements */
    
    /* Background animated glow */
    .stApp::before {{
        content: "";
        position: fixed;
        top: -10%; left: -10%; width: 120%; height: 120%;
        background-image: radial-gradient(circle at 20% 30%, var(--primary-color) 0%, transparent 20%),
                          radial-gradient(circle at 80% 70%, var(--primary-color) 0%, transparent 20%);
        opacity: 0.05;
        z-index: -1;
        pointer-events: none;
        animation: subtlePulse 8s infinite alternate;
    }}

    @keyframes subtlePulse {{
        0% {{ transform: scale(1); opacity: 0.03; }}
        100% {{ transform: scale(1.05); opacity: 0.08; }}
    }}

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-right: 1px solid var(--border-color, rgba(255, 255, 255, 0.05)) !important;
    }}
    
    /* Glowing active tabs */
    [data-testid="stTab"][aria-selected="true"] {{
        border-bottom: 3px solid var(--primary-color) !important;
        filter: drop-shadow(0 4px 6px var(--primary-color));
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateY(-2px);
    }}
    [data-testid="stTab"] {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    [data-testid="stTab"]:hover {{
        transform: translateY(-2px);
        color: var(--primary-color) !important;
    }}

    /* Static Title */
    .main-title {{
        position: relative;
        display: inline-block;
    }}

    /* Glassmorphism for containers and charts */
    .stDataFrame {{
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        border: 1px solid var(--border-color, rgba(255, 255, 255, 0.05));
    }}

    /* Smooth Chart interactions */
    .js-plotly-plot .plotly .nsewdrag {{
        cursor: pointer;
    }}


    /* SIMKL UI OVERHAUL */
    .simkl-card {{ position: relative; margin-bottom: 4px; }}
    .simkl-poster {{
        width: 100%; aspect-ratio: 2/3; border-radius: 8px; position: relative;
        overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.6); transition: transform 0.2s ease, box-shadow 0.2s ease;
        background-color: #1a1a1a;
    }}
    .simkl-poster:hover {{ transform: scale(1.04); box-shadow: 0 8px 20px rgba(0,0,0,0.8); z-index: 10; }}
    
    .simkl-badge {{
        position: absolute; background: rgba(0,0,0,0.85); color: white;
        padding: 4px 6px; font-size: 0.7rem; font-weight: 800; border-radius: 4px; z-index: 2;
        letter-spacing: 0.5px;
    }}
    .badge-top-right {{ top: 6px; right: 6px; border: 1px solid #444; color: #f5c518; }}
    .badge-top-left {{ top: 6px; left: 6px; background: #e50914; }}

    .simkl-overlay {{
        position: absolute; bottom: 0; left: 0; right: 0; top: 0;
        background: rgba(15,15,15,0.9); display: flex; flex-direction: column;
        justify-content: center; align-items: center; opacity: 0; transition: opacity 0.2s ease;
        padding: 8px; text-align: center; border-radius: 8px;
    }}
    .simkl-poster:hover .simkl-overlay {{ opacity: 1; backdrop-filter: blur(2px); }}
    
    .simkl-genres {{ color: #aaa; font-size: 0.75rem; margin-bottom: 8px; font-weight: 500; line-height: 1.4; }}
    .simkl-duration {{ color: #fff; font-size: 0.85rem; font-weight: 700; border-top: 1px solid #333; padding-top: 8px; width: 80%; }}
    
    .simkl-title {{
        font-weight: 700; font-size: 0.9rem; margin-top: 8px; margin-bottom: 4px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff;
    }}
    .simkl-btn-container {{ margin-top: 4px; }}

</style>

<div class="login-header-container">
""" + f"""{get_netflix_logo_svg('95px', 'margin: 0 auto 16px auto; display: block; filter: drop-shadow(0 4px 6px rgba(229, 9, 20, 0.4));')}""" + """
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
                conn = get_db_connection()
                admin_id = conn.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()[0]
                st.session_state["authenticated"] = True
                st.session_state["user"] = "admin"
                st.session_state["user_id"] = admin_id
                load_user_watchlist()
                st.rerun()

            if submitted:
                import hashlib
                conn = get_db_connection()
                cursor = conn.cursor()
                pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, pwd_hash))
                user_row = cursor.fetchone()
                
                if user_row:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = username
                    st.session_state["user_id"] = user_row[0]
                    load_user_watchlist()
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
        st.markdown(get_netflix_logo_svg("38px", "display:block;margin-bottom:16px;"), unsafe_allow_html=True)
        
        if "active_page" not in st.session_state:
            st.session_state.active_page = "Dashboard"
            
        selected_page = st.radio("Navigation", ["Dashboard", "My List", "Deep Dive", "Data Explorer", "Top Categories"], label_visibility="collapsed", key="nav_radio")
        if selected_page != st.session_state.active_page:
            st.session_state.active_page = selected_page
            st.rerun()
            
        st.divider()

        st.markdown(f"#### {T['filter_controls']}")

        valid_years = df["release_year"].dropna().astype(int)
        min_year, max_year = int(valid_years.min()), int(valid_years.max())

        year_range = st.slider(T["release_year"], min_value=min_year, max_value=max_year, value=(min_year, max_year), step=1)
        selected_types = st.multiselect(T["content_type"], options=sorted(df["type"].dropna().unique()), default=sorted(df["type"].dropna().unique()), format_func=lambda x: T["movie"] if x == "Movie" else (T["tv_show"] if x == "TV Show" else x), placeholder=T["choose_options"])
        selected_ratings = st.multiselect(T["maturity_rating"], options=sorted(df["rating"].dropna().unique()), default=[], placeholder=T["choose_options"])
        if "vote_average" in df.columns:
            vote_range = st.slider("Show Rating (10)", min_value=0.0, max_value=10.0, value=(0.0, 10.0), step=0.1)
        else:
            vote_range = (0.0, 10.0)
        selected_countries = st.multiselect(T["production_country"], options=sorted(df["primary_country"].dropna().unique()), default=[], placeholder=T["choose_options"])

        st.divider()
        st.markdown(f"#### {T['dataset_info']}")
        st.caption(f"Source: netflix_titles.csv")
        st.caption(f"{T['total_records']}: {len(df):,}")
        st.caption(f"Year Span: {min_year} – {max_year}")

    filtered = df[(df["release_year"] >= year_range[0]) & (df["release_year"] <= year_range[1])]
    if selected_types: filtered = filtered[filtered["type"].isin(selected_types)]
    if selected_ratings: filtered = filtered[filtered["rating"].isin(selected_ratings)]
    if selected_countries: filtered = filtered[filtered["primary_country"].isin(selected_countries)]
    if "vote_average" in filtered.columns: filtered = filtered[(filtered["vote_average"] >= vote_range[0]) & (filtered["vote_average"] <= vote_range[1])]
    return filtered


# ══════════════════════════════════════════════════════════════════
#  MODULE 4: EXECUTIVE METRIC CARDS
# ══════════════════════════════════════════════════════════════════


def localize_number(num, lang):
    if num is None or pd.isna(num): return ""
    try:
        num_str = f"{int(num):,}" if float(num).is_integer() else f"{float(num):,}"
    except:
        return str(num)
        
    if lang == "Hindi":
        mapping = str.maketrans('0123456789', '०१२३४५६७८९')
        return num_str.translate(mapping)
    elif lang == "Gujarati":
        mapping = str.maketrans('0123456789', '૦૧૨૩૪૫૬૭૮૯')
        return num_str.translate(mapping)
    elif lang == "Spanish":
        return num_str.replace(',', '.')
    return num_str

GENRE_MAP = {
    "Hindi": {
        "Dramas": "ड्रामा", "Drama": "ड्रामा", "TV Dramas": "टीवी ड्रामा", "Comedies": "कॉमेडी", "Comedy": "कॉमेडी", "TV Comedies": "टीवी कॉमेडी",
        "Action & Adventure": "एक्शन", "Action": "एक्शन", "Thrillers": "थ्रिलर", "Thriller": "थ्रिलर",
        "Romantic Movies": "रोमांस मूवी", "Romantic TV Shows": "रोमांस टीवी", "Romance": "रोमांस",
        "Documentaries": "डॉक्यूमेंट्री", "Docuseries": "डॉक्यूसीरीज",
        "Crime TV Shows": "क्राइम टीवी", "Crime": "क्राइम",
        "Kids' TV": "किड्स टीवी", "Children & Family Movies": "किड्स और फैमिली",
        "International Movies": "अंतर्राष्ट्रीय मूवी", "International TV Shows": "अंतर्राष्ट्रीय टीवी",
        "Horror Movies": "हॉरर मूवी", "Stand-Up Comedy": "स्टैंड-अप", "Anime Series": "एनीमे",
        "Sci-Fi & Fantasy": "सांसारिक फंतासी", "Mystery": "रहस्य", "Music & Musicals": "संगीत",
        "Independent Movies": "इंडिपेंडेंट मूवी", "British TV Shows": "ब्रिटिश टीवी", "Sports Movies": "स्पोर्ट्स", "Animation": "एनिमेशन", "Family": "फैमिली", "Horror": "हॉरर", "Documentary": "डॉक्यूमेंट्री", "Reality": "रियलिटी", "Science Fiction": "विज्ञान कथा", "Fantasy": "फंतासी", "History": "इतिहास", "Kids": "किड्स", "Music": "संगीत", "War": "युद्ध", "War & Politics": "युद्ध और राजनीति", "Soap": "सोप ओपेरा", "Talk": "टॉक शो", "Adventure": "एडवेंचर", "Reality TV": "रियलिटी टीवी"
    },
    "Gujarati": {
        "Dramas": "ડ્રામા", "Drama": "ડ્રામા", "TV Dramas": "ટીવી ડ્રામા", "Comedies": "કોમેડી", "Comedy": "કોમેડી", "TV Comedies": "ટીવી કોમેડી",
        "Action & Adventure": "એક્શન", "Action": "એક્શન", "Thrillers": "થ્રિલર", "Thriller": "થ્રિલર",
        "Romantic Movies": "રોમાંસ મૂવી", "Romantic TV Shows": "રોમાંસ ટીવી", "Romance": "રોમાંસ",
        "Documentaries": "ડોક્યુમેન્ટરી", "Docuseries": "ડોક્યુસિરીઝ",
        "Crime TV Shows": "ક્રાઈમ ટીવી", "Crime": "ક્રાઈમ",
        "Kids' TV": "બાળકો માટે ટીવી", "Children & Family Movies": "બાળકો અને કુટુંબ",
        "International Movies": "આંતરરાષ્ટ્રીય મૂવી", "International TV Shows": "આંતરરાષ્ટ્રીય ટીવી",
        "Horror Movies": "હોરર", "Stand-Up Comedy": "સ્ટેન્ડ-અપ", "Anime Series": "એનિમે",
        "Sci-Fi & Fantasy": "સાય-ફાઇ", "Mystery": "રહસ્ય", "Music & Musicals": "સંગીત",
        "Independent Movies": "સ્વતંત્ર મૂવી", "British TV Shows": "બ્રિટિશ ટીવી", "Sports Movies": "સ્પોર્ટ્સ", "Animation": "એનિમેશન", "Family": "કુટુંબ", "Horror": "હોરર", "Documentary": "ડોક્યુમેન્ટરી", "Reality": "રિયાલિટી", "Science Fiction": "વિજ્ઞાન કથા", "Fantasy": "કાલ્પનિક", "History": "ઇતિહાસ", "Kids": "બાળકો", "Music": "સંગીત", "War": "યુદ્ધ", "War & Politics": "યુદ્ધ અને રાજકારણ", "Soap": "સોપ ઓપેરા", "Talk": "ટૉક શો", "Adventure": "સાહસ", "Reality TV": "રિયાલિટી ટીવી"
    },
    "Spanish": {
        "Dramas": "Drama", "Drama": "Drama", "TV Dramas": "Dramas de TV", "Comedies": "Comedias", "Comedy": "Comedia", "TV Comedies": "Comedias de TV",
        "Action & Adventure": "Acción", "Action": "Acción", "Thrillers": "Suspenso", "Thriller": "Suspenso",
        "Romantic Movies": "Romance", "Romantic TV Shows": "Romance TV", "Romance": "Romance",
        "Documentaries": "Documentales", "Docuseries": "Docuseries",
        "Crime TV Shows": "Crimen TV", "Crime": "Crimen",
        "Kids' TV": "Infantil", "Children & Family Movies": "Infantil y Familiar",
        "International Movies": "Películas Internacionales", "International TV Shows": "TV Internacional",
        "Horror Movies": "Terror", "Stand-Up Comedy": "Comedia en vivo", "Anime Series": "Anime",
        "Sci-Fi & Fantasy": "Ciencia Ficción", "Mystery": "Misterio", "Music & Musicals": "Música",
        "Independent Movies": "Cine Independiente", "British TV Shows": "TV Británica", "Sports Movies": "Deportes", "Animation": "Animación", "Family": "Familiar", "Horror": "Terror", "Documentary": "Documental", "Reality": "Reality", "Science Fiction": "Ciencia Ficción", "Fantasy": "Fantasía", "History": "Historia", "Kids": "Infantil", "Music": "Música", "War": "Bélico", "War & Politics": "Guerra y Política", "Soap": "Telenovela", "Talk": "Talk Show", "Adventure": "Aventura", "Reality TV": "Reality TV"
    }
}

def localize_genre(genre, lang):
    if not isinstance(genre, str): return genre
    return GENRE_MAP.get(lang, {}).get(genre, genre)

def chart_kpi_line(value, title, x_series, y_series):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_series, y=y_series, mode='lines+markers', marker=dict(size=6, color="gray"), fill='tozeroy', line_color=theme_primary, fillcolor=hex_to_rgba(theme_primary, 0.1), line=dict(width=3)))
    fig.update_layout(
        title=dict(text=f"<span style='font-size:14px;color:gray;font-family:Inter'>{title}</span>", x=0.10, y=0.95),
        annotations=[dict(text=f"<span style='font-size:46px;color:var(--text-color);font-family:\"Bebas Neue\",sans-serif;letter-spacing:1px'>{value}</span>", xref="paper", yref="paper", x=0.10, y=1.7, showarrow=False, xanchor="left", yanchor="top")],
        margin=dict(l=16, r=16, t=120, b=10),
        height=190,
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
    fig.add_trace(go.Bar(x=x_series, y=y_series, marker_color=theme_primary, opacity=0.8, marker_line_width=0))
    fig.update_layout(
        title=dict(text=f"<span style='font-size:14px;color:gray;font-family:Inter'>{title}</span>", x=0.10, y=0.95),
        annotations=[dict(text=f"<span style='font-size:46px;color:var(--text-color);font-family:\"Bebas Neue\",sans-serif;letter-spacing:1px'>{value}</span>", xref="paper", yref="paper", x=0.10, y=1.7, showarrow=False, xanchor="left", yanchor="top")],
        margin=dict(l=16, r=16, t=120, b=10),
        height=190,
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
    fig.add_trace(go.Bar(x=labels, y=values, text=labels, textposition='inside', insidetextfont=dict(color="gray", size=14), marker_color=[theme_primary, "gray"], marker_line_width=0))
    fig.update_layout(
        title=dict(text=f"<span style='font-size:14px;color:gray;font-family:Inter'>{title}</span>", x=0.10, y=0.95),
        annotations=[dict(text=f"<span style='font-size:46px;color:var(--text-color);font-family:\"Bebas Neue\",sans-serif;letter-spacing:1px'>{value}</span>", xref="paper", yref="paper", x=0.10, y=1.7, showarrow=False, xanchor="left", yanchor="top")],
        margin=dict(l=16, r=16, t=120, b=10),
        height=190,
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
    genres = df["genres"].str.split(", ").explode()
    top_genres_counts = genres.value_counts().head(12)
    top_genres_names = top_genres_counts.index
    total_genres = len(genres.unique())
    
    # Data for Card 3
    type_counts = df["type"].value_counts()
    pct_movies = (type_counts.get('Movie', 0) / total_titles * 100) if total_titles > 0 else 0
    
    localized_total = localize_number(total_titles, st.session_state.lang)
    localized_genres = localize_number(total_genres, st.session_state.lang)
    localized_pct = localize_number(f"{pct_movies:.0f}", st.session_state.lang) + "%"
    
    localized_genre_names = [localize_genre(g, st.session_state.lang) for g in top_genres_names]
    localized_type_names = [T["movie"] if x == "Movie" else (T["tv_show"] if x == "TV Show" else x) for x in type_counts.index]

    fig1 = chart_kpi_line(localized_total, T.get("metric_total", "Total Content"), trend_counts["year_added"], trend_counts["counts"])
    fig2 = chart_kpi_bar(localized_genres, T.get("metric_genres", "Unique Genres"), localized_genre_names[::-1], top_genres_counts.values[::-1])
    fig3 = chart_kpi_donut(localized_pct, T.get("content_type", "Content Type"), localized_type_names, type_counts.values)

    cols = st.columns(3, gap="medium")
    with cols[0]:
        ev1 = st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False}, on_select="rerun", selection_mode="points")
        process_selection(ev1, "kpi_total", "year_added", extract_key="x")
    with cols[1]:
        ev2 = st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False}, on_select="rerun", selection_mode="points")
        process_selection(ev2, "kpi_genres", "genres", extract_key="x", match_type="contains")
    with cols[2]:
        ev3 = st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False}, on_select="rerun", selection_mode="points")
        process_selection(ev3, "kpi_split", "type", extract_key="x")


# ══════════════════════════════════════════════════════════════════
#  MODULE 5: PLOTLY VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════



def chart_content_split(df: pd.DataFrame):
    type_counts = df["type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]
    type_counts["Type"] = type_counts["Type"].map({"Movie": T["movie"], "TV Show": T["tv_show"]}).fillna(type_counts["Type"])
    type_counts["Type"] = type_counts["Type"].map({"Movie": T["movie"], "TV Show": T["tv_show"]}).fillna(type_counts["Type"])
    fig = go.Figure(go.Bar(name=T.get("count", "Count"), x=type_counts["Type"], y=type_counts["Count"],
        text=type_counts["Count"].map(lambda x: localize_number(x, st.session_state.lang)), textposition='auto',
        marker=dict(color=[theme_primary, theme_primary], line=dict(color="rgba(0,0,0,0)", width=2)),
    ))
    fig.update_layout(xaxis_title=T.get("content_type", "Type"), yaxis_title=T.get("count", "Count"), title=dict(text=T["chart_distribution"], font=dict(size=14, color="gray")), showlegend=False, height=350, clickmode="event+select")
    return fig

def chart_year_ingestion(df: pd.DataFrame):
    yearly = df["year_added"].dropna().astype(int).value_counts().sort_index().reset_index()
    yearly.columns = ["Year", "Titles Added"]
    fig = go.Figure(go.Scatter(
        x=yearly["Year"], y=yearly["Titles Added"], mode="lines+markers",
        line=dict(color=theme_primary, width=2, shape="spline"), marker=dict(size=6, color="gray"), fill="tozeroy", fillcolor=hex_to_rgba(theme_primary, 0.05),
    ))
    fig.update_layout(xaxis_title=T.get("year_added", "Year Added"), yaxis_title=T.get("count", "Count"), title=dict(text=T["chart_yoy"], font=dict(size=14, color="gray")), xaxis=dict(zeroline=False), yaxis=dict(zeroline=False), height=350, clickmode="event+select")
    return fig

def chart_top_genres(df: pd.DataFrame):
    genres = df["genres"].dropna().str.split(", ").explode()
    genre_counts = genres.value_counts().head(10).sort_values(ascending=True).reset_index()
    genre_counts.columns = ["Genre", "Titles"]
    genre_counts["Genre"] = genre_counts["Genre"].map(lambda x: localize_genre(x, st.session_state.lang))
    fig = go.Figure(go.Bar(name=T.get("count", "Count"), x=genre_counts["Titles"], y=genre_counts["Genre"], orientation="h",
        marker=dict(color=theme_primary, line=dict(color="rgba(0,0,0,0)", width=0.5)),
    ))
    fig.update_layout(xaxis_title=T.get("count", "Count"), yaxis_title=T.get("genre", "Genre"), title=dict(text=T["chart_genres"], font=dict(size=14, color="gray")), xaxis=dict(gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(title=""), height=350)
    return fig

def chart_rating_distribution(df: pd.DataFrame):
    rating_counts = df["rating"].dropna().value_counts().head(10).reset_index()
    rating_counts.columns = ["Rating", "Count"]
    fig = px.bar(rating_counts, x="Rating", y="Count", color_discrete_sequence=[theme_primary], text=rating_counts["Count"].map(lambda x: localize_number(x, st.session_state.lang)), labels={"Rating": T.get("rating", "Rating"), "Count": T.get("count", "Count")})
    fig.update_traces(marker_line_color="rgba(0,0,0,0)", marker_line_width=0.5)
    fig.update_layout(title=dict(text=T["chart_rating"], font=dict(size=14, color="gray")), xaxis=dict(title=T.get("rating", "Rating"), gridcolor="rgba(0,0,0,0)", type="category"), yaxis=dict(title=T.get("count", "Count"), gridcolor="rgba(128,128,128,0.2)"), bargap=0.2, height=350)
    return fig

def chart_top_directors(df: pd.DataFrame):
    directors = df["director"].dropna().str.split(", ").explode()
    director_counts = directors.value_counts().head(10).sort_values(ascending=True).reset_index()
    director_counts.columns = ["Director", "Titles"]
    fig = go.Figure(go.Bar(name=T.get("count", "Count"), x=director_counts["Titles"], y=director_counts["Director"], orientation="h",
        marker=dict(color=theme_primary, line=dict(color="rgba(0,0,0,0)", width=0.5)),
    ))
    fig.update_layout(xaxis_title=T.get("count", "Count"), yaxis_title=T.get("director", "Director"), title=dict(text=T["chart_directors"], font=dict(size=14, color="gray")), xaxis=dict(gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(title=""), height=350)
    return fig

def chart_runtime_distribution(df: pd.DataFrame):
    movies = df[(df["type"] == "Movie") & (df["duration_minutes"].notna())]
    fig = px.histogram(movies, x="duration_minutes", nbins=40, color_discrete_sequence=["#404040"], labels={"duration_minutes": T.get("duration_minutes", "Duration (min)"), "count": T.get("count", "Count")})
    fig.update_traces(marker_line_color="rgba(0,0,0,0)", marker_line_width=0.5)
    fig.update_layout(title=dict(text=T.get("chart_title_histogram", "Movie Runtime Histogram"), font=dict(size=14, color="gray")), xaxis=dict(title=T.get("duration_minutes", "Duration (min)"), gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(title="Frequency", gridcolor="rgba(128,128,128,0.2)"), bargap=0.06, height=350, clickmode="event+select")
    return fig

# --- New Deep Dive Visualizations ---
def chart_top_countries_map(df: pd.DataFrame):
    country_counts = df["primary_country"].dropna().value_counts().reset_index()
    country_counts.columns = ["Country", "Titles"]
    fig = px.choropleth(
        country_counts, locations="Country", locationmode="country names", color="Titles",
        color_continuous_scale=["rgba(0,0,0,0)", theme_primary, "#7A271A"], labels={"Titles": T.get("titles", "Titles")}
    )
    fig.update_layout(
        title=dict(text="Global Production Hubs", font=dict(size=14, color="gray")),
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="gray", projection_type='equirectangular', bgcolor='rgba(0,0,0,0)'),
        height=400, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", clickmode="event+select"
    )
    return fig

def chart_top_cast(df: pd.DataFrame):
    cast_list = df["cast"].dropna().str.split(", ").explode()
    cast_counts = cast_list.value_counts().head(10).sort_values(ascending=True).reset_index()
    cast_counts.columns = ["Actor", "Titles"]
    fig = go.Figure(go.Bar(name=T.get("count", "Count"), x=cast_counts["Titles"], y=cast_counts["Actor"], orientation="h",
        marker=dict(color=theme_primary, line=dict(color="rgba(0,0,0,0)", width=0.5))
    ))
    fig.update_layout(xaxis_title=T.get("count", "Count"), yaxis_title="", title=dict(text=T.get("chart_title_actors", "Top 10 Most Featured Actors"), font=dict(size=14, color="gray")), xaxis=dict(gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(title=""), height=400, clickmode="event+select")
    return fig

def chart_duration_scatter(df: pd.DataFrame):
    movies = df[(df["type"] == "Movie") & (df["duration_minutes"].notna()) & (df["release_year"] >= 1970)]
    avg_duration = movies.groupby("release_year")["duration_minutes"].mean().reset_index()
    
    fig = px.scatter(movies, x="release_year", y="duration_minutes", opacity=0.3, color_discrete_sequence=["#404040"], labels={"release_year": T.get("release_year", "Release Year"), "duration_minutes": T.get("duration_minutes", "Duration (min)")})
    fig.add_trace(go.Scatter(x=avg_duration["release_year"], y=avg_duration["duration_minutes"], mode="lines+markers", marker=dict(size=6, color=theme_primary), line=dict(color=theme_primary, width=3), name=T.get("legend_avg_runtime", "Average Runtime")))
    fig.update_layout(title=dict(text=T.get("chart_title_scatter", "Movie Runtime Trends (Scatter + Average)"), font=dict(size=14, color="gray")), xaxis=dict(title=T.get("release_year", "Release Year"), gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(title=T.get("duration_minutes", "Duration (mins)"), gridcolor="rgba(128,128,128,0.2)"), height=400, clickmode="event+select")
    return fig


# ══════════════════════════════════════════════════════════════════
#  MODULE 6: RECENT FEED & DATA EXPLORER
# ══════════════════════════════════════════════════════════════════

def render_recent_feed(df: pd.DataFrame):
    T = LANG[st.session_state.lang]
    latest = df.sort_values("date_added", ascending=False).head(5)
    
    html = '<div style="display:flex; flex-direction:column; gap:16px;">'
    for _, row in latest.iterrows():
        date_str = row["date_added"].strftime("%B %d, %Y") if pd.notna(row["date_added"]) else T.get("feed_unknown", "Unknown Date")
        desc = str(row["description"])[:140] + "..." if pd.notna(row["description"]) else ""
        
        # Translate the type (Movie / TV Show)
        row_type = T["movie"] if row['type'] == "Movie" else T["tv_show"]
        
        html += f"""
<div style="border-left: 3px solid var(--primary-color); padding-left: 16px;">
<div style="font-size: 0.75rem; color: var(--text-color); opacity: 0.7; margin-bottom: 4px; font-weight: 500; text-transform: uppercase;">{date_str} &nbsp;&bull;&nbsp; {row_type}</div>
<div style="font-size: 1.05rem; font-weight: 600; color: var(--text-color); margin-bottom: 6px;">{row['title']} <span style="font-size:0.7rem; background:var(--secondary-background-color); border:1px solid gray; padding:2px 6px; border-radius:4px; margin-left:8px; color:gray; font-weight: 500;">{row['rating']}</span></div>
<div style="font-size: 0.85rem; color: var(--text-color); opacity: 0.7; line-height: 1.5;">{desc}</div>
</div>
"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)



import urllib.request
import urllib.parse
import re

@st.cache_data(show_spinner=False)
def get_youtube_trailer_url(movie_title, release_year):
    import urllib.parse, urllib.request, re
    query = urllib.parse.quote(f"{movie_title} {release_year} official trailer")
    url = f"https://www.youtube.com/results?search_query={query}"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
        
        # Look for video ids using standard watch regex or shortcodes
        video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)
        if not video_ids:
            # Fallback to search videoData ids if youtube changes layout
            video_ids = re.findall(r"\"videoId\":\"([a-zA-Z0-9_-]{11})\"", html)
            
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
    except Exception as e:
        pass
    return None

@st.dialog("🍿 Movie Details & Trailer", width="large")
def play_trailer_dialog(row):
    import urllib.parse
    title = str(row['title'])
    year = str(row.get('release_year', ''))
    
    col1, col2 = st.columns([1.6, 1], gap="large")
    
    with col1:
        with st.spinner(f"Searching for official trailer for {title}..."):
            url = get_youtube_trailer_url(title, year)
        
        if url:
            st.video(url)
            st.markdown(f"<div style='text-align: center; margin-top: 10px;'><a href='{url}' target='_blank' style='color: #e50914; text-decoration: none; font-weight: bold;'>Watch directly on YouTube</a></div>", unsafe_allow_html=True)
        else:
            st.warning("Could not automatically embed a trailer for this title.")
            search_query = urllib.parse.quote(f"{title} {year} official trailer")
            st.markdown(f"**[Click here to search YouTube manually](https://www.youtube.com/results?search_query={search_query})**")
            
    with col2:
        st.markdown(f"## {title} ({year})")
        score = f"★ {float(row.get('vote_average', 0)):.1f}" if pd.notna(row.get('vote_average')) else "NR"
        rating = row.get('rating', 'Unknown')
        duration = row.get('duration', 'Unknown')
        
        st.markdown(f"**{score}** &nbsp;|&nbsp; **{rating}** &nbsp;|&nbsp; **{duration}**", unsafe_allow_html=True)
        st.markdown(f"**Genres:** {row.get('genres', 'N/A')}")
        st.markdown(f"**Director:** {row.get('director', 'Unknown')}")
        st.markdown(f"**Cast:** {row.get('cast', 'Unknown')}")
        st.markdown(f"**Country:** {row.get('country', 'Unknown')}")
        st.divider()
        st.markdown(f"_{row.get('description', 'No description available.')}_")
        
        safe_title = urllib.parse.quote(title)
        st.markdown(f"""
            <div style='display:flex; gap:10px; margin-top:20px; width:100%;'>
                <a href='https://www.netflix.com/search?q={safe_title}' target='_blank' style='flex:1; background:#e50914; color:white; padding:10px; border-radius:6px; text-decoration:none; font-weight:bold; text-align:center; transition: opacity 0.2s;' onmouseover='this.style.opacity=0.8' onmouseout='this.style.opacity=1'>Netflix</a>
                <a href='https://www.justwatch.com/us/search?q={safe_title}' target='_blank' style='flex:1; background:rgba(255,255,255,0.1); color:#fff; border: 1px solid rgba(255,255,255,0.2); padding:10px; border-radius:6px; text-decoration:none; font-weight:bold; text-align:center; transition: opacity 0.2s;' onmouseover='this.style.opacity=0.8' onmouseout='this.style.opacity=1'>JustWatch</a>
            </div>
        """, unsafe_allow_html=True)

def render_catalog_explorer(df: pd.DataFrame, key_prefix=''):

    T = LANG[st.session_state.lang]
    
    col_search, col_view = st.columns([4, 1])
    with col_search:
        search_query = st.text_input(T.get("cat_search_prompt", "Search Titles, Directors, or Genres"), key=f"{key_prefix}search_input", placeholder=T.get("cat_search_placeholder", "e.g. Sci-Fi, Christopher Nolan"))
        
        last_query_key = f"{key_prefix}last_search_query"
        page_key = f"{key_prefix}current_page"
        if st.session_state.get(last_query_key) != search_query:
            st.session_state[page_key] = 1
            st.session_state[last_query_key] = search_query
    with col_view:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        view_mode = st.radio(T["view_mode_label"], [f":material/grid_view: {T['grid_mode']}", f":material/table_rows: {T['csv_mode']}"], horizontal=True, label_visibility="collapsed", key=f"{key_prefix}view_mode")
        
    if search_query:
        try:
            from rapidfuzz import process, fuzz
            search_corpus = (df['title'].fillna('') + ' ' + df['director'].fillna('') + ' ' + df['genres'].fillna('')).tolist()
            matches = process.extract(search_query, search_corpus, scorer=fuzz.WRatio, limit=100, score_cutoff=60)
            matched_indices = [idx for _, _, idx in matches]
            search_results = df.iloc[matched_indices].copy()
        except ImportError:
            query_lower = search_query.lower()
            mask = (df["title"].str.lower().str.contains(query_lower, na=False) | df["director"].str.lower().str.contains(query_lower, na=False) | df["genres"].str.lower().str.contains(query_lower, na=False))
            search_results = df[mask]
    else:
        search_results = df

    display_cols = ["title", "type", "director", "country", "release_year", "rating", "vote_average", "duration", "genres", "show_id", "description"]
    display_df = search_results[[c for c in display_cols if c in search_results.columns]].reset_index(drop=True).copy()

    # Rename columns based on translation map
    col_map = {
        "title": T.get("col_title", "Title"),
        "type": T.get("col_type", "Type"),
        "director": T.get("col_director", "Director"),
        "country": T.get("col_country", "Country"),
        "release_year": T.get("col_year", "Release Year"),
        "rating": T.get("col_rating", "Rating"),
        "vote_average": "Show Rating (10)",
        "duration": T.get("col_duration", "Duration"),
        "genres": T.get("col_genres", "Genres")
    }
    
    # Translate types and genres inside the dataframe for non-English languages
    if st.session_state.lang != "English":
        type_col = "type"
        genres_col = "genres"
        if type_col in display_df.columns:
            display_df[type_col] = display_df[type_col].apply(lambda x: T["movie"] if x == "Movie" else T["tv_show"] if pd.notna(x) else x)
        if genres_col in display_df.columns:
            from app import GENRE_MAP
            display_df[genres_col] = display_df[genres_col].apply(lambda g: ", ".join([GENRE_MAP.get(st.session_state.lang, {}).get(genre.strip(), genre.strip()) for genre in str(g).split(',')]) if pd.notna(g) else g)

    st.caption(T.get("cat_showing_results", "Showing {0:,} results").format(len(display_df)))
    
    if "Grid" in view_mode:
        ITEMS_PER_PAGE = 30
        total_items = len(display_df)
        total_pages = max(1, (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        
        page_key = f"{key_prefix}current_page"
        if page_key not in st.session_state:
            st.session_state[page_key] = 1
            
        current_page = st.session_state[page_key]
        if current_page > total_pages:
            current_page = 1
            st.session_state[page_key] = 1
            
        start_idx = (current_page - 1) * ITEMS_PER_PAGE
        end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
        page_df = display_df.iloc[start_idx:end_idx]
        
        cols = st.columns(5)
        for i, (_, row) in enumerate(page_df.iterrows()):
            with cols[i % 5]:
                m_img = get_image(f"{row['title']} movie", is_movie=True)
                bg_style = f"background: url({m_img}) center/cover;" if m_img else "background: linear-gradient(45deg, #111, #333);"
                
                score = f"{float(row.get('vote_average', 0)):.1f}" if pd.notna(row.get('vote_average')) else "NR"
                year = f"{row.get('release_year', '')}"
                rating = f"{row.get('rating', '')}" if pd.notna(row.get('rating')) else ""
                director = f"Dir: {row.get('director', 'Unknown')}" if pd.notna(row.get('director')) else ""
                genres = f"{row.get('genres', 'N/A')}"
                duration = f"{row.get('duration', 'N/A')}"
                
                desc = str(row.get('description', ''))
                if pd.isna(row.get('description')) or desc == 'nan': desc = ""
                elif len(desc) > 70: desc = desc[:67] + "..."
                
                import urllib.parse
                safe_title = urllib.parse.quote(str(row['title']))
                watch_link = f"""<div style='display:flex; gap:6px; margin-top:8px; width:100%;'>
<a href='https://www.netflix.com/search?q={safe_title}' title='{T['title_search_netflix']}' target='_blank' style='flex:1; background:var(--primary-color); color:white; padding:4px; border-radius:4px; text-decoration:none; font-size:0.7rem; font-weight:bold; text-align:center; transition: opacity 0.2s;' onmouseover='this.style.opacity=0.8' onmouseout='this.style.opacity=1'>{T['btn_netflix']}</a>
<a href='https://www.justwatch.com/us/search?q={safe_title}' title='{T['title_find_justwatch']}' target='_blank' style='flex:1; background:rgba(255,255,255,0.1); color:#fff; border: 1px solid rgba(255,255,255,0.2); padding:4px; border-radius:4px; text-decoration:none; font-size:0.7rem; font-weight:bold; text-align:center; transition: opacity 0.2s;' onmouseover='this.style.opacity=0.8' onmouseout='this.style.opacity=1'>{T['btn_where']}</a>
</div>"""
                
                html = f'''
                <div class="simkl-card">
                    <div class="simkl-poster" style="{bg_style}">
                        <div class="simkl-badge badge-top-right">★ {score}</div>
                        <div class="simkl-badge badge-top-left">{year}</div>
                        <div class="simkl-overlay">
                            <div style="color: #e50914; font-weight: 800; font-size: 0.75rem; margin-bottom: 2px;">{rating}</div>
                            <div class="simkl-genres" style="margin-bottom: 4px;">{genres}</div>
                            <div style="color: #ccc; font-size: 0.7rem; font-style: italic; margin-bottom: 6px;">{director}</div>
                            <div style="color: #fff; font-size: 0.7rem; text-align: left; line-height: 1.3; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis;" title="{desc}">{desc}</div>
                            <div class="simkl-duration">{duration}</div>
                            {watch_link}
                        </div>
                    </div>
                    <div class="simkl-title" title="{row['title']}">{row['title']}</div>
                </div>
                '''
                st.markdown(html, unsafe_allow_html=True)
                
                
                # Watchlist logic
                if "watchlist" not in st.session_state and "user_id" in st.session_state:
                    load_user_watchlist()
                
                watchlist = st.session_state.get("watchlist", set())
                is_saved = row.get('show_id') in watchlist
                wl_text = "✔ In My List" if is_saved else "+ My List"
                if st.button(wl_text, key=f"{key_prefix}wl_btn_{i}_{row.get('show_id', i)}", use_container_width=True, type="secondary"):
                    toggle_watchlist(row.get('show_id'))
                    st.rerun()
                    
                if st.button(T["btn_cast"], key=f"{key_prefix}grid_btn_{i}_{row.get('show_id', i)}", use_container_width=True):
                    set_node("movie", row.get('show_id', row['title']))
                    st.session_state.cast_button_clicked = True
                    st.rerun()
                if st.button(T["btn_trailer"], key=f"{key_prefix}trailer_btn_{i}_{row.get('show_id', i)}", use_container_width=True, type="primary"):
                    play_trailer_dialog(row)
                        
        if total_pages > 1:
            st.markdown("<br>", unsafe_allow_html=True)
            p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
            with p_col1:
                if current_page > 1:
                    if st.button("⬅️ Previous Page", key=f"{key_prefix}prev_page", use_container_width=True):
                        st.session_state[page_key] = current_page - 1
                        st.rerun()
            with p_col2:
                st.markdown(f"<div style='text-align: center; padding-top: 8px;'>Page <b>{current_page}</b> of <b>{total_pages}</b></div>", unsafe_allow_html=True)
            with p_col3:
                if current_page < total_pages:
                    if st.button("Next Page ➡️", key=f"{key_prefix}next_page", use_container_width=True):
                        st.session_state[page_key] = current_page + 1
                        st.rerun()
                        
    else:
        display_df = display_df.rename(columns=col_map)
        display_df = display_df.drop(columns=["show_id"], errors='ignore')
        st.dataframe(display_df, use_container_width=True, height=500)

    csv_payload = search_results.to_csv(index=False).encode("utf-8")
    st.download_button(T["download_csv"], data=csv_payload, file_name="netflix_export.csv", mime="text/csv", use_container_width=True, key=f"{key_prefix}dl_btn")





def render_watchlist_page():
    st.markdown("## 🍿 My List", unsafe_allow_html=True)
    if "user_id" not in st.session_state:
        st.warning("Please sign in to view your saved titles.")
        return
        
    if "watchlist" not in st.session_state:
        load_user_watchlist()
        
    if not st.session_state.watchlist:
        st.info("Your list is empty! Explore the catalog and add some titles.")
        return
        
    conn = get_db_connection()
    placeholders = ','.join(['?'] * len(st.session_state.watchlist))
    query = f"SELECT * FROM titles WHERE show_id IN ({placeholders})"
    wl_df = pd.read_sql(query, conn, params=list(st.session_state.watchlist))
    
    # CSS for horizontal carousel
    st.markdown('''
        <style>
        .carousel-container {
            display: flex;
            overflow-x: auto;
            gap: 16px;
            padding: 20px 0;
            scroll-snap-type: x mandatory;
        }
        .carousel-container::-webkit-scrollbar {
            height: 8px;
        }
        .carousel-container::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
        }
        .carousel-container::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
        }
        .carousel-item {
            flex: 0 0 220px;
            scroll-snap-align: start;
        }
        </style>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="carousel-container">', unsafe_allow_html=True)
    
    # We will use columns to fake a carousel visually for standard streamlit, 
    # but the container CSS will make it scrollable horizontally if we inject raw HTML.
    # Actually, Streamlit columns wrap. Let's just use raw HTML for the carousel items!
    
    html = '<div class="carousel-container">'
    for _, row in wl_df.iterrows():
        m_img = get_image(f"{row['title']} movie", is_movie=True)
        bg_style = f"background: url({m_img}) center/cover;" if m_img else "background: linear-gradient(45deg, #111, #333);"
        score = f"{float(row.get('vote_average', 0)):.1f}" if pd.notna(row.get('vote_average')) else "NR"
        year = f"{row.get('release_year', '')}"
        
        html += f'''
        <div class="carousel-item">
            <div class="simkl-card" style="width: 100%; height: 330px;">
                <div class="simkl-poster" style="{bg_style}">
                    <div class="simkl-badge badge-top-right">★ {score}</div>
                    <div class="simkl-badge badge-top-left">{year}</div>
                </div>
                <div class="simkl-title" title="{row['title']}">{row['title']}</div>
            </div>
        </div>
        '''
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)
    
    st.markdown("<br><hr><br><h3>Manage Watchlist</h3>", unsafe_allow_html=True)
    # We can reuse the catalog explorer renderer but pass the watchlist dataframe!
    render_catalog_explorer(wl_df, key_prefix="wl_")

def render_top_categories(df: pd.DataFrame):
    popular_genres = ["Action", "Comedy", "Sci-Fi", "Horror", "Thrillers", "Drama"]
    

    
    for genre in popular_genres:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f'<div class="section-header" style="margin-bottom: 8px; font-size: 1.4rem;">🎬 Top 5 {genre} Movies</div>', unsafe_allow_html=True)
        with col2:
            if st.button(f"View All {genre}", key=f"view_{genre}", use_container_width=True):
                st.session_state.view_all_clicked = genre
                st.session_state['tab3_search_input'] = genre
                st.session_state.active_page = "Data Explorer"
                st.rerun()
                
        genre_df = df[df["genres"].str.contains(genre, case=False, na=False)].copy()
        genre_df['vote_numeric'] = pd.to_numeric(genre_df['vote_average'], errors='coerce').fillna(0)
        genre_df = genre_df.sort_values(by="vote_numeric", ascending=False).head(5)
        
        if len(genre_df) > 0:
            cols = st.columns(5)
            for i, (_, row) in enumerate(genre_df.iterrows()):
                with cols[i % 5]:
                    m_img = get_image(f"{row['title']} movie", is_movie=True)
                    bg_style = f"background: url({m_img}) center/cover;" if m_img else "background: linear-gradient(45deg, #111, #333);"
                    
                    score = f"{float(row.get('vote_average', 0)):.1f}" if pd.notna(row.get('vote_average')) else "NR"
                    year = f"{row.get('release_year', '')}"
                    rating = f"{row.get('rating', '')}" if pd.notna(row.get('rating')) else ""
                    director = f"Dir: {row.get('director', 'Unknown')}" if pd.notna(row.get('director')) else ""
                    genres_str = f"{row.get('genres', 'N/A')}"
                    duration = f"{row.get('duration', 'N/A')}"
                    
                    desc = str(row.get('description', ''))
                    if pd.isna(row.get('description')) or desc == 'nan': desc = ""
                    elif len(desc) > 70: desc = desc[:67] + "..."
                    
                    import urllib.parse
                    safe_title = urllib.parse.quote(str(row['title']))
                    watch_link = f"""<div style='display:flex; gap:6px; margin-top:8px; width:100%;'>
<a href='https://www.netflix.com/search?q={safe_title}' title='{T['title_search_netflix']}' target='_blank' style='flex:1; background:var(--primary-color); color:white; padding:4px; border-radius:4px; text-decoration:none; font-size:0.7rem; font-weight:bold; text-align:center; transition: opacity 0.2s;' onmouseover='this.style.opacity=0.8' onmouseout='this.style.opacity=1'>{T['btn_netflix']}</a>
<a href='https://www.justwatch.com/us/search?q={safe_title}' title='{T['title_find_justwatch']}' target='_blank' style='flex:1; background:rgba(255,255,255,0.1); color:#fff; border: 1px solid rgba(255,255,255,0.2); padding:4px; border-radius:4px; text-decoration:none; font-size:0.7rem; font-weight:bold; text-align:center; transition: opacity 0.2s;' onmouseover='this.style.opacity=0.8' onmouseout='this.style.opacity=1'>{T['btn_where']}</a>
</div>"""
                    
                    html = f'''
                    <div class="simkl-card">
                        <div class="simkl-poster" style="{bg_style}">
                            <div class="simkl-badge badge-top-right">★ {score}</div>
                            <div class="simkl-badge badge-top-left">{year}</div>
                            <div class="simkl-overlay">
                                <div style="color: #e50914; font-weight: 800; font-size: 0.75rem; margin-bottom: 2px;">{rating}</div>
                                <div class="simkl-genres" style="margin-bottom: 4px;">{genres_str}</div>
                                <div style="color: #ccc; font-size: 0.7rem; font-style: italic; margin-bottom: 6px;">{director}</div>
                                <div style="color: #fff; font-size: 0.7rem; text-align: left; line-height: 1.3; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis;" title="{desc}">{desc}</div>
                                <div class="simkl-duration">{duration}</div>
                                {watch_link}
                            </div>
                        </div>
                        <div class="simkl-title" title="{row['title']}">{row['title']}</div>
                    </div>
                    '''
                    st.markdown(html, unsafe_allow_html=True)
                    
                    if st.button(T["btn_cast"], key=f"cat_btn_{genre}_{i}_{row.get('show_id', i)}", use_container_width=True):
                        set_node("movie", row.get('show_id', row['title']))
                        st.session_state.cast_button_clicked = True
                        st.rerun()
                    if st.button(T["btn_trailer"], key=f"cat_trl_{genre}_{i}_{row.get('show_id', i)}", use_container_width=True, type="primary"):
                        play_trailer_dialog(row)
        st.markdown("<hr style='margin: 24px 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  MAIN APPLICATION ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def render_top_bar(df=None):
    if df is None:
        return
        
    user = st.session_state.get('user', 'unknown')
    T = LANG[st.session_state.lang]
    
    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1.5, 1], gap="medium", vertical_alignment="center")
        
        with col1:
            search_query = st.text_input("Global Search", placeholder="🔍 Search catalog... (Press Enter to search)", label_visibility="collapsed", key="global_search_input")

        with col2:
            selected_lang = st.selectbox(T["language_selector"], options=list(LANG.keys()), index=list(LANG.keys()).index(st.session_state.lang), label_visibility="collapsed", key="top_lang")
            if selected_lang != st.session_state.lang:
                st.session_state.lang = selected_lang
                st.rerun()

        with col3:
            selected_theme = st.selectbox(T["ui_theme"], options=list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme), label_visibility="collapsed", key="top_theme")
            if selected_theme != st.session_state.theme:
                st.session_state.theme = selected_theme
                update_theme_config(selected_theme)
                st.rerun()

        with col4:
            st.markdown(f"<div style='text-align: right; line-height: 1.2;'><b style='font-size:0.9rem; color:var(--text-color);'>{user.capitalize()}</b><br><span style='font-size:0.7rem; color:var(--text-color); opacity:0.6;'>{user}@netflix.com</span></div>", unsafe_allow_html=True)

        with col5:
            if st.button("Log Out", use_container_width=True, type="primary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

@st.dialog("Detailed Data View", width="large")
def show_data_popup(df, filter_col, filter_val, match_type="exact"):
    with st.spinner("Analyzing and retrieving data..."):
        if "page_size" not in st.session_state:
            st.session_state.page_size = 50
            
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.markdown(f"### {filter_val if match_type != 'all' else T['metric_total']}")
        with header_col2:
            st.session_state.page_size = st.selectbox(T["items_per_page"], options=[10, 50, 100, 500, 1000], index=[10, 50, 100, 500, 1000].index(st.session_state.page_size), label_visibility="collapsed")
            
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
            st.markdown(f"<div style='text-align: center; padding-top: 8px; color: var(--text-color); opacity: 0.7;'>Page {st.session_state.popup_page + 1} of {total_pages}</div>", unsafe_allow_html=True)
        with col3:
            if st.button("Next ➡️", disabled=st.session_state.popup_page >= total_pages - 1, use_container_width=True):
                st.session_state.popup_page += 1
        with col4:
            csv_payload = display_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Data", data=csv_payload, file_name=f"netflix_export_{filter_col}.csv", mime="text/csv", use_container_width=True)


def process_selection(event, chart_key, filter_col, extract_key="x", match_type="exact", is_range=False, bin_size=10):
    if event and event.get("selection", {}).get("points"):
        pt = event["selection"]["points"][0]
        val = pt.get(extract_key)
        if val is None: val = pt.get("label", pt.get("x"))
        if is_range:
            raw_val = pt.get("x")
            try:
                val = float(raw_val)
            except (ValueError, TypeError):
                if isinstance(raw_val, str) and '-' in raw_val:
                    try: val = float(raw_val.split('-')[0])
                    except: val = 0.0
                else:
                    val = 0.0
            if st.session_state.chart_selections.get(chart_key) != val:
                st.session_state.chart_selections[chart_key] = val
                st.session_state.popup_request = {"col": filter_col, "val": (val-(bin_size/2), val+(bin_size/2)), "match": "range"}
                st.session_state.popup_page = 0
        else:
            if val is not None and st.session_state.chart_selections.get(chart_key) != str(val):
                st.session_state.chart_selections[chart_key] = str(val)
                st.session_state.popup_request = {"col": filter_col, "val": val, "match": match_type}
                st.session_state.popup_page = 0
    else:
        st.session_state.chart_selections[chart_key] = None


@st.cache_resource
def build_recommender_engine(df):
    vectorizer = TfidfVectorizer(stop_words='english')
    descriptions = df['description'].fillna('')
    tfidf_matrix = vectorizer.fit_transform(descriptions)
    return vectorizer, tfidf_matrix

def get_recommendations(query, vectorizer, tfidf_matrix, df, top_n=5):
    query_vec = vectorizer.transform([query])
    sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = sim_scores.argsort()[-top_n:][::-1]
    results = []
    for idx in top_indices:
        if sim_scores[idx] > 0:
            results.append({
                "title": df.iloc[idx]['title'],
                "description": df.iloc[idx]['description'],
                "score": sim_scores[idx] * 100,
                "type": df.iloc[idx]['type'],
                "genres": df.iloc[idx]['genres']
            })
    return results







def set_node(node_type, node_id):
    if st.session_state.current_node:
        st.session_state.node_history.append(st.session_state.current_node)
    st.session_state.current_node = {"type": node_type, "id": node_id}
    st.session_state.visible_limit = 6

def node_go_back():
    if st.session_state.node_history:
        st.session_state.current_node = st.session_state.node_history.pop()
    else:
        st.session_state.current_node = None
    st.session_state.visible_limit = 6

@st.cache_data(show_spinner=False, ttl=86400)
def get_image(query, is_movie=False):
    import urllib.request, urllib.parse, json, re, difflib
    
    def is_match(q, res):
        if not res: return False
        q = q.lower().replace("movie", "").strip()
        res = res.lower().strip()
        res = re.sub(r'\(\d{4}\)', '', res).strip()
        if q == res: return True
        
        def clean(s):
            s = re.sub(r'[^\w\s]', '', s)
            s = re.sub(r'^(the|a|an)\s+', '', s).strip()
            return s.replace(' ', '')
            
        q_clean = clean(q)
        res_clean = clean(res)
        if q_clean == res_clean: return True
        return difflib.SequenceMatcher(None, q_clean, res_clean).ratio() > 0.85

    # --- LEVEL 1: TVMAZE ---
    try:
        if is_movie:
            url = 'https://api.tvmaze.com/search/shows?q=' + urllib.parse.quote(query.replace(" movie", ""))
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=1).read().decode('utf-8'))
            for d in data:
                if d['show']['image'] and is_match(query, d['show']['name']):
                    return d['show']['image']['original']
        else:
            url = 'https://api.tvmaze.com/search/people?q=' + urllib.parse.quote(query)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=1).read().decode('utf-8'))
            for d in data:
                if d['person']['image'] and is_match(query, d['person']['name']):
                    return d['person']['image']['original']
    except Exception:
        pass

    # --- LEVEL 2: WIKIPEDIA ---
    try:
        if is_movie:
            url = 'https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch=' + urllib.parse.quote(query.replace(" movie", "")) + '&gsrlimit=3&prop=pageimages&format=json&pithumbsize=400'
        else:
            url = 'https://en.wikipedia.org/w/api.php?action=query&titles=' + urllib.parse.quote(query) + '&prop=pageimages&format=json&pithumbsize=400'
            
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = json.loads(urllib.request.urlopen(req, timeout=1).read().decode('utf-8'))
        if 'query' in data and 'pages' in data['query']:
            pages = data['query']['pages']
            for page_id in pages:
                if 'thumbnail' in pages[page_id] and is_match(query, pages[page_id].get('title', '')):
                    return pages[page_id]['thumbnail']['source']
    except Exception:
        pass
        
    # --- LEVEL 3: TMDB SCRAPER ---
    try:
        if not is_movie:
            url = 'https://www.themoviedb.org/search/person?query=' + urllib.parse.quote(query)
        else:
            url = 'https://www.themoviedb.org/search?query=' + urllib.parse.quote(query.replace(" movie", ""))
            
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=1).read().decode('utf-8')
        img_tags = re.findall(r"""<img[^>]+src=["']([^"']+\.jpg)["'][^>]+alt=["']([^"']+)["']""", html)
        if not img_tags:
            img_tags = re.findall(r"""<img[^>]+alt=["']([^"']+)["'][^>]+src=["']([^"']+\.jpg)["']""", html)
            img_tags = [(src, alt) for alt, src in img_tags]
            
        for src, alt in img_tags:
            if '/t/p/' in src and is_match(query, alt):
                img_url = src
                if img_url.startswith('/'): img_url = "https://media.themoviedb.org" + img_url
                img_url = re.sub(r'/w[0-9]+_and_h[0-9]+_[^/]+/', '/w600_and_h900_bestv2/', img_url)
                return img_url
    except Exception:
        pass
        
    return None

def render_cast_network(df):
    import pandas as pd
    T = LANG[st.session_state.lang]
    st.markdown("### 🔍 Global Deep Search")
    st.markdown("Explore the Netflix universe! Search for any actor to traverse their filmography network globally.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search for an actor or movie...", key="actor_search")
    with col2:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        if st.button(T.get("cast_search_btn", "Search Actor"), use_container_width=True):
                actor_mask = df['cast'].str.contains(search_query, case=False, na=False)
                all_cast = set()
                if actor_mask.any():
                    for c_str in df[actor_mask]['cast'].dropna():
                        for c in c_str.split(','):
                            all_cast.add(c.strip())
                closest_actors = [("actor", c) for c in all_cast if search_query.lower() in c.lower()]
                
                movie_mask = df['title'].str.contains(search_query, case=False, na=False)
                closest_movies = [("movie", t) for t in df[movie_mask]['title'].dropna() if search_query.lower() in t.lower()]
                
                closest = closest_actors + closest_movies
                if closest:
                    if len(closest) == 1 or search_query.lower() == closest[0][1].lower():
                        st.session_state.node_history = []
                        st.session_state.current_node = {"type": closest[0][0], "id": closest[0][1]}
                        st.session_state.visible_limit = 6
                        st.session_state.ambiguous_results = None
                    else:
                        closest.sort(key=lambda x: len(x[1]))
                        st.session_state.ambiguous_results = closest[:8]
                        st.session_state.current_node = None
    
    if st.session_state.get("ambiguous_results"):
        st.markdown(f"**Found multiple matches for \"{search_query}\". Which one did you mean?**")
        ambig_cols = st.columns(4)
        for idx, (ntype, name) in enumerate(st.session_state.ambiguous_results):
            icon = "🎭" if ntype == "actor" else "🎬"
            if ambig_cols[idx % 4].button(f"{icon} {name}", key=f"ambig_{ntype}_{name}", use_container_width=True):
                st.session_state.node_history = []
                st.session_state.current_node = {"type": ntype, "id": name}
                st.session_state.visible_limit = 6
                st.session_state.ambiguous_results = None
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
                        
    if st.session_state.node_history:
        if st.button(f"⬅ {T.get('cast_go_back', 'Go Back')}"):
            node_go_back()
            st.rerun()
            
    if st.session_state.current_node:
        n_type = st.session_state.current_node["type"]
        n_id = st.session_state.current_node["id"]
        
        st.divider()
        
        if n_type == "actor":
            ac1, ac2 = st.columns([1, 3])
            img_url = get_image(n_id, is_movie=False)
            with ac1:
                if img_url:
                    st.markdown(f'<div style="width:100%; aspect-ratio: 1/1; background: url({img_url}) center/cover; border-radius: 8px;"></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='width:100%; aspect-ratio: 1/1; background:#333; display:flex; align-items:center; justify-content:center; border-radius:8px;'><span style='font-size:48px'>🎭</span></div>", unsafe_allow_html=True)
            with ac2:
                st.markdown(f"## {n_id}")
                actor_movies = df[df['cast'].str.contains(n_id, case=False, na=False, regex=False)]
                st.caption(f"{T.get('cast_total_titles', 'Total Titles')}: {len(actor_movies)}")
            
            st.divider()
            st.markdown(f"#### {T.get('cast_filmography', 'Filmography')}")
            cols = st.columns(4)
            limit = st.session_state.get("visible_limit", 4)
            movie_list = list(actor_movies.itertuples())
            for idx, row in enumerate(movie_list[:limit]):
                with cols[idx % 4]:
                    with st.container(border=True):
                        m_img = get_image(f"{row.title} movie", is_movie=True)
                        if m_img:
                            st.markdown(f'<div style="width:100%; aspect-ratio: 2/3; background: url({m_img}) center/cover; border-radius: 6px; margin-bottom: 8px;"></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='width:100%; aspect-ratio: 2/3; background:linear-gradient(45deg, #2b00ff, var(--primary-color)); display:flex; align-items:center; justify-content:center; border-radius:6px; margin-bottom: 8px;'><span style='font-size:14px; font-weight:bold; color:white; text-align:center;'>{row.title}</span></div>", unsafe_allow_html=True)
                        if st.button(f"🎬 {row.release_year}", key=f"mov_{idx}_{row.show_id}", use_container_width=True):
                            set_node("movie", row.show_id)
                            st.rerun()
                            
            if len(movie_list) > limit:
                if st.button("🔽 See More Movies", use_container_width=True):
                    st.session_state.visible_limit += 4
                    st.rerun()
                        
            st.divider()
            st.markdown(f"#### {T.get('cast_costars', 'Frequent Co-Stars')}")
            co_stars = {}
            for cast_str in actor_movies['cast'].dropna():
                for co_star in cast_str.split(','):
                    c = co_star.strip()
                    if c and c != n_id:
                        co_stars[c] = co_stars.get(c, 0) + 1
            
            top_costars = sorted(co_stars.items(), key=lambda x: x[1], reverse=True)
            if top_costars:
                c_cols = st.columns(6)
                limit_cs = st.session_state.get("visible_limit", 4)
                for i, (cs, count) in enumerate(top_costars[:limit_cs]):
                    with c_cols[i % 6]:
                        with st.container(border=True):
                            cs_img = get_image(cs, is_movie=False)
                            if cs_img:
                                st.markdown(f'<div style="width:100%; aspect-ratio: 1/1; background: url({cs_img}) center/cover; border-radius: 50%; margin-bottom: 8px;"></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='width:100%; aspect-ratio: 1/1; background:#333; display:flex; align-items:center; justify-content:center; border-radius:50%; margin-bottom: 8px;'><span style='font-size:32px'>🎭</span></div>", unsafe_allow_html=True)
                            if st.button(f"{cs} ({count})", key=f"cs_{i}", use_container_width=True):
                                set_node("actor", cs)
                                st.rerun()
                if len(top_costars) > limit_cs:
                    if st.button("🔽 See More Co-Stars", use_container_width=True):
                        st.session_state.visible_limit += 6
                        st.rerun()
            else:
                st.info(T.get("cast_no_costars", "No co-stars found."))
                
        elif n_type == "movie":
            matches = df[df['show_id'] == n_id]
            if matches.empty:
                matches = df[df['title'] == n_id]
            movie_row = matches.iloc[0]
            
            mc1, mc2 = st.columns([1, 2])
            m_img = get_image(f"{movie_row.title} movie", is_movie=True)
            with mc1:
                if m_img:
                    st.markdown(f'<div style="width:100%; aspect-ratio: 2/3; background: url({m_img}) center/cover; border-radius: 12px; box-shadow: 0 10px 20px rgba(0,0,0,0.3);"></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="aspect-ratio: 2/3; width: 100%; background: linear-gradient(135deg, var(--primary-color) 0%, #2b00ff 100%); 
                                border-radius: 12px; display: flex; align-items: center; justify-content: center;
                                box-shadow: 0 10px 20px rgba(0,0,0,0.3); padding: 20px; text-align: center;">
                        <h2 style="color: white; font-size: 28px; font-weight: 800; text-shadow: 0 2px 10px rgba(0,0,0,0.5);">{movie_row.title}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
            with mc2:
                st.markdown(f"## {movie_row.title}")
                st.markdown(f"**{movie_row.release_year}** • {movie_row.type} • **{movie_row.rating}** • {movie_row.duration}")
                st.markdown(f"**{T.get('genre', 'Genre')}:** {movie_row.genres}")
                import pandas as pd
                if pd.notna(movie_row.director):
                    st.markdown(f"**{T.get('director', 'Director')}:** {movie_row.director}")
                st.markdown("---")
                st.markdown(f"*{movie_row.description}*")
                
            st.divider()
            st.markdown(f"#### 🎭 Cast")
            if pd.notna(movie_row.cast):
                cast_list = [c.strip() for c in str(movie_row.cast).split(',')]
                c_cols = st.columns(6)
                limit_mc = st.session_state.get("visible_limit", 4)
                for i, c in enumerate(cast_list[:limit_mc]):
                    with c_cols[i % 6]:
                        with st.container(border=True):
                            c_img = get_image(c, is_movie=False)
                            if c_img:
                                st.markdown(f'<div style="width:100%; aspect-ratio: 1/1; background: url({c_img}) center/cover; border-radius: 50%; margin-bottom: 8px;"></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='width:100%; aspect-ratio: 1/1; background:#333; display:flex; align-items:center; justify-content:center; border-radius:50%; margin-bottom: 8px;'><span style='font-size:32px'>🎭</span></div>", unsafe_allow_html=True)
                            if st.button(c, key=f"mcast_{i}", use_container_width=True):
                                set_node("actor", c)
                                st.rerun()
                if len(cast_list) > limit_mc:
                    if st.button("🔽 See More Cast", use_container_width=True):
                        st.session_state.visible_limit += 6
                        st.rerun()
            else:
                st.info("No cast information available for this title.")

def render_top_metrics_dashboard(df: pd.DataFrame):
    total_titles = len(df)
    total_movies = len(df[df['type'] == 'Movie'])
    total_shows = len(df[df['type'] == 'TV Show'])
    total_directors = df['director'].nunique()

    st.markdown(f'''
    <div style="display: flex; gap: 24px; margin-bottom: 32px; flex-wrap: wrap;">
        <!-- Highlighted Card -->
        <div style="flex: 1; min-width: 200px; background: var(--primary-color); border-radius: 16px; padding: 24px; box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3); display: flex; flex-direction: column; justify-content: center; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 16px; right: 16px; background: rgba(255,255,255,0.2); border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: white;">↗</div>
            <div style="color: white; opacity: 0.9; font-size: 0.9rem; font-weight: 500; margin-bottom: 8px;">Total Titles</div>
            <div style="color: white; font-size: 2.8rem; font-weight: 700; line-height: 1; font-family: 'Bebas Neue', sans-serif;">{total_titles:,}</div>
            <div style="color: white; opacity: 0.7; font-size: 0.75rem; margin-top: 12px; display: flex; align-items: center; gap: 4px;"><span style="color: #4ade80;">↑</span> Entire Catalog</div>
        </div>
        <!-- Card 2 -->
        <div style="flex: 1; min-width: 200px; background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 16px; padding: 24px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: center; position: relative;">
            <div style="position: absolute; top: 16px; right: 16px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: var(--text-color); opacity: 0.5;">↗</div>
            <div style="color: var(--text-color); opacity: 0.7; font-size: 0.9rem; font-weight: 500; margin-bottom: 8px;">Movies</div>
            <div style="color: var(--text-color); font-size: 2.8rem; font-weight: 700; line-height: 1; font-family: 'Bebas Neue', sans-serif;">{total_movies:,}</div>
            <div style="color: var(--text-color); opacity: 0.5; font-size: 0.75rem; margin-top: 12px; display: flex; align-items: center; gap: 4px;"><span style="color: #4ade80;">↑</span> Feature films</div>
        </div>
        <!-- Card 3 -->
        <div style="flex: 1; min-width: 200px; background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 16px; padding: 24px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: center; position: relative;">
            <div style="position: absolute; top: 16px; right: 16px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: var(--text-color); opacity: 0.5;">↗</div>
            <div style="color: var(--text-color); opacity: 0.7; font-size: 0.9rem; font-weight: 500; margin-bottom: 8px;">TV Shows</div>
            <div style="color: var(--text-color); font-size: 2.8rem; font-weight: 700; line-height: 1; font-family: 'Bebas Neue', sans-serif;">{total_shows:,}</div>
            <div style="color: var(--text-color); opacity: 0.5; font-size: 0.75rem; margin-top: 12px; display: flex; align-items: center; gap: 4px;"><span style="color: #4ade80;">↑</span> Series & miniseries</div>
        </div>
        <!-- Card 4 -->
        <div style="flex: 1; min-width: 200px; background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 16px; padding: 24px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: center; position: relative;">
            <div style="position: absolute; top: 16px; right: 16px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: var(--text-color); opacity: 0.5;">↗</div>
            <div style="color: var(--text-color); opacity: 0.7; font-size: 0.9rem; font-weight: 500; margin-bottom: 8px;">Directors</div>
            <div style="color: var(--text-color); font-size: 2.8rem; font-weight: 700; line-height: 1; font-family: 'Bebas Neue', sans-serif;">{total_directors:,}</div>
            <div style="color: var(--text-color); opacity: 0.5; font-size: 0.75rem; margin-top: 12px; display: flex; align-items: center; gap: 4px;"><span style="color: #4ade80;">↑</span> Unique creators</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def main():
    st.markdown('''<style>
        /* Premium UI Upgrades */
        
        /* Typography */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Outfit', sans-serif !important;
        }
        
        /* Glassmorphic Navbar (assuming there's a top container we can target) */
        header[data-testid="stHeader"] {
            background: rgba(20, 20, 20, 0.7) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            transition: background 0.3s ease;
        }
        
        /* Smooth Micro-animations for Cards */
        .simkl-card {
            transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94), box-shadow 0.3s ease !important;
            border: 1px solid rgba(255, 255, 255, 0.03) !important;
        }
        .simkl-card:hover {
            transform: scale(1.05) translateY(-5px) !important;
            box-shadow: 0 15px 30px rgba(0,0,0,0.8), 0 0 15px rgba(229, 9, 20, 0.3) !important;
            border-color: rgba(229, 9, 20, 0.5) !important;
            z-index: 10;
        }
        
        /* Button Hover Glows */
        .stButton>button {
            transition: all 0.2s ease !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.4) !important;
        }
        .stButton>button[kind="primary"]:hover {
            box-shadow: 0 5px 20px rgba(229, 9, 20, 0.6) !important;
            filter: brightness(1.2);
        }
        
        /* Header typography enhancements */
        .section-header {
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5) !important;
        }
        
        /* Custom scrollbar for entire app to match Netflix */
        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #141414;
        }
        ::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 5px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #e50914;
        }
</style>''', unsafe_allow_html=True)
    if "demo_credentials" not in st.session_state:
        st.session_state.demo_credentials = {"admin": "admin123"}
    if "popup_request" not in st.session_state:
        st.session_state.popup_request = None
    if "current_node" not in st.session_state:
        st.session_state.current_node = None
    if "node_history" not in st.session_state:
        st.session_state.node_history = []
    if "chart_selections" not in st.session_state:
        st.session_state.chart_selections = {}

    if not check_auth():
        render_top_bar(None)
        render_login_screen()
        return

    # --- STATE INTERCEPTORS ---
    if st.session_state.get('cast_button_clicked'):
        st.session_state.active_page = "Deep Dive"
        st.session_state.nav_radio = "Deep Dive"
        st.session_state.cast_button_clicked = False

    if st.session_state.get('view_all_clicked'):
        genre = st.session_state.view_all_clicked
        st.session_state.active_page = "Data Explorer"
        st.session_state.nav_radio = "Data Explorer"
        st.session_state['tab3_search_input'] = genre
        st.session_state['tab3_last_search_query'] = genre
        st.session_state.view_all_clicked = None

    current_global_search = st.session_state.get('global_search_input')
    if current_global_search and current_global_search != st.session_state.get('last_global_search'):
        st.session_state.active_page = "Data Explorer"
        st.session_state.nav_radio = "Data Explorer"
        st.session_state['tab3_search_input'] = current_global_search
        st.session_state['tab3_last_search_query'] = current_global_search
        st.session_state['last_global_search'] = current_global_search

    df = load_and_preprocess_data()
    filtered_df = render_sidebar(df)
    


        # --- Global Header ---
    render_top_bar(filtered_df)

    page = st.session_state.active_page
    T = LANG[st.session_state.lang]

    if page == "Dashboard":
        render_top_metrics_dashboard(filtered_df)
        
        st.markdown(f'<div class="section-header" style="margin-top: 16px;">{T["header_trend"]}</div>', unsafe_allow_html=True)
        with st.container(border=True):
            ev_hero = st.plotly_chart(chart_year_ingestion(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev_hero, "tab1_year", "year_added", extract_key="x")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown(f'<div class="section-header">{T["header_dist"]}</div>', unsafe_allow_html=True)
            with st.container(border=True):
                ev_split = st.plotly_chart(chart_content_split(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
                process_selection(ev_split, "tab1_split", "type", extract_key="x")
        with col2:
            st.markdown(f'<div class="section-header">Top Categories</div>', unsafe_allow_html=True)
            with st.container(border=True):
                ev_genres = st.plotly_chart(chart_top_genres(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
                process_selection(ev_genres, "tab1_genres", "genres", extract_key="y", match_type="contains")

        col3, col4 = st.columns(2, gap="large")
        with col3:
            st.markdown(f'<div class="section-header">{T["header_ratings"]}</div>', unsafe_allow_html=True)
            with st.container(border=True):
                ev_rating = st.plotly_chart(chart_rating_distribution(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
                process_selection(ev_rating, "tab1_ratings", "rating", extract_key="x", match_type="exact", is_range=False)
        with col4:
            st.markdown(f'<div class="section-header">Top Creators</div>', unsafe_allow_html=True)
            with st.container(border=True):
                ev_directors = st.plotly_chart(chart_top_directors(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
                process_selection(ev_directors, "tab1_directors", "director", extract_key="y", match_type="contains")
                
        st.markdown(f'<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)
        render_metric_cards(filtered_df)

    elif page == "Deep Dive":
        st.markdown(f'<div class="section-header" style="margin-top: 16px;">{T["header_granular"]}</div>', unsafe_allow_html=True)
        with st.container(border=True):
            ev_m = st.plotly_chart(chart_top_countries_map(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev_m, "tab2_map", "primary_country", extract_key="location", match_type="contains")
        
        st.divider()
        render_cast_network(df)
        
        col_dd1, col_dd2 = st.columns(2, gap="large")
        with col_dd1:
            st.markdown(f'<div class="section-header">Top Cast</div>', unsafe_allow_html=True)
            with st.container(border=True):
                ev_c = st.plotly_chart(chart_top_cast(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
                process_selection(ev_c, "tab2_cast", "cast", extract_key="y", match_type="contains")
        with col_dd2:
            st.markdown(f'<div class="section-header">Duration Trends</div>', unsafe_allow_html=True)
            with st.container(border=True):
                ev_d = st.plotly_chart(chart_duration_scatter(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
                process_selection(ev_d, "tab2_scatter", "release_year", extract_key="x")
            
        st.markdown(f'<div class="section-header">Runtime Distribution</div>', unsafe_allow_html=True)
        with st.container(border=True):
            ev_r = st.plotly_chart(chart_runtime_distribution(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev_r, "tab2_histogram", "duration_minutes", is_range=True)

    elif page == "Data Explorer":
        col_ex1, col_ex2 = st.columns([2, 1], gap="large")
        with col_ex1:
            st.markdown(f'<div class="section-header" style="margin-top: 16px;">{T.get("cat_header", "Catalog Search & Export")}</div>', unsafe_allow_html=True)
            with st.container(border=True):
                render_catalog_explorer(filtered_df, key_prefix='tab3_')
        with col_ex2:
            st.markdown(f'<div class="section-header" style="margin-top: 16px;">{T.get("feed_header", "Live Ingestion Feed")}</div>', unsafe_allow_html=True)
            render_recent_feed(filtered_df)

    elif page == "Top Categories":
        st.markdown("<h2 style='margin-bottom: 24px; font-weight: 600;'>🎬 Top Categories</h2>", unsafe_allow_html=True)
        render_top_categories(filtered_df)

    elif page == "My List":
        render_watchlist_page()


    st.markdown(
        f'''
        <div style="text-align: center; padding: 24px 0 12px; margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.1);">
            <span style="color: var(--text-color); opacity: 0.5; font-size: 0.8rem; font-weight: 500; letter-spacing: 0.5px;">
                Netflix Content Insights Engine &nbsp;|&nbsp; Enterprise Dashboard
            </span>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    if st.session_state.popup_request:
        req = st.session_state.popup_request
        show_data_popup(filtered_df, req["col"], req["val"], req["match"])
        st.session_state.popup_request = None


if __name__ == "__main__":
    main()
