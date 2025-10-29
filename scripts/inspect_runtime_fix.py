"""
Show runtime values after heuristic normalization:
- if runtime > 10000 -> assume milliseconds -> minutes = runtime / 60000
- elif runtime > 1000 -> assume seconds -> minutes = runtime / 60
- else -> minutes = runtime
Print some stats and top few values after normalization.
"""
import pandas as pd
import numpy as np

df = pd.read_excel('data/raw/movies.xlsx')
r = pd.to_numeric(df['runtime'], errors='coerce')

def to_minutes(x):
    if pd.isna(x):
        return x
    try:
        xv = float(x)
    except Exception:
        return np.nan
    if xv > 10000:
        return xv / 60000.0
    elif xv > 1000:
        return xv / 60.0
    else:
        return xv

mins = r.apply(to_minutes)
print('before: count, mean, median, max ->', r.count(), r.mean(), r.median(), r.max())
print('after : count, mean, median, max ->', mins.count(), mins.mean(), mins.median(), mins.max())
print('\nTop 10 after normalization:')
out = df.assign(runtime_minutes=mins).sort_values('runtime_minutes', ascending=False).head(20)
print(out[['id','title','runtime','runtime_minutes']].to_string(index=False))
