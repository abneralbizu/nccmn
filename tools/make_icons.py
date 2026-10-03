"""Render favicon.ico, apple-touch-icon.png and og.png from the SVG mark. Run once: python3 tools/make_icons.py"""
import asyncio, subprocess
from pathlib import Path
from playwright.async_api import async_playwright
ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "static" / "img"
fav = (IMG / "favicon.svg").read_text()
mark_light = (IMG / "mark-light.svg").read_text()
fonts = (ROOT / "static" / "fonts").as_uri()
OG = f"""<html><head><style>
@font-face {{ font-family: L; src: url('{fonts}/literata-latin-600-normal.woff2'); }}
@font-face {{ font-family: F; src: url('{fonts}/libre-franklin-latin-600-normal.woff2'); }}
body {{ margin:0; width:1200px; height:630px; background:#1B2A55; color:#fff; display:flex; align-items:center; gap:64px; padding:0 96px; box-sizing:border-box; }}
.m {{ width:150px; flex:none }} h1 {{ font: 600 60px/1.1 L; margin:0 0 24px }} p {{ font: 600 26px/1.3 F; color:#C9D2E4; margin:0 }}
</style></head><body><div class="m">{mark_light}</div><div><h1>Donde la administración está al servicio de la misión</h1>
<p>Red Nacional de Iglesias y Ministerios Cristianos (NCCMN)</p></div></body></html>"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 180, "height": 180})
        await pg.set_content(f"<body style='margin:0'>{fav.replace('<svg ', '<svg width=180 height=180 ')}</body>")
        await pg.screenshot(path=str(IMG / "apple-touch-icon.png"), omit_background=True)
        await pg.set_viewport_size({"width": 64, "height": 64})
        await pg.set_content(f"<body style='margin:0'>{fav.replace('<svg ', '<svg width=64 height=64 ')}</body>")
        await pg.screenshot(path="/tmp/fav64.png", omit_background=True)
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        await pg.set_content(OG); await pg.wait_for_timeout(300)
        await pg.screenshot(path=str(IMG / "og.png"))
        await b.close()
    subprocess.run(["convert", "/tmp/fav64.png", "-define", "icon:auto-resize=48,32,16", str(ROOT / "static" / "favicon.ico")], check=True)
asyncio.run(main())
