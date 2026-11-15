import sys, glob, os
import pandas as pd
d = sys.argv[1]
for pat in ["modis_bb_2005", "modis_bb_2026", "viirs_snpp_bb_2012", "viirs_snpp_bb_2025"]:
    f = os.path.join(d, pat + ".parquet")
    df = pd.read_parquet(f)
    print("=====", pat, df.shape)
    print(df.dtypes)
    print(df.head(3).to_string())
    print(df.describe(include="all").T.head(30).to_string())
