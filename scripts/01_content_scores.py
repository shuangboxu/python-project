"""Generate content-based component scores for movies."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from wordcloud import WordCloud

from content_utils import (
    build_document,
    compute_content_features,
    load_movie_data,
    parse_iterable_from_cell,
)

# Paths
RAW_DATA_PATH = Path("data/raw/movies.xlsx")
PROCESSED_DIR = Path("data/processed")
TABLES_DIR = Path("reports/tables")
LOGS_DIR = Path("reports/logs")
FIGURES_DIR = Path("reports/figures")
OUTPUT_TABLE = TABLES_DIR / "01_content_scores.csv"
FEATURE_EXPORT = PROCESSED_DIR / "01_content_features.csv"


FEATURE_WEIGHTS: Dict[str, float] = {
    "tfidf_norm": 0.35,
    "keyword_count": 0.18,
    "genre_count": 0.12,
    "overview_word_count": 0.18,
    "overview_char_length": 0.10,
    "title_char_length": 0.07,
}


def ensure_directories() -> None:
    for directory in (PROCESSED_DIR, TABLES_DIR, LOGS_DIR, FIGURES_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def prepare_dataframe() -> pd.DataFrame:
    df = load_movie_data(RAW_DATA_PATH)

    df = df.rename(columns={"id": "movie_id"})
    df = df.dropna(subset=["movie_id", "title"]).copy()

    df["genres_list"] = df["genres"].apply(parse_iterable_from_cell)
    df["keywords_list"] = df["keywords"].apply(parse_iterable_from_cell)

    df["document"] = df.apply(build_document, axis=1)

    return df


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    vectorizer = TfidfVectorizer(max_features=8000, min_df=2)
    features = compute_content_features(df, vectorizer)

    engineered = pd.DataFrame({
        "tfidf_norm": features["tfidf_norm"],
        "keyword_count": np.log1p(features["keyword_count"]),
        "genre_count": features["genre_count"],
        "overview_word_count": np.log1p(features["overview_word_count"]),
        "overview_char_length": np.log1p(features["overview_char_length"]),
        "title_char_length": np.log1p(features["title_char_length"]),
    })

    scaler = MinMaxScaler()
    scaled = pd.DataFrame(
        scaler.fit_transform(engineered),
        columns=[f"scaled_{col}" for col in engineered.columns],
        index=df.index,
    )

    df[engineered.columns] = engineered
    df[scaled.columns] = scaled

    weight_series = pd.Series(FEATURE_WEIGHTS)
    weight_series = weight_series / weight_series.sum()

    df["component_score"] = (
        scaled.mul(weight_series.values, axis=1).sum(axis=1) * 100
    )

    return df


def export_outputs(df: pd.DataFrame) -> None:
    df_sorted = df.sort_values("component_score", ascending=False)

    output = df_sorted[["movie_id", "title", "component_score"]]
    output.to_csv(OUTPUT_TABLE, index=False)

    features_to_save = df_sorted[
        [
            "movie_id",
            "title",
            "component_score",
            "tfidf_norm",
            "keyword_count",
            "genre_count",
            "overview_word_count",
            "overview_char_length",
            "title_char_length",
            "scaled_tfidf_norm",
            "scaled_keyword_count",
            "scaled_genre_count",
            "scaled_overview_word_count",
            "scaled_overview_char_length",
            "scaled_title_char_length",
            "genres_list",
            "keywords_list",
        ]
    ].copy()
    features_to_save.to_csv(FEATURE_EXPORT, index=False)


def plot_score_distribution(df: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 5))
    plt.hist(df["component_score"], bins=30, color="#3776ab", edgecolor="black", alpha=0.75)
    plt.title("Content Component Score Distribution")
    plt.xlabel("Component Score")
    plt.ylabel("Number of Movies")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "01_score_distribution.png", dpi=300)
    plt.close()


def plot_genre_profile(df: pd.DataFrame) -> None:
    exploded = df.explode("genres_list").dropna(subset=["genres_list"])
    if exploded.empty:
        return

    genre_scores = (
        exploded.groupby("genres_list")["component_score"].mean().sort_values(ascending=False)
    )

    top_genres = genre_scores.head(10)

    plt.figure(figsize=(8, 6))
    top_genres.iloc[::-1].plot(kind="barh", color="#ff8c00")
    plt.title("Top Genres by Average Content Score")
    plt.xlabel("Average Component Score")
    plt.ylabel("Genre")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "01_genre_score_profile.png", dpi=300)
    plt.close()


def plot_keyword_cloud(df: pd.DataFrame) -> None:
    keywords = df["keywords_list"].explode().dropna()
    if keywords.empty:
        return

    frequencies = keywords.value_counts().to_dict()
    word_cloud = WordCloud(
        width=1600,
        height=900,
        background_color="white",
        colormap="viridis",
    ).generate_from_frequencies(frequencies)

    plt.figure(figsize=(12, 7))
    plt.imshow(word_cloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(FIGURES_DIR / "01_keyword_wordcloud.png", dpi=300)
    plt.close()


def plot_keyword_frequency(df: pd.DataFrame) -> None:
    keywords = df["keywords_list"].explode().dropna()
    if keywords.empty:
        return

    top_keywords = keywords.value_counts().head(15)

    plt.figure(figsize=(8, 6))
    top_keywords.iloc[::-1].plot(kind="barh", color="#4c72b0")
    plt.title("Top Keywords Frequency")
    plt.xlabel("Count")
    plt.ylabel("Keyword")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "01_keyword_frequency.png", dpi=300)
    plt.close()


def plot_tfidf_vs_score(df: pd.DataFrame) -> None:
    plt.figure(figsize=(7, 6))
    plt.scatter(
        df["scaled_tfidf_norm"],
        df["component_score"],
        alpha=0.5,
        s=20,
        color="#2ca02c",
        edgecolor="white",
        linewidth=0.3,
    )
    plt.xlabel("Scaled TF-IDF Norm")
    plt.ylabel("Component Score")
    plt.title("Content Score vs. TF-IDF Signal Strength")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "01_tfidf_vs_score.png", dpi=300)
    plt.close()


def main() -> None:
    ensure_directories()
    df = prepare_dataframe()
    df_scored = compute_scores(df)
    export_outputs(df_scored)
    plot_score_distribution(df_scored)
    plot_genre_profile(df_scored)
    plot_keyword_cloud(df_scored)
    plot_keyword_frequency(df_scored)
    plot_tfidf_vs_score(df_scored)


if __name__ == "__main__":
    main()