# data_loader.py
import pandas as pd
import streamlit as st
from pathlib import Path

GOOGLE_FILE = "FULL DATA.xlsx"
SHEET_NAME = "Sheet1"


# ============================================================
# NAME CLEANING
# ============================================================

NAME_MAPPING = {
    "Penang Ferry Museum": [
        "penang ferry museum",
        "the penang ferry museum",
        "ferry museum penang",
    ],
    "Penang 3D Trick Art Museum": [
        "penang 3d trick art museum",
        "3d trick art museum",
        "penang 3d trick art",
    ],
    "Pinang Peranakan Mansion": [
        "pinang peranakan mansion",
        "peranakan mansion",
    ],
    "Khoo Kongsi": ["khoo kongsi", "leong san tong khoo kongsi"],
    "Wonderfood Museum": ["wonderfood museum"],
    "The Habitat Penang Hill": ["the habitat penang hill", "the habitat"],
    "Entopia by Penang Butterfly Farm": [
        "entopia",
        "penang butterfly farm",
    ],
    "Penang Hill": ["penang hill", "bukit bendera"],
    "Fort Cornwallis": ["fort cornwallis"],
    "Penang History Gallery": ["penang history gallery"],
    "Colonial Penang Museum": ["colonial penang museum"],
    "Asia Camera Museum": ["asia camera museum"],
    "Upside Down Museum": ["upside down museum"],
    "Ghost Museum": ["ghost museum"],
    "The TOP Penang": ["the top penang", "the top"],
    "Tech Dome Penang": ["tech dome penang"],
    "ESCAPE Penang": ["escape penang", "escape theme park"],
    "Botanical Gardens Penang": [
        "botanical gardens penang",
        "penang botanical gardens",
    ],
    "Chew Jetty": ["chew jetty", "clan jetties of penang"],
}


def clean_attraction_name(raw):
    """Normalize an attraction name to its canonical form."""
    if pd.isna(raw):
        return "Unknown"

    # collapse whitespace + lowercase
    name = " ".join(str(raw).strip().lower().split())

    # exact canonical match first (fastest + safest)
    for canonical in NAME_MAPPING.keys():
        if name == canonical.lower():
            return canonical

    # substring match
    for canonical, variants in NAME_MAPPING.items():
        for v in variants:
            if v in name:
                return canonical

    # fallback: title-case the raw value
    return str(raw).strip().title()


# ============================================================
# SENTIMENT
# ============================================================

def map_sentiment(rating):
    if pd.isna(rating):
        return "Unknown"
    if rating >= 4:
        return "Positive"
    if rating == 3:
        return "Neutral"
    return "Negative"


# ============================================================
# VISIT CONTEXT
# ============================================================

def normalize_visit_context(value):
    if pd.isna(value):
        return "Not specified"
    v = str(value).strip().lower()
    if "public" in v or "holiday" in v:
        return "Public holiday"
    if "weekend" in v:
        return "Weekend"
    if "weekday" in v:
        return "Weekday"
    return "Not specified"


# ============================================================
# OWNER RESPONSE
# ============================================================

def has_owner_response(text):
    if pd.isna(text):
        return False
    return len(str(text).strip()) > 0


# ============================================================
# MAIN LOADER
# ============================================================

@st.cache_data(show_spinner=False)
def load_data():
    path = Path(GOOGLE_FILE)
    if not path.exists():
        st.error(f"File not found: {GOOGLE_FILE}")
        st.stop()

    raw = pd.read_excel(path, sheet_name=SHEET_NAME)

    def col(name, default=""):
        """Safely fetch a column (returns default if missing)."""
        if name in raw.columns:
            return raw[name]
        return pd.Series([default] * len(raw))

    df = pd.DataFrame({
        # ⚠️ Attraction name lives in "title", NOT "name"
        # "name" is the REVIEWER name
        "attraction_name":  col("title", ""),
        "reviewer_name":    col("name", ""),
        "platform":         "Google Maps",
        "rating":           pd.to_numeric(col("stars", None), errors="coerce"),
        "text":             col("text", "").fillna("").astype(str),
        "text_translated":  col("textTranslated", "").fillna("").astype(str),
        "date":             pd.to_datetime(col("publishedAtDate", None),
                                           errors="coerce"),
        "visit_context":    col("reviewContext/Visited on", "")
                                .apply(normalize_visit_context),
        "owner_response":   col("responseFromOwnerText", "")
                                .fillna("").astype(str),
        "language":         col("originalLanguage", "unknown")
                                .fillna("unknown").astype(str),
        "lat":              pd.to_numeric(col("location/lat", None),
                                          errors="coerce"),
        "lng":              pd.to_numeric(col("location/lng", None),
                                          errors="coerce"),
        "category":         col("categoryName", "Unknown")
                                .fillna("Unknown").astype(str),
    })

    df["attraction_name"] = df["attraction_name"].apply(clean_attraction_name)
    df["sentiment"] = df["rating"].apply(map_sentiment)
    df["owner_responded"] = df["owner_response"].apply(has_owner_response)

    # Drop rows without a rating
    df = df.dropna(subset=["rating"]).reset_index(drop=True)

    return df


# ============================================================
# COORDINATES — now built FROM the data, not hardcoded
# ============================================================

@st.cache_data(show_spinner=False)
def get_attraction_coords():
    """
    Returns a dict: { attraction_name -> (lat, lng) }
    Computed from the mean of location/lat + location/lng in the dataset.
    """
    df = load_data()

    coords = (
        df.dropna(subset=["lat", "lng"])
          .groupby("attraction_name")[["lat", "lng"]]
          .mean()
          .round(6)
          .to_dict(orient="index")
    )

    # convert nested dict to tuples
    return {k: (v["lat"], v["lng"]) for k, v in coords.items()}


def get_geolocation(attraction_name):
    """Safe lookup — falls back to central George Town."""
    coords = get_attraction_coords()
    return coords.get(attraction_name, (5.4164, 100.3400))