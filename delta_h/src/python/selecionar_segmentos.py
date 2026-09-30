"""Delta H — seleção estratificada de trechos para o estudo com leitores.

NT-01 §6.6: dentro de cada obra, escolher trechos dos extremos de Δ_gap —
transforma a correlação observacional num contraste quase-experimental
(grupos alto/baixo gap), com muito mais poder.

Regras operacionalizadas (decididas na NT-02 a partir do piloto):

1. **Só segmentos completos.** O trecho congelado tem 4 000–6 000 palavras;
   o último segmento de cada obra costuma ser uma cauda (< 4 000 palavras) e
   NÃO entra no estudo (caudas têm n_sentencas minúsculo e σ_ref instável).

2. **Extremos top-k, não quartis.** NT-01 §6.6 pedia quartis; com 5–6 segmentos
   por obra o quartil tem 1–2 elementos (grupos estatisticamente vazios).
   Seleciona-se os `k` maiores e os `k` menores |z_H| dentro da obra — para
   obras grandes isso equivale aos quartis (k=3 de 16 ≈ 19º percentil), para
   obras pequenas vira metades. A ordem por |z_H| é idêntica à ordem por
   Δ_gap = ln(1+|z_H|) (transformada monotônica), então a seleção é robusta
   à escolha final da forma da métrica.

3. **Métrica = |z_H|** (gap padronizado assinado, em magnitude): a forma
   congelada na NT-02 §8.

Saída: results/segmentos_selecionados_{L}pal_p{eps}.csv
  (colunas do segmento + grupo 'gap_alto' | 'gap_baixo' + covariáveis, se
   results/covariaveis_{L}pal_p{eps}.csv existir)

Uso:
  python selecionar_segmentos.py --largura 4000 \
      --obras alice_wonderland metamorphosis dom_casmurro \
              memorias_braz_cubas ulysses quincas_borba \
      --por-obra 3 --extra ulysses=4
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from delta_h_pipeline import carregar_obras  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RES = Path(__file__).resolve().parents[2] / "results"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--largura", type=int, default=4000,
                    help="largura do trecho em palavras (faixa congelada 4000-6000)")
    ap.add_argument("--eps", type=int, default=75)
    ap.add_argument("--por-obra", type=int, default=3,
                    help="pares (alto, baixo) por obra — padrão 3 = 6 segmentos")
    ap.add_argument("--extra", nargs="*", default=[],
                    help="exceções obra=k, ex.: ulysses=4")
    ap.add_argument("--obras", nargs="*", default=None)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    src = RES / f"segmentos_{args.largura}pal_p{args.eps}.csv"
    if not src.exists():
        sys.exit(f"{src.name} não existe — rode antes:\n"
                 f"  delta_h_pipeline.py --segmentos {args.largura} "
                 f"--eps-pct {args.eps}")
    df = pd.read_csv(src, encoding="utf-8-sig")
    if args.obras:
        df = df[df["obra"].isin(args.obras)].copy()
    if not len(df):
        sys.exit("nenhum segmento para as obras pedidas")

    # --- regra 1: só segmentos completos (>= largura palavras até o fim da obra)
    obras_txt = carregar_obras(sorted(df["obra"].unique()))
    total = {s: sum(len(x.split()) for x in obras_txt[s]["sentencas"])
             for s in obras_txt}
    df["palavra_fim"] = df["palavra_ini"] + args.largura
    df["n_pal_obra"] = df["obra"].map(total)
    n_tudo = len(df)
    df = df[df["palavra_fim"] <= df["n_pal_obra"]].copy()
    caudas = n_tudo - len(df)

    # --- métrica de estratificação (magnitude do gap padronizado)
    df["abs_z"] = df["z_H"].abs()

    # --- covariáveis, se já calculadas
    cov = RES / f"covariaveis_{args.largura}pal_p{args.eps}.csv"
    if cov.exists():
        c = pd.read_csv(cov, encoding="utf-8-sig")
        cols = ["obra", "janela_idx", "palavras_por_frase", "ttr", "freq_log",
                "vocabulario_raro_frac", "aspas_cem"]
        df = df.merge(c[cols], on=["obra", "janela_idx"], how="left")

    # --- regra 2: extremos top-k por obra (determinístico: ordenação por |z|)
    k_padrao = args.por_obra
    excecoes = dict(x.split("=") for x in args.extra)
    excecoes = {k: int(v) for k, v in excecoes.items()}

    escolhidos, tabela_k = [], []
    for obra, sub in df.groupby("obra"):
        k = excecoes.get(obra, k_padrao)
        k_eff = min(k, len(sub) // 2)
        s = sub.sort_values(["abs_z", "janela_idx"],
                            ascending=[False, True])
        alto = s.head(k_eff)
        baixo = s.tail(k_eff)
        tabela_k.append({"obra": obra, "disponiveis": len(sub),
                         "k": k_eff, "alto": k_eff, "baixo": k_eff})
        escolhidos.append(alto.assign(grupo="gap_alto"))
        escolhidos.append(baixo.assign(grupo="gap_baixo"))
    if not escolhidos:
        sys.exit("nada selecionado")
    out = pd.concat(escolhidos, ignore_index=True).drop_duplicates(
        subset=["obra", "janela_idx"], keep="first")
    out = out.sort_values(["obra", "grupo", "janela_idx"])

    destino = RES / f"segmentos_selecionados_{args.largura}pal_p{args.eps}.csv"
    out.to_csv(destino, index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------------ relatório
    print("=" * 96)
    print(f"SELEÇÃO ESTRATIFICADA — {args.largura} palavras, eps p{args.eps}, "
          f"extremos top-k de |z|")
    print("=" * 96)
    print(f"  descartadas {caudas} caudas (< {args.largura} palavras até o fim "
          f"da obra); disponíveis: {len(df)}")
    print("\n  por obra:")
    print(pd.DataFrame(tabela_k).to_string(index=False))
    tab = (df.groupby("obra")
             .agg(n=("janela_idx", "size"),
                  z_min=("z_H", "min"), z_med=("z_H", "median"),
                  z_max=("z_H", "max"),
                  ddB_med=("delta_dB", "median"))
             .reset_index().sort_values("z_med"))
    print("\n  distribuição (segmentos completos):")
    print(tab.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    print(f"\n  SELECIONADOS: {len(out)} "
          f"({int((out.grupo == 'gap_alto').sum())} alto + "
          f"{int((out.grupo == 'gap_baixo').sum())} baixo)")
    print(out.groupby(["obra", "grupo"]).size().unstack(fill_value=0).to_string())

    # contraste obtido (é ele que gera o poder do desenho)
    a = out[out.grupo == "gap_alto"]["z_H"]
    b = out[out.grupo == "gap_baixo"]["z_H"]
    print(f"\n  contraste: |z| alto mediano = {a.abs().median():.2f} vs "
          f"baixo = {b.abs().median():.2f} "
          f"(razão {a.abs().median() / max(b.abs().median(), 1e-9):.1f}×)")
    print(f"  z assinado: alto {a.median():+.2f} | baixo {b.median():+.2f}")

    # sanidade: grupos não podem diferir sistematicamente em covariáveis (§6.4)
    if "palavras_por_frase" in out.columns:
        print("\n  SANIDADE das covariáveis entre grupos (não devem diferir):")
        from scipy.stats import mannwhitneyu
        for c in ["palavras_por_frase", "ttr", "freq_log",
                  "vocabulario_raro_frac"]:
            x = out[out.grupo == "gap_alto"][c].dropna()
            y = out[out.grupo == "gap_baixo"][c].dropna()
            if len(x) > 2 and len(y) > 2:
                p = mannwhitneyu(x, y, alternative="two-sided").pvalue
                flag = "  <-- ATENÇÃO" if p < 0.05 else ""
                print(f"    {c:<24}alto={x.median():.3f} baixo={y.median():.3f}"
                      f"   p = {p:.3f}{flag}")

    # concordância confirmatória nos selecionados (§5: Δd_B deve acompanhar)
    from scipy.stats import spearmanr
    r, p = spearmanr(out["abs_z"], out["delta_dB"])
    print(f"\n  concordância nos selecionados: spearman(|z|, delta_dB) = "
          f"{r:+.3f} (p = {p:.3f})")
    print(f"  % delta_dB>0 (alto) = "
          f"{(out[out.grupo == 'gap_alto'].delta_dB > 0).mean():.0%} | "
          f"(baixo) = {(out[out.grupo == 'gap_baixo'].delta_dB > 0).mean():.0%}")

    faltando = sorted(set(df["obra"]) - set(out["obra"]))
    if faltando:
        print(f"\n  [aviso] obras sem seleção: {faltando}")
    print(f"\n  -> {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
