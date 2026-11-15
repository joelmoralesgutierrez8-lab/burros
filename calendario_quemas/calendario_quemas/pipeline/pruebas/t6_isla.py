import asyncio, io, csv
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":1320,"height":1000}, accept_downloads=True); pg = await ctx.new_page(); logs=[]
        pg.on("console", lambda m: logs.append((m.type, m.text))); pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
        await pg.goto("http://localhost:8765/index.html"); await pg.wait_for_function("document.getElementById('loading').hidden === true", timeout=90000)
        await pg.select_option("#f-region", "s1"); await pg.fill("#f-from","2008-09-15"); await pg.fill("#f-to","2008-09-16"); await pg.press("#f-to","Tab"); await pg.wait_for_timeout(300)
        async with pg.expect_download() as dl: await pg.click("#ex-points")
        f = await dl.value; rows = list(csv.DictReader(open(await f.path(), encoding="utf-8-sig")))
        w = [r for r in rows if float(r["longitud"]) < -118]
        print("filas:", len(rows), "con lon<-118:", len(w), [ (r["latitud"], r["longitud"]) for r in w[:3] ], "lon máx abs:", max(abs(float(r["longitud"])) for r in rows))
        print("logs:", logs); await b.close()
asyncio.run(main())
