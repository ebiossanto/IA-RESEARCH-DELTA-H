"""Delta H — controles C4 (estabilidade de seed) e C5 (extensão da frase)
definidos em NT-01 §10, mais o teste de sinal já incorporado a pilot_stats.

C4: compara duas rodadas com seeds diferentes (mesma escala, mesmas obras) e
    verifica CV das medianas de Δ entre seeds < 5%.
    Requer: results/delta_curves_p75.csv            (seed 42)
            results/delta_curves_parcial_s123_p75.csv (seed 123)
            (ou --seed2 para outro arquivo/escala)

C5: com os CSVs já gerados, testa se Δ depende do comprimento médio da frase
    (controle de extensão): dentro de cada obra x largura, correlaciona z_H com
    palavras/frase. |rho| pequeno => Δ não é artefato de frases curtas/longas.

Uso: python controles_c4_c5.py [--seed2 results/delta_curves_parcial_s123_p75.csv]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RES = Path(__file__).resolve().parents[2] / "results"


def c5(df: pd.DataFrame) -> None:
    print("=" * 96)
    print("C5 — estabilidade quanto ao comprimento da frase (controle de extensão)")
    print("=" * 96)
    d = df.copy()
    # janelas têm largura fixa em palavras: palavras/frase = largura / n_sentencas
    d["pal_por_frase"] = d["janela_palavras"] / d["n_sentencas"]
    rhos = []
    for (obra, L), sub in d.groupby(["obra", "janela_palavras"]):
        if len(sub) >= 8:
            r = spearmanr(sub["pal_por_frase"], sub["z_H"])[0]
            rhos.append(r)
    rhos = np.array(rhos)
    print(f"   n (obra x largura) = {len(rhos)}")
    print(f"   rho de Spearman(palavras/frase, z_H): mediana = {np.median(rhos):+.3f}, "
          f"|rho| mediano = {np.median(np.abs(rhos)):.3f}, "
          f"máx = {np.max(np.abs(rhos)):.3f}")
    print(f"   grupos com |rho| > 0.3: {int((np.abs(rhos) > 0.3).sum())}/{len(rhos)}")
    # controle global (parcialmente confundido com obra, reportado só como referência)
    r = spearmanr(d["pal_por_frase"], d["z_H"])[0]
    print(f"   rho global (confundido por obra — só referência) = {r:+.3f}")
    print("   critério NT-01: Δ estável => poucos grupos com |rho| > 0.3 e "
          "mediana perto de 0.")


def c4(df1: pd.DataFrame, df2: pd.DataFrame, rot2: str) -> None:
    print("\n" + "=" * 96)
    print("C4 — estabilidade entre seeds (CV das medianas de Δ < 5%)")
    print("=" * 96)
    a = (df1.groupby(["obra", "janela_palavras"])
             .agg(dH=("delta_H", "median"), z=("z_H", "median")).reset_index())
    b = (df2.groupby(["obra", "janela_palavras"])
             .agg(dH=("delta_H", "median"), z=("z_H", "median")).reset_index())
    m = a.merge(b, on=["obra", "janela_palavras"], suffixes=("_s1", "_s2"))
    if not len(m):
        print(f"   [ERRO] nenhuma (obra, largura) em comum com {rot2}")
        return
    m["cv_dH"] = (m["dH_s1"] - m["dH_s2"]).abs() / ((m["dH_s1"] + m["dH_s2"]) / 2)
    m["dz"] = (m["z_s1"] - m["z_s2"]).abs()
    print(m[["obra", "janela_palavras", "dH_s1", "dH_s2", "cv_dH", "z_s1", "z_s2", "dz"]]
          .to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print(f"\n   CV de ΔH: mediana = {m['cv_dH'].median():.2%}, "
          f"máx = {m['cv_dH'].max():.2%}   (critério: < 5%)")
    print(f"   |Δz|: mediana = {m['dz'].median():.3f}, máx = {m['dz'].max():.3f}")
    print(f"   C4 {'PASSA' if m['cv_dH'].max() < 0.05 else 'NÃO PASSA (máx >= 5%)'} "
          f"no critério literal do ΔH bruto")
    print(f"   (arquivo 1 = seed 42; arquivo 2 = {rot2})")

    # --- o que importa para o DESENHO: o RANKING das janelas é reprodutível?  #
    # (a seleção de trechos é por quartis de Δ dentro da obra — se o ranking
    #  muda com a seed, o grupo alto/baixo gap não é reprodutível)
    print("\n   Estabilidade de RANKING (o que a seleção estratificada usa):")
    chaves = ["obra", "janela_palavras", "janela_idx"]
    a2 = df1[chaves + ["z_H", "delta_H"]]
    b2 = df2[chaves + ["z_H", "delta_H"]]
    j = a2.merge(b2, on=chaves, suffixes=("_s1", "_s2"))
    print(f"   {'obra':<24}{'n':>7}{'rho(z)':>10}{'rho(dH)':>10}"
          f"{'quartil concord.':>18}")
    for obra, sub in j.groupby("obra"):
        r_z = spearmanr(sub["z_H_s1"], sub["z_H_s2"])[0]
        r_d = spearmanr(sub["delta_H_s1"], sub["delta_H_s2"])[0]
        q1 = sub["z_H_s1"].quantile([0.25, 0.75])
        g1 = np.where(sub["z_H_s1"] >= q1[0.75], "alto",
                      np.where(sub["z_H_s1"] <= q1[0.25], "baixo", "meio"))
        q2 = sub["z_H_s2"].quantile([0.25, 0.75])
        g2 = np.where(sub["z_H_s2"] >= q2[0.75], "alto",
                      np.where(sub["z_H_s2"] <= q2[0.25], "baixo", "meio"))
        conc = (g1 == g2).mean()
        print(f"   {obra:<24}{len(sub):>7}{r_z:>10.3f}{r_d:>10.3f}{conc:>18.1%}")
    r_z_t = spearmanr(j["z_H_s1"], j["z_H_s2"])[0]
    r_d_t = spearmanr(j["delta_H_s1"], j["delta_H_s2"])[0]
    print(f"   {'TOTAL':<24}{len(j):>7}{r_z_t:>10.3f}{r_d_t:>10.3f}")
    print("   leitura: rho > 0.9 => a estratificação alto/baixo gap é "
          "reprodutível mesmo com a seed mudando.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="results/delta_curves_p75.csv")
    ap.add_argument("--seed2", default="results/delta_curves_parcial_s123_p75.csv")
    ap.add_argument("--rot2", default="seed 123 (parcial)")
    args = ap.parse_args()

    base = Path(__file__).resolve().parents[2] / args.base
    if not base.exists():
        sys.exit(f"{base} não existe")
    df = pd.read_csv(base, encoding="utf-8-sig")
    c5(df)

    p2 = Path(__file__).resolve().parents[2] / args.seed2
    if p2.exists():
        c4(df, pd.read_csv(p2, encoding="utf-8-sig"), args.rot2)
    else:
        print(f"\nC4: arquivo {p2.name} ainda não existe — rode antes a rodada "
              f"--seed 123.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
