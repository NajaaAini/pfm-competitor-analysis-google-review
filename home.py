# Home.py
import streamlit as st
import pandas as pd
import altair as alt
import re
import base64
from collections import Counter
from pathlib import Path

from data_loader import load_data, map_sentiment
from styles import apply_global_styles, render_sidebar, YELLOW, POSITIVE, NEGATIVE


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Penang Ferry Museum | PFM Analytics",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()
render_sidebar(current_page="pfm_analysis")


# =========================================================
# EXTRA CSS
# =========================================================

st.markdown("""
<style>
div[data-testid="stExpander"] details summary p {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #292929 !important;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA
# =========================================================

df = load_data().copy()

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

pfm = df[
    df["attraction_name"].astype(str).str.strip().str.lower()
    == "penang ferry museum"
].copy()

if pfm.empty:
    st.error(
        "No Penang Ferry Museum data found. "
        "Please check the attraction name mapping in data_loader.py."
    )
    st.stop()


# ============================================================
# DASHBOARD HEADER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
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
else:
    st.markdown(
        "<div style='text-align:center;font-size:70px;margin-bottom:-20px;'>🚢</div>",
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
    Penang Ferry Museum
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
    Competitor Analysis
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


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_reviews = len(pfm)
avg_rating = pfm["rating"].mean()
positive_pct = pfm["sentiment"].eq("Positive").mean() * 100
negative_pct = pfm["sentiment"].eq("Negative").mean() * 100
neutral_pct = pfm["sentiment"].eq("Neutral").mean() * 100
responded = int(pfm["owner_responded"].sum())
response_rate = responded / total_reviews * 100 if total_reviews else 0

date_min = pfm["date"].min()
date_max = pfm["date"].max()
if pd.notna(date_min) and pd.notna(date_max):
    review_period = f"{date_min.strftime('%b %y')} – {date_max.strftime('%b %y')}"
else:
    review_period = "N/A"


# =========================================================
# 1) PERFORMANCE OVERVIEW
# =========================================================

st.markdown('<p class="pfm-section-title">1) Performance Overview</p>',
            unsafe_allow_html=True)
st.caption("Key indicators based on available Google Maps reviews.")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric(
        "Total Reviews",
        f"{total_reviews:,}",
        help=f"Total number of reviews: {total_reviews:,}",
    )
with k2:
    st.metric(
        "Average Rating",
        f"{avg_rating:.2f} / 5",
        help=f"Average rating across {total_reviews:,} reviews",
    )
with k3:
    st.metric(
        "Positive Reviews",
        f"{positive_pct:.1f}%",
        help=f"{int(pfm['sentiment'].eq('Positive').sum()):,} positive reviews (4–5★)",
    )
with k4:
    st.metric(
        "Negative Reviews",
        f"{negative_pct:.1f}%",
        help=f"{int(pfm['sentiment'].eq('Negative').sum()):,} negative reviews (1–2★)",
    )
with k5:
    st.metric(
        "Review Period",
        review_period,
        help=f"First review: {date_min.strftime('%b %Y') if pd.notna(date_min) else 'N/A'}\n"
             f"Latest review: {date_max.strftime('%b %Y') if pd.notna(date_max) else 'N/A'}",
    )


# =========================================================
# 2) VISITOR SATISFACTION
# =========================================================

st.markdown('<p class="pfm-section-title">2) Visitor Satisfaction</p>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### Rating Distribution")

        rating_counts = (
            pfm["rating"].round().value_counts()
            .reindex([1, 2, 3, 4, 5], fill_value=0)
        )

        rating_df = pd.DataFrame({
            "Rating": ["1★", "2★", "3★", "4★", "5★"],
            "Reviews": rating_counts.values,
        })
        rating_df["Label"] = rating_df["Reviews"].astype(str)
        rating_df["Percent"] = (rating_df["Reviews"] / total_reviews * 100).round(1)

        base = alt.Chart(rating_df).encode(
            x=alt.X("Rating:N", title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Reviews:Q", title="Reviews"),
        )

        bars = base.mark_bar(
            color=YELLOW,
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
            cursor="pointer",
        ).encode(
            tooltip=[
                alt.Tooltip("Rating:N", title="Rating"),
                alt.Tooltip("Reviews:Q", title="Reviews"),
                alt.Tooltip("Percent:Q", title="% of total", format=".1f"),
            ]
        )

        labels = base.mark_text(
            dy=-8, fontSize=13, fontWeight="bold", color="#555"
        ).encode(text="Label:N")

        st.altair_chart((bars + labels).properties(height=300),
                        use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown("### Visitor Sentiment")

        sentiment_counts = (
            pfm["sentiment"].value_counts()
            .reindex(["Positive", "Neutral", "Negative"], fill_value=0)
        )

        sentiment_df = pd.DataFrame({
            "Sentiment": sentiment_counts.index,
            "Reviews": sentiment_counts.values,
        })
        sentiment_df["Label"] = sentiment_df["Reviews"].astype(str)
        sentiment_df["Percent"] = (sentiment_df["Reviews"] / total_reviews * 100).round(1)

        sentiment_colors = {
            "Positive": POSITIVE,
            "Neutral": YELLOW,
            "Negative": NEGATIVE,
        }

        base = alt.Chart(sentiment_df).encode(
            x=alt.X("Sentiment:N", title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Reviews:Q", title="Reviews"),
        )

        bars = base.mark_bar(
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
            cursor="pointer",
        ).encode(
            color=alt.Color(
                "Sentiment:N",
                scale=alt.Scale(
                    domain=list(sentiment_colors.keys()),
                    range=list(sentiment_colors.values()),
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Sentiment:N", title="Sentiment"),
                alt.Tooltip("Reviews:Q", title="Reviews"),
                alt.Tooltip("Percent:Q", title="% of total", format=".1f"),
            ],
        )

        labels = base.mark_text(
            dy=-8, fontSize=13, fontWeight="bold", color="#555"
        ).encode(text="Label:N")

        st.altair_chart((bars + labels).properties(height=300),
                        use_container_width=True)


# =========================================================
# 3) OWNER RESPONSE PERFORMANCE
# =========================================================

st.markdown('<p class="pfm-section-title">3) Owner Response Performance</p>',
            unsafe_allow_html=True)
st.caption(
    "How actively Penang Ferry Museum responds to visitor reviews. "
    "Responding — especially to negative reviews — improves future ratings."
)

o1, o2, o3 = st.columns(3)
with o1:
    st.metric(
        "Reviews Responded",
        f"{responded:,} / {total_reviews:,}",
        help=f"{responded:,} reviews have been responded to by the owner",
    )
with o2:
    st.metric(
        "Response Rate",
        f"{response_rate:.1f}%",
        help="Percentage of reviews that received an owner response",
    )
with o3:
    st.metric(
        "Unanswered",
        f"{total_reviews - responded:,}",
        help=f"{total_reviews - responded:,} reviews have not been responded to",
    )

resp_pfm = pfm.dropna(subset=["date"]).copy()

if not resp_pfm.empty:
    resp_min = resp_pfm["date"].min().date()
    resp_max = resp_pfm["date"].max().date()

    resp_picked = st.date_input(
        "Filter owner responses by date range:",
        value=(resp_min, resp_max),
        min_value=resp_min,
        max_value=resp_max,
        key="owner_response_date_range",
    )

    if isinstance(resp_picked, tuple) and len(resp_picked) == 2:
        r_start, r_end = resp_picked
        resp_pfm = resp_pfm[
            (resp_pfm["date"].dt.date >= r_start)
            & (resp_pfm["date"].dt.date <= r_end)
        ]

with st.expander("Owner responses"):
    samples = resp_pfm[resp_pfm["owner_responded"]].head(10)

    if samples.empty:
        st.info("No owner responses recorded in the selected date range.")
    else:
        for _, row in samples.iterrows():
            guest_text = str(row["text"]).strip()
            if len(guest_text) > 250:
                guest_text = guest_text[:250] + "..."

            st.markdown(f"**{row['rating']:.0f}★ review**")
            st.write(guest_text)
            st.success(f"**Owner:** {row['responseFromOwnerText']}")
            st.markdown("---")


# =========================================================
# 4) VISIT CONTEXT
# =========================================================

st.markdown('<p class="pfm-section-title">4) When Do Visitors Come?</p>',
            unsafe_allow_html=True)
st.caption(
    "Breakdown of reviews by visit context — Weekday, Weekend, Public holiday."
)

context_stats = (
    pfm.groupby("visit_context")
    .agg(
        Reviews=("rating", "count"),
        Avg_Rating=("rating", "mean"),
        Positive=("sentiment", lambda x: (x == "Positive").mean() * 100),
    )
    .round(2)
    .reset_index()
    .sort_values("Reviews", ascending=False)
)

c1, c2 = st.columns(2)

with c1:
    with st.container(border=True):
        st.markdown("### Review Volume by Context")
        ctx_vol = context_stats.copy()
        ctx_vol["Label"] = ctx_vol["Reviews"].astype(str)
        ctx_vol["Percent"] = (ctx_vol["Reviews"] / total_reviews * 100).round(1)

        base = alt.Chart(ctx_vol).encode(
            x=alt.X("visit_context:N", title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Reviews:Q", title="Reviews"),
        )

        bars = base.mark_bar(
            color=YELLOW,
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
            cursor="pointer",
        ).encode(
            tooltip=[
                alt.Tooltip("visit_context:N", title="Context"),
                alt.Tooltip("Reviews:Q", title="Reviews"),
                alt.Tooltip("Percent:Q", title="% of total", format=".1f"),
            ]
        )

        labels = base.mark_text(
            dy=-8, fontSize=13, fontWeight="bold", color="#555"
        ).encode(text="Label:N")

        st.altair_chart((bars + labels).properties(height=300),
                        use_container_width=True)

with c2:
    with st.container(border=True):
        st.markdown("### Avg Rating by Context")
        ctx_rate = context_stats.copy()
        ctx_rate["Label"] = ctx_rate["Avg_Rating"].apply(lambda x: f"{x:.2f}")

        base = alt.Chart(ctx_rate).encode(
            x=alt.X("visit_context:N", title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Avg_Rating:Q", title="Avg Rating",
                    scale=alt.Scale(domain=[1, 5])),
        )

        bars = base.mark_bar(
            color="#2F6B7C",
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
            cursor="pointer",
        ).encode(
            tooltip=[
                alt.Tooltip("visit_context:N", title="Context"),
                alt.Tooltip("Avg_Rating:Q", title="Avg rating", format=".2f"),
                alt.Tooltip("Reviews:Q", title="Reviews"),
                alt.Tooltip("Positive:Q", title="% positive", format=".1f"),
            ]
        )

        labels = base.mark_text(
            dy=-8, fontSize=13, fontWeight="bold", color="#555"
        ).encode(text="Label:N")

        st.altair_chart((bars + labels).properties(height=300),
                        use_container_width=True)

with st.container(border=True):
    st.dataframe(context_stats, use_container_width=True, hide_index=True)


# =========================================================
# 5) REVIEW TRENDS
# =========================================================

st.markdown('<p class="pfm-section-title">5) Review Trends</p>',
            unsafe_allow_html=True)

monthly = (
    pfm.dropna(subset=["date"])
    .groupby(pfm["date"].dt.to_period("M"))
    .agg(Reviews=("rating", "count"),
         Average_Rating=("rating", "mean"))
    .reset_index()
)

if not monthly.empty:
    monthly["Month"] = monthly["date"].astype(str)

    t1, t2 = st.columns(2)

    with t1:
        with st.container(border=True):
            st.markdown("### Review Volume")
            month_vol = monthly[["Month", "Reviews"]].copy()
            month_vol["Label"] = month_vol["Reviews"].astype(str)

            base = alt.Chart(month_vol).encode(
                x=alt.X("Month:N", title="", sort=None,
                        axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("Reviews:Q", title="Reviews"),
            )

            bars = base.mark_bar(
                color=YELLOW,
                cornerRadiusTopLeft=4,
                cornerRadiusTopRight=4,
                cursor="pointer",
            ).encode(
                tooltip=[
                    alt.Tooltip("Month:N", title="Month"),
                    alt.Tooltip("Reviews:Q", title="Reviews"),
                ]
            )

            labels = base.mark_text(
                dy=-8, fontSize=11, fontWeight="bold", color="#555"
            ).encode(text="Label:N")

            st.altair_chart((bars + labels).properties(height=300),
                            use_container_width=True)

    with t2:
        with st.container(border=True):
            st.markdown("### Average Rating")
            month_rate = monthly[["Month", "Average_Rating"]].copy()
            month_rate["Label"] = month_rate["Average_Rating"].apply(lambda x: f"{x:.2f}")

            base = alt.Chart(month_rate).encode(
                x=alt.X("Month:N", title="", sort=None,
                        axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("Average_Rating:Q", title="Avg Rating",
                        scale=alt.Scale(domain=[1, 5])),
            )

            line = base.mark_line(
                color=YELLOW, strokeWidth=3, point=True
            ).encode(
                tooltip=[
                    alt.Tooltip("Month:N", title="Month"),
                    alt.Tooltip("Average_Rating:Q", title="Avg rating", format=".2f"),
                ]
            )

            labels = base.mark_text(
                dy=-10, fontSize=11, fontWeight="bold", color="#7A5B00"
            ).encode(text="Label:N")

            st.altair_chart((line + labels).properties(height=300),
                            use_container_width=True)


# =========================================================
# 6) KEYWORD ANALYSIS
# =========================================================

STOPWORDS = {
    "the","and","for","that","this","with","was","were","are","but",
    "not","you","your","from","have","has","had","very","really",
    "about","there","their","they","them","its","our","out","all",
    "one","two","too","also","can","just","been","more","much",
    "into","than","then","when","what","where","which","who","would",
    "could","should","will","get","got","we","i","it","a","an","to",
    "of","in","on","at","is","as","be","or","by","so","my","me",
    "he","she","his","her","do","did","no","yes","if","up","down",
    "over","after","before","during","through","visit","visited",
    "place","museum","penang","ferry",
}


def extract_words(texts):
    words = []
    for text in texts:
        text = str(text).lower()
        for w in re.findall(r"\b[a-zA-Z]{3,}\b", text):
            if w not in STOPWORDS:
                words.append(w)
    return Counter(words)


positive_words = extract_words(pfm[pfm["sentiment"] == "Positive"]["text"])
negative_words = extract_words(pfm[pfm["sentiment"] == "Negative"]["text"])

st.markdown('<p class="pfm-section-title">6) Keyword Analysis</p>',
            unsafe_allow_html=True)

kw1, kw2 = st.columns(2)

with kw1:
    with st.container(border=True):
        st.markdown("### Top Positive Words")
        top_pos = pd.DataFrame(
            positive_words.most_common(10),
            columns=["Word", "Count"],
        )
        if not top_pos.empty:
            top_pos["Label"] = top_pos["Count"].astype(str)

            base = alt.Chart(top_pos).encode(
                x=alt.X("Count:Q", title="Mentions"),
                y=alt.Y("Word:N", sort="-x", title=""),
            )

            bars = base.mark_bar(
                color=POSITIVE,
                cornerRadiusEnd=4,
                cursor="pointer",
            ).encode(
                tooltip=[
                    alt.Tooltip("Word:N", title="Word"),
                    alt.Tooltip("Count:Q", title="Mentions"),
                ]
            )

            labels = base.mark_text(
                dx=8, fontSize=12, fontWeight="bold", color="#333"
            ).encode(text="Label:N")

            st.altair_chart((bars + labels).properties(height=300),
                            use_container_width=True)

with kw2:
    with st.container(border=True):
        st.markdown("### Top Negative Words")
        top_neg = pd.DataFrame(
            negative_words.most_common(10),
            columns=["Word", "Count"],
        )
        if not top_neg.empty:
            top_neg["Label"] = top_neg["Count"].astype(str)

            base = alt.Chart(top_neg).encode(
                x=alt.X("Count:Q", title="Mentions"),
                y=alt.Y("Word:N", sort="-x", title=""),
            )

            bars = base.mark_bar(
                color=NEGATIVE,
                cornerRadiusEnd=4,
                cursor="pointer",
            ).encode(
                tooltip=[
                    alt.Tooltip("Word:N", title="Word"),
                    alt.Tooltip("Count:Q", title="Mentions"),
                ]
            )

            labels = base.mark_text(
                dx=8, fontSize=12, fontWeight="bold", color="#333"
            ).encode(text="Label:N")

            st.altair_chart((bars + labels).properties(height=300),
                            use_container_width=True)
        else:
            st.info("No negative reviews to analyse.")


# =========================================================
# 7) REPRESENTATIVE REVIEWS
# =========================================================

st.markdown('<p class="pfm-section-title">7) Representative Visitor Reviews</p>',
            unsafe_allow_html=True)

search_query = st.text_input(
    "Search reviews by keyword:",
    placeholder="e.g. staff, ticket, photo, price...",
    key="representative_review_search",
)

base_reviews = pfm[pfm["text"].astype(str).str.len() > 40].copy()

if search_query.strip():
    base_reviews = base_reviews[
        base_reviews["text"].astype(str).str.contains(
            search_query.strip(), case=False, na=False
        )
    ]
    st.caption(f"Showing {len(base_reviews):,} reviews matching '{search_query}'.")

r1, r2 = st.columns(2)

with r1:
    pos_samples = (
        base_reviews[base_reviews["sentiment"] == "Positive"]
        .sort_values("rating", ascending=False)
        .head(5)
    )
    st.markdown(f"### Positive Feedback — {len(pos_samples)} shown")

    if pos_samples.empty:
        st.info("No matching positive reviews found.")
    else:
        for _, row in pos_samples.iterrows():
            txt = str(row["text"]).strip()
            if len(txt) > 300:
                txt = txt[:300] + "..."

            review_url = row.get("reviewUrl", "")

            with st.container(border=True):
                st.markdown(f":green[**{row['name']} — {row['rating']:.0f}/5**]")
                st.write(txt)
                if pd.notna(review_url) and str(review_url).strip():
                    st.markdown(f"[Read on Google]({review_url})")

with r2:
    neg_samples = (
        base_reviews[base_reviews["sentiment"] == "Negative"]
        .sort_values("rating", ascending=True)
        .head(5)
    )
    st.markdown(f"### Critical Feedback — {len(neg_samples)} shown")

    if neg_samples.empty:
        st.info("No matching negative reviews found.")
    else:
        for _, row in neg_samples.iterrows():
            txt = str(row["text"]).strip()
            if len(txt) > 300:
                txt = txt[:300] + "..."

            review_url = row.get("reviewUrl", "")

            with st.container(border=True):
                st.markdown(f":red[**{row['name']} — {row['rating']:.0f}/5**]")
                st.write(txt)
                if pd.notna(review_url) and str(review_url).strip():
                    st.markdown(f"[Read on Google]({review_url})")


# =========================================================
# 8) MANAGEMENT INSIGHTS
# =========================================================

st.markdown('<p class="pfm-section-title">8) Management Insights</p>',
            unsafe_allow_html=True)

i1, i2 = st.columns(2)

with i1:
    with st.container(border=True):
        st.markdown("### Visitor Strengths")
        strengths = []
        if avg_rating >= 4:
            strengths.append(f"Average rating is {avg_rating:.2f}/5.")
        if positive_pct >= 70:
            strengths.append(f"{positive_pct:.1f}% of reviews are positive.")
        if positive_words:
            strengths.append(
                f"Most mentioned positive theme: "
                f"**'{positive_words.most_common(1)[0][0].title()}'**."
            )
        if response_rate > 0:
            strengths.append(f"Owner responds to {response_rate:.1f}% of reviews.")
        if not strengths:
            strengths.append("Continue monitoring to identify strengths.")
        for s in strengths:
            st.write(f"• {s}")

with i2:
    with st.container(border=True):
        st.markdown("### Areas to Monitor")
        improvements = []
        if negative_pct > 15:
            improvements.append(f"Negative reviews are {negative_pct:.1f}% of total.")
        if negative_words:
            improvements.append(
                f"Common complaint term: "
                f"**'{negative_words.most_common(1)[0][0].title()}'**."
            )
        if response_rate < 30:
            improvements.append(
                f"Owner response rate is low ({response_rate:.1f}%). "
                "Aim for at least 30%."
            )
        if not improvements:
            improvements.append("Keep monitoring for emerging issues.")
        for s in improvements:
            st.write(f"• {s}")


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption(
    "Note: Sentiment is derived from review ratings "
    "(4–5 = Positive, 3 = Neutral, 1–2 = Negative)."
)