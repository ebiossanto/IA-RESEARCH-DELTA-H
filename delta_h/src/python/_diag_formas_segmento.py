"""Delta H — comparação das FORMAS candidatas na escala de TRECHO (4000 palavras).

A NT-02 precisa congelar a forma da métrica primária. A NT-01 §6.1 deixou em
aberto (ΔH bruto | ΔH_norm | z_H). A decisão anterior usou a escala de janela;
o estudo com leitores opera em trecho de 4000 palavras — logo a forma deve ser
escolhida NESTA escala (n = segmentos completos, sem caudas < 4000 palavras).

Critérios (todos só-texto):
  1. caudas             -> quantis, |x|>3 (forma precisa ser modelável)
  2. comparabilidade    -> dp das medianas entre obras (Δ deve ser comparável)
  3. concordância       -> |spearman| com Δd_B (métrica confirmatória §5)
  4. monotonicidade     -> rho com ΔH bruto (a forma deve preservar a ordem)
  5. confundimento      -> |rho| com n_sentencas / palavras por frase
                           (§6.4: Δ não pode ser sinônimo de dificuldade léxica)

Uso: python _diag_formas_segmento.py
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
LARGURA = 4000


def carregar() -> pd.DataFrame:
    df = pd.read_csv(RES / f"segmentos_{LARGURA}pal_p75.csv", encoding="utf-8-sig")
    # descarta segmentos-cauda (< LARGURA palavras): o segmento de leitura
    # congelado é 4000-6000 palavras; caudas não entram no estudo
    obras = {}
    txt = Path(__file__).resolve().parents[2] / "data" / "texts"
    for f in txt.glob("*.txt"):
        obras[f.stem] = len(f.read_text(encoding="utf-8", errors="replace").split())
    df["n_pal_obra"] = df["obra"].map(obras)
    df["palavra_fim"] = df["palavra_ini"] + LARGURA
    df["cauda"] = df["palavra_fim"] > df["n_pal_obra"]
    n_t = int(df["cauda"].sum())
    df = df[~df["cauda"]].reset_index(drop=True)
    print(f"segmentos: {len(df) + n_t} -> {len(df)} (descartadas {n_t} caudas "
          f"< {LARGURA} palavras)")
    return df


def formas(df: pd.DataFrame) -> dict[str, pd.Series]:
    # z_H = (H_obs - H_ref)/sigma_ref  =>  sigma_ref = (H_obs - H_ref)/z_H
    sigma = np.where(df["z_H"] != 0,
                     (df["H_obs"] - df["H_ref"]) / df["z_H"], np.nan)
    df["sigma"] = sigma
    dH = df["delta_H"]
    sgn = np.sign(df["H_obs"] - df["H_ref"])
    sig_obra = df.groupby("obra")["sigma"].transform("median")
    out = {
        "1. dH bruto": dH,
        "2. z_H": df["z_H"],
        "3. dH_norm": df["delta_H_norm"],
        "4. z winsor +/-8": df["z_H"].clip(-8, 8),
        "5. z log-mod sign(z)*ln(1+|z|)": sgn * np.log1p(np.abs(df["z_H"])),
        "6. dH/sigma_med_obra": sgn * dH / sig_obra,
    }
    # rank-normal (inverse normal) dentro da obra
    from scipy.stats import norm
    out["7. rank-normal z na obra"] = df.groupby("obra")["z_H"].transform(
        lambda s: norm.ppf((s.rank(method="average") - 0.5) / len(s)))
    return out


def main() -> int:
    df = carregar()
    F = formas(df)
    ddB = df["delta_dB"]
    n_sent = df["n_sentencas"]

    print("\n" + "=" * 118)
    print(f"COMPARAÇÃO DAS FORMAS — escala de TRECHO {LARGURA} palavras (n = {len(df)})")
    print("=" * 118)
    hdr = (f"{'forma':<38}{'q1':>9}{'q50':>9}{'q99':>9}{'max':>9}"
           f"{'|x|>3':>8}{'dpObras':>9}{'|rho|ddB':>10}{'rho_dH':>9}"
           f"{'|rho|nSent':>12}")
    print(hdr)
    print("-" * len(hdr))
    for nome, s in F.items():
        q = s.quantile([.25, .5, .99])
        dp = s.groupby(df["obra"]).median().std()
        r_ddb = spearmanr(s, ddB)[0]
        r_dh = spearmanr(s, df["delta_H"])[0]
        r_ns = spearmanr(s, n_sent)[0]
        print(f"{nome:<38}{q.loc[.25]:>9.3f}{q.loc[.5]:>9.3f}{q.loc[.99]:>9.3f}"
              f"{s.max():>9.3f}{(s.abs() > 3).mean():>8.1%}{dp:>9.3f}"
              f"{abs(r_ddb):>10.3f}{r_dh:>9.3f}{abs(r_ns):>12.3f}")

    print("\n  legenda:")
    print("   • |x|>3      fração de cauda pesada (forma precisa de compressão se alta)")
    print("   • dpObras    dispersão das medianas por obra (comparabilidade entre obras)")
    print("   • |rho|ddB   concordância com a métrica confirmatória (§5) — quanto maior, melhor")
    print("   • rho_dH     monotonicidade com ΔH bruto (preservação da ordem, sinal à parte)")
    print("   • |rho|nSent confundimento com nº de frases (§6.4) — quanto menor, melhor")

    print("\n== DIREÇÃO DO SINAL NA ESCALA DE TRECHO ==")
    print(f"   % z>0 = {(df['z_H'] > 0).mean():.1%}   mediana z = {df['z_H'].median():+.3f}")
    print(f"   % delta_dB>0 = {(ddB > 0).mean():.1%}  mediana delta_dB = {ddB.median():+.4f}")
    print(f"   % delta_H sign(H_obs-H_ref)>0 = "
          f"{(np.sign(df.H_obs - df.H_ref) > 0).mean():.1%}")
    print(f"   n_barras obs vs ref (mediana): "
          f"{df.n_barras_obs.median():.0f} vs {df.n_barras_ref.median():.0f}")

    print("\n== MEDIANA DAS FORMAS PRINCIPAIS POR OBRA ==")
    tab = df.groupby(["obra"]).agg(
        z=("z_H", "median"), dH=("delta_H", "median"),
        ddB=("delta_dB", "median"), n=("z_H", "size"),
        nSent=("n_sentencas", "median")).sort_values("z")
    print(tab.to_string(float_format=lambda v: f"{v:.3f}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
