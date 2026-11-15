"""Figura estática de dos paneles: factor efectivo por celda y densidad espacial de VIIRS armonizado.
Uso: python3 09_mapas.py points_state.parquet geojson_completo meta.json salida.png [anio_ini anio_fin]"""
import sys, json
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

pts_f, geo_f, meta_f, out_f = sys.argv[1:5]
y0, y1 = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (2012, 2025)
MIN_N, NCX, NCY = 20, 140, 90
meta = json.load(open(meta_f)); kV = np.array(meta["kV"])      # [mes 0..11][estado 0..31]
p = pd.read_parquet(pts_f, columns=["date", "sat", "state", "lat", "lon"])
p["sat"] = p["sat"].astype(str)
p = p[(p.date >= "2012-01-20") & (p.date.dt.year >= y0) & (p.date.dt.year <= y1)]
cx = np.floor((p.lon.values + 118) / 0.25).astype(int); cy = np.floor((p.lat.values - 14) / 0.25).astype(int)
ok = (cx >= 0) & (cx < NCX) & (cy >= 0) & (cy < NCY)   # descarta unas 25 detecciones de Isla Guadalupe, al oeste de la malla
cell = (cy * NCX + cx)[ok]
v = (p.sat == "SNPP").values[ok]
w = np.where(v, kV[p.date.dt.month.values[ok] - 1, p.state.values.astype(int)[ok]], 0.0)
aS = np.bincount(cell[v], minlength=NCX * NCY).astype(float)
aH = np.bincount(cell[v], weights=w[v], minlength=NCX * NCY)
fact = np.where((aS >= MIN_N) & (aH > 0), aS / np.where(aH > 0, aH, 1), np.nan).reshape(NCY, NCX)
dens = np.where(aH > 0, aH, np.nan).reshape(NCY, NCX)
ext = [-118, -118 + NCX * 0.25, 14, 14 + NCY * 0.25]
g = gpd.read_file(geo_f).to_crs(4326)

fig, ax = plt.subplots(1, 2, figsize=(16.5, 6.4), dpi=150)
lo, hi = np.nanpercentile(fact, [2, 98])
im0 = ax[0].imshow(fact, origin="lower", extent=ext, cmap="YlOrRd", vmin=lo, vmax=hi, interpolation="nearest")
im1 = ax[1].imshow(dens, origin="lower", extent=ext, cmap="magma_r", norm=LogNorm(vmin=1, vmax=np.nanmax(dens)), interpolation="nearest")
rng = f"{y0}–{y1}"
ax[0].set_title(f"Factor efectivo por celda ({rng})", fontsize=12); ax[1].set_title(f"Densidad espacial de VIIRS armonizado ({rng})", fontsize=12)
c0 = fig.colorbar(im0, ax=ax[0], fraction=0.046, pad=0.03); c0.set_label(f"Detecciones VIIRS por hotspot equivalente a MODIS\n(celdas con ≥ {MIN_N} detecciones VIIRS)")
c1 = fig.colorbar(im1, ax=ax[1], fraction=0.046, pad=0.03); c1.set_label("Hotspots armonizados acumulados (escala log)")
for a in ax:
    g.boundary.plot(ax=a, color="black", linewidth=0.5)
    a.set_xlim(-118, -86); a.set_ylim(14, 33); a.set_xlabel("Longitud (°)", fontsize=9); a.set_ylabel("Latitud (°)", fontsize=9); a.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(out_f, bbox_inches="tight"); print("ok", out_f, "celdas factor:", int(np.isfinite(fact).sum()), "p2-p98:", round(lo, 2), round(hi, 2))
