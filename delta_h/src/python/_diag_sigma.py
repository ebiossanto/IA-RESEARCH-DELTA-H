import sys, numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
RES = Path(r"E:\Users\Euzebio\Desktop\projetos\DeltaH\delta_h\results")
df = pd.read_csv(RES / "delta_curves_p75.csv", encoding="utf-8-sig")
print("colunas:", list(df.columns))
# sigma_ref = |H_obs - H_ref| / |z|  (quando z != 0)
nz = df["z_H"].abs() > 1e-9
sig = df.loc[nz, "delta_H"] / df.loc[nz, "z_H"].abs()
df["sigma_ref"] = np.nan
df.loc[nz, "sigma_ref"] = sig
print("\n-- sigma_ref por obra (mediana) --")
g = df.groupby("obra")["sigma_ref"].agg(["median", "min", "max"])
print(g.to_string(float_format=lambda v: f"{v:.5f}"))
print("\n-- sigma_ref global --")
print(df["sigma_ref"].describe(percentiles=[.01,.05,.25,.5,.75,.95,.99]).to_string(float_format=lambda v: f"{v:.5f}"))
print(f"\nsigma_ref < 0.001: {(df['sigma_ref']<0.001).mean():.4f}   < 0.005: {(df['sigma_ref']<0.005).mean():.4f}")
print(f"z=0 exatamente (sigma>=1e-9, dH<=1e-9?): {(~nz).mean():.4f}")
# cauda: quem tem |z|>5
cauda = df[df["z_H"].abs()>5]
print(f"\n|z|>5: n={len(cauda)} ({len(cauda)/len(df):.3f})  sigma_ref mediano deles: {cauda['sigma_ref'].median():.5f}")
print("obras dominantes na cauda:", cauda["obra"].value_counts().head(4).to_dict())
# alternativas robustas: rank-normalizada
from scipy.stats import rankdata, norm
r = rankdata(df["z_H"])  # dentro de cada obra? vamos nas duas formas
df["z_rank_global"] = norm.ppf((rankdata(df["z_H"])-0.5)/len(df))
df["z_rank_obra"] = df.groupby("obra")["z_H"].transform(lambda s: norm.ppf((rankdata(s)-0.5)/len(s)))
print("\n-- z rank-normalizado (dentro da obra): quantis --")
print(df["z_rank_obra"].describe(percentiles=[.01,.05,.25,.5,.75,.95,.99]).to_string(float_format=lambda v: f"{v:+.3f}"))
# winsorizado
print("\n-- winsorizar z em +/- 4: quantis apos --")
zw = df["z_H"].clip(-4, 4)
print(zw.describe(percentiles=[.01,.05,.5,.95,.99]).to_string(float_format=lambda v: f"{v:+.3f}"))
