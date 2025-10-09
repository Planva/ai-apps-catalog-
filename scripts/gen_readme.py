import pathlib, yaml, re
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "projects.yaml"
ICONS = ROOT / "assets" / "icons"
OUT = ROOT / "README.md"

def slugify(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()

with open(DATA, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

lines = []
lines.append("# 🧭 Awesome AI Apps Catalog\n")
lines.append("> 精选热门 AI 应用导航（点击图标直达官网）。数据源：`data/projects.yaml`，图标会自动抓取到 `assets/icons/`。\n")
lines.append("\n")

for cat in cfg["categories"]:
    lines.append(f"## {cat['title']}\n")
    row = []
    for item in cat["items"]:
        host = urlparse(item["website"]).netloc.replace("www.","")
        icon_candidates = sorted(ICONS.glob(f"{slugify(item['name'])}__*.png"))
        icon_rel = f"assets/icons/{icon_candidates[0].name}" if icon_candidates else None
        badge = f"<img src='{icon_rel}' width='36' height='36' style='vertical-align:middle;border-radius:8px'/>" if icon_rel else "🔗"
        label = item["name"]
        note = f"<br/><sub>{item.get('note','')}</sub>" if item.get("note") else ""
        row.append(f"<a href='{item['website']}' target='_blank'>{badge}&nbsp;{label}</a>{note}")
    for i in range(0, len(row), 3):
        chunk = row[i:i+3]
        while len(chunk) < 3:
            chunk.append("")
        lines.append("| " + " | ".join(chunk) + " |")
        lines.append("| :-- | :-- | :-- |")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("Wrote", OUT)