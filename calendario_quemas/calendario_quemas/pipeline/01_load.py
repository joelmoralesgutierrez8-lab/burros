"""Carga los parquet de FIRMS (MODIS y VIIRS SNPP) y los unifica en un esquema común."""
import sys, glob, os
import numpy as np, pandas as pd

src, out = sys.argv[1], sys.argv[2]
frames = []
for f in sorted(glob.glob(os.path.join(src, "*.parquet"))):
    name = os.path.basename(f)
    df = pd.read_parquet(f)
    if name.startswith("modis"):
        sensor = "MODIS"
        conf = df["confidence"].astype(int)
        conf_cls = np.where(conf >= 80, 2, np.where(conf >= 30, 1, 0)).astype("int8")
        sat = df["satellite"].map({"Terra": "Terra", "Aqua": "Aqua"})
        bt = df["brightness"]
        nrt = df["version"].astype(str).str.contains("NRT")
        conf_raw = conf.astype("int16")
    else:
        sensor = "VIIRS"
        conf_cls = df["confidence"].map({"l": 0, "n": 1, "h": 2}).astype("int8")
        sat = df["satellite"].map({"N": "SNPP"})
        bt = df["bright_ti4"]
        nrt = pd.Series(False, index=df.index)
        conf_raw = pd.Series(-1, index=df.index, dtype="int16")
    o = pd.DataFrame({
        "date": pd.to_datetime(df["acq_date"]),
        "acq_time": df["acq_time"].astype("int16"),
        "lat": df["latitude"].astype("float32"),
        "lon": df["longitude"].astype("float32"),
        "sensor": sensor,
        "sat": sat.astype("string"),
        "conf_cls": conf_cls,
        "conf_raw": conf_raw,
        "frp": df["frp"].astype("float32"),
        "bright": bt.astype("float32"),
        "scan": df["scan"].astype("float32"),
        "track": df["track"].astype("float32"),
        "dn": df["daynight"].astype("string"),
        "type": df["type"].astype("int8"),
        "nrt": nrt.values,
        "src": name,
    })
    frames.append(o)
allp = pd.concat(frames, ignore_index=True)
for c in ["sensor", "sat", "dn", "src"]:
    allp[c] = allp[c].astype("category")
allp.to_parquet(out, index=False)
print(allp.shape)
print(allp.groupby(["sensor", "sat"], observed=True).size())
print("fechas:", allp.date.min(), allp.date.max())
print("nulos:\n", allp.isna().sum())
