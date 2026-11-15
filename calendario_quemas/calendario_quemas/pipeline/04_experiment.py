"""Compara variantes de armonización VIIRS -> MODIS (Terra+Aqua) en el traslape 2012-2025."""
import sys, itertools
import numpy as np, pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 50)

p = pd.read_parquet(sys.argv[1], columns=["date","sat","sensor","dn","ix","iy","state","frp","type","conf_cls"])
p["sat"] = p["sat"].astype(str); p["dn"] = p["dn"].astype(str)
p["ym"] = p.date.dt.to_period("M")
NS = 32

def monthly(df, sat_filter):
    d = df[df.sat.isin(sat_filter)]
    g = d.groupby([d.date.dt.year.rename("y"), d.date.dt.month.rename("m"), "state"]).size()
    full = pd.MultiIndex.from_product([range(2000, 2026), range(1, 13), range(NS)], names=["y","m","state"])
    return g.reindex(full, fill_value=0).values.reshape(26, 12, NS).astype(float)   # [año-2000, mes-1, estado]

def build(df, dedupe, viirs_frp_min=0.0):
    if dedupe:
        df = df.sort_values("frp", ascending=False).drop_duplicates(["sat","date","dn","ix","iy"])
    if viirs_frp_min > 0:
        df = df[(df.sensor == "MODIS") | (df.frp >= viirs_frp_min)]
    return monthly(df, ["Terra","Aqua"]), monthly(df, ["Aqua"]), monthly(df, ["SNPP"])

def fit_k(M, V, years, tau, level):
    """M, V: [año, mes, estado]. Devuelve k[mes, estado]."""
    yi = [y - 2000 for y in years]
    Ms, Vs = M[yi].sum(0), V[yi].sum(0)      # [mes, estado]
    if level == "global":
        k = Ms.sum() / Vs.sum(); return np.full_like(Ms, k)
    knat = Ms.sum(1) / Vs.sum(1)             # [mes]
    if level == "mes":
        return np.repeat(knat[:, None], NS, 1)
    # estado x mes con contracción hacia el ratio nacional del mes
    return (Ms + tau * knat[:, None]) / (Vs + tau)

def metrics(M, V, k, years):
    yi = [y - 2000 for y in years]
    pred = V[yi] * k[None]; obs = M[yi]
    # excluir ene-2012 incompleto
    if 2012 in years:
        j = years.index(2012); pred[j, 0] = np.nan; obs[j, 0] = np.nan
    ok = ~np.isnan(obs)
    wape_sm = np.abs(pred - obs)[ok].sum() / obs[ok].sum()
    nat_p = np.nansum(pred, 2); nat_o = np.nansum(obs, 2)
    nat_p[np.isnan(obs).all(2)] = np.nan; nat_o[np.isnan(obs).all(2)] = np.nan
    okn = ~np.isnan(nat_o)
    wape_nat = np.abs(nat_p - nat_o)[okn].sum() / nat_o[okn].sum()
    bias = (np.nansum(pred) - np.nansum(obs)) / np.nansum(obs)
    ann_p = np.nansum(pred, (1, 2)); ann_o = np.nansum(obs, (1, 2))
    wape_ann = np.abs(ann_p - ann_o).sum() / ann_o.sum()
    return wape_sm, wape_nat, wape_ann, bias

TRAIN = list(range(2012, 2020)); TEST = list(range(2020, 2026))
rows = []
variants = [
    ("V0 crudo (sin filtros, sin huella)", None, False, 0),
    ("V1 filtro (tipo 0, conf>=nominal)", "f", False, 0),
    ("V2 filtro + huella 1 km", "f", True, 0),
    ("V3 filtro + huella + FRP>=2", "f", True, 2.0),
    ("V4 filtro + huella + FRP>=4", "f", True, 4.0),
    ("V5 filtro + huella + FRP>=6", "f", True, 6.0),
]
for name, flt, dd, fmin in variants:
    if flt is None:
        d = p[p.date < "2026-01-01"]
    else:
        d = p[(p.type == 0) & (p.conf_cls >= 1) & (p.date < "2026-01-01")]
    for target in ["Terra+Aqua", "Aqua"]:
        MT, MA, V = build(d, dd, fmin)
        M = MT if target == "Terra+Aqua" else MA
        for level, tau in [("global", 0), ("mes", 0), ("estado-mes", 30)]:
            # LOYO en 2012-2019
            err = []
            for y in TRAIN:
                tr = [t for t in TRAIN if t != y]
                k = fit_k(M, V, tr, tau, level)
                err.append(metrics(M, V, k, [y]))
            err = np.array(err)
            # ponderar por magnitud: promedio simple de WAPE anual (aprox.)
            k = fit_k(M, V, TRAIN, tau, level)
            ho = metrics(M, V, k, TEST)
            rows.append(dict(variante=name, objetivo=target, calibracion=level,
                             LOYO_WAPE_estado_mes=err[:,0].mean(), LOYO_WAPE_nac_mes=err[:,1].mean(), LOYO_WAPE_anual=err[:,2].mean(),
                             HO_WAPE_estado_mes=ho[0], HO_WAPE_nac_mes=ho[1], HO_WAPE_anual=ho[2], HO_sesgo=ho[3]))
r = pd.DataFrame(rows)
r.to_csv("data/experimento_variantes.csv", index=False)
print(r[r.objetivo=="Terra+Aqua"].round(3).to_string(index=False))
print()
print(r[r.objetivo=="Aqua"].round(3).to_string(index=False))
