"""Delta H — estatísticas do piloto computacional (Fase 2) para a NT-02.

Lê results/delta_curves_p75.csv + results/controles_p75.csv e imprime tudo que a
NT-02 precisa citar: agregados por obra, heterogeneidade, controles, caudas e
concordância entre a primária (z_H) e a confirmatória (d_B).

Uso:
    python pilot_stats.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results"


def mad(x) -> float:
    """Desvio absoluto mediano (robusto a caudas — o z_H tem caudas longas)."""
    x = np.asarray(x, float)
    return float(np.median(np.abs(x - np.median(x))) * 1.4826)


def main() -> int:
    df = pd.read_csv(RES / "delta_curves_p75.csv", encoding="utf-8-sig")
    ctrl = pd.read_csv(RES / "controles_p75.csv", encoding="utf-8-sig")

    print("=" * 90)
    print("1. DIMENSÃO DA AMOSTRA COMPUTACIONAL")
    print("=" * 90)
    print(f"   obras = {df['obra'].nunique()}  |  janelas = {len(df)}  |  "
          f"tamanhos = {sorted(df['janela_palavras'].unique())}  |  "
          f"embedder = {df['embedder'].iloc[0]}")
    print(f"   faixa de n_sentencas por janela: {df['n_sentencas'].min()} a "
          f"{df['n_sentencas'].max()}")
    print(f"   fração degenerada (<=1 barra): {df['degenerado'].mean():.4f}")

    print("\n" + "=" * 90)
    print("2. POR OBRA (mediana sobre as 3 larguras de janela)")
    print("=" * 90)
    agg = (df.groupby(["nivel", "obra"])
             .agg(n=("delta_H", "size"),
                  dH=("delta_H", "median"),
                  z_med=("z_H", "median"),
                  z_mad=("z_H", mad),
                  frac_z_neg=("z_H", lambda s: (s < 0).mean()),
                  dB=("delta_dB", "median"),
                  dT=("delta_T", "median"))
             .reset_index()
             .sort_values(["nivel", "obra"]))
    print(agg.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    print("\n" + "=" * 90)
    print("3. HETEROGENEIDADE ENTRE OBRAS (é ela que viabiliza o estudo com leitores)")
    print("=" * 90)
    med = agg["z_med"]
    print(f"   mediana de z entre obras: min={med.min():+.3f} "
          f"max={med.max():+.3f} dp={med.std():.3f}")
    print(f"   obra com maior gap : {agg.loc[med.idxmax(), 'obra']} ({med.max():+.3f})")
    print(f"   obra com menor gap : {agg.loc[med.idxmin(), 'obra']} ({med.min():+.3f})")
    nivel = (df.groupby(["nivel", "obra"])["z_H"].median().reset_index()
               .groupby("nivel")["z_H"].agg(["mean", "std", "count"]))
    print("\n   por nível de complexidade (média das medianas de obra):")
    print(nivel.to_string(float_format=lambda v: f"{v:.4f}"))

    print("\n" + "=" * 90)
    print("4. EFEITO DA LARGURA DE JANELA (dentro de cada obra)")
    print("=" * 90)
    janela = (df.groupby("janela_palavras")
                .agg(n=("z_H", "size"),
                     z_med=("z_H", "median"),
                     z_mad=("z_H", mad),
                     dH=("delta_H", "median"),
                     frac_z_neg=("z_H", lambda s: (s < 0).mean()))
                .reset_index())
    print(janela.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    print("\n" + "=" * 90)
    print("5. CONTROLES (janela = 250 palavras)")
    print("=" * 90)
    real = df[df["janela_palavras"] == 250]
    linhas = [("texto real", real)]
    for nome in ["C1_salad", "C2_ref_mc"]:
        sub = ctrl[ctrl["controle"] == nome]
        if len(sub):
            linhas.append((nome, sub))
    for rot, sub in linhas:
        print(f"   {rot:<14} n={len(sub):>5}  dH={sub['delta_H'].median():.5f}  "
              f"z={sub['z_H'].median():+.4f}  MAD(z)={mad(sub['z_H']):.3f}  "
              f"frac_z_neg={(sub['z_H'] < 0).mean():.3f}")
    d_real = real["delta_H"].median()
    d_c1 = ctrl[ctrl["controle"] == "C1_salad"]["delta_H"].median()
    d_c2 = ctrl[ctrl["controle"] == "C2_ref_mc"]["delta_H"].median()
    print(f"\n   razão real/C1 = {d_real / d_c1:.2f}×   "
          f"real/C2 (piso MC) = {d_real / d_c2:.2f}×")
    print(f"   dispersão z: real MAD={mad(real['z_H']):.3f} vs "
          f"C1 MAD={mad(ctrl[ctrl['controle'] == 'C1_salad']['z_H']):.3f} "
          f"-> {mad(real['z_H']) / mad(ctrl[ctrl['controle'] == 'C1_salad']['z_H']):.2f}×")

    print("\n" + "=" * 90)
    print("6. CONCORDÂNCIA PRIMÁRIA x CONFIRMATÓRIA (regra de união-interseção, NT-01 §5)")
    print("=" * 90)
    from scipy.stats import spearmanr
    for col, rot in [("delta_dB", "d_B"), ("delta_T", "ΔT"), ("delta_H_norm", "ΔH_norm")]:
        r, p = spearmanr(df["z_H"], df[col])
        print(f"   spearman(z_H, {rot:<8}) = {r:+.3f}  (p = {p:.2e}, n = {len(df)})")
    # a regra: as duas precisam ser significativas na direção declarada
    print("   direção declarada: janela contígua com MENOR H que a referência "
          "(z_H < 0) e d_B excedente > 0")
    print(f"   frac(janela com z_H<0) = {(df['z_H'] < 0).mean():.3f}")

    print("\n" + "=" * 90)
    print("7. CAUDAS / ROBUSTEZ (o z_H é assimétrico; estatística robusta obrigatória)")
    print("=" * 90)
    for q in [1, 5, 25, 50, 75, 95, 99]:
        print(f"   q{q:>2} z_H = {np.percentile(df['z_H'], q):+.3f}", end="")
        if q == 50:
            print(f"   MAD = {mad(df['z_H']):.3f}", end="")
        print()
    print(f"   |z|>2 = {(df['z_H'].abs() > 2).mean():.3f}  "
          f"|z|>3 = {(df['z_H'].abs() > 3).mean():.3f}")

    print("\n" + "=" * 90)
    print("8. ΔT: CONFIRMAÇÃO DA PROPOSIÇÃO 1 (offset mecânico, não métrica primária)")
    print("=" * 90)
    dt = (df.groupby(["janela_palavras", "n_sentencas"])["delta_T"]
            .median().reset_index())
    print("   correlação entre n_sentencas e ΔT (se ≈ -1, é mecânico):")
    r, p = spearmanr(dt["n_sentencas"], dt["delta_T"])
    print(f"   spearman(n_sentencas, ΔT) = {r:+.3f} (p = {p:.2e}, n = {len(dt)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
