import asyncio, json, sys, csv, io
from playwright.async_api import async_playwright
SH="/home/claude/work/shots/"
async def ready(pg):
    await pg.wait_for_function("document.getElementById('loading').hidden === true", timeout=60000)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":1320,"height":1000}, accept_downloads=True)
        pg = await ctx.new_page(); logs=[]
        pg.on("console", lambda m: logs.append((m.type, m.text))); pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
        await pg.goto("http://localhost:8765/index.html"); await ready(pg)
        # 1. Morelos, 2012-2025, anomalía
        await pg.select_option("#f-region", "s16")   # Morelos (índice 16)
        await pg.click("[data-preset='viirs']")
        await pg.click("#cm-anom")
        await pg.wait_for_timeout(300)
        print("region:", await pg.inner_text("#region-line"))
        print("kpis:", [k.replace("\n"," | ") for k in await pg.eval_on_selector_all(".kpi","els=>els.map(e=>e.innerText)")])
        await pg.screenshot(path=SH+"morelos_anom.png", full_page=True)
        # 2. exportar puntos de Morelos en 2019
        await pg.fill("#f-from","2019-01-01"); await pg.fill("#f-to","2019-12-31")
        await pg.press("#f-to","Tab"); await pg.wait_for_timeout(300)
        print("ex-points:", (await pg.inner_text("#ex-points")).replace("\n"," | "))
        async with pg.expect_download() as dl:
            await pg.click("#ex-points")
        d = await dl.value; path = await d.path(); print("download:", d.suggested_filename)
        txt = open(path, encoding="utf-8-sig").read(); rows = list(csv.DictReader(io.StringIO(txt)))
        print("filas:", len(rows), "suma peso:", round(sum(float(r["peso_armonizado"]) for r in rows),2), rows[0])
        tot = await pg.evaluate("()=>{const q=window.__qm,DL=q.getDL(),S=q.S; let t=0; for(let d=S.from; d<=S.to; d++) t+=DL.H[d]; return t}")
        print("suma H app:", round(tot,2))
        async with pg.expect_download() as dl:
            await pg.click("#ex-daily")
        d = await dl.value; txt = open(await d.path(), encoding="utf-8-sig").read().splitlines(); print("diario:", d.suggested_filename, len(txt)-1, "filas;", txt[0], "|", txt[100])
        async with pg.expect_download() as dl:
            await pg.click("#ex-monthly")
        d = await dl.value; txt = open(await d.path(), encoding="utf-8-sig").read().splitlines(); print("mensual:", d.suggested_filename, len(txt)-1, txt[1])
        async with pg.expect_download() as dl:
            await pg.click("#ex-png")
        d = await dl.value; await d.save_as(SH+"calendario_export.png"); print("png:", d.suggested_filename)
        # 3. pestañas
        await pg.click("#tab-harm"); await pg.wait_for_timeout(400); await pg.screenshot(path=SH+"harm.png", full_page=True)
        print("harm metrics:", [k.replace("\n"," | ") for k in await pg.eval_on_selector_all("#harm-metrics .kpi","els=>els.map(e=>e.innerText)")])
        await pg.click("#tab-about"); await pg.wait_for_timeout(200); await pg.screenshot(path=SH+"about.png", full_page=True)
        print("logs:", logs)
        await b.close()
asyncio.run(main())
