def hex_to_rgba(hex_color, alpha=0.1):
    hex_color = hex_color.lstrip('#')
    return f'rgba({int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}, {alpha})'



import streamlit as st
import pandas as pd
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

</style>
"""



LANG = {
    "English": {
        "language_selector": "Language",
        "logged_in_as": "Logged in as",
        "ui_theme": "UI Theme",
        "log_out": "Log Out",
        "filter_controls": "Filter Controls",
        "release_year": "Release Year Range",
        "content_type": "Content Type",
        "movie": "Movie",
        "tv_show": "TV Show",
        "maturity_rating": "Maturity Rating",
        "choose_options": "Choose options",
        "production_country": "Production Country",
        "main_title": "Content Insights Engine",
        "main_desc": "Enterprise analytics dashboard. Adjust filters in the sidebar to explore streaming content trends.",
        "tab_overview": "Overview",
        "tab_deep_dive": "Content Deep Dive",
        "tab_data": "Data Explorer", "tab_ai": "🤖 AI Recommender", "ai_desc": "Describe what you want to watch in natural language, and our AI will find the best matches based on plot descriptions!",         "cat_search_prompt": "Search Titles, Directors, or Genres",
        "cat_search_placeholder": "e.g. Sci-Fi, Christopher Nolan",
        "cat_showing_results": "Showing {0:,} results",
        "cat_header": "Catalog Search & Export",
        "feed_header": "Live Ingestion Feed",
        "feed_unknown": "Unknown Date",
        "col_title": "Title",
        "col_type": "Type",
        "col_director": "Director",
        "col_country": "Country",
        "col_year": "Release Year",
        "col_rating": "Rating",
        "col_duration": "Duration",
        "col_genres": "Genres",
        "metric_total": "Total Content",
        "metric_genres": "Unique Genres",
        "metric_type": "Content Type",
                "cat_search_prompt": "શીર્ષકો, દિગ્દર્શકો અથવા શૈલીઓ શોધો",
        "cat_search_placeholder": "દા.ત. સાય-ફાઇ, ક્રિસ્ટોફર નોલાન",
        "cat_showing_results": "{0:,} પરિણામો બતાવી રહ્યાં છીએ",
        "cat_header": "કેટલોગ શોધ અને નિકાસ",
        "feed_header": "લાઇવ ઇન્જેશન ફીડ",
        "feed_unknown": "અજ્ઞાત તારીખ",
        "col_title": "શીર્ષક",
        "col_type": "પ્રકાર",
        "col_director": "દિગ્દર્શક",
        "col_country": "દેશ",
        "col_year": "પ્રકાશન વર્ષ",
        "col_rating": "રેટિંગ",
        "col_duration": "સમયગાળો",
        "col_genres": "શૈલીઓ",
        "metric_total": "કુલ સામગ્રી",
        "metric_genres": "અનન્ય શૈલીઓ",
        "metric_type": "સામગ્રી પ્રકાર",
                "cat_search_prompt": "शीर्षक, निर्देशक या शैलियां खोजें",
        "cat_search_placeholder": "उदा. साई-फाई, क्रिस्टोफर नोलन",
        "cat_showing_results": "{0:,} परिणाम दिखा रहे हैं",
        "cat_header": "कैटलॉग खोज और निर्यात",
        "feed_header": "लाइव इंजेशन फ़ीड",
        "feed_unknown": "अज्ञात तिथि",
        "col_title": "शीर्षक",
        "col_type": "प्रकार",
        "col_director": "निर्देशक",
        "col_country": "देश",
        "col_year": "रिलीज़ वर्ष",
        "col_rating": "रेटिंग",
        "col_duration": "अवधि",
        "col_genres": "शैलियां",
        "metric_total": "कुल सामग्री",
        "metric_genres": "अद्वितीय शैलियां",
        "metric_type": "सामग्री का प्रकार",
                "cat_search_prompt": "Buscar Títulos, Directores o Géneros",
        "cat_search_placeholder": "ej. Ciencia Ficción, Christopher Nolan",
        "cat_showing_results": "Mostrando {0:,} resultados",
        "cat_header": "Búsqueda y Exportación",
        "feed_header": "Feed de Ingestión en Vivo",
        "feed_unknown": "Fecha Desconocida",
        "col_title": "Título",
        "col_type": "Tipo",
        "col_director": "Director",
        "col_country": "País",
        "col_year": "Año de Lanzamiento",
        "col_rating": "Clasificación",
        "col_duration": "Duración",
        "col_genres": "Géneros",
        "metric_total": "Contenido Total",
        "metric_genres": "Géneros Únicos",
        "metric_type": "Tipo de Contenido",
        "ai_search_prompt": "🔍 Search query...", "ai_search_placeholder": "e.g., A spooky detective movie with a twist ending", "ai_no_match": "No matches found. Try describing it differently!",
        "metric_total": "Total Content",
        "metric_movies": "Movies",
        "metric_shows": "TV Shows",
        "metric_directors": "Total Directors",
        "metric_cast": "Unique Cast",
        "metric_countries": "Countries", "metric_genres": "Unique Genres",
        "chart_distribution": "Content Distribution",
        "chart_yoy": "Year-over-Year Ingestion",
        "chart_genres": "Top 10 Genres",
        "chart_rating": "Maturity Rating Distribution",
        "chart_directors": "Top 10 Directors",
        "chart_map": "Global Content Map",
        "chart_cast": "Top 20 Cast Members",
        "chart_duration": "Movie Duration vs Release Year",
        "trend_10y": "Content Release Trend (10 Years)",
        "search_titles": "Search Titles",
        "items_per_page": "Items per page",
        "page": "Page",
        "of": "of",
        "download_csv": "Download CSV", "count": "Count", "titles": "Titles", "genre": "Genre", "rating": "Rating", "director": "Director", "duration_minutes": "Duration (min)", "year_added": "Year Added", "release_year": "Release Year", "header_trend": "Content Release Trend (10 Years)", "header_dist": "Distribution & Genres", "header_ratings": "Ratings & Directors", "header_granular": "Granular Analysis", "dataset_info": "Dataset Info", "source": "Source", "total_records": "Total Records", "year_span": "Year Span"
    },
    "Hindi": {
        "language_selector": "भाषा (Language)",
        "logged_in_as": "लॉग इन किया है",
        "ui_theme": "यूआई थीम",
        "log_out": "लॉग आउट",
        "filter_controls": "फ़िल्टर नियंत्रण",
        "release_year": "रिलीज़ वर्ष सीमा",
        "content_type": "सामग्री का प्रकार",
        "movie": "फ़िल्म",
        "tv_show": "टीवी शो",
        "maturity_rating": "परिपक्वता रेटिंग",
        "choose_options": "विकल्प चुनें",
        "production_country": "उत्पादन देश",
        "main_title": "सामग्री अंतर्दृष्टि इंजन",
        "main_desc": "एंटरप्राइज़ एनालिटिक्स डैशबोर्ड। स्ट्रीमिंग सामग्री रुझानों का पता लगाने के लिए साइडबार में फ़िल्टर समायोजित करें।",
        "tab_overview": "अवलोकन",
        "tab_deep_dive": "सामग्री विश्लेषण",
        "tab_data": "डेटा एक्सप्लोरर", "tab_ai": "🤖 एआई अनुशंसाकर्ता", "ai_desc": "प्राकृतिक भाषा में बताएं कि आप क्या देखना चाहते हैं, और हमारा एआई प्लॉट विवरण के आधार पर सर्वोत्तम मेल खोजेगा!", "ai_search_prompt": "🔍 खोज क्वेरी...", "ai_search_placeholder": "उदा., एक ट्विस्ट एंडिंग वाली डरावनी जासूसी फिल्म", "ai_no_match": "कोई मेल नहीं मिला. इसे अलग तरह से वर्णित करने का प्रयास करें!",
        "metric_total": "कुल सामग्री",
        "metric_movies": "फिल्में",
        "metric_shows": "टीवी शो",
        "metric_directors": "कुल निर्देशक",
        "metric_cast": "अद्वितीय कास्ट",
        "metric_countries": "देश", "metric_genres": "अद्वितीय शैलियां",
        "chart_distribution": "सामग्री वितरण",
        "chart_yoy": "साल-दर-साल वृद्धि",
        "chart_genres": "शीर्ष 10 शैलियां",
        "chart_rating": "परिपक्वता रेटिंग वितरण",
        "chart_directors": "शीर्ष 10 निर्देशक",
        "chart_map": "वैश्विक सामग्री मानचित्र",
        "chart_cast": "शीर्ष 20 कास्ट सदस्य",
        "chart_duration": "मूवी अवधि बनाम रिलीज़ वर्ष",
        "trend_10y": "सामग्री रिलीज ट्रेंड (10 वर्ष)",
        "search_titles": "शीर्षक खोजें",
        "items_per_page": "प्रति पृष्ठ आइटम",
        "page": "पृष्ठ",
        "of": "का",
        "download_csv": "सीएसवी डाउनलोड करें", "count": "गिनती", "titles": "शीर्षक", "genre": "शैलियां", "rating": "रेटिंग", "director": "निर्देशक", "duration_minutes": "अवधि (मिनट)", "year_added": "जोड़ा गया वर्ष", "release_year": "रिलीज़ वर्ष", "header_trend": "सामग्री रिलीज ट्रेंड (10 वर्ष)", "header_dist": "वितरण और शैलियां", "header_ratings": "रेटिंग और निर्देशक", "header_granular": "विस्तृत विश्लेषण", "dataset_info": "डेटासेट जानकारी", "source": "स्रोत", "total_records": "कुल रिकॉर्ड", "year_span": "वर्ष अवधि"
    },
    "Gujarati": {
        "language_selector": "ભાષા (Language)",
        "logged_in_as": "તરીકે લૉગ ઇન કર્યું છે",
        "ui_theme": "યુઆઇ થીમ",
        "log_out": "લોગ આઉટ",
        "filter_controls": "ફિલ્ટર નિયંત્રણો",
        "release_year": "પ્રકાશન વર્ષ શ્રેણી",
        "content_type": "સામગ્રીનો પ્રકાર",
        "movie": "ફિલ્મ",
        "tv_show": "ટીવી શો",
        "maturity_rating": "પરિપક્વતા રેટિંગ",
        "choose_options": "વિકલ્પો પસંદ કરો",
        "production_country": "ઉત્પાદન દેશ",
        "main_title": "સામગ્રી આંતરદૃષ્ટિ એન્જિન",
        "main_desc": "એન્ટરપ્રાઇઝ એનાલિટિક્સ ડેશબોર્ડ. સ્ટ્રીમિંગ સામગ્રી વલણોનું અન્વેષણ કરવા માટે સાઇડબારમાં ફિલ્ટર્સને સમાયોજિત કરો.",
        "tab_overview": "ઝાંખી",
        "tab_deep_dive": "સામગ્રી વિશ્લેષણ",
        "tab_data": "ડેટા એક્સપ્લોરર", "tab_ai": "🤖 એઆઈ ભલામણકર્તા", "ai_desc": "કુદરતી ભાષામાં તમે શું જોવા માંગો છો તેનું વર્ણન કરો, અને અમારું AI પ્લોટ વર્ણનોના આધારે શ્રેષ્ઠ મેળ શોધશે!", "ai_search_prompt": "🔍 શોધ ક્વેરી...", "ai_search_placeholder": "દા.ત., ટ્વિસ્ટ અંત સાથેની ડરામણી ડિટેક્ટીવ મૂવી", "ai_no_match": "કોઈ મેળ મળ્યો નથી. તેને અલગ રીતે વર્ણવવાનો પ્રયાસ કરો!",
        "metric_total": "કુલ સામગ્રી",
        "metric_movies": "ફિલ્મો",
        "metric_shows": "ટીવી શો",
        "metric_directors": "કુલ દિગ્દર્શકો",
        "metric_cast": "અનન્ય કાસ્ટ",
        "metric_countries": "દેશો", "metric_genres": "અનન્ય શૈલીઓ",
        "chart_distribution": "સામગ્રી વિતરણ",
        "chart_yoy": "વર્ષ-દર-વર્ષ વધારો",
        "chart_genres": "ટોચની 10 શૈલીઓ",
        "chart_rating": "પરિપક્વતા રેટિંગ વિતરણ",
        "chart_directors": "ટોચના 10 દિગ્દર્શકો",
        "chart_map": "વૈશ્વિક સામગ્રી નકશો",
        "chart_cast": "ટોચના 20 કાસ્ટ સભ્યો",
        "chart_duration": "મૂવી અવધિ વિ પ્રકાશન વર્ષ",
        "trend_10y": "સામગ્રી પ્રકાશન વલણ (10 વર્ષ)",
        "search_titles": "શીર્ષકો શોધો",
        "items_per_page": "પૃષ્ઠ દીઠ આઇટમ્સ",
        "page": "પૃષ્ઠ",
        "of": "નું",
        "download_csv": "સીએસવી ડાઉનલોડ કરો", "count": "ગણતરી", "titles": "શીર્ષકો", "genre": "શૈલીઓ", "rating": "રેટિંગ", "director": "દિગ્દર્શક", "duration_minutes": "અવધિ (મિનિટ)", "year_added": "ઉમેરાયેલ વર્ષ", "release_year": "પ્રકાશન વર્ષ", "header_trend": "સામગ્રી પ્રકાશન વલણ (10 વર્ષ)", "header_dist": "વિતરણ અને શૈલીઓ", "header_ratings": "રેટિંગ્સ અને દિગ્દર્શકો", "header_granular": "વિગતવાર વિશ્લેષણ", "dataset_info": "ડેટાસેટ માહિતી", "source": "સ્ત્રોત", "total_records": "કુલ રેકોર્ડ્સ", "year_span": "વર્ષનો સમયગાળો"
    },
    "Spanish": {
        "language_selector": "Idioma (Language)",
        "logged_in_as": "Conectado como",
        "ui_theme": "Tema de UI",
        "log_out": "Cerrar sesión",
        "filter_controls": "Controles de filtro",
        "release_year": "Rango de año de lanzamiento",
        "content_type": "Tipo de contenido",
        "movie": "Película",
        "tv_show": "Programa de TV",
        "maturity_rating": "Clasificación por edades",
        "choose_options": "Elegir opciones",
        "production_country": "País de producción",
        "main_title": "Motor de Análisis de Contenido",
        "main_desc": "Panel de análisis empresarial. Ajuste los filtros en la barra lateral para explorar tendencias.",
        "tab_overview": "Resumen",
        "tab_deep_dive": "Análisis profundo",
        "tab_data": "Explorador de datos",
        "metric_total": "Contenido total",
        "metric_movies": "Películas",
        "metric_shows": "Programas de TV",
        "metric_directors": "Directores",
        "metric_cast": "Elenco",
        "metric_countries": "Países", "metric_genres": "Géneros Únicos",
        "chart_distribution": "Distribución de contenido",
        "chart_yoy": "Ingresos año tras año",
        "chart_genres": "Top 10 Géneros",
        "chart_rating": "Distribución de clasificación",
        "chart_directors": "Top 10 Directores",
        "chart_map": "Mapa de contenido global",
        "chart_cast": "Top 20 Miembros del elenco",
        "chart_duration": "Duración vs Año",
        "trend_10y": "Tendencias (10 Años)",
        "search_titles": "Buscar títulos",
        "items_per_page": "Artículos por página",
        "page": "Página",
        "of": "de",
        "download_csv": "Descargar CSV", "count": "Cantidad", "titles": "Títulos", "genre": "Género", "rating": "Clasificación", "director": "Director", "duration_minutes": "Duración (min)", "year_added": "Año Añadido", "release_year": "Año de Lanzamiento", "header_trend": "Tendencia de lanzamientos (10 Años)", "header_dist": "Distribución y Géneros", "header_ratings": "Calificaciones y Directores", "header_granular": "Análisis Granular", "dataset_info": "Info del Dataset", "source": "Fuente", "total_records": "Registros Totales", "year_span": "Lapso de Años"
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

@st.cache_data(show_spinner=False)
def load_and_preprocess_data():
    df = pd.read_csv("netflix_titles_2025.csv")
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
    st.markdown(f"<p style='color:gray; font-size:0.9rem;'>Register a new demo account.</p>", unsafe_allow_html=True)
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
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        
        
        
        
        

        /* Netflix-Themed Blobs */
        .blob-1 {
            position: absolute;
            top: 15%;
            right: 20%;
            width: 350px;
            height: 350px;
            background: linear-gradient(135deg, var(--primary-color) 0%, #83050C 100%);
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
            background: linear-gradient(135deg, var(--primary-color) 0%, #330000 100%);
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
            color: var(--text-color);
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
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 1px var(--primary-color) !important;
        }
        
        /* Pill Button (Primary) */
        [data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"],
        [data-testid="stForm"] .stButton > button:not([data-testid="baseButton-secondaryFormSubmit"]):not([data-testid="baseButton-tertiaryFormSubmit"]) {
            background-color: var(--primary-color) !important;
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
            color: var(--text-color);
            text-decoration: underline;
        }

        @media (max-width: 768px) {
            .blob-1 { width: 200px !important; height: 200px !important; right: -50px !important; top: -50px !important; opacity: 0.4 !important; filter: blur(12px) !important; }
            .blob-2 { width: 150px !important; height: 150px !important; left: -20px !important; bottom: 0px !important; opacity: 0.3 !important; filter: blur(10px) !important; }
            .login-header-container h1 { font-size: 1.8rem !important; }
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

</style>

<div class="login-header-container">
<div class="dynamic-logo logo-center"></div>
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
        st.markdown(get_netflix_logo_svg("38px", "display:block;margin-bottom:16px;"), unsafe_allow_html=True)
        st.caption(f"{T['logged_in_as']} {st.session_state.get('user', 'unknown')}")

        selected_lang = st.selectbox(T["language_selector"], options=list(LANG.keys()), index=list(LANG.keys()).index(st.session_state.lang))
        if selected_lang != st.session_state.lang:
            st.session_state.lang = selected_lang
            st.rerun()



        selected_theme = st.selectbox(T["ui_theme"], options=list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme))
        if selected_theme != st.session_state.theme:
            st.session_state.theme = selected_theme
            update_theme_config(selected_theme)
            st.rerun()

        if st.button(T["log_out"], use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.divider()
        st.markdown(f"#### {T['filter_controls']}")

        valid_years = df["release_year"].dropna().astype(int)
        min_year, max_year = int(valid_years.min()), int(valid_years.max())

        year_range = st.slider(T["release_year"], min_value=min_year, max_value=max_year, value=(min_year, max_year), step=1)
        selected_types = st.multiselect(T["content_type"], options=sorted(df["type"].dropna().unique()), default=sorted(df["type"].dropna().unique()), format_func=lambda x: T["movie"] if x == "Movie" else (T["tv_show"] if x == "TV Show" else x), placeholder=T["choose_options"])
        selected_ratings = st.multiselect(T["maturity_rating"], options=sorted(df["rating"].dropna().unique()), default=[], placeholder=T["choose_options"])
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
    fig.update_layout(xaxis_title=T.get("titles", "Titles"), yaxis_title=T.get("genre", "Genre"), title=dict(text=T["chart_genres"], font=dict(size=14, color="gray")), xaxis=dict(gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(title=""), height=350)
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
    fig.update_layout(xaxis_title=T.get("titles", "Titles"), yaxis_title=T.get("director", "Director"), title=dict(text=T["chart_directors"], font=dict(size=14, color="gray")), xaxis=dict(gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(title=""), height=350)
    return fig

def chart_runtime_distribution(df: pd.DataFrame):
    movies = df[(df["type"] == "Movie") & (df["duration_minutes"].notna())]
    fig = px.histogram(movies, x="duration_minutes", nbins=40, color_discrete_sequence=["#404040"], labels={"duration_minutes": T.get("duration_minutes", "Duration (min)"), "count": T.get("count", "Count")})
    fig.update_traces(marker_line_color="rgba(0,0,0,0)", marker_line_width=0.5)
    fig.update_layout(title=dict(text="Movie Runtime Histogram", font=dict(size=14, color="gray")), xaxis=dict(title=T.get("duration_minutes", "Duration (min)"), gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(title="Frequency", gridcolor="rgba(128,128,128,0.2)"), bargap=0.06, height=350, clickmode="event+select")
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
    fig.update_layout(xaxis_title=T.get("titles", "Titles"), yaxis_title="", title=dict(text="Top 10 Most Featured Actors", font=dict(size=14, color="gray")), xaxis=dict(gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(title=""), height=400, clickmode="event+select")
    return fig

def chart_duration_scatter(df: pd.DataFrame):
    movies = df[(df["type"] == "Movie") & (df["duration_minutes"].notna()) & (df["release_year"] >= 1970)]
    avg_duration = movies.groupby("release_year")["duration_minutes"].mean().reset_index()
    
    fig = px.scatter(movies, x="release_year", y="duration_minutes", opacity=0.3, color_discrete_sequence=["#404040"], labels={"release_year": T.get("release_year", "Release Year"), "duration_minutes": T.get("duration_minutes", "Duration (min)")})
    fig.add_trace(go.Scatter(x=avg_duration["release_year"], y=avg_duration["duration_minutes"], mode="lines+markers", marker=dict(size=6, color=theme_primary), line=dict(color=theme_primary, width=3), name="Average Runtime"))
    fig.update_layout(title=dict(text="Movie Runtime Trends (Scatter + Average)", font=dict(size=14, color="gray")), xaxis=dict(title=T.get("release_year", "Release Year"), gridcolor="rgba(128,128,128,0.2)"), yaxis=dict(title="Duration (mins)", gridcolor="rgba(128,128,128,0.2)"), height=400, clickmode="event+select")
    return fig


# ══════════════════════════════════════════════════════════════════
#  MODULE 6: RECENT FEED & DATA EXPLORER
# ══════════════════════════════════════════════════════════════════

def render_recent_feed(df: pd.DataFrame):
    T = LANG[st.session_state.language]
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


def render_catalog_explorer(df: pd.DataFrame):
    T = LANG[st.session_state.language]
    search_query = st.text_input(T.get("cat_search_prompt", "Search Titles, Directors, or Genres"), placeholder=T.get("cat_search_placeholder", "e.g. Sci-Fi, Christopher Nolan"))
    if search_query:
        query_lower = search_query.lower()
        mask = (df["title"].str.lower().str.contains(query_lower, na=False) | df["director"].str.lower().str.contains(query_lower, na=False) | df["genres"].str.lower().str.contains(query_lower, na=False))
        search_results = df[mask]
    else:
        search_results = df

    display_cols = ["title", "type", "director", "country", "release_year", "rating", "duration", "genres"]
    display_df = search_results[[c for c in display_cols if c in search_results.columns]].reset_index(drop=True).copy()

    # Rename columns based on translation map
    col_map = {
        "title": T.get("col_title", "Title"),
        "type": T.get("col_type", "Type"),
        "director": T.get("col_director", "Director"),
        "country": T.get("col_country", "Country"),
        "release_year": T.get("col_year", "Release Year"),
        "rating": T.get("col_rating", "Rating"),
        "duration": T.get("col_duration", "Duration"),
        "genres": T.get("col_genres", "Genres")
    }
    display_df = display_df.rename(columns=col_map)
    
    # Translate types and genres inside the dataframe for non-English languages
    if st.session_state.language != "English":
        type_col = T.get("col_type", "Type")
        genres_col = T.get("col_genres", "Genres")
        if type_col in display_df.columns:
            display_df[type_col] = display_df[type_col].apply(lambda x: T["movie"] if x == "Movie" else T["tv_show"] if pd.notna(x) else x)
        if genres_col in display_df.columns:
            from app import GENRE_MAP
            display_df[genres_col] = display_df[genres_col].apply(lambda g: ", ".join([GENRE_MAP.get(st.session_state.language, {}).get(genre.strip(), genre.strip()) for genre in str(g).split(',')]) if pd.notna(g) else g)

    st.caption(T.get("cat_showing_results", "Showing {0:,} results").format(len(display_df)))
    st.dataframe(display_df, use_container_width=True, height=500)

    csv_payload = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(T["download_csv"], data=csv_payload, file_name="netflix_export.csv", mime="text/csv", use_container_width=True)


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
    
    st.markdown(get_netflix_logo_svg("24px", "margin: 12px 0;"), unsafe_allow_html=True)
    
    
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"]:first-of-type {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 4px !important;
            align-items: center !important;
        }
        [data-testid="stHorizontalBlock"]:first-of-type > div {
            flex: 1 1 30% !important;
            width: 30% !important;
            min-width: 100px !important;
        }
        [data-testid="stHorizontalBlock"]:first-of-type > div:last-child {
            flex: 1 1 100% !important;
            width: 100% !important;
            text-align: center !important;
            margin-top: 8px !important;
        }
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

</style>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2, 2, 2, 5])

    with c1:
        if st.button(f"**{localize_number(total, st.session_state.lang)}** {T['metric_total']}", type="tertiary", use_container_width=True):
            st.session_state.popup_request = {"col": "type", "val": "", "match": "all"}
            st.session_state.popup_page = 0
    with c2:
        if st.button(f"**{localize_number(movies, st.session_state.lang)}** {T['metric_movies']}", type="tertiary", use_container_width=True):
            st.session_state.popup_request = {"col": "type", "val": "Movie", "match": "exact"}
            st.session_state.popup_page = 0
    with c3:
        if st.button(f"**{localize_number(shows, st.session_state.lang)}** {T['metric_shows']}", type="tertiary", use_container_width=True):
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
            val = float(pt.get("x", 0))
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
    tab1, tab2, tab3, tab4 = st.tabs([T["tab_overview"], T["tab_deep_dive"], T["tab_data"], T.get("tab_ai", "🤖 AI Recommender")])

    with tab1:
        st.markdown(f'<div class="section-header" style="margin-top: 24px;">{T["header_trend"]}</div>', unsafe_allow_html=True)
        ev_hero = st.plotly_chart(chart_year_ingestion(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
        process_selection(ev_hero, "tab1_year", "year_added", extract_key="x")

        st.markdown(f'<div class="section-header">{T["header_dist"]}</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            ev_split = st.plotly_chart(chart_content_split(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev_split, "tab1_split", "type", extract_key="x")
        with col2:
            ev_genres = st.plotly_chart(chart_top_genres(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev_genres, "tab1_genres", "genres", extract_key="y", match_type="contains")

        st.markdown(f'<div class="section-header">{T["header_ratings"]}</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2, gap="large")
        with col3:
            ev_rating = st.plotly_chart(chart_rating_distribution(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev_rating, "tab1_ratings", "vote_average", is_range=True, bin_size=0.5)
        with col4:
            ev_directors = st.plotly_chart(chart_top_directors(filtered_df), use_container_width=True, on_select="rerun", selection_mode="points")
            process_selection(ev_directors, "tab1_directors", "director", extract_key="y", match_type="contains")

    with tab2:
        st.markdown(f'<div class="section-header">{T["header_granular"]}</div>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="section-header">{T.get("cat_header", "Catalog Search & Export")}</div>', unsafe_allow_html=True)
            render_catalog_explorer(filtered_df)
        with col_ex2:
            st.markdown(f'<div class="section-header">{T.get("feed_header", "Live Ingestion Feed")}</div>', unsafe_allow_html=True)
            render_recent_feed(filtered_df)

    with tab4:
        st.markdown(f'<div class="section-header">{T.get("tab_ai", "🤖 AI Recommender")}</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="opacity:0.8;">{T.get("ai_desc", "Describe what you want to watch in natural language, and our AI will find the best matches based on plot descriptions!")}</p>', unsafe_allow_html=True)
        
        search_query = st.text_input(T.get("ai_search_prompt", "🔍 Search query..."), placeholder=T.get("ai_search_placeholder", "e.g., A spooky detective movie with a twist ending"))
        
        if search_query:
            with st.spinner("Analyzing..."):
                vec, matrix = build_recommender_engine(df)
                results = get_recommendations(search_query, vec, matrix, df)
                
            if results:
                for r in results:
                    st.markdown(f'''
                    <div class="metric-card" style="margin-bottom: 16px;">
                        <h3 style="margin:0; color:var(--primary-color)">{r['title']} <span style="font-size:0.9rem; opacity:0.6; color:var(--text-color);">({r['score']:.1f}% Match)</span></h3>
                        <p style="font-size:0.85rem; font-weight:600; opacity:0.7; margin-top:4px;">{r['type']} • {r['genres']}</p>
                        <p style="margin-top:8px; font-size:1rem;">{r['description']}</p>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.info(T.get("ai_no_match", "No matches found. Try describing it differently!"))

    st.markdown(
        f"""
        <div style="text-align: center; padding: 24px 0 12px; margin-top: 40px; border-top: 1px solid gray;">
            <span style="color: var(--text-color); opacity: 0.7; font-size: 0.8rem;">
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
