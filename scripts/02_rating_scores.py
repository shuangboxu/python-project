import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime

# 自动定位项目根目录与文件路径
base_dir = os.path.dirname(os.path.dirname(__file__))
data_path = os.path.join(base_dir, "data", "raw", "movies.xlsx")
table_dir = os.path.join(base_dir, "reports", "tables")
fig_dir = os.path.join(base_dir, "reports", "figures")
log_path = os.path.join(base_dir, "reports", "log.txt")

# 创建目录
os.makedirs(table_dir, exist_ok=True)
os.makedirs(fig_dir, exist_ok=True)

# 简单日志记录函数
def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

# 文件检查
if not os.path.exists(data_path):
    write_log(f"文件不存在: {data_path}")
    raise FileNotFoundError(f"找不到数据文件: {data_path}")

# 数据读取
try:
    df = pd.read_excel(data_path)
except Exception as e:
    write_log(f"读取数据失败: {e}")
    raise

# 提取并重命名列
expected_cols = ["id", "title", "vote_average", "vote_count", "popularity"]
missing = [c for c in expected_cols if c not in df.columns]
if missing:
    write_log(f"缺失列: {missing}")
    raise ValueError(f"数据列缺失: {missing}")

df = df[expected_cols].rename(columns={"id": "movie_id"})

# 数据清理与类型转换
for col in ["vote_average", "vote_count", "popularity"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["vote_average", "vote_count", "popularity"])
write_log(f"清洗后剩余 {len(df)} 条有效数据。")

# 标准化处理
for col in ["vote_average", "vote_count", "popularity"]:
    df[col + "_norm"] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# 计算权重与综合得分
w_vote, w_count, w_pop = 0.5, 0.3, 0.2
df["component_score"] = (
    w_vote * df["vote_average_norm"]
    + w_count * df["vote_count_norm"]
    + w_pop * df["popularity_norm"]
) * 100

# 排序
df = df.sort_values(by="component_score", ascending=False)

# 保存主要得分结果
score_path = os.path.join(table_dir, "02_rating_scores.csv")
try:
    df[["movie_id", "title", "component_score"]].to_csv(score_path, index=False)
    write_log("保存综合得分表成功。")
except Exception as e:
    write_log(f"保存得分表失败: {e}")

# 绘制得分分布图
try:
    plt.figure(figsize=(8, 5))
    plt.hist(df["component_score"], bins=20, color="skyblue", edgecolor="black")
    plt.title("Distribution of Rating & Popularity Scores")
    plt.xlabel("Component Score")
    plt.ylabel("Movie Count")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "02_rating_distribution.png"))
    plt.close()
except Exception as e:
    write_log(f"绘制得分分布图失败: {e}")

# 绘制Top10条形图
top10 = df.nlargest(10, "component_score")[["title", "component_score"]]
try:
    plt.figure(figsize=(10, 6))
    plt.barh(top10["title"], top10["component_score"], color="orange")
    plt.xlabel("Component Score")
    plt.title("Top 10 Movies by Rating & Popularity")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "02_rating_top10.png"))
    plt.close()
except Exception as e:
    write_log(f"绘制Top10图失败: {e}")

# 得分区间统计表
bins = np.arange(0, 110, 10)
labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]
df["score_bin"] = pd.cut(df["component_score"], bins=bins, labels=labels, include_lowest=True)
dist_table = df["score_bin"].value_counts().sort_index().reset_index()
dist_table.columns = ["Score Range", "Movie Count"]
dist_out_path = os.path.join(table_dir, "02_rating_distribution_table.csv")
dist_table.to_csv(dist_out_path, index=False)

# 评分与受欢迎度散点图
try:
    plt.figure(figsize=(8, 6))
    plt.scatter(df["vote_average"], df["popularity"], alpha=0.6, edgecolors='k')
    plt.title("Vote Average vs Popularity")
    plt.xlabel("Vote Average")
    plt.ylabel("Popularity")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "02_rating_scatter.png"))
    plt.close()
except Exception as e:
    write_log(f"绘制散点图失败: {e}")

# 统计信息表输出（均值、中位数等）
desc = df["component_score"].describe().reset_index()
desc.columns = ["Metric", "Value"]
stats_out = os.path.join(table_dir, "02_rating_summary_stats.csv")
desc.to_csv(stats_out, index=False)



# 保存Top10摘要表（带排名）
top10["Rank"] = range(1, len(top10) + 1)
top10_out = os.path.join(table_dir, "02_rating_top10_table.csv")
top10[["Rank", "title", "component_score"]].to_csv(top10_out, index=False)



# 程序总结输出
print("文件已生成：")
print(" - reports/tables/02_rating_scores.csv")
print(" - reports/tables/02_rating_distribution_table.csv")
print(" - reports/tables/02_rating_summary_stats.csv")
print(" - reports/tables/02_rating_top10_table.csv")
print(" - reports/figures/02_rating_distribution.png")
print(" - reports/figures/02_rating_top10.png")
print(" - reports/figures/02_rating_scatter.png")
print("日志文件: reports/log.txt")
