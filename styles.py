# styles.py
"""
Shared styling for all pages of the Penang Ferry Museum dashboard.
Import apply_global_styles() and render_sidebar() in every page.
"""
import streamlit as st
import base64
from pathlib import Path


# ============================================================
# DESIGN TOKENS
# ============================================================

YELLOW        = "#F2B705"   # primary accent
YELLOW_DARK   = "#D99400"   # hover / darker accent
INK           = "#292929"   # primary text
INK_MUTED     = "#666666"   # secondary text
INK_SOFT      = "#777777"   # captions
BG            = "#FFFDF7"   # page background
CARD          = "#FFFFFF"   # card / sidebar background
BORDER        = "#E7DFC9"   # borders
POSITIVE      = "#4C8C5A"
NEUTRAL       = "#D99A00"
NEGATIVE      = "#C75B39"

LOGO_FILE     = "images (1).jpg"

DEFAULT_MIN_WORDS = 4


# ============================================================
# GLOBAL CSS
# ============================================================

def apply_global_styles():
    """Inject the shared CSS into a Streamlit page."""

    st.markdown(f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');

    /* =========================================================
       GLOBAL
    ========================================================= */

    html, body, [class*="css"] {{
        font-family: "Lato", Arial, sans-serif !important;
    }}

    .stApp, .main {{
        background: {BG} !important;
        color: {INK} !important;
    }}

    .block-container {{
        max-width: 1400px !important;
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
    }}

    h1, h2, h3, h4 {{
        font-family: "Poppins", Arial, sans-serif !important;
        color: {INK} !important;
        font-weight: 700 !important;
    }}

    h1 {{ font-weight: 800 !important; letter-spacing: -0.5px; }}
    h2 {{
        margin-top: 25px !important;
        padding-bottom: 8px !important;
        border-bottom: 3px solid {YELLOW} !important;
    }}
    h3 {{ margin-top: 20px !important; }}


    /* =========================================================
       SIDEBAR
    ========================================================= */

    [data-testid="stSidebar"] {{
        background: {CARD} !important;
        border-right: 3px solid {YELLOW} !important;
        box-shadow: 4px 0 18px rgba(0,0,0,0.05);
    }}

    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
        padding-top: 0.3rem !important;
        padding-bottom: 0.3rem !important;
    }}

    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
        padding-top: 0.4rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }}

    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
        padding-top: 0.2rem !important;
    }}

    /* Kill default padding around st.image in sidebar */
    [data-testid="stSidebar"] [data-testid="stImage"] {{
        margin: 0 !important;
        padding: 0 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stImage"] img {{
        display: block !important;
        margin: 0 auto !important;
        padding: 0 !important;
    }}

    [data-testid="stSidebar"] * {{
        color: {INK} !important;
        font-family: "Lato", Arial, sans-serif !important;
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        font-family: "Poppins", Arial, sans-serif !important;
    }}

    /* Sidebar navigation radio */
    .stRadio > div {{ gap: 8px !important; }}

    .stRadio div[role="radiogroup"] label {{
        background: {BG} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        margin-bottom: 7px !important;
        transition: all 0.2s ease !important;
    }}

    .stRadio div[role="radiogroup"] label:hover {{
        background: #FFF4CC !important;
        border-color: {YELLOW} !important;
    }}

    .stRadio div[role="radiogroup"] label p {{
        color: {INK} !important;
        font-weight: 600 !important;
    }}

    /* Sidebar selectbox */
    [data-testid="stSidebar"] div[data-baseweb="select"] {{
        background-color: {BG} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
    }}


    /* =========================================================
       HIDE STREAMLIT'S AUTO-GENERATED NAV
    ========================================================= */

    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}


    /* =========================================================
       CUSTOM PAGE LINKS (st.page_link) — button style
    ========================================================= */

    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        padding: 10px 14px !important;
        margin-bottom: 6px !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
        background: {BG} !important;
        text-decoration: none !important;
        transition: all 0.2s ease !important;
    }}

    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {{
        background: #FFF4CC !important;
        border-color: {YELLOW} !important;
    }}

    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {{
        color: {INK} !important;
        font-family: "Poppins", Arial, sans-serif !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 0.6px !important;
        text-transform: uppercase !important;
        text-align: center !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }}

    /* Highlight active page_link */
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {{
        background: {YELLOW} !important;
        border-color: {YELLOW} !important;
        box-shadow: 0 3px 10px rgba(242, 183, 5, 0.3) !important;
    }}

    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] p {{
        color: {INK} !important;
        font-weight: 800 !important;
    }}

    /* Hide any icon next to the page_link label */
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] svg,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] img,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] > span:first-child:not(:last-child) {{
        display: none !important;
    }}


    /* =========================================================
       ACTIVE NAV BUTTON (rendered as HTML div)
    ========================================================= */

    .pfm-nav-active {{
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 10px 14px;
        margin-bottom: 6px;
        border: 1px solid {YELLOW};
        border-radius: 8px;
        background: {YELLOW};
        box-shadow: 0 3px 10px rgba(242, 183, 5, 0.3);
    }}

    .pfm-nav-active span {{
        color: {INK};
        font-family: "Poppins", Arial, sans-serif;
        font-weight: 800;
        font-size: 13px;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }}


    /* =========================================================
       PAGE HEADERS
    ========================================================= */

    .pfm-page-title {{
        text-align: center;
        font-family: "Poppins", Arial, sans-serif;
        font-size: 34px;
        font-weight: 800;
        color: {INK};
        margin: 0;
    }}

    .pfm-page-subtitle {{
        text-align: center;
        font-family: "Lato", Arial, sans-serif;
        font-size: 14px;
        color: {INK_MUTED};
        margin: 5px 0;
    }}

    .pfm-yellow-line {{
        text-align: center;
        color: {YELLOW};
        font-size: 18px;
        margin: 0 0 22px 0;
    }}


    /* =========================================================
       SECTION TITLES
    ========================================================= */

    .pfm-section-title {{
        font-family: "Poppins", Arial, sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: {INK};
        border-left: 5px solid {YELLOW};
        padding-left: 12px;
        margin: 20px 0 15px 0;
    }}

    .pfm-card-title {{
        font-family: "Poppins", Arial, sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: {INK};
        margin-bottom: 5px;
    }}

    .pfm-description {{
        font-family: "Lato", Arial, sans-serif;
        font-size: 14px;
        color: {INK_MUTED};
        line-height: 1.6;
        margin-bottom: 12px;
    }}

    .pfm-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        margin-bottom: 10px;
    }}


    /* =========================================================
       METRIC CARDS
    ========================================================= */

    div[data-testid="stMetric"] {{
        background: {CARD} !important;
        border: 1px solid {BORDER} !important;
        border-top: 4px solid {YELLOW} !important;
        border-radius: 12px !important;
        padding: 18px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }}

    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 22px rgba(0,0,0,0.08) !important;
    }}

    div[data-testid="stMetric"] label {{
        color: {INK_MUTED} !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
    }}

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {INK} !important;
        font-family: "Poppins", Arial, sans-serif !important;
        font-weight: 800 !important;
    }}


    /* =========================================================
       DATAFRAME
    ========================================================= */

    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04) !important;
    }}

    thead tr th {{
        background: {YELLOW} !important;
        color: {INK} !important;
        font-weight: 800 !important;
    }}


    /* =========================================================
       BUTTONS
    ========================================================= */

    .stButton > button {{
        background: {YELLOW} !important;
        color: {INK} !important;
        border: 2px solid {YELLOW} !important;
        border-radius: 8px !important;
        font-family: "Poppins", Arial, sans-serif !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }}

    .stButton > button:hover {{
        background: {YELLOW_DARK} !important;
        border-color: {YELLOW_DARK} !important;
        color: #FFFFFF !important;
        transform: translateY(-2px);
    }}


    /* =========================================================
       SELECTBOX
    ========================================================= */

    div[data-baseweb="select"] > div {{
        background-color: {CARD} !important;
        border-color: {BORDER} !important;
        border-radius: 8px !important;
    }}


    /* =========================================================
       ALERTS / DIVIDERS
    ========================================================= */

    [data-testid="stAlert"] {{ border-radius: 10px !important; }}

    hr {{
        border: none !important;
        height: 1px !important;
        background: {BORDER} !important;
        margin: 25px 0 !important;
    }}


    /* =========================================================
       MOBILE
    ========================================================= */

    @media (max-width: 768px) {{
        .pfm-page-title {{ font-size: 27px; }}
        .pfm-section-title {{ font-size: 19px; }}
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        div[data-testid="stMetric"] {{ padding: 15px !important; }}
    }}

    </style>
    """, unsafe_allow_html=True)


# ============================================================
# STANDARDISED SIDEBAR
# ============================================================

def render_sidebar(
    current_page="pfm_analysis",
    show_attraction_selector=False,
    attraction_options=None,
    show_extra_filters=False,
    show_sentiment_filter=False,
):
    """
    Render the standard sidebar used across all pages.

    Parameters
    ----------
    current_page : str
        One of: "pfm_analysis", "comparison", "detail_review",
        "overview_places".

    Returns
    -------
    dict with keys:
        attraction, rating_filter, sentiment_filter, min_words, max_words
    """

    result = {
        "attraction": None,
        "rating_filter": None,
        "sentiment_filter": None,
        "min_words": DEFAULT_MIN_WORDS,
        "max_words": None,
    }

    base_dir = Path(__file__).resolve().parent
    logo_path = base_dir / LOGO_FILE

    # ---------- NAV ITEMS ----------
    nav_items = [
        ("pfm_analysis",    "home.py",           "PFM ANALYSIS"),
        ("comparison",      "pages/comparison.py",         "COMPARISON"),
        ("detail_review",   "pages/detail_review.py",      "DETAIL REVIEW"),
        ("overview_places", "pages/overview_places.py",    "OVERVIEW PLACES"),
    ]

    with st.sidebar:

        # ====================================================
        # BRAND — LOGO + TITLE (tight, no gap)
        # ====================================================

        if logo_path.exists():
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()

            st.markdown(
                f"""
                <div style="text-align:center; margin:0; padding:0; line-height:0;">
                    <img src="data:image/jpeg;base64,{logo_b64}"
                         width="110"
                         style="display:inline-block; margin:0; padding:0;"/>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='text-align:center;font-size:52px;margin:0;'>🚢</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <h2 style="
                text-align:center;
                font-family:Poppins,Arial,sans-serif;
                font-size:18px;
                font-weight:800;
                color:{INK};
                margin:4px 0 0 0;
                padding:0;
                line-height:1.1;
                letter-spacing:0.5px;
            ">
                PENANG FERRY MUSEUM
            </h2>

            <p style="
                text-align:center;
                font-family:Lato,Arial,sans-serif;
                font-size:12px;
                font-weight:500;
                color:{INK_SOFT};
                margin:2px 0 8px 0;
                padding:0;
            ">
                Attractions Analytics
            </p>

            <p style="
                text-align:center;
                color:{YELLOW};
                font-size:16px;
                margin:0 0 14px 0;
                padding:0;
            ">
                ━━━━━━━━━
            </p>
            """,
            unsafe_allow_html=True,
        )

        # ====================================================
        # CUSTOM NAVIGATION
        # ====================================================

        for key, path, label in nav_items:

            if key == current_page:

                st.markdown(
                    f"""
                    <div class="pfm-nav-active">
                        <span>{label}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                st.page_link(path, label=label)

        # ====================================================
        # ATTRACTION SELECTOR
        # ====================================================

        if show_attraction_selector and attraction_options:
            st.markdown("---")
            st.markdown(
                f"""
                <p style="
                    font-family:Poppins,Arial,sans-serif;
                    font-size:14px;
                    font-weight:700;
                    color:{INK};
                    margin-bottom:5px;
                ">
                    Attraction Selection
                </p>
                """,
                unsafe_allow_html=True,
            )
            result["attraction"] = st.selectbox(
                "Select Attraction:",
                options=attraction_options,
                label_visibility="collapsed",
                key="sidebar_attraction",
            )

        # ====================================================
        # EXTRA FILTERS
        # ====================================================

        if show_extra_filters:
            st.markdown("---")
            st.markdown(
                f"""
                <p style="
                    font-family:Poppins,Arial,sans-serif;
                    font-size:14px;
                    font-weight:700;
                    color:{INK};
                    margin-bottom:5px;
                ">
                    Review &amp; Text Filters
                </p>
                """,
                unsafe_allow_html=True,
            )
            result["rating_filter"] = st.selectbox(
                "Filter by Star Rating:",
                options=["All Ratings", "5 ⭐", "4 ⭐", "3 ⭐", "2 ⭐", "1 ⭐"],
                key="sidebar_rating_filter",
            )

            if show_sentiment_filter:
                result["sentiment_filter"] = st.selectbox(
                    "Filter by Sentiment:",
                    options=[
                        "All Sentiments",
                        "Positive",
                        "Neutral",
                        "Negative",
                    ],
                    key="sidebar_sentiment_filter",
                )

            result["max_words"] = st.slider(
                "Max Words Shown:", 20, 200, 100, 10, key="sidebar_max"
            )

            st.markdown("---")
            st.caption(
                "Use the filters above to explore attraction reviews "
                "and visitor feedback."
            )

    return result