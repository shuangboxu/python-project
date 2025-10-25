"""Utility functions for content-based movie analysis."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import ast
import re
from typing import Iterable, List, Sequence

import pandas as pd

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")


def load_movie_data(path: Path | str) -> pd.DataFrame:
    """Load the movie metadata Excel file.

    Args:
        path: Path to the Excel file.

    Returns:
        DataFrame with the movie metadata.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Movie data not found at {path}")
    return pd.read_excel(path)


def parse_iterable_from_cell(value: object) -> List[str]:
    """Parse a cell containing JSON-like lists into a list of strings."""
    if pd.isna(value):
        return []

    # Attempt to interpret as a Python literal (typical for TMDB metadata exports)
    if isinstance(value, str):
        text = value.strip()
        if text:
            try:
                parsed = ast.literal_eval(text)
            except (ValueError, SyntaxError):
                parsed = None
            if isinstance(parsed, Sequence):
                names: List[str] = []
                for item in parsed:
                    if isinstance(item, dict):
                        name = item.get("name")
                        if name:
                            names.append(str(name))
                    elif isinstance(item, str):
                        names.append(item)
                    else:
                        names.append(str(item))
                if names:
                    return names
        # Fallback: split by comma for plain text lists
        return [part.strip() for part in text.split(",") if part.strip()]

    if isinstance(value, Iterable):
        return [str(item) for item in value]

    return [str(value)]


def normalise_token(token: str) -> str:
    """Normalise a textual token for TF-IDF input."""
    token = token.lower().strip()
    token = token.replace("&", " and ")
    token = re.sub(r"[^a-z0-9]+", " ", token)
    return token.strip()


def build_document(row: pd.Series) -> str:
    """Create a combined document string for TF-IDF modelling."""
    fields = []
    for key in ("genres_list", "keywords_list"):
        terms = row.get(key, [])
        if isinstance(terms, list):
            fields.extend(normalise_token(term) for term in terms if term)

    for text_key in ("title", "overview"):
        text = row.get(text_key)
        if isinstance(text, str):
            fields.append(normalise_token(text))

    # Tokenise using alphanumeric chunks to improve signal-to-noise ratio
    tokens: List[str] = []
    for chunk in fields:
        if not chunk:
            continue
        tokens.extend(t.lower() for t in TOKEN_PATTERN.findall(chunk))

    return " ".join(tokens)


@dataclass
class ContentFeatures:
    tfidf_norm: float
    keyword_count: int
    genre_count: int
    overview_word_count: int
    overview_char_length: int
    title_char_length: int


def compute_content_features(df: pd.DataFrame, tfidf_vectorizer) -> pd.DataFrame:
    """Compute engineered features for each movie."""
    documents = df["document"].tolist()
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
    tfidf_norm = (tfidf_matrix.power(2).sum(axis=1)).A1 ** 0.5

    overview_text = df["overview"].fillna("").astype(str)
    title_text = df["title"].fillna("").astype(str)

    features = pd.DataFrame(
        {
            "tfidf_norm": tfidf_norm,
            "keyword_count": df["keywords_list"].apply(len),
            "genre_count": df["genres_list"].apply(len),
            "overview_word_count": overview_text.str.split().apply(len),
            "overview_char_length": overview_text.str.len(),
            "title_char_length": title_text.str.len(),
        }
    )

    return features


__all__ = [
    "ContentFeatures",
    "build_document",
    "compute_content_features",
    "load_movie_data",
    "normalise_token",
    "parse_iterable_from_cell",
]