"""Armonización MODIS (Terra+Aqua) / VIIRS (SNPP): factores, series y tablas compactas para la app."""
import sys, json, gzip, os, struct
import numpy as np, pandas as pd, geopandas as gpd, shapely

PTS, GEO, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
D0 = pd.Timestamp("2000-11-01")
AQUA0 = pd.Timestamp("2002-07-04")     # primer día con Aqua en la data
VIIRS0 = pd.Timestamp("2012-01-20")    # primer día con VIIRS SNPP en la data
TAU = 100.0
NS = 32

p = pd.read_parquet(PTS, columns=["date","acq_time","lat","lon","sat","dn","conf_cls","frp","ix","iy","state"])
p["sat"] = p["sat"].astype(str); p["dn"] = p["dn"].astype(str)
p["d"] = (p.date - D0).dt.days.astype("int32")
NDAYS = int((pd.Timestamp("2025-12-31") - D0).days) + 1
assert p.d.max() == NDAYS - 1 or p.d.max() < NDAYS
print("días:", NDAYS, "puntos:", len(p))

# ---------- estados ----------
g = gpd.read_file(GEO).to_crs(4326)
ES = {"Aguascalientes":"Aguascalientes","Baja California":"Baja California","Baja California Sur":"Baja California Sur","Campeche":"Campeche",
 "Chiapas":"Chiapas","Chihuahua":"Chihuahua","Coahuila de Zaragoza":"Coahuila","Colima":"Colima","Distrito Federal":"Ciudad de México",
 "Durango":"Durango","Guanajuato":"Guanajuato","Guerrero":"Guerrero","Hidalgo":"Hidalgo","Jalisco":"Jalisco","Mexico":"Estado de México",
 "Michoacan de Ocampo":"Michoacán","Morelos":"Morelos","Nayarit":"Nayarit","Nuevo Leon":"Nuevo León","Oaxaca":"Oaxaca","Puebla":"Puebla",
 "Queretaro de Arteaga":"Querétaro","Quintana Roo":"Quintana Roo","San Luis Potosi":"San Luis Potosí","Sinaloa":"Sinaloa","Sonora":"Sonora",
 "Tabasco":"Tabasco","Tamaulipas":"Tamaulipas","Tlaxcala":"Tlaxcala","Veracruz de Ignacio de la Llave":"Veracruz","Yucatan":"Yucatán","Zacatecas":"Zacatecas"}
state_names = [ES[n] for n in g.shapeName]
state_iso = g.shapeISO.tolist()
assert len(state_names) == NS

# ---------- factores de calibración ----------
def monthly(df):
    gg = df.groupby([df.date.dt.year.rename("y"), df.date.dt.month.rename("m"), "state"]).size()
    full = pd.MultiIndex.from_product([range(2000, 2026), range(1, 13), range(NS)], names=["y","m","state"])
    return gg.reindex(full, fill_value=0).values.reshape(26, 12, NS).astype(float)
Tm, Am, Vm = monthly(p[p.sat=="Terra"]), monthly(p[p.sat=="Aqua"]), monthly(p[p.sat=="SNPP"])
Mm = Tm + Am

def shrunk(num, den, years, tau, mask_jan2012=False):
    yi = [y-2000 for y in years]
    n, d_ = num[yi].copy(), den[yi].copy()
    if mask_jan2012 and 2012 in years:
        j = years.index(2012); n[j,0] = 0; d_[j,0] = 0
    ns, ds = n.sum(0), d_.sum(0)                       # [mes, estado]
    knat = ns.sum(1) / ds.sum(1)
    return (ns + tau*knat[:,None]) / (ds + tau), knat, ns, ds
TRAIN_V = list(range(2012, 2020)); TRAIN_T = list(range(2003, 2012))
kV, kV_nat, _, _ = shrunk(Mm, Vm, TRAIN_V, TAU, mask_jan2012=True)   # [mes, estado]
kT, kT_nat, _, _ = shrunk(Mm, Tm, TRAIN_T, TAU)
print("kV nacional por mes:", kV_nat.round(3)); print("kT nacional por mes:", kT_nat.round(2))
print("kV rango entre estados:", kV.min().round(3), kV.max().round(3), " kT:", kT.min().round(2), kT.max().round(2))

# ---------- peso armonizado por detección ----------
m0 = p.date.dt.month.values - 1
st = p.state.values
w = np.zeros(len(p), dtype="float64")
is_T = (p.sat == "Terra").values; is_A = (p.sat == "Aqua").values; is_S = (p.sat == "SNPP").values
pre_v = (p.date < VIIRS0).values
w[is_A & pre_v & (p.date >= AQUA0).values] = 1.0
w[is_T & pre_v & (p.date >= AQUA0).values] = 1.0
mT = is_T & pre_v & (p.date < AQUA0).values
w[mT] = kT[m0[mT], st[mT]]
w[is_S] = kV[m0[is_S], st[is_S]]
p["w"] = w
p["en_serie"] = w > 0
print("detecciones en la serie armonizada:", int(p.en_serie.sum()), " suma de pesos:", round(w.sum()))

# ---------- tabla estado-día ----------
cnt = p.groupby(["d","state","sat"]).size().unstack("sat", fill_value=0)
for c in ["Terra","Aqua","SNPP"]:
    if c not in cnt: cnt[c] = 0
wsum = p.groupby(["d","state"]).w.sum()
full = pd.MultiIndex.from_product([range(NDAYS), range(NS)], names=["d","state"])
sd = pd.DataFrame(index=full)
sd = sd.join(cnt[["Terra","Aqua","SNPP"]]).join(wsum.rename("armonizado")).fillna(0)
sd[["Terra","Aqua","SNPP"]] = sd[["Terra","Aqua","SNPP"]].astype(int)
sd = sd.reset_index()
sd["fecha"] = D0 + pd.to_timedelta(sd.d, unit="D")
def fuente(f):
    return np.where(f < AQUA0, "Terra (escalado)", np.where(f < VIIRS0, "Terra+Aqua", "VIIRS SNPP (calibrado)"))
sd["fuente"] = fuente(sd.fecha)
sd["estado"] = [state_names[i] for i in sd.state]; sd["clave_estado"] = [state_iso[i] for i in sd.state]
sd_out = sd[["fecha","clave_estado","estado","Terra","Aqua","SNPP","armonizado","fuente"]].rename(columns={"Terra":"modis_terra","Aqua":"modis_aqua","SNPP":"viirs_snpp","armonizado":"hotspots_armonizados"})
sd_out["fecha"] = sd_out.fecha.dt.strftime("%Y-%m-%d"); sd_out["hotspots_armonizados"] = sd_out.hotspots_armonizados.round(3)
sd_out.to_csv(f"{OUT}/hotspots_armonizados_estado_dia.csv", index=False)
sm = sd.assign(anio=sd.fecha.dt.year, mes=sd.fecha.dt.month).groupby(["anio","mes","clave_estado","estado"], sort=False)[["Terra","Aqua","SNPP","armonizado"]].sum().reset_index()
sm = sm.rename(columns={"Terra":"modis_terra","Aqua":"modis_aqua","SNPP":"viirs_snpp","armonizado":"hotspots_armonizados"}); sm["hotspots_armonizados"] = sm.hotspots_armonizados.round(3)
sm.to_csv(f"{OUT}/hotspots_armonizados_estado_mes.csv", index=False)
kk = []
for s in range(NS):
    for m in range(12):
        kk.append(dict(clave_estado=state_iso[s], estado=state_names[s], mes=m+1, k_viirs_a_modis=round(kV[m,s],5), k_terra_a_terra_aqua=round(kT[m,s],4)))
pd.DataFrame(kk).to_csv(f"{OUT}/factores_calibracion.csv", index=False)

# ---------- unidades (celda 0.25° x estado) ----------
p["cx"] = (p.ix // 25).astype("int32"); p["cy"] = (p.iy // 25).astype("int32")
units = p[["state","cy","cx"]].drop_duplicates().sort_values(["state","cy","cx"]).reset_index(drop=True)
units["u"] = np.arange(len(units))
p = p.merge(units, on=["state","cy","cx"], how="left")
assert len(units) < 65535
print("unidades:", len(units))

# ---------- fragmentos (día, unidad) ----------
fr = p.groupby(["d","u","sat"]).size().unstack("sat", fill_value=0)
for c in ["Terra","Aqua","SNPP"]:
    if c not in fr: fr[c] = 0
fr = fr.reset_index().sort_values(["d","u"])
assert fr[["Terra","Aqua","SNPP"]].max().max() < 65535
print("fragmentos:", len(fr))
buf = b"".join([struct.pack("<I", len(fr)),
    fr.d.values.astype("<u2").tobytes(), fr.u.values.astype("<u2").tobytes(),
    fr.Terra.values.astype("<u2").tobytes(), fr.Aqua.values.astype("<u2").tobytes(), fr.SNPP.values.astype("<u2").tobytes()])
os.makedirs(f"{OUT}/app_data", exist_ok=True)
with gzip.open(f"{OUT}/app_data/frag.bin.gz", "wb", compresslevel=9) as f: f.write(buf)

# ---------- puntos por año (solo los que entran a la serie armonizada) ----------
os.makedirs(f"{OUT}/app_data/pts", exist_ok=True)
q = p[p.en_serie].copy()
q["year"] = q.date.dt.year
sat_code = {"Terra":0, "Aqua":1, "SNPP":2}
q["fl"] = (q.sat.map(sat_code).to_numpy().astype("int64") | ((q.conf_cls.to_numpy().astype("int64") - 1) << 2) | ((q.dn == "N").to_numpy().astype("int64") << 3)).astype("uint8")
q["dy"] = np.clip(np.round((q.lat.astype("float64") - (14.0 + q.cy*0.25)) / 0.001), 0, 249).astype("uint8")
q["dx"] = np.clip(np.round((q.lon.astype("float64") - (-118.0 + q.cx*0.25)) / 0.001), 0, 249).astype("uint8")
q["frp10"] = np.clip(np.round(q.frp.astype("float64") * 10), 0, 65535).astype("uint16")
print("FRP > 6553.5 MW:", int((q.frp > 6553.5).sum()))
sizes = {}
for y, gq in q.groupby("year"):
    gq = gq.sort_values(["d","u"])
    b = b"".join([struct.pack("<I", len(gq)), gq.d.values.astype("<u2").tobytes(), gq.u.values.astype("<u2").tobytes(),
        gq.dy.values.tobytes(), gq.dx.values.tobytes(), gq.frp10.values.astype("<u2").tobytes(),
        gq.acq_time.values.astype("<u2").tobytes(), gq.fl.values.tobytes()])
    fn = f"{OUT}/app_data/pts/pts_{y}.bin.gz"
    with gzip.open(fn, "wb", compresslevel=9) as f: f.write(b)
    sizes[int(y)] = (len(gq), os.path.getsize(fn))
tot_pts = sum(v[0] for v in sizes.values()); tot_b = sum(v[1] for v in sizes.values())
print("puntos exportados:", tot_pts, " tamaño gz total MB:", round(tot_b/1e6,1), " frag MB:", round(os.path.getsize(f"{OUT}/app_data/frag.bin.gz")/1e6,2))
print("mayor chunk MB:", round(max(v[1] for v in sizes.values())/1e6,2))

# ---------- mapa: polígonos simplificados y cuantizados ----------
geoms = shapely.coverage_simplify(g.geometry.values, 0.02)
def rings(geom):
    out = []
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    for pg in polys:
        if pg.area < 0.002: continue          # descarta islotes < ~20 km²
        for r in [pg.exterior] + list(pg.interiors):
            c = np.round((np.array(r.coords) - [-118.0, 14.0]) * 100).astype(int)
            keep = np.r_[True, (np.diff(c, axis=0) != 0).any(1)]
            out.append(c[keep].ravel().tolist())
    return out
poly = [rings(gm) for gm in geoms]

# ---------- metadatos ----------
meta = dict(
    d0="2000-11-01", ndays=NDAYS, aqua0=int((AQUA0-D0).days), viirs0=int((VIIRS0-D0).days),
    state_names=state_names, state_iso=state_iso,
    units=dict(cx=units.cx.tolist(), cy=units.cy.tolist(), st=units.state.tolist()),
    kV=np.round(kV, 5).tolist(), kT=np.round(kT, 4).tolist(),      # [mes][estado]
    kV_nat=np.round(kV_nat, 5).tolist(), kT_nat=np.round(kT_nat, 4).tolist(),
    train_V=[2012, 2019], train_T=[2003, 2011], tau=TAU,
    poly=poly, pts_years={str(k): v[0] for k, v in sizes.items()},
)
json.dump(meta, open(f"{OUT}/app_data/meta.json", "w"), separators=(",", ":"), ensure_ascii=False)
print("meta.json KB:", round(os.path.getsize(f"{OUT}/app_data/meta.json")/1e3))
# resumen nacional anual para verificación
ann = sd.assign(anio=sd.fecha.dt.year).groupby("anio")[["Terra","Aqua","SNPP","armonizado"]].sum().round(0).astype(int)
print(ann.to_string())
