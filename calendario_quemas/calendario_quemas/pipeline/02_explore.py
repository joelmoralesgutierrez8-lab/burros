import sys
import numpy as np, pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 50); pd.set_option("display.max_rows", 200)
p = pd.read_parquet(sys.argv[1])
p["year"] = p.date.dt.year
print("== tipo (type) por sensor"); print(pd.crosstab(p.sensor, p.type))
print("== confianza por sensor/sat"); print(pd.crosstab([p.sensor, p.sat], p.conf_cls))
print("== nrt"); print(p.groupby(["sensor","nrt"], observed=True).size())
print("== puntos por año y satélite (todos)")
t = p.groupby(["year","sat"], observed=True).size().unstack(fill_value=0); print(t)
print("== puntos por año/sat con type==0 y conf>=1")
q = p[(p.type==0)&(p.conf_cls>=1)]
print(q.groupby(["year","sat"], observed=True).size().unstack(fill_value=0))
# horas locales aprox de paso (UTC)
p["hr"] = (p.acq_time//100) + (p.acq_time%100)/60
print("== hora UTC mediana por año/sat/dn")
print(p.groupby(["sat","dn","year"], observed=True).hr.median().unstack("year").round(1).to_string())
# días con datos por sat
d = p.groupby("sat", observed=True).date.agg(["min","max","nunique"]); print(d)
# duplicados exactos
dup = p.duplicated(["date","acq_time","lat","lon","sat"]).sum(); print("duplicados exactos:", dup)
