"""
Delta H — Fase 1/2: pipeline de cálculo do gap topológico (MVP + controles).

Implementa a Nota Técnica NT-01 (delta_h/docs/NT-01_...​.md):

  * embeddings por SENTENÇA, L2-normalizados, distância de cosseno      (NT-01 §2.1)
  * complexo Vietoris-Rips, dimensão 2, corpo Z/2Z                       (NT-01 §9)
  * escala comum por obra (percentil da MST das sentenças)               (NT-01 §6.5)
  * REFERÊNCIA CASADA POR TAMANHO: subconjuntos aleatórios de n sentenças
    sorteadas de toda a obra — é contra eles que a janela contígua é
    comparada (NT-01 §6.1, refino "tamanho casado")
  * métricas:
      ΔH  = |H(janela) - mediana H(referências)|      [PRIMÁRIA]
      d_B = mediana d_B(janela, refs) - mediana d_B(ref, ref)   [CONFIRMATÓRIA]
      ΔT, ΔT^pers                                   [DESCRITIVAS]
  * controles: C2 (sentenças embaralhadas) e C3 (é a própria referência)

Uso:
    python fetch_texts.py
    python delta_h_pipeline.py                       # todas as obras, smoke completo
    python delta_h_pipeline.py --works dom_casmurro --max-windows 60 --embedder tfidf
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):          # console Windows (cp1252) x UTF-8
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --------------------------------------------------------------------------- #
# CONFIGURAÇÃO CONGELADA (NT-01 §9)                                            #
# --------------------------------------------------------------------------- #
SEED = 42
MAX_DIM = 2                       # beta >= 3 e' artefato em embedding ruidoso
MODEL_SBERT = "paraphrase-multilingual-MiniLM-L12-v2"
MODEL_LABSE = "sentence-transformers/LaBSE"
GLOBAL_SUBSAMPLE = 250            # pontos da nuvem global (custo Rips ~ O(n^3))
EPS_PCT_DEFAULT = 75              # percentil da MST que fixa a escala da obra
B_REF = 50                        # subconjuntos de referencia por (obra, n)
WINDOW_SIZES_DEFAULT = (150, 250, 400)
COEF_LABEL = "Z/2Z"

ROOT = Path(__file__).resolve().parents[2]          # .../delta_h
TEXT_DIR = ROOT / "data" / "texts"
CACHE_DIR = ROOT / "data" / "embeddings"
RESULT_DIR = ROOT / "results"
FIG_DIR = ROOT / "paper" / "figures"

_SENT_SPLIT = re.compile(
    r"(?<=[.!?…])(?:[\"'»”)\]]*)\s+(?=[\"'“«(\[]?[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9])"
)


# --------------------------------------------------------------------------- #
# TEXTO                                                                         #
# --------------------------------------------------------------------------- #
def _partir_longo(trecho: str, max_pal: int = 60) -> list[str]:
    """Quebra trechos longos em blocos <= max_palavras. NENHUM texto perdido."""
    if len(trecho.split()) <= max_pal:
        return [trecho]
    pedacos, buf = [], []
    for ped in re.split(r"(?<=[;—–])\s+", trecho):   # respeita coesao sintatica
        if len(buf) + len(ped.split()) <= max_pal:
            buf.append(ped)
        else:
            if buf:
                pedacos.append(" ".join(buf))
            buf = [ped]
    if buf:
        pedacos.append(" ".join(buf))
    saida = []
    for p in pedacos:
        w = p.split()
        if len(w) <= max_pal:
            saida.append(p)
        else:                                        # quebra burra por palavra
            saida.extend(" ".join(w[i:i + max_pal]) for i in range(0, len(w), max_pal))
    return saida


def dividir_sentencas(texto: str) -> list[str]:
    """Segmentacao heuristica (MVP). Nenhum trecho e descartado."""
    brutos = _SENT_SPLIT.split(texto.replace("\n", " "))
    saida = []
    for p in brutos:
        p = re.sub(r"\s+", " ", p).strip()
        if p:
            saida.extend(_partir_longo(p))
    return saida


def carregar_obras(somente: list[str] | None) -> dict[str, dict]:
    meta_path = TEXT_DIR / "metadata.json"
    if not meta_path.exists():
        sys.exit("metadata.json ausente — rode antes: python fetch_texts.py")
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    obras = {}
    for slug, info in metadata.items():
        if somente and slug not in somente:
            continue
        caminho = TEXT_DIR / f"{slug}.txt"
        if not caminho.exists():
            continue
        texto = caminho.read_text(encoding="utf-8")
        sentencas = dividir_sentencas(texto)
        if len(sentencas) < 60:
            print(f"  [aviso] {slug}: apenas {len(sentencas)} frases — ignorado")
            continue
        obras[slug] = {**info, "sentencas": sentencas}
    return obras


# --------------------------------------------------------------------------- #
# EMBEDDINGS                                                                    #
# --------------------------------------------------------------------------- #
def embeddings_sbert(textos: list[str], cache: Path) -> np.ndarray:
    if cache.exists():
        arr = np.load(cache)["arr"]
        if arr.shape[0] == len(textos):
            return arr
    from sentence_transformers import SentenceTransformer

    modelo = SentenceTransformer(MODEL_SBERT, device="cpu")
    arr = modelo.encode(
        textos,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,     # L2 -> distancia de cosseno em [0,2]
        convert_to_numpy=True,
    ).astype(np.float32)
    np.savez_compressed(cache, arr=arr)
    return arr


def embeddings_labse(textos: list[str], cache: Path) -> np.ndarray:
    """LaBSE — modelo multilingue de frases, focado em similaridade semântica."""
    if cache.exists():
        arr = np.load(cache)["arr"]
        if arr.shape[0] == len(textos):
            return arr
    from sentence_transformers import SentenceTransformer

    modelo = SentenceTransformer(MODEL_LABSE, device="cpu")
    arr = modelo.encode(
        textos,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype(np.float32)
    np.savez_compressed(cache, arr=arr)
    return arr


def embeddings_tfidf(textos: list[str], cache: Path) -> np.ndarray:
    """Fallback de PIPELINE (smoke test) — NAO serve para resultados do artigo."""
    if cache.exists():
        arr = np.load(cache)["arr"]
        if arr.shape[0] == len(textos):
            return arr
    from sklearn.feature_extraction.text import TfidfVectorizer

    vec = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), max_features=512,
                          sublinear_tf=True)
    arr = vec.fit_transform(textos).toarray().astype(np.float32)
    normas = np.linalg.norm(arr, axis=1, keepdims=True)
    normas[normas == 0] = 1.0
    arr = arr / normas
    np.savez_compressed(cache, arr=arr)
    return arr


def obter_embeddings(slug: str, textos: list[str], embedder: str) -> np.ndarray:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tag = MODEL_SBERT if embedder == "sbert" else (
        MODEL_LABSE if embedder == "labse" else "tfidf_char512"
    )
    chave = hashlib.md5(f"{slug}|{len(textos)}|{tag}".encode()).hexdigest()[:10]
    cache = CACHE_DIR / f"{slug}_{embedder}_{chave}.npz"
    if embedder == "sbert":
        try:
            return embeddings_sbert(textos, cache)
        except Exception as exc:                       # noqa: BLE001
            print(f"  [aviso] SBERT indisponível ({exc}); usando TF-IDF (PIPELINE)")
    if embedder == "labse":
        try:
            return embeddings_labse(textos, cache)
        except Exception as exc:                       # noqa: BLE001
            print(f"  [aviso] LaBSE indisponível ({exc}); usando TF-IDF (PIPELINE)")
    return embeddings_tfidf(textos, cache)


# --------------------------------------------------------------------------- #
# TOPOLOGIA                                                                     #
# --------------------------------------------------------------------------- #
def escala_mst(pontos: np.ndarray, percentil: float) -> tuple[float, dict]:
    """Escala da obra = percentil das arestas da arvore geradora minima.

    Evita o erro classico de usar o percentil de TODOS os pares (em alta
    dimensao as distancias concentram -> complexo quase completo).
    """
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import minimum_spanning_tree

    n = len(pontos)
    dist = 1.0 - pontos @ pontos.T                    # cosseno, [0,2]
    np.fill_diagonal(dist, 0.0)
    mst = minimum_spanning_tree(csr_matrix(dist))
    arestas = np.array(mst.data) if len(mst.data) else np.array([0.0])
    eps = float(np.percentile(arestas, percentil))
    # diagnostico: densidade de arestas do complexo na escala escolhida
    n_arestas = int((dist[np.triu_indices(n, 1)] <= eps).sum())
    diag = {"eps": eps, "mst_n": int(n), "n_arestas": n_arestas,
            "frac_pares": n_arestas / max(1, n * (n - 1) / 2)}
    return eps, diag


def escala_pares(pontos: np.ndarray, percentil: float) -> tuple[float, dict]:
    """Escala da obra = percentil de TODAS as distancias pareadas.

    E exatamente a regra citada na NT-01 §6.5/§9 («90º percentil das
    distancias pareadas»). Implementada para ser TESTADA, nao assumida: em
    alta dimensao as distancias concentram, entao o percentil alto tende ao
    diametro e o complexo satura — a NT-02 compara com a regra MST.
    """
    n = len(pontos)
    dist = 1.0 - pontos @ pontos.T                    # cosseno, [0,2]
    iu = np.triu_indices(n, 1)
    pares = dist[iu]
    eps = float(np.percentile(pares, percentil))
    n_arestas = int((pares <= eps).sum())
    diag = {"eps": eps, "mst_n": int(n), "n_arestas": n_arestas,
            "frac_pares": n_arestas / max(1, len(pares))}
    return eps, diag


def escala_obra(pontos: np.ndarray, percentil: float,
                regra: str = "mst") -> tuple[float, dict]:
    """Dispatcher de regra de escala: 'mst' (padrão) ou 'pares' (NT-01 §9)."""
    if regra == "pares":
        return escala_pares(pontos, percentil)
    return escala_mst(pontos, percentil)


def diagrama(pontos: np.ndarray, eps: float, max_dim: int = MAX_DIM) -> dict[int, np.ndarray]:
    """Diagramas de persistencia com ESCALA COMUM `eps`.

    `eps` e a distancia de COSSENO. O GUDHI filtra por distancia EUCLIDIANA;
    para pontos L2-normalizados a troca e exata:  ||x-y||^2 = 2(1 - cos),
    logo  eps_eucl = sqrt(2*eps)  e o inverso e  cos = d^2/2.

    Toda barra ainda viva em `eps` tem morte truncada em `eps` (censura a
    direita identica para TODAS as nuvens -> comparabilidade garantida).
    """
    import math

    import gudhi

    pontos = np.asarray(pontos, dtype=np.float64)
    n = len(pontos)

    if n == 1:
        return {0: np.array([[0.0, eps]]), 1: np.empty((0, 2)), 2: np.empty((0, 2))}
    if n == 2:
        d = float(1.0 - pontos[0] @ pontos[1])
        d = min(d, eps)
        return {0: np.array([[0.0, d], [0.0, eps]]),
                1: np.empty((0, 2)), 2: np.empty((0, 2))}

    eps_eucl = math.sqrt(2.0 * eps)
    rips = gudhi.RipsComplex(points=pontos, max_edge_length=eps_eucl)
    st = rips.create_simplex_tree(max_dimension=max_dim)
    st.persistence()

    saida: dict[int, np.ndarray] = {}
    for k in range(max_dim + 1):
        iv = np.asarray(st.persistence_intervals_in_dimension(k), dtype=float).reshape(-1, 2)
        if iv.size:
            nasc = np.minimum(iv[:, 0] ** 2 / 2.0, eps)
            morte = np.where(np.isinf(iv[:, 1]), eps, np.minimum(iv[:, 1] ** 2 / 2.0, eps))
            iv = np.column_stack([nasc, morte])
        saida[k] = iv

    if saida[0].size == 0:
        # GUDHI devolve vazio quando existem SO vertices -> n componentes
        # isolados, cada um vivo ate o limiar (comportamento correto).
        if st.num_simplices() <= n:
            saida[0] = np.column_stack([np.zeros(n), np.full(n, eps)])
        else:
            saida[0] = np.array([[0.0, eps]])
    return saida


def vetor_betti(dg: dict[int, np.ndarray], eps: float) -> list[int]:
    """Beta_k(eps) lidos do diagrama (nao depende de betti_numbers())."""
    beta = []
    for k in sorted(dg):
        iv = dg[k]
        if iv.size == 0:
            beta.append(0)
            continue
        vivas = ((iv[:, 0] <= eps) & (iv[:, 1] >= eps - 1e-12)
                 & ((iv[:, 1] - iv[:, 0]) > 1e-12))
        beta.append(int(vivas.sum()))
    return beta


def complexidade(beta: list[int]) -> float:
    """C = sum (k+1) beta_k   (NT-01 candidata A — DESCRITIVA)."""
    return float(sum((k + 1) * b for k, b in enumerate(beta)))


def persistencia_total(dg: dict[int, np.ndarray]) -> float:
    """C^pers = sum_k (k+1) P_k, P_k = sum_i (d_i - b_i)  (candidata B)."""
    total = 0.0
    for k, iv in dg.items():
        if iv.size:
            total += (k + 1) * float((iv[:, 1] - iv[:, 0]).sum())
    return total


def entropia_persistente(dg: dict[int, np.ndarray]) -> float:
    """H(D) = -sum p_i log p_i, p_i = l_i / sum l   (NT-01 §2.7 — PRIMÁRIA)."""
    barras = [iv for iv in dg.values() if iv.size]
    if not barras:
        return 0.0
    comp = np.concatenate([(iv[:, 1] - iv[:, 0]) for iv in barras])
    comp = comp[comp > 1e-12]
    if comp.size == 0:
        return 0.0
    p = comp / comp.sum()
    return float(-(p * np.log(p)).sum())


def bottleneck(a: dict[int, np.ndarray], b: dict[int, np.ndarray]) -> float:
    """d_B por dimensao, combinado pelo maximo (barras de dimensoes distintas
    nunca casam entre si)."""
    import gudhi

    dists = []
    for k in sorted(set(a) | set(b)):
        pa = a.get(k, np.empty((0, 2)))
        pb = b.get(k, np.empty((0, 2)))
        if pa.size == 0 and pb.size == 0:
            continue
        lista_a = [tuple(map(float, p)) for p in pa] or [(0.0, 0.0)]
        lista_b = [tuple(map(float, p)) for p in pb] or [(0.0, 0.0)]
        if pa.size == 0:
            lista_a = [(float(pb[:, 0].min()), float(pb[:, 0].min()))]
        if pb.size == 0:
            lista_b = [(float(pa[:, 0].min()), float(pa[:, 0].min()))]
        dists.append(float(gudhi.bottleneck_distance(lista_a, lista_b)))
    return max(dists) if dists else 0.0


def estatisticas(dg: dict[int, np.ndarray], eps: float) -> dict:
    beta = vetor_betti(dg, eps)
    n_barras = int(sum(iv.size // 2 for iv in dg.values()))
    H = entropia_persistente(dg)
    return {
        "H": H,
        # H/ln(n) normaliza a CONTAGEM de barras: em espacos de embedding as
        # distancias concentram e H -> ln(n_barras). A comparacao obs x ref ja
        # e casada por n; reportar as duas formas permite auditar o que gera o gap.
        "H_norm": (H / math.log(n_barras)) if n_barras > 1 else 0.0,
        "C": complexidade(beta),
        "Cpers": persistencia_total(dg),
        "beta": beta,
        "n_barras": n_barras,
        "n_H1": int(np.asarray(dg.get(1, np.empty((0, 2)))).shape[0]),
        "n_H2": int(np.asarray(dg.get(2, np.empty((0, 2)))).shape[0]),
    }


# --------------------------------------------------------------------------- #
# REFERENCIA CASADA POR TAMANHO (NT-01 §6.1)                                    #
# --------------------------------------------------------------------------- #
class Referencias:
    """Para cada (obra, n): B subconjuntos aleatorios de n sentenças sorteadas
    de TODA a obra. Cache porque todas as janelas de mesmo n partilham a mesma
    distribuicao de referencia."""

    def __init__(self, emb: np.ndarray, eps: float, b_ref: int, seed: int):
        self.emb = emb
        self.eps = eps
        self.b_ref = b_ref
        self.rng = np.random.default_rng(seed)
        self.cache: dict[int, list[dict]] = {}
        self._base: dict[int, float] = {}

    def diagramas(self, n: int) -> list[dict[int, np.ndarray]]:
        if n not in self.cache:
            pool = len(self.emb)
            diagramas = []
            for _ in range(self.b_ref):
                idx = self.rng.choice(pool, size=min(n, pool), replace=False)
                diagramas.append(diagrama(self.emb[idx], self.eps))
            self.cache[n] = diagramas
        return self.cache[n]

    def estatisticas(self, n: int) -> dict:
        ests = [estatisticas(d, self.eps) for d in self.diagramas(n)]
        return {
            "H_med": float(np.median([e["H"] for e in ests])),
            "H_dp": float(np.std([e["H"] for e in ests])),
            "H_norm_med": float(np.median([e["H_norm"] for e in ests])),
            "n_barras_med": float(np.median([e["n_barras"] for e in ests])),
            "n_H1_med": float(np.median([e["n_H1"] for e in ests])),
            "C_med": float(np.median([e["C"] for e in ests])),
            "Cpers_med": float(np.median([e["Cpers"] for e in ests])),
            "dB_ref": None,   # preenchido sob demanda
        }

    def bottleneck_base(self, n: int, limite_pares: int = 200) -> float:
        """Mediana d_B entre pares de referencias (ruido de fundo). Cacheado."""
        if n in self._base:
            return self._base[n]
        dg = self.diagramas(n)
        custos = []
        for i in range(min(len(dg), 25)):
            for j in range(i + 1, min(len(dg), 25)):
                custos.append(bottleneck(dg[i], dg[j]))
                if len(custos) >= limite_pares:
                    break
            if len(custos) >= limite_pares:
                break
        valor = float(np.median(custos)) if custos else 0.0
        self._base[n] = valor
        return valor


# --------------------------------------------------------------------------- #
# JANELAS                                                                       #
# --------------------------------------------------------------------------- #
def janelas_por_palavras(sentencas: list[str], largura: int) -> list[dict]:
    """Janelas NAO sobrepostas de `largura` palavras (evita autocorrelacao)."""
    saida, atual = [], []
    contador_janela = 0        # palavras SO da janela atual
    palavra_ini = 0            # posicao absoluta da primeira palavra
    total = 0                  # posicao absoluta corrente
    for i, s in enumerate(sentencas):
        n = len(s.split())
        atual.append(i)
        contador_janela += n
        total += n
        if contador_janela >= largura:
            saida.append({"sentencas": atual, "palavra_ini": palavra_ini,
                          "palavra_fim": total})
            atual = []
            palavra_ini = total
            contador_janela = 0
    if len(atual) >= 3:
        saida.append({"sentencas": atual, "palavra_ini": palavra_ini,
                      "palavra_fim": total})
    return saida


# --------------------------------------------------------------------------- #
# CONTROLE C2: sentencas embaralhadas                                          #
# --------------------------------------------------------------------------- #
def controle_embaralhar(emb: np.ndarray, janelas: list[dict], refs: Referencias,
                        eps: float, b_ref: int, seed: int, max_janelas: int
                        ) -> list[dict]:
    rng = np.random.default_rng(seed)
    linhas = []
    for w in janelas[:max_janelas]:
        idx = np.array(w["sentencas"])
        n = len(idx)
        Hs, dBs = [], []
        for _ in range(b_ref):
            # mesma janela, ordem aleatoria das sentencas do texto INTEIRO:
            # sortear n sentencas quaisquer = perder a localidade narrativa
            escolha = rng.choice(len(emb), size=n, replace=False)
            dg = diagrama(emb[escolha], eps)
            Hs.append(entropia_persistente(dg))
            dBs.append(bottleneck(dg, dg))
        est = refs.estatisticas(n)
        linhas.append({
            "controle": "C2_ref_mc",
            "n_sentencas": n,
            "H_obs": float(np.median(Hs)),
            "H_ref": est["H_med"],
            "delta_H": abs(float(np.median(Hs)) - est["H_med"]),
            "z_H": ((float(np.median(Hs)) - est["H_med"]) / est["H_dp"]
                    if est["H_dp"] > 1e-9 else 0.0),
        })
    return linhas


# --------------------------------------------------------------------------- #
# CONTROLE C1: texto-avra (sem estrutura narrativa)                             #
# --------------------------------------------------------------------------- #
def controle_salad(slug: str, obra: dict, args, largura: int = 250,
                   seed: int | None = None) -> list[dict]:
    """C1: texto-avra — cada frase e reescrita so com palavras sorteadas do
    PROPRIO vocabulario da obra, preservando o comprimento. Destruem-se sintase,
    semantica e narrativa. Se o gap medir estrutura narrativa, ele (e a sua
    dispersao entre janelas) deve colapsar.

    Nota de design: "C2 = reordenar as sentencas da janela" NAO e controle
    informativo aqui — a representacao e um CONJUNTO de embeddings de frases,
    portanto a ordem nao entra no calculo. O nulo de localidade e justamente a
    referencia casada por tamanho (NT-01 §6.1), que ja roda em todo o pipeline;
    o que `controle_embaralhar` mede alem disso e o ERRO DE MONTE CARLO da
    propria referencia (mediana vs mediana), i.e. o piso numerico do gap.
    """
    sents = obra["sentencas"]
    rng = np.random.default_rng(SEED if seed is None else seed)
    vocab = np.array(sorted({w for s in sents for w in s.split()}))
    saladas = [" ".join(rng.choice(vocab, size=max(3, len(s.split()))))
               for s in sents]

    emb_s = obter_embeddings(f"{slug}__salad", saladas, args.embedder)
    seed = SEED if seed is None else seed
    rng_g = np.random.default_rng(seed)
    n_g = min(GLOBAL_SUBSAMPLE, len(emb_s))
    Xg = emb_s[rng_g.choice(len(emb_s), size=n_g, replace=False)]
    eps_s, _ = escala_obra(Xg, args.eps_pct, args.eps_rule)
    refs = Referencias(emb_s, eps_s, args.b_ref, seed)

    linhas = []
    for w in janelas_por_palavras(saladas, largura)[:args.max_controls]:
        idx = np.array(w["sentencas"])
        n = len(idx)
        if n < 4:
            continue
        e = estatisticas(diagrama(emb_s[idx], eps_s), eps_s)
        er = refs.estatisticas(n)
        linhas.append({
            "controle": "C1_salad",
            "obra": slug,
            "janela_palavras": largura,
            "n_sentencas": n,
            "H_obs": e["H"],
            "H_ref": er["H_med"],
            "delta_H": abs(e["H"] - er["H_med"]),
            "z_H": ((e["H"] - er["H_med"]) / er["H_dp"]) if er["H_dp"] > 1e-9 else 0.0,
        })
    return linhas


# --------------------------------------------------------------------------- #
# PIPELINE                                                                      #
# --------------------------------------------------------------------------- #
def processar_obra(slug: str, obra: dict, args) -> tuple[list[dict], dict]:
    t0 = time.time()
    sentencas = obra["sentencas"]
    emb = obter_embeddings(slug, sentencas, args.embedder)

    rng = np.random.default_rng(args.seed)
    n_global = min(GLOBAL_SUBSAMPLE, len(emb))
    idx_global = rng.choice(len(emb), size=n_global, replace=False)
    Xg = emb[idx_global]

    eps, diag_escala = escala_obra(Xg, args.eps_pct, args.eps_rule)
    Dg = diagrama(Xg, eps)
    g = estatisticas(Dg, eps)

    refs = Referencias(emb, eps, args.b_ref, args.seed)

    linhas = []
    for largura in args.window_sizes:
        for widx, w in enumerate(janelas_por_palavras(sentencas, largura)):
            idx = np.array(w["sentencas"])
            n = len(idx)
            if n < 4:
                continue
            dw = diagrama(emb[idx], eps)
            e = estatisticas(dw, eps)
            er = refs.estatisticas(n)
            dH = abs(e["H"] - er["H_med"])
            zH = (e["H"] - er["H_med"]) / er["H_dp"] if er["H_dp"] > 1e-9 else 0.0
            dHn = abs(e["H_norm"] - er["H_norm_med"])

            dB_obs = float(np.median([bottleneck(dw, d) for d in refs.diagramas(n)]))
            dB_base = refs.bottleneck_base(n)
            dBover = max(0.0, dB_obs - dB_base)

            linhas.append({
                "obra": slug,
                "nivel": obra["nivel"],
                "idioma": obra["idioma"],
                "embedder": args.embedder,
                "janela_palavras": largura,
                "janela_idx": widx,
                "palavra_ini": w["palavra_ini"],
                "n_sentencas": n,
                "eps": eps,
                # --- PRIMARIA (Delta H) ---
                "H_obs": e["H"],
                "H_ref": er["H_med"],
                "delta_H": dH,
                "z_H": zH,
                "H_norm_obs": e["H_norm"],
                "H_norm_ref": er["H_norm_med"],
                "delta_H_norm": dHn,
                "n_barras_obs": e["n_barras"],
                "n_barras_ref": er["n_barras_med"],
                "n_H1_obs": e["n_H1"],
                "n_H1_ref": er["n_H1_med"],
                # --- CONFIRMATORIA (bottleneck) ---
                "dB_obs_ref": dB_obs,
                "dB_base": dB_base,
                "delta_dB": dBover,
                # --- DESCRITIVAS ---
                "C_obs": e["C"],
                "C_ref": er["C_med"],
                "delta_T": e["C"] - er["C_med"],
                "Cpers_obs": e["Cpers"],
                "Cpers_ref": er["Cpers_med"],
                "delta_Tpers": e["Cpers"] - er["Cpers_med"],
                "beta_obs": json.dumps(e["beta"]),
                "n_barras": e["n_barras"],
                # --- diagnostico ---
                "degenerado": int(e["n_barras"] <= 1),
            })

    # ---- controles ---------------------------------------------------------
    # C1_salad : texto sem estrutura -> gap deve colapsar
    # C2_ref   : erro de Monte Carlo da propria referencia (piso numerico)
    controles = []
    if args.controls:
        controles = controle_embaralhar(emb, janelas_por_palavras(sentencas, 250),
                                        refs, eps, min(args.b_ref, 20),
                                        args.seed + 1, args.max_controls)
        controles += controle_salad(slug, obra, args, largura=250,
                                    seed=args.seed + 7)

    resumo = {
        "obra": slug,
        "nivel": obra["nivel"],
        "idioma": obra["idioma"],
        "titulo": obra["titulo"],
        "n_sentencas": len(sentencas),
        "n_janelas_total": sum(len(janelas_por_palavras(sentencas, L))
                               for L in args.window_sizes),
        "eps": eps,
        "frac_pares_conectados": diag_escala["frac_pares"],
        "H_global": g["H"],
        "C_global": g["C"],
        "Cpers_global": g["Cpers"],
        "n_barras_global": g["n_barras"],
        "beta_global": json.dumps(g["beta"]),
        "embedder": args.embedder,
        "segundos": round(time.time() - t0, 1),
    }
    return linhas, {"resumo": resumo, "controles": controles}


# --------------------------------------------------------------------------- #
# RELATORIO                                                                     #
# --------------------------------------------------------------------------- #
def relatorio(df: pd.DataFrame, resumos: list[dict], controles: pd.DataFrame,
              args, raiz: Path) -> None:
    print("\n" + "=" * 78)
    print("RESUMO POR OBRA (mediana entre janelas)")
    print("=" * 78)
    cols = ["obra", "nivel", "n_sentencas", "eps", "H_global", "n_barras_global", "segundos"]
    print(pd.DataFrame(resumos)[cols].to_string(index=False))

    print("\n" + "=" * 78)
    print("GAP PRIMÁRIO  ΔH = |H(janela) - H(referência casada)|   [NT-01 §2.7/§6.1]")
    print("=" * 78)
    agg = (df.groupby(["obra", "nivel", "janela_palavras"])
             .agg(n_janelas=("delta_H", "size"),
                  dH_mediano=("delta_H", "median"),
                  dH_media=("delta_H", "mean"),
                  dHnorm_med=("delta_H_norm", "median"),
                  zH_mediano=("z_H", "median"),
                  zH_dp=("z_H", "std"),
                  barras_obs=("n_barras_obs", "median"),
                  barras_ref=("n_barras_ref", "median"),
                  dB_mediano=("delta_dB", "median"),
                  dT_mediano=("delta_T", "median"),
                  pct_degenerado=("degenerado", "mean"))
             .reset_index())
    print(agg.to_string(index=False,
                        float_format=lambda v: f"{v:.3f}"))

    print("\n" + "=" * 78)
    print("CONTROLES  (janela = 250 palavras)")
    print("=" * 78)
    if controles is not None and len(controles) and "delta_H" in controles:
        real = df[df["janela_palavras"] == 250]
        print(f"  {'texto real':<28} dH={real['delta_H'].median():.4f}  "
              f"z={real['z_H'].median():+.3f}  dp(z)={real['z_H'].std():.3f}  "
              f"(n={len(real)})")
        rotulos = {
            "C1_salad": "texto-avra (sem narrativa)",
            "C2_ref_mc": "piso de Monte Carlo (mediana vs mediana)",
        }
        for nome, sub in controles.groupby("controle"):
            rot = rotulos.get(nome, nome)
            if "delta_H" not in sub or sub["delta_H"].isna().all():
                continue
            print(f"  {rot:<28} dH={sub['delta_H'].median():.4f}  "
                  f"z={sub['z_H'].median():+.3f}  dp(z)={sub['z_H'].std():.3f}  "
                  f"(n={len(sub)})")
        print("\n  leitura:")
        print("   • C1_salad ~ 0  -> o gap depende de estrutura semantica/narrativa;")
        print("     C1_salad ~ texto real -> o gap e apenas artefato de densidade.")
        print("   • C2_ref_mc = erro de Monte Carlo da referencia (B amostras);")
        print("     dH(real) >> C2_ref_mc -> o gap nao e ruido numerico.")
    else:
        print("  controles não executados (use --controls)")

    print("\nSensibilidade à escala: rerode com --eps-pct 50,75,90 e compare ΔH.")
    print("Sensibilidade à janela : compare as colunas janela_palavras acima.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Delta H — pipeline (NT-01)")
    ap.add_argument("--works", nargs="*", default=None)
    ap.add_argument("--window-sizes", nargs="*", type=int,
                    default=list(WINDOW_SIZES_DEFAULT))
    ap.add_argument("--embedder", choices=["sbert", "labse", "tfidf"], default="sbert")
    ap.add_argument("--eps-pct", type=float, default=EPS_PCT_DEFAULT)
    ap.add_argument("--eps-rule", choices=["mst", "pares"], default="mst",
                    help="regra da escala: mst = percentil das arestas da MST "
                         "(padrão); pares = percentil de todas as distâncias "
                         "pareadas (regra literal da NT-01 §9)")
    ap.add_argument("--b-ref", type=int, default=B_REF)
    ap.add_argument("--max-windows", type=int, default=0, help="limita janelas por obra (smoke)")
    ap.add_argument("--controls", action="store_true", help="roda os controles C1/C2")
    ap.add_argument("--max-controls", type=int, default=40)
    ap.add_argument("--segmentos", type=int, default=0,
                    help="modo segmento (ex. 5000): ignora as janelas e grava "
                         "segmentos_p<eps>.csv — é a unidade do estudo com leitores")
    ap.add_argument("--seed", type=int, default=SEED,
                    help="seed global (controle C4: repetir com seed diferente)")
    args = ap.parse_args()

    if args.segmentos:
        args.window_sizes = [args.segmentos]
        args.controls = False          # controles C1/C2 são de escala de janela

    np.random.seed(args.seed)
    obras = carregar_obras(args.works)
    if not obras:
        sys.exit("nenhuma obra encontrada em data/texts/")

    print(f"Delta H | embedder={args.embedder}  eps={args.eps_pct}%"
          f"{args.eps_rule.upper()}  "
          f"dim<={MAX_DIM}  coef={COEF_LABEL}  B_ref={args.b_ref}  seed={args.seed}"
          + (f"  | MODO SEGMENTO {args.segmentos} pal" if args.segmentos else ""))

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    todas, resumos, todos_controles = [], [], []
    for slug, obra in obras.items():
        print(f"\n--- {slug} ({obra['nivel']}, {obra['idioma']}) ---")
        linhas, extra = processar_obra(slug, obra, args)
        if args.max_windows:
            limitado = [l for l in linhas if l["janela_idx"] < args.max_windows]
            linhas = limitado
        todas.extend(linhas)
        resumos.append(extra["resumo"])
        todos_controles.extend(extra["controles"])
        print(f"    {len(linhas)} janelas | eps={extra['resumo']['eps']:.3f} | "
              f"{extra['resumo']['segundos']}s")

    base = "segmentos" if args.segmentos else "delta_curves"
    df = pd.DataFrame(todas)
    df.to_csv(RESULT_DIR / f"{base}.csv", index=False, encoding="utf-8-sig")
    # cópia com a escala no nome, para comparar --eps-pct 50/75/90 sem apagar;
    # rodadas parciais (--works) gravam em arquivo próprio para não se misturarem
    sufixo = (f"{'_parcial' if args.works else ''}"
              f"{'_s' + str(args.seed) if args.seed != SEED else ''}"
              f"{'_' + str(args.segmentos) + 'pal' if args.segmentos else ''}"
              f"{'_pares' if args.eps_rule == 'pares' else ''}"
              f"_p{int(args.eps_pct)}")
    df.to_csv(RESULT_DIR / f"{base}{sufixo}.csv", index=False,
              encoding="utf-8-sig")
    nome_resumo = "resumo_segmentos" if args.segmentos else "resumo_obras"
    (RESULT_DIR / f"{nome_resumo}.json").write_text(
        json.dumps(resumos, ensure_ascii=False, indent=2), encoding="utf-8")
    (RESULT_DIR / f"{nome_resumo}{sufixo}.json").write_text(
        json.dumps(resumos, ensure_ascii=False, indent=2), encoding="utf-8")

    controles_df = pd.DataFrame(todos_controles)
    if len(controles_df):
        controles_df.to_csv(RESULT_DIR / "controles.csv", index=False,
                            encoding="utf-8-sig")
        controles_df.to_csv(RESULT_DIR / f"controles{sufixo}.csv", index=False,
                            encoding="utf-8-sig")

    relatorio(df, resumos, controles_df, args, RESULT_DIR)
    print(f"\nCSV  : {RESULT_DIR / (base + '.csv')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
