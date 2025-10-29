#!/usr/bin/env python3
"""
重新绘制两张图（过滤 runtime > 500）：
- reports/figures/04_time_runtime_hist.png
- reports/figures/04_runtime_vs_age_scatter.png

脚本做的事：
 - 读取 data/raw/movies.xlsx（第一个 sheet）
 - 识别 runtime 列和 release_date（或 year）列
 - 对 runtime 应用启发式归一化（ms -> 分钟, 秒 -> 分钟）
 - 过滤 runtime <= 500 后绘图并保存
"""
import os
from pathlib import Path
import math
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]
RAW_XLSX = ROOT / 'data' / 'raw' / 'movies.xlsx'
OUT_DIR = ROOT / 'reports' / 'figures'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def find_column(cols, patterns):
    cols_low = [c.lower() for c in cols]
    for p in patterns:
        for i, c in enumerate(cols_low):
            if p in c:
                return cols[i]
    return None


def normalize_runtime_val(v):
    # v may be numeric or string. Return minutes (float) or np.nan
    if pd.isna(v):
        return np.nan
    try:
        fv = float(v)
    except Exception:
        # try to strip non-digits
        s = str(v).strip()
        s = ''.join(ch for ch in s if (ch.isdigit() or ch == '.' or ch == '-'))
        try:
            fv = float(s)
        except Exception:
            return np.nan

    # Heuristics based on observed data magnitudes
    # If extremely large, treat as milliseconds -> minutes
    if fv > 10000:  # e.g. 64,076,736 -> likely milliseconds
        return fv / 60000.0
    # If moderately large (>500), might be seconds -> minutes
    if fv > 500:
        return fv / 60.0
    # otherwise assume minutes
    return fv


def main():
    print('Reading', RAW_XLSX)
    if not RAW_XLSX.exists():
        raise SystemExit(f'Raw file not found: {RAW_XLSX}')

    # Read first sheet
    df = pd.read_excel(RAW_XLSX, sheet_name=0)
    print('Columns found:', list(df.columns)[:20])

    # Identify runtime column
    runtime_col = find_column(df.columns, ['runtime', 'run_time', 'duration', 'length'])
    if runtime_col is None:
        raise SystemExit('Cannot find runtime column (tried runtime/run_time/duration/length)')
    print('Using runtime column:', runtime_col)

    # Identify release date or year column
    date_col = find_column(df.columns, ['release_date', 'release', 'date', 'year'])
    print('Using date/year column (if any):', date_col)

    # Normalize runtime
    df['runtime_raw'] = df[runtime_col]
    df['runtime_min'] = df['runtime_raw'].apply(normalize_runtime_val)

    # Compute age in years if we have a date-like column
    now = datetime.now()
    if date_col is not None:
        try:
            dt = pd.to_datetime(df[date_col], errors='coerce')
            df['age_years'] = dt.dt.year.apply(lambda y: (now.year - int(y)) if not pd.isna(y) else np.nan)
        except Exception:
            df['age_years'] = np.nan
    else:
        df['age_years'] = np.nan

    # Filter for plotting: runtime <= 500 and runtime not null
    max_display = 500
    plot_df = df[df['runtime_min'].notna() & (df['runtime_min'] <= max_display)].copy()
    print(f'Total rows: {len(df)}, rows with runtime: {df["runtime_min"].notna().sum()}, rows after filtering <= {max_display}: {len(plot_df)}')

    # Histogram of runtime (minutes)
    hist_path = OUT_DIR / '04_time_runtime_hist.png'
    plt.figure(figsize=(8,5))
    plt.hist(plot_df['runtime_min'].dropna(), bins=40, color='#2b8cbe', edgecolor='black')
    plt.xlabel('Runtime (minutes)')
    plt.ylabel('Count')
    plt.title(f'Runtime distribution (<= {max_display} min)')
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(hist_path, dpi=150)
    plt.close()
    print('Saved histogram to', hist_path)

    # Scatter: runtime vs age
    scatter_path = OUT_DIR / '04_runtime_vs_age_scatter.png'
    # ensure age exists; if not, try to derive from a 'year' column directly
    if plot_df['age_years'].isna().all():
        # try to find a numeric year column
        year_col = find_column(df.columns, ['year'])
        if year_col is not None:
            try:
                plot_df['age_years'] = now.year - pd.to_numeric(df[year_col], errors='coerce')
            except Exception:
                plot_df['age_years'] = np.nan

    # sample for plotting if very large
    sample_df = plot_df.sample(n=min(len(plot_df), 5000), random_state=1) if len(plot_df) > 5000 else plot_df

    plt.figure(figsize=(7,6))
    plt.scatter(sample_df['age_years'], sample_df['runtime_min'], s=10, alpha=0.6, c='tab:orange', edgecolors='none')
    plt.xlabel('Age (years since release)')
    plt.ylabel('Runtime (minutes)')
    plt.title(f'Runtime vs Age (filtered <= {max_display} min)')
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(scatter_path, dpi=150)
    plt.close()
    print('Saved scatter to', scatter_path)


if __name__ == '__main__':
    main()
