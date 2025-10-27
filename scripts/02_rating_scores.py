import pandas as pd
import matplotlib.pyplot as plt
import os

# 自动定位项目根目录
base_dir = os.path.dirname(os.path.dirname(__file__))
data_path = os.path.join(base_dir, "data", "raw", "movies.xlsx")

# 1读取数据
df = pd.read_excel(data_path)

# 2提取并重命名列
cols = ["id", "title", "vote_average", "vote_count", "popularity"]
df = df[cols].rename(columns={"id": "movie_id"})

# 3转换为数值型并清理无效数据
for col in ["vote_average", "vote_count", "popularity"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["vote_average", "vote_count", "popularity"])

# 4标准化
for col in ["vote_average", "vote_count", "popularity"]:
    df[col + "_norm"] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# 5综合得分计算
df["component_score"] = (
    0.5 * df["vote_average_norm"]
    + 0.3 * df["vote_count_norm"]
    + 0.2 * df["popularity_norm"]
) * 100

# 6排序（从高到低）
df = df.sort_values(by="component_score", ascending=False)

# 7输出结果
output_dir = os.path.join(base_dir, "reports", "tables")
os.makedirs(output_dir, exist_ok=True)
out_path = os.path.join(output_dir, "02_rating_scores.csv")
df[["movie_id", "title", "component_score"]].to_csv(out_path, index=False)
print("已生成 02_rating_scores.csv（按得分从高到低排序）")


# 8 绘制图像
fig_dir = os.path.join(base_dir, "reports", "figures")
os.makedirs(fig_dir, exist_ok=True)

# 图 1：评分分布
plt.figure(figsize=(8, 5))
plt.hist(df["component_score"], bins=20, color="skyblue", edgecolor="black")
plt.title("Distribution of Rating & Popularity Scores")
plt.xlabel("Component Score")
plt.ylabel("Movie Count")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "02_rating_distribution.png"))
plt.close()

# 图 2：Top10 电影对比
top10 = df.nlargest(10, "component_score")[["title", "component_score"]]
plt.figure(figsize=(10, 6))
plt.barh(top10["title"], top10["component_score"], color="orange")
plt.xlabel("Component Score")
plt.title("Top 10 Movies by Rating & Popularity")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "02_rating_top10.png"))
plt.close()

print("已生成图像：")
print(" - reports/figures/02_rating_distribution.png")
print(" - reports/figures/02_rating_top10.png")
