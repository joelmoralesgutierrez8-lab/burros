import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
        pg = await (await b.new_context(viewport={"width":1320,"height":1000})).new_page()
        await pg.goto("http://localhost:8765/index.html"); await pg.wait_for_function("document.getElementById('loading').hidden === true", timeout=90000)
        for a_, b_ in [("2012-01-20","2025-12-31"),("2012-01-20","2019-12-31"),("2020-01-01","2025-12-31")]:
            await pg.fill("#f-from", a_); await pg.fill("#f-to", b_); await pg.press("#f-to","Tab"); await pg.select_option("#map-layer","resid"); await pg.wait_for_timeout(300)
            st = await pg.evaluate("""()=>{const L=window.__qm.getLAY(); const v=[...L.v].filter(isFinite).sort((a,b)=>a-b); const q=p=>v[Math.floor((v.length-1)*p)]; return {n:v.length, p05:+q(.05).toFixed(2), p25:+q(.25).toFixed(2), med:+q(.5).toFixed(2), p75:+q(.75).toFixed(2), p95:+q(.95).toFixed(2)}}""")
            print(a_, b_, json.dumps(st))
        await b.close()
asyncio.run(main())
