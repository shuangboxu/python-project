# Final Project — Movie Recommendation System
---

## 1) What this project delivers
- **Final ranked recommendations** (CSV): `reports/tables/05_final_scores.csv` and `reports/tables/05_top_recommendations.csv` (Top‑N).
- **Reproducible logs**: component and merge logs under `reports/logs/`.
- **Figures & tables**: diagnostics and summary artifacts under `reports/figures/` and `reports/tables/`.
- **A simple web app** to browse the results: open `app/index.html` via a local server.

**Components (Stage‑1)**  
1) `content` — content completeness & topical relevance.  
2) `rating` — audience reception (vote average/count, popularity).  
3) `business` — ROI & studio signals.  
4) `time` — recency, language match, runtime fitness.

**Blending (Stage‑2)**  
The four normalized components are merged with default weights:  
`content=0.25, rating=0.40, business=0.20, time=0.15` (configurable).

**Presentation (Stage‑3)**  
A static site in `app/` loads the generated recommendation JSON and provides filtering by age/language and keyword search.

---

## 2) Environment & data
- **Python**: 3.12+
- **Install dependencies**:  
  ```bash
  python -m pip install -r requirements.txt
  ```
- **Input data**: place the provided dataset at `data/raw/movies.xlsx` (first sheet).

> Tip (Windows fonts for plots): if non‑Latin labels render as boxes, see `scripts/download_and_install_noto.ps1` to install Noto fonts locally, then re‑run plotting scripts.

---

## 3) Reproduce Stage‑1 component scores
> Run from the project root.

### 3.1 Content (01)
```bash
python scripts/01_content_scores.py
```
**Outputs**
- `reports/tables/01_content_scores.csv`
- Figures under `reports/figures/` (distribution, genre profiles, word cloud)
- Log: `reports/logs/01_content_log.txt`

### 3.2 Rating & Popularity (02)
```bash
python scripts/02_rating_scores.py
```
**Outputs**
- `reports/tables/02_rating_scores.csv`
- Figures under `reports/figures/` (distribution, scatter, top‑10)
- Log: `reports/log.txt`

### 3.3 Business (03)
```bash
python scripts/03_business_scores.py
```
**Outputs**
- `reports/tables/03_business_scores.csv`
- Preview tables: `reports/tables/03_business_top20_preview.csv` / `..._bottom20_preview.csv`
- Log: `reports/logs/03_business_log.txt`

### 3.4 Time & Locale (04)
```bash
python scripts/04_release_geo.py
```
**Outputs**
- `reports/tables/04_time_scores.csv`
- Diagnostics: `reports/tables/04_time_data_quality.csv`
- Figures under `reports/figures/` (release years, age, runtime, language match, missingness)
- Log: `reports/logs/04_timelanguage_log.txt`

---

## 4) Merge & export final rankings (Stage‑2)
```bash
# default top N = 20; override with --top_n
python scripts/05_final_recommendations.py --top_n 20
```
**Outputs**
- Full ranking: `reports/tables/05_final_scores.csv`
- Top‑N: `reports/tables/05_top_recommendations.csv`
- Log: `reports/logs/05_final_merge_log.txt` (records the normalized weights and command)

---

## 5) Build data for the web app (Stage‑3)
```bash
python scripts/generate_recommendation_dataset.py
```
**Outputs**
- `reports/logs/recommendation_data.json` (movies + metadata for the UI)

---

## 6) Launch the web app
Because modern browsers restrict `file://` fetches, serve the repo root locally and open the app page:

```bash
# from repository root
python -m http.server 8000
# then visit
#   http://localhost:8000/app/          (directory index)
#   http://localhost:8000/app/index.html (direct page)
```

The app (`app/index.html`, `app/app.js`, `app/styles.css`) will automatically load `reports/logs/recommendation_data.json` and render paginated, filterable cards for the top‑ranked movies.

---

## 7) What to grade
- **Reproducibility**: rerun 3–5 scripts above and verify matching tables/logs.
- **Data quality & analysis**: check `reports/tables/04_time_data_quality.csv` and figures in `reports/figures/`.
- **Final results**: confirm `05_final_scores.csv` is sorted by `final_score` and matches `05_top_recommendations.csv` top‑N.
- **Presentation**: open the app and validate language/age filters, search, and metadata display.

---

## 8) File map (key artifacts)
```
data/
  raw/movies.xlsx
reports/
  figures/                    # all diagnostic and summary plots
  logs/
    01_content_log.txt
    03_business_log.txt
    04_timelanguage_log.txt
    05_final_merge_log.txt
    recommendation_data.json  # dataset used by the web app
  tables/
    01_content_scores.csv
    02_rating_scores.csv
    03_business_scores.csv
    04_time_data_quality.csv
    04_time_scores.csv
    05_final_scores.csv
    05_top_recommendations.csv
app/
  index.html
  app.js
  styles.css
scripts/
  01_content_scores.py
  02_rating_scores.py
  03_business_scores.py
  04_release_geo.py
  05_final_recommendations.py
  generate_recommendation_dataset.py
  download_and_install_noto.ps1
```

---

## 9) Notes
- All scripts read/write **relative paths** from the repo root—no machine‑specific paths.  
- If any component table is missing, the merge step will raise a clear error indicating which file to generate.

---

# 电影推荐系统 — 课程大作业
---

## 1）成果清单
- **最终排序结果（CSV）**：`reports/tables/05_final_scores.csv` 与 `reports/tables/05_top_recommendations.csv`（Top‑N）。
- **可复现实验日志**：位于 `reports/logs/` 的组件与合并日志。
- **图表与表格**：位于 `reports/figures/`、`reports/tables/` 的诊断与汇总产物。
- **浏览型网页**：在本地服务器下打开 `app/index.html` 进行交互式查看。

**组件（第一阶段）**  
1）内容（content）评分：内容完备度与主题相关性。  
2）口碑（rating）评分：评分均值/票数/热度。  
3）商业（business）评分：投入产出与头部制片厂命中。  
4）时间（time）评分：新鲜度、语言匹配、时长适配。

**融合（第二阶段）**  
四个标准化分数按默认权重融合：`content=0.25, rating=0.40, business=0.20, time=0.15`（可调整）。

**展示（第三阶段）**  
`app/` 为静态网页，加载生成的 JSON 数据，支持按年龄/语言、关键词筛选。

---

## 2）环境与数据
- **Python**：3.12+  
- **依赖安装**：
  ```bash
  python -m pip install -r requirements.txt
  ```
- **输入数据**：将课程数据放置到 `data/raw/movies.xlsx`（第 1 个工作表）。

> **提示（Windows 字体）**：如中文/多语言标签在图表显示为方框，可运行 `scripts/download_and_install_noto.ps1` 安装 Noto 字体后重跑绘图脚本。

---

## 3）复现第一阶段（组件分数）
> 所有命令在**项目根目录**执行。

### 3.1 内容（01）
```bash
python scripts/01_content_scores.py
```
**输出**
- `reports/tables/01_content_scores.csv`
- 图表位于 `reports/figures/`（分布、类型对比、词云等）
- 日志：`reports/logs/01_content_log.txt`

### 3.2 口碑（02）
```bash
python scripts/02_rating_scores.py
```
**输出**
- `reports/tables/02_rating_scores.csv`
- 图表位于 `reports/figures/`（分布、散点、Top‑10）
- 日志：`reports/log.txt`

### 3.3 商业（03）
```bash
python scripts/03_business_scores.py
```
**输出**
- `reports/tables/03_business_scores.csv`
- 预览表：`reports/tables/03_business_top20_preview.csv` / `..._bottom20_preview.csv`
- 日志：`reports/logs/03_business_log.txt`

### 3.4 时间与语言（04）
```bash
python scripts/04_release_geo.py
```
**输出**
- `reports/tables/04_time_scores.csv`
- 质量诊断：`reports/tables/04_time_data_quality.csv`
- 图表位于 `reports/figures/`（年份、年龄、时长、语言命中、缺失率）
- 日志：`reports/logs/04_timelanguage_log.txt`

---

## 4）融合与导出（第二阶段）
```bash
# 默认导出 Top-20，可用 --top_n 调整
python scripts/05_final_recommendations.py --top_n 20
```
**输出**
- 全量排序：`reports/tables/05_final_scores.csv`
- Top‑N：`reports/tables/05_top_recommendations.csv`
- 日志：`reports/logs/05_final_merge_log.txt`（记录权重与运行命令）

---

## 5）为网页生成数据（第三阶段）
```bash
python scripts/generate_recommendation_dataset.py
```
**输出**
- `reports/logs/recommendation_data.json`（网页所需的电影与元数据）

---

## 6）本地启动网页
现代浏览器默认限制 `file://` 的跨域读取，建议用本地服务器打开：
```bash
# 在项目根目录
python -m http.server 8000
# 打开
#   http://localhost:8000/app/
#   http://localhost:8000/app/index.html
```
网页（`app/index.html`, `app/app.js`, `app/styles.css`）会自动读取 `reports/logs/recommendation_data.json` 并分页渲染卡片，支持筛选与搜索。

---

## 7）评分要点
- **可复现性**：按上文命令重跑 3–5 个脚本，检查产物与日志一致性。  
- **数据质量与分析**：查看 `reports/tables/04_time_data_quality.csv` 与 `reports/figures/` 图表。  
- **最终结果**：确认 `05_final_scores.csv` 以 `final_score` 降序排列，并与 `05_top_recommendations.csv` 的 Top‑N 对齐。  
- **展示效果**：网页过滤与检索是否生效，字段展示是否完整。

---

## 8）文件结构（关键产物）
```
data/
  raw/movies.xlsx
reports/
  figures/
  logs/
    01_content_log.txt
    03_business_log.txt
    04_timelanguage_log.txt
    05_final_merge_log.txt
    recommendation_data.json
  tables/
    01_content_scores.csv
    02_rating_scores.csv
    03_business_scores.csv
    04_time_data_quality.csv
    04_time_scores.csv
    05_final_scores.csv
    05_top_recommendations.csv
app/
  index.html
  app.js
  styles.css
scripts/
  01_content_scores.py
  02_rating_scores.py
  03_business_scores.py
  04_release_geo.py
  05_final_recommendations.py
  generate_recommendation_dataset.py
  download_and_install_noto.ps1
```

---

## 9）附注
- 所有脚本统一使用**相对路径**；如缺某组件表，融合脚本会明确报出缺失文件名并中止。
