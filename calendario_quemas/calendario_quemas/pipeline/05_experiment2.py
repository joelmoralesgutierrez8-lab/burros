"""Afinación de la calibración (tau, día/noche, no linealidad) y factor Terra->Terra+Aqua."""
import sys
import numpy as np, pandas as pd
pd.set_option("display.width", 250)
p = pd.read_parquet(sys.argv[1], columns=["date","sat","dn","state","frp"])
p["sat"] = p["sat"].astype(str); p["dn"] = p["dn"].astype(str)
p = p[p.date < "2026-01-01"]
NS = 32
def arr(sats, dn=None):
    d = p[p.sat.isin(sats)]
    if dn: d = d[d.dn == dn]
    g = d.groupby([d.date.dt.year.rename("y"), d.date.dt.month.rename("m"), "state"]).size()
    full = pd.MultiIndex.from_product([range(2000, 2026), range(1, 13), range(NS)], names=["y","m","state"])
    return g.reindex(full, fill_value=0).values.reshape(26, 12, NS).astype(float)
M = arr(["Terra","Aqua"]); V = arr(["SNPP"]); T = arr(["Terra"]); A = arr(["Aqua"])
Md = {k: arr(["Terra","Aqua"], k) for k in "DN"}; Vd = {k: arr(["SNPP"], k) for k in "DN"}

def fit(Mx, Vx, years, tau):
    yi = [y-2000 for y in years]; Ms, Vs = Mx[yi].sum(0), Vx[yi].sum(0)
    knat = Ms.sum(1)/Vs.sum(1)
    return (Ms + tau*knat[:,None])/(Vs + tau)
def score(pred, obs, years):
    pred = pred.copy(); obs = obs.copy()
    if 2012 in years:
        j = years.index(2012); pred[j,0] = np.nan; obs[j,0] = np.nan
    ok = ~np.isnan(obs)
    w_sm = np.abs(pred-obs)[ok].sum()/obs[ok].sum()
    np_, no_ = np.nansum(pred,2), np.nansum(obs,2)
    bad = np.isnan(obs).all(2); np_[bad]=np.nan; no_[bad]=np.nan
    w_nm = np.nansum(np.abs(np_-no_))/np.nansum(no_)
    w_an = np.abs(np.nansum(pred,(1,2))-np.nansum(obs,(1,2))).sum()/np.nansum(obs)
    bias = (np.nansum(pred)-np.nansum(obs))/np.nansum(obs)
    return w_sm, w_nm, w_an, bias
TRAIN = list(range(2012,2020)); TEST = list(range(2020,2026))
def cv(predict_fn):
    e = []
    for y in TRAIN:
        tr = [t for t in TRAIN if t!=y]
        e.append(score(predict_fn(tr,[y]), M[[y-2000]], [y]))
    e = np.array(e).mean(0)
    h = score(predict_fn(TRAIN,TEST), M[[y-2000 for y in TEST]], TEST)
    return e, h
rows = []
for tau in [0, 10, 30, 100, 300, 1000]:
    f = lambda tr, te: V[[y-2000 for y in te]] * fit(M, V, tr, tau)[None]
    e, h = cv(f); rows.append(("estado-mes tau=%d"%tau, *e, *h))
# día/noche
for tau in [30, 100]:
    def f(tr, te, tau=tau):
        return sum(Vd[k][[y-2000 for y in te]] * fit(Md[k], Vd[k], tr, tau)[None] for k in "DN")
    e, h = cv(f); rows.append(("estado-mes x día/noche tau=%d"%tau, *e, *h))
# no linealidad: pred = k * V^b con b global estimado en train (log-log sobre estado-mes con V>=30)
def f_pow(tr, te, tau=30):
    yi = [y-2000 for y in tr]
    v = V[yi].ravel(); m = M[yi].ravel(); ok = (v>=30)&(m>=10)
    # regresión de log(m/V) sobre log(V) tras quitar efecto estado-mes (demedia por estado-mes)
    lv = np.log(V[yi]); lr = np.log(np.where(V[yi]>0, M[yi]/np.maximum(V[yi],1), np.nan))
    okm = (V[yi]>=30)&(M[yi]>=10)
    lvd = lv - np.nanmean(np.where(okm, lv, np.nan), 0, keepdims=True)
    lrd = lr - np.nanmean(np.where(okm, lr, np.nan), 0, keepdims=True)
    x = lvd[okm]; y_ = lrd[okm]; x = x[np.isfinite(x)&np.isfinite(y_)]; y_ = y_[np.isfinite(lvd[okm])&np.isfinite(lrd[okm])]
    b = (x*y_).sum()/(x*x).sum()
    Vt = V[[y-2000 for y in te]]
    Vref = V[yi].mean(0, keepdims=True)
    k = fit(M, V, tr, tau)[None]
    return k * Vt * (np.maximum(Vt,1)/np.maximum(Vref,1))**b
e, h = cv(f_pow); rows.append(("estado-mes + potencia (V/Vref)^b", *e, *h))
r = pd.DataFrame(rows, columns=["modelo","LOYO_estado_mes","LOYO_nac_mes","LOYO_anual","LOYO_sesgo","HO_estado_mes","HO_nac_mes","HO_anual","HO_sesgo"])
print(r.round(3).to_string(index=False))

# Terra -> Terra+Aqua con años 2003-2011 (Aqua operativo todo el año)
YT = list(range(2003, 2012))
def fitT(years, tau=30):
    yi = [y-2000 for y in years]; Ms, Ts = M[yi].sum(0), T[yi].sum(0)
    kn = Ms.sum(1)/Ts.sum(1); return (Ms+tau*kn[:,None])/(Ts+tau)
e = []
for y in YT:
    tr = [t for t in YT if t!=y]; pred = T[[y-2000]]*fitT(tr)[None]
    e.append(score(pred, M[[y-2000]], [y]))
print("Terra -> Terra+Aqua LOYO 2003-2011 (WAPE estado-mes, nac-mes, anual, sesgo):", np.array(e).mean(0).round(3))
k = fitT(YT)
print("k Terra->T+A: rango nacional por mes:", (M[[y-2000 for y in YT]].sum((0,2))/T[[y-2000 for y in YT]].sum((0,2))).round(2))
# ratio VIIRS->MODIS nacional por mes (2012-2019)
yi = [y-2000 for y in TRAIN]
print("k VIIRS->T+A nacional por mes:", (M[yi].sum((0,2))/V[yi].sum((0,2))).round(3))
# deriva: razón anual nacional MODIS(T+A)/VIIRS
yy = list(range(2013, 2026))
print("razón anual T+A / VIIRS:", {y: round(M[y-2000].sum()/V[y-2000].sum(),3) for y in yy})
print("razón anual Aqua/VIIRS:", {y: round(A[y-2000].sum()/V[y-2000].sum(),3) for y in yy})
print("razón anual Terra/Aqua:", {y: round(T[y-2000].sum()/A[y-2000].sum(),3) for y in range(2003,2026)})
