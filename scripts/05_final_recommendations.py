"""Combine component scores into final recommendation rankings.

This script reads the component score tables generated in stage one,
normalizes each component, applies configurable weights, and exports the
final blended recommendation list. The default behavior prioritizes
content relevance followed by audience reception, business viability,
and timeliness.

Example
-------
python scripts/05_final_recommendations.py --top_n 20
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
TABLES_DIR = BASE_DIR / "reports" / "tables"
LOGS_DIR = BASE_DIR / "reports" / "logs"

INPUT_FILES = {
    "content": TABLES_DIR / "01_content_scores.csv",
    "rating": TABLES_DIR / "02_rating_scores.csv",
    "business": TABLES_DIR / "03_business_scores.csv",
    "time": TABLES_DIR / "04_time_scores.csv",
}

OUTPUT_FULL = TABLES_DIR / "05_final_scores.csv"
OUTPUT_TOP = TABLES_DIR / "05_top_recommendations.csv"
LOG_FILE = LOGS_DIR / "05_final_merge_log.txt"


def read_scores() -> Dict[str, pd.DataFrame]:
    """Read component score files and ensure the expected structure."""
    data_frames: Dict[str, pd.DataFrame] = {}
    for key, path in INPUT_FILES.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing component score file: {path}")
        df = pd.read_csv(path)
        expected_cols = {"movie_id", "title", "component_score"}
        missing = expected_cols.difference(df.columns)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"{path} is missing required columns: {missing_str}")
        df = df.dropna(subset=["movie_id"]).copy()
        df["movie_id"] = df["movie_id"].astype(str)
        data_frames[key] = df
    return data_frames


def normalize_series(series: pd.Series) -> pd.Series:
    """Min-max normalize a score column, guarding against constant series."""
    numeric = pd.to_numeric(series, errors="coerce")
    min_val = numeric.min()
    max_val = numeric.max()
    if pd.isna(min_val) or pd.isna(max_val):
        return pd.Series(0.0, index=series.index)
    if max_val - min_val == 0:
        return pd.Series(1.0, index=series.index)
    return (numeric - min_val) / (max_val - min_val)


def blend_scores(
    frames: Dict[str, pd.DataFrame],
    weights: Dict[str, float],
) -> pd.DataFrame:
    """Merge component scores and compute the weighted final score."""
    merged: pd.DataFrame | None = None
    for key, df in frames.items():
        score_col = f"{key}_score"
        norm_col = f"{key}_normalized"
        df = df[["movie_id", "title", "component_score"]].rename(
            columns={"component_score": score_col}
        )
        df[norm_col] = normalize_series(df[score_col])
        df = df[["movie_id", "title", score_col, norm_col]]
        if merged is None:
            merged = df
        else:
            merged = merged.merge(df, on=["movie_id", "title"], how="outer")
    assert merged is not None, "No frames to merge"

    for key in frames:
        norm_col = f"{key}_normalized"
        merged[norm_col] = merged[norm_col].fillna(0.0)

    weight_total = sum(weights.values())
    if weight_total <= 0:
        raise ValueError("Weights must sum to a positive value")
    normalized_weights = {k: v / weight_total for k, v in weights.items()}

    merged["final_score"] = 0.0
    for key, weight in normalized_weights.items():
        merged["final_score"] += merged[f"{key}_normalized"] * weight

    merged["final_score"] = merged["final_score"].round(6)
    merged = merged.sort_values("final_score", ascending=False)
    return merged


def export_results(df: pd.DataFrame, top_n: int) -> Tuple[Path, Path]:
    """Save the full ranking and the top-N subset to disk."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    df_full = df.copy()
    df_full.insert(0, "rank", range(1, len(df_full) + 1))
    df_full["final_score"] = (df_full["final_score"] * 100).round(2)
    df_full.to_csv(OUTPUT_FULL, index=False, encoding="utf-8-sig")

    top_df = df_full.head(top_n)
    top_df.to_csv(OUTPUT_TOP, index=False, encoding="utf-8-sig")
    return OUTPUT_FULL, OUTPUT_TOP


def write_log(weights: Dict[str, float], top_n: int) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    normalized_weights = {
        key: weight / sum(weights.values()) for key, weight in weights.items()
    }
    content = [
        f"[{timestamp} UTC] Stage-2 blending executed.",
        "Run command: python scripts/05_final_recommendations.py",
        f"Top-N exported: {top_n}",
        "Weights (after normalization):",
    ]
    for key, weight in normalized_weights.items():
        reason = {
            "content": "强调文本与标签匹配度以保持主题相关性",
            "rating": "利用用户评分与受欢迎度衡量口碑表现",
            "business": "考虑投资回报与头部制片厂影响力",
            "time": "兼顾上映时间、语言和时长的适配度",
        }.get(key, "")
        line = f"  - {key}: {weight:.2%} {reason}"
        content.append(line)

    LOG_FILE.write_text("\n".join(content) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--top_n",
        type=int,
        default=20,
        help="Number of recommendations to export in the top-N file (default: 20)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    weights = {
        "content": 0.4,
        "rating": 0.25,
        "business": 0.2,
        "time": 0.15,
    }

    frames = read_scores()
    blended = blend_scores(frames, weights)
    export_results(blended, args.top_n)
    write_log(weights, args.top_n)

    top_preview = blended.head(args.top_n).copy()
    top_preview["final_score"] = (top_preview["final_score"] * 100).round(2)
    print(top_preview[["movie_id", "title", "final_score"]].to_string(index=False))
    print(f"Full ranking: {OUTPUT_FULL}")
    print(f"Top-{args.top_n} ranking: {OUTPUT_TOP}")
    print(f"Log written to: {LOG_FILE}")


if __name__ == "__main__":
    main()
