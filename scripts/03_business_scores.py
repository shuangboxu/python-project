# scripts/03_business.py
import json, re, math, numpy as np, pandas as pd
from pathlib import Path

# ====== 路径区（按你的项目结构，无需改）======
PROCESSED_FILE = Path("data/processed/movies_business.xlsx")  # 步骤一产物
RAW_FILE       = Path("data/raw/movies.xlsx")                 # 原始（只读）
OUT_DIR        = Path("reports/tables")
LOG_DIR        = Path("reports/logs")
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ====== 通用加载 ======
def read_any(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    suf = path.suffix.lower()
    if suf in [".xlsx", ".xls"]:
        xls = pd.ExcelFile(path)
        return xls.parse(xls.sheet_names[0])
    elif suf in [".csv", ".txt"]:
        return pd.read_csv(path)
    else:
        raise ValueError(f"暂不支持的格式: {suf}")


# ====== 公司解析与标准化 ======
def parse_companies(x):
    if pd.isna(x): return []
    if isinstance(x, list):
        return [str(v).strip() for v in x if str(v).strip()]
    s = str(x).strip()
    # 1) 尝试按 JSON 列表解析
    try:
        obj = json.loads(s)
        if isinstance(obj, list):
            out=[]
            for it in obj:
                if isinstance(it, dict) and "name" in it:
                    out.append(str(it["name"]).strip())
                elif isinstance(it, str):
                    out.append(it.strip())
            return [v for v in out if v]
    except Exception:
        pass
    # 2) 回退：逗号/分号切分
    return [v.strip() for v in re.split(r"[;,]", s) if v.strip()]

def normalize_name(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[()\-—–·.,&!?:;\"'`]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

KNOWN = {
    "disney","pixar","warner","wb","universal","paramount","sony","columbia",
    "fox","20th century","netflix","amazon","mgm","lionsgate","new line",
    "dreamworks","illumination"
}
def count_hits(names):
    if not isinstance(names, (list, tuple)):
        names = [str(names)] if pd.notna(names) else []
    names_n = [normalize_name(x) for x in names if str(x).strip()]
    return sum(any(k in n for n in names_n) for k in KNOWN)

# ====== 标准化工具 ======
def winsor_minmax(s: pd.Series, lo=0.01, hi=0.99):
    s = s.copy()
    if s.dropna().empty:
        return pd.Series(np.zeros(len(s)), index=s.index)
    ql, qh = s.quantile(lo), s.quantile(hi)
    s2 = s.clip(ql, qh)
    denom = (s2.max() - s2.min())
    if denom == 0 or pd.isna(denom):
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s2 - s2.min()) / (denom + 1e-9)

def main():
    # 1) 读“步骤一”产物
    df = read_any(PROCESSED_FILE).copy()
    if "movie_id" not in df.columns and "id" in df.columns:
        df = df.rename(columns={"id":"movie_id"})

    need_base = {"movie_id","title","budget","revenue"}
    missing_base = [c for c in need_base if c not in df.columns]
    if missing_base:
        raise ValueError(f"movies_business 缺失必要列: {missing_base}")

    # 若 production_companies 不在 movies_business，就去 RAW 里回填
    if "production_companies" not in df.columns:
        raw = read_any(RAW_FILE)
        if "movie_id" not in raw.columns and "id" in raw.columns:
            raw = raw.rename(columns={"id":"movie_id"})
        if "production_companies" not in raw.columns:
            raise ValueError("RAW 中也没有 production_companies，无法计算公司加成。")
        df = df.merge(
            raw[["movie_id","production_companies"]],
            on="movie_id", how="left"
        )

    # 2) 清洗
    df["budget"] = pd.to_numeric(df["budget"], errors="coerce")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    df["production_companies_parsed"] = df["production_companies"].apply(parse_companies)

    # 3) 原始指标
    eps = 1.0
    df["rev_raw"] = df["revenue"].clip(lower=0).apply(lambda x: math.log1p(x) if pd.notna(x) else np.nan)
    roi_ratio   = df["revenue"] / (df["budget"].where(df["budget"]>0, np.nan) + eps)
    df["roi_raw"] = roi_ratio.clip(lower=0).apply(lambda x: math.log1p(x) if pd.notna(x) else np.nan)

    # 4) 标准化到 [0,1]
    df["rev"] = winsor_minmax(df["rev_raw"])
    df["roi"] = winsor_minmax(df["roi_raw"])

    # 5) 公司加成
    df["studio_hits"] = df["production_companies_parsed"].apply(count_hits)
    df["studio"] = df["studio_hits"].apply(lambda k: 1.0 if k>=2 else (0.5 if k==1 else 0.0))

    # 6) 合成（缺失项权重归一）
    W = {"roi":0.50, "rev":0.35, "studio":0.15}
    def combine_row(row):
        vals, ws = [], []
        for k,w in W.items():
            v = row[k]
            if pd.notna(v):
                vals.append(v); ws.append(w)
        if not ws: return np.nan
        return sum(v*w for v,w in zip(vals,ws))/sum(ws)

    df["component_01"]   = df.apply(combine_row, axis=1)
    df["component_score"] = (100*df["component_01"]).clip(0,100).round(2)

    # 7) 输出三列表
    out = df[["movie_id","title","component_score"]].copy()
    out_path = OUT_DIR / "03_business_scores.csv"
    out.to_csv(out_path, index=False, encoding="utf-8-sig")

    # 8) 质量快检（可选但推荐）
    df.sort_values("component_score", ascending=False).head(20)[
        ["movie_id","title","budget","revenue","studio","roi","rev","component_score"]
    ].to_csv(OUT_DIR / "03_business_top20_preview.csv", index=False, encoding="utf-8-sig")
    df.sort_values("component_score", ascending=True).head(20)[
        ["movie_id","title","budget","revenue","studio","roi","rev","component_score"]
    ].to_csv(OUT_DIR / "03_business_bottom20_preview.csv", index=False, encoding="utf-8-sig")

    # 9) 简易日志
    LOG_DIR.joinpath("03_business_log.txt").write_text(
        "模块：03 Business（预算/票房/出品方）\n"
        "指标：ROI、Revenue（对数+分位裁剪+MinMax）、Studio（公司命中加成）\n"
        "合成：0.50*ROI + 0.35*Revenue + 0.15*Studio；缺失项权重归一\n"
        "输入：data/processed/movies_business.(xlsx/csv)，必要列 movie_id,title,budget,revenue(+production_companies)\n"
        "输出：reports/tables/03_business_scores.csv（三列）\n",
        encoding="utf-8"
    )

if __name__ == "__main__":
    main()
