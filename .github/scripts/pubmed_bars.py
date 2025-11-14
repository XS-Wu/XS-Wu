# .github/scripts/pubmed_bars.py
import os
import collections
from pathlib import Path
from datetime import datetime

import feedparser
import matplotlib.pyplot as plt

# 用环境变量传入 PubMed RSS URL
RSS_URL = os.environ.get(
    "PUBMED_RSS_URL",
    "https://pubmed.ncbi.nlm.nih.gov/rss/search/1lyR11GsxK1bMA3jTm7Uhi20O_g2bcbLaEf-itlqG1dZLlVEGt/?limit=15&utm_campaign=pubmed-2&fc=20251114012738"
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

# ========== 一些通用的画图小函数 ==========

BAR_COLOR = "#4C72B0"  # 稍暗的蓝色，学术期刊常见风格

def style_axes(ax):
    """去掉上右边框，统一字体大小"""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", labelsize=9)

def add_bar_labels(ax, values):
    """在每个条形上方标出数值"""
    if not values:
        return
    max_val = max(values)
    offset = max_val * 0.05 if max_val > 0 else 0.3
    for i, v in enumerate(values):
        ax.text(
            i, v + offset, str(v),
            ha="center", va="bottom", fontsize=9
        )

# ========== 1) 按年份的条形图 ==========

years = sorted(year_counts.keys())
year_values = [year_counts[y] for y in years]

plt.figure(figsize=(6, 3))
ax = plt.gca()
ax.bar(range(len(years)), year_values, color=BAR_COLOR)
ax.set_xticks(range(len(years)))
ax.set_xticklabels(years)
ax.set_xlabel("Year", fontsize=10)
ax.set_ylabel("Number of publications in RSS", fontsize=10)
ax.set_title("Publications per year (PubMed RSS)", fontsize=11)
style_axes(ax)
add_bar_labels(ax, year_values)
plt.tight_layout()
year_path = out_dir / "pubmed_yearly_bar.png"
plt.savefig(year_path, dpi=200)
plt.close()
print(f"Saved yearly bar chart to {year_path}")

# ========== 2) 最近 12 个自然月的条形图 ==========

if month_counts:
    # 以当前月份为结束，向前数 11 个月，共 12 个自然月
    today = datetime.today()
    base_year = today.year
    base_month = today.month

    def add_months(year: int, month: int, delta: int):
        """year, month 加减 delta 个月（delta 可为负）"""
        total = year * 12 + (month - 1) + delta
        new_year = total // 12
        new_month = total % 12 + 1
        return new_year, new_month

    months_seq = [add_months(base_year, base_month, -11 + i) for i in range(12)]
    month_labels = [f"{y}-{m:02d}" for (y, m) in months_seq]
    month_values = [month_counts.get((y, m), 0) for (y, m) in months_seq]

    plt.figure(figsize=(7, 3))
    ax = plt.gca()
    ax.bar(range(len(months_seq)), month_values, color=BAR_COLOR)
    ax.set_xticks(range(len(months_seq)))
    ax.set_xticklabels(month_labels, rotation=45, ha="right")
    ax.set_xlabel("Month (last 12 calendar months)", fontsize=10)
    ax.set_ylabel("Number of publications in RSS", fontsize=10)
    ax.set_title("Publications per month (PubMed RSS)", fontsize=11)
    style_axes(ax)
    add_bar_labels(ax, month_values)
    plt.tight_layout()
    month_path = out_dir / "pubmed_monthly_bar.png"
    plt.savefig(month_path, dpi=200)
    plt.close()
    print(f"Saved monthly bar chart to {month_path}")
else:
    print("No entries with month information, skip monthly plot.")
