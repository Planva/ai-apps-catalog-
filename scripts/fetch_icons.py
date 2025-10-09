import os, re, io, pathlib, time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from PIL import Image
try:
    import cairosvg  # for SVG -> PNG if available
except Exception:
    cairosvg = None
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "projects.yaml"
OUT = ROOT / "assets" / "icons"
OUT.mkdir(parents=True, exist_ok=True)

def load_projects():
    with open(DATA, "r", encoding="utf-8") as f:
        d = yaml.safe_load(f)
    for cat in d["categories"]:
        for item in cat["items"]:
            yield cat["id"], item["name"], item["website"]
    return []

def fetch_bytes(url, timeout=15):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AI-Apps-Catalog/1.0)"}
    r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return r.content, r.headers.get("Content-Type", "")

def best_icon_from_html(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    rel_keys = ["apple-touch-icon", "apple-touch-icon-precomposed", "mask-icon", "icon", "shortcut icon"]
    hrefs = []
    for link in soup.find_all("link"):
        rel = " ".join(link.get("rel", [])).lower()
        if any(k in rel for k in rel_keys) and link.get("href"):
            hrefs.append(link["href"])
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        hrefs.append(og["content"])
    for h in hrefs:
        yield urljoin(base_url, h)

def url_to_filename(name, website):
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    host = urlparse(website).netloc.replace("www.", "")
    return f"{slug}__{host}.png"

def save_png(img_bytes, ctype, out_path, size=256):
    if "svg" in ctype or out_path.suffix.lower() == ".svg":
        if cairosvg is None:
            return False
        import io as _io
        png_bytes = cairosvg.svg2png(bytestring=img_bytes)
        img = Image.open(_io.BytesIO(png_bytes)).convert("RGBA")
    else:
        import io as _io
        img = Image.open(_io.BytesIO(img_bytes)).convert("RGBA")
    w, h = img.size
    m = max(w, h)
    canvas = Image.new("RGBA", (m, m), (255, 255, 255, 0))
    canvas.paste(img, ((m - w)//2, (m - h)//2))
    canvas = canvas.resize((size, size), Image.LANCZOS)
    canvas.save(out_path, format="PNG")
    return True

def try_endpoints(base_url):
    paths = ["/favicon.ico", "/favicon.png", "/favicon.svg", "/apple-touch-icon.png", "/icon.png"]
    for p in paths:
        yield urljoin(base_url, p)

def fetch_icon_for(name, website):
    out_name = url_to_filename(name, website)
    out_path = OUT / out_name
    if out_path.exists():
        print(f"[skip] {name} -> {out_name}")
        return out_path
    try:
        html_bytes, ctype = fetch_bytes(website)
        for candidate in best_icon_from_html(website, html_bytes):
            try:
                b, ct = fetch_bytes(candidate)
                if save_png(b, ct, out_path):
                    print(f"[ok] {name} <- {candidate}")
                    return out_path
            except Exception:
                continue
    except Exception:
        pass
    for candidate in try_endpoints(website):
        try:
            b, ct = fetch_bytes(candidate)
            if save_png(b, ct, out_path):
                print(f"[ok] {name} <- {candidate}")
                return out_path
        except Exception:
            continue
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGBA", (256,256), (245,245,245,255))
        d = ImageDraw.Draw(img)
        initials = "".join([w[0] for w in name.split() if w][:2]).upper() or "AI"
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 120)
        except Exception:
            font = ImageFont.load_default()
        w, h = d.textsize(initials, font=font)
        d.text(((256-w)//2, (256-h)//2), initials, fill=(60,60,60,255), font=font)
        img.save(out_path, "PNG")
        print(f"[placeholder] {name}")
        return out_path
    except Exception as e:
        print(f"[fail] {name}: {e}")
        return None

def main():
    for cat, name, site in load_projects():
        try:
            fetch_icon_for(name, site)
            time.sleep(0.2)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("[error]", name, e)

if __name__ == "__main__":
    main()