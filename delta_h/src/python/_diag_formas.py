"""Diagnóstico v2 — compara as formas de ΔH com a concordância CALCULADA POR FORMA
(bug da v1: usava z_H em todas as linhas) + taxas de corte de winsorização.

Uso: python _diag_formas.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, rankdata, spearmanr

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RES = Path(__file__).resolve().parents[2] / "results"
q = lambda x, p: float(np.nanpercentile(x, p))  # noqa: E731


def main() -> int:
    df = pd.read_csv(RES / "delta_curves_p75.csv", encoding="utf-8-sig")

    nz = df["z_H"].abs() > 1e-9
    sigma = pd.Series(np.nan, index=df.index)
    sigma[nz] = df.loc[nz, "delta_H"] / df.loc[nz, "z_H"].abs()

    print("=" * 120)
    print("NATUREZA DAS LINHAS COM z = 0 (4,4%) — empate exato ou sigma nulo?")
    print("=" * 120)
    z0 = df[~nz]
    print(f"   n(z=0) = {len(z0)}   das quais delta_H == 0 (empate exato de H): "
          f"{int((z0['delta_H'] < 1e-9).sum())}")
    print(f"   delta_H > 0 mas sigma_ref nulo: {int((z0['delta_H'] >= 1e-9).sum())}")
    if int((z0["delta_H"] >= 1e-9).sum()):
        print("   -> essas linhas PERDEM informacao no z (H diferente, z=0)")

    formas = {}
    formas["1. dH bruto"] = df["delta_H"]
    formas["2. z_H"] = df["z_H"]
    formas["3. dH_norm"] = df["delta_H_norm"]
    for c in [5, 8, 10]:
        formas[f"4.{c}. z winsor +/-{c}"] = df["z_H"].clip(-c, c)
    formas["5. z log-modulus sign(z)*ln(1+|z|)"] = np.sign(df["z_H"]) * np.log1p(df["z_H"].abs())
    formas["6. dH/sigma_med_obra"] = df["delta_H"] / sigma.groupby(df["obra"]).transform("median")
    formas["7. rank-normal z dentro da obra"] = df.groupby("obra")["z_H"].transform(
        lambda s: norm.ppf((rankdata(s) - 0.5) / len(s)))

    print("\n" + "=" * 120)
    print(f"COMPARAÇÃO DAS FORMAS  (n = {len(df)})")
    print("=" * 120)
    print(f"{'forma':<40}{'q1':>9}{'q50':>9}{'q99':>9}{'max':>9}"
          f"{'cort%':>7}{'dpObras':>9}{'rho_dB':>9}{'rho_dH':>9}{'rho_zH':>9}")
    print("-" * 120)
    for nome, s in formas.items():
        med_obra = s.groupby(df["obra"]).median()
        rho_db = spearmanr(s, df["delta_dB"])[0]
        rho_dh = np.mean([spearmanr(s[df["obra"] == o],
                                    df.loc[df["obra"] == o, "delta_H"])[0]
                          for o in med_obra.index])
        rho_zh = spearmanr(s, df["z_H"])[0]
        # taxa de corte: fracao de linhas no topo/cauda que uma winsor +/-5 cortaria
        cort = float((df["z_H"].abs() > 5).mean()) if nome.startswith(("2.", "4.", "5.")) else float("nan")
        print(f"{nome:<40}{q(s,1):>9.3f}{q(s,50):>9.3f}{q(s,99):>9.3f}"
              f"{s.abs().max():>9.2f}{cort:>7.1%}{med_obra.std():>9.3f}"
              f"{rho_db:>+9.3f}{rho_dh:>+9.3f}{rho_zh:>+9.3f}")
    print("-" * 120)
    print("cort% = fracao com |z|>5 (o que uma winsor +/-5 cortaria); dpObras =")
    print("dp das medianas por obra (0 = apaga a variacao entre obras); rho_dB =")
    print("concordancia com a confirmatoria (queremos |rho| alto); rho_dH =")
    print("monotonia dentro da obra (queremos |rho| ~ 1).")

    print("\n" + "=" * 120)
    print("CONCORDÂNCIA POR OBRA (regra de união-interseção, NT-01 §5): todas precisam passar")
    print("=" * 120)
    print(f"{'obra':<24}{'n':>7}{'med z':>9}{'P(z<0)':>9}{'med dH':>10}"
          f"{'med dB':>9}{'rho(z,dB)':>11}{'regra':>8}")
    todos_ok = True
    for o, sub in df.groupby("obra"):
        rho = spearmanr(sub["z_H"], sub["delta_dB"])[0]
        frac = float((sub["z_H"] < 0).mean())
        ok = (frac > 0.5) and (sub["delta_dB"].median() > 0) and (rho < 0)
        todos_ok &= ok
        print(f"{o:<24}{len(sub):>7}{sub['z_H'].median():>+9.3f}{frac:>9.1%}"
              f"{sub['delta_H'].median():>10.5f}{sub['delta_dB'].median():>9.3f}"
              f"{rho:>+11.3f}{'SIM' if ok else 'NAO':>8}")
    print(f"\n  as 9/9 obras passam a regra: {'SIM' if todos_ok else 'NAO'}")

    # teste de sinal por obra (binomial: frac z<0 > 0.5 ?)
    print("\n" + "=" * 120)
    print("TESTE DE SINAL POR OBRA (H0: mediana z = 0; exato de binomial, direcao z<0)")
    print("=" * 120)
    from scipy.stats import binomtest
    for o, sub in df.groupby("obra"):
        k = int((sub["z_H"] < 0).sum())
        n = int((sub["z_H"] != 0).sum())
        p = binomtest(k, n, 0.5, alternative="greater").pvalue
        print(f"   {o:<24} {k}/{n} = {k/n:.1%}   p = {p:.3e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
