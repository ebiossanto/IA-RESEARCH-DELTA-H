# Projeto de Pesquisa: **Delta H**

![Banner](banner.png)

**Título completo:** Delta H — Validação Empírica do Gap Topológico Narrativo (ΔT): Relação entre Estrutura Semântica Global e Compreensão de Leitores

> O nome oficial do trabalho é **Delta H**. Pasta, `README.md`, `paper/main.tex` e o título do documento original já foram corrigidos.

> **Nota:** Este é um projeto de estudos e pesquisa desenvolvido com ferramentas de inteligência artificial. O autor é um estudante, entusiasta e pesquisador.

---

## Citation

Se você usar este software em sua pesquisa, por favor cite:

```bibtex
@software{ia_research_delta_h,
  author = {Soares, Euzébio},
  title = {IA RESEARCH: DELTA H — Validação Empírica do Gap Topológico Narrativo},
  year = {2026},
  url = {https://github.com/ebiossanto/IA-RESEARCH-DELTA-H},
  license = {MIT}
}
```

Consulte [`CITATION.cff`](CITATION.cff) para mais detalhes.

---

## 📄 Comece por aqui

**`docs/NT-01_ESTADO_E_ESCOLHA_DA_METRICA_PRIMARIA.md`** — nota técnica que (i) resume o estado real do projeto, (ii) analisa formalmente as quatro métricas candidatas com proposições e contra-exemplos, (iii) **decide a métrica primária** e (iv) fixa todos os demais ajustes (hiperparâmetros, desenho amostral, modelo estatístico, controles, critérios de sucesso).

---

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `docs/` | notas técnicas de decisão (NT-01, NT-02, …) |
| `src/python/fetch_texts.py` | baixa as obras do Project Gutenberg → `data/texts/` |
| `src/python/delta_h_pipeline.py` | pipeline completo: frases → embeddings → Rips → métricas → CSV |
| `src/python/fazer_figuras.py` | gera `paper/figures/*.png` a partir dos CSVs |
| `src/python/pilot_stats.py` | estatísticas agregadas do piloto (base da NT-02) |
| `src/python/sensibilidade_eps.py` | compara escalas ε p50/p75/p90 |
| `src/python/controles_c4_c5.py` | controles C4 (seed) e C5 (extensão de frase) |
| `src/python/selecionar_segmentos.py` | seleção estratificada de trechos (quartis de Δ) |
| `src/python/mesclar_parcial.py` | mescla rodadas `--works` no arquivo da mesma escala |
| `src/python/_diag_*.py`, `_diagnostico.py` | diagnósticos auxiliares |
| `data/texts/` | textos limpos (domínio público) + `metadata.json` |
| `data/embeddings/` | cache dos embeddings (chave = obra + nº de frases + modelo) |
| `results/` | `delta_curves_p{50,75,90}.csv`, `segmentos_*`, `controles_*`, `resumo_*` |
| `src/julia/`, `proofs/`, `assets/geogebra/` | ainda vazios |
| `paper/` | `main.tex` e `paper/figures/` |

---

## Como rodar

```powershell
$py = "C:\Users\Euzébio Soares\AppData\Local\Programs\Python\Python312\python.exe"

# 1) textos (uma vez)
& $py src\python\fetch_texts.py

# 2) pipeline completo
& $py src\python\delta_h_pipeline.py --embedder sbert --controls
```

| Opção | Efeito |
|---|---|
| `--works dom_casmurro ulysses` | processa só essas obras |
| `--window-sizes 150 250 400` | larguras das janelas, em palavras |
| `--eps-pct 50` | escala da obra = percentil da MST (padrão 75) |
| `--b-ref 50` | nº de subconjuntos de referência por tamanho |
| `--max-windows 40` | smoke test rápido |
| `--embedder tfidf` | fallback **apenas** para testar o pipeline (nunca para resultados) |
| `--controls` | roda C1 (texto-avra) e C2 (piso de Monte Carlo) |
| `--segmentos 4000` | **modo segmento**: ignora janelas e grava `segmentos_4000pal_p75.csv` (é a unidade do estudo com leitores) |
| `--seed 123` | seed alternativa (controle C4); grava em arquivo `_s123_` separado |

Saídas: cada CSV também recebe um sufixo `_p{eps}` (e `_parcial`/`_s{seed}` quando aplicável) para que rodadas de sensibilidade não se sobreponham — **os arquivos com sufixo são os canônicos**; `delta_curves.csv` sem sufixo é apenas o espelho da última rodada.

Fluxo típico da Fase 2:

```powershell
# 3 escalas de ε (sensibilidade) — as 3 gravam delta_curves_p{50,75,90}.csv
& $py src\python\delta_h_pipeline.py --embedder sbert --controls --eps-pct 50
& $py src\python\delta_h_pipeline.py --embedder sbert --controls --eps-pct 75
& $py src\python\delta_h_pipeline.py --embedder sbert --controls --eps-pct 90

# escala do segmento de leitura (4000-6000 palavras) -> seleção de trechos
& $py src\python\delta_h_pipeline.py --segmentos 4000 --eps-pct 75
& $py src\python\selecionar_segmentos.py --largura 4000 --por-obra 3

# análises
& $py src\python\pilot_stats.py
& $py src\python\sensibilidade_eps.py
& $py src\python\controles_c4_c5.py
& $py src\python\fazer_figuras.py
```

---

## O que o pipeline calcula

Para cada janela contígua de $n$ frases, compara com $B$ subconjuntos aleatórios de $n$ frases sorteados da **mesma obra** (referência casada por tamanho — NT-01 §6.1):

| Métrica | Colunas | Papel |
|---|---|---|
| **ΔH** — $\lvert H_{obs}-H_{ref}\rvert$ | `delta_H`, `z_H`, `delta_H_norm` | **primária** |
| **d_B** — excedente sobre o piso | `delta_dB` | **confirmatória** |
| **ΔT** — soma de Betti | `delta_T` | descritiva |
| **ΔT^pers** — persistência total | `delta_Tpers` | descritiva |

**Configuração congelada (NT-01 §9):** modelo `paraphrase-multilingual-MiniLM-L12-v2` (uma frase por ponto, ≤128 wordpieces), frases L2-normalizadas, distância de cosseno $\in[0,2]$, Vietoris–Rips com dimensão máxima 2, corpo $\mathbb{Z}/2\mathbb{Z}$, escala comum por obra (percentil da MST — não o percentil de todos os pares, que em alta dimensão degenera), barra essencial censurada no limiar comum, `seed=42`.

---

## Corpus (9 obras, domínio público)

| Nível | Português | Inglês |
|---|---|---|
| **Simples** | Pérolas e Diamantes: Contos Infantis (#30510) | Alice's Adventures in Wonderland (#11); The Metamorphosis (#5200) |
| **Intermediário** | Dom Casmurro (#55752); Memórias Póstumas de Brás Cubas (#54829) | Hamlet (#1524) |
| **Complexo** | O Guarany vol. 1 (#67724); Quincas Borba (#55682) | Ulysses (#4300) |

> **Correção de corpus (Fase 2):** os IDs #21040 (*Brazilian Tales*, antologia inglesa) e #61653 (*Poesias Completas*) estavam errados; os textos corretos (#54829 e #55682) foram baixados e as rodadas das duas obras refeitas — ver NT-02.

*Grande Sertão: Veredas* e *Harry Potter* **não** entram como dados (copyright ativo) — apenas como citação curta no artigo (NT-01 §11).

---

## Estado das fases

| Fase | Entrega | Situação |
|---|---|---|
| 0 | ambiente (Python 3.12, `gudhi`, `scikit-learn`, `torch` CPU, `sentence-transformers`) | ✅ |
| 1 | obras `.txt` + pipeline ΔH / d_B | ✅ |
| 2 | **piloto computacional** (sinal, escala, sensibilidade, controles) | 🔄 em curso |
| 3 | congelamento do pré-registro | ⏳ |
| 4 | piloto com 5–10 leitores | ⏳ |
| 5 | coleta (≈108 observações) | ⏳ |
| 6 | análise multinível + artigo | ⏳ |

**Princípio de ouro:** nenhuma decisão estatística é tomada depois de ver dados de leitores. A Fase 2 usa *apenas* texto — por isso não contamina a hipótese.
