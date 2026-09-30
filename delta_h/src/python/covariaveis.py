"""Delta H — covariáveis de dificuldade léxica por segmento (NT-01 §6.4).

§6.4: "Uma janela com vocabulário raro, sintaxe longa ou baixa frequência é
difícil independentemente de topologia." Sem essas covariáveis no modelo, o efeito
de Δ sobre a compreensão é confundido.

Calcula, para cada segmento de results/segmentos_{L}pal_p{eps}.csv:

  palavras, n_sentencas, palavras_por_frase   (sintaxe longa)
  ttr, guiraud                               (diversidade léxica)
  freq_log                                   (log10 frequência por milhão no
                                              corpus — proxy externo barato;
                                              trocar por SUBTLEX no pré-registro
                                              se disponível)
  aspas_cem, maiusculas_cem                   (fração de discurso direto / nominal)
  vocabulario_raro_frac                       (fração de tokens com freq < 10/milhão
                                              no corpus)

O recorte do texto usa os MESMOS offsets de palavra do pipeline (contagem por
`s.split()` sobre as frases), então casa exatamente com o segmento medido.

Saída: results/covariaveis_{L}pal_p{eps}.csv  (colunas do segmento + covariáveis)

Uso: python covariaveis.py --largura 4000 --eps 75
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from delta_h_pipeline import carregar_obras  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RES = Path(__file__).resolve().parents[2] / "results"
_PALAVRA = re.compile(r"[^\W\d_]+", re.UNICODE)
_MAIUSCULA = re.compile(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ]")


def tokens(texto: str) -> list[str]:
    return [t.lower() for t in _PALAVRA.findall(texto)]


def sentencas_do_segmento(sentencas: list[str], ini: int, fim: int) -> list[str]:
    """Frases cuja faixa de palavras intersecta [ini, fim) (mesma contagem do pipeline)."""
    saida, pos = [], 0
    for s in sentencas:
        n = len(s.split())
        if pos + n > ini and pos < fim:
            saida.append(s)
        pos += n
        if pos >= fim:
            break
    return saida


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--largura", type=int, default=4000)
    ap.add_argument("--eps", type=int, default=75)
    args = ap.parse_args()

    src = RES / f"segmentos_{args.largura}pal_p{args.eps}.csv"
    if not src.exists():
        sys.exit(f"{src.name} não existe — rode antes o modo --segmentos")
    seg = pd.read_csv(src, encoding="utf-8-sig")

    obras = carregar_obras(sorted(seg["obra"].unique()))
    textos = {s: " ".join(obras[s]["sentencas"]) for s in obras}

    # frequência do corpus (proxy de frequência externa) — uma vez, para tudo
    conta = Counter()
    for s, txt in textos.items():
        conta.update(tokens(txt))
    total = sum(conta.values())
    ppm = {t: c / total * 1e6 for t, c in conta.items()}
    RARO_PPM = 10.0           # < 10 ocorrências por milhão = raro no corpus

    # palavra_fim por deslocamento do segmento seguinte (igual ao seletor)
    fim_por_chave = {}
    for obra, sub in seg.sort_values("janela_idx").groupby("obra"):
        inis = list(sub["palavra_ini"])
        idxs = list(sub["janela_idx"])
        L = args.largura
        for i, (ii, j) in enumerate(zip(inis, idxs)):
            fim_por_chave[(obra, j)] = inis[i + 1] if i + 1 < len(inis) else ii + L

    out = []
    for _, r in seg.iterrows():
        chave = (r["obra"], r["janela_idx"])
        frases = sentencas_do_segmento(obras[r["obra"]]["sentencas"],
                                       int(r["palavra_ini"]), fim_por_chave[chave])
        txt = " ".join(frases)
        tk = tokens(txt)
        n = len(tk)
        tipos = len(set(tk))
        freqs = [ppm.get(t, 0.0) for t in tk]
        logf = [math.log10(f) for f in freqs if f > 0]
        out.append({
            "palavras": n,
            "palavras_por_frase": n / max(1, int(r["n_sentencas"])),
            "ttr": tipos / max(1, n),
            "guiraud": tipos / math.sqrt(max(1, n)),
            "freq_log": sum(logf) / len(logf) if logf else 0.0,
            "vocabulario_raro_frac": sum(1 for f in freqs if f < RARO_PPM) / max(1, n),
            "aspas_cem": 100.0 * sum(txt.count(c) for c in "“”«»\"") / max(1, n),
            "maiusculas_cem": 100.0 * sum(1 for t in _PALAVRA.findall(txt)
                                          if _MAIUSCULA.match(t)) / max(1, n),
        })

    res = pd.concat([seg.reset_index(drop=True), pd.DataFrame(out)], axis=1)
    destino = RES / f"covariaveis_{args.largura}pal_p{args.eps}.csv"
    res.to_csv(destino, index=False, encoding="utf-8-sig")

    print("=" * 96)
    print(f"COVARIÁVEIS (NT-01 §6.4) — {args.largura} palavras, eps p{args.eps}")
    print("=" * 96)
    cols = ["palavras", "palavras_por_frase", "ttr", "guiraud", "freq_log",
            "vocabulario_raro_frac", "aspas_cem", "maiusculas_cem"]
    print(res[cols].describe(percentiles=[.25, .5, .75])
          .to_string(float_format=lambda v: f"{v:.4f}"))
    print(f"\n  n segmentos = {len(res)}   -> {destino.name}")
    # correlação com Δ: se |rho| baixo, Δ não está só medindo dificuldade léxica
    from scipy.stats import spearmanr
    print("\n  Spearman com z_H (coluna de Δ) — se |rho| baixo, Δ não é sinônimo "
          "de dificuldade léxica:")
    for c in ["palavras_por_frase", "ttr", "freq_log", "vocabulario_raro_frac",
              "aspas_cem"]:
        r, p = spearmanr(res[c], res["z_H"])
        print(f"    {c:<24}{r:>+.3f}   (p = {p:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
