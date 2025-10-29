"""
Inspect runtime field for anomalies and print diagnostics.
Writes reports/tables/04_runtime_outliers.csv with top outliers.
"""
import os
import pandas as pd
import numpy as np

p = 'data/raw/movies.xlsx'
df = pd.read_excel(p)
print('columns:', list(df.columns))
if 'runtime' not in df.columns:
    print('runtime column not found')
    raise SystemExit(1)

r = pd.to_numeric(df['runtime'], errors='coerce')
print('rows:', len(df))
print('runtime non-null:', r.notna().sum())
print('dtype:', r.dtype)
print(r.describe())

# counts beyond thresholds
thresholds = [60*24, 5000, 1000, 500]  # minutes: 1 day, 5000, 1000, 500 (use 500 as overlong)
for t in thresholds:
    print(f'> {t}:', (r > t).sum())

# show top 20 largest
out = df.assign(runtime_num=r).sort_values('runtime_num', ascending=False).head(50)
print('\nTop 50 by runtime (showing available columns):')
cols_show = []
for c in ['movie_id','id','title','name','runtime_num','release_date','release_date_parsed']:
    if c in out.columns:
        cols_show.append(c)
if not cols_show:
    cols_show = out.columns.tolist()[:6]
print(out[cols_show].to_string(index=False))

# write outliers CSV (runtime > 5000 minutes)
out_dir = 'reports/tables'
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, '04_runtime_outliers.csv')
sel = out[out['runtime_num']>5000]
if sel.empty:
    # also try >1000
    sel = df.assign(runtime_num=r).sort_values('runtime_num', ascending=False)
    sel = sel[sel['runtime_num']>1000]
sel_cols = [c for c in ['movie_id','id','title','name','runtime_num','release_date'] if c in sel.columns]
if sel.empty:
    print('\nNo outliers above threshold found to write.')
else:
    sel[sel_cols].to_csv(out_path, index=False, encoding='utf-8')
    print('\nWrote outliers to', out_path)
