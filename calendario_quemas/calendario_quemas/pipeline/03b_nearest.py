import sys, numpy as np, pandas as pd, geopandas as gpd
p = pd.read_parquet(sys.argv[1])
cells = p[p.state < 0][["ix","iy"]].drop_duplicates()
cx = -118.0 + (cells.ix.values + 0.5) * 0.01; cy = 14.0 + (cells.iy.values + 0.5) * 0.01
pts = gpd.GeoDataFrame(cells.reset_index(drop=True), geometry=gpd.points_from_xy(cx, cy), crs=4326).to_crs(6372)
for name, f in [("simplificado", sys.argv[2]), ("completo", sys.argv[3])]:
    g = gpd.read_file(f).to_crs(6372)[["shapeName","geometry"]]
    j = gpd.sjoin_nearest(pts, g, how="left", distance_col="d")
    j = j.drop_duplicates(["ix","iy"])
    print(name, "celdas fuera:", len(j))
    print(j.d.describe(percentiles=[.5,.75,.9,.95,.99]).round(0).to_string())
    print(" <=3 km:", (j.d<=3000).sum(), " <=10 km:", (j.d<=10000).sum(), " >10 km:", (j.d>10000).sum())
    if name == "completo":
        far = j[j.d>10000]
        print(far.assign(lon=far.geometry.x if False else 0).head(0))
        ff = far.to_crs(4326)
        print(pd.DataFrame({"lon":ff.geometry.x.round(2),"lat":ff.geometry.y.round(2),"d_km":(far.d/1000).round(0), "estado":far.shapeName}).sort_values("d_km").tail(15).to_string())
