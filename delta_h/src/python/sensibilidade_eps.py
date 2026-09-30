"""Delta H — sensibilidade à escala ε (percentil da MST), exigida por NT-01 §9.

Compara results/delta_curves_p50.csv, _p75.csv e _p90.csv:
  * janelas são alinháveis 1:1 (mesma segmentação em todas as escalas);
  * correlação de Spearman do z_H entre escalas (a forma precisa ser estável);
  * concordância de SINAL (frac. de janelas com o mesmo sinal);
  * medianas por obra em cada escala;
  * medianas dos controles (C1/C2) por escala.

Uso: python sensibilidade_eps.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RES = Path(__file__).resolve().parents[2] / "results"
ESCALAS = [50, 75, 90]
CHAVES = ["obra", "janela_palavras", "janela_idx"]


def carregar(eps: int) -> pd.DataFrame | None:
    p = RES / f"delta_curves_p{eps}.csv"
    if not p.exists():
        print(f"  [falta] {p.name}")
        return None
    df = pd.read_csv(p, encoding="utf-8-sig")
    df["_eps"] = eps
    return df


def main() -> int:
    print("=" * 100)
    print("SENSIBILIDADE À ESCALA ε (percentil da MST por obra)")
    print("=" * 100)
    dados = {e: carregar(e) for e in ESCALAS}
    dados = {e: d for e, d in dados.items() if d is not None}
    if len(dados) < 2:
        sys.exit("preciso de ao menos 2 escalas completas em results/")

    print("\n1. TAMANHO DAS ESCALAS")
    for e, d in dados.items():
        print(f"   eps_p{e}: {len(d)} janelas, {d['obra'].nunique()} obras, "
              f"eps_mediano={d['eps'].median():.3f}")

    # --- pares 1:1 ---------------------------------------------------------
    print("\n2. ESTABILIDADE DA FORMA ENTRE ESCALAS (janelas alinháveis 1:1)")
    print(f"   {'par':<14}{'n':>7}{'rho(z)':>10}{'rho(dH)':>10}"
          f"{'%mesmo sinal':>14}{'|Δz| med':>10}")
    escalas = sorted(dados)
    for i, a in enumerate(escalas):
        for b in escalas[i + 1:]:
            m = dados[a].merge(dados[b], on=CHAVES, suffixes=("_a", "_b"))
            if not len(m):
                continue
            r_z = spearmanr(m["z_H_a"], m["z_H_b"])[0]
            r_d = spearmanr(m["delta_H_a"], m["delta_H_b"])[0]
            mesma = (np.sign(m["z_H_a"]) == np.sign(m["z_H_b"])).mean()
            dz = (m["z_H_a"] - m["z_H_b"]).abs().median()
            print(f"   {f'p{a} vs p{b}':<14}{len(m):>7}{r_z:>10.3f}{r_d:>10.3f}"
                  f"{mesma:>14.1%}{dz:>10.3f}")

    print("\n3. MEDIANA DE z_H POR OBRA EM CADA ESCALA")
    tab = None
    for e in escalas:
        g = (dados[e].groupby("obra")["z_H"].median().rename(f"z_p{e}"))
        tab = g.to_frame() if tab is None else tab.join(g, how="outer")
    tab = tab.reset_index()
    print(tab.to_string(index=False, float_format=lambda v: f"{v:+.3f}"))
    cols = [c for c in tab.columns if c != "obra"]
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            r = spearmanr(tab[a], tab[b])[0]
            print(f"   rank entre obras {a} x {b}: rho = {r:+.3f}")

    print("\n4. CONTROLES POR ESCALA (janela 250)")
    for e in ESCALAS:
        p = RES / f"controles_p{e}.csv"
        if not p.exists():
            continue
        c = pd.read_csv(p, encoding="utf-8-sig")
        linhas = []
        for nome in ["C1_salad", "C2_ref_mc"]:
            sub = c[c["controle"] == nome]
            if len(sub):
                linhas.append(f"{nome}: dH={sub['delta_H'].median():.5f} "
                              f"z={sub['z_H'].median():+.3f}")
        real_p = RES / f"delta_curves_p{e}.csv"
        if real_p.exists():
            r = pd.read_csv(real_p, encoding="utf-8-sig")
            r = r[r["janela_palavras"] == 250]
            linhas.insert(0, f"real: dH={r['delta_H'].median():.5f} "
                             f"z={r['z_H'].median():+.3f}")
        print(f"   eps_p{e}: " + " | ".join(linhas))

    print("\n5. LEITURA")
    print("   • rho(z) entre escalas alto e %mesmo-sinal alta => a forma é estável")
    print("     à escala, e o valor congelado (p75) não é um artefato do percentil.")
    print("   • queda de rho => a escala importa; nesse caso a NT-02 precisa congelar")
    print("     formalmente o percentil (p75) e reportar as 3 escalas.")
    print("   • NOTE: p50/p75/p90 com obras de corpus divergente não casam 1:1;")
    print("     rode de novo após mesclar a rodada parcial da escala em questão.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
