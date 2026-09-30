"""Diagnóstico rápido: por que poucas janelas / diagrama vazio? (uso interno)"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from delta_h_pipeline import (                      # noqa: E402
    GLOBAL_SUBSAMPLE,
    carregar_obras,
    diagrama,
    dividir_sentencas,
    escala_mst,
    estatisticas,
    janelas_por_palavras,
    obter_embeddings,
)

obras = carregar_obras(["perolas_infantis", "dom_casmurro"])
for slug, obra in obras.items():
    sents = obra["sentencas"]
    print("=" * 70)
    print(f"{slug}: {len(sents)} sentencas, "
          f"{sum(len(s.split()) for s in sents)} palavras")

    tams = np.array([len(s.split()) for s in sents])
    print(f"  palavras/frase: min={tams.min()} p25={np.percentile(tams,25):.0f} "
          f"med={np.median(tams):.0f} p75={np.percentile(tams,75):.0f} "
          f"p95={np.percentile(tams,95):.0f} max={tams.max()}")
    print(f"  3 sentencas mais longas: {sorted(tams)[-3:]}")
    print(f"  exemplo curta: {min(sents, key=lambda s: len(s.split()))[:80]!r}")
    print(f"  exemplo longa: {max(sents, key=lambda s: len(s.split()))[:140]!r}")

    for L in (150, 250, 400):
        js = janelas_por_palavras(sents, L)
        ns = [len(w["sentencas"]) for w in js]
        print(f"  janelas de {L:>3} pal: {len(js):>4} | sentencas/janela: "
              f"min={min(ns) if ns else 0} med={int(np.median(ns)) if ns else 0} "
              f"max={max(ns) if ns else 0} | <4 sentencas: "
              f"{sum(1 for n in ns if n < 4)}")

    emb = obter_embeddings(slug, sents, "tfidf")
    print(f"  embeddings: {emb.shape}")
    rng = np.random.default_rng(42)
    idx = rng.choice(len(emb), size=min(GLOBAL_SUBSAMPLE, len(emb)), replace=False)
    Xg = emb[idx]
    eps, diag = escala_mst(Xg, 75)
    print(f"  eps(75%MST)={eps:.4f} | frac de pares conectados={diag['frac_pares']:.3f}")
    dg = diagrama(Xg, eps)
    for k, iv in dg.items():
        print(f"  H{k}: {iv.shape[0]} barras" +
              (f" | ex.: {iv[:3].round(3).tolist()}" if iv.size else ""))
    est = estatisticas(dg, eps)
    print(f"  H={est['H']:.4f} C={est['C']:.3f} Cpers={est['Cpers']:.3f} "
          f"beta={est['beta']}")
