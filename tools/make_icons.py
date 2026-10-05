"""Make the favicon, app icons and social-sharing image from the original NCCMN logo.

Run once after changing static/img/nccmn-logo.png:   python3 tools/make_icons.py
Needs: Pillow and Playwright (for the sharing image text).
"""
import asyncio
import base64
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "static" / "img"
LOGO = Image.open(IMG / "nccmn-logo.png").convert("RGBA")
CROSS = LOGO.crop((250, 60, 446, 256))  # the cross over the map, square


def icon(size, pad=0.06, radius=0.2):
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * radius), fill=255)
    out.paste(Image.new("RGBA", (size, size), (255, 255, 255, 255)), (0, 0), mask)
    inner = int(size * (1 - 2 * pad))
    out.alpha_composite(CROSS.resize((inner, inner), Image.LANCZOS), (int(size * pad), int(size * pad)))
    return out


def make_icons():
    big = icon(512)
    big.resize((32, 32), Image.LANCZOS).save(IMG / "favicon-32.png")
    big.resize((192, 192), Image.LANCZOS).save(IMG / "icon-192.png")
    icon(180, 0.05, 0.18).convert("RGB").save(IMG / "apple-touch-icon.png")
    icon(64).save(ROOT / "static" / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


async def make_og():
    from playwright.async_api import async_playwright
    fdir = ROOT / "static" / "fonts"
    def font(name):
        return "data:font/woff2;base64," + base64.b64encode((fdir / name).read_bytes()).decode()
    logo = base64.b64encode((IMG / "nccmn-logo.png").read_bytes()).decode()
    html = f"""<html><head><style>
    @font-face {{ font-family: L; src: url('{font("literata-latin-600-normal.woff2")}'); }}
    @font-face {{ font-family: F; src: url('{font("libre-franklin-latin-600-normal.woff2")}'); }}
    body {{ margin:0; width:1200px; height:630px; background:#fff; display:flex; align-items:center; gap:56px;
            padding:0 80px; box-sizing:border-box; border-bottom:14px solid #1B2A55; }}
    img {{ width:470px; flex:none }}
    h1 {{ font:600 50px/1.12 L; color:#1B2A55; margin:0 0 22px }}
    p {{ font:600 24px/1.35 F; color:#4B5672; margin:0 }}
    </style></head><body><img src="data:image/png;base64,{logo}">
    <div><h1>Donde la administración está al servicio de la misión</h1>
    <p>Red Nacional de Iglesias y Ministerios Cristianos</p></div></body></html>"""
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        await pg.set_content(html)
        await pg.evaluate("document.fonts.ready")
        await pg.wait_for_timeout(300)
        await pg.screenshot(path=str(IMG / "og.png"))
        await b.close()


if __name__ == "__main__":
    make_icons()
    asyncio.run(make_og())
