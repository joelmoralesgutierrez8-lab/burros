import asyncio, json
from playwright.async_api import async_playwright
SH="/home/claude/work/shots/"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":1320,"height":1000}, accept_downloads=True)
        pg = await ctx.new_page(); logs=[]
        pg.on("console", lambda m: logs.append((m.type, m.text))); pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
        await pg.goto("http://localhost:8765/index.html"); await pg.wait_for_function("document.getElementById('loading').hidden === true", timeout=90000)
        await pg.fill("#f-from","2012-01-20"); await pg.fill("#f-to","2020-12-31"); await pg.press("#f-to","Tab"); await pg.wait_for_timeout(300)
        card = pg.locator("#card-map")
        for lay in ["dens","fact","resid"]:
            await pg.select_option("#map-layer", lay)
            if lay == "dens": await pg.check("#map-log")
            await pg.wait_for_timeout(300)
            await card.screenshot(path=SH+"map_%s.png" % lay)
            st = await pg.evaluate("""()=>{const L=window.__qm.getLAY(); const v=[...L.v].filter(x=>isFinite(x)&&(L.kind!=='dens'||x>0)).sort((a,b)=>a-b); const q=p=>v[Math.floor((v.length-1)*p)]; return {kind:L.kind, n:v.length, p05:q(.05), med:q(.5), p95:q(.95), labels:L.labels, empty:!!L.empty}}""")
            print(lay, json.dumps(st))
        # TLS: capa factor fuera de la era VIIRS
        await pg.fill("#f-from","2003-01-01"); await pg.fill("#f-to","2010-12-31"); await pg.press("#f-to","Tab"); await pg.wait_for_timeout(300)
        await pg.select_option("#map-layer","fact"); await pg.wait_for_timeout(300); await card.screenshot(path=SH+"map_fact_empty.png")
        await pg.select_option("#map-layer","resid"); await pg.fill("#f-from","2012-01-20"); await pg.fill("#f-to","2025-12-31"); await pg.press("#f-to","Tab"); await pg.wait_for_timeout(300)
        async with pg.expect_download() as dl: await pg.click("#ex-mappng")
        f = await dl.value; await f.save_as(SH+"map_export.png"); print("png:", f.suggested_filename)
        # exportación de puntos funciona con datos base64
        await pg.select_option("#f-region","s16"); await pg.fill("#f-from","2019-04-01"); await pg.fill("#f-to","2019-04-05"); await pg.press("#f-to","Tab"); await pg.wait_for_timeout(300)
        async with pg.expect_download() as dl: await pg.click("#ex-points")
        f = await dl.value; import io; n = sum(1 for _ in open(await f.path(), encoding="utf-8-sig")) - 1; print("puntos morelos abr 2019:", n)
        print("logs:", logs)
        await b.close()
asyncio.run(main())
