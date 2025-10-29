"""
04_release_geo.py

Time & Locale component (编号 04)

规范：脚本应在项目根目录运行并直接读取：
    df = pd.read_excel("data/raw/movies.xlsx")

输出：
    reports/tables/04_time_scores.csv (movie_id,title,component_score)
    reports/figures/04_time_runtime_hist.png （可选）

该脚本实现示例：新片优先（时间衰减）、语言匹配、时长适配度。
"""

import os
from datetime import datetime
import math

import ast
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


def english_name_for_lang(s: str) -> str:
    if not s:
        return 'unknown'
    orig = str(s).strip()
    key = orig.lower()

    # common ISO 639-1 mappings
    iso_map = {
        'en': 'English', 'fr': 'French', 'es': 'Spanish', 'de': 'German', 'it': 'Italian',
        'ru': 'Russian', 'ja': 'Japanese', 'zh': 'Chinese', 'pt': 'Portuguese', 'ar': 'Arabic',
        'pl': 'Polish', 'hi': 'Hindi', 'ko': 'Korean', 'tr': 'Turkish', 'nl': 'Dutch',
        'sv': 'Swedish', 'no': 'Norwegian', 'da': 'Danish', 'fi': 'Finnish', 'hu': 'Hungarian',
        'cs': 'Czech', 'el': 'Greek', 'he': 'Hebrew', 'vi': 'Vietnamese'
    }

    local_map = {
        'english': 'English', 'fran\u00e7ais': 'French', 'francais': 'French', 'espa\u00f1ol': 'Spanish',
        'espanol': 'Spanish', 'deutsch': 'German', 'italiano': 'Italian', 'русский': 'Russian',
        '日本語': 'Japanese', '中文': 'Chinese', '汉语': 'Chinese', '漢語': 'Chinese', 'portugu\u00eas': 'Portuguese',
        'العربية': 'Arabic', 'polski': 'Polish', 'हिन्दी': 'Hindi', 'हिंदी': 'Hindi', '한국어': 'Korean',
        'norsk': 'Norwegian', 'magyar': 'Hungarian', 'हिन्दी/': 'Hindi', 'हिन्दी/उर्दू': 'Hindi/Urdu'
    }

    # If looks like ISO code
    if len(key) <= 3 and key.isalpha():
        if key in iso_map:
            return iso_map[key]

    # direct match in local_map
    if key in local_map:
        return local_map[key]

    # contains a known token
    for k, v in local_map.items():
        if k in key:
            return v

    # fallback: if ASCII letters, title case it
    try:
        if all(ord(c) < 128 for c in key):
            return key.title()
    except Exception:
        pass

    # last resort
    return orig


def parse_spoken_languages(x):
    if pd.isna(x):
        return []
    if isinstance(x, list):
        out = []
        for v in x:
            if isinstance(v, dict):
                name = v.get('name') or v.get('iso_639_1')
                if name:
                    out.append(str(name).strip())
            else:
                out.append(str(v).strip())
        return [o.lower() for o in out if o]
    s = str(x).strip()
    if s.startswith('[') and s.endswith(']'):
        try:
            vals = ast.literal_eval(s)
            out = []
            for v in vals:
                if isinstance(v, dict):
                    name = v.get('name') or v.get('iso_639_1')
                    if name:
                        out.append(str(name).strip())
                else:
                    out.append(str(v).strip())
            return [o.lower() for o in out if o]
        except Exception:
            s = s[1:-1]
    if ',' in s:
        parts = [p.strip().lower() for p in s.split(',') if p.strip()]
        return parts
    return [s.lower()] if s else []


def compute_scores(df, target_lang='en', today=None):
    if today is None:
        today = pd.to_datetime(datetime.utcnow().date())

    rd = pd.to_datetime(df.get('release_date', None), errors='coerce')
    days = (today - rd).dt.days
    days = days.fillna(36500).clip(lower=0)
    tau = 365.0 * 2.0
    recency_raw = np.exp(-days / tau)
    recency = recency_raw

    def lang_score(row):
        orig = row.get('original_language', '')
        sl = parse_spoken_languages(row.get('spoken_languages', ''))
        target = str(target_lang).strip().lower()
        score = 0.0
        try:
            if isinstance(orig, str) and orig.strip().lower() == target:
                score = 1.0
            elif target in sl:
                score = 1.0
            else:
                score = 0.0
        except Exception:
            score = 0.0
        return score

    lang_scores = df.apply(lang_score, axis=1).astype(float)

    runtime = pd.to_numeric(df.get('runtime', None), errors='coerce').fillna(0)
    ideal = 110.0
    max_dev = 120.0
    dev = np.abs(runtime - ideal)
    runtime_score = (1.0 - (dev / max_dev)).clip(0.0, 1.0)

    w_recency = 0.5
    w_lang = 0.3
    w_runtime = 0.2

    combined = w_recency * recency + w_lang * lang_scores + w_runtime * runtime_score
    scaled = (combined * 100.0).clip(0.0, 100.0)
    return scaled, recency, lang_scores, runtime_score


def main():
    # 按规范直接读取原始数据文件（不要使用绝对个人路径）
    df = pd.read_excel("data/raw/movies.xlsx")

    if 'movie_id' not in df.columns:
        if 'id' in df.columns:
            df = df.rename(columns={'id': 'movie_id'})
        else:
            raise KeyError('movie_id column not found in data')
    if 'title' not in df.columns:
        raise KeyError('title column not found in data')

    scores, recency, lang_scores, runtime_score = compute_scores(df, target_lang='en')

    out_df = pd.DataFrame({
        'movie_id': df['movie_id'],
        'title': df['title'],
        'component_score': scores.round(2)
    })

    out_path = 'reports/tables/04_time_scores.csv'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    out_df.to_csv(out_path, index=False, encoding='utf-8')
    print(f'Wrote {out_path} ({len(out_df)} rows)')

    try:
        os.makedirs('reports/figures', exist_ok=True)

        # Try to pick a font that supports wide unicode glyphs (Chinese/Japanese/etc.)
        try:
            # prefer a prioritized list; matplotlib will resolve the first available
            preferred = ['Noto Sans', 'Noto Naskh Arabic', 'Noto Sans Devanagari', 'Microsoft YaHei', 'SimHei', 'Segoe UI', 'DejaVu Sans']
            available = {f.name for f in fm.fontManager.ttflist}
            # pick first available and set rcParams to the whole preferred list as fallback
            found = None
            for p in preferred:
                if p in available:
                    found = p
                    break
            matplotlib.rcParams['font.family'] = preferred
            print(f'Configured matplotlib font.family with fallbacks: {preferred} (found available: {found})')
        except Exception as _e:
            print('Could not auto-configure fonts for matplotlib:', _e)

        # ----- prepare derived columns -----
        df_local = df.copy()
        # runtime numeric
        df_local['runtime_num'] = pd.to_numeric(df_local.get('runtime', pd.Series([])), errors='coerce')
        # release_date -> year and recency days
        df_local['release_date_parsed'] = pd.to_datetime(df_local.get('release_date', None), errors='coerce')
        today = pd.to_datetime(datetime.utcnow().date())
        df_local['age_days'] = (today - df_local['release_date_parsed']).dt.days
        df_local['age_days'] = df_local['age_days'].where(df_local['age_days'].notna(), 36500).clip(lower=0)
        df_local['release_year'] = df_local['release_date_parsed'].dt.year

        # parse spoken languages into list
        df_local['spoken_langs_parsed'] = df_local.get('spoken_languages', '').apply(parse_spoken_languages)

        # language match flag
        target = 'en'
        def is_lang_match(row):
            orig = str(row.get('original_language', '')).strip().lower()
            sl = row.get('spoken_langs_parsed', [])
            if orig == target:
                return True
            if isinstance(sl, (list, tuple)) and target in sl:
                return True
            return False
        df_local['lang_match_target'] = df_local.apply(is_lang_match, axis=1)

        # ----- Figure 1: release year histogram -----
        try:
            plt.figure(figsize=(10, 4))
            years = df_local['release_year'].dropna().astype(int)
            if len(years) > 0:
                years.hist(bins=range(int(years.min()), int(years.max())+2), color='#4c72b0')
            plt.xlabel('release year')
            plt.ylabel('count')
            plt.title('Release year distribution')
            plt.tight_layout()
            p1 = 'reports/figures/04_release_year_hist.png'
            plt.savefig(p1, dpi=150)
            print(f'Wrote figure {p1}')
        except Exception as e:
            print('Could not create release year figure:', e)

        # ----- Figure 2: recency (age_days) histogram -----
        try:
            plt.figure(figsize=(8, 4))
            df_local['age_days'].replace(36500, np.nan).dropna().apply(lambda x: x/365.0).hist(bins=50, color='#55a868')
            plt.xlabel('age (years)')
            plt.ylabel('count')
            plt.title('Age distribution (years) — NaN/unknown excluded')
            plt.tight_layout()
            p2 = 'reports/figures/04_age_years_hist.png'
            plt.savefig(p2, dpi=150)
            print(f'Wrote figure {p2}')
        except Exception as e:
            print('Could not create age histogram:', e)

        # threshold for considering a runtime "overlong" (minutes)
        max_runtime_display = 500

        # ----- Figure 3: runtime histogram (zoomed) and outlier note -----
        try:
            runt = df_local['runtime_num']
            runt_nonan = runt.dropna()
            # count outliers beyond max_runtime_display minutes
            outliers = runt_nonan[runt_nonan > max_runtime_display]
            plt.figure(figsize=(8, 4))
            runt_nonan[runt_nonan <= max_runtime_display].hist(bins=40, color='#c44e52')
            plt.xlabel('runtime (minutes)')
            plt.ylabel('count')
            plt.title(f'Runtime distribution (<={max_runtime_display} min). outliers>{max_runtime_display}: {len(outliers)}')
            plt.tight_layout()
            p3 = 'reports/figures/04_runtime_hist_zoom.png'
            plt.savefig(p3, dpi=150)
            print(f'Wrote figure {p3}')
        except Exception as e:
            print('Could not create runtime histogram:', e)

        # ----- Figure 4: runtime boxplot (for values <= max_runtime_display) -----
        try:
            vals = df_local['runtime_num'].dropna()
            vals = vals[vals <= max_runtime_display]
            plt.figure(figsize=(6, 3))
            plt.boxplot(vals, vert=False)
            plt.xlabel('runtime (minutes)')
            plt.title(f'Runtime boxplot (<={max_runtime_display} min)')
            plt.tight_layout()
            p4 = 'reports/figures/04_runtime_boxplot.png'
            plt.savefig(p4, dpi=150)
            print(f'Wrote figure {p4}')
        except Exception as e:
            print('Could not create runtime boxplot:', e)

        # ----- Figure 5: runtime vs age scatter (sampled) -----
        try:
            # drop NA then filter out runtime outliers beyond max_runtime_display
            samp = df_local[['age_days', 'runtime_num']].dropna()
            samp = samp[samp['runtime_num'] <= max_runtime_display]
            # sample if too many points
            if len(samp) > 5000:
                samp = samp.sample(5000, random_state=1)
            plt.figure(figsize=(6, 5))
            plt.scatter(samp['age_days']/365.0, samp['runtime_num'], s=6, alpha=0.4)
            plt.xlabel('age (years)')
            plt.ylabel('runtime (minutes)')
            plt.title(f'Runtime vs Age (sampled, <= {max_runtime_display} min)')
            plt.tight_layout()
            p5 = 'reports/figures/04_runtime_vs_age_scatter.png'
            plt.savefig(p5, dpi=150)
            print(f'Wrote figure {p5} (plotted {len(samp)} points)')
        except Exception as e:
            print('Could not create runtime vs age scatter:', e)

        # ----- Figure 6/7: top languages (original and spoken) -----
        try:
            # original_language counts
            orig_counts = df_local['original_language'].fillna('')
            orig_counts = orig_counts[orig_counts != '']
            top_orig = orig_counts.value_counts().nlargest(15)
            plt.figure(figsize=(8, 4))
            top_orig.plot(kind='bar', color='#4c72b0')
            plt.xlabel('original_language')
            plt.ylabel('count')
            plt.title('Top original languages')
            plt.tight_layout()
            p6 = 'reports/figures/04_top_original_languages.png'
            plt.savefig(p6, dpi=150)
            print(f'Wrote figure {p6}')

            # spoken languages aggregated
            from collections import Counter
            c = Counter()
            for lst in df_local['spoken_langs_parsed']:
                if isinstance(lst, (list, tuple)):
                    for v in lst:
                        if v:
                            c[v] += 1
            top_spoken = pd.Series(dict(c)).sort_values(ascending=False).head(15)
            # map labels to English where appropriate to avoid missing glyphs
            mapped_labels = [english_name_for_lang(k) for k in top_spoken.index]
            top_spoken.index = mapped_labels
            plt.figure(figsize=(10, 4))
            ax = top_spoken.plot(kind='bar', color='#55a868')
            plt.xlabel('spoken_language')
            plt.ylabel('count')
            plt.title('Top spoken languages (aggregated)')
            # rotate x labels and align
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            p7 = 'reports/figures/04_top_spoken_languages.png'
            plt.savefig(p7, dpi=150)
            print(f'Wrote figure {p7}')
        except Exception as e:
            print('Could not create language top plots:', e)

        # ----- Figure 8: language match pie -----
        try:
            counts = df_local['lang_match_target'].value_counts()
            plt.figure(figsize=(5, 4))
            counts.plot(kind='pie', autopct='%1.1f%%', labels=['match' if x else 'no_match' for x in counts.index], colors=['#4c72b0', '#c44e52'])
            plt.ylabel('')
            plt.title(f'Language match to target={target}')
            plt.tight_layout()
            p8 = 'reports/figures/04_language_match_pie.png'
            plt.savefig(p8, dpi=150)
            print(f'Wrote figure {p8}')
        except Exception as e:
            print('Could not create language match pie:', e)

        # ----- Figure 9: missingness for key fields -----
        try:
            missing = pd.Series({
                'release_date_missing': df_local['release_date_parsed'].isna().mean(),
                'runtime_missing': df_local['runtime_num'].isna().mean(),
                'spoken_languages_missing': df_local['spoken_langs_parsed'].apply(lambda x: len(x)==0).mean(),
                'original_language_missing': df_local['original_language'].isna().mean()
            })
            plt.figure(figsize=(6, 3))
            (missing*100).plot(kind='bar', color='#8172b2')
            plt.ylabel('percent missing')
            plt.title('Missingness (%)')
            plt.tight_layout()
            p9 = 'reports/figures/04_missingness.png'
            plt.savefig(p9, dpi=150)
            print(f'Wrote figure {p9}')
        except Exception as e:
            print('Could not create missingness plot:', e)

        # ----- Data quality CSV -----
        try:
            diag = {
                'n_rows': len(df_local),
                'runtime_mean': float(df_local['runtime_num'].dropna().mean()) if df_local['runtime_num'].dropna().size>0 else None,
                'runtime_median': float(df_local['runtime_num'].dropna().median()) if df_local['runtime_num'].dropna().size>0 else None,
                'runtime_90pct': float(df_local['runtime_num'].dropna().quantile(0.9)) if df_local['runtime_num'].dropna().size>0 else None,
                'release_date_missing_pct': float(df_local['release_date_parsed'].isna().mean())*100,
                'runtime_missing_pct': float(df_local['runtime_num'].isna().mean())*100,
                'spoken_languages_missing_pct': float(df_local['spoken_langs_parsed'].apply(lambda x: len(x)==0).mean())*100,
                'original_language_missing_pct': float(df_local['original_language'].isna().mean())*100,
                'lang_match_pct': float(df_local['lang_match_target'].mean())*100
            }
            diag_df = pd.DataFrame([diag])
            qpath = 'reports/tables/04_time_data_quality.csv'
            os.makedirs(os.path.dirname(qpath), exist_ok=True)
            diag_df.to_csv(qpath, index=False, encoding='utf-8')
            print(f'Wrote diagnostics {qpath}')
        except Exception as e:
            print('Could not write diagnostics CSV:', e)
    except Exception as e:
        print('Could not create figure:', e)


if __name__ == '__main__':
    main()
