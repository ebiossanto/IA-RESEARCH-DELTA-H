"""Delta H — figuras do artigo a partir de results/delta_curves.csv.

Uso:
    python fazer_figuras.py

Saídas (paper/figures/):
    delta_h_curvas.png    ΔH e z_H por obra x largura de janela
    delta_h_metricas.png  comparação entre as 4 candidatas (ΔH, d_B, ΔT, ΔT^pers)
    delta_h_controles.png contrroles C1/C2, se results/controles.csv existir

Tudo em 300 dpi, rótulos em português, sem dependência de LaTeX.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as  plt                      # noqa: E402
import numpy as np                                    # noqa: E402
import pandas as pd                                   # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "results"
FIG_DIR = ROOT / "paper" / "figures"

ORDEM_NIVEL = ["simples", "intermediario", "complexo"]
CORES = {150: "#4C78A8", 250: "#F58518", 400: "#54A24B"}
ROTULO_NIVEL = {"simples": "simples", "intermediario": "intermediário",
                "complexo": "complexo"}


def carregar(caminho: Path) -> pd.DataFrame:
    if not caminho.exists():
        sys.exit(f"{caminho} não existe — rode antes o delta_h_pipeline.py")
    df = pd.read_csv(caminho, encoding="utf-8-sig")
    df["nivel"] = pd.Categorical(df["nivel"], ORDEM_NIVEL, ordered=True)
    return df.sort_values(["nivel", "obra", "janela_palavras", "janela_idx"])


def ordenar_obras(df: pd.DataFrame) -> list[str]:
    tmp = (df[["nivel", "obra"]].drop_duplicates()
           .sort_values(["nivel", "obra"]))
    return list(tmp["obra"])


def _eixo_x(df: pd.DataFrame, ax) -> list[str]:
    obras = ordenar_obras(df)
    ax.set_xticks(range(len(obras)))
    ax.set_xticklabels([o.replace("_", "\n") for o in obras], fontsize=7)
    return obras


def figura_curvas(df: pd.DataFrame) -> Path:
    fig, eixos = plt.subplots(1, 2, figsize=(13.5, 4.6), constrained_layout=True)

    for ax, col, titulo, ylabel in [
        (eixos[0], "delta_H", r"$\Delta H = |H_{obs} - H_{ref}|$  (bruto)",
         "gap de entropia persistente"),
        (eixos[1], "z_H", r"$z_H = (H_{obs} - H_{ref})\,/\,\sigma_{ref}$",
         "gap padronizado (desvios-padrão)"),
    ]:
        obras = ordenar_obras(df)
        larguras = sorted(df["janela_palavras"].unique())
        larg = 0.8 / max(1, len(larguras))
        for k, L in enumerate(larguras):
            dados = [df[(df["obra"] == o) & (df["janela_palavras"] == L)][col].values
                     for o in obras]
            pos = np.arange(len(obras)) - 0.4 + larg * (k + 0.5)
            bp = ax.boxplot(dados, positions=pos, widths=larg * 0.9,
                            patch_artist=True, manage_ticks=False, showfliers=False)
            for b in bp["boxes"]:
                b.set(facecolor=CORES.get(L, "gray"), alpha=0.75, linewidth=0)
            for med in bp["medians"]:
                med.set(color="black", linewidth=1.1)
        ax.axhline(0, color="0.5", lw=0.8, ls="--")
        ax.set_title(titulo, fontsize=10)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(axis="y", color="0.9", lw=0.6)
        _eixo_x(df, ax)
        alca = [plt.Line2D([0], [0], marker="s", ls="", ms=7,
                           color=CORES.get(L, "gray"),
                           label=f"{L} palavras") for L in larguras]
        ax.legend(handles=alca, fontsize=7, loc="upper right", frameon=False)

    fig.suptitle("Gap topológico por obra — métrica primária ΔH "
                 "(referência casada por tamanho, NT-01 §6.1)", fontsize=11)
    destino = FIG_DIR / "delta_h_curvas.png"
    fig.savefig(destino, dpi=300)
    plt.close(fig)
    return destino


def figura_metricas(df: pd.DataFrame) -> Path:
    fig, eixos = plt.subplots(1, 3, figsize=(13.5, 4.2), constrained_layout=True)

    # (a) ΔH bruto vs ΔH normalizado — mostra o efeito da concentração de distâncias
    ax = eixos[0]
    amostra = df[df["janela_palavras"] == 250]
    ax.scatter(amostra["H_norm_obs"], amostra["delta_H_norm"], s=9,
               alpha=0.5, color=CORES[250], linewidths=0)
    ax.set_xlabel(r"$H^{norm}_{obs} = H/\ln(\#\text{barras})$")
    ax.set_ylabel(r"$\Delta H^{norm}$")
    ax.set_title("(a) entropia normalizada", fontsize=10)
    ax.grid(color="0.9", lw=0.6)

    # (b) ΔT é discreto e de faixa estreita (Prop. 1 da NT-01)
    ax = eixos[1]
    for nivel, cor in zip(ORDEM_NIVEL, ["#4C78A8", "#F58518", "#54A24B"]):
        sub = amostra[amostra["nivel"] == nivel]
        if len(sub):
            ax.scatter(sub["z_H"], sub["delta_T"], s=9, alpha=0.5, color=cor,
                       linewidths=0, label=ROTULO_NIVEL[nivel])
    ax.axhline(0, color="0.5", lw=0.8, ls="--")
    ax.set_xlabel(r"$z_H$ (primária)")
    ax.set_ylabel(r"$\Delta T = C_{obs} - C_{ref}$")
    ax.set_title(r"(b) $\Delta T$ contra a primária", fontsize=10)
    ax.legend(fontsize=7, frameon=False)
    ax.grid(color="0.9", lw=0.6)

    # (c) confirmatória: excedente de bottleneck
    ax = eixos[2]
    ax.scatter(amostra["z_H"], amostra["delta_dB"], s=9, alpha=0.5,
               color="#B279A2", linewidths=0)
    ax.axhline(0, color="0.5", lw=0.8, ls="--")
    ax.set_xlabel(r"$z_H$ (primária)")
    ax.set_ylabel(r"$\Delta d_B$ (confirmatória)")
    ax.set_title(r"(c) concordância $\Delta H \times d_B$", fontsize=10)
    ax.grid(color="0.9", lw=0.6)

    fig.suptitle("As quatro candidatas lado a lado (janela = 250 palavras)",
                 fontsize=11)
    destino = FIG_DIR / "delta_h_metricas.png"
    fig.savefig(destino, dpi=300)
    plt.close(fig)
    return destino


def figura_controles(df: pd.DataFrame, caminho: Path) -> Path | None:
    if not caminho.exists():
        return None
    ctrl = pd.read_csv(caminho, encoding="utf-8-sig")
    if "delta_H" not in ctrl or not len(ctrl):
        return None

    real = df[df["janela_palavras"] == 250]
    grupos = [("texto real", real)]
    for nome, rotulo in [("C1_salad", "C1: texto-avra"),
                         ("C2_ref_mc", "C2: piso de Monte Carlo")]:
        sub = ctrl[ctrl["controle"] == nome]
        if len(sub):
            grupos.append((rotulo, sub))

    fig, eixos = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    nomes = [g[0] for g in grupos]

    for ax, col, tit in [
        (eixos[0], "delta_H", r"$\Delta H$ (bruto)"),
        (eixos[1], "z_H", r"$z_H$ (padronizado)"),
    ]:
        dados = [g[1][col].dropna().values for g in grupos]
        bp = ax.boxplot(dados, patch_artist=True, manage_ticks=False,
                        showfliers=False, widths=0.55)
        for b, cor in zip(bp["boxes"], ["#4C78A8", "#E45756", "#9D9D9D"]):
            b.set(facecolor=cor, alpha=0.8, linewidth=0)
        for med in bp["medians"]:
            med.set(color="black", linewidth=1.2)
        ax.set_xticks(range(1, len(nomes) + 1))
        ax.set_xticklabels(nomes, fontsize=8)
        ax.axhline(0, color="0.5", lw=0.8, ls="--")
        ax.set_title(tit, fontsize=10)
        ax.grid(axis="y", color="0.9", lw=0.6)

    fig.suptitle("Controles: o gap depende de estrutura narrativa? (janela = 250 palavras)",
                 fontsize=11)
    destino = FIG_DIR / "delta_h_controles.png"
    fig.savefig(destino, dpi=300)
    plt.close(fig)
    return destino


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="figuras do artigo (Delta H)")
    ap.add_argument("--eps", type=int, default=75,
                    help="escala: lê results/delta_curves_p{eps}.csv (padrão 75)")
    args = ap.parse_args()

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    caminho_df = RESULT_DIR / f"delta_curves_p{args.eps}.csv"
    caminho_ctrl = RESULT_DIR / f"controles_p{args.eps}.csv"
    df = carregar(caminho_df)
    print(f"{caminho_df.name}: {len(df)} janelas, {df['obra'].nunique()} obras, "
          f"embedder={df['embedder'].iloc[0]}")

    geradas = [figura_curvas(df), figura_metricas(df),
               figura_controles(df, caminho_ctrl)]
    for g in geradas:
        if g:
            print(f"  -> {g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
