import asyncio, json, csv, io
import pandas as pd
from playwright.async_api import async_playwright
d = pd.read_csv("/home/claude/work/out/hotspots_armonizados_estado_dia.csv", parse_dates=["fecha"])
d["y"] = d.fecha.dt.year
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":1320,"height":1000}, accept_downloads=True)
        pg = await ctx.new_page(); logs=[]
        pg.on("console", lambda m: logs.append((m.type, m.text))); pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
        await pg.goto("http://localhost:8765/index.html")
        await pg.wait_for_function("document.getElementById('loading').hidden === true", timeout=60000)
        names = await pg.evaluate("()=>window.__qm.M.state_names")
        # 1 nacional por año
        js = await pg.evaluate("""()=>{const q=window.__qm,DL=q.getDL(); const o={}; for(let d=0; d<DL.H.length; d++){ const y=new Date(Date.UTC(2000,10,1)+d*864e5).getUTCFullYear(); o[y]=o[y]||[0,0,0,0]; o[y][0]+=DL.H[d]; o[y][1]+=DL.T[d]; o[y][2]+=DL.A[d]; o[y][3]+=DL.S[d]; } return o;}""")
        ref = d.groupby("y")[["hotspots_armonizados","modis_terra","modis_aqua","viirs_snpp"]].sum()
        mx = 0; mxc = 0
        for y, v in js.items():
            r = ref.loc[int(y)]
            mx = max(mx, abs(v[0]-r.hotspots_armonizados)); mxc = max(mxc, abs(v[1]-r.modis_terra), abs(v[2]-r.modis_aqua), abs(v[3]-r.viirs_snpp))
        print("nacional/año: dif máx armonizado = %.3f ; dif máx conteos crudos = %.1f" % (mx, mxc))
        print("total app = %.2f ; total pipeline = %.2f" % (sum(v[0] for v in js.values()), ref.hotspots_armonizados.sum()))
        # 2 por estado (rango completo)
        bad = []
        for i, nm in enumerate(names):
            await pg.select_option("#f-region", "s%d" % i)
            v = await pg.evaluate("()=>{const DL=window.__qm.getDL(); let h=0,t=0,a=0,s=0; for(let d=0; d<DL.H.length; d++){h+=DL.H[d];t+=DL.T[d];a+=DL.A[d];s+=DL.S[d];} return [h,t,a,s];}")
            r = d[d.estado == nm][["hotspots_armonizados","modis_terra","modis_aqua","viirs_snpp"]].sum()
            dif = abs(v[0]-r.hotspots_armonizados)
            if dif > 0.5 or abs(v[1]-r.modis_terra) > 0 or abs(v[3]-r.viirs_snpp) > 0: bad.append((nm, v, r.tolist()))
        print("estados con diferencia:", len(bad), bad[:3])
        # 3 puntos vs diario, tres eras
        await pg.select_option("#f-region", "all")
        for a_, b_ in [("2001-03-01","2001-05-31"),("2005-01-01","2005-12-31"),("2015-01-01","2015-12-31"),("2024-03-01","2024-05-31")]:
            await pg.fill("#f-from", a_); await pg.fill("#f-to", b_); await pg.press("#f-to","Tab"); await pg.wait_for_timeout(300)
            dis = await pg.is_disabled("#ex-points")
            if dis: print(a_, b_, "botón deshabilitado:", await pg.inner_text("#ex-points-s")); continue
            async with pg.expect_download() as dl: await pg.click("#ex-points")
            f = await dl.value; rows = list(csv.DictReader(io.StringIO(open(await f.path(), encoding="utf-8-sig").read())))
            sw = sum(float(r["peso_armonizado"]) for r in rows)
            sub = d[(d.fecha >= a_) & (d.fecha <= b_)]
            sub_h = sub.hotspots_armonizados.sum(); nraw = (sub.modis_terra.sum()+sub.modis_aqua.sum()) if a_ < "2012" else sub.viirs_snpp.sum()
            print(a_, b_, "filas=%d (esperado %d) | Σpesos=%.1f | pipeline=%.1f" % (len(rows), nraw, sw, sub_h))
        # 4 puntos vs parquet original (Morelos 2019)
        await pg.select_option("#f-region", "s16"); await pg.fill("#f-from","2019-04-01"); await pg.fill("#f-to","2019-04-05"); await pg.press("#f-to","Tab"); await pg.wait_for_timeout(300)
        async with pg.expect_download() as dl: await pg.click("#ex-points")
        f = await dl.value; pts = pd.read_csv(await f.path(), encoding="utf-8-sig"); pts.to_csv("/home/claude/work/data/_app_pts_morelos.csv", index=False)
        print("morelos abr 2019:", len(pts), pts.head(3).to_dict("records"))
        print("logs:", logs)
        await b.close()
asyncio.run(main())
