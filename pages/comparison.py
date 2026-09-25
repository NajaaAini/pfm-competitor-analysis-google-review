# pages/comparison.py
import streamlit as st
import pandas as pd
import altair as alt
import re
import base64
from collections import Counter
from pathlib import Path

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from data_loader import load_data
from styles import apply_global_styles, render_sidebar, YELLOW, POSITIVE, NEGATIVE


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Competitor Comparison | Penang Ferry Museum",
    page_icon="🚢",
    layout="wide",
)

apply_global_styles()
render_sidebar(current_page="comparison")


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
    Competitor Comparison
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
    Penang Ferry Museum vs Penang Attractions
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
            key="date_preset",
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
        else:
            picked = st.date_input(
                "Custom range:",
                value=(global_min, global_max),
                min_value=global_min,
                max_value=global_max,
                key="custom_date_range",
            )
            if isinstance(picked, tuple) and len(picked) == 2:
                start_date, end_date = picked
            else:
                start_date, end_date = global_min, global_max

        if start_date < global_min:
            start_date = global_min
        if end_date > global_max:
            end_date = global_max

        st.session_state["filter_start"] = start_date
        st.session_state["filter_end"] = end_date

        st.caption(f"Range: **{start_date}** → **{end_date}**")
else:
    st.session_state["filter_start"] = None
    st.session_state["filter_end"] = None


# ============================================================
# APPLY FILTER
# ============================================================

if (st.session_state.get("filter_start") is not None
        and st.session_state.get("filter_end") is not None):

    start_date = st.session_state["filter_start"]
    end_date = st.session_state["filter_end"]

    mask = ((df["date"].dt.date >= start_date)
            & (df["date"].dt.date <= end_date))
    df = df[mask].copy()


# ============================================================
# COMPETITOR SELECTOR (MAIN PAGE)
# ============================================================

st.markdown('<p class="pfm-section-title">Select Competitors</p>',
            unsafe_allow_html=True)

attractions = sorted(
    df["attraction_name"].dropna().astype(str).str.strip().unique().tolist()
)
competitors = [x for x in attractions if x != "Penang Ferry Museum"]

selected_competitors = st.multiselect(
    "Choose one or more attractions to compare with Penang Ferry Museum:",
    competitors,
    default=competitors[:2] if len(competitors) >= 2 else competitors,
    key="selected_competitors",
)

if not selected_competitors:
    st.info("Please select at least one competitor to continue.")
    st.stop()

comparison_attractions = ["Penang Ferry Museum"] + selected_competitors


# ============================================================
# COLOURS
# ============================================================

colour_palette = [YELLOW, "#2F6B7C", "#C75B39", "#5B4B8A",
                  "#4C8C5A", "#B45F8A", "#6A6A6A",
                  "#D46A1F", "#3F7CAC", "#8A6F3D"]

attraction_colors = {
    a: colour_palette[i % len(colour_palette)]
    for i, a in enumerate(comparison_attractions)
}


# ============================================================
# DATAFRAMES
# ============================================================

pfm_df = df[df["attraction_name"] == "Penang Ferry Museum"].copy()
competitor_dfs = {
    c: df[df["attraction_name"] == c].copy()
    for c in selected_competitors
}


# ============================================================
# SUMMARY
# ============================================================

rows = []
for a in comparison_attractions:
    a_df = pfm_df if a == "Penang Ferry Museum" else competitor_dfs[a]
    rows.append({
        "Attraction": a,
        "Reviews": len(a_df),
        "Average Rating": round(a_df["rating"].mean(), 2) if len(a_df) else 0,
        "Positive %": round(a_df["rating"].apply(lambda x: x >= 4).mean() * 100, 1)
                      if len(a_df) else 0,
    })

summary = pd.DataFrame(rows)


# ============================================================
# 1) RATING & REVIEW VOLUME
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">1) Rating & Review Volume</p>',
            unsafe_allow_html=True)

cols = st.columns(min(len(comparison_attractions), 4))
for i, a in enumerate(comparison_attractions):
    row = summary[summary["Attraction"] == a].iloc[0]
    with cols[i % len(cols)]:
        st.metric(
            f"{a}",
            f"{row['Average Rating']:.2f} / 5",
            help=f"{int(row['Reviews']):,} reviews · Positive rate: {row['Positive %']:.1f}%",
        )
        st.caption(f"{int(row['Reviews']):,} reviews")

with st.container(border=True):
    st.dataframe(summary, use_container_width=True, hide_index=True)

rating_chart_df = summary[["Attraction", "Average Rating"]].copy()
rating_chart_df["Label"] = rating_chart_df["Average Rating"].apply(lambda x: f"{x:.2f}")

base = alt.Chart(rating_chart_df).encode(
    x=alt.X("Attraction:N", title="", sort=None,
            axis=alt.Axis(labelAngle=-25)),
    y=alt.Y("Average Rating:Q", title="Average Rating",
            scale=alt.Scale(domain=[0, 5])),
)
bars = base.mark_bar(cursor="pointer").encode(
    color=alt.Color("Attraction:N",
                    scale=alt.Scale(domain=list(attraction_colors.keys()),
                                    range=list(attraction_colors.values())),
                    legend=None),
    tooltip=[
        alt.Tooltip("Attraction:N", title="Attraction"),
        alt.Tooltip("Average Rating:Q", title="Average Rating", format=".2f"),
    ],
)
labels = base.mark_text(dy=-8, fontSize=12, fontWeight="bold",
                        color="#555").encode(text="Label:N")

st.altair_chart((bars + labels).properties(height=320),
                use_container_width=True)


# ============================================================
# 2) RATING TREND & SENTIMENT
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">2) Rating Trend & Sentiment</p>',
            unsafe_allow_html=True)

left_col, right_col = st.columns(2)

with left_col:
    with st.container(border=True):
        st.markdown("### Rating Trend Over Time")

        trend_rows = []
        for a in comparison_attractions:
            a_df = pfm_df if a == "Penang Ferry Museum" else competitor_dfs[a]
            a_df = a_df.dropna(subset=["date", "rating"])
            if a_df.empty:
                continue

            period = a_df["date"].dt.to_period("M")
            period_ts = period.dt.to_timestamp()
            period_label = period_ts.dt.strftime("%Y-%m")

            grouped = (
                a_df.assign(Period_ts=period_ts.values,
                            Period_label=period_label.values)
                .groupby(["Period_ts", "Period_label"])["rating"]
                .agg(["mean", "count"])
                .reset_index()
            )
            grouped["Attraction"] = a
            grouped = grouped.rename(columns={"mean": "Avg Rating", "count": "Reviews"})
            trend_rows.append(
                grouped[["Period_ts", "Period_label", "Attraction", "Avg Rating", "Reviews"]]
            )

        if trend_rows:
            trend_df = pd.concat(trend_rows, ignore_index=True)
            trend_df = trend_df[trend_df["Reviews"] >= 1]
            trend_df = trend_df.sort_values(["Period_ts", "Attraction"])

            if not trend_df.empty:
                y_min = trend_df["Avg Rating"].min()
                y_max = trend_df["Avg Rating"].max()
                pad = 0.3
                y_lower = max(0, round((y_min - pad) * 2) / 2)
                y_upper = min(5, round((y_max + pad) * 2) / 2)

                trend_chart = (
                    alt.Chart(trend_df)
                    .mark_line(point=True, strokeWidth=2.5)
                    .encode(
                        x=alt.X(
                            "Period_ts:T",
                            title="Period",
                            axis=alt.Axis(format="%Y-%m", labelAngle=-45,
                                          tickCount="month"),
                        ),
                        y=alt.Y(
                            "Avg Rating:Q",
                            title="Average Rating",
                            scale=alt.Scale(domain=[y_lower, y_upper], nice=False),
                        ),
                        color=alt.Color(
                            "Attraction:N",
                            scale=alt.Scale(
                                domain=list(attraction_colors.keys()),
                                range=list(attraction_colors.values()),
                            ),
                        ),
                        tooltip=[
                            alt.Tooltip("Period_label:N", title="Period"),
                            "Attraction",
                            alt.Tooltip("Avg Rating:Q", format=".2f"),
                            "Reviews",
                        ],
                    )
                    .properties(height=360)
                )
                st.altair_chart(trend_chart, use_container_width=True)
            else:
                st.info("No dated reviews available to plot trend.")
        else:
            st.info("No dated reviews available to plot trend.")

with right_col:
    with st.container(border=True):
        st.markdown("### Volume by Sentiment")

        sent_rows = []
        for a in comparison_attractions:
            a_df = pfm_df if a == "Penang Ferry Museum" else competitor_dfs[a]
            counts = a_df["sentiment"].value_counts().reindex(
                ["Positive", "Neutral", "Negative"], fill_value=0
            )
            for s in ["Positive", "Neutral", "Negative"]:
                sent_rows.append({"Attraction": a, "Sentiment": s,
                                  "Reviews": int(counts[s])})

        sent_long = pd.DataFrame(sent_rows)
        sent_long["Label"] = sent_long["Reviews"].astype(str)

        base = alt.Chart(sent_long).encode(
            x=alt.X("Sentiment:N", title=""),
            xOffset=alt.XOffset("Attraction:N"),
            y=alt.Y("Reviews:Q", title="Reviews"),
        )
        bars = base.mark_bar(cursor="pointer").encode(
            color=alt.Color("Attraction:N",
                            scale=alt.Scale(domain=list(attraction_colors.keys()),
                                            range=list(attraction_colors.values()))),
            tooltip=["Attraction", "Sentiment", "Reviews"],
        )
        labels = base.mark_text(dy=-6, fontSize=10, fontWeight="bold",
                                color="#555").encode(text="Label:N")

        st.altair_chart((bars + labels).properties(height=360),
                        use_container_width=True)


# ============================================================
# 3) OWNER RESPONSE COMPARISON
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">3) Owner Response Comparison</p>',
            unsafe_allow_html=True)

owner_rows = []
for a in comparison_attractions:
    a_df = pfm_df if a == "Penang Ferry Museum" else competitor_dfs[a]
    if a_df.empty:
        continue
    neg = a_df[a_df["sentiment"] == "Negative"]
    owner_rows.append({
        "Attraction": a,
        "Reviews": len(a_df),
        "Responded": int(a_df["owner_responded"].sum()),
        "Response Rate %": round(a_df["owner_responded"].mean() * 100, 1),
        "Negative Responded %": round(neg["owner_responded"].mean() * 100, 1)
                                  if len(neg) else 0,
    })

owner_df = pd.DataFrame(owner_rows)

with st.container(border=True):
    st.dataframe(owner_df, use_container_width=True, hide_index=True)

st.markdown("**How owners handle visitor feedback**")
st.caption(
    "Select an attraction and rating level to see how the owner responds to reviews."
)

with st.expander("**Show owner responses**"):
    sample_attraction = st.selectbox(
        "**Choose attraction:**",
        comparison_attractions,
        key="owner_response_sample_attraction",
    )
    sample_df = (pfm_df if sample_attraction == "Penang Ferry Museum"
                 else competitor_dfs[sample_attraction])

    rating_filter = st.radio(
        "**Filter by rating:**",
        ["All", "5★", "4★", "3★", "2★", "1★"],
        horizontal=True,
        key="owner_response_rating_filter",
    )

    n_samples = st.slider(
        "**Number of responses to show:**",
        min_value=5, max_value=50, value=10, step=5,
        key="owner_response_n_samples",
    )

    all_samples = sample_df[sample_df["owner_responded"]].copy()
    if rating_filter != "All":
        target = int(rating_filter.replace("★", ""))
        all_samples = all_samples[all_samples["rating"].round() == target]

    total_available = len(all_samples)
    samples = all_samples.head(n_samples)

    st.caption(
        f"Showing **{len(samples)}** of **{total_available}** available responses."
    )

    if samples.empty:
        st.info("No owner responses match this filter.")
    else:
        for _, row in samples.iterrows():
            guest_text = str(row.get("text", "")).strip()
            if len(guest_text) > 250:
                guest_text = guest_text[:250] + "..."

            review_url = row.get("reviewUrl", "")

            st.markdown(f"**{row['rating']:.0f}★ review**")
            st.write(guest_text)
            st.success(f"**Owner:** {row['responseFromOwnerText']}")
            if pd.notna(review_url) and str(review_url).strip():
                st.markdown(f"[Read on Google]({review_url})")
            st.markdown("---")


# ============================================================
# 4) VISIT CONTEXT COMPARISON
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">4) Visit Context Comparison</p>',
            unsafe_allow_html=True)

ctx_rows = []
for a in comparison_attractions:
    a_df = pfm_df if a == "Penang Ferry Museum" else competitor_dfs[a]
    if a_df.empty:
        continue
    for ctx in ["Weekday", "Weekend", "Public holiday", "Not specified"]:
        sub = a_df[a_df["visit_context"] == ctx]
        ctx_rows.append({
            "Attraction": a,
            "Context": ctx,
            "Reviews": len(sub),
            "Avg Rating": round(sub["rating"].mean(), 2) if len(sub) else 0,
        })

ctx_df = pd.DataFrame(ctx_rows)

if not ctx_df.empty:
    ctx_df["Label"] = ctx_df["Reviews"].astype(str)

    base = alt.Chart(ctx_df).encode(
        x=alt.X("Context:N", title=""),
        xOffset=alt.XOffset("Attraction:N"),
        y=alt.Y("Reviews:Q", title="Reviews"),
    )
    bars = base.mark_bar(cursor="pointer").encode(
        color=alt.Color("Attraction:N",
                        scale=alt.Scale(domain=list(attraction_colors.keys()),
                                        range=list(attraction_colors.values()))),
        tooltip=["Attraction", "Context", "Reviews", "Avg Rating"],
    )
    labels = base.mark_text(dy=-6, fontSize=10, fontWeight="bold",
                            color="#555").encode(text="Label:N")

    st.altair_chart((bars + labels).properties(height=340),
                    use_container_width=True)

    with st.container(border=True):
        st.dataframe(ctx_df, use_container_width=True, hide_index=True)


# ============================================================
# 5) VISITOR TOPICS (LDA)
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">5) Visitor Topics</p>',
            unsafe_allow_html=True)

corpus_records = []
for a in comparison_attractions:
    a_df = pfm_df if a == "Penang Ferry Museum" else competitor_dfs[a]
    for idx, row in a_df.iterrows():
        text = str(row.get("text", "")).strip()
        corpus_records.append({
            "attraction": a,
            "row_idx": idx,
            "text": text,
        })

corpus_texts = [r["text"].lower() for r in corpus_records]

if len(corpus_texts) >= 10:
    vectorizer = CountVectorizer(
        max_df=0.95,
        min_df=2,
        stop_words="english",
        max_features=800,
        ngram_range=(1, 1),
    )

    try:
        X = vectorizer.fit_transform(corpus_texts)
        feature_names = vectorizer.get_feature_names_out()
    except ValueError:
        X = None
        feature_names = []

    if X is not None and X.shape[1] > 0:
        N_TOPICS = 8
        N_TOPICS = min(N_TOPICS, X.shape[1])

        lda = LatentDirichletAllocation(
            n_components=N_TOPICS,
            random_state=42,
            max_iter=15,
            learning_method="batch",
        )
        lda.fit(X)

        topics_words = {}
        for i, topic_dist in enumerate(lda.components_):
            top_idx = topic_dist.argsort()[-8:][::-1]
            words = [feature_names[j] for j in top_idx]
            topics_words[i] = words

        def make_label(words, i):
            return f"Topic {i+1}: " + ", ".join(w.title() for w in words[:3])

        topic_labels = {i: make_label(w, i) for i, w in topics_words.items()}

        review_topics = lda.transform(X)
        assigned = review_topics.argmax(axis=1)

        topic_rows = []
        for idx, rec in enumerate(corpus_records):
            topic_id = int(assigned[idx])
            topic_rows.append({
                "Attraction": rec["attraction"],
                "TopicID": topic_id,
                "Topic": topic_labels[topic_id],
                "RowIdx": rec["row_idx"],
            })

        topic_assign = pd.DataFrame(topic_rows)

        topic_counts_df = (
            topic_assign
            .groupby(["Attraction", "TopicID", "Topic"])
            .size()
            .reset_index(name="Mentions")
        )

        with st.expander("View LDA topic keywords"):
            for i in sorted(topics_words.keys()):
                st.markdown(
                    f"**{topic_labels[i]}**  \n"
                    f"*Top words:* {', '.join(topics_words[i])}"
                )

        st.markdown(
            '<p style="font-size:15px;font-weight:700;color:#292929;'
            'margin:10px 0 6px 0;text-transform:uppercase;letter-spacing:0.5px;">'
            'Topic Mentions by Attraction</p>',
            unsafe_allow_html=True,
        )

        topic_options = sorted(topic_counts_df["Topic"].unique().tolist())

        selected_topic = st.selectbox(
            "**Choose a topic:**",
            topic_options,
            key="lda_topic_selector",
            label_visibility="collapsed",
        )

        sel_df = topic_counts_df[topic_counts_df["Topic"] == selected_topic]

        complete = []
        for a in comparison_attractions:
            m = sel_df[sel_df["Attraction"] == a]
            complete.append({
                "Attraction": a,
                "Mentions": int(m["Mentions"].sum()) if not m.empty else 0,
            })
        sel_df = pd.DataFrame(complete)
        sel_df["Label"] = sel_df["Mentions"].astype(str)

        base = alt.Chart(sel_df).encode(
            x=alt.X("Attraction:N", title="",
                    axis=alt.Axis(labelAngle=-25)),
            y=alt.Y("Mentions:Q", title="Review Mentions"),
        )
        bars = base.mark_bar(cursor="pointer").encode(
            color=alt.Color("Attraction:N",
                            scale=alt.Scale(
                                domain=list(attraction_colors.keys()),
                                range=list(attraction_colors.values()),
                            ),
                            legend=None),
            tooltip=["Attraction", "Mentions"],
        )
        labels = base.mark_text(dy=-8, fontSize=12, fontWeight="bold",
                                color="#555").encode(text="Label:N")

        st.altair_chart((bars + labels).properties(height=300),
                        use_container_width=True)

        with st.expander(f"See sample reviews for '{selected_topic}'"):
            for a in comparison_attractions:
                rows_for_a = topic_assign[
                    (topic_assign["Attraction"] == a)
                    & (topic_assign["Topic"] == selected_topic)
                ]

                if rows_for_a.empty:
                    continue

                a_full = pfm_df if a == "Penang Ferry Museum" else competitor_dfs[a]
                st.markdown(f"**{a}** — {len(rows_for_a)} mentions")

                sample_idx = rows_for_a["RowIdx"].head(3).tolist()
                samples = a_full.loc[a_full.index.isin(sample_idx)]

                for _, srow in samples.iterrows():
                    with st.expander(
                        f"{srow['rating']:.0f}★ — {srow.get('name', 'Anonymous')}"
                    ):
                        st.write(str(srow.get("text", "")).strip())
                st.markdown("---")
    else:
        st.info("Not enough review text available to run topic modelling.")
else:
    st.info("Not enough review text available to run topic modelling.")