"""
Delta H — Fase 1: aquisição de textos (Project Gutenberg).

Uso:
    python fetch_texts.py

Saídas:
    delta_h/data/texts/<slug>.txt     texto limpo (cabeçalho/rodapé Gutenberg removidos)
    delta_h/data/texts/metadata.json  origem, id, idioma, nível de complexidade, contagens

NT-01 §5 / §11: obras em domínio público. Obras com direitos autorais ativos
(Harry Potter, Grande Sertão: Veredas) NÃO são baixadas aqui — entram apenas
como citação curta no artigo.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # .../delta_h
OUT_DIR = ROOT / "data" / "texts"

# slug -> (gutenberg_id, idioma, nivel, titulo)
WORKS = {
    "alice_wonderland":  (11,    "en", "simples",      "Alice's Adventures in Wonderland"),
    "perolas_infantis":  (30510, "pt", "simples",      "Pérolas e Diamantes: Contos Infantis"),
    "dom_casmurro":      (55752, "pt", "intermediario","Dom Casmurro"),
    "hamlet":            (1524,  "en", "intermediario","Hamlet"),
    "ulysses":           (4300,  "en", "complexo",     "Ulysses"),
    "o_guarany_v1":      (67724, "pt", "complexo",     "O Guarany (vol. 1)"),
}

# backups caso algum id falhe (mesma faixa de complexidade)
BACKUPS = {
    "memorias_braz_cubas": (54829, "pt", "intermediario", "Memórias Póstumas de Brás Cubas"),
    "metamorphosis":       (5200,  "en", "simples",       "The Metamorphosis"),
    "quincas_borba":       (55682, "pt", "complexo",      "Quincas Borba"),
}

URLS = [
    "https://www.gutenberg.org/ebooks/{id}.txt.utf-8",        # livros so em HTML
    "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt",
    "https://www.gutenberg.org/files/{id}/{id}-0.txt",
    "https://www.gutenberg.org/files/{id}/{id}.txt",
]

_START = re.compile(r"\*\*\*\s*START OF (?:THIS|THE) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*", re.I)
_END = re.compile(r"\*\*\*\s*END OF (?:THIS|THE) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*", re.I)
# fallback: livros derivados de HTML as vezes nao trazem o marcador *** END ***
_LEGAL = re.compile(
    r"\n\s*(?:This eBook is for the use of anyone|Project Gutenberg.s electronic works"
    r"|Project Gutenberg is a registered trademark|Limited liability|FULL PROJECT GUTENBERG)",
    re.I,
)


def baixar(gutenberg_id: int) -> str:
    ultimo_erro = None
    for modelo in URLS:
        url = modelo.format(id=gutenberg_id)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "DeltaH/1.0 (pesquisa academica)"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                bruto = resp.read()
        except Exception as exc:                     # noqa: BLE001
            ultimo_erro = exc
            continue
        for codificacao in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
            try:
                return bruto.decode(codificacao)
            except UnicodeDecodeError:
                continue
    raise RuntimeError(f"id={gutenberg_id}: todas as URLs falharam ({ultimo_erro})")


def limpar(texto: str) -> str:
    """Remove cabecalho e rodape legais do Gutenberg. Idempotente."""
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")

    inicio = _START.search(texto)
    if inicio:
        texto = texto[inicio.end():]

    # o _END deve ser procurado DEPOIS do corte do cabecalho (mesma base)
    fim = _END.search(texto)
    if fim:
        texto = texto[: fim.start()]
    else:
        corte = int(len(texto) * 0.80)
        ilegal = _LEGAL.search(texto[corte:])
        if ilegal:
            texto = texto[: corte + ilegal.start()]

    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def contar_palavras(texto: str) -> int:
    return len(texto.split())


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tudo = dict(WORKS)
    tudo.update(BACKUPS)
    metadata = {}

    for slug, (gid, idioma, nivel, titulo) in tudo.items():
        destino = OUT_DIR / f"{slug}.txt"
        if destino.exists() and destino.stat().st_size > 10_000:
            bruto = destino.read_text(encoding="utf-8")
            texto = limpar(bruto)                     # re-limpeza idempotente
            if texto != bruto:
                destino.write_text(texto, encoding="utf-8")
            origem = "cache local"
        else:
            try:
                texto = limpar(baixar(gid))
            except Exception as exc:                  # noqa: BLE001
                print(f"  [FALHA] {slug} (id={gid}): {exc}")
                continue
            destino.write_text(texto, encoding="utf-8")
            origem = "download"
            time.sleep(1)                             # cortesia com o Gutenberg
        n_palavras = contar_palavras(texto)
        metadata[slug] = {
            "gutenberg_id": gid,
            "idioma": idioma,
            "nivel": nivel,
            "titulo": titulo,
            "palavras": n_palavras,
            "bytes": destino.stat().st_size,
            "origem": origem,
            "url": f"https://www.gutenberg.org/ebooks/{gid}",
        }
        marca = "OK " if origem == "download" else "CCH"
        print(f"  [{marca}] {slug:<22} {nivel:<14} {idioma}  {n_palavras:>7} palavras")

    (OUT_DIR / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n{len(metadata)}/{len(tudo)} textos em {OUT_DIR}")

    niveis = {}
    for v in metadata.values():
        niveis.setdefault(v["nivel"], []).append(v["titulo"])
    for nivel in ("simples", "intermediario", "complexo"):
        obras = niveis.get(nivel, [])
        print(f"  {nivel:<14}: {len(obras)} -> {', '.join(obras)}")

    return 0 if len(metadata) >= 4 else 1


if __name__ == "__main__":
    sys.exit(main())
