# .github/scripts/pubmed_bars.py
import os
import collections
from pathlib import Path
from datetime import datetime

import feedparser
import matplotlib.pyplot as plt

# 用环境变量传入 PubMed RSS URL，没设就用默认这个
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
    # 转成 datetime，方便后面处理
    dt = datetime(t.tm_year, t.tm_mon, t.tm_mday)

    year_counts[dt.year] += 1
    month_counts[(dt.year, dt.month)] += 1

if not year_counts:
    print("No entries with year information, nothing to plot.")
    raise SystemExit(0)

out_dir = Path("assets")
out_dir.mkdir(parents=True, exist_ok=True)

# -------- 1) 按年份的条形图 --------
years = sorted(year_counts.keys())
year_values = [year_counts[y] for y in years]

plt.figure(figsize=(6, 3))
plt.bar(range(len(years)), year_values)
plt.xticks(range(len(years)), years)
plt.xlabel("Year")
plt.ylabel("Number of publications in RSS")
plt.title("Publications per year (PubMed RSS)")
plt.tight_layout()
year_path = out_dir / "pubmed_yearly_bar.png"
plt.savefig(year_path, dpi=200)
plt.close()
print(f"Saved yearly bar chart to {year_path}")

# -------- 2) 最近 12 个月按月份的条形图 --------
if month_counts:
    # 按 (year, month) 排序
    all_months = sorted(month_counts.keys())
    # 只取最后 12 个月（如果不足 12 个就全用）
    if len(all_months) > 12:
        all_months = all_months[-12:]

    month_labels = [f"{y}-{m:02d}" for (y, m) in all_months]
    month_values = [month_counts[(y, m)] for (y, m) in all_months]

    plt.figure(figsize=(7, 3))
    plt.bar(range(len(all_months)), month_values)
    plt.xticks(range(len(all_months)), month_labels, rotation=45, ha="right")
    plt.xlabel("Month (last 12 months in RSS)")
    plt.ylabel("Number of publications in RSS")
    plt.title("Publications per month (PubMed RSS)")
    plt.tight_layout()
    month_path = out_dir / "pubmed_monthly_bar.png"
    plt.savefig(month_path, dpi=200)
    plt.close()
    print(f"Saved monthly bar chart to {month_path}")
else:
    print("No entries with month information, skip monthly plot.")
