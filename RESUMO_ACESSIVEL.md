# Delta H — Resumo Acessível

## Para que serve este documento?

Este documento explica, em linguagem simples, o que é o projeto **Delta H**, o que estamos calculando, por que isso importa e como será feita a coleta de dados com leitores. Não é necessário conhecimento prévio de matemática ou programação.

---

## 1. A ideia central (em uma frase)

**Queremos medir o quanto um texto é "difícil de entender" analisando a estrutura do texto — não apenas o vocabulário — e verificar se essa medida prevê o desempenho de leitores reais.**

---

## 2. O problema que motiva o trabalho

### 2.1 Como se mede a dificuldade de um texto hoje?

Os métodos tradicionais (Flesch-Kincaid, por exemplo) contam:
- Número de palavras por frase
- Número de sílabas por palavra
- Frequência de palavras no vocabulário

**Problema:** Esses métodos ignoram a **estrutura do texto** — como as ideias se conectam, como o texto se organiza em cenas, como a narrativa se desenvolve.

### 2.2 O que queremos medir?

Queremos medir algo diferente: **a distância entre a estrutura global do texto e a estrutura que o leitor consegue ver em um trecho específico**.

**Exemplo intuitivo:**
- Imagine um romance com 10 capítulos. Cada capítulo tem uma "cena" com personagens, diálogos e descrições.
- Se você lê **apenas um parágrafo**, vê uma pequena parte da história — um fragmento.
- Se você lê **um capítulo inteiro**, vê uma sequência completa de cenas — uma estrutura mais rica.
- Se você lê **o livro inteiro**, vê todas as conexões entre personagens, temas e eventos — a estrutura completa.

**A hipótese:** Quanto maior a diferença entre o que o leitor vê (trecho) e a estrutura completa do texto, mais difícil é para o leitor entender a história.

---

## 3. O que estamos calculando?

### 3.1 A metáfora do "mapa"

Pense no texto como um **mapa de uma cidade**:

| Conceito | Metáfora | No texto |
|---|---|---|
| **Estrutura global** | O mapa completo da cidade | Todas as frases do texto, com suas conexões |
| **Estrutura local** | O que você vê da janela de um prédio | Um trecho específico que o leitor está lendo |
| **Gap (Δ)** | A diferença entre o mapa e a vista da janela | A diferença entre a estrutura completa e o trecho |

### 3.2 Como calculamos isso?

Usamos uma técnica matemática chamada **Análise Topológica de Dados (TDA)**. Em termos simples:

1. **Transformamos cada frase em um ponto** no espaço (usando inteligência artificial para entender o significado das frases)
2. **Conectamos os pontos** que são parecidos (frases com significado semelhante ficam próximas)
3. **Analisamos a forma** dessa rede de conexões:
   - Quantos "aglomerados" de frases existem?
   - Quantos "ciclos" (ideias que se conectam de formas diferentes) existem?
   - Como essas estruturas variam em diferentes escalas?
4. **Comparamos** a estrutura do trecho (o que o leitor vê) com a estrutura de um pedaço aleatório do mesmo tamanho (para controlar o efeito do tamanho do trecho)

### 3.3 O resultado: Delta H (ΔH)

O **Delta H** é um número que mede **quanto a estrutura do trecho difere da estrutura esperada** de um pedaço aleatório do mesmo texto.

- **ΔH alto** = o trecho tem uma estrutura muito diferente do esperado (mais "conectado" ou mais "fragmentado")
- **ΔH baixo** = o trecho tem uma estrutura parecida com a de um pedaço aleatório

### 3.4 O que o Delta H **não** é

- **Não é** uma medida de dificuldade léxica (palavras difíceis)
- **Não é** uma medida de tamanho do texto
- **Não é** uma medida de qualidade literária

---

## 4. Por que isso importa? (Pertinência)

### 4.1 Para a educação
- **Avaliação de textos:** Podemos identificar trechos que são "difíceis" não por causa do vocabulário, mas por causa da estrutura narrativa
- **Adaptação de materiais:** Podemos sugerir adaptações de textos para diferentes níveis de leitores
- **Ensino de leitura:** Podemos ensinar leitores a identificar estruturas narrativas complexas

### 4.2 Para a ciência
- **Nova métrica:** O Delta H é uma medida objetiva e matemática de "complexidade estrutural" de um texto
- **Compreensão de leitura:** Podemos testar se a estrutura do texto prevê a compreensão melhor que medidas tradicionais
- **Interdisciplinaridade:** O projeto conecta matemática, ciência da computação e linguística

### 4.3 Para a sociedade
- **Acessibilidade:** Textos complexos podem ser identificados e adaptados para pessoas com dificuldades de leitura
- **Tradução:** A estrutura topológica pode ajudar a avaliar se uma tradução preserva a estrutura narrativa original
- **Preservação cultural:** Podemos analisar como a estrutura narrativa varia entre culturas e épocas

---

## 5. O que é original neste trabalho? (Originalidade)

### 5.1 Primeira aplicação de TDA à compreensão de leitura
Até onde sabemos, este é o **primeiro estudo** a usar Análise Topológica de Dados para prever compreensão de leitura.

### 5.2 Nova métrica: entropia persistente
A definição de Delta H como **entropia sobre comprimentos de barra** (em vez de perfil de Betti) é uma contribuição original ao campo de TDA.

### 5.3 Descoberta da inversão de sinal
Descobrimos que o sinal do gap **inverte** entre escalas:
- **Janela curta (250 palavras):** O trecho tem **menos** estrutura que um pedaço aleatório (ΔH negativo)
- **Trecho longo (4000 palavras):** O trecho tem **mais** estrutura que um pedaço aleatório (ΔH positivo)

Essa inversão é mecanicamente explicada e foi uma descoberta nova.

### 5.4 Desenho experimental rigoroso
O projeto usa:
- **Referência casada por tamanho:** Comparação com pedaços aleatórios do mesmo tamanho (não com a obra inteira)
- **Teste união-interseção:** Só declaramos suporte se duas métricas independentes concordarem
- **Pré-registro:** Todas as decisões são congeladas antes de ver dados de leitores

---

## 6. O que já foi feito?

### 6.1 Fase 1 — Pipeline e corpus ✅
- 9 obras do Project Gutenberg baixadas e verificadas
- Pipeline completo funcionando (frases → embeddings → topologia → métricas)
- Figuras geradas

### 6.2 Fase 2 — Piloto computacional ✅ (quase concluída)
- 7 rodadas computacionais executadas (7.446 janelas + 150 segmentos)
- 9 decisões congeladas (forma da métrica, escala, controles, etc.)
- Controles C1–C5 executados e verificados
- Análises de sensibilidade completadas

### 6.3 Resultados preliminares
- **Sinal negativo em 9/9 obras** na escala de janela (p ≤ 1,4×10⁻²²)
- **Sinal positivo em 72,7% dos segmentos** na escala de trecho (p = 1,3×10⁻⁸)
- **Controles robustos:** C1 (4,63×), C2 (25,59×)
- **Concordância entre métricas:** ρ = −0,724

---

## 7. O que falta fazer?

### 7.1 Fase 2 — Robustez de embedding (pendente)
- Testar o pipeline com outros modelos de embedding (LaBSE, fastText)
- Verificar se o sinal do gap é consistente entre modelos

### 7.2 Fase 3 — Pré-registro
- Escrever o documento de pré-registro (NT-03)
- Congelar todas as decisões estatísticas

### 7.3 Fase 4 — Piloto de calibração
- Testar o questionário com 5–10 leitores
- Ajustar o procedimento de coleta

### 7.4 Fase 5 — Coleta completa
- 54 leitores × 2 trechos = 108 observações
- Cada trecho lido exatamente 3 vezes

### 7.5 Fase 6 — Artigo
- Análise multinível
- Escrita do artigo científico

---

## 8. Guia de Coleta de Dados com Leitores

### 8.1 Visão geral

| Elemento | Especificação |
|---|---|
| **Participantes** | 54 leitores |
| **Trechos** | 36 trechos (18 alto-Δ + 18 baixo-Δ) |
| **Obras** | 6 obras (2 simples, 2 intermediárias, 2 complexas) |
| **Observações** | 108 (54 leitores × 2 trechos) |
| **Por trecho** | 3 leitores diferentes |
| **Duração** | ~30–40 min por leitor |

### 8.2 Critérios de inclusão para leitores

**Inclusão:**
- Idade ≥ 18 anos
- Ensino médio completo ou superior
- Leitor habitual (lê pelo menos 1 livro por mês)
- Português ou inglês nativo ou fluente

**Exclusão:**
- Dificuldade visual não corrigida
- Distúrbio de leitura diagnosticado (dislexia, etc.)
- Participação em estudos similares nos últimos 6 meses

### 8.3 Os 36 trechos

Os trechos foram selecionados automaticamente com base no valor de Delta H:

| Tipo | Quantidade | Descrição |
|---|---|---|
| **Alto-Δ** | 18 trechos | Trechos com estrutura muito diferente do esperado |
| **Baixo-Δ** | 18 trechos | Trechos com estrutura parecida com a de um pedaço aleatório |

**Distribuição por obra:**

| Nível | Obras | Trechos |
|---|---|---|
| Simples | Alice's Adventures in Wonderland, The Metamorphosis | 6 + 4 = 10 |
| Intermediário | Dom Casmurro, Memórias Póstumas de Brás Cubas | 6 + 6 = 12 |
| Complexo | Ulysses, Quincas Borba | 8 + 6 = 14 |

### 8.4 Atribuição de trechos a leitores

Cada leitor recebe **2 trechos** de níveis diferentes:

| Par | Quantidade | Descrição |
|---|---|---|
| **SI** (Simples + Intermediário) | 12 leitores | 1 trecho simples + 1 trecho intermediário |
| **SC** (Simples + Complexo) | 18 leitores | 1 trecho simples + 1 trecho complexo |
| **IC** (Intermediário + Complexo) | 24 leitores | 1 trecho intermediário + 1 trecho complexo |
| **Total** | **54 leitores** | **108 observações** |

### 8.5 Procedimento de coleta

#### Passo 1 — Preparação
1. Verificar se o leitor atende aos critérios de inclusão
2. Obter consentimento informado (assinado)
3. Coletar dados demográficos:
   - Idade
   - Escolaridade (anos de estudo)
   - Familiaridade com literatura (auto-relato + teste objetivo)

#### Passo 2 — Leitura
1. Apresentar o primeiro trecho (4000 palavras, ~20–30 min de leitura)
2. O leitor lê o trecho em silêncio
3. O leitor pode fazer anotações, mas não pode voltar ao texto durante o questionário

#### Passo 3 — Questionário
Após a leitura, o leitor responde:

**5 itens locais** (sobre o trecho lido):
1. Quem falou neste trecho?
2. Onde ocorreu a cena principal?
3. Qual foi o evento principal?
4. Quem eram os personagens presentes?
5. O que aconteceu antes/depois deste trecho?

**5 itens globais** (sobre a estrutura do trecho):
1. Qual é o tema central deste trecho?
2. Como os eventos se conectam?
3. Qual é o conflito principal?
4. Como os personagens se relacionam?
5. Qual é a mensagem ou ideia principal?

**Escala:** 4 alternativas (múltipla escolha), com piso corrigido por sorte (0,25)

#### Passo 4 — Segunda leitura
1. Apresentar o segundo trecho (mesmo procedimento)
2. Aplicar o questionário novamente

#### Passo 5 — Encerramento
1. Agradecer ao leitor
2. Registrar dados da sessão
3. Anonimizar dados (conforme LGPD)

### 8.6 Cálculo do escore (S)

O escore de compreensão é calculado como:

```
S = 0,3 × S_local + 0,7 × S_global
```

Onde:
- **S_local** = média dos 5 itens locais (corrigida por sorte)
- **S_global** = média dos 5 itens globais (corrigida por sorte)

**Correção por sorte:**
```
S_corrigido = (acertos - 0,25) / 0,75
```

Isso corrige o fato de que, com 4 alternativas, um leitor que chuta aleatoriamente acerta 25% das questões.

### 8.7 Análise estatística

**Modelo principal:**
```
S_ij = a_obra(j) - b × Δ_gap(j) + c1 × Escolaridade + c2 × Idade + c3 × Familiaridade + ε
```

Onde:
- **S_ij** = escore do leitor i no trecho j
- **a_obra(j)** = efeito fixo por obra (intercepto diferente para cada obra)
- **Δ_gap** = ln(1 + |z_H|) — o preditor principal
- **b** = coeficiente que testamos (H0: b = 0 vs H1: b > 0)

**Teste união-interseção:**
- Só declaramos suporte à teoria se **ambas** as métricas (ΔH e d_B) rejeitarem H0 a α = 0,05

### 8.8 Considerações éticas

- **Consentimento informado:** Todos os leitores assinam um termo de consentimento
- **Anonimização:** Dados são anonimizados conforme LGPD
- **Voluntariedade:** O leitor pode desistir a qualquer momento
- **Compensação:** A definir (se aplicável)
- **Aprovação ética:** O projeto deve ser aprovado por um Comitê de Ética em Pesquisa (CEP)

---

## 9. Perguntas frequentes

### P: O que é "entropia persistente"?
R: É uma medida matemática que quantifica a "heterogeneidade" das estruturas em um diagrama de persistência. Em termos simples, mede quantas "escalas" diferentes de estrutura existem no texto.

### P: Por que 4000 palavras?
R: Porque é o tamanho mínimo para que a estrutura topológica seja estável. Trechos mais curtos têm estruturas muito instáveis (muito sensíveis a pequenas mudanças).

### P: Por que 54 leitores?
R: Porque o cálculo de poder amostral indicou que 108 observações (54 leitores × 2 trechos) são suficientes para detectar um efeito moderado (|r| ≈ 0,45) com 80% de poder.

### P: O que acontece se a hipótese não for confirmada?
R: Isso é um resultado legítimo e será publicado. A ciência avança também com resultados negativos.

### P: Posso usar o Delta H para avaliar meus próprios textos?
R: Ainda não. O Delta H está em fase de validação. Após a confirmação, ele pode se tornar uma ferramenta útil para educadores e editores.

---

## 10. Resumo visual

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO DO PROJETO                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Texto completo  →  Embeddings  →  Diagrama global      │
│                                    (estrutura completa)     │
│                                                             │
│  2. Trecho (4000 pal)  →  Embeddings  →  Diagrama local    │
│                                       (estrutura do trecho)│
│                                                             │
│  3. Referência aleatória  →  Diagrama de referência        │
│     (mesmo tamanho)        (esperado para um pedaço        │
│                             aleatório do mesmo texto)       │
│                                                             │
│  4. Comparação:                                            │
│     ΔH = |H(trecho) - H(referência)|                      │
│                                                             │
│  5. Coleta com leitores:                                   │
│     - 54 leitores × 2 trechos = 108 observações            │
│     - Questionário: 5 itens locais + 5 itens globais       │
│     - Escore S = 0,3×S_local + 0,7×S_global               │
│                                                             │
│  6. Análise:                                               │
│     S = a - b×ΔH + covariáveis                             │
│     H0: b = 0  vs  H1: b > 0                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Contato e referências

**Projeto:** Delta H — Validação Empírica do Gap Topológico Narrativo

**Documentos técnicos:**
- NT-01: Estado do Projeto e Escolha da Métrica Primária
- NT-02: Relatório do Piloto Computacional e Congelamento da Forma da Métrica

**Referências principais:**
- Chazal, Cohen-Steiner, Mérigot — *Persistence-based clustering / stability of Rips*
- Edelsbrunner, Harer — *Computational Topology: An Introduction*
- Munch, Wang — *Applied Topological Data Analysis*
- Green, S. B. (1991) — *How many subjects does it take to do a regression analysis?*
- Gelman & Hill — *Data Analysis Using Regression and Multilevel/Hierarchical Models*

---

*Documento gerado em 28/09/2026. Projeto em Fase 2 (piloto computacional).*
