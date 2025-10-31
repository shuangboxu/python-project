"""Generate a JSON dataset for the movie recommendation web app.

This script merges the final recommendation scores with the raw movie metadata
and serialises a compact JSON file that can be consumed directly by the front
end.  It also creates a summary of the available languages to power the
language selector on the site.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL_SCORES_PATH = PROJECT_ROOT / "reports" / "tables" / "05_final_scores.csv"
RAW_MOVIES_PATH = PROJECT_ROOT / "data" / "raw" / "movies.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "reports" / "logs" / "recommendation_data.json"

# Genres that are typically unsuitable for minors.
AGE_RESTRICTED_GENRES = {
    "Horror",
    "Thriller",
    "Crime",
    "War",
    "Mystery",
}

LANGUAGE_CODE_MAP = {
    "AF": "Afrikaans",
    "AR": "Arabic",
    "CN": "Chinese",
    "CS": "Czech",
    "DA": "Danish",
    "DE": "German",
    "EL": "Greek",
    "EN": "English",
    "ES": "Spanish",
    "FA": "Persian",
    "FI": "Finnish",
    "FR": "French",
    "HE": "Hebrew",
    "HI": "Hindi",
    "HU": "Hungarian",
    "ID": "Indonesian",
    "IS": "Icelandic",
    "IT": "Italian",
    "JA": "Japanese",
    "KO": "Korean",
    "KY": "Kyrgyz",
    "NB": "Norwegian Bokmål",
    "NL": "Dutch",
    "NO": "Norwegian",
    "PS": "Pashto",
    "PL": "Polish",
    "PT": "Portuguese",
    "RO": "Romanian",
    "RU": "Russian",
    "SL": "Slovenian",
    "SV": "Swedish",
    "TA": "Tamil",
    "TE": "Telugu",
    "TH": "Thai",
    "TR": "Turkish",
    "VI": "Vietnamese",
    "XX": "Unknown",
    "ZH": "Chinese",
}


def _parse_json_column(value: Any) -> list[dict[str, Any]]:
    """Safely parse JSON-like strings stored in the dataset."""

    if isinstance(value, float) and pd.isna(value):
        return []
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return []


def _extract_names(items: list[dict[str, Any]], key: str = "name") -> list[str]:
    return [str(item.get(key, "")).strip() for item in items if key in item and item.get(key)]


def _clean_language_name(value: str) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    lowered = cleaned.lower()
    blocked_terms = (
        "company",
        "studio",
        "pictures",
        "films",
        "entertainment",
        "partners",
        "network",
        "office",
        "television",
        "media",
        "production",
        "productions",
        "disney",
        "lawson",
        "mitsubishi",
        "vivendi",
        "film",
    )
    if any(blocker in lowered for blocker in blocked_terms):
        return None
    if cleaned.replace(" ", "").isdigit():
        return None
    cleaned = cleaned.title()
    return cleaned


def _safe_float(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    final_scores = pd.read_csv(FINAL_SCORES_PATH, encoding="utf-8-sig")
    raw_movies = pd.read_excel(RAW_MOVIES_PATH)

    merged = final_scores.merge(raw_movies, left_on="movie_id", right_on="id", how="left")

    movies: list[dict[str, Any]] = []
    languages_lookup: dict[str, str] = {}

    for _, row in merged.iterrows():
        genres = _extract_names(_parse_json_column(row.get("genres", "")))
        keywords = _extract_names(_parse_json_column(row.get("keywords", "")))
        raw_spoken_languages = _extract_names(
            _parse_json_column(row.get("spoken_languages", "")), key="name"
        )
        spoken_languages = [
            language
            for language in (
                _clean_language_name(language) for language in raw_spoken_languages
            )
            if language
        ]
        # Preserve insertion order while deduplicating.
        spoken_languages = list(dict.fromkeys(spoken_languages))
        language_code = str(row.get("original_language", "")).upper()
        language_label = LANGUAGE_CODE_MAP.get(language_code, language_code)
        if language_code:
            languages_lookup.setdefault(language_code, language_label)

        homepage = row.get("homepage")
        if not isinstance(homepage, str) or not homepage.strip():
            homepage = f"https://www.themoviedb.org/movie/{int(row['movie_id'])}"

        release_date = row.get("release_date")
        if hasattr(release_date, "date"):
            release_date_str = release_date.date().isoformat()
        elif isinstance(release_date, str):
            release_date_str = release_date.split(" ")[0]
        else:
            release_date_str = ""

        movies.append(
            {
                "rank": int(row["rank"]),
                "movie_id": int(row["movie_id"]),
                "title": row.get("title_x") or row.get("title"),
                "overview": row.get("overview", ""),
                "genres": genres,
                "keywords": keywords,
                "spoken_languages": spoken_languages,
                "language_code": language_code,
                "language_label": language_label,
                "release_date": release_date_str,
                "runtime": _safe_int(row.get("runtime")),
                "vote_average": _safe_float(row.get("vote_average")),
                "vote_count": _safe_int(row.get("vote_count")),
                "final_score": float(row["final_score"]),
                "homepage": homepage,
                "is_restricted_for_minors": any(
                    genre in AGE_RESTRICTED_GENRES for genre in genres
                ),
            }
        )

    movies.sort(key=lambda item: item["rank"])

    language_options = [
        {"code": code, "label": label}
        for code, label in sorted(languages_lookup.items(), key=lambda item: item[1])
    ]

    output = {
        "metadata": {
            "total_movies": len(movies),
            "age_restricted_genres": sorted(AGE_RESTRICTED_GENRES),
            "languages": language_options,
        },
        "movies": movies,
    }

    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
