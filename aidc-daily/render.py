"""Usage: python3 render.py day03  -> reads days/day03.json + .html (+ .css), writes out/day03.png"""
import json, os, sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
F = pathlib.Path(os.environ.get("AIDC_FONTS", ROOT / "fonts")).resolve().as_uri()
FONTS = "".join(f'<link rel="stylesheet" href="{F}/{p}">' for p in [
    "fontsource-zcool-kuaile-5.3.0/package/index.css",
    "fontsource-kalam-5.3.0/package/400.css",
    "fontsource-kalam-5.3.0/package/700.css",
    "lxgw-wenkai-webfont-1.7.0/package/lxgwwenkai-regular.css",
    "lxgw-wenkai-webfont-1.7.0/package/lxgwwenkai-bold.css",
    "lxgw-wenkai-webfont-1.7.0/package/lxgwwenkaimono-regular.css",
])
HANDLE = "@startre47133551"

LOGO = '''<svg class="i" width="{s}" height="{s}" viewBox="0 0 64 64" style="stroke:var(--teal);stroke-width:{w}">
<path d="M32 4 56 17v30L32 60 8 47V17z"/><rect x="21" y="19" width="22" height="26" rx="2"/>
<path d="M21 27h22M21 35h22"/><circle cx="26" cy="23" r="1"/><circle cx="26" cy="31" r="1"/><circle cx="26" cy="39" r="1"/>
<path d="M32 45v6M24 51h16" style="stroke:var(--red)"/></svg>'''


def build(day):
    d = ROOT / "days"
    meta = json.loads((d / f"{day}.json").read_text())
    body = (d / f"{day}.html").read_text()
    css = (ROOT / "series.css").read_text()
    extra = (d / f"{day}.css").read_text() if (d / f"{day}.css").exists() else ""
    return f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">{FONTS}
<style>{css}{extra}</style></head><body><div class="page">
<div class="top">
  <div></div>
  <div class="title">
    <div class="series">AIDC 每日一图</div>
    <h1 class="hd">{meta["title"]}</h1>
    <svg class="sq" width="480" height="12" viewBox="0 0 480 12"><path d="M4 7 C 80 2, 170 11, 240 6 S 400 2, 476 7" fill="none" stroke="var(--teal)" stroke-width="3.5" stroke-linecap="round"/></svg>
    <h2>{meta["subtitle"]}</h2>
  </div>
  <div class="ribbon"><div><small>DAY</small><span>{meta["day"]}</span></div>
    <svg width="112" height="30" viewBox="0 0 112 30"><path d="M8 0v28l24-10 24 10 24-10 24 10V0" fill="#fff" stroke="var(--red)" stroke-width="2.6" stroke-linejoin="round"/></svg></div>
</div>
{body}
<div class="foot">
  <div class="who">{LOGO.format(s=44, w=3)}<div><b>AIDC NOTES</b><small>GPU 集群运维笔记</small></div></div>
  <div class="src">{meta["source"]}</div>
  <div class="xid"><span class="xl">𝕏</span><div><b>{HANDLE}</b><small>关注，每天一张 AIDC 知识卡</small></div></div>
</div>
</div></body></html>'''


if __name__ == "__main__":
    day = sys.argv[1]
    html = ROOT / "out" / f"{day}.html"
    html.parent.mkdir(exist_ok=True)
    html.write_text(build(day))
    with sync_playwright() as p:
        exe = os.environ.get("CHROME_PATH")
        b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 600}, device_scale_factor=2)
        pg.goto(html.as_uri()); pg.wait_for_timeout(1500)
        pg.screenshot(path=str(ROOT / "out" / f"{day}.png"), full_page=True)
        print(pg.evaluate("document.body.scrollHeight"))
        b.close()
