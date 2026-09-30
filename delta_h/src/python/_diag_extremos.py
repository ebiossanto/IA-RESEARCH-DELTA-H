"""Diagnóstico dos extremos: |z_H| grande é segmento narrativo real ou lixo
residual do Gutenberg (Índice/TOC)?  Imprime o texto das janelas mais extremas.

Uso: python _diag_extremos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from delta_h_pipeline import carregar_obras, janelas_por_palavras  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RES = Path(__file__).resolve().parents[2] / "results"


def main() -> int:
    df = pd.read_csv(RES / "delta_curves_p75.csv", encoding="utf-8-sig")
    slugs = sorted(df["obra"].unique())
    obras = carregar_obras(slugs)

    print("=" * 110)
    print("1. ONDE ESTÃO AS JANELAS EXTREMAS (|z| > 20)?")
    print("=" * 110)
    ext = df[df["z_H"].abs() > 20].copy()
    ext["ultima"] = 0
    for slug, sub in ext.groupby("obra"):
        mx = df[df["obra"] == slug]["janela_idx"].max()
        ext.loc[sub.index, "ultima"] = (sub["janela_idx"] == mx).astype(int)
    print(f"   n(|z|>20) = {len(ext)} de {len(df)} ({len(ext)/len(df):.2%})")
    if len(ext):
        print("   por obra:", ext["obra"].value_counts().to_dict())
        print(f"   fração que é a ÚLTIMA janela da obra (suspeita de TOC/rodapé): "
              f"{ext['ultima'].mean():.1%}")

    print("\n" + "=" * 110)
    print("2. CONTEÚDO DAS 2 JANELAS MAIS EXTREMAS DE CADA OBRA")
    print("=" * 110)
    for slug in slugs:
        sub = df[df["obra"] == slug].copy()
        sub["absz"] = sub["z_H"].abs()
        top = sub.nlargest(2, "absz")
        janelas_cache = {}
        print(f"\n--- {slug} ---")
        for _, r in top.iterrows():
            L = int(r["janela_palavras"])
            if L not in janelas_cache:
                janelas_cache[L] = janelas_por_palavras(obras[slug]["sentencas"], L)
            js = janelas_cache[L]
            idx = int(r["janela_idx"])
            w = js[idx] if idx < len(js) else None
            print(f"   janela {idx:>4} | {L} pal | n_sent={int(r['n_sentencas']):>3} | "
                  f"z={r['z_H']:+9.2f} | dH={r['delta_H']:.4f} | "
                  f"ultima_da_obra={int(idx == sub['janela_idx'].max())}")
            if w:
                txt = " ".join(obras[slug]["sentencas"][i] for i in w["sentencas"])
                print(f"      INÍCIO: {txt[:150]!r}")
                print(f"      FIM   : {txt[-100:]!r}")

    print("\n" + "=" * 110)
    print("3. SÍNTESE: extremos são concentrados no fim do arquivo? (limite de "
          "limpeza do Gutenberg)")
    print("=" * 110)
    for slug, sub in df.groupby("obra"):
        mx = sub["janela_idx"].max()
        tail = sub[sub["janela_idx"] >= mx - 1]
        zmax = sub["z_H"].abs().max()
        frac_tail = (tail["z_H"].abs() > 20).sum() / max(1, (sub["z_H"].abs() > 20).sum()) \
            if (sub["z_H"].abs() > 20).any() else np.nan
        print(f"   {slug:<24} |z|max={zmax:>8.1f}   extremos nas 2 últimas janelas: "
              f"{frac_tail if not np.isnan(frac_tail) else 0:.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
