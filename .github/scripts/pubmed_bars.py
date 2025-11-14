# .github/scripts/pubmed_bars.py
import os
import collections
from pathlib import Path
from datetime import datetime

import feedparser
import matplotlib.pyplot as plt

# PubMed RSS URL，从环境变量读取（没设置就用默认）
RSS_URL = os.environ.get(
    "PUBMED_RSS_URL",
    "https://pubmed.ncbi.nlm.nih.gov/rss/search/1TmjO1ifNewr3ZCXeKQ51L39DD88RQ2pLVl-AXtYCYAoQ3OQyZ/?limit=100&utm_campaign=pubmed-2&fc=20251114043805"
)

print(f"Fetching RSS from: {RSS_URL}")
feed = feedparser.parse(RSS_URL)

year_counts = collections.Counter()
month_counts = collections.Counter()  # key: (year, month)

for entry in feed.entries:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if not t:
        continue
    dt = datetime(t.tm_year, t.tm_mon, t.tm_mday)

    year_counts[dt.year] += 1
    month_counts[(dt.year, dt.month)] += 1

if not year_counts:
    print("No entries with year information, nothing to plot.")
    raise SystemExit(0)

out_dir = Path("assets")
out_dir.mkdir(parents=True, exist_ok=True)

# ---------- 通用画图小工具 ----------

# 五档颜色：灰、绿、蓝、浅红、深红
COLOR_0 = "#E5E5E5"   # 0 篇
COLOR_1 = "#b2df8a"   # 1–2 篇
COLOR_2 = "#a6cee3"   # 3–4 篇
COLOR_3 = "#fb9a99"   # 5–6 篇
COLOR_4 = "#e31a1c"   # ≥7 篇

def color_for_count(n: int) -> str:
    """根据篇数返回对应颜色。"""
    if n == 0:
        return COLOR_0
    elif n <= 2:
        return COLOR_1
    elif n <= 4:
        return COLOR_2
    elif n <= 6:
        return COLOR_3
    else:
        return COLOR_4

def style_axes(ax):
    """去掉上右边框，统一字体大小。"""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", labelsize=9)

def add_bar_labels(ax, values):
    """在每个条形上方标出数值（包括 0）。"""
    if not values:
        return
    max_val = max(values)
    offset = max_val * 0.05 if max_val > 0 else 0.3
    for i, v in enumerate(values):
        ax.text(
            i, v + offset, str(v),
            ha="center", va="bottom", fontsize=9
        )

# ---------- 1) 按年份的条形图 ----------

years = sorted(year_counts.keys())
year_values = [year_counts[y] for y in years]
year_colors = [color_for_count(v) for v in year_values]

plt.figure(figsize=(6, 3))
ax = plt.gca()
ax.bar(range(len(years)), year_values, color=year_colors, width=0.9)
ax.set_xticks(range(len(years)))
ax.set_xticklabels(years)
ax.set_xlabel("Year", fontsize=10)
ax.set_ylabel("Number of publications in RSS", fontsize=10)
ax.set_title("Publications per year (PubMed RSS)", fontsize=11)
style_axes(ax)

# 让顶部数字完全显示
ymax = max(year_values) if year_values else 0
ax.set_ylim(0, ymax * 1.25 + 0.5)
add_bar_labels(ax, year_values)

plt.tight_layout()
year_path = out_dir / "pubmed_yearly_bar.png"
plt.savefig(year_path, dpi=200)
plt.close()
print(f"Saved yearly bar chart to {year_path}")

# ---------- 2) 按自然月的条形图（全部月份） ----------

if month_counts:
    # 所有出现过的 (year, month)，找到最早和最晚的自然月
    keys_sorted = sorted(month_counts.keys())
    start_year, start_month = keys_sorted[0]
    end_year, end_month = keys_sorted[-1]

    def add_months(year: int, month: int, delta: int):
        """year, month 加减 delta 个月（delta 可为负）。"""
        total = year * 12 + (month - 1) + delta
        new_year = total // 12
        new_month = total % 12 + 1
        return new_year, new_month

    # 从起始自然月累加到结束自然月，中间每个月都画出来（没有文献就是 0）
    months_seq = []
    y, m = start_year, start_month
    while True:
        months_seq.append((y, m))
        if (y, m) == (end_year, end_month):
            break
        y, m = add_months(y, m, 1)

    month_labels = [f"{y}-{m:02d}" for (y, m) in months_seq]
    month_values = [month_counts.get((y, m), 0) for (y, m) in months_seq]
    month_colors = [color_for_count(v) for v in month_values]

    # 宽度调大一点，条之间间隙更小
    plt.figure(figsize=(max(7, len(months_seq) * 0.4), 3))
    ax = plt.gca()
    ax.bar(range(len(months_seq)), month_values, color=month_colors, width=0.9)
    ax.set_xticks(range(len(months_seq)))
    ax.set_xticklabels(month_labels, rotation=45, ha="right")
    ax.set_xlabel("Month", fontsize=10)
    ax.set_ylabel("Number of publications in RSS", fontsize=10)
    ax.set_title("Publications per month (PubMed RSS)", fontsize=11)
    style_axes(ax)

    ymax_m = max(month_values) if month_values else 0
    ax.set_ylim(0, ymax_m * 1.25 + 0.5)
    add_bar_labels(ax, month_values)

    plt.tight_layout()
    month_path = out_dir / "pubmed_monthly_bar.png"
    plt.savefig(month_path, dpi=200)
    plt.close()
    print(f"Saved monthly bar chart to {month_path}")
else:
    print("No entries with month information, skip monthly plot.")
