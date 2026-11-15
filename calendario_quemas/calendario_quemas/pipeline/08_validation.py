"""Validación de la armonización: LOYO 2012-2019, retención temporal 2020-2025 y factor Terra->Terra+Aqua."""
import sys, json
import numpy as np, pandas as pd
p = pd.read_parquet(sys.argv[1], columns=["date","sat","sensor","dn","ix","iy","state","frp"])
p["sat"] = p["sat"].astype(str); p["dn"] = p["dn"].astype(str)
p = p[p.date < "2026-01-01"]
NS, TAU = 32, 100.0

def monthly(df):
    g = df.groupby([df.date.dt.year.rename("y"), df.date.dt.month.rename("m"), "state"]).size()
    full = pd.MultiIndex.from_product([range(2000, 2026), range(1, 13), range(NS)], names=["y","m","state"])
    return g.reindex(full, fill_value=0).values.reshape(26, 12, NS).astype(float)

def arrays(df, dedupe=False, vmin=0.0):
    if dedupe: df = df.sort_values("frp", ascending=False).drop_duplicates(["sat","date","dn","ix","iy"])
    if vmin > 0: df = df[(df.sensor == "MODIS") | (df.frp >= vmin)]
    return monthly(df[df.sat.isin(["Terra","Aqua"])]), monthly(df[df.sat == "Terra"]), monthly(df[df.sat == "SNPP"])

def kfit(M, X, years, level, tau=TAU):
    yi = [y-2000 for y in years]; n, d = M[yi].copy(), X[yi].copy()
    if 2012 in years and X is not None and d.sum() and years[0] == 2012 and level != "terra":
        j = years.index(2012); n[j,0] = 0; d[j,0] = 0        # enero 2012 incompleto en VIIRS
    ns, ds = n.sum(0), d.sum(0)
    if level == "global": return np.full_like(ns, ns.sum()/ds.sum())
    knat = ns.sum(1)/ds.sum(1)
    if level == "mes": return np.repeat(knat[:,None], NS, 1)
    return (ns + tau*knat[:,None])/(ds + tau)

def score(pred, obs, years):
    pred, obs = pred.copy(), obs.copy()
    if 2012 in years:
        j = years.index(2012); pred[j,0] = np.nan; obs[j,0] = np.nan
    ok = ~np.isnan(obs)
    sm = np.abs(pred-obs)[ok].sum()/obs[ok].sum()
    pn, on = np.nansum(pred,2), np.nansum(obs,2); bad = np.isnan(obs).all(2); pn[bad] = np.nan; on[bad] = np.nan
    nm = np.nansum(np.abs(pn-on))/np.nansum(on)
    an = np.abs(np.nansum(pred,(1,2))-np.nansum(obs,(1,2))).sum()/np.nansum(obs)
    bias = (np.nansum(pred)-np.nansum(obs))/np.nansum(obs)
    # correlación mensual nacional
    c = np.corrcoef(pn[np.isfinite(pn)&np.isfinite(on)], on[np.isfinite(pn)&np.isfinite(on)])[0,1]
    return dict(wape_estado_mes=sm, wape_nacional_mes=nm, wape_anual=an, sesgo=bias, r_nacional_mes=c)

TRAIN, TEST = list(range(2012,2020)), list(range(2020,2026))
def evaluate(M, V, level):
    folds = []
    for y in TRAIN:
        tr = [t for t in TRAIN if t != y]
        folds.append(score(V[[y-2000]]*kfit(M, V, tr, level)[None], M[[y-2000]], [y]))
    loyo = {k: float(np.mean([f[k] for f in folds])) for k in folds[0]}
    ho = score(V[[y-2000 for y in TEST]]*kfit(M, V, TRAIN, level)[None], M[[y-2000 for y in TEST]], TEST)
    return dict(loyo=loyo, holdout={k: float(v) for k, v in ho.items()})

filt = p[(p.date < "2026-01-01")]
res = {"niveles": [], "variantes": [], "terra": None, "anual": []}
M, T, V = arrays(filt)
for level, label in [("global","Factor único (todo México, todo el año)"), ("mes","Factor por mes (nacional)"), ("estado-mes","Factor por estado y mes (contracción τ=100)")]:
    res["niveles"].append(dict(clave=level, nombre=label, **evaluate(M, V, level)))
for name, dd, vmin in [("Sin huella 1 km, sin umbral de FRP (elegida)", False, 0), ("Con huella de 1 km (fusiona píxeles VIIRS)", True, 0),
                       ("Huella + FRP VIIRS ≥ 2 MW", True, 2.0), ("Huella + FRP VIIRS ≥ 4 MW", True, 4.0), ("Huella + FRP VIIRS ≥ 6 MW", True, 6.0)]:
    M2, T2, V2 = arrays(filt, dd, vmin)
    res["variantes"].append(dict(nombre=name, **evaluate(M2, V2, "estado-mes")))
# Terra -> Terra+Aqua, validación dejando un año fuera (2003-2011)
YT = list(range(2003, 2012)); folds = []
for y in YT:
    tr = [t for t in YT if t != y]
    folds.append(score(T[[y-2000]]*kfit(M, T, tr, "estado-mes")[None], M[[y-2000]], [y]))
res["terra"] = {k: float(np.mean([f[k] for f in folds])) for k in folds[0]}
# nacional anual (observado MODIS T+A, VIIRS crudo, VIIRS calibrado con 2012-2019)
k = kfit(M, V, TRAIN, "estado-mes")
for y in range(2013, 2026):
    obs = M[y-2000].sum(); raw = V[y-2000].sum(); cal = (V[y-2000]*k).sum()
    res["anual"].append(dict(anio=y, modis_observado=float(obs), viirs_crudo=float(raw), viirs_armonizado=float(cal)))
json.dump(res, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
for n in res["niveles"]: print(n["nombre"], {a: round(b,3) for a,b in n["loyo"].items()}, {a: round(b,3) for a,b in n["holdout"].items()})
for n in res["variantes"]: print(n["nombre"], round(n["loyo"]["wape_anual"],3), round(n["holdout"]["wape_anual"],3), round(n["holdout"]["wape_estado_mes"],3))
print("Terra->T+A", {a: round(b,3) for a,b in res["terra"].items()})
