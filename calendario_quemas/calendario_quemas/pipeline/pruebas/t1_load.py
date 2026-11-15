import asyncio, json, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width":1320,"height":1000})
        logs = []
        pg.on("console", lambda m: logs.append((m.type, m.text)))
        pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
        await pg.goto("http://localhost:8765/index.html")
        try:
            await pg.wait_for_function("document.getElementById('loading').hidden === true", timeout=60000)
        except Exception as e:
            print("TIMEOUT", e)
        print("logs:", logs[:10])
        await pg.screenshot(path="/home/claude/work/shots/explore_full.png", full_page=True)
        info = await pg.evaluate("""() => { const q = window.__qm; const DL = q.getDL(); const A = q.getA();
          let tot=0; for (let d=0; d<DL.H.length; d++) tot+=DL.H[d];
          const y = {}; for (let d=0; d<DL.H.length; d++){ const yr = 2000 + Math.floor(q.monthInfo ? 0:0); }
          return {tot, years: A.rows.length, kpis: [...document.querySelectorAll('.kpi')].map(k=>k.innerText.replace(/\\n/g,' | '))}; }""")
        print(json.dumps(info, ensure_ascii=False, indent=1))
        await b.close()
asyncio.run(main())
