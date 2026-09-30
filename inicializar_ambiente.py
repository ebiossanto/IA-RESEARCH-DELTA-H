import os
import re
import unicodedata


def sanitizar_nome(nome):
    """Remove acentos, espaços e caracteres especiais -> nome seguro de pasta."""
    sem_acentos = "".join(
        c for c in unicodedata.normalize("NFKD", nome) if not unicodedata.combining(c)
    )
    seguro = re.sub(r"[^a-zA-Z0-9]+", "_", sem_acentos.strip().lower())
    return seguro.strip("_")


def inicializar_ambiente_isolado(nome_projeto):
    nome_pasta = sanitizar_nome(nome_projeto)

    # Lista de subdiretórios baseados no System Prompt matemático
    subdiretorios = [
        f"{nome_pasta}/src/julia",
        f"{nome_pasta}/src/python",
        f"{nome_pasta}/assets/geogebra",
        f"{nome_pasta}/proofs",
        f"{nome_pasta}/paper",
        f"{nome_pasta}/paper/figures",
        f"{nome_pasta}/data",
        f"{nome_pasta}/notebooks",
    ]

    print(f"📦 Criando ambiente científico isolado para: '{nome_pasta}'...\n")

    for pasta in subdiretorios:
        os.makedirs(pasta, exist_ok=True)
        print(f"   ✓ [Criado] {pasta}")

    # Arquivo README estrutural
    with open(f"{nome_pasta}/README.md", "w", encoding="utf-8") as f:
        f.write(
            f"# Projeto de Pesquisa: {nome_projeto}\n\n"
            "Ambiente isolado gerado automaticamente via OpenCode.\n"
        )

    # Esqueleto do LaTeX
    with open(f"{nome_pasta}/paper/main.tex", "w", encoding="utf-8") as f:
        f.write(
            "% Padrão de Publicação Científica\n"
            "\\documentclass[11pt,a4paper]{article}\n"
            "\\usepackage[utf8]{inputenc}\n"
            "\\usepackage{amsmath,amssymb,amsthm}\n"
            "\\usepackage{graphicx}\n"
            "\n"
            "\\begin{document}\n"
            f"\\title{{{nome_projeto}}}\n"
            "\\maketitle\n"
            "\n"
            "\\end{document}\n"
        )

    print(
        f"\n✅ Pronto! O projeto '{nome_pasta}' está totalmente isolado e pronto "
        "para receber códigos em Python, Julia e LaTeX."
    )
    return nome_pasta


if __name__ == "__main__":
    # --- Execução de Teste ---
    # Substitua pelo tema da sua primeira pesquisa real
    nome_do_seu_estudo = "Delta H"
    inicializar_ambiente_isolado(nome_do_seu_estudo)
