import sys, numpy as np, pandas as pd
p = pd.read_parquet(sys.argv[1], columns=["date","sat","ix","iy","state","frp"])
p["sat"] = p["sat"].astype(str)
print("puntos filtrados:", len(p), p.groupby("sat").size().to_dict())
for step in [25, 10]:   # celdas de 0.25 y 0.10 grados (ix,iy son de 0.01)
    cx = p.ix // step; cy = p.iy // step
    key = pd.DataFrame({"d": p.date.dt.normalize(), "cx": cx, "cy": cy, "s": p.state})
    n = len(key.drop_duplicates())
    ncell = len(key[["cx","cy","s"]].drop_duplicates())
    print(f"malla {step/100:.2f}°: fragmentos (día,celda,estado)={n:,}  unidades (celda,estado)={ncell:,}")
# puntos que sí entran en la serie armonizada
d = p.date
inser = ((p.sat=="Terra")&(d<"2012-01-20")) | ((p.sat=="Aqua")&(d<"2012-01-20")&(d>="2002-07-04")) | ((p.sat=="SNPP")&(d>="2012-01-20"))
print("puntos en serie armonizada:", int(inser.sum()), p[inser].groupby("sat").size().to_dict())
print("frp max:", p.frp.max())
