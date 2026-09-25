#detail_review.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from pathlib import Path

from styles import apply_global_styles, render_sidebar


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Penang Ferry Museum & Attractions Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# GLOBAL STYLES
# ============================================================

apply_global_styles()


# ============================================================
# LOAD AND CLEAN DATA
# ============================================================

@st.cache_data
def load_data():

    base_dir = Path(__file__).parent
    google_file = base_dir / "FULL DATA.xlsx"

    google_df = pd.read_excel(
        google_file,
        sheet_name="Sheet1"
    )

    google_clean = pd.DataFrame({

        "attraction_name":
            google_df["title"].astype(str).str.strip(),

        "platform":
            "Google Maps",

        "rating":
            google_df["stars"],

        "text":
            google_df["text"].fillna("").astype(str),

        "date":
            google_df["publishedAtDate"],

        "lat":
            google_df["location/lat"],

        "lng":
            google_df["location/lng"],

        "name":
            google_df["name"] if "name" in google_df.columns else "Anonymous",

        "reviewUrl":
            google_df["reviewUrl"] if "reviewUrl" in google_df.columns else "",

        "responseFromOwnerText":
            google_df["responseFromOwnerText"]
            if "responseFromOwnerText" in google_df.columns else ""

    })

    return google_clean


# ============================================================
# LOAD DATA
# ============================================================

df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

sidebar = render_sidebar(
    current_page="detail_review",   # <-- tukar dari "combined"
    show_attraction_selector=True,
    attraction_options=sorted(df["attraction_name"].dropna().unique()),
    show_extra_filters=True,
    show_sentiment_filter=True,
)

selected_attraction = sidebar["attraction"]
rating_filter = sidebar["rating_filter"]
sentiment_filter = sidebar["sentiment_filter"]
min_words_limit = sidebar["min_words"]
max_words_limit = sidebar["max_words"]


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<p class="pfm-page-title">Penang Ferry Museum & Attractions Dashboard</p>
<p class="pfm-page-subtitle">Explore visitor reviews and attraction insights</p>
<p class="pfm-yellow-line">━━━━━</p>
""", unsafe_allow_html=True)


# ============================================================
# 1) DATASET OVERVIEW
# ============================================================

st.markdown('<p class="pfm-section-title">1) Dataset Overview</p>',
            unsafe_allow_html=True)

total_reviews = len(df)
total_attractions = df["attraction_name"].nunique()
overall_avg = df["rating"].mean()
overall_avg_rating = round(overall_avg, 2) if pd.notna(overall_avg) else "N/A"
platforms = ", ".join(df["platform"].dropna().unique())

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Total Reviews",
        f"{total_reviews:,}",
        help=f"Total number of reviews: {total_reviews:,}",
    )

with k2:
    st.metric(
        "Total Attractions",
        total_attractions,
        help=f"{total_attractions} attractions with reviews",
    )

with k3:
    st.metric(
        "Average Rating",
        f"{overall_avg_rating} / 5.0",
        help=f"Average rating across {total_reviews:,} reviews",
    )

with k4:
    st.metric(
        "Platform",
        platforms,
        help="Source of review data",
    )


# ============================================================
# 2) ATTRACTION SUMMARY
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">2) Attraction Summary</p>',
            unsafe_allow_html=True)

summary = (
    df.groupby("attraction_name")
    .agg(
        Reviews=("rating", "size"),
        Average_Rating=("rating", "mean")
    )
    .reset_index()
)

summary["Average_Rating"] = summary["Average_Rating"].round(2)
summary = summary.sort_values("Reviews", ascending=False)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 3) DETAILED ATTRACTION ANALYSIS
# ============================================================

st.markdown("---")

st.markdown("""
<p class="pfm-page-title"> Detailed Attraction Analysis</p>
<p class="pfm-page-subtitle">Review insights and visitor feedback</p>
<p class="pfm-yellow-line">━━━━━</p>
""", unsafe_allow_html=True)

st.markdown(f'<p class="pfm-section-title">{selected_attraction}</p>',
            unsafe_allow_html=True)

filtered_df = df[df["attraction_name"] == selected_attraction].copy()
analysis_df = filtered_df.copy()

if rating_filter != "All Ratings":
    star_val = int(rating_filter[0])
    analysis_df = analysis_df[analysis_df["rating"] == star_val]

analysis_df["sentiment"] = analysis_df["rating"].apply(
    lambda x: "Positive" if pd.notna(x) and x >= 4
    else ("Neutral" if pd.notna(x) and x == 3
    else ("Negative" if pd.notna(x) else "Unknown"))
)

if sentiment_filter != "All Sentiments":
    analysis_df = analysis_df[analysis_df["sentiment"] == sentiment_filter]

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Filtered Reviews", len(analysis_df))
with c2:
    avg_filtered = analysis_df["rating"].mean()
    st.metric("Average Rating",
              round(avg_filtered, 2) if pd.notna(avg_filtered) else "N/A")
with c3:
    st.metric("Platform",
              ", ".join(analysis_df["platform"].unique())
              if not analysis_df.empty else "N/A")


# ============================================================
# 4) REVIEWS SUMMARY — table + download
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">3) Reviews Summary</p>',
            unsafe_allow_html=True)

table_df = analysis_df[
    analysis_df["text"].astype(str).str.strip() != ""
].copy()

if not table_df.empty:
    display_df = table_df[["platform", "rating", "sentiment",
                           "date", "text"]].copy()
    display_df["date"] = pd.to_datetime(
        display_df["date"], errors="coerce"
    ).dt.strftime("%d %b %Y")
    display_df["date"] = display_df["date"].fillna("—")

    display_df = display_df.rename(columns={
        "platform": "Platform", "rating": "Rating",
        "sentiment": "Sentiment", "date": "Date", "text": "Review"
    })

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered reviews",
                       data=csv,
                       file_name=f"{selected_attraction}_reviews.csv",
                       mime="text/csv")
else:
    st.info("No reviews with text match the selected filters.")


# ============================================================
# 5) REVIEW DETAILS — dengan nama, owner response, link
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">4) Review Details</p>',
            unsafe_allow_html=True)
st.caption("Showing latest 10 reviews with full details.")

review_df = analysis_df[
    analysis_df["text"].astype(str).str.strip() != ""
].copy()

review_df["date"] = pd.to_datetime(review_df["date"], errors="coerce")
review_df = review_df.sort_values("date", ascending=False).head(10)

if not review_df.empty:
    for _, row in review_df.iterrows():
        rating_val = row["rating"] if pd.notna(row["rating"]) else 0
        name_val = row.get("name", "Anonymous")
        if pd.isna(name_val) or str(name_val).strip() == "":
            name_val = "Anonymous"

        text_val = str(row.get("text", "")).strip()
        if len(text_val) > 400:
            text_val = text_val[:400] + "..."

        review_url = row.get("reviewUrl", "")
        owner_response = row.get("responseFromOwnerText", "")
        date_val = row["date"]
        date_str = date_val.strftime("%d %b %Y") if pd.notna(date_val) else "—"

        sentiment_val = row.get("sentiment", "")

        with st.container(border=True):
            st.markdown(
                f"**{name_val}** · **{rating_val:.0f}★** · *{date_str}* · {sentiment_val}"
            )
            st.write(text_val)

            if pd.notna(owner_response) and str(owner_response).strip():
                st.success(f"**Owner:** {owner_response}")

            if pd.notna(review_url) and str(review_url).strip():
                st.markdown(f"[Read on Google]({review_url})")
else:
    st.info("No reviews available for the selected filters.")


# ============================================================
# 6) REVIEW TEXT ANALYSIS
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">5) Review Text Analysis</p>',
            unsafe_allow_html=True)

text_series = analysis_df["text"].astype(str)
text_series = text_series[text_series.str.strip() != ""]

corpus = " ".join(text_series.tolist())

if corpus.strip():
    wc1, wc2 = st.columns(2)

    with wc1:
        st.markdown('<p class="pfm-card-title">Unigram Word Cloud</p>',
                    unsafe_allow_html=True)
        wc = WordCloud(width=500, height=350, background_color="white",
                       colormap="Wistia", min_word_length=min_words_limit,
                       max_words=max_words_limit).generate(corpus)
        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with wc2:
        st.markdown('<p class="pfm-card-title">Bigram Word Cloud</p>',
                    unsafe_allow_html=True)
        try:
            vec = CountVectorizer(ngram_range=(2, 2), stop_words="english")
            X = vec.fit_transform(text_series.tolist())
            freqs = dict(zip(vec.get_feature_names_out(), X.sum(axis=0).A1))
        except ValueError:
            freqs = {}

        if freqs:
            wc = WordCloud(width=500, height=350, background_color="white",
                           colormap="YlOrBr",
                           max_words=max_words_limit).generate_from_frequencies(freqs)
            fig, ax = plt.subplots(figsize=(5, 3.5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        else:
            st.info("Not enough text for bigram word cloud.")
else:
    st.info("No text available for the selected filters.")


# ============================================================
# 7) ATTRACTION LOCATIONS
# ============================================================

st.markdown("---")
st.markdown('<p class="pfm-section-title">6) Attraction Locations</p>',
            unsafe_allow_html=True)

st.markdown("""
<p class="pfm-description">
    Explore the locations of Penang Ferry Museum and its competitors across Penang.
</p>
""", unsafe_allow_html=True)

coords_per_attraction = (
    df.dropna(subset=["lat", "lng"])
    .groupby("attraction_name")[["lat", "lng"]]
    .first()
    .reset_index()
)

map_selected_attraction = st.selectbox(
    "Select an attraction to view on the map",
    ["All"] + sorted(coords_per_attraction["attraction_name"].tolist()),
    key="map_attraction_selector"
)


# ---------- VIEW: SELECTED ATTRACTION ----------
if map_selected_attraction != "All":

    row = coords_per_attraction[
        coords_per_attraction["attraction_name"] == map_selected_attraction
    ].iloc[0]

    lat = row["lat"]
    lng = row["lng"]

    specific_df = df[df["attraction_name"] == map_selected_attraction].copy()

    col_info, col_map = st.columns([1, 1])

    with col_info:

        st.markdown("""
        <p class="pfm-card-title">
            Attraction Overview
        </p>
        """, unsafe_allow_html=True)

        total_revs = len(specific_df)

        avg_rating = specific_df["rating"].mean()
        avg_rating = round(avg_rating, 2) if pd.notna(avg_rating) else "N/A"

        specific_df["sentiment"] = specific_df["rating"].apply(
            lambda x: "Positive" if pd.notna(x) and x >= 4
            else ("Neutral" if pd.notna(x) and x == 3
            else ("Negative" if pd.notna(x) else "Unknown"))
        )

        positive_count = specific_df["sentiment"].eq("Positive").sum()
        negative_count = specific_df["sentiment"].eq("Negative").sum()

        positive_rate = (positive_count / total_revs * 100) if total_revs > 0 else 0
        negative_rate = (negative_count / total_revs * 100) if total_revs > 0 else 0

        specific_df["date"] = pd.to_datetime(
            specific_df["date"], errors="coerce"
        )

        latest_date = specific_df["date"].max()

        if pd.notna(latest_date):
            latest_date_text = latest_date.strftime("%d %b %Y")
        else:
            latest_date_text = "N/A"

        st.markdown(
            f"""
            <div class="pfm-card">

            <p class="pfm-card-title">
                {map_selected_attraction}
            </p>

            <p class="pfm-description">
                Performance summary based on the available
                Google Maps reviews.
            </p>

            <b>Reviews Tracked:</b>
            {total_revs:,}<br>

            <b>Average Rating:</b>
            {avg_rating} / 5.0<br>

            <b>Positive Reviews:</b>
            {positive_rate:.1f}%<br>

            <b>Negative Reviews:</b>
            {negative_rate:.1f}%<br>

            <b>Latest Review:</b>
            {latest_date_text}<br>

            <b>Platform:</b>
            Google Maps

            </div>
            """,
            unsafe_allow_html=True
        )

    with col_map:

        st.markdown("""
        <p class="pfm-card-title">
            Location
        </p>
        """, unsafe_allow_html=True)

        m = folium.Map(
            location=[lat, lng],
            zoom_start=15,
            control_scale=True
        )

        folium.Marker(
            [lat, lng],
            popup=map_selected_attraction,
            tooltip=map_selected_attraction,
            icon=folium.Icon(
                color="red",
                icon="ship",
                prefix="fa"
            )
        ).add_to(m)

        st_folium(
            m,
            height=350,
            use_container_width=True
        )


# ---------- VIEW: ALL ATTRACTIONS ----------
else:

    m = folium.Map(
        location=[5.4164, 100.3400],
        zoom_start=13,
        control_scale=True
    )

    for _, row in coords_per_attraction.iterrows():

        folium.Marker(
            [row["lat"], row["lng"]],
            popup=row["attraction_name"],
            tooltip=row["attraction_name"],
            icon=folium.Icon(
                color="red",
                icon="ship",
                prefix="fa"
            )
        ).add_to(m)

    st_folium(
        m,
        height=500,
        use_container_width=True
    )