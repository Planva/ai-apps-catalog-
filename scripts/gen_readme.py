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
lines.append("> AI apps directory / AI 应用导航：聊天、图片、视频、翻译、代码、语音、办公、搜索、智能体。点击图标直达官网。数据源：`data/projects.yaml`，图标自动抓取到 `assets/icons/`。\n")

for cat in cfg["categories"]:
    lines.append(f"\n## {cat['title']}\n")
    row = []
    for item in cat["items"]:
        label = item["name"]
        website = item["website"]
        icon_candidates = sorted(ICONS.glob(f"{slugify(label)}__*.png"))
        icon_rel = f"assets/icons/{icon_candidates[0].name}" if icon_candidates else None
        if icon_rel:
            badge = f"<img src='{icon_rel}' alt='{label} icon' width='36' height='36' style='vertical-align:middle;border-radius:8px'/>"
        else:
            badge = "🔗"
        note = f"<br/><sub>{item.get('note','')}</sub>" if item.get("note") else ""
        row.append(f"<a href='{website}' target='_blank' rel='noopener noreferrer'>{badge}&nbsp;{label}</a>{note}")

    for i in range(0, len(row), 3):
        chunk = row[i:i+3]
        while len(chunk) < 3:
            chunk.append("—")
        lines.append("| " + " | ".join(chunk) + " |")
        lines.append("| :-- | :-- | :-- |")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Wrote", OUT)
