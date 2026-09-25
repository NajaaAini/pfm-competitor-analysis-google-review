# pages/4_Overview_Places.py
import streamlit as st
import pandas as pd
import altair as alt
import base64
from pathlib import Path

from data_loader import load_data
from styles import apply_global_styles, render_sidebar, YELLOW, POSITIVE, NEGATIVE


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Overview | Penang Ferry Museum",
    page_icon="🚢",
    layout="wide",
)

apply_global_styles()
render_sidebar(current_page="overview_places")


# ============================================================
# LOAD DATA
# ============================================================

df = load_data().copy()
df["date"] = pd.to_datetime(df["date"], errors="coerce")

df = df.rename(columns={
    "reviewer": "name",
    "author": "name",
    "user": "name",
    "user_name": "name",
    "reviewer_name": "name",
    "review_url": "reviewUrl",
    "url": "reviewUrl",
    "link": "reviewUrl",
    "review_link": "reviewUrl",
    "google_url": "reviewUrl",
    "owner_response": "responseFromOwnerText",
    "response": "responseFromOwnerText",
    "owner_response_text": "responseFromOwnerText",
    "response_from_owner_text": "responseFromOwnerText",
})


# ============================================================
# HEADER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_PATH = BASE_DIR / "images (1).jpg"

if IMAGE_PATH.exists():
    with open(IMAGE_PATH, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 0; margin-bottom: -10px;">
            <img src="data:image/jpeg;base64,{img_b64}"
                width="180"
                style="display: inline-block; vertical-align: middle;"/>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("""
<h1 style="
    text-align: center;
    color: #292929;
    font-family: 'Poppins', Arial, sans-serif;
    font-size: 36px;
    font-weight: 800;
    margin: 0;
    padding: 0;
    line-height: 1.2;
">
    Executive Overview
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<h3 style="
    text-align: center;
    color: #666666;
    font-family: 'Lato', Arial, sans-serif;
    font-size: 18px;
    font-weight: 500;
    margin: 2px 0 0 0;
    padding: 0;
">
    Penang Ferry Museum &amp; Attractions Analytics
</h3>
""", unsafe_allow_html=True)

st.markdown("""
<p style="
    text-align: center;
    color: #F2B705;
    font-size: 16px;
    margin: 4px 0 12px 0;
    padding: 0;
">
    ━━━━━
</p>
""", unsafe_allow_html=True)


# ============================================================
# SUB-HEADING HELPER
# ============================================================

def sub_heading(text):
    st.markdown(
        f'<p style="font-size:15px;font-weight:700;color:#292929;'
        f'margin:14px 0 6px 0;text-transform:uppercase;letter-spacing:0.5px;">'
        f'{text}</p>',
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR — TIMELINE FILTER
# ============================================================

valid_dates = df["date"].dropna()

if not valid_dates.empty:
    global_min = valid_dates.min().date()
    global_max = valid_dates.max().date()

    with st.sidebar:
        st.markdown("### Timeline Filter")

        preset = st.selectbox(
            "Quick range:",
            ["All time", "Past Week", "Past Month", "Past 3 Months",
             "Past 6 Months", "Past Year", "Past 2 Years", "Custom"],
            index=0,
            key="overview_date_preset",
        )

        today = pd.Timestamp.today().normalize()

        if preset == "All time":
            start_date, end_date = global_min, global_max
        elif preset == "Past Week":
            start_date = (today - pd.Timedelta(days=7)).date()
            end_date = today.date()
        elif preset == "Past Month":
            start_date = (today - pd.Timedelta(days=30)).date()
            end_date = today.date()
        elif preset == "Past 3 Months":
            start_date = (today - pd.Timedelta(days=90)).date()
            end_date = today.date()
        elif preset == "Past 6 Months":
            start_date = (today - pd.Timedelta(days=180)).date()
            end_date = today.date()
        elif preset == "Past Year":
            start_date = (today - pd.Timedelta(days=365)).date()
            end_date = today.date()
        elif preset == "Past 2 Years":
            start_date = (today - pd.Timedelta(days=730)).date()
            end_date = today.date()
        else:  # Custom
            picked = st.date_input(
                "Custom range:",
                value=(global_min, global_max),
                min_value=global_min,
                max_value=global_max,
                key="overview_custom_date_range",
            )
            if isinstance(picked, tuple) and len(picked) == 2:
                start_date, end_date = picked
            else:
                start_date, end_date = global_min, global_max

        if start_date < global_min:
            start_date = global_min
        if end_date > global_max:
            end_date = global_max

        st.session_state["overview_filter_start"] = start_date
        st.session_state["overview_filter_end"] = end_date

        st.caption(f"Range: **{start_date}** → **{end_date}**")
else:
    st.session_state["overview_filter_start"] = None
    st.session_state["overview_filter_end"] = None


# ============================================================
# APPLY FILTER
# ============================================================

if (st.session_state.get("overview_filter_start") is not None
        and st.session_state.get("overview_filter_end") is not None):

    start_date = st.session_state["overview_filter_start"]
    end_date = st.session_state["overview_filter_end"]

    mask = ((df["date"].dt.date >= start_date)
            & (df["date"].dt.date <= end_date))
    df = df[mask].copy()

df["month"] = df["date"].dt.to_period("M").astype(str)


if df.empty:
    st.info("No reviews match the selected date range.")
    st.stop()


# ============================================================
# 1) KEY METRICS
# ============================================================

st.markdown('<p class="pfm-section-title">1) Key Metrics</p>',
            unsafe_allow_html=True)

total_reviews = len(df)
total_attractions = df["attraction_name"].nunique()
overall_avg = round(df["rating"].mean(), 2) if pd.notna(df["rating"].mean()) else 0
pos_pct = df["sentiment"].eq("Positive").mean() * 100

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Total Reviews",
        f"{total_reviews:,}",
        help=f"Total number of reviews in selected range: {total_reviews:,}",
    )
with c2:
    st.metric(
        "Average Rating",
        f"{overall_avg} / 5",
        help=f"Average rating across {total_reviews:,} reviews",
    )
with c3:
    st.metric(
        "Positive Reviews",
        f"{pos_pct:.1f}%",
        help=f"{int(df['sentiment'].eq('Positive').sum()):,} positive reviews (4–5★)",
    )
with c4:
    st.metric(
        "Attractions",
        f"{total_attractions}",
        help=f"{total_attractions} attractions with reviews",
    )


# ============================================================
# 2) TOP 3 ATTRACTIONS — chart only
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">2) Top 3 Attractions</p>',
            unsafe_allow_html=True)

rank_df = (
    df.groupby("attraction_name")
    .agg(
        Reviews=("rating", "count"),
        Avg_Rating=("rating", "mean"),
        Positive=("sentiment", lambda x: (x == "Positive").mean() * 100),
    )
    .reset_index()
)
rank_df = rank_df[rank_df["Reviews"] >= 5]
rank_df = rank_df.sort_values(
    ["Avg_Rating", "Positive", "Reviews"], ascending=False
)

top3 = rank_df.head(3).copy()

if not top3.empty:
    top3["Label"] = top3["Avg_Rating"].apply(lambda x: f"{x:.2f}")

    base = alt.Chart(top3).encode(
        x=alt.X("Avg_Rating:Q", title="Average Rating",
                scale=alt.Scale(domain=[0, 5])),
        y=alt.Y("attraction_name:N", sort="-x", title=""),
    )
    bars = base.mark_bar(color=YELLOW, cornerRadiusEnd=4,
                         cursor="pointer").encode(
        tooltip=[
            alt.Tooltip("attraction_name:N", title="Attraction"),
            alt.Tooltip("Avg_Rating:Q", title="Avg Rating", format=".2f"),
            alt.Tooltip("Reviews:Q", title="Reviews"),
            alt.Tooltip("Positive:Q", title="Positive %", format=".1f"),
        ],
    )
    labels = base.mark_text(dx=8, fontSize=12, fontWeight="bold",
                            color="#555").encode(text="Label:N")

    st.altair_chart((bars + labels).properties(height=220),
                    use_container_width=True)
else:
    st.info("Not enough reviews to compute top 3.")


# ============================================================
# 3) ATTRACTION PERFORMANCE
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">3) Attraction Performance</p>',
            unsafe_allow_html=True)

table = (
    df.groupby("attraction_name")
    .agg(
        Reviews=("rating", "count"),
        Rating=("rating", "mean"),
        Positive=("sentiment", lambda x: (x == "Positive").mean() * 100),
        Negative=("sentiment", lambda x: (x == "Negative").mean() * 100),
        ResponseRate=("owner_responded", lambda x: x.mean() * 100),
    )
    .round(2)
    .reset_index()
    .rename(columns={"attraction_name": "Attraction"})
    .sort_values("Reviews", ascending=False)
)

st.dataframe(table, use_container_width=True, hide_index=True)


# ============================================================
# 4) REVIEW VOLUME BY ATTRACTION
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">4) Review Volume by Attraction</p>',
            unsafe_allow_html=True)

vol = df["attraction_name"].value_counts().head(15).reset_index()
vol.columns = ["Attraction", "Reviews"]
vol["Label"] = vol["Reviews"].astype(str)

base = alt.Chart(vol).encode(
    x=alt.X("Reviews:Q", title="Reviews"),
    y=alt.Y("Attraction:N", sort="-x", title=""),
)
bars = base.mark_bar(color=YELLOW, cornerRadiusEnd=4,
                     cursor="pointer").encode(
    tooltip=["Attraction", "Reviews"],
)
labels = base.mark_text(dx=8, fontSize=12, fontWeight="bold",
                        color="#555").encode(text="Label:N")

st.altair_chart((bars + labels).properties(height=420),
                use_container_width=True)


# ============================================================
# 5) REVIEW TRENDS
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">5) Review Trends</p>',
            unsafe_allow_html=True)

monthly = (
    df.dropna(subset=["date"])
    .groupby("month")
    .agg(Reviews=("rating", "count"),
         Avg_Rating=("rating", "mean"))
    .reset_index()
)

t1, t2 = st.columns(2)

with t1:
    with st.container(border=True):
        sub_heading("Monthly Review Volume")

        month_vol = monthly.copy()
        month_vol["Label"] = month_vol["Reviews"].astype(str)

        base = alt.Chart(month_vol).encode(
            x=alt.X("month:N", sort=None, title=""),
            y=alt.Y("Reviews:Q", title="Reviews"),
        )
        line = base.mark_line(color=YELLOW, strokeWidth=3, point=True).encode(
            tooltip=["month", "Reviews"],
        )
        labels = base.mark_text(dy=-10, fontSize=11, fontWeight="bold",
                                color="#7A5B00").encode(text="Label:N")

        st.altair_chart((line + labels).properties(height=300),
                        use_container_width=True)

with t2:
    with st.container(border=True):
        sub_heading("Monthly Average Rating")

        month_rate = monthly.copy()
        month_rate["Label"] = month_rate["Avg_Rating"].apply(lambda x: f"{x:.2f}")

        base = alt.Chart(month_rate).encode(
            x=alt.X("month:N", sort=None, title=""),
            y=alt.Y("Avg_Rating:Q", title="Average Rating",
                    scale=alt.Scale(domain=[1, 5])),
        )
        line = base.mark_line(color=YELLOW, strokeWidth=3, point=True).encode(
            tooltip=["month", alt.Tooltip("Avg_Rating:Q", format=".2f")],
        )
        labels = base.mark_text(dy=-10, fontSize=11, fontWeight="bold",
                                color="#7A5B00").encode(text="Label:N")

        st.altair_chart((line + labels).properties(height=300),
                        use_container_width=True)


# ============================================================
# 6) VISIT CONTEXT DISTRIBUTION
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">6) Visit Context Distribution</p>',
            unsafe_allow_html=True)

ctx = (
    df.groupby("visit_context")
    .agg(Reviews=("rating", "count"),
         Avg_Rating=("rating", "mean"))
    .round(2)
    .reset_index()
    .sort_values("Reviews", ascending=False)
)
ctx["Label"] = ctx["Reviews"].astype(str)

base = alt.Chart(ctx).encode(
    x=alt.X("visit_context:N", title="", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("Reviews:Q", title="Reviews"),
)
bars = base.mark_bar(color=YELLOW, cornerRadiusTopLeft=4,
                     cornerRadiusTopRight=4, cursor="pointer").encode(
    tooltip=["visit_context", "Reviews",
             alt.Tooltip("Avg_Rating:Q", format=".2f")],
)
labels = base.mark_text(dy=-8, fontSize=12, fontWeight="bold",
                        color="#555").encode(text="Label:N")

st.altair_chart((bars + labels).properties(height=320),
                use_container_width=True)

with st.container(border=True):
    st.dataframe(ctx, use_container_width=True, hide_index=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption(
    "Data source: Google Maps Reviews. "
    "Sentiment is derived from star ratings "
    "(4–5 = Positive, 3 = Neutral, 1–2 = Negative)."
)