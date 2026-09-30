# NOTA TÉCNICA NT-01
## Estado do Projeto **Delta H** e Escolha da Métrica Primária

| Campo | Valor |
|---|---|
| Projeto | **Delta H** — Validação Empírica do Gap Topológico Narrativo |
| Documento | NT-01 (decisão de projeto / pré-registro preliminar) |
| Data | 2026-09-27 |
| Origem | Decisão técnica assistida; **requer validação do pesquisador** antes da coleta |
| Status das decisões | 🔶 **Propostas** — devem ser congeladas (congelamento = *preregistration*) **antes** de qualquer coleta com leitores |
| **Atualização (27/09/2026)** | ✅ **Fase 2 executada.** Ver **NT-02** (*Relatório do Piloto Computacional e Congelamento da Forma da Métrica*), que **congela** as decisões abertas aqui (forma da métrica, sinal, escala, N) e **emenda** os pontos da §6.5/§6.6/§7/§9/§10 que a evidência contradiz — tabela de reconciliação na NT-02 §10. Esta NT-01 permanece válida como fundamentação; em caso de conflito, vale a NT-02. |

---

## 0. SUMÁRIO EXECUTIVO — as 10 decisões

1. **Métrica primária: `ΔH` = *entropia persistente* do diagrama global menos a do diagrama local** — e **não** a entropia do perfil de Betti do §11 do projeto original (que é cega à magnitude; ver Proposição 2). Mantém-se o nome do trabalho.
2. **Métrica confirmatória: distância de *bottleneck*** `d_B(D_T, D_obs)`. Só se declara suporte à teoria se **ambas** apontarem na mesma direção (teste de união-interseção → nível α preservado).
3. **ΔT (soma ponderada de Betti) e ΔT^pers ficam como descritivas/exploratórias.** ΔT é estatisticamente inválido como preditor isolado (Proposição 1).
4. **Resolução comum:** embeddings L2-normalizados, distância de cosseno ∈ [0,2], um único parâmetro de filtração por obra, mesmo corpo de coeficientes (ℤ/2ℤ) para todas as nuvens.
5. **Referência casada por tamanho:** cada janela de $n$ pontos é comparada a $B\ge50$ subconjuntos aleatórios de $n$ pontos sorteados da **mesma obra** (§6.1). Sem isso, o gap mede *quantidade de pontos*, não *narratividade*.
6. **Unidade de análise = trecho (segmento), não leitor.** O `Δ` só varia entre trechos — tratar leitores como `N` independentes é pseudorreplicação.
7. **Correção de desenho:** perguntas *globais* só são respondíveis sobre o texto **efetivamente lido**. O texto define `S`; a obra define apenas a *seleção* de trechos.
8. **Variável omitida crítica:** dificuldade léxica da janela. Sem controle, `Δ` vira *proxy* de vocabulário difícil.
9. **Amostra alvo: 36–48 trechos × 3 leitores = 108–144 observações** (ver cálculo de poder na §8).
10. **Fase imediata = piloto computacional sem leitores**, para fixar sinal, escala e sensibilidade a hiperparâmetros. A hipótese direcional só é congelada depois dele.

---

# PARTE I — O QUE ESTÁ ACONTECENDO

## 1. Estado atual do projeto

### 1.1 A ideia central (uma frase)

Medir a **distância entre a estrutura topológica global de um texto e a estrutura acessível numa janela local de leitura** — o *gap* — e mostrar que ele **explica o desempenho do leitor**:

```
corr(gap, S) < 0
```

ou seja: quanto mais o trecho local diverge da organização global, pior o leitor reconstrói essa organização.

### 1.2 O que já existe

| Componente | Situação | Evidência |
|---|---|---|
| Formulação teórica | ✅ Pronta | `PROJETO DE VALIDAÇÃO…​.md`, 14 seções, 508 linhas |
| Protocolo experimental | ✅ Esboçado | corpus, questionário, Pearson, regressão, critérios de sucesso |
| Estrutura de pastas | ✅ Criada | `delta_h/{src,proofs,paper,assets}` |
| Nome do trabalho | ✅ Corrigido | pastas, `README.md`, `main.tex` e título do `.md` → **Delta H** |
| Código executável | ❌ Zero | trechos do `.md` são colagens com artefatos (`Mostrar mais linhas`) |
| Textos das obras | ❌ Zero | nenhum `.txt` baixado |
| Dados de leitores | ❌ Zero | tabela do §7 é ilustrativa (3 linhas) |
| Artigo | ❌ Esqueleto | `delta_h/paper/main.tex` |

**Diagnóstico: ≈15% do total — 100% de conceito, 0% de execução.**

### 1.3 O que foi feito nesta sessão

- Localização do projeto (`Desktop\projetos\DeltaH`) e leitura integral do documento.
- Correção do nome para **Delta H** (pasta `delta_h/`, `README.md`, `main.tex`, título do documento).
- Ambiente: **Python 3.12.10 já instalado** (`...\Python312\python.exe`), com `numpy`, `scipy`, `pandas`, `statsmodels`, `matplotlib`. Em instalação: `scikit-learn`, `gudhi`, `networkx`.
- Esta nota técnica (NT-01).

### 1.4 O documento original precisa de saneamento

O `.md` foi colado de um chat anterior e contém: fórmulas duplicadas (`ΔT(r)=CT−Cobs(r)\Delta\_T(r)=…`), LaTeX misturado com Unicode, e blocos truncados (`Mostrar mais linhas`). **Antes de virar artigo, deve ser reescrito a partir desta nota.**

---

# PARTE II — ANÁLISE FORMAL DAS MÉTRICAS CANDIDATAS

## 2. Formalização

### 2.1 Construção básica

Seja um texto $T$ com sentenças $s_1,\dots,s_N$. Seja

$$f:\ s_i \mapsto x_i \in \mathbb{R}^d,\qquad \|x_i\|_2 = 1$$

o modelo de *embeddings* (multilíngue, PT+EN). Distância usada em todo o projeto:

$$d(i,j) = 1 - \langle x_i, x_j\rangle \in [0,2]$$

(normalização L2 **obrigatória** — sem ela, o módulo do vetor contamina a distância e nuvens de obras diferentes deixam de ser comparáveis).

Para uma nuvem de pontos $X$, o complexo de Vietoris–Rips é

$$\mathrm{VR}_\varepsilon(X) = \{\sigma \subseteq X : \operatorname{diam}(\sigma) \le \varepsilon\}.$$

Sua *persistência* produz diagramas $D(X) = \{D_0, D_1, D_2\}$, conjuntos de pares $(b_i, d_i)$ por dimensão de homologia, com comprimento de barra $\ell_i = d_i - b_i$.

**Corpo de coeficientes:** fixar $\mathbb{Z}/2\mathbb{Z}$ para todo o projeto (evita torção, é mais rápido e é o padrão de facto em TDA aplicado). Deve ser explicitado no código e no artigo.

**Barra essencial:** a classe infinita $(0,\infty)$ de $H_0$ **deve ser descartada** antes de qualquer entropia, sob pena de divergência.

### 2.2 As duas grandezas

- **Global** $D_T$: diagrama da obra (ou do trecho lido — ver §6.3).
- **Local** $D_{obs}(r)$: diagrama da janela $W_r$.

O *gap* é a discrepância entre elas. Resta definir **qual função de discrepância**.

---

## 2.3 Candidata A — $\Delta_T = C_T - C_{obs}$, com $C = \sum_k (k+1)\beta_k$

**Definição (§2 do projeto).** Soma ponderada dos números de Betti a um $\varepsilon$ fixo.

> **Proposição 1 (confundimento mecânico).**
> Para qualquer nuvem $X$ com $n$ pontos, se $\varepsilon < \delta_{\min}(X) := \min_{i\ne j} d(x_i,x_j)$, então $\mathrm{VR}_\varepsilon(X)$ contém apenas vértices, logo $\beta_0 = n$ e
> $$C(X) = \sum_k (k+1)\beta_k \;\ge\; \beta_0 = n.$$
>
> *Demonstração.* $\varepsilon < \delta_{\min}$ implica que nenhum par de pontos satisfaz $\operatorname{diam}\{x_i,x_j\}\le\varepsilon$; logo não há arestas, cada ponto é uma componente de conexão, $\beta_0=n$. $\square$

**Consequências (3 defeitos independentes):**

1. **$C$ é pelo menos linear no número de pontos.** Como $n_{obs} \ll n_T$, temos $C_T - C_{obs} \ge n_T - n_{obs} > 0$ **mesmo para texto sem nenhuma estrutura**. O gap é positivo por construção, não por descoberta.
2. **Descontinuidade.** $\beta_k(\varepsilon)$ é uma função escada: um deslocamento arbitrário de $\varepsilon$ (ou um ruído minúsculo em um embedding) pode alterar $\beta_k$ em $\pm1$. $C$ herda essa instabilidade — não há teorema de estabilidade para números de Betti em $\varepsilon$ fixo.
3. **Pesos $(k+1)$ são arbitrários.** Nenhum princípio de invariância os justifica; trocá-los por $(k+1)^2$ ou $2^k$ pode inverter resultados. Isso é um *grau de liberdade do pesquisador* — e, como tal, deve ser evitado na métrica primária.

> **Veredicto:** ❌ **inválida como métrica primária.** Permanece como *descritiva* (é a definição canônica do artigo e é didática), desde que $\varepsilon$ seja reportado e a correção por $\beta_0$ seja discutida.

---

## 2.4 Candidata B — $\Delta_T^{pers} = C_T^{pers} - C_{obs}^{pers}$, com $P_k = \sum_i (d_i - b_i)$

**Definição (§10 do projeto).** Substitui números de Betti pelos comprimentos de barra totais por dimensão.

**Avanço real:** usa a filtração inteira, não um corte — elimina o grau de liberdade $\varepsilon$ e elimina a descontinuidade.

**Problemas remanescentes:**

1. **Depende da escala linear.** $P_k$ tem unidades de $d$; se $\varepsilon$ (ou a norma dos embeddings) mudar de fator $c$, $P_k$ muda de fator $c$. Só é comparável entre nuvens se **todas usarem a mesma escala** — daí a exigência da §6.5.
2. **Dominância de $H_0$.** $\beta_0$ é sempre o maior e as barras de $H_0$ são as mais longas; $P_0$ engole o resto e a métrica converge de volta para "quantidade de componentes".
3. Continua **com peso $(k+1)$ arbitrário**.

> **Veredicto:** ⚠️ **aceitável como secundária/exploratória**, condicionada a escala comum e ao descarte da barra essencial.

---

## 2.5 Candidata C — $\Delta_H = H_T - H_{obs}$ conforme o **§11 original** (entropia do perfil de Betti)

**Definição original.** $p_k = \beta_k / \sum_j \beta_j$, $H = -\sum_k p_k \log p_k$.

> **Proposição 2 (cegueira à magnitude).**
> Se $\beta = (b, 0, \dots, 0)$ para qualquer $b \ge 1$, então $p = (1,0,\dots,0)$ e $H = 0$.
>
> *Demonstração.* $-\log 1 = 0$. $\square$

**Contra-exemplos (mesmo $H$, estruturas radicalmente diferentes):**

| Nuvem | $\beta$ | $H$ |
|---|---|---|
| 10 pontos isolados | $(10,0,0)$ | $0$ |
| 1 000 000 de pontos isolados (texto sem estrutura) | $(10^6,0,0)$ | $0$ |
| nuvem com 5 componentes e 5 ciclos | $(5,5,0)$ | $\ln 2 \approx 0{,}693$ |
| nuvem rica em 3 dimensões uniforme | $(1,1,1)$ | $\ln 3 \approx 1{,}099$ |

> **Proposição 3 (faixa dinâmica limitada).**
> $0 \le H \le \ln(K+1)$, com $K = \max\{k : \beta_k > 0\}$. Para $K=2$, $H \in [0, 1{,}099]$ e portanto $\Delta_H \in [-1{,}099, 1{,}099]$.
>
> *Demonstração.* desigualdade de Jensen / máximo da entropia sobre $K+1$ categorias atingido na distribuição uniforme. $\square$

**Leitura:** um texto perfeitamente estruturado e um texto degenerado **ambos podem dar $\Delta_H = 0$**; a métrica mede apenas o *perfil relativo entre dimensões*, e toda a informação de magnitude é jogada fora.

> **Veredicto:** ❌ **a definição do §11 é inadequada como está.** Não é o conceito de entropia que falha — é a escolha do **espaço de probabilidade**. A correção é na §2.7.

---

## 2.6 Candidata D — distância de *bottleneck* $d_B(D_T, D_{obs})$

**Definição (§14 do projeto).** Para diagramas $D_1, D_2$:

$$d_B(D_1,D_2) = \inf_{M \ \text{acoplamento}} \ \max_{(p,q)\in M}\ \delta_\infty(p,q),\qquad
\delta_\infty\big((b_1,d_1),(b_2,d_2)\big) = \max\big(|b_1-b_2|,\ |d_1-d_2|\big)$$

com a convenção de que um ponto pode ser pareado com a diagonal, a custo $\tfrac{d-b}{2}$.

**Propriedades:**

1. **É uma métrica** sobre diagramas de persistência (não-negatividade, simetria, desigualdade triangular). Logo $\Delta = d_B \ge 0$ **por construção** — a direção da hipótese fica bem definida sem escolha arbitrária de sinal.
2. **Estabilidade.** Para a filtração de Vietoris–Rips vale um resultado do tipo
 $$d_B\big(D(X), D(Y)\big) \le 2\, d_H(X,Y),$$
 com $d_H$ = distância de Hausdorff. I.e.: *nuvens parecidas ⇒ diagramas parecidos*, com constante explícita. Nenhuma das candidatas A–C possui garantia equivalente.
3. **Invariância isométrica:** depende apenas das distâncias entre pontos, logo é invariante a rotação/translação/reordenação dos vetores.
4. **Sensibilidade a ruído diagonal:** pontos próximos da diagonal (barras curtas) inflam $d_B$ — daí a necessidade do modelo nulo da §6.1 e do tratamento da barra essencial.

**Custo computacional:** desprezível para $n \lesssim 2000$.

> **Veredicto:** ✅ **métrica canônica, com garantia teórica.** Melhor *fundamento* das quatro.

---

## 2.7 Candidata E (proposta desta nota) — $\Delta_H$ = **entropia persistente**

**Definição.** Sobre **todas as barras** dos diagramas (barra essencial removida):

$$\ell_i = d_i - b_i,\qquad p_i = \frac{\ell_i}{\sum_j \ell_j},\qquad
H(D) = -\sum_i p_i \log p_i$$

$$\boxed{\ \Delta_H = \big|\,H(D_T) - H(D_{obs})\,\big|\ }$$

> **Propriedade 1 (invariança de escala).**
> Se todo comprimento de barra for multiplicado por $c>0$ — em particular, se os embeddings forem multiplicados por $c$, ou se o parâmetro de filtração mudar de unidade — então $p_i$ é invariante e $H(D)$ não muda.
>
> *Demonstração.* $\dfrac{c\ell_i}{\sum_j c\ell_j} = \dfrac{\ell_i}{\sum_j \ell_j}$. $\square$

**Por que esta e não a do §11:**

| | §11 (entropia de perfil de Betti) | NT-01 (entropia persistente) |
|---|---|---|
| Espaço de probabilidade | dimensões $k$ (só $K{+}1$ categorias) | **barras** (uma por feature topológica) |
| Magnitude | descartada (Prop. 2) | **preservada via $\ell_i$** |
| Invariância à escala dos embeddings | não garantida | **garantida (Prop. 1)** |
| Sensibilidade à estrutura | baixa (só perfil) | alta (geometria inteira dos diagramas) |
| Faixa | $\le \ln(K{+}1) \approx 1{,}1$ | $\le \ln(\#\text{barras})$, tipicamente $2$–$5$ |
| Nome do trabalho | mantém | **mantém** |

**Observação de sinal.** $H(D_T) > H(D_{obs})$ é a expectativa teórica (a obra tem estruturas em *muitas* escalas; a janela local tem estruturas em *poucas* escalas parecidas), mas **não é um teorema**. Por isso o valor absoluto é usado como *magnitude do gap*, e a direção é verificada no piloto computacional (§12) **antes** de congelar a hipótese.

> **Veredicto:** ✅ **Métrica primária.** Mantém o nome **Delta H**, remove todos os defeitos das Proposições 1–3 e herda a estabilidade da construção por persistência.

---

## 3. Matriz de decisão

Critérios: **I1** comparabilidade entre nuvens · **I2** estabilidade/continuidade · **I3** ausência de confundimento por $n$ · **I4** invariância a hiperparâmetros (não exige $\varepsilon$) · **I5** significado direto do gap (não-negatividade) · **I6** garantia teórica publicada · **I7** amplitude de faixa dinâmica.

| Candidata | I1 | I2 | I3 | I4 | I5 | I6 | I7 | Nota |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **A** $\Delta_T$ soma de Betti | ❌ | ❌ | ❌ | ❌ | ⚠️ | ❌ | ✅ | 2/7 |
| **B** $\Delta_T^{pers}$ | ⚠️ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ | ✅ | 4/7 |
| **C** $\Delta_H$ perfil de Betti | ❌ | ⚠️ | ✅ | ❌ | ⚠️ | ❌ | ❌ | 2/7 |
| **D** $d_B$ bottleneck | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **7/7** |
| **E** $\Delta_H$ entropia persistente | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | **6/7** |

**Por que E antes de D**, apesar de D completo:

1. **I5** é o único ponto fraco de E, e é corrigível: $|\cdot|$ torna o gap não-negativo, e a direção é fixada pelo piloto.
2. **A entropia é uma quantidade com interpretação própria** ("heterogeneidade das escalas estruturais"), enquanto $d_B$ é uma distância bruta sem unidades naturais de interpretação substantiva.
3. **A identidade do projeto é ΔH.** Renomear o trabalho para "Bottleneck Gap" seria uma quebra de continuidade com o §11 e com o nome já adotado — e a correção matemática *preserva* o nome.
4. A desvantagem residual de E (dependência do conjunto de barras consideradas) é **exatamente a mesma** de D — ambas operam sobre o diagrama completo.

**Decisão: E primária, D confirmatória.** A exigência de concordância (§5) recupera o rigor de D sem abrir mão do nome nem da interpretação.

---

## 4. Decisão — encadeamento lógico

> **P1.** Um preditor de compreensão deve ser comparável entre obras, janelas e modelos de embedding. *(premissa metodológica)*
> **P2.** Comparabilidade exige invariância a escala linear dos embeddings e a escolha de $\varepsilon$. *(consequência das Proposições 1 e da candidata B.1)*
> **P3.** A candidata A viola P2 (Prop. 1 e descontinuidade) → descartada como primária.
> **P4.** A candidata C viola P2 (faixa finita) **e** é cega à magnitude (Prop. 2) → descartada na forma do §11.
> **P5.** A candidata B satisfaz P2 apenas sob escala comum e mantém pesos arbitrários → secundária.
> **P6.** A candidata E satisfaz P1 e P2 (Propriedade 1) e é construída sobre diagramas, que são estáveis. → **primária.**
> **P7.** A candidata D é completa nos 7 critérios e possui teorema de estabilidade explícito → **confirmatória.**
> **C1.** Suporte à teoria só é declarado se **E e D concordarem** (§5).

---

## 5. Regra de concordância (teste de união-interseção)

Sejam $H_0^{E}$: "ΔH não prediz $S$" e $H_0^{D}$: "$d_B$ não prediz $S$".

- Hipótese nula composta: $H_0 = H_0^{E} \cup H_0^{D}$ (*nenhuma métrica funciona*).
- Regra: **rejeitar $H_0$ somente se ambos os testes rejeitarem**, cada um a nível $\alpha = 0{,}05$.

> **Justificativa.** Se $H_0$ é verdadeira, então ao menos um $H_0^i$ é verdadeiro, e
> $$P(\text{rejeitar } H_0) \le P(\text{rejeitar } H_0^i) \le \alpha.$$
> Logo o nível de teste é preservado **sem correção adicional** e o resultado é conservador. $\square$

Testes secundários (B, C-descritiva, modelos alternativos) entram como **exploratórios** e não geram afirmação confirmatória (fica registrado, para evitar *p-hacking*).

---

# PARTE III — AJUSTES OBRIGATÓRIOS

## 6. Correções metodológicas que precisam entrar no artigo

### 6.1 Referência casada por tamanho ★ crítico

$D_{obs}$ vem de uma nuvem **contígua** e **pequena**; $D_T$ vem de uma nuvem **dispersa** e **grande**. Duas fontes de gap se misturam:

- **(a) efeito de tamanho/resolução** — artefato, não é narrativa;
- **(b) efeito de contiguidade narrativa** — é o fenômeno de interesse.

Comparar diretamente $D_{obs}$ ($n \approx 15$ pontos) com $D_T$ ($n \approx 250$) é **ilegítimo**: a entropia persistente cresce como $\ln(\#\text{barras})$, e o número de barras escala com o número de pontos. Duas nuvens de resoluções diferentes não vivem no mesmo espaço amostral.

**Definição operacional (a que está implementada em `delta_h_pipeline.py`).** Para cada janela com $n$ pontos, sorteiam-se $B \ge 50$ subconjuntos aleatórios $R_b \subset X_T$ com $|R_b| = n$, distribuídos por **toda** a obra. Define-se a *referência casada por tamanho*:

$$H_{\text{ref}}(n) = \operatorname{median}_b\, H\big(D(R_b)\big), \qquad \sigma_{\text{ref}}(n) = \operatorname{sd}_b\, H\big(D(R_b)\big)$$

$$\boxed{\ \Delta_H(r) = \big|\,H(D_{obs}(r)) - H_{\text{ref}}(n_r)\,\big|\ }, \qquad z_H(r) = \frac{H(D_{obs}(r)) - H_{\text{ref}}(n_r)}{\sigma_{\text{ref}}(n_r)}$$

$$\Delta_{d_B}(r) = \underbrace{\operatorname{median}_b\ d_B\big(D_{obs}(r), D(R_b)\big)}_{\text{janela vs. obra, na mesma resolução}} \;-\; \underbrace{\operatorname{median}_{b \ne b'}\ d_B\big(D(R_b), D(R_{b'})\big)}_{\text{piso: amostra aleatória vs. amostra aleatória}}$$

**Propriedades:**

1. **Casamento exato de tamanho e de obra.** $R_b$ e a janela têm o mesmo $n$, vêm do mesmo texto, mesmo idioma e mesmo domínio semântico — a **única** diferença entre elas é a contiguidade narrativa. É essa única diferença que o gap passa a medir.
2. **Comparabilidade.** $z_H$ é adimensional, portanto comparável entre obras e entre tamanhos de janela; $\Delta_H$ bruto também, desde que a Fase 2 confirme que $\sigma_{\text{ref}}$ é estável.
3. **Subtração do piso.** Em $\Delta_{d_B}$, se duas amostras aleatórias do mesmo tamanho já estão longe uma da outra, isso é descontado — o gap reportado é o **excedente** sobre a distância que qualquer pedaço da obra teria.

> **Proposição 4 (o que a referência faz e o que não faz).**
> Se todas as janelas de uma obra têm o mesmo $n$, então $H_{\text{ref}}$, $\sigma_{\text{ref}}$ e o piso de $d_B$ são **constantes por obra**. Logo:
> (i) **dentro** de uma obra, $\Delta_H$ difere de $|H_{obs} - c|$ por constante → a referência **não fabrica nem destrói** correlação com $S$;
> (ii) **entre** obras, essas constantes variam com comprimento, densidade e idioma do texto → **sem** o casamento, qualquer análise *pooled* mediria tamanho de texto em vez de topologia.
>
> *Demonstração.* $c_T$, $\sigma_T$ e o piso dependem de $T$ e de $n$, mas não do índice de janela $r$; portanto $\operatorname{corr}(|H_{obs}(r)-c_T|, S) $ não é afetada pela constante dentro de cada obra. $\square$

**Interpretação:** $\Delta_H > 0$ (ou $z_H$ sistematicamente negativo) significa "a janela contígua tem uma estrutura de escalas **diferente** da que um pedaço aleatório do mesmo tamanho apresenta na mesma obra" — ou seja, **mede localidade narrativa, não quantidade de dados**.

> ⚠️ **Aviso registrado na Fase 2 (em curso).** Em espaços de embedding as distâncias se concentram e $H \approx \ln(\#\text{barras})$; o $\Delta_H$ bruto sai da ordem de $10^{-3}$ enquanto $H \approx 5{,}5$. Por isso o pipeline reporta **em paralelo** $H^{norm} = H/\ln(\#\text{barras})$ e o $z_H$ padronizado. **Qual das três formas ($\Delta_H$, $\Delta_H^{norm}$, $z_H$) entra no pré-registro será decidido no fim da Fase 2, usando apenas texto — nunca dados de leitores.**

### 6.2 Pseudorreplicação ★ crítico

Na tabela do §7 original, $\Delta$ é constante por trecho e varia entre trechos; $S$ varia entre leitores. Calcular `pearsonr(delta, S)` sobre **todos os leitores** infla o $N$ e produz $p$-valores artificialmente pequenos (erros-padrao subestimados).

**Regra:** a unidade de análise para o efeito de $\Delta$ é o **trecho**. Modelos aceitáveis:
- agregação: uma linha por trecho ($\bar S$ por trecho) → Pearson sobre trechos; **ou**
- modelo multinível com interceptos aleatórios por leitor **e** por trecho, com erros-padrão agrupados por trecho (recomendado: mantém todo o dado).

### 6.3 Incompatibilidade lógica: perguntas globais × texto lido ★ crítico

O §3 pede ao leitor "tema central; destino dos personagens; relações entre eventos distantes" — mas o leitor **nunca vê a obra inteira**. Não se pode medir reconstrução de uma estrutura global que não foi exposta.

| Desenho | O que o leitor vê | $S$ global mede | Viabilidade |
|---|---|---|---|
| **A** — obra completa | obra inteira (7 h no Ulysses) | reconstrução real da obra | ❌ inviável |
| **B** — trecho longo | 4 000–6 000 palavras | integração **dentro do trecho lido** | ✅ **recomendado** |
| **C** — janela curta | 250 palavras | só compreensão local | ⚠️ não testa a tese |

**Desenho adotado (B):** o texto lido é o **universo de $S$**; a obra inteira entra apenas na **seleção de trechos** (§6.6). Gap é computado entre janela local e diagrama do **texto lido**.

### 6.4 Variável omitida: dificuldade léxica ★ crítica

Uma janela com vocabulário raro, sintaxe longa ou baixa frequência é difícil **independentemente de topologia**. Se $\Delta$ correlacionar com dificuldade léxica, o efeito observado é confundido.

**Covariates obrigatórias** no modelo final: frequência média de palavras (log), tamanho médio de frase, razão tipo/token, fração de discurso direto, comprimento do trecho.

### 6.5 Resolução comum (checklist técnico)

1. Embeddings L2-normalizados; distância de cosseno.
2. Um único `max_edge_length` **por obra**, igual para todas as nuvens dela (ex.: 90º percentil das distâncias pareadas da obra).
3. Mesmo `max_dimension` (recomendado **2**; $\beta \ge 3$ em embeddings ruidosos é artefato) para todas as nuvens.
4. Mesmo corpo de coeficientes ($\mathbb{Z}/2\mathbb{Z}$).
5. Barra essencial removida.
6. Subamostragem global com seed fixo se $N > 1500$ pontos (custo $\mathcal{O}(N^2)$).
7. **Sem denoise na análise primária** (introduziria outro limiar arbitrário); denoise entra só na análise de robustez.

### 6.6 Sinal e seleção de trechos

- A direção "obra mais rica em escalas ⇒ $H_T > H_{obs}$" é **expectativa, não teorema**. O piloto computacional (§12) fixa o sinal; **só então** a hipótese direcional é congelada.
- **Seleção de trechos estratificada por $\Delta$:** dentro de cada obra, escolher trechos dos quartis superior e inferior de $\Delta_{\text{gap}}$. Isso transforma uma correlação observacional num contraste quase-experimental (grupos alto/baixo gap), com muito mais poder.

---

## 7. Desenho experimental recomendado

| Elemento | Especificação |
|---|---|
| Unidade | leitor × trecho |
| Trecho | 4 000–6 000 palavras contíguas (≈ 20–30 min de leitura) |
| Obras | 6 (grupos simples/intermediário/complexo do §5) |
| Trechos/obra | 6 (3 alto-Δ, 3 baixo-Δ) → **36 trechos** |
| Leitores/trecho | ≥ 3 → **≥ 108 observações** |
| Por leitor | 2 trechos (um de obra "simples", um de "complexa"), ordem contrabalanceada |
| Questionário | 5 itens locais + 5 itens globais, 4 alternativas, piso corrigido por sorte ($0{,}25$) |
| $S$ | $S = 0{,}3\,S_{local} + 0{,}7\,S_{global}$ com $\alpha = 0{,}3$ **congelado** (sensibilidade em $\alpha \in \{0{,}3; 0{,}5\}$ só como exploratória) |
| Escala | $S_{corr} = (p - 0{,}25)/0{,}75 \in [0,1]$ |
| Covariates | escolaridade (anos), idade, familiaridade (auto-relato + teste objetivo), dificuldade léxica do trecho |
| Ética | consentimento livre e assinado; dados anonimizados conforme LGPD |

---

## 8. Modelo estatístico e poder amostral

### 8.1 Modelo primário (pré-especificado)

Nível leitor, erro-padrão agrupado por trecho:

$$S_{ij} = a_{w(j)} - b\,\Delta_{\text{gap},j} + c_1 E_i + c_2 I_i + c_3 F_i + c_4 L_j + \varepsilon_{ij}$$

- $a_{w(j)}$ = efeitos fixos por obra (intercepto por obra) — **obrigatório**: $\Delta$ e $S$ têm nível base diferente entre obras;
- $E$ escolaridade, $I$ idade, $F$ familiaridade, $L$ dificuldade léxica;
- **$H_0: b = 0$ vs $H_1: b > 0$** (unicaudal, pois $S = a - b\Delta$);
- teste complementar de Pearson (unidade = trecho), reportando $r$, IC-95% por *bootstrap* agrupado, e $R^2$;
- nível de significância $\alpha = 0{,}05$; para as duas métricas primárias, regra da §5.

**Versão final (Fase 4):** modelo logístico multinível **por item** (correto/incorrecto) com interceptos aleatórios de leitor, item e trecho — é a que respeita a escala de medição.

### 8.2 Poder amostral

Para teste de correlação unicaudal ($\alpha = 0{,}05$, poder $0{,}80$):
$n = \left(\dfrac{z_{1-\alpha} + z_{1-\beta}}{\operatorname{atanh}|r|}\right)^2 + 3 = \left(\dfrac{2{,}487}{\operatorname{atanh}|r|}\right)^2 + 3$

| $|r|$ esperado | $N$ mínimo |
|---:|---:|
| 0,50 | **24** |
| 0,40 | **38** |
| 0,30 | **68** |
| 0,20 | **154** |

Para regressão com $m=5$ preditores (Green, 1991): $N \ge 50 + 8m = 90$ (modelo) e $N \ge 104 + m = 109$ (preditor individual).

> **Recomendação:** 36 trechos × 3 leitores = **108 observações** (atende 109 no nível leitor) e **36 unidades** para o efeito de $\Delta$ (poder $\approx 0{,}80$ para $|r| \approx 0{,}45$). Para sustentar $|r| = 0{,}30$ seriam necessários **68 trechos** — caso o piloto indique efeito menor que 0,4, ampliar para 6 obras × 12 trechos.

> ⚠️ **O critério de sucesso do §13 original (`r < −0,5`) é otimista para dado comportamental.** Recomenda-se fixar **`r ≤ −0,30` como suporte moderado** e **`r ≤ −0,50` como suporte forte**, declarados antes da coleta.

---

## 9. Hiperparâmetros congelados (tabela de pré-registro)

| Parâmetro | Valor congelado | Justificativa |
|---|---|---|
| Modelo principal | `paraphrase-multilingual-MiniLM-L12-v2` | multilíngue PT/EN; **max 128 wordpieces** |
| Unidade de embedding | **sentença** (nunca janela inteira) | evita truncamento silencioso da janela |
| Normalização | L2 + distância de cosseno ∈ [0,2] | comparabilidade entre obras |
| Janela de cálculo | 250 palavras (passo 250, **sem sobreposição**) | sobreposição gera autocorrelação entre pontos |
| Janela de leitura (desenho) | 4 000–6 000 palavras (§7) | resolução topológica suficiente |
| `max_dimension` | **2** | $\beta_{\ge3}$ é ruído em embedding ruidoso |
| `max_edge_length` | 90º percentil das distâncias da obra | mesmo "zoom" para todas as nuvens |
| Corpo de coeficientes | $\mathbb{Z}/2\mathbb{Z}$ | sem torção, rápido, explícito |
| Barra essencial $(0,\infty)$ | descartada | evita entropia infinita |
| Denoise | **não** na primária; só na robustez | evita limiar arbitrário |
| Modelo nulo | $B = 50$ subconjuntos aleatórios/obra | correção da §6.1 |
| Seed | 42 (globais), registrado em log | reprodutibilidade |
| Robustez de embeddings | + `LaBSE`, + `fastText`/Word2Vec | atende §13 |
| Robustez de janela | 150 / 250 / 400 palavras | atende §13 |
| $\alpha$ do escore | 0,3 | §3 original, congelado |

---

## 10. Controles e critérios de sucesso pré-registrados

**Controles obrigatórios (sanidade):**

| # | Controle | Resultado esperado |
|---|---|---|
| C1 | Texto aleatório (palavras sorteadas) | $\Delta_{\text{gap}} \approx 0$ |
| C2 | Sentenças embaralhadas dentro da obra | $\Delta_{\text{gap}}$ cai significativamente vs. ordem original |
| C3 | Subconjunto aleatório do mesmo tamanho | $\Delta \approx 0$ (é a própria baseline da §6.1) |
| C4 | Repetições com seeds diferentes | CV dos $\Delta < 5\%$ |
| C5 | Sentenças curtas *vs.* longas | $\Delta$ estável (controle de extensão) |

**Critérios de sucesso (declarar antes da coleta):**

- **Suporte forte:** $b > 0$ com $p < 0{,}05$ **em E e em D** (§5), $r \le -0{,}50$, replicado em ≥ 4 das 6 obras e em ≥ 2 dos 3 modelos de embedding.
- **Suporte moderado:** mesmo critério de concordância, com $-0{,}50 < r \le -0{,}30$.
- **Sem suporte:** qualquer das duas métricas não rejeitar $H_0$, ou sinal invertido, ou efeito desaparecer ao incluir dificuldade léxica (§6.4) — este último é **resultado negativo legítimo** e deve ser publicado como tal.

---

## 11. Checklist de ajustes no documento original

- [ ] Reescrever as fórmulas (remover duplicações LaTeX/Unicode e `Mostrar mais linhas`).
- [ ] §11: substituir a entropia de perfil de Betti pela **entropia persistente** (§2.7 desta nota).
- [ ] §2: marcar $\Delta_T$ como *descritiva*, com a ressalva da Proposição 1.
- [ ] §14 (bottleneck): promover de "próximo passo" a **métrica confirmatória**.
- [ ] §7: incluir modelo nulo (§6.1), unidade de análise (§6.2) e covariates léxicas (§6.4).
- [ ] §13: redefinir limiares de $r$ (§8.2) e a regra de concordância (§5).
- [ ] §5: registrar direitos autorais — Dom Casmurro e Hamlet (domínio público) para os textos; *Harry Potter* e *Grande Sertão* apenas por citação curta.
- [ ] Acrescentar: consentimento ético, LGPD, versão do software e seeds.

---

## 12. Plano de execução

| Fase | Entrega | Pré-requisito |
|---|---|---|
| **0** (em curso) | ambiente (`gudhi`, `scikit-learn`, `sentence-transformers`), NT-01 validada | — |
| **1** | obras `.txt` baixadas + pipeline `ΔH` e `d_B` + curvas por obra | fase 0 |
| **2** | **piloto computacional**: sinal do $\Delta_H$, sensibilidade a hiperparâmetros, controles C1–C5 | fase 1 |
| **3** | **congelamento do pré-registro** (sinal, limiares, modelo) com base na fase 2 | fase 2 |
| **4** | piloto com 5–10 leitores (calibração do questionário) | fase 3 |
| **5** | coleta completa (108–144 observações) | fase 4 |
| **6** | análise multinível + artigo em `delta_h/paper/main.tex` | fase 5 |

**Princípio:** nenhuma decisão estatística é tomada depois de ver os dados de leitores. O piloto da fase 2 usa **apenas texto** — não contamina a hipótese.

---

## 13. Referências (guia de leitura)

- Chazal, Cohen-Steiner, Mérigot — *Persistence-based clustering / stability of Rips* (estabilidade $d_B \le 2\,d_H$).
- Edelsbrunner, Harer — *Computational Topology: An Introduction* (bottleneck, persistência).
- Munch, Wang — *Applied Topological Data Analysis* (entropia persistente).
- Green, S. B. (1991) — *How many subjects does it take to do a regression analysis?* (regras $N \ge 50+8m$).
- Gelman & Hill — *Data Analysis Using Regression and Multilevel/Hierarchical Models* (pseudorreplicação, multinível).

---

*Documento gerado como proposta técnica. As 10 decisões da §0 exigem aceite explícito do pesquisador antes da Fase 3 (congelamento do pré-registro).*
