"""Delta H — mescla uma rodada parcial (--works) no arquivo completo da MESMA escala.

Corpus parcial é reaproveitado porque as rodadas completas demoram; sem isso o
trabalho de uma rodada parcial seria perdido.

Uso:
    python mesclar_parcial.py --eps 75 --obras memorias_braz_cubas quincas_borba

Arquivos:
    results/delta_curves_p{eps}.csv          <- base (recebe as linhas novas)
    results/delta_curves_parcial_p{eps}.csv  <- só as obras corrigidas
    (idem para controles*.csv e resumo_obras*.json)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RES = Path(__file__).resolve().parents[2] / "results"


def mesclar_df(nome: str, eps: int, obras: list[str]) -> str | None:
    base_p = RES / f"{nome}_p{eps}.csv"
    novo_p = RES / f"{nome}_parcial_p{eps}.csv"
    if not base_p.exists():
        return f"[pula] {base_p.name} não existe"
    if not novo_p.exists():
        return f"[pula] {novo_p.name} não existe"
    base = pd.read_csv(base_p, encoding="utf-8-sig")
    novo = pd.read_csv(novo_p, encoding="utf-8-sig")
    faltando = [o for o in obras if o not in set(novo["obra"])]
    if faltando:
        return f"[ERRO] parcial não contém: {faltando}"
    antes = len(base)
    base = base[~base["obra"].isin(obras)]
    base = pd.concat([base, novo], ignore_index=True)
    ordenar = [c for c in ["obra", "janela_palavras", "janela_idx"]
               if c in base.columns]
    if ordenar:
        base = base.sort_values(ordenar)
    base.to_csv(base_p, index=False, encoding="utf-8-sig")
    removidas = antes - (len(base) - len(novo))
    return (f"[ok] {base_p.name}: {antes} -> {len(base)} linhas "
            f"(-{removidas} antigas de {obras}, +{len(novo)} novas)")


def mesclar_json(eps: int, obras: list[str]) -> str | None:
    base_p = RES / f"resumo_obras_p{eps}.json"
    novo_p = RES / f"resumo_obras_parcial_p{eps}.json"
    if not (base_p.exists() and novo_p.exists()):
        return f"[pula] resumo_obras_p{eps}.json ou o parcial não existe"
    base = json.loads(base_p.read_text(encoding="utf-8"))
    novo = json.loads(novo_p.read_text(encoding="utf-8"))
    base = [r for r in base if r["obra"] not in obras]
    base.extend(novo)
    base_p.write_text(json.dumps(base, ensure_ascii=False, indent=2),
                      encoding="utf-8")
    return f"[ok] {base_p.name}: {len(base)} obras"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eps", type=int, required=True)
    ap.add_argument("--obras", nargs="+", required=True)
    args = ap.parse_args()

    print(f"Mesclando parcial de {args.obras} em escala eps={args.eps}%:")
    for nome in ["delta_curves", "controles"]:
        print("  " + (mesclar_df(nome, args.eps, args.obras) or ""))
    print("  " + (mesclar_json(args.eps, args.obras) or ""))
    # mantém o arquivo "sem sufixo" igual ao da escala 75 (o padrão)
    if args.eps == 75:
        for nome in ["delta_curves.csv", "controles.csv"]:
            src = RES / nome.replace(".csv", "_p75.csv")
            if src.exists():
                (RES / nome).write_bytes(src.read_bytes())
        print("  [ok] delta_curves.csv / controles.csv sincronizados com _p75")
    return 0


if __name__ == "__main__":
    sys.exit(main())
