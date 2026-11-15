import asyncio
from playwright.async_api import async_playwright
SH="/home/claude/work/shots/"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
        logs=[]
        # escritorio, claro, México completo, año 2011 de referencia, vista anomalía
        ctx = await b.new_context(viewport={"width":1320,"height":1000}, accept_downloads=True)
        pg = await ctx.new_page(); pg.on("console", lambda m: logs.append((m.type, m.text))); pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
        await pg.goto("http://localhost:8765/index.html"); await pg.wait_for_function("document.getElementById('loading').hidden === true", timeout=60000)
        await pg.select_option("#f-ref", "2011"); await pg.click("#cm-anom"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SH+"nac_anom_2011.png", full_page=True)
        await pg.click("#tab-harm"); await pg.wait_for_timeout(300); await pg.screenshot(path=SH+"harm2.png", clip={"x":0,"y":0,"width":1320,"height":1100})
        # exportar PNG con 2 años para ver leyenda
        await pg.click("#tab-explore"); await pg.click("#cm-count"); await pg.fill("#f-from","2020-01-01"); await pg.fill("#f-to","2025-12-31"); await pg.press("#f-to","Tab"); await pg.wait_for_timeout(300)
        async with pg.expect_download() as dl: await pg.click("#ex-png")
        f = await dl.value; await f.save_as(SH+"cal_export2.png")
        await ctx.close()
        # móvil, oscuro, inglés
        ctx = await b.new_context(viewport={"width":390,"height":844}, color_scheme="dark", device_scale_factor=2)
        pg = await ctx.new_page(); pg.on("console", lambda m: logs.append((m.type, m.text))); pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
        await pg.goto("http://localhost:8765/index.html"); await pg.wait_for_function("document.getElementById('loading').hidden === true", timeout=60000)
        await pg.click("#btn-lang"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SH+"mobile_dark_en.png", full_page=True)
        ov = await pg.evaluate("()=>document.documentElement.scrollWidth - document.documentElement.clientWidth")
        print("desborde horizontal móvil (px):", ov)
        print("logs:", logs)
        await b.close()
asyncio.run(main())
