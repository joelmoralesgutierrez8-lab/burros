"""Filtra detecciones (vegetación, confianza >= nominal), construye huellas de ~1 km y asigna estado."""
import sys, time
import numpy as np, pandas as pd, geopandas as gpd, shapely

allp_f, geo_f, out_f = sys.argv[1:4]
t0 = time.time()
p = pd.read_parquet(allp_f)
p["sat"] = p["sat"].astype(str); p["dn"] = p["dn"].astype(str)
n0 = len(p)
p = p[p.date < "2026-01-01"]
n1 = len(p)
p = p[(p.type == 0) & (p.conf_cls >= 1)].copy()
print(f"total={n0:,} hasta 2025={n1:,} tras filtro type==0 & conf>=nominal={len(p):,}")

STEP = 0.01
p["ix"] = np.floor((p.lon.astype("float64") + 118.0) / STEP).astype("int32")
p["iy"] = np.floor((p.lat.astype("float64") - 14.0) / STEP).astype("int32")
cells = p[["ix", "iy"]].drop_duplicates().reset_index(drop=True)
print("celdas 0.01 únicas:", len(cells))
cx = -118.0 + (cells.ix.values + 0.5) * STEP
cy = 14.0 + (cells.iy.values + 0.5) * STEP

g = gpd.read_file(geo_f).to_crs(4326)
state = np.full(len(cells), -1, dtype="int16")
names = g.shapeName.tolist()
for i, geom in enumerate(g.geometry.values):
    m = shapely.contains_xy(geom, cx, cy) & (state < 0)
    state[m] = i
print("asignación por polígono: %.1fs" % (time.time() - t0))
cells["state"] = state
n_out = int((state < 0).sum())
print("celdas fuera de estados:", n_out, "de", len(cells))
if n_out:
    # todas están a < 5 km de un polígono (ajuste de línea de costa): se asignan al estado más cercano
    gp = g.to_crs(6372)[["geometry"]].reset_index().rename(columns={"index": "sid"})
    pts = gpd.GeoDataFrame({"k": np.where(state < 0)[0]}, geometry=gpd.points_from_xy(cx[state < 0], cy[state < 0]), crs=4326).to_crs(6372)
    j = gpd.sjoin_nearest(pts, gp, how="left", distance_col="d").drop_duplicates("k")
    assert j.d.max() < 5000, j.d.max()
    state[j.k.values] = j.sid.values
    print("asignadas al estado más cercano; distancia máx (m):", round(j.d.max()))
cells["state"] = state
p = p.merge(cells, on=["ix", "iy"], how="left")
out_mask = p.state < 0
assert not out_mask.any()
p.to_parquet(out_f, index=False)
pd.Series(names).to_csv(out_f.replace(".parquet", "_estados.csv"), index=True, header=["shapeName"])
print("listo %.1fs" % (time.time() - t0))
