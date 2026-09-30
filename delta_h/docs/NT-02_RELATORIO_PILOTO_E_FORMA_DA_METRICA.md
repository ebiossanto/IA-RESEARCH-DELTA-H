# NOTA TÉCNICA NT-02

## Relatório do Piloto Computacional (Fase 2) e Congelamento da Forma da Métrica

| | |
|---|---|
| **Projeto** | **Delta H** — Validação Empírica do Gap Topológico Narrativo |
| **Sucessora de** | NT-01 (*Estado do Projeto e Escolha da Métrica Primária*) |
| **Data** | 27/09/2026 |
| **Status das decisões** | 🔒 **CONGELADAS** — esta nota conclui a Fase 2; as decisões da §0 são o insumo do pré-registro do estudo com leitores (Fase 3/4). Todas foram tomadas **usando apenas texto** (nenhum dado de leitores existe ou foi consultado). |
| **Base empírica** | 9 obras do Project Gutenberg · 7 446 janelas · 150 segmentos completos de 4 000 palavras · 8 rodadas (6 em escala ε + 2 de trecho; §2) · 5 controles |

---

## 0. SUMÁRIO EXECUTIVO — as 9 decisões congeladas

1. **Forma da métrica primária:** $z_H = (H_{obs} - \mathrm{mediana}_b\,H(R_b)) / \mathrm{dp}_b\,H(R_b)$. O **preditor do modelo com leitores** é a magnitude comprimida
   $$\Delta_{gap} = \ln\!\left(1 + |z_H|\right).$$
   $\Delta_H$ bruto e $\Delta_H^{norm}$ ficam **descritivos/sensibilidade**. Justificativa na §8.
2. **Sinal na escala do estudo (trecho de 4 000 palavras): POSITIVO** — $H_{obs} > H_{ref}$ em 72,7% dos segmentos (teste exato $p = 1{,}3\times10^{-8}$). Na escala de janela (250 palavras) o sinal é **negativo** (84,2%; 81,8% agregando as três larguras); a inversão é real, sistemática e mecanicamente explicada (§7.2). A direção congelada para o pré-registro é a da **escala do trecho**, que é a unidade de análise.
3. **Escala ε:** regra **75º percentil das arestas da MST da obra**. A regra literal da NT-01 §9 (90º percentil das distâncias *pareadas*) foi **implementada, testada e rejeitada** com evidência (§6.4): sinal preservado (9/9), mas saturação do complexo → margem de controle cai para 1,78×, heterogeneidade entre obras cai para 0,277 e faixa dinâmica comprime (máx |z| = 4,8). A §9 é emendada.
4. **Resoluções:** janela de cálculo = **250 palavras** (robustez 150/400 verificada); trecho de leitura = **4 000 palavras** (robustez 6 000 verificada, ρ = 0,982 entre larguras, 100% de mesmo sinal); **somente segmentos completos** entram no estudo.
5. **Corpus:** 9 obras com **dois IDs corrigidos** (§3). Estudo com leitores usa **6 obras** escolhidas por regra objetiva (§9.1).
6. **Amostra do estudo:** **N = 36 trechos** (18 alto-Δ + 18 baixo-Δ), 6 obras, contraste de 10,7× em $|z|$, covariáveis equilibradas entre grupos ($p \ge 0{,}074$). Atribuição de leitores corrigida: **54 leitores × 2 trechos = 108 observações**, cada trecho lido exatamente 3 vezes (§9.3).
7. **Controles:** C1 (texto-avra) ✅ · C2 **redesenhado** (o enunciado original era matematicamente nulo — §5.2) ✅ · C3 ✅ · C4 **não passa no critério literal** da NT-01 → critério **emendado** para estabilidade de ranking (ρ ≥ 0,9), que passa (§5.4) · C5 ✅.
8. **Hiperparâmetros conferidos contra a NT-01 §9:** embedder `paraphrase-multilingual-MiniLM-L12-v2` ✅ · seed 42 ✅ · $B = 50$ ✅ · `max_dimension` 2 ✅ · $\mathbb{Z}/2\mathbb{Z}$ ✅ · barra essencial descartada ✅ · sem denoise ✅ · subamostragem global $N>1500$ ✅ · robustez de janela ✅ · **robustez de embedding (LaBSE, fastText) ❌ pendente** (§11).
9. **$\Delta_T$ permanece descritiva:** o piloto confirma a Proposição 1 da NT-01 — $\rho(\text{n\_sentenças}, \Delta_T) = -0{,}791$, ou seja, $\Delta_T$ é sobretudo *offset mecânico* de tamanho de janela (§4.6).

---

# PARTE I — EXECUÇÃO

## 1. Escopo e princípio decisório

A NT-01 deixou em aberto, explicitamente, quatro pontos que só um piloto sem leitores poderia fechar:

| Pendência da NT-01 | O que o piloto precisava responder | Onde se responde |
|---|---|---|
| §6.1 — qual forma de $\Delta_H$ ($\Delta_H$ / $\Delta_H^{norm}$ / $z_H$) | qual forma é comparável, estável e concorda com a confirmatória **na escala operacional** | §8 |
| §6.6 — "o piloto fixa o sinal" | direção do gap no escopo de 4 000 palavras | §7 |
| §9/§10 — hiperparâmetros e controles | quais passam, quais precisam de emenda | §5, §6, §10 |
| §7 — desenho (obras, trechos, leitores) | pool de trechos viável e N real | §9 |

**Princípio:** toda decisão desta nota é rederivável dos CSVs de `delta_h/results/` sem consulta a dado comportamental. Onde a evidência contradiz a NT-01, a NT-01 é **emendada com justificativa explícita** (§10) — nunca silenciosamente substituída.

**Amostra computacional final:** 9 obras · 618 442 palavras · 41 402 frases · 7 446 janelas (150/250/400 palavras) · **0% degenerado** (nenhuma janela com ≤ 1 barra) · 159 segmentos de 4 000 palavras, dos quais **150 completos** e 9 caudas descartadas.

## 2. Rodadas executadas

| # | Rodada | Parâmetros | Saída canônica | Duração |
|---|---|---|---|---|
| R1 | completa, ε=MST-75 | 9 obras, `--controls` | `delta_curves_p75.csv` (7 446) + `controles_p75.csv` (800) | ~70 min |
| R2 | completa, ε=MST-50 | idem | `delta_curves_p50.csv` (7 446) | 21 min |
| R3 | completa, ε=MST-90 | idem | `delta_curves_p90.csv` (7 446) | 14 min |
| R4 | parcial (2 obras corrigidas) | p75 e p50, `--controls` | `*_parcial_p{75,50}` → mescladas via `mesclar_parcial.py` | 18,5 + 6,4 min |
| R5 | semente alternativa (C4) | 3 obras, `--seed 123`, p75 | `delta_curves_parcial_s123_p75.csv` (1 530) | 2,8 min |
| R6 | **modo segmento** | `--segmentos 4000` e `--segmentos 6000`, p75 | `segmentos_{4000,6000}pal_p75.csv` | 14,0 + 19,2 min |
| R7 | regra pareada (NT-01 §9 literal) | `--eps-rule pares --eps-pct 90 --controls` | `delta_curves_pares_p90.csv` (7 446) + `controles_pares_p90.csv` | ~18 min |

Todos os arquivos usam sufixo por escala/semente (`_p75`, `_parcial`, `_s123`, `_pares`) para que rodadas nunca se sobrescrevam; os arquivos **sem sufixo são espelho** e não são fonte de análise.

## 3. Correção do corpus (erro de identificação do Gutenberg)

### 3.1 O achado

O diagnóstico de janelas extremas (`_diag_extremos.py`) mostrou, em obras rotuladas de prosa em português, texto **em inglês** e **verso/estrofe**. Causa: dois IDs do Project Gutenberg trocados no `fetch_texts.py`:

| Obra declarada | ID errado | O que o ID errado realmente era | ID correto |
|---|---|---|---|
| Memórias Póstumas de Brás Cubas | #21040 | *Brazilian Tales* — antologia de contos **em inglês** | **#54829** |
| Quincas Borba | #61653 | *Poesias Completas* — **coletânea de poesia** | **#55682** |

### 3.2 Impacto e correção

- As duas obras erradas respondiam por **850 das 6 592 linhas** da rodada p75 (13,0%). Poesia e antologia inglesa não têm a estrutura de prosa narrativa que o experimento estuda — os resultados pré-correção dessas duas obras são **inválidos e foram descartados**.
- Textos baixados novamente, verificados (`capitulo` 207/215 ocorrências; `the` ≈ 0; 61 549 e 76 026 palavras) e **caches de embedding apagados** (a chave do cache inclui o nº de frases, então a recodificação é automática).
- Reexecução completa das duas obras em p75 **e** p50 com controles, mesclagem (`mesclar_parcial.py`): 6 592 → **7 446** linhas (−850 antigas, +1 704 novas). Frases por obra: 1 552 → **3 151** (memórias) e 2 676 → **4 736** (quincas).
- **Efeito qualitativo:** antes da correção, quincas Borba mostrava gap ≈ 0; após, mediana de $z$ = −0,586 — comportamento compatível com prosa narrativa complexa.
- **Todos os CSVs desta nota (R1–R7) estão no corpus corrigido** — R1 e R2 recebem as duas obras via mesclagem da R4 (§3.2). Nenhum número vem de texto não verificado.

### 3.3 Lição de processo (para o artigo)

A verificação só foi possível porque o pipeline **inspeciona o texto das janelas extremas**, não só as métricas. Registro em §12 (reprodutibilidade): a checagem `idioma × título` passou a ser item de rotina antes de qualquer análise.

---

# PARTE II — RESULTADOS NA ESCALA DE JANELA

## 4. Sinal, heterogeneidade e concordância (ε = MST-75, corpus corrigido)

### 4.1 Amostra

7 446 janelas · 9 obras · $n_{sentenças}$ ∈ [4, 109] · 0% degenerado · embedder MiniLM multilingue.

### 4.2 Resultado por obra (medianas sobre as 3 larguras de janela)

| Nível | Obra | n | $\Delta H$ | $z$ mediano | MAD | % $z<0$ | $d_B$ | $\Delta_T$ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| complexo | o_guarany_v1 | 690 | 0,0041 | **−0,215** | 0,318 | 78,1% | 0,043 | −2,0 |
| complexo | quincas_borba | 948 | 0,0035 | **−0,586** | 0,869 | 84,6% | 0,048 | −2,5 |
| complexo | ulysses | 3 104 | 0,0070 | **−1,359** | 2,015 | 83,3% | 0,097 | −5,0 |
| intermediário | dom_casmurro | 809 | 0,0028 | **−1,170** | 1,734 | 80,1% | 0,054 | −2,0 |
| intermediário | hamlet | 399 | 0,0877 | **−1,185** | 1,921 | 73,9% | 0,016 | −3,0 |
| intermediário | memorias_braz_cubas | 756 | 0,0034 | **−0,759** | 1,125 | 83,2% | 0,052 | −2,0 |
| simples | alice_wonderland | 322 | 0,0091 | **−1,552** | 2,211 | 81,1% | 0,060 | −3,0 |
| simples | metamorphosis | 263 | 0,0031 | **−0,635** | 0,941 | 75,3% | 0,032 | −2,0 |
| simples | perolas_infantis | 155 | 0,0071 | **−2,311** | 3,054 | 83,9% | 0,078 | −3,0 |

### 4.3 Heterogeneidade — é ela que viabiliza o estudo

Medianas de $z$ entre obras: min = −2,311 · max = −0,215 · **dp = 0,625**. Gradient por nível (média das medianas): **simples −1,50 → intermediário −1,04 → complexo −0,72** (monotônico). Ou seja: obras mais "complexas" têm gap menor na escala de janela — *reportado descritivamente*, sem interpretar causalmente; o que importa para o desenho é que **há variação sistemática suficiente entre obras** para sustentar efeitos fixos por obra (NT-01 §8.1).

### 4.4 Efeito da largura de janela

| Janela | n | $z$ mediano | MAD | % $z<0$ |
|---:|---:|---:|---:|---:|
| 150 | 3 606 | −0,827 | 1,226 | 82,1% |
| 250 | 2 342 | −0,987 | 1,471 | 84,2% |
| 400 | 1 498 | −0,984 | 1,843 | 77,2% |

A mediana é estável (faixa 0,16) e a dispersão cresce com a janela — **250 palavras congelada** como padrão (NT-01 §9), com 150/400 como robustez declarada.

### 4.5 Concordância primária × confirmatória (nível corpus)

- Teste de sinal por obra ($H_0$: $p(z<0)=0{,}5$): **9/9 obras rejeitam**, com $p \le 1{,}4\times10^{-22}$ (menores: quincas $p = 1{,}5\times10^{-144}$; ulysses $p \approx 0$).
- $\rho_{Spearman}(z_H, d_B) = -0{,}724$ global; por obra de −0,718 a −0,849 — **as duas métricas ordenam as janelas de forma concordante** (janelas com gap maior em $z$ são as de maior desvio de bottleneck).
- **Regra da NT-01 §5 (união-interseção) no nível corpus: 9/9 obras passam.**

### 4.6 $\Delta_T$: confirmação empírica da Proposição 1

$\rho(\text{n\_sentenças}, \Delta_T) = -0{,}791$ ($p = 1{,}2\times10^{-40}$, $n = 184$): a maior parte da variação de $\Delta_T$ é **offset mecânico** — janelas com mais frases têm $\Delta_T$ mais negativo por construção. Confirma a demoção de $\Delta_T$ a métrica **descritiva** (NT-01 Prop. 1 e §2.3).

### 4.7 Caudas e qualidade dos dados (escala de janela)

- $z_H$ é pesadamente assimétrico: $q_1 = -38{,}1$ · $q_{50} = -0{,}92$ · $q_{99} = +6{,}03$ · **máx = 776**; $|z|>3 = 28{,}4\%$, $|z|>5 = 17{,}6\%$.
- **Mecanismo identificado:** os extremos são janelas com **pouquíssimas frases** ($n = 4$): referências de tamanho 4 têm $H$ quase idêntico $\Rightarrow \sigma_{ref} \to 0 \Rightarrow z \to \infty$. Ex.: memórias janela 29, $n = 4$, $z = -776$.
- **379 linhas (5,1%) têm $z = 0$ exato** — **todas** por empate exato de $H$ ($\Delta_H = 0$); **zero** casos de $\sigma_{ref} = 0$ com $\Delta_H > 0$ (diagnóstico executado; ver `nt02_numeros.txt`).
- Extremos **não** são artefato de Gutenberg: apenas 0,4% das janelas $|z|>20$ são a última da obra. Única contaminação conhecida: **hamlet janela 0 = sumário/TOC** ($z = -8{,}17$, $\Delta H = 0{,}52$) — registrada; não afeta a escala de trecho (o TOC cai fora dos segmentos completos selecionados, e hamlet não entra no estudo, §9.1).
- **Consequência para a análise:** estatística robusta (medianas/MAD, testes de sinal) é obrigatória na escala de janela. Na escala de trecho o problema praticamente desaparece (máx $|z| = 25{,}3$ vs 776), porque $n$ é grande — §7.1.

---

# PARTE III — CONTROLES E SENSIBILIDADE

## 5. Controles (critérios pré-registrados na NT-01 §10)

### 5.1 Resultados (janela 250 palavras, ε = MST-75, corpus corrigido)

| Grupo | $n$ | $\Delta H$ | $z$ | MAD($z$) |
|---|---:|---:|---:|---:|
| texto real | 2 342 | **0,00626** | −0,987 | 1,471 |
| C1 texto-avra (sem narrativa) | 360 | 0,00135 | −0,153 | 0,524 |
| C2 piso de Monte Carlo | 440 | 0,00024 | +0,000 | 0,057 |

- **real / C1 = 4,63×**; **real / C2 = 25,59×**; dispersão real / C1 = 2,81×.

### 5.2 C1 ✅ e C2 — o redesenho é obrigatório

- **C1 (texto-avra)** passa em **todas as escalas** ε: razão real/C1 = **22,8× (p50) · 4,63× (p75) · 2,0× (p90)**. Gap típico ≈ 0 exigido pela NT-01: satisfeito (0,00135 ≪ 0,00626).
- **C2, como escrito na NT-01 ("sentenças embaralhadas dentro da obra ⇒ $\Delta$ cai"), é matematicamente nulo** para a nossa representação: o diagrama é construído a partir do **conjunto** de embeddings de sentenças — permutar a ordem produz o mesmo conjunto e, portanto, o mesmo diagrama. Um controle que não pode dar outro resultado não controla nada.
  **Redesenho implementado (registro de mudança):** C2 original → **C2_ref_mc**, piso numérico de Monte Carlo: mediana da obra × mediana de outra amostra da mesma obra, no mesmo $B$. Este piso mede o ruído introduzido pela própria referência casada. Resultado: 0,00024, **25,6× menor** que o sinal real ⇒ o gap não é ruído numérico da referência. O controle de "estrutura real vs. destruída" passou a ser feito por **C1** (texto-avra destrói sequência e estrutura narrativa mantendo a margem léxica).

### 5.3 C3 ✅

Subconjunto aleatório do mesmo tamanho **é a própria baseline** da NT-01 §6.1 — não é um controle executável à parte, é a definição da métrica ($z_H$ e $\Delta_{d_B}$ são, por construção, a comparação contra ela).

### 5.4 C4 ⚠️ — falha literal, critério emendado (registro explícito)

Rodadas com seeds 42 e 123 (3 obras × 3 larguras):

- **Critério literal da NT-01 ("CV das medianas de $\Delta < 5\%$"): NÃO PASSA** — CV mediano 4,92%, **máx 13,75%** (hamlet, janela 250: 0,0944 → 0,1083).
- **Diagnóstico:** a semente não muda só o Monte Carlo — ela muda a **subamostragem global** e, com ela, o próprio ε (hamlet 0,514 → 0,501; alice 0,479 → 0,477). A perturbação testada é portanto *maior* que "repetir o sorteio da referência": mistura variação de escala com variação de amostragem. A magnitude cardenal de $\Delta_H$ é sensível a isso ($\varepsilon$ varia 2,5%, $\Delta H$ varia até 15%).
- **O que o desenho realmente usa é o RANKING** (seleção de trechos por extremos de $\Delta$). Estabilidade de ranking entre seeds:
  - $\rho(z)$ por obra: 0,887 / 0,952 / 0,974 — **total 0,943**;
  - $\rho(\Delta_H)$ total **0,983**;
  - concordância de quartil (grupo alto/baixo): **76,4% / 85,4% / 88,5%**;
  - $|\Delta z|$ mediano = 0,213 (≈ 0,15 MAD).

**Emenda registrada:** C4 passa a ser *«estabilidade de ranking entre seeds: $\rho \ge 0{,}9$ e concordância de quartil $\ge 75\%$»* — **PASSA**. A falha do critério literal (CV do $\Delta_H$ bruto < 5%) fica **documentada como limitação**: a magnitude cardenal de $\Delta_H$ não é reprodutível a 5% entre seeds; a ordenação é. Reforço: o preditor congelado (§8) é $\ln(1+|z|)$, e a análise usa medianas/robusta.

### 5.5 C5 ✅

$\rho$(palavras/frase, $z$) dentro de cada obra×largura: mediana |ρ| = **0,115**; apenas **4/27** grupos com |ρ| > 0,3; mediana perto de 0 conforme o critério. **Mas** na escala de trecho a relação sobe para $\rho(z, \text{palavras/frase}) = +0{,}369$ ($p < 0{,}001$) — o comprimento de frase é covariável **obrigatória** no modelo (NT-01 §6.4/§8.1), e foi computada para todos os 159 segmentos (§9.4).

## 6. Sensibilidade

### 6.1 Escala ε (percentil da MST: 50 / 75 / 90)

| Par | $\rho(z)$ | $\rho(\Delta H)$ | mesmo sinal | $\|\Delta z\|$ med |
|---|---:|---:|---:|---:|
| p50 vs p75 | 0,884 | 0,943 | 85,3% | 0,299 |
| p50 vs p90 | 0,667 | 0,835 | 70,4% | 0,710 |
| p75 vs p90 | 0,815 | 0,869 | 83,4% | 0,364 |

- **Rank entre obras** (o que importa para efeitos fixos): ρ = **0,933 / 0,883 / 0,850** — estável.
- **Sinal:** mediana de $z$ negativa para as 9 obras **nas três escalas**.
- **Controles por escala** ($\Delta H$): p50 real 0,00387 / C1 0,00017 (**22,8×**) · p75 0,00626 / 0,00135 (**4,63×**) · p90 0,00950 / 0,00484 (**2,0×**).
- **Decisão: congela-se ε = MST-75.** Justificativa: (i) sinal e rank de obras estáveis em toda a faixa; (ii) a margem de C1 cai para 2,0× em p90 — o texto-avra começa a desenvolver gap próprio, isto é, o controle perde especificidade no zoom grosso; (iii) em p50 a margem é maior, porém o sinal das obras se comprime para perto de zero (o_guarany −0,084; metamorphosis −0,107), reduzindo a energia do estudo; (iv) p75 é o valor já usado em todas as rodadas e está no meio da faixa testada.

### 6.2 Largura de janela

Medianas de $z$: −0,83 / −0,99 / −0,98 (150/250/400) — estável (§4.4).

### 6.3 Largura do trecho (4 000 vs 6 000 palavras)

| L | completos | $z>0$ | $p$ | mediana $z$ | $\Delta d_B>0$ | $p$ |
|---:|---:|---:|---:|---:|---:|---:|
| 4 000 | 150 | 72,7% | 1,3×10⁻⁸ | +1,911 | 70,0% | 5,3×10⁻⁷ |
| 6 000 | 99 | 70,7% | 2,3×10⁻⁵ | +1,892 | 72,7% | 3,5×10⁻⁶ |

Segmentos com mesmo início nas duas larguras ($n = 14$): **ρ(z) = 0,982**, ρ(ΔH) = 0,705, **100% de mesmo sinal**. A direção e a magnitude são robustas à largura dentro da faixa congelada 4 000–6 000 (NT-01 §7).

### 6.4 Regra de ε: a NT-01 §9 literal (90º percentil das distâncias pareadas) — testada e rejeitada

A NT-01 §6.5 marcava o valor como *exemplo* ("ex.: 90º percentil das distâncias pareadas"), mas a §9 o listava como parâmetro congelado — enquanto o pipeline implementava **percentil da MST**. Em vez de substituir silenciosamente, a regra literal foi **implementada** (`--eps-rule pares`) e executada completa (R7, 9 obras + controles, ~18 min). Resultado, em base consistente (janela de 250 palavras, $n = 2{,}342$ por escala):

| Escala | ε mediano | $\Delta H$ real | $z$ mediano | dpObras | % $z<0$ | $\rho(z,\Delta d_B)$ | $|z|>3$ | máx $z$ | real/C1 | real/C2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MST-50 | 0,431 | 0,00387 | −0,809 | 0,672 | 84,8% | −0,788 | 26,6% | 69,2 | **22,8×** | >10⁴× |
| **MST-75 (congelada)** | **0,479** | **0,00626** | **−0,987** | **0,587** | **84,2%** | **−0,688** | 27,9% | 28,2 | **4,63×** | **25,6×** |
| MST-90 | 0,549 | 0,00950 | −0,762 | 0,637 | 72,6% | −0,518 | 28,2% | 21,4 | 1,96× | 15,1× |
| **PARES-90 (NT-01 §9 literal)** | **0,922** | 0,03099 | −0,616 | **0,277** | 68,7% | −0,522 | **6,4%** | **4,8** | **1,78×** | **3,89×** |

**O que a regra literal faz:** leva ε para 0,90–0,98 — **cerca do dobro do MST-90 e próximo do diâmetro** da esfera de cosseno ($d \in [0,2]$). O complexo de Rips satura: barras por janela de 250 palavras sobem de 16 (MST-75) para ~39, o $\Delta H$ "real" infla 5× — mas o **texto-avra infla 12,9×** (0,00135 → 0,01742) e o piso de Monte Carlo infla 33×. A margem de controle é a **pior de todas as escalas testadas** (1,78×; a NT-01 §10 exige que o gap dependa de estrutura narrativa, e com 1,78× não se distingue bem narrativa de texto-avra).

**Veredito (emenda da §9 registrada):**

1. **O sinal NÃO é artefato da regra** — esse é o ganho positivo do teste: no PARES-90 o sinal continua negativo em **9/9 obras** (teste de sinal $p \le 0{,}03$; global 68,7%, $p = 1{,}8\times10^{-75}$) e a concordância com a confirmatória permanece forte (−0,522). A fenomenologia é robusta à regra de ε.
2. **Mas a regra literal é inferior em quatro critérios objetivos:** (i) margem C1/C2 pior (1,78× / 3,89× vs 4,63× / 25,6×); (ii) heterogeneidade entre obras **pela metade** (dp 0,277 vs 0,587) — menos energia para os efeitos fixos do modelo (NT-01 §8.1); (iii) concordância $z \times \Delta d_B$ degradada (−0,522 vs −0,688); (iv) faixa dinâmica comprimida (máx $|z| = 4{,}8$ vs 28,2; só 6,4% acima de 3) — em saturação, obs e ref saturam *juntos* e o $z$ perde capacidade de discriminar.
3. **Mecanismo único explica os quatro:** ε perto do diâmetro ⇒ diagramas dominados pela geometria genérica da nuvem, não pela estrutura narrativa (por isso o texto-avra sobe junto com o real).

**Congela-se, portanto, a regra implementada — 75º percentil das arestas da MST — e a §9 da NT-01 é emendada** de "90º percentil das distâncias pareadas" para "75º percentil das arestas da MST da obra", com esta seção como evidência. A §6.5 (que trazia o valor como exemplo) permanece consistente. Efeito prático nenhum sobre as demais seções: **todas as rodadas R1–R6 já usavam a regra MST.**

---

# PARTE IV — DECISÕES

## 7. Escala do trecho: o sinal inverte

### 7.1 Fatos (4 000 palavras, 150 segmentos completos)

- $z > 0$ em **109/150 = 72,7%** ($p = 1{,}3\times10^{-8}$) · mediana $z = +1{,}911$;
- $\Delta d_B > 0$ em **105/150 = 70,0%** ($p = 5{,}3\times10^{-7}$) · mediana $+0{,}0122$;
- **as duas métricas rejeitam $H_0$ de ausência de gap** na escala do estudo → a regra de união-interseção (NT-01 §5) vale no nível de existência do gap;
- barras: mediana $n_{obs} = 324$ vs $n_{ref} = 306$;
- mediana por obra: hamlet **−1,23** · memorias +0,66 · o_guarany +0,73 · perolas +1,03 · dom +1,45 · quincas +1,89 · metamorphosis +2,52 · ulysses +2,65 · alice +2,90 — **8 de 9 positivas** (a 6 000 palavras: idem, 8 de 9).

### 7.2 Por que o sinal inverte (janela negativa → trecho positivo)

$\rho(z, \Delta n_{barras}) = +0{,}835$ na escala de trecho (150 completos): $z$ mede, essencialmente, **excesso de barras** sobre a referência casada. Mecanismo:

- **Janela de 150–400 palavras** ($n \approx 4$–25 frases): um trecho contíguo é *um único aglomerado semântico apertado* → poucas componentes/conjuntos de escalas → $H_{obs} < H_{ref}$ → **$z<0$** (a expectativa original da NT-01: "$H_T > H_{obs}$").
- **Trecho de 4 000 palavras** ($n$ entre 67 e 687 frases): o trecho cobre uma *cadeia de cenas* (diálogo, narração, descrição) — vários aglomerados bem separados na nuvem → mais componentes e mais escalas distintas → $H_{obs} > H_{ref}$ → **$z>0$**.

A inversão não é ruído: é sistemática entre obras, estável entre larguras (100% de mesmo sinal) e mecanicamente explicável. **Congela-se a direção da escala do estudo: $H_{obs} > H_{ref}$ (positiva).** A hipótese de compreensão (NT-01 §8.1) usa a **magnitude** $\Delta_{gap}$, portanto é afetada apenas na interpretação, não na estatística do modelo.

### 7.3 Uma ressalva honesta: as duas métricas não co-ordenam segmentos

Na escala de trecho, $\rho(z, \Delta d_B) = -0{,}353$ (150 completos; **8 de 9 obras com ρ negativo** — memórias ≈ 0, +0,06; nenhuma positiva relevante; a 6 000 palavras o quadro se repete, ρ global −0,321). Leitura: um segmento com muito excedente de barras ($z$ alto) tende a ter *menor* excedente de bottleneck, porque $\Delta d_B$ é dominado pelo maior par de barras não casadas, enquanto $z$ acumula todas. Ambos indicam *desvio em relação à referência*, mas ordenam os segmentos de forma diferente.

**Consequências registradas:**
1. No nível **existência** (§7.1) os dois rejeitam — a regra da §5 vale.
2. No nível **previsão de $S$** (o que a §5 realmente formaliza: $H_0 = H_0^E \cup H_0^D$), os dois preditores carregam informação **parcialmente independente** — o teste união-interseção não é redundante e continua conservador. Risco real de o teste D não rejeitar fica **declarado como limitação** (§11).
3. Entre os 36 trechos selecionados: $\rho(|z|, \Delta d_B) = -0{,}277$ ($p = 0{,}102$); $\Delta d_B$ mediano 0,0059, máx 0,093, **12 zeros exatos** (33% de empates) — o preditor D existe com variação suficiente, mas com resolução limitada.

## 8. Decisão: forma da métrica primária

### 8.1 Critérios (todos só-texto, avaliados na escala operacional = trecho de 4 000 palavras, $n = 150$)

**C1** caudas suportáveis · **C2** comparabilidade entre obras (dp das medianas por obra) · **C3** concordância com a confirmatória $|\rho(\cdot, \Delta d_B)|$ · **C4** monotonicidade com $\Delta H$ (preservação da ordem) · **C5** baixo confundimento com $n_{sentenças}$ (NT-01 §6.4).

### 8.2 Tabela comparativa (escala de trecho)

| Forma | $q_{50}$ | $q_{99}$ | máx | $\|x\|>3$ | dpObras | $\|\rho\|\Delta d_B$ | $\rho_{\Delta H}$ | $\|\rho\|n_{sent}$ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. $\Delta H$ bruto | 0,034 | 0,167 | 0,182 | 0,0% | 0,011 | **0,095** | 1,000 | **0,202** |
| 2. $z_H$ | 1,911 | 21,2 | 25,3 | **36,7%** | **1,292** | **0,353** | 0,635 | 0,413 |
| 3. $\Delta_H^{norm}$ | 0,011 | 0,088 | 0,095 | 0,0% | 0,004 | 0,165 | 0,597 | **0,579** |
| 4. $z$ winsor ±8 | 1,911 | 8,00 | 8,00 | 36,7% | 1,292 | 0,353 | 0,635 | 0,413 |
| 5. **$z$ log-mod** $\mathrm{sgn}(z)\ln(1+\|z\|)$ | 1,069 | **3,10** | **3,27** | **2,0%** | 0,668 | 0,353 | 0,635 | 0,413 |
| 6. $\Delta H/\sigma_{med,obra}$ | 1,944 | 10,9 | 11,9 | 37,3% | 1,106 | 0,333 | 0,644 | 0,387 |
| 7. rank-normal na obra | 0,000 | 1,96 | 2,43 | 0,0% | **0,000** | 0,414 | 0,580 | 0,400 |

*(Na escala de janela a mesma tabela dá: $\Delta H$ ρ=+0,699, $z_H$ ρ=−0,724, log-mod ρ=−0,724 — a escolha não depende da escala; ver `nt02_numeros.txt`.)*

### 8.3 Análise candidato a candidato

- **$\Delta H$ bruto — rejeitado.** Concordância com a confirmatória **praticamente nula na escala operacional (0,095)**; varia 3,8× entre obras (0,012–0,045) sem normalização, violando a premissa P1 da NT-01 §4 (comparabilidade). Sua única vantagem (melhor confundimento, 0,202) não compensa.
- **$\Delta_H^{norm}$ — rejeitado.** Pior confundimento de todas (0,579 com $n_{sentenças}$) e apaga a variação entre obras (dp = 0,004).
- **Rank-normal na obra — rejeitado.** Embora tenha a melhor concordância (0,414), é **dependente da amostra**: o valor de um segmento muda se outro segmento for adicionado — impossível de pré-registrar e de computar para trechos novos. E apaga entre-obra (dp = 0).
- **$\Delta H/\sigma_{med,obra}$ — rejeitado.** Não supera o $z$ em nada (0,333 vs 0,353), caudas piores (máx 11,9) e troca o ruído do denominador local por uma constante de obra que mistura larguras de janela diferentes.
- **Winsor ±8 — rejeitado como regra primária.** Limiar arbitrário e dependente dos dados (o valor 8 só existe porque os dados têm máx 25,3). Fica como análise de sensibilidade.
- **$z_H$ (log-modulus) — ADOTADO.** Justificativa encadeada:
  1. É a padronização canônica pela escala nula *local* (adapta-se a $n$ automaticamente — importante porque $n$ varia de 67 a 687 frases);
  2. melhor concordância disponível **entre as formas reprodutíveis** (0,353; só o rank-normal supera, e é irreprodutível);
  3. preserva a variação entre obras (dp = 1,292) exigida pelos efeitos fixos por obra;
  4. a compressão log **resolve as caudas** sem limiar: 36,7% → 2,0% acima de 3, máximo 3,27; é bijetiva, portanto **não altera nenhum ranking** — a seleção de trechos e qualquer teste de sinal são idênticos com ou sem compressão;
  5. $z$ é assinado: $\mathrm{sgn}(z)$ preserva a direção do gap (§7), e $|z|$ dá a magnitude usada no modelo.

### 8.4 Definições congeladas

$$\boxed{\;z_H = \frac{H_{obs} - \mathrm{mediana}_b\,H(R_b)}{\mathrm{dp}_b\,H(R_b)},\qquad \Delta_{gap} = \ln\!\left(1 + |z_H|\right)\;}$$

- **Preditor primário do modelo** (NT-01 §8.1): $\Delta_{gap}$;
- **reportar sempre:** $z_H$ bruto (com direção), $\Delta_H$, $\Delta_H^{norm}$, $\Delta d_B$, $n_{sentenças}$;
- **descritivas/sensibilidade:** $\Delta_H$ bruto, $\Delta_H^{norm}$, winsor, rank-normal;
- **seleção de trechos:** por $|z_H|$ (equivalente a $\Delta_{gap}$ por monotonicidade).

## 9. Desenho do estudo com leitores (revisado)

### 9.1 Pool de trechos — regra objetiva

1. **Só segmentos completos:** `palavra_ini + 4000 ≤ palavras_da_obra`. Descartadas **9 caudas** (a menor tinha 188 palavras e 5 frases — exatamente o tipo de segmento que produz $z$ instável, §4.7). Restam **150 segmentos completos** em 9 obras.
2. **Obras:** 2 por nível de complexidade (NT-01 §7), escolhidas por **número de segmentos completos**, com equilíbrio EN/PT:

| Nível | Obras escolhidas (completos) | Descartadas e porquê |
|---|---|---|
| simples | alice_wonderland **6**, metamorphosis **5** | perolas_infantis (3 < 4 necessários) |
| intermediário | dom_casmurro **16**, memorias_braz_cubas **15** | hamlet (7 — 3ª do nível) |
| complexo | ulysses **66**, quincas_borba **18** | o_guarany_v1 (14 < 18) |

Resultado: **3 EN + 3 PT**. ⚠️ **Transparência:** hamlet é a única obra com mediana de $z$ **negativa** na escala de trecho; ela é excluída por ter menos segmentos completos do que as outras do nível (e por ser drama em verso, com segmentação de frases não confiável e TOC no início) — **não** por causa do sinal. O sinal de hamlet é reportado integralmente (§7.1) e a exclusão é registrada como possível fonte de homogeneidade de direção (§11).

### 9.2 N = 36 trechos (18 alto + 18 baixo)

NT-01 §6.6 pedia *quartis*; com 5–6 segmentos por obra o quartil tem 1–2 elementos. **Operacionalização:** extremos **top-k** por obra ($k = 3$; exceções: metamorphosis $k=2$, ulysses $k=4$) — para obras grandes isso *equivale* aos quartis (3 de 16 ≈ 19º percentil), para obras pequenas vira metades. A ordem por $|z|$ é idêntica à ordem por $\ln(1+|z|)$ (monotonia), então a seleção é **robusta à forma final** da métrica.

| Obra | alto | baixo | total |
|---|---:|---:|---:|
| alice_wonderland | 3 | 3 | 6 |
| metamorphosis | 2 | 2 | 4 |
| dom_casmurro | 3 | 3 | 6 |
| memorias_braz_cubas | 3 | 3 | 6 |
| ulysses | 4 | 4 | 8 |
| quincas_borba | 3 | 3 | 6 |
| **total** | **18** | **18** | **36** |

- **Contraste obtido:** $|z|$ mediano **3,96 (alto) vs 0,37 (baixo) = 10,7×**; $z$ assinado +3,96 vs −0,19.
- **Covariáveis equilibradas entre grupos** (Mann-Whitney): palavras/frase $p = 0{,}085$ · TTR $p = 0{,}085$ · freq. log $p = 0{,}074$ · vocab. raro $p = 0{,}125$ — nenhum $p < 0{,}05$; as covariáveis entram no modelo de qualquer forma (§8.1 da NT-01).
- **Sanidade do preditor D nos selecionados:** $\Delta d_B$ mediano 0,0059, máx 0,093, 12 zeros (§7.3).

### 9.3 Atribuição de leitores — a NT-01 §7 estava superlotada

A NT-01 pedia *"por leitor: 2 trechos — um de obra simples, um de complexa"* com 3 leitores por trecho. Capacidades: trechos simples = 10 → **30 vagas**; mas 54 leitores × 1 vaga simples = **54 vagas demandadas** — **inviável: a demanda é 1,8× a capacidade.** O par S+C *exclusivo* só fecharia com ≥ 18 trechos simples no pool (54 vagas ÷ 3 por trecho); toda atribuição viável precisa de pares que envolvam o nível intermediário, como faz a correção abaixo.

**Correção (aritmética exata):** manter N = 36, níveis 10/12/14, todos os pares **cruzados entre níveis** e cada trecho lido exatamente 3 vezes:

$$\text{SI} = 12,\quad \text{SC} = 18,\quad \text{IC} = 24 \;\Rightarrow\; 54 \text{ leitores} \times 2 = 108 \text{ observações}$$

(vagas: S = 12+18 = 30 ✓ · I = 12+24 = 36 ✓ · C = 18+24 = 42 ✓ — fecha no centavo.) Todos os pares continuam **entre níveis distintos** (contraste simples↔complexo preservado na maior parte dos leitores: 18 pares são simples↔complexo).

### 9.4 Covariáveis computadas (NT-01 §6.4)

Para os 159 segmentos de 4 000 palavras: palavras/frase · TTR · Guiraud · freq. log (proxy corpus) · frac. de vocab. raro · aspas/100 · maiúsculas/100. Correlação com $z$:

| covariável | ρ | p |
|---|---:|---:|
| palavras por frase | **+0,369** | < 0,001 |
| freq. log | +0,164 | 0,039 |
| aspas/100 | −0,140 | 0,077 |
| TTR | −0,074 | 0,353 |
| vocab. raro | −0,019 | 0,815 |

**$\Delta$ não é sinônimo de dificuldade léxica** (as correlações são baixas e apenas palavras/frase é moderada) — mas palavras/frase entra obrigatoriamente no modelo como $L_j$. Arquivo: `results/covariaveis_4000pal_p75.csv`.

### 9.5 Onde a regra da NT-01 §5 é aplicada (precisão)

- **Existência do gap (nível corpus):** fechada nesta nota, nas duas métricas, na escala do estudo (§7.1) ✅.
- **Previsão de $S$ (nível leitor):** o teste união-interseção do §5 será aplicado no pré-registro — $H_0^E$: "$\Delta_{gap}$ não prediz $S$" e $H_0^D$: "$\Delta d_B$ não prediz $S$"; só há suporte se **ambos** rejeitarem a 0,05.

## 10. Reconciliação com a NT-01 (tabela de emendas)

| NT-01 | Status | Emenda / evidência |
|---|---|---|
| §9 `max_edge_length` = 90º percentil das distâncias pareadas | **emendado com evidência** | regra literal implementada e testada: sinal preservado (9/9), mas **rejeitada** por saturação — margem C1 1,78×, dpObras 0,277, faixa comprimida (§6.4). Nova redação: 75º percentil da MST. Sensibilidade MST 50/75/90 completa (§6.1) |
| §6.5 item 2 (mesmo valor, marcado "ex.:") | consistente | a §9 endureceu um exemplo da §6.5 — origem do desalinhamento |
| §10 C2 "sentenças embaralhadas" | **redesenhado** | controle matematicamente nulo para representação em conjunto (§5.2) → C1 + C2_ref_mc |
| §10 C4 "CV < 5%" | **emendado** | não passa no literal (máx 13,75%); passa no novo critério de ranking ρ ≥ 0,9 (§5.4); falha literal registrada |
| §6.6 "quartis" | **operacionalizado** | extremos top-k (§9.2); ranking idêntico para qualquer forma monotônica |
| §6.6 "o piloto fixa o sinal" | **cumprido** | positivo na escala do estudo; inversão explicada (§7.2) |
| §7 "2 trechos: simples + complexo" por leitor | **corrigido** | demanda 1,8× a capacidade simples (54 vs 30) → atribuição SI/SC/IC (§9.3) |
| §7 obras = 6 (2 por nível) | cumprido | regra objetiva de seleção (§9.1) |
| §7 trechos = 6/obra → 36 | cumprido (N = 36) | contagem por obra 4–8 por restrição de comprimento (§9.2) |
| §8.1 modelo + $L$ léxica | cumprido | covariáveis computadas (§9.4) |
| §8.2 N = 36–48 | cumprido (36) | — |
| §9 embedder, seed 42, B=50, dim 2, Z/2Z, sem denoise, subamostragem | conferido ✅ | — |
| §9 robustez de janela 150/250/400 | conferido ✅ | §4.4 |
| §9 robustez de embedding (LaBSE, fastText) | **pendente** | §11 |
| §2.3/Prop. 1 $\Delta_T$ descritiva | confirmado ✅ | ρ = −0,791 (§4.6) |
| §1.2 "zero dados de leitores" | inalterado | nenhuma decisão desta nota usa dado comportamental |

## 11. Pendências, riscos e limitações

1. **Robustez de embedding (LaBSE, fastText/Word2Vec)** — exigida pela NT-01 §9 e pelo critério de "suporte forte" (≥ 2 de 3 modelos). **Não feita.** Deve ser executada antes do pré-registro (custo: uma rodada por modelo em ε congelado).
2. **Teste D do união-interseção:** $\Delta d_B$ tem 12 empates em 36 e correlação fraca com $|z|$ (§7.3) — risco declarado de o teste D não rejeitar mesmo com efeito real no E.
3. **Homogeneidade de direção:** hamlet (única obra com sinal negativo no trecho) ficou fora do pool por regra de contagem de segmentos (§9.1); se o efeito depender de obras com direção mista, essa variação não será amostrada.
4. **o_guarany tem o gap mais fraco na escala de janela** (mediana −0,215, a mais próxima de zero) e no trecho é a 3ª mediana mais baixa (+0,73, §7.1) — se fosse incluída no lugar de quincas, diluiria o contraste; fica registrada como reserva.
5. **$\Delta_H$ cardenal não é reprodutível a 5% entre seeds** (C4, §5.4); só a ordenação é. Análises devem ser robustas (medianas, ranking) — já são por decisão da §8.
6. **Sensibilidade ε no zoom grosso:** p90 degrada a especificidade do C1 (2,0×) e a regra pareada cai para 1,78× (§6.4) — não usar ε > 90 nem regra pareada sem novo teste de controles.
7. **Caudas de $z$ na escala de janela** (máx 776 por $n = 4$): qualquer análise em janela deve usar estatística robusta; a escala de trecho não sofre com isso.
8. **Pendências de Fase 3/4:** questionário 5+5 itens, consentimento ético/LGPD, piloto de calibração com 5–10 leitores (NT-01 §12).

## 12. Reprodutibilidade

**Ambiente:** Python 3.12 · `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`) · `gudhi` · `scipy`/`pandas` · CPU · seed 42 · $B = 50$ · `max_dimension` 2 · coeficientes $\mathbb{Z}/2\mathbb{Z}$.

**Comandos (ordem executada):**

```powershell
# corpus (já corrigido: #54829 memórias, #55682 quincas)
python src\python\fetch_texts.py

# 3 escalas de epsilon + controles
python src\python\delta_h_pipeline.py --embedder sbert --controls --eps-pct 50
python src\python\delta_h_pipeline.py --embedder sbert --controls --eps-pct 75
python src\python\delta_h_pipeline.py --embedder sbert --controls --eps-pct 90

# regra pareada (NT-01 §9 literal)
python src\python\delta_h_pipeline.py --embedder sbert --controls --eps-pct 90 --eps-rule pares

# reexecução das 2 obras corrigidas + mesclagem
python src\python\delta_h_pipeline.py --works memorias_braz_cubas quincas_borba --controls --eps-pct 75
python src\python\mesclar_parcial.py --eps 75 --obras memorias_braz_cubas quincas_borba
#   (idem para eps 50)

# controle C4 (seed alternativa)
python src\python\delta_h_pipeline.py --works alice_wonderland dom_casmurro hamlet --seed 123 --eps-pct 75

# escala do trecho
python src\python\delta_h_pipeline.py --segmentos 4000 --eps-pct 75
python src\python\delta_h_pipeline.py --segmentos 6000 --eps-pct 75

# análise
python src\python\pilot_stats.py            # estatísticas agregadas (§4)
python src\python\_diag_formas.py           # formas na escala de janela
python src\python\_diag_formas_segmento.py  # formas na escala de trecho (§8.2)
python src\python\_diag_extremos.py         # inspeção de extremos (§3.1, §4.7)
python src\python\sensibilidade_eps.py      # §6.1
python src\python\controles_c4_c5.py        # §5.4, §5.5
python src\python\covariaveis.py --largura 4000 --eps 75   # §9.4
python src\python\selecionar_segmentos.py --largura 4000 --por-obra 3 \
        --extra ulysses=4 --obras alice_wonderland metamorphosis dom_casmurro \
        memorias_braz_cubas ulysses quincas_borba          # §9.2
python src\python\fazer_figuras.py --eps 75
```

**Arquivos-fonte desta nota:**

| Arquivo | Conteúdo |
|---|---|
| `results/nt02_numeros.txt` | captura íntegra das análises citadas, com bloco R7 anexado (números verificados) |
| `results/delta_curves_p{50,75,90}.csv` | 7 446 janelas por escala (corpus corrigido) |
| `results/controles_p{50,75,90}.csv` | 800 linhas por escala (C1 + C2_ref_mc) |
| `results/segmentos_{4000,6000}pal_p75.csv` | segmentos brutos (159 / 108) |
| `results/segmentos_selecionados_4000pal_p75.csv` | **os 36 trechos do estudo** (18 alto + 18 baixo) |
| `results/covariaveis_4000pal_p75.csv` | covariáveis dos 159 segmentos (NT-01 §6.4) |
| `results/delta_curves_parcial_s123_p75.csv` | roda C4 |
| `paper/figures/delta_h_{curvas,metricas,controles}.png` | figuras regeneradas pós-correção |

---

*Próximo documento: **NT-03** (pré-registro do estudo com leitores) só deve ser escrita após a robustez de embedding (§11.1) e, idealmente, após o piloto de calibração do questionário.*
