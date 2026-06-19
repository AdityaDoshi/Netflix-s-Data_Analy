import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Inject THEMES and get_custom_css
theme_code = """
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
    css = \"\"\"
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: VAR_TEXT; }
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

    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 48px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: transparent !important; border-bottom: 2px solid VAR_ACCENT !important; color: VAR_ACCENT !important; }

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
</style>
\"\"\"
    for k, v in t.items():
        css = css.replace(f"VAR_{k.upper()}", v)
    return css

st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)
"""

css_regex = re.compile(r'CUSTOM_CSS = """(.*?)st\.markdown\(CUSTOM_CSS, unsafe_allow_html=True\)', re.DOTALL)
content = css_regex.sub(theme_code.replace('\\', '\\\\'), content)

# 2. Refactor PLOTLY_LAYOUT_DEFAULTS
plotly_layout_regex = re.compile(r'PLOTLY_LAYOUT_DEFAULTS = dict\(.*?hoverlabel=dict\(bgcolor="#141414", font_size=12, font_family="Inter, sans-serif", bordercolor="#333333"\),\n\)', re.DOTALL)

plotly_layout_code = """
def get_plotly_layout(theme):
    t = THEMES[theme]
    return dict(
        paper_bgcolor=t["plotly_bg"],
        plot_bgcolor=t["plotly_bg"],
        font=dict(family="Inter, sans-serif", color=t["text_muted"], size=12),
        margin=dict(l=20, r=20, t=50, b=20),
        hoverlabel=dict(bgcolor=t["card"], font_size=12, font_family="Inter, sans-serif", bordercolor=t["border"]),
    )
"""
content = plotly_layout_regex.sub(plotly_layout_code, content)

# Replace **PLOTLY_LAYOUT_DEFAULTS with **get_plotly_layout(st.session_state.theme)
content = content.replace('**PLOTLY_LAYOUT_DEFAULTS', '**get_plotly_layout(st.session_state.theme)')

# Update specific hardcoded colors in charts
content = content.replace('color="#FFFFFF"', 'color=THEMES[st.session_state.theme]["text"]')
content = content.replace('gridcolor="#333333"', 'gridcolor=THEMES[st.session_state.theme]["grid"]')
content = content.replace('color="#344054"', 'color=THEMES[st.session_state.theme]["bar_default"]')
content = content.replace('color="#404040"', 'color=THEMES[st.session_state.theme]["bar_default"]')
content = content.replace('color="#808080"', 'color=THEMES[st.session_state.theme]["bar_default"]')
content = content.replace('marker_line_color="#141414"', 'marker_line_color=THEMES[st.session_state.theme]["bg"]')
content = content.replace('coastlinecolor="#333333"', 'coastlinecolor=THEMES[st.session_state.theme]["border"]')

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Refactored app.py for themes.")
